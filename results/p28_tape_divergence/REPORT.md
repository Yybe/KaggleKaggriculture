# P28 / CQ-6b — WITHIN-EPISODE TAPE DIVERGENCE ATTRIBUTION

**STATUS: DECISIVE ON THE OBSERVATION, NOT YET ON CONSTRUCTIBILITY.**
Engine pin `kaggle_environments==1.32.7`. Exec model reproduces `phase_p6.jsonl` `sell_units_exec` on
**every** `(ep,seat,item)` cell of **85** replays (**0 mismatches**), so the prices walked below are
applied to exactly the quantities the field report publishes. Read-only. No agent edited, no gate run,
no submission mechanism called. `results/p6_field_20260925/**`, `results/p6_godview_replays/**`,
`WybeV2/datasets/**` untouched.

---

## TASK

The offensive's whole price axis hung on a control that p17 reported as **impossible**: `"episodes
where OUR submission played a TOP-13 team: 0 <-- the shared-price-path test against our own agent is
IMPOSSIBLE in this cohort"` (`results/p17_realisation/REPORT.md` E9).

Two routes were tried to obtain it. Both are closed:
* the CLI route works (`kaggle competitions replay <ep>` → 32.5 MB in ~1 s; `tools/fetch_episodes.py`
  429s), and our newest live episode (113676899, 2026-09-26) is us 85,540 vs **Jules** 85,479 — not a
  top-13 team. Our live rating band (~1,600) never meets theirs (~3,093), so **a us-vs-top-13 episode
  does not exist and cannot be manufactured without submitting**, which is the operator's call.
* p19 falsified the leader-side premise anyway: **0 of 13** leaders hold per-item peak daily release at
  or below the town's ~10-13 u/day, on 7/7 items, on two series that differ by 30%.

So the question was moved to where the data **does** exist. p17 E8: inside one shared market two leader
tapes land within **9.9%** of each other on the median item-pair — but that means a substantial minority
**diverge hard**. This tool asks what separates them.

> **When two tapes in ONE market realise different per-unit prices on the SAME item, which tape action
> distinguishes the higher-realising one — and is that action portable to our spine?**

## METHOD

`tools/p28_tape_divergence.py`, one run, no engine simulation.

1. **Executed units** per `(ep, seat, item, step)` from `tools/p19_replay_exec`'s shed model (the
   `record()` model: handles `PICKUP` withdrawal, `DROP`-whole-hand, the 10-order cap, debits the shed
   in queue order). Re-run at step granularity and **asserted equal to `phase_p6.sell_units_exec` on
   every cell** — the report aborts if any cell differs. Result: 0 mismatches / 85 replays.
2. **Prices walked per unit through the pinned engine's own `market_price()`**, from the **recorded**
   `obs[step-1].market.inventory` (pre-action state), in the engine's lockstep
   (`kaggriculture.py:595-628`: both players quoted at the *same* pre-commit inventory, **seat 0
   commits first**, a `SELL` at `px>1` increments the shared inventory `:659-660`). Never `obs[step]`
   prices — post-walk prices bias `px/base` low ([[project-exact-price-attribution-law]]).
3. **One symmetric pass per episode**: both seats' `SELL` **and** `BUY_PRODUCT` commits walk the same
   inventory, so the trajectory cannot depend on which seat is being scored. (The first draft made our
   own buys invisible while the opponent's were visible — an asymmetry that would have produced a
   different price for each seat by construction. Discarded before the run.)
4. Paired comparison over `leader-vs-leader` episodes only, per item, both seats ≥20 executed units.
   Winner = higher exec-weighted realised price. Sign-flip permutation test, 20,000 draws, seed 20260926.

Variables: `px` (realised exec-weighted price), `mod23` (% of units sold at `step%24==23`, the spine's
preempt slot), `hour` (mean hour-of-day of sale), `day` (mean day of sale), `inv` (mean shared-pool
inventory at the moment of sale), `maxrun` (largest single executed order), `nsell` (number of executed
sell events).

## RESULT

**578 paired `(ep,item)` cells. Median relative gap 0.054. 18.9% (n=109) exceed p17's own 15%
threshold.** The divergence is real and it is a tape property, not only a market property.

**Divergent pairs (rel > 15%, n=109), winner − loser:**

| variable | median | mean | win-share | perm p | reading |
|---|---:|---:|---:|---:|---|
| `px` | 22.41 | 27.89 | 100% | 0.0000 | (definitional) |
| **`inv`** | **−25.75** | −35.16 | **1%** | **0.0000** | winner sells into a pool ~26 units **less glutted** |
| **`day`** | **−3.06** | −3.42 | **6%** | **0.0000** | winner sells **~3 days earlier** |
| **`maxrun`** | **−3.00** | −8.00 | **29%** | **0.0005** | winner's largest single order is **3 units smaller** |
| `mod23` | 0.00 | −1.98 | 28% | 0.0725 | **no separation** |
| `hour` | −0.82 | −0.49 | 42% | 0.2408 | **no separation** |
| `nsell` | −2.00 | −1.58 | 41% | 0.8346 | **no separation** |

Three items of that table are the finding, and two of them are **negative results that kill candidate
axes**:

* **The discriminator is WHEN, measured against the shared pool, not HOW OFTEN, not WHICH HOUR, not the
  `step%24==23` slot.** The preemption slot our spine actually uses (`mod23`) and the hour-of-day
  pattern our own DNA report told us to copy (`Top-10 DNA levers`: "sell at hour 22-23") are both
  **inert inside a shared market** — p=0.07 and p=0.24. `nsell` (cadence/order count) p=0.83.
* **Winner sells earlier AND in smaller maximum orders.** Both point the same way: the winner does not
  wait to accumulate, and does not dump.
* **This is not p17's refuted "season timing".** That test compared *season thirds* across teams
  (5.2/36.3/58.4% vs 5.4/36.2/58.4%, identical). This is a within-episode, per-item, per-pair statistic
  with a 94% win-share and 6% for the loser, i.e. the ordering is near-deterministic, and it is
  **relative to one specific opponent in one specific market**.

Per-item divergence (divergent pairs): MELON 26, WOOL 23, FERTILIZER 22, STRAWBERRY 12, MILK 11,
CARROT 6, WHEAT 6, TOMATO 3. Mean $ gap on the matched volume: **WHEAT 5,116**, STRAWBERRY 4,039,
MELON 3,573, FERTILIZER 2,429, MILK 2,594, WOOL 2,029.

**Label correction for the txt table:** its column reads `median px hi/lo` but the second figure is the
median **gap**, not the loser's price (e.g. MILK 83.2 / 19.7 means hi 83.2, loser ≈ 63.5).

## WHAT THIS RULES OUT

1. **Copying the mod23 preempt slot or the hour-22/23 sell window to raise realisation is ruled out** by
   the pair-level test, not by a gate: those variables do not separate winners from losers inside a
   shared market. This closes the last "just adopt the leaders' sell *schedule shape*" idea.
2. **`inv` is a mediator, not a lever.** Price is a function of inventory by construction, so
   "the winner sells where `inv` is lower" is *nearly* tautological. The informative variables are
   `day` and `maxrun`, which are actions. Treating `inv` as the target would repeat p19's error
   ("price percentile is a symptom of cumulative net release").
3. **It does not resurrect rationing.** p19 stands: 0/13 leaders cap their peak day. The winner here is
   not releasing *less*, it is releasing *first* and in smaller worst-case orders.
4. **It does not contradict E220.** E220 closed *withholding into the shed* (the cap destroys the
   deferred volume, -2,099…-21,112/seat symmetric). The lead-time direction is the opposite: move
   volume **out earlier**, not later. Whether that is affordable against the same shed is the open test.

## CONFIDENCE

**High** on the fidelity of the exec model (0 mismatches, and the assert is in the script and aborts on
failure) and on the within-market statistics (578 pairs, n=109 divergent, perm p<0.0001 on the two
separating variables, 20k draws, fixed seed).

**Medium** on the price walk: it is engine-faithful for lockstep and per-unit commits but takes recorded
inventory as ground truth rather than re-simulating, so any engine path that moves inventory outside the
market phase and the town curve (geese, town-shop edge cases) is absorbed silently. The 1465-cell unit
assert constrains the sell side, not the whole state.

**Low / undecided — the only thing left — on constructibility.** `day`-earlier requires the units to
**exist** earlier, which is a production-start question, not a sell-trigger question; and a "sell now
because the pool is scarce" trigger collides with the shed cap that E220 proved destructive
(parent shed mean 8-9, peak 46, 0/30 days at cap — there is headroom, but only until you *stop*
liquidating same-day).

## WHAT SHOULD HAPPEN NEXT

1. **Separate cause from prerequisite** (cheap, same script): add, per divergent pair, the winner's and
   loser's **first-sale day** for that item and **units committed by each seat before the opponent's
   first sale**. If the winner's edge is a genuinely earlier *first* sale, the axis is production-start /
   tape ordering (high-magnitude, route-resident, and it is exactly what TapeForge was supposed to
   generate). If it is the same first-sale day and only the *later* mass differs, it is a sell-trigger
   rule, buildable as a wrapper.
2. **Symmetric lead-time arm** (the only honest test, per the E220 method law): both seats sell
   premium-item shed at the first step where `market_price(item, inv) / base ≥ θ`, with the
   debt-conserved volume rule so total season volume is unchanged, θ swept, against both-seats-parent,
   ≥4 seeds, reporting **H2H and absolute** (they disagree; [[project-h2h-margin-is-not-absolute-money]]).
3. If (1) says production-start and the tape cannot be re-ordered without the route geometry that E152
   showed is inseparable ("a tape's crop is not separable from its slot geometry"), then the honest §22
   answer on TapeForge is **NO — the substitution is not constructible**, and the recommendation is to
   ship `cha22_e199_lo96q8` and stop the offensive.

## FILES

`tools/p28_tape_divergence.py` · `results/p28_tape_divergence/REPORT.md` (this file) ·
`results/p28_tape_divergence/p28_tape_divergence.txt` ·
`results/p28_tape_divergence/p28_per_seat_item.csv` (578-pair source rows) · `results/p28_run.log`.
Dead instrument, do not revive: `research/coder/redteam/_proto2.py` parses both seats' queues to the
same object (reports FERTILIZER 2361 sold by *both* seats) and fails its own money check on 181/719
steps; `_proto_validate.py` unrun. CQ-5 and CQ-1b both died without writing their reports
(`research/coder/tape/` is empty) — the artifact-dir check caught it, per
[[project-gate-sweep-ops]].
