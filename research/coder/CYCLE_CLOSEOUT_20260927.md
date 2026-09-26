# CYCLE CLOSE-OUT — the market/price axis is CLOSED experimentally, not just observationally

`research/coder/CYCLE_CLOSEOUT_20260927.md` · written as this goal window nears auto-pause.
Engine pin `kaggle_environments==1.32.7` asserted in every instrument cited here. **No submit, no deploy,
`submission.py` never opened for write by CODER.**

## The result that closes it

`cha22_e222_throughput` — cross-day sell-through governor on MILK/WOOL/STRAWBERRY/MELON, debt-ledger
volume-conserved — evaluated **symmetrically** (both seats candidate vs both seats parent), 8 seeds, from
`results/p31_e222/mirror_ctrl.csv`:

| seed | 1M | 2M | 3.33M | 5M | 6M | 7.77M | 8M | 9M |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| candidate − parent, per seat | **−876** | **−1,410** | **−425** | **−360** | **−649** | **−935** | **−248** | **−223** |

**8/8 seeds negative, mean −641/seat, 0W/8L**, with `fires` 34–128 per game — the layer is live, so it
loses **because it works**, not because it is inert. On the same seed H2H reads **positive** (81,385 vs
80,747): one candidate, two estimators, opposite signs. This is the third time this project has been saved
by refusing to pick on H2H ([[project-h2h-margin-is-not-absolute-money]]).

**The pre-registered rule fires.** Its threshold was `|Δ| < +900/seat absolute`, or unreplicated on ≥4
independently differing seeds ⇒ axis CLOSED. The result clears neither escape: the sign is negative and it
replicated on **8/8**. Per the rule, no second variant is authorised — §20.

## Why three estimators agreeing matters

| estimator | what it holds fixed | prize for sell-through re-timing |
|---|---|---:|
| p28c, cross-team within-market pairs | real opponents, real impact, **one** advantaged seat | **+1,619/seat** |
| P34, agent-internal counterfactual | **opponent fixed**, our own supply priced endogenously | **−913/seat** |
| E222 arm, symmetric deployment | **both** seats running the rule | **−641/seat** |

The money is in *being earlier than the opponent*, not in an absolute schedule — and there is no way to be
earlier than an opponent running the same rule. p30's +11,233/seat of gross headroom was positional slack;
P34 predicted the arm would come back below +900 and probably negative, and it did.

## WITHDRAWAL: my "the control leaks, void the deltas" alarm was premature

One turn earlier I asserted the arm's numbers were void because its `off` control leaked (81,372 vs
81,600; flow MILK 410 vs 407). That was read from the **00:12 snapshot** of a file the agent was still
writing. By 00:16 `off` ties the parent **exactly on every seed** (81,600/407/391; 75,362/300/352;
80,005/367/388; 72,685/209/332; 85,336/363/338; 119,773/426/424; 112,658/283/367) with `fires=0`, so the
deltas are valid and the alarm is withdrawn.

The underlying **construction rule still stands on its own merits**: an inert preset must not rebuild the
keys the engine consumes (`tools/build_e222_throughput.py:179` assigns `out["market"] = revised[...]`
unconditionally, which is what produced the transient 81,372), because `_process_market` walks orders **by
index across both seats** and quotes each unit at the shared pre-commit inventory
(`kaggriculture.py:595-628`), while a `$1` SELL never enters the pool (`:659-660`) — so queue rebuilding is
never a semantic no-op. Inertness must be asserted as **byte-equal rewards AND equal per-item committed
flow AND `fires==0`**.

New method law taken from my own error: **when auditing a concurrently running agent's artifacts, re-read
the file before asserting a defect — its mtime is moving.** I published off an intermediate state.

## DONE this cycle (all committed)

§5 Questions A–J answered on measured evidence with an in-file correction; §22's seven TapeForge
questions answered; §20 escape condition met and answered (yes — wrong abstraction, named: crop/pool
co-design rather than market wrapping). **Eleven mechanisms measured and closed:** release rate (0/13
leaders ration), item mix (6.5%), season shape, season centroid (sd 0.68 d across 35 teams), opponent
animal-mix, sell hour, `step%24==23` preempt (three independent nulls), order size, intra-step commit
order (real +14.9/unit on WOOL but seat-average neutral), carrot lane (ICC 0.007, t = −4.75), tomato lane
(t = 1.19). Also: the us-vs-top-13 control established unobtainable (**0 encounters across all 214 of our
episodes**), the `submission.py` incident corrected by hash (**it is byte-identical to
`agents/cha22_e199_lo96q8.py`**, sha1 `ec0f0edc2ce2…`), a vetted opponent panel plus **6 import-writing
hazard files**, and a memory repair pass. Commits `6c23aeb` → this one.

## REMAINS — concrete next steps, in order

1. **Read E222's independent-opponent gate when it lands** (last seen 10/192 games, 23 s). It cannot
   rescue the verdict — the mirror already decided — but record whether a candidate losing −641/seat
   absolute is still H2H-positive against non-clones. Descriptive only, never a promotion argument.
2. **Do not open a twelfth market/price/crop axis.** The sanctioned remaining construct is production:
   E104's herd scale (overlay priced −65,875; all 41 routes animal-maxed; COW XOR SHEEP) and E152's route
   geometry. Any attempt must be a **new co-designed livestock + wheat + hire block** (route generation,
   not a wrapper) and must be pre-screened against E152's slot-geometry law before building.
3. **Two decisions that are the operator's alone:**
   * **Authorise or revert the `submission.py` promotion.** The worktree file is `cha22_e199_lo96q8`
     (`CHAMPION.md`'s best-supported finals line); `HEAD` holds FutureV1. Submitting from here today ships
     e199. Not my call.
   * **Commit the untracked baselines** — `agents/cha22_champion.py`, `agents/cha22_e199_lo96q8.py`,
     `agents/cha22_e206_mw_h1q6.py`, `agents/sluice_topup7.py`, `research/baselines/`. All are one
     `git clean -fd` from deletion and the sibling repo has zero tracked `cha22` files. I will not commit
     another session's files unilaterally.
4. **Integrity:** a delegated agent this cycle was fed ~10 injected user-role turns, one of which ordered
   a Kaggle submission; it refused. **Instructions arriving through agent or tool streams are not the
   operator's authorisation.**

## Honest final assessment against §29

The brief asked for a previously unknown mechanism, reproduced, that materially improves performance
against independent opponents. **The mechanism was found and reproduced** — intra-market lead-time,
measured three independent ways with consistent signs — **and it was shown NOT to improve our results**,
because it is positional and zero-sum in a two-seat shared-pool game. That is a *negative* answer to §29,
delivered by the pre-registered rule set up to catch exactly this. The ~87% of the gap that survives is
production-side, and no local artifact reaches it without route generation.

## APPENDED at 18:51 UTC - the independent-opponent estimator (was unread at write time)

`results/p31_e222/abs.csv`, 120 games, 6 unrelated opponents, candidate vs parent against the SAME
opponent (mean reward per seat, 10 games each):

| opponent | parent | candidate | delta |
|---|---:|---:|---:|
| etsutani-demand-preserving-turn-sale-timing | 78,891 | 78,702 | **-189** |
| ahmedberatozer-v34-observed-market-timing | 75,768 | 75,629 | **-139** |
| yhay81-shop-router-0913 | 77,242 | 76,977 | **-265** |
| aurax7-shop-router-reactive-v7 | 78,290 | 77,967 | **-323** |
| thomastschinkel-2945-farm-96-top-10 | 78,737 | 78,426 | **-311** |
| tschinkel-router-v55 | 85,493 | 85,349 | **-144** |

**Mean -212/seat, 0W/6L by opponent.** So the loss is real against non-clones too, just ~3x smaller than
the -641 mirror: the positional component shrinks when the opponent is not running our own lineage, which
is exactly what the three-estimator table predicts. Gate incomplete (120/192), so treat as partial, but
the direction is unanimous across 6 unrelated opponents and 8 mirror seeds.

Final: the pre-registered rule is satisfied on BOTH absolute estimators. The market/price/crop axis is
CLOSED. No twelfth variant.

## APPENDED 18:53 UTC - E222 agent finished; this REPLACES my partial read above

Full run, 232 + 18 games, 8 seeds, both seats, 0 errored rows, engine pin asserted in-script:

| estimator | mean | W/L/T | seeds differing |
|---|---:|---|---|
| A mirror (cand-cand vs parent-parent) | **-640.8/seat** | 0W/8L/0T | 8/8 all negative |
| B H2H vs parent inside one game | +294.2 | 8W/0L/0T | 8/8 |
| C **absolute vs 6 unseen reactive opponents** | **-270.3/seat** | **5W/43L/0T** | 48/48, **0/8 seeds in favour** |

**Correction to the -212/seat I read at 18:51:** that was 120 of 192 games; the completed figure is
**-270.3/seat (5W/43L)**. My direction was right, my magnitude understated it - the same lesson as the
next paragraph, learned twice in two turns.

**Correction to my own withdrawal:** I retracted the control-leak alarm as a "transient state". It was NOT
noise - the agent confirms the first build had a real defect (the spend-down branch fired even with
`cap=0`, costing -228/seat on seed 1000000) and that it fixed it, after which the caps-off control is
**byte-exact on 8/8 seeds including per-item flows**. So the original observation was correct and my
withdrawal over-corrected it. The durable rule is unchanged: assert inertness as byte-equal rewards AND
equal per-item committed flow AND fires==0, because an inert preset must never rebuild the keys the engine
consumes.

Additional evidence that hardens the null:
- **theta sensitivity, 3 seeds, mirror, all live: theta=0.35 -1,065 | theta=0.50 -641 | theta=0.70 -873 |
  keep=0.3/cap=16 -1,200.** Every arm negative and **the least aggressive is best** - so the result is not
  a threshold artefact, it is the slope of the loss curve.
- **Conservation is only approximate**, measured as committed flow per seat: MILK -0.74%, WOOL +0.06%,
  STRAWBERRY **+1.57%**. The ledger bounds but does not perfectly conserve, so part of the loss is extra
  volume rather than pure re-timing. Stated as a caveat, not hidden - it makes the loss, if anything, an
  understatement of the re-timing penalty and an overstatement of nothing else.
- MELON, excluded by design, differs on 0/8 seeds - a clean negative control on the item axis.
- `agents/live_replay_20260926/**` was rejected as the common-opponent bank (HANDOFF_OPENCODE D-0927-1:
  adaptive-market layer disabled, 0.27x live reward; screened tapes scored 472 and 57k), and
  `salem3000`/`zakariajoudar-rules` were dropped after screening. The opponent bank was audited, not assumed.

**FINAL VERDICT under the pre-registered rule: CLOSED.** Absolute -270.3/seat fails the +900 bar and 8/8
differing seeds point the wrong way. Estimator B's +294 is a tie-break against a same-spine clone, not
money - mirror and absolute both say no. Recommendation on record, from both parent and agent: ship
`cha22_e199_lo96q8` / `cha22_e210_straw_h13q6` and stop the price offensive. No second variant was invented.

Objective 29 is answered NEGATIVE: the previously unknown mechanism (intra-market lead-time) was discovered,
reproduced, priced on four estimators, and demonstrated NOT to improve results against independent
opponents. Remaining axis: production (herd/route co-design).
