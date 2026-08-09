# Strategy: the economic reasoning

Every claim below is derived from the verified `MARKET_PARAMS` /
`CROPS` / `ANIMALS` constants in `agent/rules.py` (themselves checked
against the live environment -- see `RESEARCH_SUMMARY.md`), not from the
README's qualitative hints, though the two agree everywhere they overlap.

## The price curve is the whole game

```
price(inv) = base + sign * amp * f(|inv - I0|)
```

with an *independent* shape function and target on the scarcity side
(`inv < I0`) and the glut side (`inv > I0`). This single design decision
is why "sell everything ASAP" is wrong as a universal policy, and why the
crop planner can't use a fixed allocation percentage per crop:

| Resource | Scarcity reaction | Glut reaction | Reading |
|---|---|---|---|
| Wheat | steep (`sqrt`, 0.80) | gentle (`log`, 0.20) | Absorbs oversupply; the safe high-volume staple. Also the only crop with a second use (animal feed), so it's rarely truly "surplus". |
| Egg | moderate both sides (`linear`/0.40, `log`/0.20) | | The most stable resource in the game either direction -- ideal for a long-running, high-volume "engine" (see Animals below). |
| Carrot | gentle scarcity (`log`, 0.20) | steep glut (`sqrt`, 0.70) | Mirror image of wheat: fine as a small/secondary crop, punishing if mass-planted. |
| Tomato | moderate both sides | | Middling on every axis (yield/tile/day, price stability) *and* an 8-day wait before any revenue at all -- the weakest ROI crop unless town demand (Pizza Shop, Farmers Market) specifically calls for it. |
| Melon | barely reacts to scarcity (`log`, 0.20) | **severe** on glut (`sq`, 3.60) | Best raw $/tile/day in the game by a wide margin at moderate quantities, but the quadratic glut penalty means a large *simultaneous* melon dump is genuinely ruinous -- this is why melon allocation is capped by the water-filling loop's own batch-price feedback, not a hand-tuned limit. |
| Strawberry, Milk, Wool | | glut target > 1.0 (1.60, 1.60, 3.20) | "Premium resources... even modest gluts drive them straight to the $1 floor" per the README, confirmed by the constants: an `above_target > 1` means the SAME quantity that would only knock a normal resource down by, say, 40%, sends these straight through zero and hits the floor. Sell these steadily in small batches, never as a single dump. |

This table is exactly what `market_model.max_qty_within_price_floor` and
`planners.plan_tiles`'s marginal water-filling loop operationalize: they
don't need to know "melon is risky" as a rule, because the *actual*
marginal value of the 16th melon tile, computed from the real formula,
already comes out lower than planting something else instead.

## Animals: the "engine" case

Goose/egg has the highest `yield/tile/day` in the entire object table
(1.00) and the flattest, most boring price curve in the game -- a rare
combination, and the reason `roi.rank_animals` tends to favor it as a
long-run capacity investment once the opening's cash crunch is over.
Cow/milk and sheep/wool have higher per-unit value but the same
"premium resource, punishing glut" profile as strawberry, so scaling them
up needs the same caution as melon -- codified as `MAX_PER_ANIMAL_TYPE`
in `planners.py` rather than left to an ROI formula that (as of this
version) doesn't yet price in same-product market impact across multiple
animals the way crop allocation does for tiles. See `ROADMAP.md`.

## Opening -> liquidation, without hard phase boundaries

`strategy.py` doesn't implement discrete phases with jump-cut behavior
changes at fixed days. Everything that would naturally be phase-dependent
is instead a continuous function of `remaining_days`:

- **Sell threshold** (`strategy._sell_threshold`) loosens smoothly as the
  season winds down (0.55 -> 0.45 -> 0.35 -> unconditional liquidation in
  the final 2 days), because holding out for a better price only makes
  sense if there's time left to sell into it.
- **What's worth planting** (`planners.plan_tiles`) is naturally excluded
  once a crop's occupancy time plus a small sell buffer wouldn't fit in
  the remaining season -- a melon planted on day 25 would still be
  growing on day 30 and score nothing, so the marginal-value loop simply
  never proposes it that late, with no special-cased "day 25: stop
  planting melon" rule needed.
- **Fertilizer and hiring** both gate off in the final few days
  (`_fertilize_allowed`, `plan_hiring`'s `turns_left_today` check) for
  the same reason: a fresh investment needs enough remaining season to
  pay itself back.
- **Liquidation** is the one true discrete event, and deliberately so: in
  the final 2 days, `_sell_threshold` returns `None`, which
  `strategy._build_market_orders` reads as "sell everything regardless of
  price" -- because unsold inventory literally scores zero
  (`README.md`: "Unsold items in the inventory do not count towards that
  total"), holding out for a better price has no defensible value once
  there's no time left to realize it, and the measured result confirms
  this works: shed and seed inventory are empty at the end of every test
  game (see `TESTING_AND_RESULTS.md`).

## What's *not* modeled yet, on purpose

- **Opponent-reactive strategy switching.** `opponent_model.py` only
  feeds a mild sell-urgency multiplier when the opponent's visible tiles
  suggest a supply wave is coming; it doesn't try to out-time the
  opponent's expansion or hiring. Given both players only see each
  other's *public* farm state (never shed/seeds), and the market's
  concurrent per-unit resolution already prices in same-tick competition
  fairly, the highest-leverage lever available is still "play your own
  economics well", not opponent-modeling depth. This is a reasonable
  place to invest more effort next (see `ROADMAP.md`).
- **Town-demand-driven crop selection.** `rules.expected_daily_town_demand`
  exists and is wired into nothing yet -- the crop planner currently
  reacts to town demand only indirectly, through its effect on market
  price/inventory. Explicitly steering toward whatever the newest-unlocked
  shop wants is a natural next iteration.
