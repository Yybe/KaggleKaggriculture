"""P28b - SEAT-COLLISION decomposition of the within-market realisation gap.

Why: kaggriculture.py:612-620 quotes BOTH players at the same pre-commit inventory each unit tick and
commits **seat 0 first**, and a SELL at px>1 increments the shared inventory (`:659-660`). So when both
seats sell the SAME item in the SAME step, seat 1 systematically gets the price seat 0 just lowered.
p28 established the winner sells ~3 days earlier (win-share 6%) but never split the gap into
  (i)  units sold on DIFFERENT steps  -> a schedule/lead-time property (route-resident, J=NO), and
  (ii) units sold in the SAME step as the opponent -> an ORDERING property a wrapper CAN express.
If (ii) dominates, there is a cheap, architecture-compatible lever: never let a premium-item ask meet
the opponent's same-step ask for the same item. This measures which one we are actually paying for.

Reuses p28's proven machinery (exec model asserted exact vs phase_p6 on 1465/1465 cells). READ-ONLY.
Writes results/p28_tape_divergence/p28b_*. No engine run, no gate, no agent edit, no submission.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p19_common as C                     # noqa: E402
import p28_tape_divergence as P            # noqa: E402

REPLAYS = P.REPLAYS
OUT = P.OUTDIR


def main():
    C.assert_engine_pin()
    join, phase, mi, dup, unmapped = C.build_join()
    refs = {P.canon(t) for t in C.REFS}
    leaders = {P.canon(t) for t in join.values()} - refs
    files = sorted(f for f in os.listdir(REPLAYS) if f.startswith("episode-") and f.endswith("-replay.json"))
    eps = {ep for (ep, _) in phase}
    bad = 0
    # (ep,item) accumulators
    acc = defaultdict(lambda: dict(u=[0, 0], rev=[0.0, 0.0],
                                   coll_u=[0, 0], coll_rev=[0.0, 0.0],
                                   dif_u=[0, 0], dif_rev=[0.0, 0.0],
                                   coll_steps=0, both_steps=0))
    for fn in files:
        ep = int(fn.split("-")[1])
        if ep not in eps:
            continue
        with open(os.path.join(REPLAYS, fn), encoding="utf-8") as fh:
            d = json.load(fh)
        iv = P.inv_series(d)
        seats = [s for s in (0, 1) if (ep, s) in phase]
        per, tot = P.episode_pair_exec(d, iv)
        for s in seats:
            ref = {it: int(v) for it, v in (phase[(ep, s)].get("sell_units_exec") or {}).items()}
            for it in set(ref) | set(tot[s]):
                if tot[s].get(it, 0) != ref.get(it, 0):
                    bad += 1
        tl = {s: P.canon(join.get((ep, s), "")) for s in seats}
        paired = len(seats) == 2 and tl[0] in leaders and tl[1] in leaders and tl[0] != tl[1]
        if paired:
            bysi = defaultdict(lambda: [0, 0])          # (step,item) -> units per seat
            for (step, s, it), (u, rev) in per.items():
                if u > 0:
                    bysi[(step, it)][s] += u
                    a = acc[it]
                    a["u"][s] += u
                    a["rev"][s] += rev
            coll_steps = 0
            for (step, s, it), (u, rev) in per.items():
                if u <= 0:
                    continue
                a = acc[it]
                c = bysi[(step, it)]
                if c[0] > 0 and c[1] > 0:               # both seats sold this item in this step
                    a["coll_u"][s] += u
                    a["coll_rev"][s] += rev
                    if s == 0:
                        a["both_steps"] += 1
                        coll_steps += 1
                else:                                   # this seat sold this item alone this step
                    a["dif_u"][s] += u
                    a["dif_rev"][s] += rev
            acc_it = acc[it] if it in acc else None
            _ = acc_it, coll_steps
        del d

    L = ["# P28b - seat-collision decomposition of the within-market realisation gap", "",
         "engine pin %s | fidelity mismatches: %d (0 required)" % (C.ENGINE_PIN, bad), "",
         "Seat 0 commits before seat 1 within a unit tick (engine :612-620) and every SELL at px>1",
         "raises the shared inventory (:659-660), so a same-step same-item collision costs the LATER",
         "seat real money by construction. Below, the season gap per item is split into units sold in",
         "a step where the opponent sold the same item (COLLISION) vs units sold ALONE.", "",
         "| item | units s0/s1 | px s0/s1 | COLLIDED units s0/s1 | px collided s0/s1 | px alone s0/s1 | share units colliding |",
         "|---|---|---|---|---|---|---|"]
    tot_coll = tot_all = 0
    for it in P.FOCUS:
        a = acc.get(it)
        if not a or not (a["u"][0] and a["u"][1]):
            continue
        pu = [a["rev"][s] / max(1, a["u"][s]) for s in (0, 1)]
        pc = [a["coll_rev"][s] / max(1, a["coll_u"][s]) for s in (0, 1)]
        pa = [a["dif_rev"][s] / max(1, a["dif_u"][s]) if a["dif_u"][s] else 0.0 for s in (0, 1)]
        share = 100.0 * sum(a["coll_u"]) / max(1, sum(a["u"]))
        tot_coll += sum(a["coll_u"])
        tot_all += sum(a["u"])
        L.append("| %s | %d/%d | %.1f/%.1f | %d/%d | %.1f/%.1f | %.1f/%.1f | %.1f%% |" % (
            it, a["u"][0], a["u"][1], pu[0], pu[1], a["coll_u"][0], a["coll_u"][1],
            pc[0], pc[1], pa[0], pa[1], share))
    L += ["", "TOTAL collided units / all units across FOCUS items: **%d / %d = %.1f%%**" % (
        tot_coll, tot_all, 100.0 * tot_coll / max(1, tot_all)), ""]
    txt = "\n".join(L) + "\n"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "p28b_seat_collision.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
