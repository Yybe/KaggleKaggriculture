# P32 — WHY THE WHOLE MARKET AXIS KEEPS FAILING: the price gradient is positive but unbankable, and the exploitable part is zero-sum

`results/p28_tape_divergence/p32_positional_vs_level.md` · computed from
`results/p28_tape_divergence/p28_per_seat_item.csv` (my own asserted-exact exec model, engine 1.32.7) and
`p29_pairs.csv` (CQ-7). Read-only, no engine run, no gate, no agent edited, **no submission mechanism**.

## The two facts that look like each other and are not

| estimator | quantity | result |
|---|---|---|
| **ACROSS teams** (leader cohort, n=27 teams, >200 premium units each) | r(premium-season centroid day, realised px) | **+0.239**, R² 0.057 — teams that sell **later** realise **more** |
| across-team spread of that centroid | sd / min / max | **0.68 d** / 17.05 / 20.42 — 35 teams all sell around **day 19** |
| **WITHIN one market** (n=276 paired seat-episodes, same item) | \|Δ centroid\| | median **1.10 d**, mean 1.74, **p90 4.47** |
| within-market who wins | earlier seat | **94%** of divergent pairs (p28: `d_day` win-share 6% for the loser side) |

**Both are correct and they point in opposite directions**, and the reason is the ratchet itself:

* Nothing refills the shared pool (`_town_consume` only decrements, `kaggriculture.py:728-749`), so the
  pool **falls monotonically through the season** — p19's crossings: FERTILIZER d1, WOOL d9, MILK d17,
  STRAWBERRY d21. Below `I0` the price is *above* base and rising. **So the seasonal price gradient is
  POSITIVE: late units are worth more.** That is the +0.239 across-team signal.
* But a SELL at `px>1` **adds** to that same pool (`:659-660`), so inside one episode the opponent's
  volume is the thing that ruins your price. **Whoever commits first lands above the other's glut.** That
  is the 94% within-episode signal, and it is why the two readings disagree.

## The bind, in one sentence

> **The direction that would earn money unconditionally (sell later) is the one the engine forbids, and the
> direction that is available (sell before the opponent) is zero-sum.**

* **Sell-later is blocked by storage, not by policy.** `shedCapacity=100` with end-of-day discard, measured
  in E220: the rationed arm committed **130.7 MILK / 103.7 WOOL / 131.3 STRAWBERRY fewer units per seat**,
  step-718 shed was `0` in both arms, and capping premium release throttled **WHEAT by 153 units/seat** —
  an item the cap never names, because shed+cash is one bottleneck. Deferral needs ~3.7x the entire shed.
* **Sell-first is a race, not a level.** The prize measured from pairs (+1,619/seat collectable on
  MILK+WOOL+STRAW per p28c×p30) is estimated from episodes where **only one of the two seats** had the
  advantage. Deploy it to both seats — which is what the live pool does to a spine clone, and what finals
  matchmaking will do to any rule we ship — and both seats move at the same time, the pooled supply rises
  earlier, and the positional component **cancels**. p28b already measured the step-level version of the
  same cancellation: seat 0 keeps +14.9/unit on WOOL inside a collision, but the pair mean is identical
  either way (138.1/139.4 alone vs 145.5/130.6 collided = 138.05).

## Pre-registered prediction for the arm now running (`cha22_e222_throughput`)

Stated **before** its results, so it cannot be fitted afterwards:

* A fixed-threshold, **level** rule (sell when `px/base >= theta`) makes all adopters move together. On the
  symmetric arm (both seats candidate vs both seats parent) it should return **|delta| < +900/seat
  absolute** — inside the live-noise band — with H2H ≈ 0 because the rule is symmetric by construction.
* **If it instead returns a large positive absolute gain, this document is wrong** and the positional
  reading must be re-examined — most likely the gain would then be a *pool-state* effect the model above
  underweights (the town's removal curve being steeper than assumed on WOOL). Either outcome is
  informative, which is why it is worth running.
* Either way it does **not** license a third variant; §20 applies.

## What is actually left, and it is not a schedule

The only non-zero-sum lever the engine offers on the price side is **which pool the marginal unit enters**,
not **when** it enters:

* cliff widths to `$1`: **CARROT 842, TOMATO 529, FERTILIZER 493** vs **WOOL 59, STRAWBERRY 62, MILK 76**
  (p18/p19, computed from the pinned `market_price()`).
* p27: carrot is the only item whose realised price *rises* under contest (42.0 → 55.2). Caveat stands:
  that pair straddles two `unlocked_shops` regimes, so it is directional.
* Substituting marginal volume from a 59-unit cliff into an 842-unit cliff raises revenue **without needing
  to beat anybody in time** — it is not positional. It is also **production**, i.e. crop choice and plot
  geometry, which is exactly where E152 (slot geometry inseparable from the crop), V20/V27-V29 (crop-mix
  overlays inert), E57c and E118 (plant-redirect −138,266) all stopped previous attempts.

So the objective's own §5J answer survives in a sharper form than I wrote it this morning: the missing
capability is not a better market wrapper and not a tape re-timing — it is **co-designing which crops the
route plants with which pool each item's volume will meet**, and no wrapper in the current architecture can
choose a crop, because the crop is fixed by the generated route's slot geometry. That is the abstraction
§20 asked us to question, now identified concretely.

## Method laws to keep

1. **Never quote a within-episode paired effect as a per-team prescription.** They have opposite signs here
   (+0.239 across vs 94% earlier-wins within). This is the same failure class as the mirror traps E73/E119b
   and the H2H-vs-absolute split — the estimator's population must match the deployment population.
2. **Report the direction of the seasonal price gradient before pricing any timing idea.** It is positive
   here, and storage is what blocks it; that single fact predicts the outcome of the entire
   ration/hold/preempt family, nine candidates deep.
3. Across-team centroid spread is only **0.68 days** — so "the leaders sell at a better time of season" is
   refuted at team level, independently of p19's rate refutation and p17's shape refutation.
