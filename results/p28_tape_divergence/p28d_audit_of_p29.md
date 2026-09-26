# P28d ADDENDUM — I audited CQ-7's own conclusion and it held. §22 value branch = GO, with a corrected construction

`results/p28_tape_divergence/p28d_audit_of_p29.md` · computed read-only from
`results/p29_leadtime_split/p29_pairs.csv` (109 divergent / 578 paired cells, engine pin 1.32.7,
fidelity asserts inside `tools/p29_leadtime_split.py`). No engine run, no gate, no agent edit, no
submission mechanism called. Commit of this file is separate from CQ-7's own report.

## Why I ran this

CQ-7/p29 concluded **sell-trigger, not production-start** (policy-side = 86.2% of the $ excess;
bucket `A_matched_start` alone = 74.2%). Its headline rested on `winner_first_day - loser_first_day`
being **0.000 median in 81/109 pairs**. I distrusted that, because p29's own `d_hold` row is
**median 0.000 with perm p=0.846** — if the loser is *not* withholding, then a difference in when the
mass lands would have to come from the units *existing* earlier, i.e. route-resident production, which
would flip §22 back to NO-GO. Per [[audit-the-auditor]] I tested it against the availability columns
rather than argue it.

## Test and result

`W_shedday` / `L_shedday` = the day the item **first appears in that seat's shed** (availability),
`L_impossible` = the loser could not have sold at that step.

| set | n | median `d_shedday` | winner-earlier | same day | winner-later | dollar-weighted winner-earlier | `L_impossible` |
|---|---:|---:|---:|---:|---:|---:|---|
| all divergent | 109 | +0.00 | 16 | 83 | 10 | 16.0% | 14 (12.8%) |
| **bucket A** | **81** | **+0.00** | **1** | **79 (97.5%)** | **1** | **1.5%** | **0 (0.0%)** |

`L_prod_lag` in bucket A: median 0.00, mean −0.01.

**CQ-7 is right and my objection is refuted.** In the bucket that carries 74.2% of the money, the two
seats receive the item on the **same day** and the loser was **never unable to sell** — yet the winner
still realised more. The difference is therefore in **how much of the available shed is released per
day**, not in when the units exist. Hold-time being null is not a contradiction: `d_hold` measures steps
held *before the first sale*, while the divergence happens *mid-season in the sell-through rate*.

## Corrected construction (this is the part the earlier documents got wrong)

Every prior attempt moved volume at the **step** level: `step%24==23` preemption, one item per turn,
tick delays, terminal sweeps. p28 (`mod23` p=0.07), p28c (`d_mod23` beta 0.029, CI [−0.02, 0.09]) and now
p29 all say step-level reordering carries **no** price. The mechanism lives one level up:

> **A daily sell-through governor.** On each `step%24` wave, for WOOL and MELON (and only those — p28c
> puts +2,842 of the +3,341 prize there), release a *larger fraction of whatever is in the shed* when
> `market_price(item, inv)/base ≥ θ` and the pool is still inside the item's cliff budget (WOOL 59,
> MELON 158), and a smaller fraction otherwise, with the debt ledger conserving season volume.
> Availability is untouched, so no route surgery, so it is wrapper-expressible.

That is a **different graft from anything in the drain/sluice/preempt family** and it is the only candidate
the evidence now supports. Prize ceiling **+3,341/seat/season** (12.5% of p17's 26,813); at realistic 50%
capture **+1,671**. It clears the ±900 live-noise band, and it does **not** close the gap to the leaders.

## Scope statement, so the cycle cannot drift

* §22 TapeForge: **the tape generator is still NOT required** — p29 shows the money is in a decision the
  spine can be given, not in a route it cannot. The remaining NO-GO branch is the 13.8% production-start
  residual (`C_production_lead`, 15 pairs), which is route-resident and which we are *not* chasing.
* The other ~87% of the gap stays where p28c left it: production (herd scale E104 route-locked, route
  geometry E152). Nothing in p29 changes that.
* Do not re-open: rate, mix, season shape, opponent mix, hour, `mod23`, order size, commit ordering. Each
  now has a within-market measurement, and each is null or seat-average neutral.

Files: `tools/p28c_leadtime_price.py`, `tools/p29_leadtime_split.py` (CQ-7),
`results/p28_tape_divergence/p28c_VERDICT.md`, `results/p29_leadtime_split/REPORT.md` (CQ-7), this file.
