# Research Summary

## 1. Reality check (before writing any strategy code)

The brief read like it could plausibly be a private/sandboxed exercise, so
the first thing to establish was what's actually real:

- **Kaggriculture is a live, real Kaggle competition.** Hosted by Kaggle
  and Google, a two-player farming-sim simulation competition with a
  $50,000 prize pool, entered "recently" as of this writing with an entry
  deadline in September 2026. This was confirmed via web search, not
  assumed.
- **The environment is genuinely pip-installable.** `pip install -U
  kaggle-environments` (PyPI, version 1.32.2, released ~2 weeks before
  this was written) registers both `kaggriculture` and a
  `kaggriculture_beginner` variant under
  `kaggle_environments/envs/`. The provided `README.md` / `AGENTS.md` are
  **byte-for-byte identical** to the installed package's copies (verified
  with `diff`), confirming they're the real, current documentation and
  that the target is the full `kaggriculture` env, not the beginner one.
- **The Kaggle competition/notebook pages themselves are not fetchable.**
  Both `kaggle.com/competitions/kaggriculture/overview` and community
  notebook URLs are client-rendered React apps; `web_fetch` only returns
  page metadata (title, og:description), not the actual rules text or
  notebook content. Search results surfaced several community notebooks
  with titles suggesting real strategic content already exists --
  *"Adaptive Farming Strategy for Kaggriculture"*, *"Kaggriculture:
  Findings from Zero to Top Meta"*, *"Kaggriculture: Observable Economic
  Control"*, *"Building a Kaggriculture AI Agent"* -- but their content
  could not be retrieved by any available tool. **This is stated plainly
  rather than guessed at**: if you want that community perspective, those
  notebooks are worth opening yourself; nothing in this codebase is
  informed by their contents, because nothing in this codebase *could* be.

## 2. What "treat the implementation as source of truth" actually meant here

Because the real environment was installed, not just documented, the
whole research phase changed shape. Instead of building a parallel
simulator from the README's prose and hoping it matched reality, the
actual `kaggriculture.py` (1,064 lines) was read in full, and every
non-trivial formula in `agent/rules.py` was checked two ways:

1. **Read the source directly** for the ground-truth formula (e.g. the
   exact bonus-window calculation, the exact concurrent market-order
   algorithm, the exact hire-cost / land-cost / spawn-tile logic).
2. **Empirically verified it against a live, running episode**
   (`tests/verify_rules_against_real_env.py`) -- plant real crops, water
   them for real, read `yield_units` back out of real observations at
   every age, and assert it matches what `agent/rules.py` predicts. Same
   for market price at real inventory levels (including the exact
   calibration points implied by the README's price table), hire cost
   across real successive hires, `BUY_LAND` order and price, decay timing
   down to the exact step, and shed-adjacent spawn placement.

Every check in that file passes against the real environment. This is a
meaningfully stronger evidentiary basis than "the docs say so" -- and it
caught real discrepancies between the README's plain-English description
and the actual code (see `VERIFIED_VS_INFERRED.md` and
`docs/STRATEGY.md`'s note on the melon bonus window). The clearest example:
the README table lists melon's "Time to Max Yield" as 10 days, but the
source's internal `max_yield_day` parameter for melon is **12** -- a
different, larger number that governs the bonus window's end and the
decay trigger, while "10" is really an *emergent* property (when the
yield cap is actually reached under optimal watering). Reading only the
table would have produced a bonus-window formula that's subtly wrong for
melon specifically (right for wheat/carrot, wrong by one day for melon).

## 3. What this means for the "internet research" phase

The brief's Phase 2 asked for exhaustive research into Kaggle discussions,
public notebooks, GitHub, Reddit, and community strategy writeups. Given
the tool limitations above, that phase is honestly close to empty for
directly-cited community findings -- there simply wasn't a way to read
them. What substituted for it, and what this codebase actually rests on:

- The verified source code (strongest possible ground truth for a
  competition where the eval harness *is* that source code).
- Direct mathematical analysis of the documented and verified formulas
  (see `docs/STRATEGY.md` for the price-curve reasoning -- which crops are
  glut-fragile, why, and by how much, worked out from the actual
  `MARKET_PARAMS` constants rather than the qualitative README hints).
- Real, repeated empirical testing against the actual environment (self-
  play and the three built-in baselines), with every claimed number in
  `docs/TESTING_AND_RESULTS.md` coming from an actual `env.run()`, not an
  estimate.

If/when the community notebooks above become readable (or you paste their
content in), the strategy layer (`agent/strategy.py`, `agent/planners.py`)
is the place to fold in anything genuinely new -- the rules/economics
layer (`agent/rules.py`, `agent/roi.py`) shouldn't need to change, since
it's independently verified against the actual game, not against anyone's
writeup of it.
