"""E95 ladder analyzer: E94 (frozen pub_e94_omw_clean) vs r78u across the banded pool.

Reads results/e95_ladder.jsonl (rows: opp,tier,seed,swap,var,our,opp_rw,delta,
our_status,opp_status,crash,hashes,...). Prints:
  A. band-stratified stats per variant
  B. E94-vs-r78u outcome transition matrix + per-transition detail
  C. per-opponent margin differential
  D. first-divergence step distribution (hash chains, same world)
  E. regression list (r78u WIN -> E94 LOSS/DRAW)
"""
import json, statistics, collections, pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
ROWS = [json.loads(l) for l in open(BASE/"results/e95_ladder.jsonl") if l.strip()]

def outcome(r):
    if r["crash"] or r["our_status"] not in ("DONE", "Success", "completed"):
        return "L"
    d = r["delta"]
    return "W" if d > 0 else ("L" if d < 0 else "D")

# pair rows by (opp,seed,swap)
pairs = collections.defaultdict(dict)
for r in ROWS:
    k = (r["opp"], r["seed"], r["swap"])
    v = r["var"]
    if k in pairs and v in pairs[k]:
        raise SystemExit(f"duplicate row {k} {v}")
    pairs[k][v] = r

TIER_ORDER = ["floor", "<2400", "2400-2600", "2600-2800", "2650-2750 cluster", "strong", "top"]

def band_table(variant):
    by = collections.defaultdict(list)
    for r in ROWS:
        if r["var"] == variant:
            by[r["tier"]].append(r)
    print(f"\n== A. band stats: {variant} ==")
    print(f"{'band':<20}{'n':>3}{'W':>3}{'L':>3}{'D':>3}{'win%':>7}{'mean':>10}{'median':>10}")
    for t in TIER_ORDER:
        rs = by.get(t, [])
        if not rs:
            continue
        o = [outcome(r) for r in rs]
        dl = [r["delta"] for r in rs]
        w, l, dd = o.count("W"), o.count("L"), o.count("D")
        print(f"{t:<20}{len(rs):>3}{w:>3}{l:>3}{dd:>3}{100*w/len(rs):>6.0f}%{statistics.mean(dl):>10.0f}{statistics.median(dl):>10.0f}")
    return by

band_table("e94")
band_table("r78u")

# B. transitions on complete pairs
print("\n== B. outcome transitions r78u -> E94 (same world) ==")
trans = collections.Counter()
detail = []
complete = {k: v for k, v in pairs.items() if "e94" in v and "r78u" in v}
for (opp, seed, swap), d in sorted(complete.items()):
    a, b = outcome(d["r78u"]), outcome(d["e94"])
    trans[(a, b)] += 1
    if a != b:
        detail.append((opp, d["r78u"]["tier"], seed, swap, a, b, d["r78u"]["delta"], d["e94"]["delta"]))
for (a, b), n in sorted(trans.items()):
    print(f"  {a}->{b}: {n}")
print(f"  (n pairs = {len(complete)})")
if detail:
    print("  transitions detail:")
    for x in detail:
        print(f"    {x[0]:<14}{x[1]:<16}seed{x[2]} swap{x[3]}  {x[4]}->{x[5]}  {x[6]:+.0f} -> {x[7]:+.0f}  ({x[7]-x[6]:+.0f})")

# C. per-opponent differential
print("\n== C. per-opponent mean margin, E94 - r78u ==")
print(f"{'opp':<16}{'tier':<18}{'n':>3}{'r78u':>10}{'E94':>10}{'diff':>10}")
byopp = collections.defaultdict(lambda: {"e94": [], "r78u": []})
for (opp, seed, swap), d in complete.items():
    byopp[opp]["e94"].append(d["e94"]["delta"])
    byopp[opp]["r78u"].append(d["r78u"]["delta"])
tier_of = {r["opp"]: r["tier"] for r in ROWS}
for opp in sorted(byopp, key=lambda o: TIER_ORDER.index(tier_of[o])):
    e, r = byopp[opp]["e94"], byopp[opp]["r78u"]
    print(f"{opp:<16}{tier_of[opp]:<18}{len(e):>3}{statistics.mean(r):>10.0f}{statistics.mean(e):>10.0f}{statistics.mean(e)-statistics.mean(r):>+10.0f}")

# band-level differential
print("\n== C2. band-level mean margin diff ==")
byband = collections.defaultdict(lambda: {"e94": [], "r78u": []})
for (opp, seed, swap), d in complete.items():
    byband[d["e94"]["tier"]]["e94"].append(d["e94"]["delta"])
    byband[d["e94"]["tier"]]["r78u"].append(d["r78u"]["delta"])
for t in TIER_ORDER:
    if t in byband:
        e, r = byband[t]["e94"], byband[t]["r78u"]
        print(f"  {t:<20} n={len(e):>3}  r78u {statistics.mean(r):>+9.0f}  E94 {statistics.mean(e):>+9.0f}  diff {statistics.mean(e)-statistics.mean(r):>+9.0f}")

# D. first divergence step
print("\n== D. first divergence step (E94 vs r78u action hash chain, same world) ==")
divs = []
for (opp, seed, swap), d in sorted(complete.items()):
    ha, hb = d["r78u"]["hashes"], d["e94"]["hashes"]
    fd = None
    for i in range(min(len(ha), len(hb))):
        if ha[i] != hb[i]:
            fd = i
            break
    divs.append((opp, seed, swap, fd))
steps = collections.Counter(fd for _, _, _, fd in divs)
for s, n in sorted(steps.items(), key=lambda x: (x[0] is None, x[0])):
    print(f"  {'identical' if s is None else f'step {s}'}: {n} worlds")

# E. regressions
print("\n== E. regressions (r78u W -> E94 L/D) ==")
reg = [x for x in detail if x[4] == "W" and x[5] in ("L", "D")]
if not reg:
    print("  none")
for x in reg:
    print(f"    {x[0]} {x[1]} seed{x[2]} swap{x[3]}: {x[6]:+.0f} -> {x[7]:+.0f}")

# F. low-band check: any E94 loss vs floor/<2400/2400-2600?
print("\n== F. E94 losses in low bands (<2600) ==")
lo = [(o, s, sw, complete[(o, s, sw)]["e94"]["delta"]) for (o, s, sw) in complete
      if complete[(o, s, sw)]["e94"]["tier"] in ("floor", "<2400", "2400-2600")
      and outcome(complete[(o, s, sw)]["e94"]) == "L"]
print("  none" if not lo else "")
for x in lo:
    print(f"    {x[0]} seed{x[1]} swap{x[2]}: {x[3]:+.0f}")
