"""P28c - PRICE THE LEAD-TIME MECHANISM (paired within-episode regression).

p28 showed that inside ONE market the higher-realising tape sells the same item ~3.06 days earlier, in a
pool ~25.8 units less glutted, with a ~3-unit smaller largest order. It did not say WHAT THAT IS WORTH.
The offensive's remaining decision -- change the architecture, or ship `cha22_e199_lo96q8` and stop --
turns on one number: coins per seat per season that a lead buys. This computes it.

Design:
  * Unit of analysis = the paired (episode, item) cell from p28 (both seats >= 20 executed units, both
    seats leaderboard teams). The market pair, the seed, the town shop sequence and the opponent are all
    held FIXED, which is the within-market estimator p17 wanted and could not construct.
  * Dependent variable d_px = px(winner) - px(loser) on the SAME item in the SAME episode, weighted by
    the units at risk (min of the two seats' executed units).
  * d_inv is a MEDIATOR, not an instrument: market_price() is a function of inventory by construction, so
    any specification containing d_inv is near-tautological. Both specifications are reported; the honest
    prize uses the d_inv-FREE one.
  * Inference = cluster bootstrap over EPISODES (cells within one episode are not independent).

READ-ONLY over results/p28_tape_divergence/p28_per_seat_item.csv. Writes p28c_leadtime_price.txt.
No engine run, no gate, no agent edit, no submission mechanism.
"""
from __future__ import annotations

import csv
import os
import random
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "results", "p28_tape_divergence", "p28_per_seat_item.csv")
OUT = os.path.join(ROOT, "results", "p28_tape_divergence", "p28c_leadtime_price.txt")
PREMIUM = ["MILK", "WOOL", "STRAWBERRY", "MELON"]
BOOT = 4000
SEED = 20260926


def wls(xs, y, w):
    """weighted simple regression with intercept. xs/y/w are equal-length lists."""
    W = sum(w)
    mx = sum(a * k for a, k in zip(xs, w)) / W
    my = sum(b * k for b, k in zip(y, w)) / W
    sxx = sum((a - mx) ** 2 * k for a, k in zip(xs, w))
    if sxx == 0:
        return 0.0, 0.0, 0.0
    sxy = sum((a - mx) * (b - my) * k for a, b, k in zip(xs, y, w))
    beta = sxy / sxx
    resid = [b - my - beta * (a - mx) for a, b in zip(xs, y)]
    s2 = sum(r * r * k for r, k in zip(resid, w)) / max(1.0, W - 2.0)
    se = (s2 / sxx) ** 0.5
    tss = sum((b - my) ** 2 * k for b, k in zip(y, w))
    rss = sum(r * r * k for r, k in zip(resid, w))
    return beta, se, (1.0 - rss / tss if tss else 0.0)


def main():
    rows = [dict((k, (float(v) if k not in ("team", "item") else v)) for k, v in r.items())
            for r in csv.DictReader(open(SRC, encoding="utf-8"))]
    by = {}
    for r in rows:
        if int(r["paired"]) == 1:
            by.setdefault((int(r["ep"]), r["item"]), {})[int(r["seat"])] = r
    ps = []
    for (ep, it), d in by.items():
        if 0 not in d or 1 not in d or min(d[0]["units"], d[1]["units"]) < 20:
            continue
        hi, lo = (d[0], d[1]) if d[0]["px"] > d[1]["px"] else (d[1], d[0])
        ps.append(dict(ep=ep, item=it, u=min(hi["units"], lo["units"]),
                       d_px=hi["px"] - lo["px"], d_day=hi["day"] - lo["day"],
                       d_inv=hi["inv"] - lo["inv"], d_maxrun=hi["maxrun"] - lo["maxrun"],
                       d_hour=hi["hour"] - lo["hour"], d_mod23=hi["mod23"] - lo["mod23"],
                       rel=abs(d[0]["px"] - d[1]["px"]) / ((d[0]["px"] + d[1]["px"]) / 2.0)))
    if not ps:
        print("no paired cells")
        return
    eps = sorted({p["ep"] for p in ps})
    byep = {e: [p for p in ps if p["ep"] == e] for e in eps}
    VARS = ["d_day", "d_inv", "d_maxrun", "d_hour", "d_mod23"]
    xs = {v: [p[v] for p in ps] for v in VARS}
    y = [p["d_px"] for p in ps]
    w = [p["u"] for p in ps]

    L = ["# P28c - price the lead-time mechanism", "",
         "paired (ep,item) cells, both seats >= 20 units, both seats leaderboard: **%d** over **%d** episodes"
         % (len(ps), len(eps)),
         "Weighted by units at risk; 95%% CI from a %d-draw cluster bootstrap over episodes (seed %d)."
         % (BOOT, SEED), "",
         "| regressor | beta (coins/unit per unit of the regressor) | se | R^2 | 95% CI |", "|---|---:|---:|---:|---|"]
    res = {}
    rng = random.Random(SEED)
    for v in VARS:
        b, se, r2 = wls(xs[v], y, w)
        draws = []
        for _ in range(BOOT):
            samp = []
            for _i in range(len(eps)):
                samp += byep[rng.choice(eps)]
            if len(samp) > 3:
                sx = [p[v] for p in samp]
                draws.append(wls(sx, [p["d_px"] for p in samp], [p["u"] for p in samp])[0])
        draws.sort()
        lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws))]
        res[v] = (b, se, r2, lo, hi)
        lab = v + (" [MEDIATOR - tautological, never a prize]" if v == "d_inv" else
                  ("  <-- the mechanism" if v == "d_day" else ""))
        L.append("| %s | %.3f | %.3f | %.3f | [%.2f, %.2f] |" % (lab, b, se, r2, lo, hi))

    b_day, se_day, r2_day, lo_day, hi_day = res["d_day"]
    lead = abs(st.median([p["d_day"] for p in ps if p["rel"] > 0.15]))
    our = {}
    for r in rows:
        if r["team"] in ("cha22_champion", "cha22_e206_mw_h1q6") and r["item"] in PREMIUM:
            our[r["item"]] = our.get(r["item"], 0.0) + r["units"] / 6.0      # 6 seat-episodes per ref team
    su = sum(our.values())
    L += ["", "## the prize", "",
          "SIGN CONVENTION: d_px is >= 0 by construction (winner minus loser), and the winner's d_day is",
          "NEGATIVE (it sells earlier). So a NEGATIVE beta_day means **selling earlier earns**: the prize is",
          "-beta_day * days_earlier * units. Getting this sign backwards turns a gain into a loss; it was",
          "fixed in this file after a first draft printed the prize negative.", "",
          "pooled beta_day = **%.3f** coins/unit/day (se %.3f, R^2 %.3f, CI [%.2f, %.2f])." % (b_day, se_day, r2_day, lo_day, hi_day),
          "Leader median lead in the divergent set = %.2f days. Our premium units per seat-episode:" % lead,
          "  %s => **%.0f units/seat**." % (", ".join("%s %.0f" % kv for kv in sorted(our.items())), su), "",
          "The pooled beta is an AVERAGE OVER ITEMS whose leads and slopes differ by 15x, so it is an",
          "upper-bound sanity figure only; the defensible estimate is per-item.", ""]
    for f in (0.25, 0.5, 1.0):
        L.append("* POOLED, capture **%.0f%%** of a %.2f-day lead = **%+.0f coins/seat/season** (upper bound)"
                 % (100 * f, lead, -b_day * lead * f * su))
    L.append("")
    L += ["### per-item estimate (the one to use)", "",
          "| item | beta_day | our units/seat | median lead | prize at 100% capture | at 50% |", "|---|---:|---:|---:|---:|---:|"]
    tot100 = tot50 = 0.0
    for it in PREMIUM:
        s = [p for p in ps if p["item"] == it]
        if len(s) < 6 or it not in our:
            continue
        b = wls([p["d_day"] for p in s], [p["d_px"] for p in s], [p["u"] for p in s])[0]
        ld = abs(st.median([p["d_day"] for p in s]))
        pz = -b * ld * our[it]
        tot100 += pz
        tot50 += pz / 2.0
        L.append("| %s | %.3f | %.0f | %.2f d | %+.0f | %+.0f |" % (it, b, our[it], ld, pz, pz / 2.0))
    L += ["", "**PER-ITEM PRIZE: %+.0f coins/seat/season at 100%% capture of the leaders' own median lead, "
          "%+.0f at 50%%.**" % (tot100, tot50), "", "Scale check - the deficit this must explain: p17 matched-volume `own_revenue` gap **26,813**, "
          "`price_realisation_own` **-34,682**.",
          "Live single-run rating noise is +-900, so a prize under ~2,000/seat is not an architecture change.", ""]

    # per-item betas: where is lead-time worth money?
    L += ["## beta_day by item (coins/unit/day), units-weighted", "",
          "| item | n pairs | beta | median lead (days) | units at risk |", "|---|---:|---:|---:|---:|"]
    for it in sorted({p["item"] for p in ps}):
        s = [p for p in ps if p["item"] == it]
        if len(s) >= 6:
            b, se, _ = wls([p["d_day"] for p in s], [p["d_px"] for p in s], [p["u"] for p in s])
            L.append("| %s | %d | %.3f | %.2f | %d |" % (
                it, len(s), b, abs(st.median([p["d_day"] for p in s])), sum(p["u"] for p in s)))
    # carrot
    car = [p for p in ps if p["item"] == "CARROT"]
    L += ["", "## carrot: does a bigger carrot basket buy a better price inside one market?", "",
          "carrot paired cells n=%d; d_px on d_units regression beta = %.3f (se %.3f)."
          % (len(car), *wls([-p["d_day"] * 0 + (0), [0], [1]][:0] or [p["d_day"] for p in car],
                            [p["d_px"] for p in car], [p["u"] for p in car])[:2]) if False else
          "carrot paired cells n=%d - see the per-item table above for its lead-time beta. p27's "
          "42.0->55.2 contest gain straddles two town-shop regimes (a noop opponent starves "
          "`unlocked_shops`), so it is directional evidence only, not a price." % len(car), ""]
    txt = "\n".join(L) + "\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
