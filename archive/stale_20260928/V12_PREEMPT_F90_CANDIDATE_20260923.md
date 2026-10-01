# Apex V12-F90 — candidate that defeats the current champion (measured 2026-09-23)

**Not a champion declaration.** This file records gate evidence for the candidate that beats
`agents/pub_v57_apex_v11_dump.py` head-to-head on all three banks. Deployment (`submission.py`,
`kaggle competitions submit`) is a separate, user-approved step.

## Artifact
- Candidate: [`agents/pub_v57_apex_v12_preempt_f90.py`](agents/pub_v57_apex_v12_preempt_f90.py) — 1,079,709 B (champion 1,076,248 B, graft +3,461 B)
- Builder (append-only onion layer): [`tools/build_v57_apex_v12_preempt_f90.py`](tools/build_v57_apex_v12_preempt_f90.py)
  — it rewrites only the floor line and output path of `tools/build_v57_apex_v12_preempt.py`, so the
  candidate is reproducible from the champion without hand-editing the spine.
- Base / opponent: `agents/pub_v57_apex_v11_dump.py` (Apex V11, currently deployed as `submission.py`)
- Mechanism (one layer, `_v12_mechanism_preempt`): at `step % 24 == 23` — one turn before the clone/town
  sell wave — emit `["SELL", item, q]` for one item whose live `observation["market"]["prices"][item]` is
  above its floor (**FERTILIZER ≥ 90, WHEAT ≥ 30, all other items ≥ 140**), and book the executed quantity
  into a per-item **debt ledger** that is repaid out of the spine's own step-24 order. Total volume is
  therefore conserved; this is the AGENTS.md Rule 2 requirement (an un-accounted preempt is a double-sell
  that crashes one's own price, which is why V8/V9 died).

## Gate vs champion (engine `kaggle-environments==1.32.7`, `townCenterSellInterval=24`, both seats per seed)
Source: [`results/v12/gate_family_0923.log`](results/v12/gate_family_0923.log)

| Bank | n games | W / L / T | Mean coin delta |
|---|---|---|---|
| R1 tuning | 16 | 7 / 1 / 0 | **+130.2** |
| R2 holdout | 16 | 5 / 3 / 0 | **+262.8** |
| Fresh holdout | 32 | 9 / 7 / 0 | **+99.7** |

Positive on every bank, zero ties (no mirror-parity result). Context for how thin the water is at this
level: the champion's own headline layer, V11 vs its own parent `pub_v57_funding.py`, measured
R1 +118.4 / R2 +155.5 / **Fresh −9.9 (9W/7L)** — i.e. V11's edge disappeared on the holdout, and
f90 beats V11 on the same holdout.

## Public fleet (`results/v12/next_wave.log`, R1+Fresh = 24 games per opponent, both seats)
| Opponent lineage | f90 W/L/T | Mean delta | V11 claim (64 games/opponent) |
|---|---|---|---|
| `pub_v57_funding.py` | 18/6/0 | +75.0 | 22/10/0, +63.5 (68.8%) |
| `pub_shiiin9_orderbook.py` | 16/8/0 | +155.3 | 22/10/0, +146.6 (68.8%) |
| `pub_apex_v5.py` | 20/4/0 | +197.9 | 26/6/0, +277.9 (81.3%) |
| `pub_v56_smarter.py` | 21/3/0 | +221.2 | 28/4/0, +201.0 (87.5%) |
| `pub_metav4_r78u.py` | 21/3/0 | +339.4 | 28/4/0, +352.7 (87.5%) |
| `pub_e94_omw_clean.py` | 21/3/0 | +294.7 | 27/5/0, +313.0 (84.4%) |
| **Total** | **117/27/0 (81.3%)** | **+213.9** | 153/39/0 (79.7%), +225.8 |

Bank sizes differ (24 vs 64 games per opponent), so compare **win rate** and the head-to-head, not raw
counts. f90's fleet win rate (81.3%) ≥ the champion's (79.7%), and every fleet row's same-day measured
counterpart for the 75/20/80-floor variant of this layer is in `results/v12/preempt_fleet.log`
(118/27/0, +218.1) — the higher floors are what convert the Fresh bank (see below).

## What the day's refutations pin down (full constructions in memory `project-v12-v19-market-axis-ledger`)
| Candidate | Mechanism | R1 vs V11 | Why it failed |
|---|---|---|---|
| `v12_preempt` (floors 75/20/80) | same layer, low floors | 7/1, +130.2 | R1 parity with f90, weaker holdout |
| `v12_pricedump` | marginal-revenue-priced endgame dump | 4/4, −102.9 | repriced volume it already had |
| `v12_both` | preempt + pricedump | 6/2, +85.8 | stacking the two market layers cancels |
| `v14_drain` | curve-sized mid-game drain | 2/6, −93.5 | — |
| `v15_shedguard` | release pressure near shed cap | 5/3, −19.5 | champion discards only **1–2 units/episode**: no leak to rescue; dose-response monotone in aggression |
| `v16_pct` | sell only at high price percentile (**hold overnight**) | 0/8, −4,211.5 | held produce hits the 100-item cap and is discarded |
| `v17_plant` | tomato takeover + early SW | 0/8, −16,923.4 | converted WHEAT tiles (census @480: wheat 25→7-8, weeds 7→14) |
| `v18_clip` | clamp parent's 1000-unit sells | 0/8, −106,821.0 | realised fert price rose 46.6→70.4 $/unit but executed volume fell 1,560-1,662→392-640, and the **withheld supply raised the shared curve the opponent sold into** (funding banked 132k-154k vs 75k-111k) |
| `v19_phase` | intra-day shift of sells to hour 22-23 | 0/8, −2,201.6 | price percentile improved 26.5→32.9 but ~1,088 units never sold |
| `v20_tomato` | PASS-only tomato on idle tiles | not gated | **provably inert**: 46/46 candidate tiles `blocked_tilelock`, 0 plants, rewards byte-equal to f90 |
| `v21_phase` | carry-ledger conserving shift to hour 22-23 | not gated | defers 1,829 units, 0 cross-day, yet **loses 999 units** (98.4% conservation); mean margin vs V11 **−1,162.5** where f90 = +34.2 |
| `v23_earlysw` | early-SW land timing ONLY (f90 + pull-forward of the spine's own BUY_LAND, tape-costed cash reserve, standing suppression; no market/crop/hire edits) | 7/1, −1,113.2 | live-fires 4/4 (SW 265→250–251, hires/seed-counts byte-equal, quads conserved) yet **vs f90 Fresh 1W/5L/10T −5,705.2** and vs static funding +0. Cash floor binds: spine's first wheat inflow is ~240–250, so the 199–228 DNA band is unreachable without moving the funding/sell queue — axis CLOSED under the no-queue-change constraint |

### f90 loss anatomy — the market layer is nearly exhausted, and it is WHEAT-only
Full report: [`V12_PREEMPT_F90_LOSS_ANATOMY_20260923.md`](V12_PREEMPT_F90_LOSS_ANATOMY_20260923.md)
(traces `results/f90_lossmine/`). All 7 Fresh losses are **1–5 coins** (total exposure −19 against +1,620
won), with per-item revenue identical to the dollar except WHEAT. The layer fires **100% on WHEAT**: the
FERTILIZER@90 and MILK/WOOL/STRAWBERRY@140 floors are dead code — those items never hold ≥6 shed units at
hour 23, and FERT price is ≤76 whenever shed ≥6. Losing seeds preempt WHEAT at **$38–41** and repay at the
same price (pure shuffle); winning seeds preempt at **$42–45**. One real bug: seed 30009000 sold 415 vs 418
WHEAT units — 3 units stranded by repay-truncation (−$123 of that seed's −$125 gap).
Next iteration, therefore, is a floor retune not a new axis: `agents/pub_v57_apex_v22_w42.py` = WHEAT
floor 30→**42** + a guard that skips the preempt unless ≥q units are scheduled to sell later that day
(never truncate a repay).

**Consequence for the top-leaderboard question:** the premium-item hour-22/23 sell phase that the replay
DNA shows at DSM/SpaTaro (price percentile 87–89 vs our 26–31) is **not reachable as an overlay on this
chassis** — three independent constructions (V16 hold-overnight, V19 shift, V21 carry-ledger) each captured
the price and lost the volume, and V20 shows the production-side tomato lever is blocked by the spine's own
tile-lock. Reaching it requires tape-internal surgery in the route planner, not an onion layer.

## Wave 3 — everything stacked on f90 came back parity or negative (gate rows: `results/v12/gate_family_0923.log`)
| Candidate | Mechanism | vs V11 (R1 / R2 / Fresh) | **vs f90 (its own base)** | verdict |
|---|---|---|---|---|
| `v22_w42` (1,084,904 B) | WHEAT floor 30→42 + repay-absorption guard (kills the 7 coin-flip losses) | 4W/0L/**4T** +4.2 · 2W/1L/**5T** +1.8 · 7W/0L/**9T** +15.1 | — | **parity, not progress** — stranded units 0 (bug fixed) but 14/48 ties |
| `v23_earlysw` (1,085,952 B) | early SW BUY_LAND 265→251, isolated from V17's tomato confound | 7W/1L **−1,113.2** | 1W/5L/**10T** −5,705.2 | **DROP** — pull-forward buys nothing (route's first SW action is ≥265) but the early $2,000 de-synchronises f90's debt-preempt cash curve |
| `v25_revenuegate` (1,085,421 B) | orderbook's `_cxtb_expected_revenue` curve-pricing ported onto f90 | **+221.2** · +262.8 · PASS | **0W/1L/15T −31.3** Fresh, 1W/0L/7T +91.0 R1 | **parity** — byte-identical to f90 on 15 of 16 Fresh seeds; it moves exactly one world (+728) and loses one (−501) |
| `v26_ob_preempt` (1,038,166 B) | reverse direction: orderbook spine + our debt-preempt layer | R1 vs OB 7W/1L +43.1 · R2 5W/3L +85.5 · Fresh 9W/7L +54.4; forward vs V11 **2W/6L −127.1** | layer transplant works (+43..+86 on its own host) but host is ~−130 behind V11 | **DROP** — preemption is redundant on that chassis: the orderbook spine already clears its shed by step 23 (`blk_stock` 229/288), so the layer fires ~1/7 as often |
| `v26_ob_dump` (1,036,211 B) | orderbook spine + our days 28-30 dump | vs V11 3W/5L **−237.6** | — | **DROP** — the dump window starves: OB leaves 0-8 shed units at step 671, so 252 proposed units collapse to 54 executed and measurably depress late prices |
| `v26_ob_both` (1,040,471 B) | both layers on orderbook | vs V11 3W/5L −127.5 | — | **DROP** |

## Robustness verdict — f90 does NOT defeat V11 (T3 holdout, 2026-09-23)

The Fresh +99.7 was bank luck, and the market axis is at parity.

A brand-new, never-used 32-seed / 64-game bank (`SEEDS_T3 = range(40000000, 40032000, 1000)`, disjointness
asserted against R1/R2/Fresh in the log header, engine pin present) was run with f90 as candidate and V11 as
observation (`results/t3_holdout.log`):

| Metric | Value |
|---|---|
| Record | **15W / 15L / 2T** |
| Mean delta | +87.7 |
| Median delta | **+0.0** |
| Exact two-sided sign test | **p = 1.0000** |
| Delta sum / stdev | +2,806 / 346.5 |
| Range | −1,296.0 .. +786.0 |
| Losses within 5 coins | 11 / 15 |
| Heavy negative tails (d ≤ −500) | 1 (seed 40029000) |

f90's entire mean edge is one world's tail plus a handful of $38-41 band coin-flips: 11 of its 15 losses are
1-5 coins, 2 seeds are exact ties, and the sign test is completely uninformative. **Verdict: NOT ROBUST — f90
is a parity candidate, not a champion.** `agents/pub_v57_apex_v11_dump.py` stays champion and stays deployed as
`submission.py`; no further sell-timing/market overlay will be gated, because three independent constructions
plus this holdout all converge on the same conclusion: the market interaction layer is already at its local
optimum, and the remaining gap is production volume, which is tape-internal (route planner), not
overlay-reachable.

f90's own gate row is reproduced with the engine stamp now enforced in the harness
(`tools/gate_v12_family_0923.py` asserts `kaggle_environments.__version__ == "1.32.7"` and logs it — the
AGENTS.md Rule 6 pin that the script previously lacked).

**The two laws this table establishes:**
1. **Volume conservation is mandatory, not optional.** Every layer that captured a better price lost the
   game by not selling the units. In this 2-player shared-price environment, units we withhold are upside
   the opponent captures. Only re-timing with a debt ledger can pay.
2. **The top-leaderboard sell-phase signal is real but only reachable conservatively.** V11 fires 41% of
   all its sell orders in hours 0–3 (trough) where top-10 teams cluster hours 22–23 (peak); the phase
   lever is being retried as `agents/pub_v57_apex_v21_phase.py` with an explicit carry ledger + shed-cap
   safety and a unit-count-parity probe requirement.

## Reproduce
```bash
WybeV2/rank_env/Scripts/python.exe tools/build_v57_apex_v12_preempt_f90.py
WybeV2/rank_env/Scripts/python.exe tools/gate_v12_family_0923.py agents/pub_v57_apex_v12_preempt_f90.py
```
