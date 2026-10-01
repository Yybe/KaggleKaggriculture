# World-stratified gate panel — 16 seeds over 8 replicated shop worlds (2026-09-20)

Offline tooling only. No agent, submission or live file was touched; no gate
simulation was run for tasks 1-2 (the whole census + panel is **0.9 s of pure
shop-RNG math**). Follows `results/WORLD_TAGGING_0920.md` (oracle + why worlds are
seed-only on days 3 and 6).

New files: `tools/world_panel.py` (census + panel builder), `tools/panel_report.py`
(reporting-only stratifier), `results/world_census_512.csv`,
`results/gate_panel_worldstrat.csv`. `tools/gate_eval.py`,
`tools/diag_bench_seeds.py` and `tools/shop_oracle.py` were **not** modified.

## 1. Naming correction: which file is "the gate"

The task brief pointed at `tools/gate_eval.py` for the challenger gate. It is not:

* `tools/gate_eval.py` = the old **V15 sell-timing** evaluator (docstring +
  `LOSS_SEEDS`/`WIN_SEEDS`, small seeds 2000-4774). It runs champion-vs-itself and
  scores price thresholds; it cannot A/B two different agents.
* The real challenger screen that produced the 62 `results/*_gate8*.txt` files is
  **`tools/diag_bench_seeds.py <base> <challenger> <seed_csv> <out.txt> --interval 24`**,
  driven by `tools/crop_gate8.sh` with
  `SEEDS_A = 1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000`
  (= `shop_oracle.GATE_SEEDS`, identical in `bench_all_vs_v3.py`, `bench_v29.py`,
  `bench_v29_fleet.py`, `bench_v3_vs_hardened.py`, `evaluate_apexx_fast.py`,
  `tune_v18_apex.py`, `diag_bench_seeds.py`).

Both tools already take an arbitrary seed list on the command line (positional), so
**no flag was needed and no default run path changed** — the panel plugs in as an
argument (`git diff tools/gate_eval.py` is clean; mtime unchanged). `gate_eval.py`'s
22 legacy seeds were still *tagged* into the census for completeness.

## 2. Census extended by oracle math (`results/world_census_512.csv`)

`world_of(seed) = (shop_for(seed,2,0), shop_for(seed,5,0))` — the `empty_count = 0`
rule proven 384/384 in WORLD_TAGGING §2. Columns: `seed, day3_shop, day6_shop, world_id`.

* **541 rows**: seeds 1_000_000..1_000_511 + the 8 gate seeds (1000000 overlaps) +
  gate_eval.py's `LOSS_SEEDS`/`WIN_SEEDS` (22), deduped. 0 sims, 0.9 s.
* **64/64 possible worlds present** (vs 54/64 at 128 seeds — the 512 pool saturates
  the space), largest class 19 seeds, **0 worlds with fewer than 2 seeds**, so the
  fallback "search further seed ranges" branch (`EXTRA_RANGES`, implemented) never fired.
* Cross-check: **128/128** identical to the *sim-measured* `world_census_0920.csv`
  mirror-policy worlds, and the 8 gate worlds reproduce WORLD_TAGGING §3 exactly.
* Day-3 marginals over the pool: BRUNCH 16.2%, PIZZA 13.9%, ICE_CREAM 13.7%,
  FARMERS_MARKET 13.7%, YARN 13.3%, PET_CAFE 10.5%, BAKERY 9.8%, SMOOTHIE 9.0%
  (uniform = 12.5%) -> engine is unbiased, the old panel was just unlucky.

## 3. The panel (`results/gate_panel_worldstrat.csv`) — 16 seeds, 8 worlds, 2 seeds each

Selection = brute force over all 8! = 40320 assignments of day-3 shop type -> day-6
shop type, so **every one of the 8 shops appears exactly twice in week 1** (once on
day 3, once on day 6). Feasibility first (>=2 seeds/world), then (i) keep as many
gate8 worlds as possible for comparability with the 62 historical runs, (ii) maximise
distinct week-1 demand sets, (iii) maximise replication depth. Demand sets come from
the engine's static `SHOPS` table (products consumed by the two week-1 shops), which
reproduces WORLD_TAGGING's "first-week products demanded" column exactly.

| pair (anchor + twin) | day 3 shop | day 6 shop | from | week-1 (d3-d8) shop demand | 512-pool depth |
|---|---|---|---|---|---|
| **9000000** + 1000250 | BAKERY | ICE_CREAM_SHOP | gate8 | EGG MILK STRAW WHEAT | 8 |
| **5000000** + 1000047 | BRUNCH_SPOT | BAKERY | gate8 | EGG STRAW WHEAT | 8 |
| 1000039 + 1000049 | FARMERS_MARKET | YARN_STORE | **NEW** | CARROT STRAW TOMATO WHEAT **WOOL** | 11 |
| **6000000** + 1000004 | ICE_CREAM_SHOP | PIZZA_SHOP | gate8 | MILK STRAW TOMATO WHEAT | 12 |
| 1000024 + 1000076 | PET_CAFE | PET_CAFE | **NEW** | CARROT (only; 2x draw) | 13 |
| **3330000** + 1000005 | PIZZA_SHOP | BRUNCH_SPOT | gate8 | EGG MILK STRAW TOMATO WHEAT | 9 |
| **7770000** + 1000078 | SMOOTHIE_SHOP | FARMERS_MARKET | gate8 | CARROT MILK STRAW TOMATO WHEAT | 4 |
| **8000000** + 1000048 | YARN_STORE | SMOOTHIE_SHOP | gate8 | MILK STRAW **WOOL** | 7 |

Seed list for the harness (order = as written in the CSV):
`9000000,1000250,5000000,1000047,1000039,1000049,6000000,1000004,1000024,1000076,3330000,1000005,7770000,1000078,8000000,1000048`

### Coverage vs gate8

| property | gate8 | panel16 |
|---|---|---|
| distinct (day3,day6) worlds / seeds | 8/8 (**0 within-world df**) | 8/16 -> **2 seeds per world** |
| day-3 shop types covered | 6/8 (PIZZA x2, YARN x2; **no FARMERS_MARKET, no PET_CAFE**) | **8/8, exactly once** |
| day-6 shop types covered | 7/8 (**no YARN_STORE**) | **8/8, exactly once** |
| #shop types appearing >1x in week 1 | 2 (PIZZA, FARMERS_MARKET) | 0 (each shop exactly 2x across d3+d6) |
| distinct week-1 demand profiles | 7/8 (1000000 == 7770000) | **8/8** |
| wool-demand worlds | 2/8 | 2/8 (now replicated pairs) |
| egg-demand worlds | 3/8 | 3/8 |
| carrot / milk / strawberry / wheat | 3 / 6 / 7 / 6 | 3 / 5 / 7 / 6 |
| cost | — | drops gate seeds **1000000, 2000000** (the duplicated-PIZZA / duplicated-YARN cells) in exchange for the two missing day-3 shop types |

Product *marginals* barely move (gate8 was not that skewed at product level); the
real repair is **replication** (0 -> 1 within-world contrast per world, enough for a
paired sign test over 8 worlds) plus **shop-type coverage** (6/8 -> 8/8 on day 3) and
one demand profile recovered (7 -> 8).

## 4. How to run a challenger on the panel

```bash
PY=WybeV2/rank_env/Scripts/python.exe      # kaggle_environments 1.32.7
# 32 games (16 seeds x 2 seats), ~2-4 min:
$PY tools/diag_bench_seeds.py agents/pub_metav4_early.py agents/CHALLENGER.py \
    "$($PY tools/world_panel.py seeds)" results/chall_panel16.txt --interval 24
# then the honest (world-stratified) read:
py tools/panel_report.py results/chall_panel16.txt --mapping results/gate_panel_worldstrat.csv
# A/B two challengers or a challenger vs its control, paired per world:
py tools/panel_report.py results/A_panel16.txt results/B_panel16.txt \
    --mapping results/gate_panel_worldstrat.csv
```

`tools/world_panel.py seeds` re-emits the list from the CSV, so the panel can never
drift from its tag file. Rebuild everything with
`$PY tools/world_panel.py census && $PY tools/world_panel.py panel`.

## 5. panel_report.py smoke test (parses real gate8 files)

`py tools/panel_report.py results/crop_vs_champ_r1.txt` (mapping:
`results/gate_seed_worlds.csv`, policies `mirror,vsv3`; `pass` is ignored because it
sits on a *different* world):

```
world (day3|day6)                  n gms  W  L  T   mean d  median   spread  seeds
PIZZA_SHOP|FARMERS_MARKET          1   2  0  2  0      -40     -40        0  1000000
... 8 worlds, one seed each ...
  POOLED  per-game mean delta        : -103   (16 games, no world correction)
  STRAT unweighted mean of world means: -103   (8 worlds; equal weight per world)
  worlds early>crop: 2 | crop>early: 6 | world-level sign test p=0.289
  within-world replication: min 1 / max 1 seeds per world -> NO within-world df
```

Pooled -103 reproduces that file's own `Mean Delta: -103` line exactly (parser
validated), and `+50` / `+155` likewise for `early_vs_metav4_ctrl.txt` /
`crop_vs_metav4.txt`. The paired mode on that control pair prints per-world diffs and
reports `paired diff mean -105 == naive pooled difference -105`, i.e. on a
non-replicated panel the "stratified" number cannot add information — which is the
whole reason for panel16. It also flags seeds missing from the mapping
(`crop_vs_champ_r1.txt` vs the panel CSV -> 1000000/2000000 bucketed `(unmapped)`).
Note the sign test on gate8: 6/8 worlds "losing" is only p=0.289.

## 6. Limits

* The seed-only tag holds **only for routes that fill their board by end of day 0**
  (WORLD_TAGGING §2). A challenger that plants late / digs / buys land differently can
  shift `empty_d2` or `empty_d5`, which flips the shop for 66% / 61% of seeds. For any
  such challenger, re-derive worlds with
  `$PY tools/shop_oracle.py gate --seeds ... --policies mirror` (sim) before trusting
  the tags, or verify at least that `empty_d2 == empty_d5 == 0`.
* Day 9+ is already policy-sensitive (5/128 seeds flip) and day 12+ is not taggable,
  so `world_id` here is a week-1 (day-3/6) tag only.
* 16 seeds = 8 worlds x 2 is still small: it supports a sign test and a within-world
  contrast, not a 3-way shop-interaction overlay. A double-draw world
  (`PET_CAFE|PET_CAFE`, the only cell where day3 == day6) exists because the engine
  draws shops with replacement.
* Seat swap in `diag_bench_seeds.py` output is not an independent world sample
  (mirror-like matchups give byte-identical swap=0/swap=1 rows), which is exactly why
  replication has to come from a second *seed* on the same world.
* Panel membership is a coverage choice, not a claim about live opponent mix; the two
  dropped gate8 worlds remain reachable by running gate8 alongside (cost: 16 games).
