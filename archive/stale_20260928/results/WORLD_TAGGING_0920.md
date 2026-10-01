# Shop-world tagging of the gate panel — bench-integrity notes (2026-09-20)

Offline only. Nothing in this file was measured against a live submission and no
agent was modified. Oracle source: `WybeV2/kernels_pull/_0920c/gods_pkg/shop_predictor.py`
(decoded `leoprovorov/god-s-mode-hacked-stores`), ported to
`C:\Users\xxshi\Desktop\farmmasterV2\tools\shop_oracle.py`.
Background: `reference_bundle_20260920/GOD_MODE_FINDINGS.md`,
`reference_bundle_20260920/memory/project-god-mode-shop-rng.md`.

## 0. Environment

* `kaggle_environments == 1.32.7` at
  `WybeV2/rank_env/Lib/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`
  (`tools/engine_assert.py` -> `RESULT=PASS`; hinge shapes + `townCenterSellInterval=24` OK).
  Nothing was installed, upgraded or downgraded. The findings doc's 1.32.6 caveat is
  closed: the oracle holds on our pinned 1.32.7 build.
* Engine facts read from source (`_end_of_day`, kaggriculture.py:860-891, `_spawn_weeds`:836):
  `rng = Random((seed*1_000_003) ^ day)`; one `rng.random()` per `None` tile, farm order
  player0 -> player1, row-major (y then x); `rng.choice(sorted(SHOPS))` iff
  `(day+1) % townShopUnlockInterval == 0` and `len(unlocked_shops) < MAX_SHOP_INSTANCES (8)`.
  Weed outcomes do **not** matter — only the *count* of empty tiles, and only tiles that are
  still `None` after the daily plant/animal refresh (`"LOCKED"` tiles never draw).
  Shop draws therefore land at end of days 2,5,8,11,... -> shops live on days 3,6,9,12,....
  `env.info["seed"]` equals the `configuration["seed"]` we pass, so the oracle input is exactly
  our bench seed.
* A local `Kaggriculture/` folder is injected into `sys.path` by `tools/diag_bench_seeds.py`;
  it contains no `kaggriculture.py`, so the pinned venv engine is what actually runs. Verified.

## 1. Oracle verification — 16/16, plus 128/128 and 1536/1536 at panel scale

Verification harness instruments the *engine's own* `_spawn_weeds` / `_end_of_day` (it records
the true draw count and the true unlocked shop; it does not re-derive either), then compares
against `shop_for(seed, end_day, empty_count)`.

`py WybeV2/rank_env/Scripts/python.exe tools/shop_oracle.py verify --days 14 --seeds 1000000,9000000 --policies pass,mirror`
-> **16/16 exact**, 2.2 s/game, 6.4 s total:

| policy | seed | end-day 2 / 5 / 8 / 11 empty-tile counts | result |
|---|---|---|---|
| `pass` (inert control) | 1000000 | 48 [23,25] / 48 [23,25] / 46 [22,24] / 46 [22,24] | 4/4 |
| `pass` | 9000000 | 50 / 50 / 49 / 49 | 4/4 |
| `mirror` (`pub_metav4_early` vs itself) | 1000000 | 0 / 0 / 0 / 8 [4,4] | 4/4 |
| `mirror` | 9000000 | 0 / 0 / 0 / 8 [4,4] | 4/4 |

The `pass` rows are the load-bearing ones: with 46-50 consumed draws per day the oracle is
only correct if both the seed derivation and the *count* semantics are right (a wrong count
would shift `choice()` by one slot with ~87% probability). Gate panel runs agree 128/128 and
the full 128-seed census agrees 1536/1536.

## 2. Structural result: the first three shop worlds are seed-only for competitive play

`empty_count` is produced by the agents (planting / DIG / land purchase), so a "world" is
formally a (seed, policy-pair) property. Measured on 384 competitive games
(`mirror`, `vsv3` = champion vs `lynnsakurai_v3`, both seats):

| day (end-day) | `mirror` seeds with empty==0 | `vsv3` games with empty==0 | pure-math (`empty=0`) shop = actual shop |
|---|---|---|---|
| 3 (2) | 128/128 | 256/256 | **384/384 (100%)** |
| 6 (5) | 128/128 | 256/256 | **384/384 (100%)** |
| 9 (8) | 122/128 | 250/256 | 123/128 (96%) |
| 12 (11) | 0/128 | 0/256 | 10/128 (8%) |

Our champion fills all 25 unlocked NW tiles by end of day 0 (20 plants + 4 pastures + 1 empty),
so for days 3-9 the board is fully occupied and the draw stream advances zero steps: **the
day-3 and day-6 worlds are computable with zero simulation** — `shop_for(seed, 2, 0)` and
`shop_for(seed, 5, 0)`. Confirmed identical across `mirror`/`vsv3` and across both seats for
128/128 seeds at (day3,day6); 123/128 also at day9. Beyond day ~10 the guarantee dies
(`empty_d11` up to 46), so day-12+ worlds are NOT taggable per seed.

Contrast: the `pass` control on the same seeds gets *different* shops (e.g. seed 1000000 day 3:
`YARN_STORE` under `pass` vs `PIZZA_SHOP` under both competitive policies). So the
seed-only rule is a property of our route family, not of the engine.

Fragility (why this must be re-checked per route, kernel's 76.6% claim, our own numbers):
flipping the pre-shop empty count by exactly one tile changes the shop for
**66%** of census seeds on day 3, **61%** on day 6, **50%** on day 9.

## 3. Gate panel (the 8 challenger-screening seeds)

Seed list recovered from the bench tooling — identical in `tools/bench_all_vs_v3.py`,
`tools/bench_v29.py`, `tools/bench_v29_fleet.py`, `tools/bench_v3_vs_hardened.py`,
`tools/evaluate_apexx_fast.py`, `tools/tune_v18_apex.py`, `tools/diag_bench_seeds.py` (CLI list):
`1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000`.
Secondary panel present but not tagged here: `FRESH_SEEDS` (18 seeds, `tools/bench_v29.py`) and
the old V15 win/loss lists in `tools/gate_eval.py` (a sell-timing gate, not the challenger screen).

| seed | day3 | day6 | day9 | (day3,day6) world_id | first-week products demanded |
|---|---|---|---|---|---|
| 1000000 | PIZZA_SHOP | FARMERS_MARKET | BAKERY | PIZZA_SHOP\|FARMERS_MARKET | CARROT MILK STRAW TOMATO WHEAT |
| 2000000 | YARN_STORE | PET_CAFE | PIZZA_SHOP | YARN_STORE\|PET_CAFE | CARROT WOOL |
| 3330000 | PIZZA_SHOP | BRUNCH_SPOT | FARMERS_MARKET | PIZZA_SHOP\|BRUNCH_SPOT | EGG MILK STRAW TOMATO WHEAT |
| 5000000 | BRUNCH_SPOT | BAKERY | BAKERY | BRUNCH_SPOT\|BAKERY | EGG STRAW WHEAT |
| 6000000 | ICE_CREAM_SHOP | PIZZA_SHOP | BAKERY | ICE_CREAM_SHOP\|PIZZA_SHOP | MILK STRAW TOMATO WHEAT |
| 7770000 | SMOOTHIE_SHOP | FARMERS_MARKET | FARMERS_MARKET | SMOOTHIE_SHOP\|FARMERS_MARKET | CARROT MILK STRAW TOMATO WHEAT |
| 8000000 | YARN_STORE | SMOOTHIE_SHOP | FARMERS_MARKET | YARN_STORE\|SMOOTHIE_SHOP | MILK STRAW WOOL |
| 9000000 | BAKERY | ICE_CREAM_SHOP | BRUNCH_SPOT | BAKERY\|ICE_CREAM_SHOP | EGG MILK STRAW WHEAT |

**Stratification verdict**

* 8/8 seeds sit on 8 distinct (day3,day6) signatures, and 8/8 distinct (day3,day6,day9)
  signatures: **no two gate seeds share a world**. The panel is not double-counting a world.
* Economically it is still lumpy. Grouping by the *product set* the town demands in days 3-8
  collapses 8 seeds to **7 profiles**, with **1000000 and 7770000 identical**
  (`CARROT MILK STRAWBERRY TOMATO WHEAT`) — those two seeds are one economic world, so any
  "wins on both" claim is one world, not two independent samples.
* Shop-type marginals are far from uniform for a panel this small. Day 3 covers only 6/8 shops
  (PIZZA x2, YARN x2; **FARMERS_MARKET and PET_CAFE never appear**), day 6 covers 7/8 (no
  YARN_STORE), and **day 9 covers only 4/8 shops with BAKERY x3 + FARMERS_MARKET x3 = 6 of 8
  seeds**. Any challenger whose edge depends on wool, yarn or egg demand in week 2 is being
  screened in a panel that mostly does not contain that demand; conversely a strawberry/
  wheat-friendly route gets a free pass on 6/8 seeds.
* Per-day shop-type frequencies over the 128-seed census are close to uniform
  (day 3: YARN 18.0%, PIZZA 14.8%, ..., BAKERY 6.2%), so the gate8 skew is small-sample
  luck in the seed choice, not an RNG bias.

## 4. 128-seed census (`results/world_census_0920.csv`)

Seeds 1000000..1000127, 3 policies x (mirror, vsv3 both seats) = 384 games, 14 days each,
oracle agreement 1536/1536, wall time 3 min 31 s on 12 workers.

* distinct (day3,day6) worlds: **54 of 64 possible** (uniform-random expectation ~55.5) —
  largest class holds 5 seeds (2 with 4).
* distinct (day3,day6,day9) worlds: **119 of 128 seeds** (uniform expectation ~113 of 512);
  distinct day-3-8 demand profiles: 25.
* i.e. the shop stream is statistically indistinguishable from uniform over shops; the
  *panel*, not the engine, is the source of the imbalance.

## 5. Does the panel support a world-conditioned route overlay?

Enough **diversity**, not enough **replication**.

* Diversity: yes — 54 distinct (day3,day6) worlds and 25 demand profiles exist in a 128-seed
  window, and worlds are free to compute (pure math, zero sim) for days 3-9. A stratified
  census panel can therefore be built offline at no sim cost.
* Honesty of the *current* gate8: no. One seed per world means zero within-world degrees of
  freedom; you cannot separate "route is better" from "route likes this world", and the panel
  systematically under-represents PET_CAFE/YARN_STORE demand in week 1 and 4 of 8 shops in
  week 2. Screening a world-conditioned overlay on gate8 would be a coin flip dressed as data
  (the same trap as the refuted sell-timing overlays).
* Minimum honest design: 2+ seeds per demand profile (target ~16-24 seeds over the 7 observed
  profiles), stratified report by world rather than pooled mean, plus the seat-swap pair.
  Re-derive `empty_count` by sim for any challenger that does not fill its board by day 0
  (day 9 onward is already policy-sensitive: 5/128 seeds flip).

## 6. Files / reproduction

* `results/gate_seed_worlds.csv` — 32 rows (8 gate seeds x `mirror`,`vsv3` swap0/swap1,`pass`),
  cols include `day3_shop, day6_shop, day9_shop, day12_shop, *_pred, empty_d2/5/8/11,
  seat_d2/5/8/11, match_*, world_id, world_id_3, world_id_4`.
* `results/world_census_0920.csv` — 384 rows, same schema, seeds 1000000..1000127.
* `tools/shop_oracle.py` — oracle port + engine instrumentation + `verify|gate|census` CLI.
* Reproduce: `py tools/engine_assert.py` then
  `WybeV2/rank_env/Scripts/python.exe tools/shop_oracle.py verify --days 14 --seeds 1000000,9000000 --policies pass,mirror`
  (`gate` / `census` modes as in section 0-4). Expect `kaggle_environments 1.32.7`; the
  OpenSpiel "Unknown game" stdout spam on import is benign.
