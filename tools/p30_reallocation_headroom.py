"""P30 - REALLOCATION HEADROOM ON OUR OWN TAPE (is the sell-through governor even collectable?).

p28c priced lead-time at +3,341/seat from OTHER teams' within-market pairs. p29 showed the edge is a
daily sell-through decision, not production-start. Before any candidate is gated, one question is
unanswered and it is a property of OUR tape, not theirs:

    Given the units our spine actually harvested, on the days they actually existed, could a different
    day-by-day release schedule have realised meaningfully more?

If the answer is "barely", the +3,341 is unreachable for us and the whole price axis closes - no arm will
win, because the money was never in the schedule. If it is "yes, by several thousand", the governor has
reallocation capacity and the binding constraint is elsewhere (the shed cap, or the 10-order cap).

Formulation, exactly. Per item, per seat-episode, over days d=0..29:
  A_d  = cumulative units that ever existed by end of day d = shed_at_end_of_day(d) + sum(sold through d).
         (Discards are invisible, so A_d UNDER-estimates availability -> the headroom below is a
          conservative bound, not a fantasy.)
  px_d = executed-unit-weighted realised price on day d, walked through the pinned engine's own
         market_price() from RECORDED obs[step-1] inventory (never obs[step] prices).
  Feasible schedule x: sum(x)=sum(sold), and for every d, sum(x_0..x_d) <= A_d   (you cannot sell units
         that did not exist yet). The objective sum(x_d * px_d) is maximised by the greedy over days in
         descending px, because the prefix constraints form a polymatroid.
Headroom = optimal_revenue - actual_revenue, reported per seat-episode and per item.

CAVEAT that must travel with the number: moving OUR volume onto a high-price day would itself add to the
shared pool and lower that price (the ratchet, `:659-660`), so this is an UPPER bound on a first-order
effect. It is deliberately compared against p28c's +3,341, which was measured BETWEEN two live tapes and
therefore already contains impact.

Inputs read-only: results/p6_godview_replays/** (our 12 reference seat-episodes),
results/ep_56539078_replays/** (live game, sid 56539078 = cha22_champion, seat 0 vs 'Jules'),
results/p6_field_20260925/phase_p6.jsonl + WybeV2/datasets/p6_field_20260925/manifest.csv for the join.
No engine run, no gate, no agent edited, no submission mechanism.
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

import kaggle_environments as ke
from kaggle_environments.envs.kaggriculture import kaggriculture as K

assert ke.__version__ == C.ENGINE_PIN, ke.__version__
ITEMS = ["MILK", "WOOL", "STRAWBERRY", "MELON", "CARROT", "TOMATO", "EGG", "WHEAT", "FERTILIZER"]
PREMIUM = ["MILK", "WOOL", "STRAWBERRY", "MELON"]
OUT = os.path.join(C.ROOT, "results", "p28_tape_divergence", "p30_reallocation_headroom.txt")


def raw(v):
    return P.raw(v)


def day_tables(d, seat):
    """per item -> (sold[d], px_wtd[d], shed_end[d])."""
    steps = d["steps"]
    sold = defaultdict(lambda: defaultdict(int))
    rev = defaultdict(lambda: defaultdict(float))
    shed_end = defaultdict(dict)
    for i in range(1, len(steps)):
        e = steps[i][seat] if seat < len(steps[i]) else {}
        o = raw((e or {}).get("observation")) or {}
        day = o.get("day")
        priv = raw(o.get("private")) or {}
        sh = priv.get("shed") or {}
        if day is not None:
            for it in ITEMS:
                if it in sh:
                    shed_end[it][day] = int(sh.get(it) or 0)
    # executed units + per-unit realised price come from the asserted-exact p28 model
    iv = P.inv_series(d)
    per, tot = P.episode_pair_exec(d, iv)
    for (step, s, it), (u, r) in per.items():
        if s != seat or u <= 0:
            continue
        day = (step - 1) // 24
        sold[it][day] += u
        rev[it][day] += r
    return sold, rev, shed_end


def headroom(sold_d, rev_d, shed_end_d):
    """greedy optimal re-timing under prefix-availability constraints."""
    days = list(range(30))
    sold = {k: int(v) for k, v in sold_d.items()}
    tot = sum(sold.values())
    if tot == 0:
        return 0.0, 0, 0.0
    px = {k: (rev_d[k] / sold[k]) for k in sold if sold[k]}
    actual = sum(rev_d[k] for k in sold)
    # cumulative availability A_d = shed at end of day d + sold through d (max over days <= d for the
    # shed, since a unit present on day d is present on every later day unless sold/discarded)
    cum_sold = {}
    run = 0
    for dd in days:
        run += sold.get(dd, 0)
        cum_sold[dd] = run
    shed_at = {}
    last = 0
    for dd in days:
        last = max(last, int(shed_end_d.get(dd, 0)))
        shed_at[dd] = last
    A = {dd: cum_sold[dd] + shed_at[dd] for dd in days}
    x = {dd: 0 for dd in days}
    assigned = 0
    for dd in sorted([k for k in days if k in px], key=lambda k: -px[k]):
        # feasible extra on day dd: prefix constraints for every d >= dd must still hold
        room = tot - assigned
        for e in range(dd, 30):
            used = sum(x[k] for k in range(e + 1))
            room = min(room, A[e] - used)
        if room > 0:
            x[dd] += int(room)
            assigned += int(room)
    opt = sum(x[dd] * px.get(dd, 0.0) for dd in days)
    return opt - actual, assigned - tot, px.get(min(px, key=lambda k: px[k]), 0.0)


def main():
    join, phase, mi, dup, unmapped = C.build_join()
    refs = set(C.REFS)
    rows = defaultdict(list)
    files = sorted(f for f in os.listdir(P.REPLAYS) if f.startswith("episode-"))
    n = 0
    for fn in files:
        ep = int(fn.split("-")[1])
        with open(os.path.join(P.REPLAYS, fn), encoding="utf-8") as fh:
            d = json.load(fh)
        for seat in (0, 1):
            team = P.canon(join.get((ep, seat), ""))
            if (ep, seat) not in phase or team not in refs:
                continue
            sold, rev, shed = day_tables(d, seat)
            for it in ITEMS:
                hr, over, _ = headroom(sold.get(it, {}), rev.get(it, {}), shed.get(it, {}))
                if sold.get(it):
                    rows[it].append((team, ep, seat, sum(sold[it].values()), hr))
            n += 1
        del d
    # the live game (not in the p6 cohort): sid 56539078 seat 0 = cha22_champion vs 'Jules'
    lp = os.path.join(C.ROOT, "results", "ep_56539078_replays", "episode-113676899-replay.json")
    live = []
    if os.path.exists(lp):
        with open(lp, encoding="utf-8") as fh:
            d = json.load(fh)
        sold, rev, shed = day_tables(d, 0)
        for it in ITEMS:
            hr, over, _ = headroom(sold.get(it, {}), rev.get(it, {}), shed.get(it, {}))
            if sold.get(it):
                live.append((it, sum(sold[it].values()), hr))
        del d

    L = ["# P30 - reallocation headroom on our own tape", "",
         "engine pin %s | our reference seat-episodes analysed: %d | live game 113676899 seat 0"
         % (ke.__version__, n), "",
         "Headroom = revenue achievable by re-timing THE SAME UNITS onto better-priced days, subject to",
         "prefix availability (a unit cannot be sold before it exists). Upper bound: it ignores that our",
         "own earlier sale would add to the shared pool and lower that price (`:659-660`).", "",
         "| item | n seat-eps | mean units | mean headroom /seat | median | max | total headroom |",
         "|---|---:|---:|---:|---:|---:|---:|"]
    prem_tot = 0.0
    for it in ITEMS:
        r = rows.get(it) or []
        if not r:
            continue
        hs = [x[4] for x in r]
        us = [x[3] for x in r]
        L.append("| %s%s | %d | %.0f | **%+,.0f** | %+,,.0f | %+,.0f | %+,.0f |".replace(",", "") % (
            it, " [PREMIUM]" if it in PREMIUM else "", len(r), st.fmean(us), st.fmean(hs),
            st.median(hs), max(hs), sum(hs)))
        if it in PREMIUM:
            prem_tot += st.fmean(hs)
    L += ["", "**Mean premium-item headroom (MILK+WOOL+STRAWBERRY+MELON) = %+,.0f coins/seat**".replace(",", "")
          % prem_tot, "",
          "Compare with p28c's cross-team price of the same mechanism: **+3,341/seat at 100% capture,",
          "86% of it in WOOL+MELON**. If our own headroom is materially below that, the prize is not",
          "collectable by a schedule because our tape has no slack to move - the constraint is the",
          "shed/availability, not the decision.", "", "## live game 113676899 (cha22_champion vs Jules)"]
    if live:
        L += ["", "| item | units | headroom |", "|---|---:|---:|"]
        for it, u, hr in live:
            L.append("| %s | %d | %+,.0f |".replace(",", "") % (it, u, hr))
        L.append("")
        L.append("premium total headroom in the live game: %+,.0f".replace(",", "") % sum(
            hr for it, _, hr in live if it in PREMIUM))
    txt = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
