"""P28 / CQ-6b - WITHIN-EPISODE TAPE DIVERGENCE ATTRIBUTION.

Question (the one p17 could not answer because its decisive control was empty):
  p17 E8: inside ONE shared market, two leader tapes land within 9.9% of each other on median, but
  36% of (ep,item) pairs diverge >15%.  p19: 0/13 leaders ration their release rate and the shared
  pool crosses I0 on the SAME day for essentially every team.  p17: the gap vs us is PRICE
  (74.5-93.5%), not mix (6.5%), not season timing (identical shapes).
  So: WHEN two tapes in one market diverge, WHAT action separates the higher-realising tape from the
  lower one?  If a portable schedule variable separates them, the STRAWBERRY-conversion target
  (our refs hold the scarcest strawberry pool of 15 and realise 10th/14th of 15) is ours to fix.
  If nothing separates them, the divergence is order-position luck inside a market whose LEVEL is set
  by the opponent pair, and the price axis is NOT tape-actionable.

Trustworthiness:
  * Executed units use tools/p19_replay_exec's shed model (record()), which p19 asserted EXACT against
    phase_p6.jsonl sell_units_exec on 1465/1465 cells.  The same assert is re-run here at step
    granularity; ANY mismatch aborts the report.
  * ONE symmetric pass per episode: both seats' SELL and BUY_PRODUCT commits walk the same inventory,
    so the trajectory cannot depend on which seat is being scored (the first draft of this file had
    that asymmetry and was discarded).
  * Prices are walked per unit through the pinned engine's own market_price() from the RECORDED
    obs[step-1] (pre-action) inventory, in the engine's lockstep order (kaggriculture.py:595-628: both
    players quoted at the same pre-commit inventory, seat 0 commits first; a SELL at px>1 increments
    inventory, `:659-660`).  Never obs[step] prices -- [[project-exact-price-attribution-law]].

READ-ONLY over results/p6_field_20260925/**, results/p6_godview_replays/**, WybeV2/datasets/**.
Writes only results/p28_tape_divergence/. No engine run, no gate, no agent edit, no submission.
"""
from __future__ import annotations

import csv
import json
import os
import random
import re
import statistics as st
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p19_common as C                                        # noqa: E402
from p19_replay_exec import MAX_ORDERS, raw                   # noqa: E402

import kaggle_environments as ke
from kaggle_environments.envs.kaggriculture import kaggriculture as K

assert ke.__version__ == C.ENGINE_PIN, ke.__version__
REPLAYS = os.path.join(C.ROOT, "results", "p6_godview_replays")
OUTDIR = os.path.join(C.ROOT, "results", "p28_tape_divergence")
FOCUS = ["MILK", "WOOL", "STRAWBERRY", "MELON", "TOMATO", "CARROT", "EGG", "WHEAT", "FERTILIZER"]
MIN_UNITS = 20
GAP_BIG = 0.15
N_PERM = 20000
SEED = 20260926
VAR = ["px", "mod23", "hour", "day", "inv", "maxrun", "nsell"]


def canon(t):
    return re.sub(r"[^\w &]+$", "", (t or "").strip(), flags=re.UNICODE).strip()


def shed_state(o):
    """start-of-market-phase shed for a seat: prev private shed + PLACE/DROP - PICKUP."""
    return o


def episode_pair_exec(d, iv):
    """per (step, seat, item) -> [units, revenue]; tot[seat][item] -> units.  Symmetric walk."""
    steps = d["steps"]
    n = len(steps)
    prev = [None, None]
    per = defaultdict(lambda: [0, 0.0])
    tot = [Counter(), Counter()]
    shed = [{}, {}]
    for i in range(1, n):
        acts, queues = [], []
        for s in (0, 1):
            e = steps[i][s] if s < len(steps[i]) else {}
            a = raw((e or {}).get("action")) or {}
            acts.append(a)
            queues.append([raw(x) for x in (a.get("market") or [])][:MAX_ORDERS])
            sh = dict((prev[s] or {}).get("shed") or {})
            hand = Counter()
            for u in ((prev[s] or {}).get("inventories") or []):
                for k, v in (u or {}).items():
                    hand[k] += int(v or 0)
            placed, picked = Counter(), Counter()
            ops = ([raw(a.get("farmer"))] if a.get("farmer") else []) + \
                  [raw(h) for h in (a.get("hands") or []) if raw(h)]
            for op in ops:
                if not op:
                    continue
                nm = op[0]
                if nm in ("PLACE", "DROP") and len(op) >= 3:
                    placed[op[1]] += int(op[2] or 0)
                elif nm == "DROP":
                    placed.update(hand)
                elif nm == "PICKUP" and len(op) >= 2:
                    picked[op[1]] += int(op[2]) if len(op) >= 3 else 1
            for it, q in placed.items():
                sh[it] = sh.get(it, 0) + q
            for it, q in picked.items():
                sh[it] = max(0, int(sh.get(it, 0) or 0) - q)
            shed[s] = sh
        inv = dict(iv[i - 1])
        ost = [{0: None, 1: None} for _ in range(max(len(queues[0]), len(queues[1])))]
        for k in range(len(ost)):
            for s in (0, 1):
                if k < len(queues[s]):
                    o = K._parse_order(queues[s][k])
                    ost[k][s] = o
        for k in range(len(ost)):
            guard = 0
            while guard < 3000:
                guard += 1
                active = False
                for s in (0, 1):                     # engine: seat 0 commits first per unit tick
                    o = ost[k][s]
                    if o is None or not o.get("remaining"):
                        continue
                    it, ty = o.get("item"), o["type"]
                    if ty in ("HIRE", "BUY_LAND"):      # atomic, no market-inventory effect
                        ost[k][s] = None
                        continue
                    if ty == "SELL":
                        # animal-item SELLs (SHEEP/GOOSE) have no price curve; count the units so the
                        # fidelity assert matches phase_p6, price them at 0 (they are not in FOCUS).
                        px = K.market_price(it, inv.get(it, 0)) if it in K.PRODUCTS else 0.0
                        have = int(shed[s].get(it, 0) or 0)
                        if have <= 0:
                            ost[k][s] = None
                            continue
                        shed[s][it] = have - 1
                        o["remaining"] -= 1
                        active = True
                        tot[s][it] += 1
                        c = per[(i, s, it)]
                        c[0] += 1
                        c[1] += px
                        if px > 1:
                            inv[it] = inv.get(it, 0) + 1
                    elif ty == "BUY_PRODUCT":
                        inv[it] = max(0, inv.get(it, 0) - 1)
                        o["remaining"] -= 1
                        active = True
                    else:                             # seeds/animals/hire/land: no inventory effect here
                        o["remaining"] -= 1
                        active = True
                if not active:
                    break
        # carry the post-phase shed forward as the engine's recorded private shed if present
        for s in (0, 1):
            e = steps[i][s] if s < len(steps[i]) else {}
            pr = raw((raw((e or {}).get("observation")) or {}).get("private")) or {}
            prev[s] = pr
    return per, tot


def inv_series(d):
    out = []
    for s in d["steps"]:
        o = raw(s[0].get("observation")) or {}
        m = raw(o.get("market")) or {}
        out.append({k: int(v) for k, v in (m.get("inventory") or {}).items()})
    return out


def feats(per, seat, iv):
    byit = defaultdict(lambda: dict(units=0, rev=0.0, rows=[]))
    for (step, s, it), (u, rev) in per.items():
        if s != seat or u <= 0:
            continue
        b = byit[it]
        b["units"] += u
        b["rev"] += rev
        b["rows"].append((step, u, iv[max(0, step - 1)].get(it, 0)))
    out = {}
    for it, b in byit.items():
        if b["units"] <= 0:
            continue
        rows = sorted(b["rows"])
        U = b["units"]
        out[it] = dict(units=U, rev=b["rev"], px=b["rev"] / U,
                       mod23=100.0 * sum(u for k, u, _ in rows if k % 24 == 23) / U,
                       hour=sum((k % 24) * u for k, u, _ in rows) / U,
                       day=sum((k // 24) * u for k, u, _ in rows) / U,
                       inv=sum(i * u for _, u, i in rows) / U,
                       maxrun=max(u for _, u, _ in rows), nsell=len(rows))
    return out


def perm_p(vals):
    obs = sum(vals)
    if not any(abs(x) > 1e-12 for x in vals) or not vals:
        return None
    rng = random.Random(SEED)
    cnt = 0
    for _ in range(N_PERM):
        if abs(sum(v * (1 if rng.random() < 0.5 else -1) for v in vals)) >= abs(obs):
            cnt += 1
    return (cnt + 1) / (N_PERM + 1)


def block(name, ps):
    out = ["", "### %s  (n=%d paired (ep,item) cells)" % (name, len(ps)), "",
           "| variable | median(winner-loser) | mean | win-share | perm p |", "|---|---:|---:|---:|---:|"]
    for v in VAR:
        ds = [p["d_" + v] for p in ps]
        pv = perm_p(ds)
        out.append("| %s | %.2f | %.2f | %.0f%% | %s |" % (
            v, st.median(ds), st.fmean(ds),
            100.0 * sum(1 for x in ds if x > 0) / len(ds),
            "n/a" if pv is None else "%.4f" % pv))
    return out


def main():
    C.assert_engine_pin()
    join, phase, mi, dup, unmapped = C.build_join()
    refs = {canon(t) for t in C.REFS}
    leaders = sorted({canon(t) for t in join.values()} - refs)
    files = sorted(f for f in os.listdir(REPLAYS) if f.startswith("episode-") and f.endswith("-replay.json"))
    eps = {ep for (ep, _) in phase}
    rows, bad, nre = [], [], 0
    for fn in files:
        ep = int(fn.split("-")[1])
        if ep not in eps:
            continue
        with open(os.path.join(REPLAYS, fn), encoding="utf-8") as fh:
            d = json.load(fh)
        iv = inv_series(d)
        nre += 1
        seats = [s for s in (0, 1) if (ep, s) in phase]
        per, tot = episode_pair_exec(d, iv)
        for s in seats:
            ref = {it: int(v) for it, v in (phase[(ep, s)].get("sell_units_exec") or {}).items()}
            for it in set(ref) | set(tot[s]):
                if tot[s].get(it, 0) != ref.get(it, 0):
                    bad.append((ep, s, it, tot[s].get(it, 0), ref.get(it, 0)))
        tl = {s: canon(join.get((ep, s), "")) for s in seats}
        paired = len(seats) == 2 and tl[0] in leaders and tl[1] in leaders and tl[0] != tl[1]
        for s in seats:
            for it, f in feats(per, s, iv).items():
                if it not in FOCUS:
                    continue
                rows.append(dict(ep=ep, seat=s, team=tl[s], item=it, paired=int(paired), **f))
        del d

    os.makedirs(OUTDIR, exist_ok=True)
    L = ["# P28 / CQ-6b - within-episode tape divergence attribution", "",
         "engine pin %s | replays %d | fidelity mismatches vs phase_p6 sell_units_exec: %d"
         % (ke.__version__, nre, len(bad)), ""]
    if bad:
        L.append("!! ABORT - exec model does not reproduce phase_p6. first 10: %r" % (bad[:10],))
        C.emit("p28_tape_divergence.txt", "\n".join(L) + "\n")
        print("\n".join(L))
        return
    L.append("-> exec units reproduce phase_p6.jsonl sell_units_exec on every (ep,seat,item) cell,")
    L.append("   so the per-unit price walk is applied to exactly the quantities the field report")
    L.append("   publishes, priced by the pinned engine's own market_price().")

    with open(os.path.join(OUTDIR, "p28_per_seat_item.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    byep = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        if r["paired"]:
            byep[r["ep"]][r["item"]][r["seat"]] = r
    pairs = []
    for ep, m in byep.items():
        for it, sd in m.items():
            if 0 not in sd or 1 not in sd or min(sd[0]["units"], sd[1]["units"]) < MIN_UNITS:
                continue
            a, b = sd[0], sd[1]
            rel = abs(a["px"] - b["px"]) / max(1e-9, (a["px"] + b["px"]) / 2.0)
            hi, lo = (a, b) if a["px"] > b["px"] else (b, a)
            rec = dict(ep=ep, item=it, rel=rel, gap=(hi["px"] - lo["px"]) * min(hi["units"], lo["units"]),
                       th=hi["team"], tl=lo["team"], hu=hi["units"], lu=lo["units"],
                       **{("d_" + v): hi[v] - lo[v] for v in VAR},
                       **{("h_" + v): hi[v] for v in VAR})
            pairs.append(rec)
    big = [p for p in pairs if p["rel"] > GAP_BIG]
    ok = [p for p in pairs if p["rel"] <= GAP_BIG]

    L += ["", "## paired leader-vs-leader (ep,item) cells, both seats >= %d units" % MIN_UNITS]
    if pairs:
        rl = sorted(p["rel"] for p in pairs)
        L += ["pairs=%d  median rel gap=%.3f  >15%%: %.1f%% (n=%d)" % (
            len(rl), st.median(rl), 100.0 * len(big) / len(rl), len(big)), ""]
        L += block("ALL pairs", pairs)
        L += block("DIVERGENT pairs (rel > 15%)", big)
        if ok:
            L += block("CONCORDANT pairs (rel <= 15%)", ok)
        L += ["", "### divergent pairs by item", "",
              "| item | n | median rel | median px hi/lo | mean $ gap |", "|---|---:|---:|---|---:|"]
        for it in FOCUS:
            s = [p for p in big if p["item"] == it]
            if s:
                L.append("| %s | %d | %.2f | %.1f / %.1f | %.0f |" % (
                    it, len(s), st.median([p["rel"] for p in s]),
                    st.median([p["h_px"] for p in s]),
                    st.median([p["h_px"] - (p["h_px"] - p["d_px"]) for p in s]),
                    st.fmean([p["gap"] for p in s])))
        L += ["", "### 15 most divergent pairs", "",
              "| ep | item | winner / loser | px h/l | rel | d_mod23 | d_hour | d_day | d_inv | d_maxrun |",
              "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
        for p in sorted(big, key=lambda x: -x["rel"])[:15]:
            L.append("| %d | %s | %s / %s | %.1f/%.1f | %.2f | %.0f | %.1f | %.1f | %.0f | %.0f |" % (
                p["ep"], p["item"], p["th"], p["tl"], p["h_px"], p["h_px"] - p["d_px"], p["rel"],
                p["d_mod23"], p["d_hour"], p["d_day"], p["d_inv"], p["d_maxrun"]))
        # who wins, by team - is realisation a stable team property inside one market?
        L += ["", "### winner/loser tallies over divergent pairs (is high realisation stable?)", "",
              "| team | wins | losses |", "|---|---:|---:|"]
        w, l = Counter(p["th"] for p in big), Counter(p["tl"] for p in big)
        for t in sorted(set(w) | set(l), key=lambda x: -(w[x] - l[x])):
            L.append("| %s | %d | %d |" % (t, w[t], l[t]))
    txt = "\n".join(L) + "\n"
    C.emit("p28_tape_divergence.txt", txt)
    print(txt)


if __name__ == "__main__":
    main()
