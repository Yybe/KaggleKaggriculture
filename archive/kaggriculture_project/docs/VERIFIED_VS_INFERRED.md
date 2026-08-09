# Verified vs. Inferred vs. Assumed

Per the brief's own request to "distinguish clearly between verified facts
from official documentation, verified behavior from the environment
source code, public community findings, and your own inferences" -- and
to "explicitly state" anything that can't be verified. This list is short
specifically *because* the real environment was installed and readable
(see `RESEARCH_SUMMARY.md`); most of what would ordinarily be "inference
from README prose" in this project is instead "read directly from
`kaggriculture.py` and independently confirmed against a live episode."

## Fully verified (source read + empirically confirmed against a live episode)

Everything in `agent/rules.py`: crop/animal constants, the bonus-window
formula (including the melon-specific discrepancy vs. the README table --
see below), decay timing down to the exact step, the market price
formula and every calibration point in the README's price table, hire
cost across successive hires, `BUY_LAND` order and pricing, shed-adjacent
spawn-tile placement and the NWSE tie-break order, ongoing-crop scheduled
production timing and count. Full detail and the specific test assertions
are in `tests/verify_rules_against_real_env.py` and
`docs/TESTING_AND_RESULTS.md`.

**The one deliberate resolution of a documentation/source conflict**:
the README table lists melon's "Time to Max Yield" as 10 days; the
installed source's `CROPS["MELON"]["max_yield_day"]` is **12**. These are
not the same field despite the table's phrasing suggesting they are --
"10" is the age at which the yield cap is *actually reached* under
optimal watering (an emergent property), while "12" is the literal
internal parameter that sets the bonus window's end and the decay-start
trigger. `agent/rules.py` uses the code value throughout (verified
correct via the live-episode test, including the specific "cap reached at
age 10, fertilizing reaches it at age 8" claims from the README, which
only come out right using max_yield_day=12). Per the brief: implementation
wins over documentation prose where they conflict.

## Read directly from source, reasoned from it, but not pinned by a dedicated isolated test

- **`FEED` draws from the acting unit's own inventory, not the shed
  directly** (mirroring `FERTILIZE`, which *was* directly confirmed via
  its explicit `_inv_take(inv, "FERTILIZER", 1)` call in source). This
  behavior is relied on throughout `agent/tasks.py` and `agent/scheduler.py`
  (the `Task.locked_unit` mechanism exists specifically because of it --
  see `TESTING_AND_RESULTS.md` bug #5) and is *strongly* supported
  indirectly: animals were fed correctly and survived across every
  multi-hundred-turn test game once the locking fix was in place, which
  would not happen if this assumption were wrong. Not, however, isolated
  in its own unit test the way the price formula and yield curves are.
- **A hired hand can act starting the turn *after* it's hired, not the
  same turn.** Derived from the documented turn-processing order (player
  actions are step 2, market actions including `HIRE` are step 3 --
  i.e. a hand created during a turn's market processing didn't exist yet
  during that same turn's player-action step), not separately isolated
  with a dedicated same-turn-activation test.
- **No cap on a farmer/hand's personal (carried) inventory during the
  day**, only the shed's documented 100-item cap. Based on reading the
  `HARVEST`/`PICKUP` handlers in full and finding no such check;
  consistent with every test game run (no observed truncation of carried
  items), but not stress-tested with a deliberately large single-unit
  haul.

## Assumptions about the grading environment that could not be directly confirmed

- **Default configuration.** All testing used `kaggle_environments`'s
  default `kaggriculture` configuration (`episodeSteps: 720,
  boardSize: 10, startingMoney: 3000`, default `marketParams`, etc.).
  The spec supports per-resource `marketParams` overrides at episode
  creation (`env.configuration["marketParams"]`); there is no way to
  confirm from here whether the live competition's actual grading
  episodes use the documented defaults or a custom override. If they
  differ, `agent/rules.py`'s hard-coded `MARKET_PARAMS` would need
  updating to match (a config-driven version is a natural next step --
  see `ROADMAP.md`).
- **Process/agent-instance lifetime across an episode.** Whether the
  competition's actual execution harness reuses one Python process (and
  therefore one loaded `agent` callable, preserving module-level state)
  for an entire 720-turn episode, the way local `env.run()` does, isn't
  independently confirmed for the live grading infrastructure
  specifically. The codebase is deliberately designed to not need this to
  be true for *correctness* (state is recomputed from the observation
  every call by default; the one exception, `planners._committed_tiles`,
  resets itself safely if it ever sees `step == 0` again) -- so this is a
  hedged assumption, not a load-bearing one.
- **`actTimeout: 1` / `remainingOverageTime: 60` apply to the actual
  graded submissions**, not just local `make()` defaults. These are read
  directly from the installed package's `kaggriculture.json`
  specification, which is the best available evidence, but "the
  installed package's declared spec" and "what the live competition
  server actually enforces" are not literally the same claim.

## What Phase 2 ("internet research") could not establish

Community notebooks with titles suggesting real strategic findings exist
(confirmed via search) but their content was not retrievable by any
available tool (`RESEARCH_SUMMARY.md` has the detail). Nothing in this
codebase's strategy is informed by community discussion, for the simple
reason that none was readable. This is stated here rather than papered
over with invented "community consensus" framing anywhere in the docs.
