# E256/E257 — why the tetsutani Godview V2 row scored lower, and what beats the tetsutani spine

Date 2026-09-29 (IST). Engine pin `kaggle-environments==1.32.7`, `townCenterSellInterval=24`,
`episodeSteps=720`. All live numbers below re-queried from the Kaggle API on 2026-09-29 at 14:09 UTC;
no saved leaderboard CSV and no cached episode list was used.

## 1. Headline: the deployed graft is a no-op, and the score gap is not evidence

| ref | file | submitted (UTC) | live score | episodes | W/L/T | mean per-episode margin |
|---|---|---|---|---|---|---|
| 56672630 | `agents/tetsutani_godview_v2.py` = `submission.py` (sha1 `10c610676c31`) | 2026-09-29 10:47 | **1568.3** | 55 | 40W/12L/3T | **+10,267** |
| 56653474 | `tetsutani_step1009_fortyfirst_closure.py` (its parent) | 2026-09-28 22:17 | 1851.7 | 135 | 53W/48L/34T | +2,093 |
| 56644648 | `agents/cha22_champion.py` (bar of record) | 2026-09-28 15:03 | 1742.6 | 87 | 51W/30L/6T | +4,637 |

The grafted file earns **more per episode (+10,267) than the parent it was supposed to improve (+2,093)**.
Its lower `publicScore` is the documented rating artifact, not a regression: a fresh row starts at a ~700
prior and needs ~130 games to settle, and the parent had 135 games while the child had 55 at read time.
The child's own 12 losses have median −568 (mirror noise), so nothing in the live data says the graft hurt.

**The reason it could not help: the V2 layer never modifies an action.**

`tools/build_tetsutani_godview_v2.py` gates both of its mechanisms on `isinstance(action, list)`:

* the h23 preemption converts only `action[0] == "PASS"` or appends to `action[0]` being a list;
* the crop layer reads `money` from `observation["private"]["farm"]["money"]`.

Neither holds. The spine returns a **dict** (`action['hands']`, `action['farmer']`, `action['market']` —
see its own telemetry block `tuple(farm['hands'][0]) == (4,4) and action['hands'][0] == ['DROP']`, and
every replay action recorded in `TETS_COUNTER_20260929/raw/`), and `observation['private']` has exactly
the keys `inventories`, `seeds`, `shed` — there is no `private.farm`, so `money` is permanently `0` and
the `money >= 250` crop branch is unreachable. Consequence: output equals the parent's output on every
step, which is what the gate measured (0W/0L/32T over 64 games). The reported
`_TG2_PREEMPT_FIRES = 40` counted *opportunities seen*, not actions changed; `_TG2_CROP_FIRES` was never
reported at all. This is the AGENTS.md Rule-1-phase-5 failure mode written down in advance: a counter that
increments before the mutation guard reads as a live layer on an inert graft.

## 2. Loss anatomy: where the tetsutani spine actually loses (43 replay pairs, today's episodes)

Set: **34 of our own losses** (12 `tetsutani_godview_v2`, 16 `tetsutani_step1009`, 6 `cha22_champion`
controls) + 9 winning controls (3 per file) = **43 replay pairs**, both seats parsed at step level,
seats parsed at step level, `TETS_COUNTER_20260929/out/farm_anatomy.csv` (86 seat-episode rows) and
`paired_gaps.csv`. Heavy-loss subset = margin ≤ −3,000 (n=17, mean −9,959); tail subset = margin > −1,000
(n=8, mean −364).

**When the loss is created.** Mean money gap (ours minus the seat that beat us) by day over the 34 losses:
+2,957 at day 10, +2,032 at day 12, then a monotone reversal — −1,900 by day 18, −3,634 by day 24,
−5,572 at day 29. We are ahead for the first half of the run and are out-earned from day 16 onward. The
tail class (mirror games) shows no production column moving.

**What the winners do differently, ranked by how consistently it appears in a heavy loss**
(mean gap, median, count negative out of 17):

| column | mean | median | negative | reading |
|---|---:|---:|---:|---|
| `op_FERTILIZE` | −48.6 | −53 | 14/17 | they apply ~50 more fertilizer doses |
| `tile_days_fert` | −1,226 | −476 | 14/17 | ~1.2k more fertilised tile-days |
| `op_COLLECT_FERTILIZER` | −108 (heaviest ep) | — | — | herd fertilizer left uncollected |
| `op_FEED` | −71 (heaviest ep) | — | — | animals under-fed |
| `op_PASS` | +112 (heaviest ep) | −3 | 18/34 | we idle hands they spend |
| `td_TOMATO` | −1,184 | 0 | 8 neg / 8 zero | in 8 worlds they run tomatoes, we plant none |
| `tile_days_planted` | −727 | −23 | 10/17 | less planted acreage |
| `tile_days_empty` | +727 | +23 | 5/17 | more owned-but-idle land |
| `td_STRAWBERRY` / `td_MELON` | −613 / −171 | 0 | 7/6 | high-value crops under-weighted late |
| `td_WHEAT` | **+1,320** | +866 | 4/17 | we hold wheat acreage where they hold cash crops |
| `sell_orders` | −65 | −13 | 11/17 | thinner sell cadence |
| `quads_max`, `unlock_SE`, `hires_max` | ~0 | 0 | rare | **not** discriminators this cycle |

Read together: the deficit is a **mid-game nutrient-and-labor conversion failure**, not a capacity or
land-timing failure. Quadrant count, unlock steps and hires are at parity in the heavy losses; what moves
is fertilizer doses, fertilised tile-days, feed/collect throughput, idle hands, and the crop mix those
inputs buy (wheat for tomato/strawberry/melon).

**The fertilizer paradox, per heaviest loss (ep 115160633, −27,662, vs `3정훈`).** We bought **104**
FERTILIZER units at market while they bought **17**; they collected 486 doses from animals against our 378,
fed 399 against our 328, and applied 195 against our 142. They ended with more fertilised acreage
(8,065 vs 7,604 tile-days) on less planted acreage (30,465 vs 32,669), and sold 245 EGG to our 87. We spent
+4,128 more and earned 23,534 less. The same signature repeats in ep 115233176 (−17,952) and ep 115079215.

So the single largest wrapper-expressible farm-decision mistake on this spine is: **paid fertilizer bought
while produced fertilizer is left on the animal, and hands left on PASS while standing on the tile that
would convert it.**

## 3. Counter model built from that mistake — E257 `tetsutani_e257_fertflow.py`

One mechanism, append-only graft (`TETS_COUNTER_20260929/build_e257_fertflow.py`, base sha256 prefix
`55be5d5f`, output 1,198,759 B, +2,678 B, sha256 prefix `979522c9`, `py_compile` PASS):

For every unit slot whose committed op is exactly `["PASS"]`, look at the tile the unit is standing on
(`farm['tiles'][pos[1]][pos[0]]`, engine order confirmed at `kaggriculture.py:314-320`) and its own
inventory (`private['inventories'][idx]`, idx 0 = farmer):

1. animal tile with `fertilizer_available` → `COLLECT_FERTILIZER`;
2. else animal tile, `fed_today` false, carrying ≥1 WHEAT → `FEED`;
3. else PLANT tile with `fertilized_until_day < day` and carrying ≥1 FERTILIZER → `FERTILIZE`.

Committed tape ops are never displaced and no market order is added, so the layer is cash-neutral by
construction and works only on idle labor plus already-carried stock. Engine legality for all three ops is
`kaggriculture.py:475-521`. Correcting the V2 mistake, the layer is written against the **dict** action
schema and the probe asserts `converted > 0` (mutations), not opportunity counts.

Gate protocol and results are in §4 (`TETS_COUNTER_20260929/out/gate_run.txt`, `e257b_absolute.csv`).

## 4. Gate results

Pre-registered rule, fixed before any gate number was read (E224, applied verbatim): promote only if
**every** out-of-fleet lineage's paired mean is > −1,000/seat, **no** paired row is worse than −2,500, and
the pooled mean is positive. H2H against the parent is read as an inertness test first: ties mean the layer
never fired, not that it is safe; parity is not progress.

Engine `kaggle-environments 1.32.7` asserted in every worker; seeds `15243000 + 1117*i`, `i in [11,15)`
(registered `experiments/seeds.json::E257`, disjoint from E224/E253 bands); both seats per seed.
Raw: `TETS_COUNTER_20260929/out/gate_run.txt`, `gate3_run.txt`, `e257b_absolute.csv`,
`e2589_absolute.csv`, `e2589_summary.json`.

| arm | mechanism | liveness probe | H2H vs parent | paired absolute vs 4 out-of-fleet lineages (n=32 rows) | verdict |
|---|---|---|---|---|---|
| E257 `tetsutani_e257_fertflow.py` | idle hand → COLLECT/FEED/FERTILIZE | 51–68 conversions/game, errors 0, no ties | R1 n=16 **0W/8L/0T**, mean **−366.9**, per-seed −67 … −586 | mean **−79.1**, median −29.0, 11/32 favour, worst −458; all 4 lineages negative (−31.8 … −138.9) | REJECT |
| E258 `tetsutani_e258_fertbuy_veto.py` | drop `BUY_PRODUCT FERTILIZER` when own stock covers it | 15–19 orders dropped (42–53 units), errors 0 | 2 probe seeds −255, −1,718 | mean **−374.8**, median 0.0, 12/32 favour, worst −3,075; lineages −618, −256, −712, +87 | REJECT (worst < −2,500, 3 of 4 lineages negative) |
| E259 `tetsutani_e259_idle_replant.py` | idle hand on owned-empty tile → PLANT own seeds | 9 and 17 conversions, errors 0 | 2 probe seeds −1,290, −3,288 | mean **+615.5** but median **−2,101.5**, only 9/32 favour, worst **−31,280**; +3,551 / +1,322 / +3,547 on three lineages, −5,959 on `a15_full_wheat` | REJECT (rule fires on worst row, on the negative lineage, and on the win share) |
| E260 `tetsutani_e260_collect_dump.py` | idle hand → COLLECT_FERTILIZER **and** cadenced market dump of the surplus (`step % 4 == 3`, ≤12/step, keep 5) | 25 and 70 collects with 7 and 6 sell orders (23 and 13 units), errors 0, no ties | 2 probe seeds −58, −20 | n=64 rows: mean **−12.7**, median **0.0**, worst −605, win share **39 %**; lineage means +11.2, −15.2, −58.3, +11.5 | REJECT (not positive), but it is the **control that localises the loss** |

**E260 is the decisive negative control.** Adding the shed-release valve to E257's collection moves the arm from
−79.1/seat (E257) and −366.9 (H2H) to **−12.7/seat with median exactly 0.0** — i.e. the whole E257 regression
was shed displacement, exactly as H-083 predicted. What remains after the fix is zero. The spine does not
convert collected fertilizer into money, because its tape does not schedule the applications that extra
fertilizer would feed. Collection is only worth what the plan's fertilizer demand is worth, and on this spine
that demand is already met by market purchases (E258 shows the reverse test as well: vetoing those purchases
costs 375/seat, so the demand is real).


**Rule disclosure.** The E224 threshold is a regression bound, so its literal form printed `PASS` for E257
(−79.1/seat is above −1,000); the pooled sign and the 11/32 win share are negative, so the arm is rejected.
From this experiment the operating bar is stated as written above: a candidate must have a **positive** pooled
paired mean, no catastrophic row, and no negative lineage. Reporting a lax rule as a promotion is how an inert
graft reached the board in the first place.

**E257 - why the obvious fix fails.** Converting idle hands into fertilizer collection is mechanically live
(~60 mutations a game) and still loses. Shed capacity is 100 units and collected fertilizer is inventory,
so extra collection displaces produce (`_drop_inventories_to_shed`, `kaggriculture.py:843`). The winners'
higher `COLLECT_FERTILIZER`/`FEED` counts are a **consequence** of a bigger herd turning throughput, not an
action a wrapper can buy. Same law as the cha22-era "shed is not a bank".

**E258 - the paid-fertilizer leak is not a leak.** Blocking the market buy while own stock exists keeps the
cash and still loses 375/seat: the spine's plan consumes that fertilizer within a few steps, so the veto
starves applications and the yield loss exceeds the purchase. The 104-vs-17 buy asymmetry in the replay is a
symptom of a different herd size, not an independent mistake to bank.

**E259 - the only positive direction, and it is bimodal.** Idle land is worth planting: the mean is +615/seat
and three of four lineages are positive (+3.6k, +1.3k, +3.5k). But the median is −2,101/seat, only 9 of 32
rows favour it, and the worst row is −31,280 - two worlds carry the entire mean (the documented few-worlds
law). A planted tile also consumes the worker's turn and the tile's water/labor budget, so on `a15_full_wheat`
the same layer loses 5,959/seat. **Reopen condition:** a seed-gated, day-windowed variant that plants only
when a wheat/strawberry seed is otherwise going unused for the rest of the episode, screened on ≥8 seeds with
the per-row distribution printed, not the mean alone.

## 5. What this means for the deployed rows

* The submitted `tetsutani_godview_v2.py` did not damage the farm plan - it never ran. Nothing regressed in
  dollars; the rating gap is the immature-row artifact.
* Three production-side counter arms built from the replay-measured mistakes all fail the pre-registered
  rule, and the fourth (E260) explains the first: give collection a shed release valve and the arm lands on
  exactly zero (median 0.0, −12.7/seat). On this spine as it stands, the fertilizer/collect/land gaps visible
  in the losing replays are **not wrapper-expressible**: they are properties of the tape's herd, shed release
  rate and water budget. That is the same conclusion the cha22 lineage reached from the other direction
  (H-071 overlay ceiling, H-060 land cadence).
* `submission.py` is untouched by this experiment and the two active slots are
  `56672630` (inert godview_v2) + `56671452` (leoprovorov `a-song-of-ice-and-fire`, live **147.5**).
  Restoring a strong file into an active slot is an operator browser/CLI action, not a research step; the
  inert graft means swapping slot one back to `cha22_champion` or `step1009` requires no new gate evidence
  beyond E224/E253 and the H-081 clean-panel result (**cha22_champion stays, do not ship step1009**).

