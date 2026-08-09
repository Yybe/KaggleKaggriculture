# Architecture

## Module map

| Module | Responsibility | Roughly maps to brief's suggested module |
|---|---|---|
| `rules.py` | Verified constants + pure formulas (price, yield, decay, hiring, land, geometry). No game state, no side effects. | — (ground-truth layer, not in the original list) |
| `state.py` | Read-only wrapper around the raw `obs` dict. | GameState |
| `market_model.py` | Price-aware sell pacing, glut throttling. | MarketModel |
| `roi.py` | Crop/animal $-value and $/action economics. | Economy, ROIEngine, (part of) EvaluationFunction |
| `tasks.py` | Scans farm state, emits scored candidate actions. | (part of) Scheduler, EvaluationFunction |
| `scheduler.py` | Greedy tier-then-value/distance task-to-unit assignment. | Scheduler, MovementPlanner (movement itself is in `rules.move_sequence`) |
| `planners.py` | Crop-mix allocation, animal investment, expansion, hiring. | CropPlanner, AnimalPlanner, ExpansionPlanner, HiringPlanner |
| `opponent_model.py` | Public-tile-only inference of near-term opponent supply. | OpponentModel |
| `strategy.py` | Orchestrates all of the above into one action per turn. | StrategyManager |
| `agent.py` | Kaggle entrypoint: timeout/crash safety net. | — |

Not built as separate modules, and why:
- **SimulationEngine / world model**: no custom simulator was built at
  all -- the real `kaggle_environments.make("kaggriculture")` is the
  simulator, used directly for every test. See
  `docs/RESEARCH_SUMMARY.md` for why that's strictly better than a
  hand-rolled parallel implementation here. `rules.py` provides the pure
  *forward-looking formulas* (e.g. "what will this melon yield at age 10
  if watered daily") that planning needs, without duplicating the
  environment's turn-processing engine.
- **BoardAnalyzer**: folded into `state.py` (tile iteration helpers) and
  `tasks.py` (the actual analysis); a separate module would just be a
  pass-through.
- **Logger / Profiler / ReplayAnalyzer**: live in `tools/` as scripts
  (`run_match.py`, `ablation.py`) rather than agent-side modules, since
  they're development-time tooling, not something the submitted agent
  needs at inference time -- shipping them inside `main.py` would only
  add dead weight against the 1-second `actTimeout`.

## Why greedy assignment, not search (Phase 8)

The brief asks for the planning algorithm to be chosen by measured
performance, not assumed. Two things about this specific game make that
choice easy to reason about before even profiling:

1. **Movement has no obstacles.** Locked tiles are passable; only board
   edges block movement. Manhattan distance is therefore always both
   achievable and optimal (`rules.move_sequence`) -- there is nothing for
   a pathfinding search to discover that a direct formula doesn't already
   give exactly.
2. **The reward structure is smooth and mostly known in closed form.**
   Crop yields, decay, and market prices are all deterministic functions
   of observable state (verified against source, see
   `RESEARCH_SUMMARY.md`). The two genuinely stochastic/hidden pieces are
   weed spawning (0.5%/tile/day, low-impact) and the opponent's actions
   (only their public tiles are visible). Neither rewards a deep rollout
   search the way, say, hidden-information card play or adversarial combat
   would -- there's rarely a reason to look more than one "obviously best
   next thing" deep, because the value of that next thing is already
   computable directly from `roi.py`.

Given that, MCTS/beam search/A* would mostly be spending the 1-second
`actTimeout` computing things `roi.py` and `market_model.py` already know
analytically, for no accuracy gain. What the game *does* need every turn
is fast, correct **assignment** (which of up to ~10 units does which of
up to a few hundred candidate tasks), which is where the actual
engineering went:

- **Tiers before scores.** `tasks.py` assigns each candidate a hard
  priority tier (imminent loss-of-investment > actively decaying value >
  everything else) before any continuous scoring happens. This mirrors
  how a competent player actually thinks about the game: a plant one
  unwatered day from becoming a weed is not "high value", it's
  non-negotiable, and no amount of `$` on some other task should be able
  to outbid it. Folding urgency into one blended score risks exactly that
  failure mode if the weights are ever slightly off; a hard tier can't.
- **Greedy bipartite matching, not Hungarian/optimal assignment.** Every
  turn, `scheduler.assign` repeatedly takes the single best remaining
  (unit, task) pair by score and removes both from the pool --
  `O(units * tasks)` per pick, trivially fast at this scale (≤10 units,
  a few hundred tasks). This is not globally optimal in the way the
  Hungarian algorithm is, but re-optimizing from scratch every single
  turn (which the stateless design does anyway -- see below) makes any
  one turn's sub-optimality cheap and self-correcting: a slightly wrong
  pairing this turn just gets re-evaluated fresh next turn, at a cost of
  at most one wasted step of travel. That's a very different risk profile
  than a one-shot decision (like a chess move) where getting the
  assignment exactly right matters more than getting it fast.
- **Recomputed from scratch every turn, not carried as persistent
  per-unit plans.** This was a deliberate robustness choice: nothing
  about whether `kaggle_environments` reuses the same Python process for
  an entire episode is documented, so relying on cross-call memory for
  *correctness* (not just performance) would be fragile. The one place
  persistent state is used at all is `planners.py`'s tile-commitment
  cache (see `TESTING_AND_RESULTS.md`, "seed-buying capital drain"), and
  even that resets itself defensively on `step == 0` so re-using a
  process across multiple local episodes (as `tools/run_match.py` does)
  can't leak state between games.

## The evaluation function (Phase 9)

There isn't one single scalar "evaluate this action sequence" function,
because the game decomposes cleanly into decisions with genuinely
different currencies, and collapsing them into one number would hide
that:

- **Tile/task priority** (`tasks.py`, `scheduler.py`): tier (loss
  prevention) first, then `$value - ALPHA * distance`. Distance is priced
  in because a turn spent walking is a turn not spent on the next-best
  task -- real opportunity cost, not just an implementation detail.
- **Crop/animal choice** (`roi.py`): `$/day-of-tile-occupancy` for
  ranking crops against each other (tiles, not turns, are the binding
  constraint once a farm is staffed), and `$/action` for ranking against
  hiring a hand (a hand's marginal output is bounded by turns, not
  tiles). Both numbers come from the same `CropEconomics`/
  `AnimalEconomics` objects so the two planners never disagree about what
  a crop is worth.
- **Hiring** (`planners.plan_hiring`): compares Fibonacci hire cost
  against a *decaying* marginal-value estimate, explicitly modeling that
  the best available task gets claimed by the first hand hired, not by
  every subsequent one too. See `TESTING_AND_RESULTS.md` for what
  happened before this decay was anchored correctly across turns (it's
  the single most consequential bug this project found).
- **Crop-mix allocation** (`planners.plan_tiles`): a marginal
  water-filling loop, not a fixed allocation percentage. Each additional
  tile committed to a crop is priced using the *batch* sell price that
  quantity would realize (`roi._batch_sell_price`), so a crop's own
  glut-sensitivity is what naturally caps how much of it gets planted --
  melon doesn't get a hand-coded "don't overplant melon" rule; it
  produces its own diminishing marginal value once enough tiles are
  already committed to it, straight from the verified price formula.

## Performance

`agent.agent()` is wrapped in a `SIGALRM`-based hard deadline (0.8s,
inside the documented 1s `actTimeout`) and a top-level `try/except`
falling back to a minimal hard-coded policy that cannot itself fail. Real
measured latency over a full 720-turn game: **~0.6ms mean, ~6ms observed
max, ~1.4ms p99** -- roughly 150-1500x margin under the 1-second budget
(`docs/TESTING_AND_RESULTS.md` has the full profiling run). The dominant
cost driver kept in mind throughout was the crop-allocation loop, which is
why `roi._batch_sell_price` uses an O(1) midpoint-price approximation
(`rules.approx_batch_price`) rather than simulating every unit of a
hypothetical multi-tile harvest -- real `SELL` orders still use the exact
unit-by-unit simulation, since those operate on small, shed-capacity-
bounded quantities where precision matters more than speed.
