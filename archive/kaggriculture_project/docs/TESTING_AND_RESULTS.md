# Testing and Results

Every number in this document comes from an actual `env.run()` against the
real installed `kaggriculture` environment (`kaggle_environments` 1.32.2).
Nothing here is estimated or simulated separately.

## Rules verification (`tests/verify_rules_against_real_env.py`)

Empirically checks `agent/rules.py` against live observations: one-time
crop yield curves (wheat, carrot, melon) at every age through maturity,
ongoing crop production ticks (tomato, strawberry), the market price
formula at real driven inventory levels *and* every calibration point
implied by the README's price table, per-step decay precision after max
lifespan, hire cost across six successive hires, `BUY_LAND` order and
price, and shed-adjacent spawn-tile placement.

**Current status: all checks pass.** One real bug was caught and fixed
by this harness during development, worth recording because it's a good
example of the harness doing its job: the first version of the decay
check predicted the wrong `yield_units` at every single post-decay step,
consistently off by exactly one step. The bug was in the *test's* step
accounting (`steps_into_decay = cur_step - mls + 1`, an incorrect `+1`),
not in `rules.decayed_yield` itself -- confirmed by checking that shifting
the test's labels by one lined up every data point exactly. Fixed by
removing the erroneous offset; re-run confirmed exact agreement at every
step through the plant becoming a weed.

## Bugs found during agent development (in the order they were found)

These were all caught by actually playing games, not by code review --
several only became *observable* once an earlier bug was fixed, which is
itself worth noting as a general lesson: a badly broken agent can hide
several independent bugs behind one dominant symptom.

### 1. Runaway hiring (the big one)

**Symptom:** first full-length test against the `pass` baseline (which
does nothing) lost money net negative -- final money **$160**, down from
$3,000 starting, while `pass` sat unchanged at $3,000. A turn-by-turn
trace showed 6-16 `HIRE` orders in a single turn, repeated across many
turns, with Fibonacci hire cost compounding into the hundreds within a
single day.

**Root cause:** `plan_hiring`'s marginal-value estimate was a flat
constant (`best_per_action_value * turns_left_today`) that didn't
decrease as more hires were evaluated in the same call, *and*, after a
first fix added per-call decay, didn't persist that decay across
*separate* calls within the same day -- so a task surplus that lasted
several turns kept re-justifying a fresh batch of hires every single
turn, because each call started the decay over from the same
undiscounted baseline.

**Fix:** `plan_hiring` now anchors its decay to `gs.hires_today` (read
fresh from the observation, so it reflects the whole day's hiring so far,
not just this call), plus a hard `pending_task_surplus` cap (no point
hiring beyond the number of currently-unclaimed tasks) and a hard
`MAX_HIRES_PER_DAY = 6` backstop. All three are independent brakes;
any one alone would have prevented the original blowup.

**Measured impact:** confirmed via ablation (`tools/ablation.py`) that
hiring, once bounded correctly, is the single largest lever in the
strategy -- disabling it entirely drops mean score against `starter` from
**$51,492 to $12,581** (3 seeds). The fix turned a catastrophic,
game-losing bug into the strategy's best-performing subsystem; both facts
are true at once, which is exactly why the ablation number is reported
here rather than just "it's fixed now."

### 2. Seed-buying capital drain + seed churn

**Symptom:** turn 0 of the very first game spent ~$1,600 of the $3,000
starting bank on seeds alone (16 melon + 8 carrot + 4 wheat), for a
one-farmer opening that can plant at most one tile per turn -- most of
that seed stock would sit unplanted for dozens of turns while capital
that could have funded hiring/expansion sat idle in seed form. Separately,
even after pacing purchases, a full-length game ended with **16 unused
WHEAT + 18 unused CARROT + 11 unused MELON seeds** (~$1,400 of stranded
capital, seeds bought but never planted and worth $0 at game end).

**Root cause (drain):** `seed_shopping_list` originally bought the entire
multi-day tile plan's seed requirement in one shot, with no per-turn
pacing.

**Root cause (churn):** `plan_tiles` recomputed the *entire* crop
allocation from scratch every call, using then-current market prices. As
prices genuinely shift turn to turn, a tile's "best crop" could flip
before it was actually planted, orphaning an already-purchased seed for
the old assignment.

**Fix:** `seed_shopping_list` now paces purchases to roughly
`2 * num_units` seeds per turn (only that many `PLANT` actions can
realistically land soon anyway), funding cheaper crops first when the
budget binds. `plan_tiles` now keeps a sticky per-episode commitment
cache (`planners._committed_tiles`) -- once a tile is assigned a crop, it
keeps that assignment until actually planted, regardless of how the
*unclaimed* tiles' rankings shift around it.

**Measured impact:** on the same seed (42) vs. `starter`, stranded-seed
capital went from ~$1,400 to **$0**, and final money on that seed
improved from $47,503 to $50,676 purely from this fix.

### 3. Animal planner starved of tiles

**Symptom:** an ablation run comparing "animals enabled" vs. "animals
disabled" produced **byte-identical scores** across all three test seeds
-- a strong signal that the animal-investment code path was never
actually firing, not that animals were genuinely worthless.

**Root cause:** `plan_tiles` (crops) ran first and, on a rich opening
board, greedily claimed every available empty tile; `plan_animal_investment`
ran second and was only ever offered whatever tiles crops didn't want --
on the games tested, that was none, so it could never find anywhere to
propose a `BUILD_COOP`/`BUILD_PASTURE`.

**Fix:** reordered `strategy.decide_actions` to evaluate animal
investment *first*, against the full empty-tile pool, reserving at most
one tile for it before crops run. Safe to do without triggering a new
over-investment problem because `plan_animal_investment` only ever
proposes one new structure per call.

### 4. Leftover unfixed reference (`GameState_is_empty_structure`)

**Symptom:** immediately after fixing #3 (which, for the first time,
actually exercised the code path where an animal sits in the shed waiting
to be moved to a structure), the agent crashed into its own safe
fallback on essentially every turn from very early in the game --
`empty_tiles` stuck at 25 for 16 consecutive in-game days, money
completely flat.

**Root cause:** an earlier cleanup pass had replaced a workaround
function name (`GameState_is_empty_structure`) with the proper
`GameState.is_empty_structure` static-method call throughout
`tasks.py`, using a targeted string replace that matched the literal
substring `GameState_is_empty_structure(tile)`. One call site used a
different loop variable name (`t`, not `tile`) and was silently missed.
This bug had existed since that earlier cleanup but was never *reached*
until bug #3's fix made animal-in-shed states actually occur.

**Fix:** found via `grep -rn "GameState_is_"` across the whole package
(rather than another targeted string match) to make sure no other
occurrence was hiding the same way; one was found and fixed.

**Process lesson, also fixed:** this bug was silently swallowed by
`agent.py`'s (correct, intentional) top-level `try/except` safety net for
16 in-game days before being noticed in a trace. The safety net is
correct production behavior -- a crash mid-match would be far worse than
a degraded fallback -- but it cost real debugging time locally. Added an
opt-in `KAGGRICULTURE_AGENT_DEBUG=1` environment variable that prints the
real traceback to stderr instead of silently falling back, off by default
(so a real submission never emits unexpected output), on for all local
testing from that point forward.

### 5. Inventory-gated tasks not bound to the carrying unit

**Symptom:** a purchased **COW sat unplaced in the shed for an entire
720-turn game** (final money noticeably lower on an affected seed: $2,580
vs. a healthy $49,000+ on the same seed once fixed), despite a unit
visibly walking to the pasture and repeatedly issuing `["PLACE", "COW"]`
every turn.

**Root cause:** `PLACE` (and `FERTILIZE`, and `FEED`) all consume from
the *acting unit's own* inventory, not the shed directly. Task generation
checked whether *any* unit, in aggregate, carried the needed item, but
the resulting task was freely assignable to *any* unit by the scheduler's
greedy matching -- so if unit A picked the item up but unit B (merely
closer to the target tile) got assigned the follow-up task, B's action
silently no-op'd every single turn, forever, since B never carried
anything to place/fertilize/feed with.

**Fix:** added a `Task.locked_unit` field; `FEED`, `FERTILIZE`, and
`PLACE` tasks are now generated once per *carrying* unit and locked to
that unit's index, and `scheduler._score` returns `-inf` for any
(unit, task) pairing that violates a lock, so the greedy assignment can
never place them with the wrong unit.

**Measured impact:** re-run on the affected seed: cow successfully
placed and productive by game end (confirmed via final tile state showing
an *occupied* structure, not an empty one); this was also the fix that
made the animal-investment ablation (see below) finally measure a
functioning code path instead of $0 spent.

### 6. Animal ROI threshold too loose

**Symptom:** with bugs #3-#5 all fixed, animals were now genuinely being
purchased, built, and placed -- but re-running the ablation showed a
roughly neutral-to-slightly-negative real contribution (mean $51,492 with
animals enabled vs. $52,730 with them disabled, across the same 3 seeds:
a **-$1,239** average difference).

**Root cause (best current understanding, not fully resolved -- see
`ROADMAP.md`):** `evaluate_animal`'s `daily_profit` only accounts for $
in vs. $ out (egg/milk/wool revenue minus wheat feed cost); it doesn't
price in the `FEED` (and usually `CARE`) action spent on the animal every
single day for the rest of the season, which is a real opportunity cost
in a game where unit-turns are themselves scarce.

**Fix applied:** `plan_animal_investment` now requires
`total_profit > setup_cost * ANIMAL_PROFIT_MARGIN` (30% margin of safety)
rather than merely `> 0`, as a coarse correction. This was **not**
re-validated with a fresh ablation run after being applied (time
constraint, and the margin fix is deliberately conservative/safe by
construction: it can only make the agent invest in *fewer, more clearly
profitable* animals than the version that was measured, never more) --
flagged honestly here rather than claiming a number that wasn't actually
re-measured. The properly-targeted fix (price the daily FEED/CARE action
at the best available crop's $/action, the same currency `roi.py` already
uses for the hiring decision) is recorded in `ROADMAP.md` as the next
concrete step, rather than attempted under time pressure here.

## Final benchmark results (post-fixes)

All games: full 720-turn season, default `weedSpawnChance`, using the
actual `main.py` submission file loaded in complete isolation from the
`agent/` development package (see "Isolation testing" below) unless noted.

**vs. built-in `starter`** (the real installed baseline -- a single-tile
carrot loop, distinct from the `README`'s illustrative wheat-loop
example, which is not a real graded baseline):

| seed | this agent | starter |
|---|---|---|
| 10 | $52,352 | $3,494 |
| 11 | $43,885 | $3,480 |
| 12 | $55,509 | $3,468 |
| 1000-1003 (earlier round, dev package) | $45,660-$54,944 (mean $51,395) | $3,486-$3,496 |

**vs. built-in `random`:**

| seed | this agent | random |
|---|---|---|
| 10 | $52,479 | $0 |
| 11 | $46,497 | $0 |
| 12 | $49,498 | $0 |

(`random` reliably goes bankrupt -- unsurprising, since it issues
`BUY_*` orders with no regard for affordability or payoff.)

**vs. built-in `pass`** (issues no actions at all):

| seed | this agent | pass |
|---|---|---|
| 10 | $45,745 | $3,000 |
| 11 | $49,015 | $3,000 |
| 12 | $54,660 | $3,000 |

**Self-play** (dev package, 4 games, alternating player order to cancel
positional bias):

| game | side A | side B | winner |
|---|---|---|---|
| 1 | $31,917 | $29,395 | A |
| 2 | $31,275 | $30,466 | A |
| 3 | $24,762 | $24,762 | tie |
| 4 | $27,546 | $27,516 | A |

Roughly balanced (3-0-1 in a small sample, scores within a few percent of
each other every game) -- the expected and desired result for a strategy
playing itself: no obvious exploit that only works against a weak
opponent, and lower absolute scores than vs. the baselines above, which
makes sense (two copies of the same aggressive strategy compete harder
for the same land/market/expansion timing than either does against a
passive opponent).

## Ablation (`tools/ablation.py`, mean of 3 seeds vs. `starter`)

| variant | mean score | delta vs. full agent |
|---|---|---|
| full agent | $51,492 | — |
| hiring disabled | $12,581 | **-$38,910** |
| animals disabled | $52,730 | +$1,239 (see bug #6 above) |

## Profiling

Full 720-step game, agent-side wall-clock only (excludes environment
processing and the opponent's own compute):

- mean: **0.63ms** per `agent()` call
- max observed: **6.19ms**
- p99: **1.35ms**

Against the documented `actTimeout: 1` (1 second) and
`remainingOverageTime: 60`, this leaves roughly two to three orders of
magnitude of margin. The `SIGALRM`-based hard deadline in `agent.py` is
set to 0.8s as a safety net that should, based on this profiling, never
actually be needed in practice.

## Isolation testing

`main.py` (the actual submission artifact) was tested with the
`agent/` development package made unimportable (`sys.path` filtered, and
separately, the file copied into an empty directory with no sibling
package) and loaded exactly the way `AGENTS.md` documents
(`env.run(["main.py", "starter"])`). This caught a real bundling bug the
modular-package tests could never have caught: an early version of
`build.py` stripped `from . import rules`-style import lines but didn't
rewrite the resulting dangling `rules.CROPS` / `strategy.decide_actions`
attribute references, producing a `main.py` that `NameError`'d on its
first real turn and silently fell back to doing nothing all game (final
score exactly $3,000, i.e. untouched starting money) while still
reporting `DONE` status -- worth calling out because "the match completed
with a DONE status" is not, by itself, evidence that a submission is
actually working. Fixed by rewriting `build.py` to use a proper AST
transform (see `build.py`'s docstring); re-verified isolated behavior now
matches the dev package exactly (identical score on identical seed).
