# E119 — Fert-coverage parity: the last named lever from V29 is closed with a mechanism (2026-09-25)

Engine pin `kaggle-environments 1.32.7` (interpreter `WybeV2/rank_env/Scripts/python.exe`),
`townCenterSellInterval=24`, `episodeSteps=720`.
Spine measured: `agents/futurev1_forecast.py` (md5 `4d0241a2…`, current champion, read-only).
Winner cohort: 30 live top-10 replay tapes in `results/top10_tapes/` (2026-09-21 pull), 60 seat-rows,
22 rows at reward ≥ 100k.
Tools: `tools/e119_fert_scope.py` (per-crop fertilizer coverage), `tools/e119_revenue_split.py`
(product revenue attribution). Data: `results/e119_replays.json`, `results/e119_champion.json`,
logs `results/e119_fert_scope.log`, `results/e119_champion.log`.
One code path for both sides (`e118_dna_gap.census`), so every column is comparable.

## 1 — Why this measurement existed

`V29_FERT_SUPPLY_CHAIN_20260923.md` closed the fertilizer *supply* axis (456 units in / 114 applied /
`input_stock_shortfalls = 0`) and named exactly one live lever it did not build:

> "The live lever is the **tour's crop scope**: `_R51_INPUT_CROPS` (`:2153`) … exclude
> STRAWBERRY/MELON, which are the only crops whose price clears the `:2441` ROI gate with room to
> spare … Covering the 107 uncovered strawberry tile-days/episode alone would take applications
> from 114 → ~221, inside the champions' 135–249 band, with zero additional purchases."

Those strawberry applications were later built and gated as V30/V30b/V33 on the V12 lineage
(R1 2W/6L −265.8; 1W/6L/1T −293.5, `APEX_V12_AGENT_DOCUMENTATION_20260923.md:41`) and again on the
FutureV1 spine (Round-3 ledger: 0W/8L/0T mean −1,655). So the lever was tried and lost — but nobody
had measured *why*, and V29's premise ("we under-fertilize relative to champions") was still being
re-quoted as an open opportunity in `DECISIVE_MECHANISMS_SURVEY_20260924.md:54`.

## 2 — Result: coverage is at parity, per crop

Fertilizer-covered tile-days ÷ crop tile-days (day-deduplicated, `/24` per turn):

| crop | champion tile-days | champion fert-covered | cover % | winner≥100k tile-days | winner fert-covered | cover % |
|---|---|---|---|---|---|---|
| WHEAT | 470.8 | 72.2 | 15.3 % | 443.8 | 75.7 | 17.1 % |
| CARROT | 126.5 | 27.1 | 21.4 % | 106.8 | 13.5 | 12.6 % |
| STRAWBERRY | 532.0 | 149.0 | **28.0 %** | 442.2 | 124.7 | **28.2 %** |
| TOMATO | 0.0 | 0.0 | — | 96.6 | 28.0 | 29.0 % |
| MELON | 118.2 | 0.0 | 0 % | 133.1 | 1.2 | 0.9 % |
| `FERTILIZE` ops/seat | | **116.0** | | | **154.1** | |
| money/seat | | **78,411** | | | **139,290** | |

Three conclusions, each of them a refutation of a quote still circulating in the docs:

1. **The strawberry fert-coverage premise is false on the current spine.** 28.0 % vs 28.2 % — we
   already match the winners' high-value-crop coverage to within 0.2 points. V29's "114 → 221
   applications with zero purchases" was computed against a *useful-days* denominator, not the
   winners' actual coverage; adding applications beyond parity can only oversupply. That is the
   mechanism behind the V30/V33 sign (`extra $120 units crash shared curve`), and it now explains
   both lineages' losses instead of merely recording them.
2. **MELON is not a lever even for the winners** (0.9 % coverage on 133 tile-days). Any future
   "extend the fert whitelist" idea is dead on the tapes, not just on the gates.
3. **The residual fertilizer gap is a crop-presence gap, not an intensity gap.** Our `FERTILIZE`
   count is 116 vs their 154; the entire difference sits in tomato-covered days (28.0 vs 0.0) and
   wheat (75.7 vs 72.2 is noise). We plant zero tomatoes; they hold 8 % of their tile-days in tomato.
   Crop-mix overlays are separately refuted (E118 plant-redirect 0W/8L −138,265.9; Round-2
   contest-plant), so this is a tape-generation requirement, not a coverage requirement.

## 3 — Engine facts that make the parity result non-obvious

From `kaggle_environments/envs/kaggriculture/kaggriculture.py`:

- `CROPS:12-16` — tomato `{first 8, interval 1, max_yield 4, ongoing}`, strawberry
  `{first 10, interval 2, max_yield 4, ongoing}`, melon `{first 10, max_yield_day 12, max 6, not ongoing}`.
- `WATER:437-443` — for **non-ongoing** crops watering inside
  `[(max_yield_day+1)//2, max_yield_day]` adds `bonus = 2 if fertilized_until_day >= day else 1`.
- `_advance:799-801` — for **ongoing** crops the fertilizer bonus applies only on days the tile was
  also watered: `fertilized = was_watered and fertilized_until_day >= current_day`.
  So on strawberry/tomato, fertilizer is a *watering-contingent* ×2 — a coverage race against the
  water schedule, which is exactly the coupling E118 §5 showed an outside overlay cannot repair.
- `MARKET_PARAMS:40-50` — strawberry `above_func=linear, above_target=1.60, T=100` versus tomato
  `sqrt, 0.60, T=200`: 100 strawberry units move the price 1.6× its own base, tomato 0.6×. The
  winners' willingness to hold 8 % tomato acreage at *half* the base price is explained by curve
  depth, not yield. (Consequence tested in §4.)

## 4 — Where the 1.78× money gap actually lives (revenue attribution)

> **SUPERSEDED — see §9 (same day).** The "champion" column of this section was measured by running
> `agents/futurev1_forecast.py` **against itself** (`tools/e119_revenue_split.py local A self`), which
> is the mirrored-sell-stream regime that bench trap E73 says lies about `market.prices`. Re-measured
> in a valid regime (champion vs a no-op seat, engine 1.32.7 pin verified), the champion's realised
> quotes are at or **above** the winner band on milk, strawberry, wool, melon, egg and wheat. There is
> no price-capture gap, so the premise this section used to construct E120 was an artifact. §5-§7 are
> kept as the record of what was built from that premise and why it lost.


`tools/e119_revenue_split.py` walks every seat step, reads the SELL orders the seat declared, and
records (a) the **market price quoted at declaration** weighted by declared quantity, (b) money
inflow attributed to those orders (net-negative turns are skipped so hires/buys never contaminate
revenue), and (c) the fraction of turns the shed was at capacity.

Realised quote price per unit, champion vs the winner cohort:

| product | engine base | champion $/u | winner ≥100k $/u | winner/base | champion/base |
|---|---|---|---|---|---|
| MILK | 160 | **65** | **166** | 1.04 | 0.41 |
| WOOL | 200 | **75** | **197** | 0.99 | 0.38 |
| STRAWBERRY | 120 | **72** | **167** | 1.39 | 0.60 |
| EGG | 50 | 52 | 50 | 1.00 | 1.04 |
| WHEAT | 25 | 38 | 39 | 1.56 | 1.52 |
| MELON | 250 | 181 | 182 | 0.73 | 0.72 |
| CARROT | 35 | 53 | 47 | 1.34 | 1.51 |
| FERTILIZER | 100 | 15 | 61 | 0.61 | 0.15 |

Supporting rows (`results/e119_rev_replays.log`, `results/e119_rev_champion.log`): money 78,673 vs
141,655; inflow 94,018 vs 159,693; **shed full in 0.3 % of champion turns** (0.5 % for the cohort) —
the spine's own revenue split is milk 21 %, melon 22 %, fert 16 %, wool 10 %, i.e. it is already an
animal-product farm, and it sells those animal products at 0.4× base.

**The gap is price capture, not production.** On the three lines where the winners beat us on price
they beat us by 2.3–2.6×, and those three lines are 55 % of our revenue; on EGG/WHEAT/MELON/CARROT
the prices match. Same acreage (§2), same fert coverage (§2), same herd, and the storage constraint
that V29 assumed forced the drip-selling does not bind: the shed is at capacity 0.3 % of the season.

Engine reason the timing matters more for these lines than for wheat (`MARKET_PARAMS:43-48`):
strawberry, milk and wool are the three `above_func=linear` products with the *smallest* capacity
`T` (100, 122, 105) and the *largest* `above_target` (1.60, 1.60, 3.20), so each unit sold above
`I0 = 10000` knocks 1.6 / 1.9 / 6.1 dollars off the price of every unit still to be sold, and the
town drains them at only ~6 units/day/shop (`_town_consume:726-748`). FERTILIZER is the extreme
case: `TOWN_CENTER_PRODUCTS:114` **excludes** fertilizer and no shop in `SHOPS:103-111` consumes
it, so its inventory is monotone in our own sells — but this is not an available lever, see §5.

## 5 — Fertilizer export: already refuted, re-confirmed against the tapes

`LEDGER_20260920.md:28` and `PLAN_3000_spine_extraction.md:10` close fert-retention: `_r85_fertilizer`
sells only above the plan-reserve floor (`max(14, route_reserve+dedicated)`), the retained surplus has
no tape consumer, and fert is a top-5 revenue line at 13–18 k/game. `results/ED_LEDGER_0920.md:65` adds
the arithmetic trap that makes fert volume look huge in the first place: the engine clamps a SELL to
actual shed contents, so big declared fert quantities are **no-op sentinels** (step 671 reads
`planned={'FERTILIZER': 997}` → `realised={'FERTILIZER': -8}`, money +0). The champion's 1115 declared
fert units in §4 are that artifact, not 1115 units sold — which is exactly why the price column, not
the quantity column, is the readable signal here.

## 6 — The copy target this produces, and what was built from it

The one behaviour that separates us from the winners on the three lines they beat us on is *when a
sell is placed*: they sell milk/wool/strawberry into scarcity (quote ≥ base), we drip them into the
glut at 0.4–0.6× base, and we are not storage-constrained when we do it (shed full 0.3 % of turns).
That is a timing rule, not a prediction rule, which matters because the prediction family is already
refuted on this spine (E73/E74/E100; `project-sell-timing-overlay-refuted`), as is route re-fit
(−312.3/world) and any naive quantity cut (fert-retention, §5).

**E120 = scarcity-conditioned hold-and-release** (`tools/build_e120_scarcity_hold.py`,
`agents/pub_e120_{ctrl,hold,hold11}.py`, 48th onion layer on `futurev1_forecast.py`): on a turn where
`market.prices[item] < base[item]` for MILK/WOOL/STRAWBERRY/EGG, delete the parent's SELL order and
bank the quantity (per-item bank cap 40, surplus still sold); on the first turn where the quote
clears base, re-emit the banked quantity in one order. Volume is conserved, never suppressed.
Never held on `step % 24 == 23` (the FutureV1 preempt turn), never outside `120 ≤ step < 696`, and
force-released from step 696 so nothing is stranded. `ctrl` returns the parent action untouched.

Probe (`tools/probe_e120.py`, `results/e120_probe.log`, seeds 2e6/3.33e6, both seats):

| variant | fires/game | defers | releases | release_units vs defer_units | errors |
|---|---|---|---|---|---|
| ctrl | 0 | 0 | 0 | — | 0 |
| hold | 54 / 84 | 40 / 72 | 14 / 12 | 358 = 358, 342 = 342 | 0 |
| hold11 (release at 1.1× base) | 60 / 62 | 50 / 54 | 10 / 8 | 326 = 326, 232 = 232 | 0 |

Seat-0 quote prices in the same probe, `hold11` vs `ctrl` on seed 3.33e6: STRAWBERRY **80.4 → 237.9**,
MILK 67.2 → 139.6, i.e. the release side does capture the winners' price band. Self-play cannot price
the mechanism (mirror symmetry, E118 §4 method law), so the gate below is the only admissible
evidence; self-play rewards stayed in the 63–79 k band with no collapsed episode, which is what a
probe is for.

Two build-time defects worth recording, both caught by AGENTS.md Rule 1 step 5 before any gate seed
was spent, and both of them generic:

1. **`sys` is not imported by the spine**, so a `sys.stderr.write` inside the layer's own
   `except` handler raised `NameError` *from the handler*, the engine killed that seat, and the run
   reported reward 16,036 against 137,627 for the other seat — a result that reads as "the mechanism
   is wildly asymmetric" when it is a crash. Fixed by importing the helpers under layer-prefixed
   names and asserting they are in `agent.__globals__`; exception text now goes into
   `_E120_MEM['first_error']` instead of stderr, because piped stderr from background jobs is
   swallowed (`E118_DNA_COPY_20260925.md` §5 noted the same loss).
2. A leftover `del have` from an abandoned edit produced 16 `UnboundLocalError`s per game, each
   silently returning the parent's action *after* the bank had been credited — a volume leak that
   would have double-sold the banked units. `errors == 0` is now a precondition for gating.

## 7 — Gate: REFUTED, and the price column was reading an effect, not a lever

`tools/run_h2h.py <cand> agents/futurev1_forecast.py r1` — 8 seeds × both seats, engine
`kaggle-environments 1.32.7`, `townCenterSellInterval=24`, fresh process per game:

| candidate | bank | W/L/T | mean Δ | per-seed deltas |
|---|---|---|---|---|
| `pub_e120_hold.py` (release at ≥ base) | r1 | **0W/8L/0T** | **−4,210.6** | −7,487 −6,171 −5,082 −4,433 −4,160 −3,663 −1,649 −1,040 |
| `pub_e120_hold11.py` (release at ≥ 1.1× base) | r1 | **0W/8L/0T** | **−48,503.4** | −84,725 −66,925 −60,403 −58,926 −58,618 −55,198 −1,739 −1,493 |

Logs: `results/e120_hold_r1.log`, `results/e120_hold11_r1.log`. Every seed lost under both settings
and zero ties, so the layer is unambiguously live and unambiguously negative; and the loss is
**monotone in hold aggressiveness** (1.0× base −4.2 k, 1.1× base −48.5 k), which is the signature of
the mechanism itself failing rather than a threshold being mis-tuned.

Why the tape reading did not transfer. `MARKET_PARAMS` prices are a function of *cumulative* market
inventory, and the town's consumption of a product (~6 units/day/shop, `_town_consume:726-748`) is
nearly independent of our schedule. Deferring therefore does not remove supply from the season — it
re-times it, and because the curve is monotone in cumulative volume, a conserved quantity released
as one 40-unit order earns *less* per unit than the same 40 units drip-sold across 20 turns.
The measured "winners quote $167 on milk where we quote $65" is an **effect of selling less into a
rising market**, not something a same-volume hold policy can buy. The correct causal direction is
volume, and volume is production-determined: that puts the gap back on the crop/herd mix and the
tape, which is where E118 already left it (see `E118_DNA_COPY_20260925.md` §6).

This closes the third and last sell-timing construction family on this spine:

1. predict-then-sell (E73/E74/E100) — dead;
2. front-run the clone wave, debt-accounted (Apex V5 → E116/FutureV1) — alive, already in the champion;
3. hold-and-release on scarcity, volume-conserving (E120, this note) — dead, 0W/8L ×2 banks of seeds.

## 9 — Correction: the gap is executed VOLUME and crop MIX, not price (valid-regime re-measure)

Trap E73 recurred at *analysis* level, not just probe level. `tools/e119_revenue_split.py local A self`
loads the champion into both seats, so the two identical sell streams hammer the same price curve and
every animal-product quote collapses toward `PRICE_FLOOR`. The non-mirror probe (champion vs
`tools/_noop_agent.py`, seeds 1000000-1000002, engine pin `kaggle_environments==1.32.7` verified in the
run, output `results/e119_revenue_champion_vsnoop.json`, mirror copy preserved at
`results/e119_revenue_champion_mirror.json`):

| product | engine base (`MARKET_PARAMS:42-50`) | winner ≥100k $/u | champion **mirror** $/u | champion **vs no-op** $/u | champ/no-op ÷ winner |
|---|---|---|---|---|---|
| STRAWBERRY | 120 | 167.0 | 71.9 | **241.7** | 1.45 |
| MILK | 160 | 165.9 | 64.9 | **183.6** | 1.11 |
| WOOL | 200 | 197.4 | 75.3 | 180.6 | 0.91 |
| MELON | 250 | 182.1 | 181.1 | 237.7 | 1.31 |
| WHEAT | 25 | 38.5 | 37.7 | 42.2 | 1.10 |
| EGG | 50 | 49.7 | 51.9 | 65.2 | 1.31 |
| CARROT | 35 | 46.9 | 53.4 | 36.3 | 0.77 |
| FERTILIZER | 100 | 61.5 | 14.8 | 70.0 | 1.14 |
| TOMATO | 60 | 83.7 | — (never sold) | — (never sold) | **0 volume** |

Money: champion 88,831 (vs no-op) / 78,673 (mirror) vs winners 141,655. Since unit prices match or
favor the champion on 7 of 9 lines, the 1.6× money gap is arithmetic volume, and the volume line where
they differ most is the one we are at zero on: TOMATO.

Executed-op census, one code path (`tools/e118_gap_table.py` internals over
`results/e118_cohort_replays.json`, winners = 11 seats at money ≥ 100k, vs
`results/e118_champion_census.json`, 6 champion rows), winner ÷ champion:

**At parity** — tile_days_total 1245 vs 1286 (0.97), plant_total 247 vs 242, op_HARVEST 500 vs 492,
animal_tile_days 371 vs 360, op_PLACE 110 vs 106, hands_ops 6637 vs 6292, fert_covered_days 258 vs 262,
hires_day_sum 294 vs 278, quads_end 3.0 vs 3.3.
**The gap** — crop mix and what that mix yields:

| field | winners | champion | ratio |
|---|---|---|---|
| crop_td_TOMATO | 161.9 | 38.3 | 4.22 |
| plant_TOMATO | 15.4 | 3.3 | 4.61 |
| crop_td_MELON / plant_MELON | 140.1 / 16.0 | 118.2 / 12.0 | 1.19 / 1.33 |
| op_FEED | 367.3 | 320.3 | 1.15 |
| op_CARE | 353.9 | 403.3 | **0.88** (we spend more, get less) |
| crop_td_STRAWBERRY | 415.2 | 532.0 | 0.78 |
| crop_td_WHEAT | 436.6 | 479.9 | 0.91 |
| crop_td_CARROT | 91.3 | 117.4 | 0.78 |
| op_PASS (idle turns) | 344.5 | 561.7 | **0.61** (217 turns/seat of unused labor) |

So the copy list, in the winners' own units: displace ~120 strawberry+wheat+carrot tile-days and ~14
plantings into a TOMATO+MELON cycle (tomato is `ongoing`, `first_yield_day 8`, `interval 1`,
`max_yield 4` → re-harvest every day from day 8 for ~$60-84 a unit; melon `max_yield 6` at base 250),
fund it from the 217 idle PASS turns/seat, and cut the wheat over-selling (winners sell 377 declared
wheat/seat against our 868) so the freed market slots and shed space go to the high-base lines.
`op_CARE` being *higher* for us while egg/milk/wool volume is lower says the animal axis is a species
and feeding-schedule mix problem, not a tending-effort problem (`ANIMALS:20-22` — GOOSE interval 1 vs
COW 2 vs SHEEP 3, i.e. egg ticks per fed-day are 2-3× milk/wool).

Prior art this does **not** repeat: E118 `plant` redirect (10 wheat/carrot PLANT ops rewritten to TOMATO
at the action layer) lost −138,266/seed and E57c block-doubling lost 9-39k per firing world — both were
*overlay rewrites of a tape that has no tomato cycle in it*, so the accrual/water/harvest schedule never
came with the crop. The construction that matches the DNA is a tape-level block where plant→water→fert→
harvest for the tomato/melon cycle is co-designed, per §8 of `E118` and the E104 "new co-designed
livestock+wheat+hire block" conclusion. No overlay variant of that is built yet.

## 10 — E121: the mix construction from §9, built and refuted same day

`tools/build_e121_tomato_swap.py` converts up to N of the spine's `['PLANT','STRAWBERRY']` hand ops into
`['PLANT','TOMATO']` (only while `step <= 20*24`), so the tile stays on an **ongoing-crop route** and keeps
its water/fertilize/harvest schedule — the mechanism E118's wheat→tomato redirect lacked. Variants
ctrl/n10/n20/n40; layer proven live first: `swaps = 20`, `candidates = 20`, `errors = 0`, `delta_bytes
+1676`, 48 agent layers, `engine 1.32.7` asserted in the probe process (the gate log itself carries no pin
line — verified separately the same session, noted per trap 7).

| variant | bank | result | per-seed deltas |
|---|---|---|---|
| n20 | R1 (16 games, both seats) | **0W/8L/0T, mean −25,121.2** | −37,720 −30,464 −27,945 −27,317 −24,923 −21,670 −19,957 −10,974 |

Probe games agreed before the gate: seat rewards 96,372 vs 107,291 and 77,868 vs 102,458. Zero ties, so
the gate is informative: swapping ongoing-crop identity from strawberry to tomato is worth **negative**
against this spine even with full schedule continuity.

Reading: the winner cohort's tomato acreage is not an independently portable decision — it is downstream
of *their* route economics (their strawberry tile-days are 415 vs our 532 because their routes were
co-designed with tomato in the set, so the marginal tile-day goes to the $60-base daily-renewing crop
rather than the $120-base 2-day one). Removing strawberry tile-days from a spine whose routes are already
balanced around strawberry loses both streams at once, which is the third independent confirmation of the
production-overlay closure (E118 redirect −138,266, E57c doubling, V20 PASS-only, E121 swap −25,121).

Consequence for the copy channel: nothing on the market axis and nothing on the overlay-production axis
reproduces the winner DNA. The remaining construction is the one both §9 and E104 point at — a new
co-designed block (plant/water/fertilize/harvest/sell generated together for a tomato+melon cycle with
its own labor budget), i.e. tape generation, not a graft. Not built here.

## 12 — E122: executed product flow at matched regime, and the last gap is fertilizer *carry*

`tools/e122_shed_flow.py` (asserts engine 1.32.7 at import) measures what the shed actually receives —
`sum(positive shed deltas)` per product is a lower bound on units harvested, because declared SELL
quantities are clamp-sentinels and quoted prices are mirror-sensitive. Champion seats only (the no-op
seats are filtered; they hold money 3,000 and would halve any per-seat mean — see the caveat below).

| field | winner 100k+ (15 live seats) | cohort all (44) | champion vs no-op (3 seats) | champ ÷ winner |
|---|---|---|---|---|
| HARVEST ops | 483.7 | 418.4 | 482.3 | **0.997 (parity)** |
| WATER ops | 1169.1 | 1119.0 | 1097.0 | 0.94 |
| CARE ops | 372.1 | 282.5 | 404.0 | 1.09 |
| FEED ops | 387.6 | 294.3 | 359.0 | 0.93 |
| **FERTILIZE ops** | **152.4** | 113.8 | **95.0** | **0.62** |
| units gained / HARVEST op | 3.39 | 3.59 | 2.98 | 0.88 |
| total units gained / game | 1640 | 1502 | 1436 | 0.88 |
| flow WHEAT / CARROT / TOMATO / STRAW / MELON | 733 / 76 / 67 / 154 / 28 | — | 656 / 54 / **0** / 120 / 12 | 0.89 / 0.71 / 0 / 0.78 / 0.43 |
| flow EGG / MILK / WOOL / FERTILIZER | 51 / 131 / 138 / 263 | — | 71 / 135 / 88 / 300 | 1.39 / 1.03 / 0.64 / 1.14 |
| money | 149,830 | 90,896 | 174,662 | 1.17 (uncorrected for regime) |

Two conclusions the copy channel has to accept:

1. **Labor and land are at parity** (harvest ops equal to the winner seat, water/feed within 6 %), so the
   residual volume gap is *yield per harvest op* — 2.98 vs 3.39 — and the only labor column where the
   champion is materially short is **FERTILIZE (95 vs 152)**, whose engine effect is exactly a yield
   multiplier (`+2` units instead of `+1` per accrual tick on watered days, `_advance:798-800`).
2. **The champion does not lack fertilizer; it lacks carry.** It collects ~300 FERTILIZER units/game into
   the shed (flow table) and sells most of them. `_apply_unit_action:312-321` binds `inv =
   _farmer_inventory(private, idx)` and `FERTILIZE:475-482` spends from **that** inventory via
   `_inv_take(inv, "FERTILIZER", 1)`; `private["inventories"]` is emptied into the shed and reset to
   `[{}]` at every end-of-day (`_drop_inventories_to_shed:843-856`, `:878-882`). So an application is only
   possible for a unit that picked up fert **that day** and then walked onto a PLANT tile — a
   PICKUP→move→FERTILIZE tour, not a spare op. That is the mechanism behind V13's "45 blocked ops with
   carried==0" and behind the memory law "next fert attempt must change the supply side".

E123 (`tools/build_e123_fert_use.py`, variants ctrl/app/app_sup20/app_sup60) was built to spend shed fert
on idle PASS units standing on plant tiles. It is **inert, and correctly so**: probe counters
`apps=0, idle_on_plant=0, errors=0` with `ctrl` byte-parity (`81232` vs `81232`), because `held` was read
from `private.shed.FERTILIZER`, which is 0 by day 29, and because a FERTILIZE op issued from a unit whose
*carried* inventory is empty returns silently at `:478-479`. The builder stays in the repo as the anchor
for the correct construction: the layer must (a) read/extend `private["inventories"][unit_index]`, (b)
spend an op on `PICKUP FERTILIZER` when the unit is shed-adjacent (`_is_shed_adjacent:138`), and (c) only
then convert a later PASS on a PLANT tile. Not attempted in this session — a half-built carry tour is the
exact failure class this note is about.

Regime caveat that must not be repeated: the §9 "champion money 88,831" figure came from averaging
`results/e119_revenue_champion_vsnoop.json` rows **including the no-op seats** (money 3,000 each). The
champion-only mean is 174,662 per seat-game, i.e. above the winner cohort's live 149,830 — the comparison
is not regime-matched (a no-op opponent does not depress our prices), so it is evidence that the earlier
"they out-earn us by 1.7× on identical production" framing was an artifact twice over, not a new claim of
strength.



## 14 — E124: the fertilizer *carry tour*, built and refuted at the probe (never gated)

§12 left one winner behaviour unimplemented: 152 FERTILIZE ops vs our 95. Since the engine spends
applications from the unit's carry and destroys carry at end of day, an application cycle must be
`PICKUP → move → FERTILIZE` inside one day. E124 (`tools/build_e124_fert_tour.py`) does exactly that,
and hijacks **only** turns where the spine's own farmer action is `['PASS']`, so it cannot displace a
plant/water/harvest (the E118/E121 failure class). Variant knobs: `MAX_APPS`, `K` (pickup size),
`RESERVE`, `SUP` + `BUFFER` (hold a fert buffer by stripping the parent's `SELL FERTILIZER` orders —
required, because `_r85_fertilizer` sells every collected unit on days 6-28 and leaves nothing).

Probe (`tools/probe_e124_fert_tour.py`, 2 seeds, seat 0 vs `tools/_noop_agent.py`, so the money column
is a *non-mirror* single-agent total; last-episode counters):

| variant | money (2 seeds) | apps | pickups | walks | hijacks | no_shed_fert | held_orders | errors |
|---|---|---|---|---|---|---|---|---|
| ctrl (layer OFF) | 320,474 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| tour45 | 317,788 (−2,686) | 1 | 1 | 7 | 56 | 47 | 0 | 0 |
| tour45_sup | 127,328 (−193,146) | **0** | 5 | 24 | 54 | 25 | 124 | 0 |
| tour20_sup | 127,328 (−193,146) | **0** | 5 | 24 | 54 | 25 | 124 | 0 |

ctrl is byte-parity with the champion, so the layer is not leaking when OFF. Reading of the two
independent failures:

1. **Supply is not the binding constraint the buffer fixes.** Without suppression the tour starves
   (`no_shed_fert` 47 of 56 hijacks) — §12's diagnosis, confirmed. With the buffer it finds fert
   (5 pickups) and still lands **zero** applications. `tour45_sup` and `tour20_sup` are byte-identical
   in outcome because `apps` never reaches either cap, i.e. `MAX_APPS` is inert here.
2. **The idle-turn budget is the wall.** 54 hijacks over 720 steps ≈ one spare farmer turn every 13
   steps, while a cycle costs 1 pickup + several single-step moves + the apply, and the day boundary
   (24 steps) voids the carry. The tour never completes an application before the carry is dropped,
   so `apps` stays 0 and `no_target` staying 0 confirms the carry>0 branch is what never runs.
3. **The supply-hold itself is very expensive**: 124 held sell orders cost ~96,500/seed vs the OFF
   control — the fert export stream is worth far more than the 45 applications it was meant to fund.

This is consistent with the earlier, independent E119a result (§2): per-crop fert *coverage* is already
at parity (strawberry 28.0 % vs 28.2 %), so even a successful application tour would be adding
intensity to crops we already cover at the winners' rate. Both directions now agree: the FERTILIZE-op
count difference is a **consequence** of the winners' crop presence/tape, not a portable lever.
The fertilizer axis is closed at 5 refuted constructions: V13 fertmax, V27/V29 crop-scoped fert,
E112 re-timing, E123 shed-gated use (inert container), E124 carry tour (this section).
Untried and now low-prior: a shop-BUY-funded tour — §12/§2 predict no coverage headroom to buy into,
and the idle-turn wall in (2) applies unchanged.

## 15 — State

Champion unchanged: `agents/futurev1_forecast.py` md5 `4d0241a2…`; `submission.py` untouched.
Nothing committed. `agents/pub_e120_*.py` are builder output and were deleted after the gate —
regenerate with `python tools/build_e120_scarcity_hold.py ctrl hold hold11`.
New fixture: `tools/_noop_agent.py` (the non-mirror price probe) and
`results/e119_revenue_champion_vsnoop.json` / `..._mirror.json` as the two regimes.
E122 fixtures: `tools/e122_shed_flow.py`, `results/e122_flow_replays.json`,
`results/e122_flow_local.json`, logs `results/e122_flow_{replays,local}.log`.
E123: `tools/build_e123_fert_use.py` built and probe-verified inert (§12); its `agents/pub_e123_fert_*.py`
sweep copies were deleted after the probe — regenerate with
`python tools/build_e123_fert_use.py ctrl app app_sup20 app_sup60`.
E124: `tools/build_e124_fert_tour.py` + `tools/probe_e124_fert_tour.py`; refuted at the probe (§14), so
never gated and its `agents/pub_e124_tour_*.py` sweep copies were deleted — regenerate with
`WybeV2/rank_env/Scripts/python.exe tools/build_e124_fert_tour.py ctrl tour45 tour45_sup tour20_sup`.



## 16 — E125/E126: the last live column on the copy list (animal feed discipline) — REFUTED

`tools/e122_shed_flow.py` had left one unexplained pair of signs: our `op_CARE` is *higher* than the
winners' (404 vs 361) while animal units are lower, and §9 recorded feed 388 vs 359. Engine law makes
that pairing suspicious (`kaggriculture.py`, `_daily_refresh_animals:805-833`): `CARE:525-530` only
sets `cared_today`, and the care bonus is paid **only if `fed_today` is true the same day** (`:829-830`)
and consumed only on a fed production day (`:826`); `FEED:505-513` is once per animal per day and costs
1 WHEAT from the unit's *carry*; `consecutive_unfed >= 2` makes the animal **escape** (`:817-820`).

### 16.1 Measurement (`tools/e125_feed_discipline.py`, engine pin asserted at import)

22 winner seats at reward >= 100k from `results/top10_tapes/` (32 tapes) vs 4 champion seat-games vs
`tools/_noop_agent.py`, same code path:

| field | winner_100k+ | champion |
|---|---|---|
| money | 141,655 | **180,498** |
| animal_td | 10,155 | 9,661 |
| fed_td | 5,187 | 4,637 |
| fed % of animal tile-days | 51.1 % | 48.0 % |
| feed_ops | 370.3 | 357.5 |
| care_ops | 360.9 | **404.0** |
| care/feed ratio | 0.98 | 1.13 |
| escapes | **7.0** | 0.2 |
| harvest-ready units pending (step-sum) | 8,051 | 6,975 |

The champion is at parity on feed *discipline* (48 % vs 51 % of animal tile-days fed, and 35x fewer
famine escapes), so the herd axis cannot be closed by feeding harder — the same verdict E104 reached
from the capacity side. The residual animal gap is per-day accrual (pending units 8,051 vs 6,975),
which §14 already showed is fert/carry-bound.

### 16.2 E126: the one legal reallocation the table implies — a graft that fires and loses

Care issued on an animal that is never fed that day can never pay, so `tools/build_e126_care_feed_pair.py`
swaps a parent `['CARE']` into `['FEED']` exactly when the unit stands on an animal tile whose
`fed_today` is False **and** its carry holds WHEAT. Pure op reallocation: no extra land, water, labor
or movement (the E124 wall does not apply). `ctrl` reproduces the champion's money byte-exactly on all
4 probe seeds (154,623 / 165,851 / 203,512 / 198,006), so the OFF path leaks nothing.

Probe (`tools/probe_e126_pair.py`, 4 seeds, vs no-op) explains why the premise is thin:
of 404 care ops per game, **~337 (83 %) already land on a fed animal**, 36 are blocked by empty wheat
carry, and only 20-49 qualify for the swap. Gate R1 (8 seeds x both seats, `results/e126_pair_r1.log`):

```
r1     n=16  0W/8L/0T  mean   -3056.9
       per-seed deltas: -5677, -3834, -3785, -3520, -2789, -2543, -1690, -617
```

Zero ties, 8/8 losses, and the same sign on every probe seed (-2,357 / -1,377 / -2,826 / -2,447).
Foregone care is worth more than the extra fed-day it buys: the swap spends the wheat that the fed-day
economics otherwise monetise, and the champion's care ops were already paired. Feed discipline is
therefore **not** a copyable advantage — the champion is already the better animal manager in this
cohort, which also retires the §9 reading of the care/feed columns.
