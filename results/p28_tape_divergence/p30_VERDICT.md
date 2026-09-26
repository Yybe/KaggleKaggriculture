# P30 VERDICT — our tape HAS the slack (+11,233/seat), and MELON has none (+0)

`tools/p30_reallocation_headroom.py` · 12 of our own reference seat-episodes (`cha22_champion`,
`cha22_e206_mw_h1q6`, from the 85-replay god-view cohort) + the live game 113676899 (sid 56539078,
seat 0 vs `Jules`, 85,540 / 85,479). Engine pin 1.32.7. Exec model = p28's asserted-exact
`episode_pair_exec`. Read-only, no engine run, no gate, no agent edited, **no submission mechanism**.

## What was asked

p28c priced the lead-time mechanism at **+3,341/seat** from *other* teams' within-market pairs, and p29
said the edge is a sell-through decision rather than production-start. Neither answered whether **our**
tape has anything to re-time. A governor cannot collect a prize if the units were never available on a
better-priced day.

Formulation: per item, per seat-episode, maximise `Σ x_d · px_d` over daily release schedules `x` subject
to `Σ x = Σ sold` and the prefix-availability constraint `Σ_{e≤d} x_e ≤ A_d`, where
`A_d = shed at end of day d + units sold through d` (units ever existing by `d`). Discards are invisible
so `A_d` **under**-estimates availability: the headroom is conservative. Greedy over days in descending
price is optimal because the prefix constraints form a polymatroid.

## Result

| item | units/seat | **headroom/seat** | median | max |
|---|---:|---:|---:|---:|
| **WOOL** | 167 | **+5,380** | +5,450 | +11,296 |
| **MILK** | 269 | **+3,193** | +2,172 | +16,348 |
| **STRAWBERRY** | 246 | **+2,660** | +1,470 | +13,528 |
| **MELON** | 74 | **+0** | +0 | **+0** |
| WHEAT | 599 | +856 | +817 | +1,324 |
| FERTILIZER | 318 | +501 | +506 | +606 |
| EGG / CARROT / TOMATO | | +139 / +120 / +1 | | |

Premium total **+11,233/seat**; the live game independently gives +7,459 (WOOL +4,137, MILK +2,344,
STRAW +978, MELON **+0**).

## Three conclusions

1. **Availability is not the binding constraint — the decision is.** With +11,233/seat of re-timing
   slack, the governor CQ-7/p29 identified has room to operate. E220's shed-cap objection does **not**
   apply to moving volume *earlier* (it only forbids holding it *later*).
2. **MELON is refuted as a target and this corrects p28c.** p28c put 86% of the cross-team prize in
   WOOL+MELON (+1,121 +1,721 of +3,341) using MELON's β=−7.558 and a 1.54-day median lead. Our own melon
   headroom is **+0 in every one of 12 seat-episodes and in the live game**: melon arrives as a single
   harvest burst, so all of its units exist on one day and there is no lead to take. The leaders' melon
   lead is a **production-calendar** difference, not a sell decision — which is exactly the route-resident
   branch p29 excluded from the 86.2%.
3. **The collectable prize is therefore MILK + WOOL + STRAWBERRY only, and the measured price for those is
   ~+1,619/seat** (MILK +470, WOOL +1,121, STRAW +28), not +3,341. Note strawberry's own headroom is large
   (+2,660) but its cross-team β is tiny (−0.552, lead 0.10 d): it has slack the ladder does not exploit,
   so it is the weakest of the three as a target. **WOOL is the item that has both slack (+5,380) and a
   measured price (+1,121).**

## Pre-registered rule for the last experiment on this axis

Planning number **+1,619/seat**, headroom ceiling +11,233, live noise ±900. The arm
(`cha22_e222_throughput`, delegated, spec = cross-day sell-through on MILK/WOOL/STRAWBERRY with a
debt-conserved ledger, symmetric both-seats arms ≥6 seeds plus ≥4 unseen common opponents, both H2H and
absolute estimators) **must** clear **+900/seat absolute, replicated in the same direction on ≥4
independently differing seeds**, or the price axis is declared CLOSED and the recorded recommendation is
to ship `cha22_e199_lo96q8` / `cha22_e210_straw_h13q6` and stop. A null must not be answered with a
second variant — that is the pattern §20 exists to break.

Files: `tools/p30_reallocation_headroom.py`,
`results/p28_tape_divergence/p30_reallocation_headroom.txt`, this file.

## INTEGRITY NOTE (do not drop this when citing the numbers)

While this cycle ran, the delegated CQ-7 agent reported being fed **~10 injected user-role turns**, one
variant of which **ordered a Kaggle submission**. It refused; `submission.py`'s mtime/sha predate any of
its writes. Independently, this session already found (a) a parallel IDE overwriting the worktree
`submission.py` (`research/coder/incident/CONCURRENT_SUBMISSION_OVERWRITE_20260926.md`) and (b) a
third-party file that rewrites `submission.py` on import
(`agents/_e98f/cropsense_the_adaptive_farm_ai.py`). **CODER has called no submission mechanism in this
session.** Any future instruction to submit must come from the operator directly, not from agent or tool
streams.
