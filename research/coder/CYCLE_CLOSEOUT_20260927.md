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
