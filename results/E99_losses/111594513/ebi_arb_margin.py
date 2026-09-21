"""Ebi bulk-WHEAT round-trip arb margin forensics - episode 111594513.
Run from repo root:  python results/E99_losses/111594513/ebi_arb_margin.py

Semantics that decide this whole analysis (matches ledger law "obs[t]=POST-action"):
  obs[t].market.inventory already absorbs step t's fills, and obs[t].market.prices
  ALREADY INCLUDES step t's own price impact. So the displayed price on a buy step
  is a post-impact (inflated) price and on a sell step a post-impact (depressed)
  price -- reading them as fills yields a phantom +/-3px spread.
  Ground truth for fills = the actor's own per-step money delta (quiet steps have
  exactly 0 drift, so money moves only through market ops / hires).
Engine fill model recovered here: fill ~= (price[t-1] + price[t]) / 2 (avg-price
execution against the impact curve), which is why buy-then-sell-one-step-later is
~breakeven instead of a 3px windfall.
"""
import json
from collections import defaultdict, Counter

P = "results/E99_losses/episode-111594513-replay.json"
d = json.load(open(P, encoding="utf-8"))
steps = d["steps"]
names = [a["Name"] for a in d["info"]["Agents"]]
SEAT = names.index("Ebi")
OPP = 1 - SEAT
print(f"agents={names} rewards={d['rewards']} -> Ebi seat {SEAT}, us seat {OPP}")

PHASES = [("P1 d12-17", 12, 17), ("P2 d18-25", 18, 25), ("P3 d26-29", 26, 29)]
PNS = [p[0] for p in PHASES]


def phase_of(day):
    for nm, a, b in PHASES:
        if a <= day <= b:
            return nm
    return "early d0-11"


recs = {}
for t in range(720):
    recs[t] = {}
    for seat in (0, 1):
        o = steps[t][seat]["observation"]
        mkt = [e for e in (steps[t][seat]["action"].get("market") or []) if len(e) == 3]
        recs[t][seat] = dict(
            day=o["day"], hour=o["hour"],
            px=o["market"]["prices"]["WHEAT"], inv=o["market"]["inventory"]["WHEAT"],
            money=o["farms"][seat]["money"],
            wbuy=sum(e[2] for e in mkt if e[0] == "BUY_PRODUCT" and e[1] == "WHEAT"),
            wsell=sum(e[2] for e in mkt if e[0] == "SELL" and e[1] == "WHEAT"),
            nops=len(mkt),
            other=sum(1 for e in mkt if not (e[1] == "WHEAT" and e[0] in ("BUY_PRODUCT", "SELL"))),
            hires=sum(1 for e in (steps[t][seat]["action"].get("market") or []) if e == ["HIRE"]),
        )

# ---------------------------------------------------------- (A) price-tape view
tape = defaultdict(lambda: dict(bq=0, sq=0, bpx=0.0, spx=0.0, bp0=0.0, sp0=0.0))
for t in range(720):
    r = recs[t][SEAT]
    ph = phase_of(r["day"])
    if ph not in PNS:
        continue
    e = tape[ph]
    p0 = recs[t - 1][SEAT]["px"]
    if r["wbuy"]:
        e["bq"] += r["wbuy"]; e["bpx"] += r["px"] * r["wbuy"]; e["bp0"] += p0 * r["wbuy"]
    if r["wsell"]:
        e["sq"] += r["wsell"]; e["spx"] += r["px"] * r["wsell"]; e["sp0"] += p0 * r["wsell"]

print("\n=== (A) PRICE-TAPE view: Ebi WHEAT, obs prices only (NO money check) ===")
print(f"{'phase':11} {'buyQ':>6} {'sellQ':>6} {'buyPx[t]':>9} {'sellPx[t]':>10} "
      f"{'apparent':>9} {'buyPx[t-1]':>11} {'sellPx[t-1]':>12} {'apparent':>9}")
for nm, a, b in PHASES:
    e = tape[nm]
    bt, st = e["bpx"] / e["bq"], e["spx"] / e["sq"]
    b0, s0 = e["bp0"] / e["bq"], e["sp0"] / e["sq"]
    print(f"{nm:11} {e['bq']:6d} {e['sq']:6d} {bt:9.2f} {st:10.2f} {st-bt:+9.2f} "
          f"{b0:11.2f} {s0:12.2f} {s0-b0:+9.2f}   (sum bought {e['bq']} / sold {e['sq']})")

# --------------------------------------------- (B) money-view realized fill (truth)
quiet = sorted(recs[t][SEAT]["money"] - recs[t - 1][SEAT]["money"]
               for t in range(1, 720) if recs[t][SEAT]["nops"] == 0 and recs[t][SEAT]["hires"] == 0)
print(f"\nquiet-step money drift (no market op, no hire): n={len(quiet)} median={quiet[len(quiet)//2]:.0f} "
      f"zero-share={sum(1 for x in quiet if x == 0)/len(quiet):.0%} -> money moves only via market ops")

cycles, gaps = [], Counter()
for t in range(1, 719):
    r, r0, r1 = recs[t][SEAT], recs[t - 1][SEAT], recs[t + 1][SEAT]
    n = r["wbuy"]
    if n and r1["wsell"] == n and r["nops"] == 1 and r1["nops"] == 1 \
            and r["other"] == 0 and r1["other"] == 0 and r["hires"] == 0 and r1["hires"] == 0:
        cycles.append(dict(t=t, qty=n, phase=phase_of(r["day"]),
                           spend=r0["money"] - r["money"], rev=r1["money"] - r["money"],
                           net=r1["money"] - r0["money"], px_t=r["px"], px_prev=r0["px"]))
for t in range(288, 719):
    if recs[t][SEAT]["wbuy"]:
        for k in range(1, 7):
            if recs[t + k] and recs[t + k][SEAT]["wsell"]:
                gaps[k] += 1
                break
print(f"buy -> next wheat-sell step gap distribution (d12+): {dict(gaps)}")
qc = sum(c["qty"] for c in cycles)
tb_ = sum(tape[nm]["bq"] for nm, _, _ in PHASES)
print(f"clean 1-step flips: {len(cycles)} cycles / {qc} units = {qc/tb_:.0%} of the {tb_} in-phase WHEAT buys")

print("\n=== (B) MONEY-VIEW realized fills (ground truth), clean flips only ===")
print(f"{'phase':11} {'flips':>5} {'qty':>6} {'buy/u':>7} {'sell/u':>7} {'margin/u':>9} {'gross':>7} {'gross/day':>10}")
tot = 0.0
for nm, a, b in PHASES:
    cs = [c for c in cycles if c["phase"] == nm]
    q = sum(c["qty"] for c in cs)
    bu = sum(c["spend"] for c in cs) / q
    su = sum(c["rev"] for c in cs) / q
    g = sum(c["net"] for c in cs)
    tot += g
    print(f"{nm:11} {len(cs):5d} {q:6d} {bu:7.2f} {su:7.2f} {su-bu:9.3f} {g:7.0f} {g/(b-a+1):10.0f}")
print(f"ALL d12-29 gross = {tot:,.0f}  ({tot/18:,.0f}/day);  per-cycle mean "
      f"{tot/len(cycles):.1f}, per-unit mean {tot/qc:.3f}px, max per-unit {max(c['net']/c['qty'] for c in cycles):.3f}px")
allflip = sum(1 for t in range(288, 719)
              if recs[t][SEAT]["wbuy"] and recs[t + 1][SEAT]["wsell"] == recs[t][SEAT]["wbuy"])
print(f"flip occurrences incl. contaminated steps: {allflip} -> extrapolated whole-game arb gross "
      f"{tot/len(cycles)*allflip:,.0f} = {tot/len(cycles)*allflip/18:,.0f}/day")
print(f"per-cycle net values: {Counter(int(c['net']) for c in cycles).most_common(6)} "
      f"(quantised stub, NOT proportional to qty: qty range {min(c['qty'] for c in cycles)}-{max(c['qty'] for c in cycles)})")

# ------------------------------------------------------- capital exposure
peak = max(c["qty"] for c in cycles)
print(f"\ncapital exposure: peak simultaneous market-bought position {peak} u "
      f"= {peak*max(c['px_t'] for c in cycles):,.0f} notional, held 1 hour; "
      f"running market-wheat position never carried overnight")
pos = peak_pos = 0
for t in range(288, 720):
    pos += recs[t][SEAT]["wbuy"] - recs[t][SEAT]["wsell"]
    peak_pos = max(peak_pos, pos)
print(f"  running (buys-sells) d12-29: peak +{peak_pos:.0f}, ends {pos:.0f} (net liquidation of home-grown wheat)")

# ------------------------------------------- average-fill estimator validation
print("\n=== estimator validation: avg-fill model (px[t-1]+px[t])/2 vs realized cash ===")
for nm, a, b in PHASES[:1]:
    cs = [c for c in cycles if c["phase"] == nm]
    pred = sum((c["px_prev"] + c["px_t"]) / 2 * c["qty"] for c in cs) / sum(c["qty"] for c in cs)
    print(f"  {nm}: predicted buy/u {pred:.2f} vs realized {sum(c['spend'] for c in cs)/sum(c['qty'] for c in cs):.2f}")

# --------------------------------------------------- what actually won the game
def last_of(day):
    return [t for t in range(720) if recs[t][SEAT]["day"] == day][-1]

milk = defaultdict(lambda: [0.0, 0.0])
for t in range(1, 720):
    o = steps[t][SEAT]["observation"]
    if o["day"] < 12:
        continue
    for seat in (SEAT, OPP):
        pc = steps[t][seat]["observation"]["market"]["prices"]
        pp = steps[t - 1][seat]["observation"]["market"]["prices"]
        for e in [y for y in (steps[t][seat]["action"].get("market") or [])
                  if len(y) == 3 and y[0] == "SELL" and y[1] in pc]:
            cash = (pp[e[1]] + pc[e[1]]) / 2 * e[2]
            k = "MILK" if e[1] == "MILK" else "OTHER"
            milk[(k, seat)][0] += e[2]
            milk[(k, seat)][1] += cash

print("\n=== attribution: phase money gap vs wheat-arb gross ===")
print(f"{'window':11} {'Ebi gain':>10} {'our gain':>10} {'gap':>9} {'arb gross':>10} {'arb %gap':>9}")
for nm, a, b in PHASES:
    ta, tb = last_of(a - 1), last_of(b)
    e = recs[tb][SEAT]["money"] - recs[ta][SEAT]["money"]
    o = recs[tb][OPP]["money"] - recs[ta][OPP]["money"]
    cs = [c for c in cycles if c["phase"] == nm]
    g = sum(c["net"] for c in cs)
    print(f"{nm:11} {e:10,.0f} {o:10,.0f} {e-o:9,.0f} {g:10,.0f} {100*g/(e-o):8.1f}%")
ta, tb = last_of(11), last_of(29)
e = recs[tb][SEAT]["money"] - recs[ta][SEAT]["money"]
o = recs[tb][OPP]["money"] - recs[ta][OPP]["money"]
print(f"{'d12-29':11} {e:10,.0f} {o:10,.0f} {e-o:9,.0f} {tot:10,.0f} {100*tot/(e-o):8.1f}%")
print(f"  MILK sells d12-29 (avg-fill est): Ebi {milk[('MILK',SEAT)][0]:.0f}u/${milk[('MILK',SEAT)][1]:,.0f} "
      f"vs ours {milk[('MILK',OPP)][0]:.0f}u/${milk[('MILK',OPP)][1]:,.0f} -> cash gap "
      f"{milk[('MILK',SEAT)][1]-milk[('MILK',OPP)][1]:+,.0f} ({100*(milk[('MILK',SEAT)][1]-milk[('MILK',OPP)][1])/(e-o):.0f}% of the d12-29 gap)")
print(f"  all-sell cash d12-29 est: Ebi ${sum(v[1] for k, v in milk.items() if k[1]==SEAT):,.0f} "
      f"vs ours ${sum(v[1] for k, v in milk.items() if k[1]==OPP):,.0f}")
lead = max((recs[t][OPP]["money"] - recs[t][SEAT]["money"], t) for t in range(720))
print(f"  our lead: peak {lead[0]:+,.0f} at step {lead[1]} (d{recs[lead[1]][OPP]['day']}), "
      f"final {recs[719][OPP]['money']-recs[719][SEAT]['money']:+,.0f}")
