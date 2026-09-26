"""P34 - OWN-PRICE-IMPACT TEST OF THE RE-TIMING PRIZE (policy, not optimum).

p30 measured +11,233/seat of reallocation headroom but priced the optimal schedule at ACTUAL day prices,
ignoring that our own moved volume ADDS to the shared pool and lowers that price (`:659-660`). p28c priced
the same mechanism cross-team at +1,619/seat collectable. The 7x gap IS the impact effect; this measures it.

Method, deliberately simple and exactly computable rather than optimised (a first draft with a greedy
marginal-revenue optimiser was discarded: its availability array used cumulative SOLD instead of
cumulative EXISTENT, which would have forbidden every move and returned a trivially zero answer - the kind
of false null this repo has been burned by repeatedly).

Policy evaluated: **liquidate each unit on the earliest day it exists** (forward packing), versus the
spine's ACTUAL schedule. Both are priced by walking the counterfactual inventory:

    inv(day d) = inv_recorded(day d) + [cumulative_x(d) - cumulative_actual(d)]

exact for the town component, because the recorded trajectory already contains the town's decrements and
both seats' actual sells; a re-scheduled seat changes only its own cumulative supply. Every unit is then
re-quoted with the pinned engine's `market_price()`, and each SELL at px>1 increments inventory, so
front-loading pays less the more of it there is.

If forward-packing revenue ~= actual revenue, the spine already liquidates as early as it can, and p30's
+11,233 was **entirely positional** - collectable only by beating the opponent, i.e. zero-sum - which is
exactly p32's claim and predicts the symmetric arm at ~0.

CAVEAT: opponent and town curve held FIXED. Cannot see the opponent reacting to our earlier supply, nor
second-order feedback into town growth / shop draws (a noop opponent starves `unlocked_shops`; shop draws
consume one RNG call per empty unlocked tile - E167). So this is the NON-positional slice with own-impact
included, not a full counterfactual.

Read-only. Writes results/p34_impact_endogenous/. No engine run, no gate, no agent edit, no submission.
"""
from __future__ import annotations

import json
import os
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p19_common as C                     # noqa: E402
import p28_tape_divergence as P            # noqa: E402
import p30_reallocation_headroom as H      # noqa: E402

import kaggle_environments as ke
from kaggle_environments.envs.kaggriculture import kaggriculture as K

assert ke.__version__ == C.ENGINE_PIN
PREMIUM = ["MILK", "WOOL", "STRAWBERRY", "MELON"]
OUT = os.path.join(C.ROOT, "results", "p34_impact_endogenous")


def walk(it, sched, inv_rec, actual):
    """revenue of `sched` (day->units) under endogenous inventory."""
    r = 0.0
    cx = ca = 0
    for dd in range(30):
        cx += sched.get(dd, 0)
        ca += actual.get(dd, 0)
        inv = inv_rec.get(dd, 10000) + (cx - ca)
        for _u in range(sched.get(dd, 0)):
            px = K.market_price(it, max(0, int(inv)))
            r += px
            if px > 1:
                inv += 1
    return r


def main():
    C.assert_engine_pin()
    join, phase, mi, dup, unmapped = C.build_join()
    files = sorted(f for f in os.listdir(P.REPLAYS) if f.startswith("episode-"))
    rows = defaultdict(list)
    n = 0
    for fn in files:
        ep = int(fn.split("-")[1])
        if ep not in {e for (e, _) in phase}:
            continue
        with open(os.path.join(P.REPLAYS, fn), encoding="utf-8") as fh:
            d = json.load(fh)
        for seat in (0, 1):
            team = P.canon(join.get((ep, seat), ""))
            if (ep, seat) not in phase or team not in C.REFS:
                continue
            sold, rev, shed = H.day_tables(d, seat)
            ivs = P.inv_series(d)
            for it in PREMIUM:
                if not sold.get(it):
                    continue
                actual = {k: int(v) for k, v in sold[it].items()}
                tot = sum(actual.values())
                # recorded inventory at the START of each day (step dd*24), pre-action per obs convention
                inv_rec = {dd: ivs[min(len(ivs) - 1, dd * 24)].get(it, 10000) for dd in range(30)}
                # availability = units that ever existed by end of day dd (p30's definition)
                cum = 0
                A = {}
                last = 0
                for dd in range(30):
                    cum += actual.get(dd, 0)
                    last = max(last, int(shed[it].get(dd, 0)))
                    A[dd] = cum + last
                # forward packing: x_dd = A_dd - A_(dd-1) truncated to total
                x, run = {}, 0
                for dd in range(30):
                    room = A[dd] - run
                    x[dd] = min(room, tot - sum(x.values()))
                    run += x[dd]
                if sum(x.values()) != tot:
                    rows["_fail"].append((team, ep, seat, it))
                    continue
                a = walk(it, actual, inv_rec, actual)
                b = walk(it, x, inv_rec, actual)
                rows[it].append((team, ep, seat, tot, a, b, b - a))
            n += 1
        del d
    L = ["# P34 - own-price-impact test of the re-timing prize", "",
         "engine pin %s | our reference seat-episodes: %d | opponent + town curve held FIXED"
         % (ke.__version__, n), "",
         "Policy: liquidate every unit on the earliest day it exists, priced through the pinned",
         "market_price() on the counterfactual inventory (each px>1 sale increments supply).", "",
         "| item | n | units/seat | actual rev/seat | forward-packed rev | DELTA | DELTA as pct of p30 gross |",
         "|---|---:|---:|---:|---:|---:|---:|"]
    gross = {"MILK": 3193, "WOOL": 5380, "STRAWBERRY": 2660, "MELON": 0}
    tot_net = 0.0
    for it in PREMIUM:
        r = rows.get(it) or []
        if not r:
            continue
        dl = [x[6] for x in r]
        tot_net += st.fmean(dl)
        pc = (100.0 * st.fmean(dl) / gross[it]) if gross[it] else float("nan")
        L.append("| %s | %d | %.0f | %.0f | %.0f | **%+.0f** | %s |" % (
            it, len(r), st.fmean([x[3] for x in r]), st.fmean([x[4] for x in r]),
            st.fmean([x[5] for x in r]), st.fmean(dl),
            ("%.0f%%" % pc) if pc == pc else "n/a (p30 gross was +0)"))
    nfail = len(rows.get("_fail") or [])
    L += ["", "**Net premium delta from packing everything as early as it exists: %+.0f coins/seat**" % tot_net,
          "(p30 gross headroom, same items, actual prices: +11,233. Cross-team paired estimate: +1,619.)",
          "infeasible-schedule rows: %d" % nfail, "",
          "## reading", ""]
    if tot_net <= 1500:
        L += ["The spine already liquidates essentially as early as its own availability allows, and/or",
              "own-supply impact eats the apparent headroom. Either way the non-positional slice is small,",
              "so p30's +11,233 was **positional**, and p32's zero-sum reading stands. Prediction for the",
              "symmetric `e222_throughput` arm: |delta| < +900/seat absolute."]
    else:
        L += ["A large positive net delta with the OPPONENT HELD FIXED means a genuinely non-positional",
              "prize exists and p32's zero-sum reading is too pessimistic; the symmetric arm should then",
              "return a positive absolute gain, and a null there would instead indict the graft, not the",
              "measurement."]
    txt = "\n".join(L) + "\n"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "p34_impact_endogenous.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
