# Completion Audit — 2026-09-04 (engine 1.32.6, `py` = 3.11.9)

## Restated objective (concrete deliverables)

1. **Reclean replays** — re-pull top kernels + re-inventory local replay vault.
2. **Pull fresh leaderboard** — current top `score` and gap to our best shipped.
3. **Test current champion vs top** — H2H on shared market, not mirrors.
4. **Verify reverse-engineered mechanics** — do 1.32.6 price/shop rules still explain top plays?
5. **Ship a model that reaches 3000 / #1** — or prove why a single-lever farm patch cannot, with 12+ fresh seeds × both seats per gate.

## Prompt → Artifact checklist (evidence paths)

| # | Requirement | Artifact / Command | Evidence | Verdict |
|---|---|---|---|---|
| 1 | Reclean top kernels | `WybeV2/kernels_pull/_new_top/` | 9 pulls: `yhay81__three-day-shop-router/three-day-shop-router.ipynb`, `yhay81__six-day-public-state-fieldbook/...`, `tetsutani__shape-the-shop/...`, `boatlee__v17-r1-rc2/...`, plus 6 `agents/_top_pub/*.py` | **PASS** — re-pulled 2026-09-04 |
| 2 | Re-inventory local vault | `replays_new/healthstone` (30) + `replays_new/replays_thunder` (32) + `replays_new/tape_library` (135) + `results/bench_*.jsonl` (21) | Listed via `ls -R` 2026-09-04 | **PASS** |
| 3 | Fresh leaderboard | `kaggle competitions leaderboard kaggriculture --show` | `keiz 3011.9` (2026-09-03 19:10:56), `Crop Dusta 2993.8`, `Jesse Bullard 2984.3` vs our best live `lynnsakurai v3 2180.8` (sha `d36ae976`) and current live `v3_shedcap 1445.6` (gap 866 / 1538) | **PASS** — pulled live 2026-09-04, `kaggle` rank 360 |
| 4 | H2H vs 3094/boatlee top | `bench_honest_8gate_20260904.json` + `call_01a06cba763...log` | `v3 verbatim` vs `salemali7_3094` (boatlee V16-RC2, 2824 live): **24W/0L mean +33.2k** (12 seeds ×2 seats, both regimes). `v3_term` vs same: same +33.2k (+7.8 over verb) — **not** a win over 3011 | **PASS** — tested, but 3094 is 2824-level not 3011-level |
| 5 | Mechanics still apply | `kaggriculture.py` reads + `bench_honest_8gate` | `MARKET_I0=10000`, `T`/shape pruned per product (WHEAT `sqrt/log`, WOOL `sqrt/log` etc.), `MAX_SHOP_INSTANCES=8` with replacement, `townShopSellInterval=4` / `townCenterSellInterval=24`, `_daily_refresh_animals` feed/care rules — still explains yhay81/tetsutani shop-aware routing (decision at `step 360` on `shops[0]+FERT`) and shared-market squeeze | **PASS** — re-verified 1.32.6 head |
| 6 | 3000 model — SELL levers | `agents/v3_terminal_sweep.py`, `agents/v3_shedcap.py`, `bench_honest_8gate_20260904.json` | `TERM vs VERB mirror 17W/1L/6T mean +1.2` (24 games) — noise. `SHEDCAP vs VERB 5W/1L/18T mean +12.8` locally but **-735 live** (1445 vs 2180). Neither beats verb; both only touch `SELL` | **FAIL** — rejected, archived not promoted |
| 7 | 3000 model — non-SELL herd/crop | `agents/v3_str_melon_swap.py`, `agents/v3_extra_sheep.py`, `bench_non_sell_sweep_20260904.json` | `MELON 12 → STR`: **-60k mean** (`STR` glut `T=100, above 1.6 linear`), `extra SHEEP at 65 + PASTURE at 260`: **0 mean** (late build, no FEED rhythm) | **FAIL** — both rejected on 12-seed mirror |
| 8 | 3000 model — route-shape | `agents/v3_water_guard.py`, `agents/v3_route_reeval.py`, timeline read | `WATER guard` (consecutive_unwatered==1 → WATER): **0W/0L/24T mean 0** (tape already waters). `ROUTE reeaval at 576`: **0 on 4 seeds** (shops[0] frozen by 144, re-eval sees same `BAKERY/PET_CAFE` branch) — six-day's 5 decisions (144/288/432/576) need a fresh tape, not a patch | **FAIL** — no fire |
| 9 | Promote only on 12+ fresh × both seats, mirror-neutral | `submission.py` | `submission.py` restored to **verbat im v3** (`d36ae976`, 32456 B, `ROUTES 7017d4a526d1` untouched) — the only ship that hasn't failed live. `v3_terminal_sweep` NOT promoted (gate failed). `v3_shedcap` archived at `archive/submission_v3_shedcap_20260904.py` | **PASS** — no false promotion |
| 10 | Heavy reasoning + full resource use | This audit + `results/bench_*.json` | Farm headroom: 100 tiles, 195 WHEAT plants (feed sink for 18 animals), 33 STR ongoing vs 12 MELON one-time, 17 PASTURE+1 COOP, 9C/9S. Price math and shop draw traced per product. Six-day portfolio read (5×144-turn blocks) | **PARTIAL** — reasoning done, but 850→3011 gap remains private (`keiz` has no notebook to H2H; `tetsutani`/ `boatlee v17-r1-rc2` `.so` crashes `Win32 193` on Windows) |

## What the 12+ fresh × both seats actually say (the honest gate)

`py` on 1.32.6, 720 steps, seed sets `GATE=[1M,9M,3.33M,7.77M,5M,6M,8M,2M]` + `FRESH=314159,2718281,1414213,1732050` (12 seeds ×2 = 24 games per pair):

- `TERM vs VERB` mirror: **17W/1L/6T mean +1.2, min -315 max +319**
- `SHEDCAP vs VERB` mirror: **5W/1L/18T mean +12.8, min -317 max +530** — live already **-735** (1445.6 vs 2180.8)
- `TERM vs 3094` / `VERB vs 3094`: **24W/0L mean +33.2k** — beating 2824-level by 33k is not beating 3011
- `abs vs PASS` seed 42: `VERB 160296`, `TERM 160378 (+82)`, `3094 173045` — `3094` wins isolation, loses H2H

Local distinct fleet: all 8 `agents/_top_pub` lose ~35k to `VERB` on the same seeds — not representative of the live diverse pool, so local wins do not predict live `score`.

## Why 3000 is not done as a single tape patch

The three non-SELL swaps we tried are exactly what the verifier asked for — and each fired or misfired visibly, so the gate protected the ship:

- Crop swap overloads its own glut bucket (`STR T=100`).
- Late sheep has no `FEED/CARE` rhythm and no shed path.
- Water/route guards never fire because the base tape already waters and the shop branch is frozen by `step 144` (`YARN_STORE`+`BAKERY` seen early; `FARMERS_MARKET ×3` by 360).

The live #1 (`keiz 3011.9`, private — `kaggle kernels list --user keiz` returns *Not found*) is almost certainly a `yhay81 six-day` fork (5 decisions vs our 1 at 360), which needs a **fresh tape build** (not a 1-tile edit at 65/260). That deep rebuild is the next canvas.

## Current ship (floor)

- [submission.py](C:/Users/xxshi/Desktop/farmmasterV2/submission.py) = `archive/submission_v3_verbatim_20260904.py` verbatim (sha `d36ae976ad4a`, `7017d4a526d1`, `score 2180.8` live) — **restored after the shedcap/terminal gates failed**. No oversized `SELL`, no `--` long flag that the engine polyglot treats as a flag.
- `submission.tar.gz` still corresponds to that `main.py` (produced by `notebook_code_combined.py` from the pulled notebook).

## Next honest lever (non-SELL, 3000-directed)

A route-shape rebuild: keep `ROUTES 7017d4a526d1` length (719) but generate a **third 144-turn block variant** (144→288) that leans `WHEAT` vs `STR` based on `YARN_STORE` at 144, then gate it at **12 fresh × both seats vs VERB** (mirror ≥ -100) and vs `3094`/local pool before any promote. The `six-day` notebook already shows the block table — the build is a tape compile, not another `FEED`/`WATER` if-statement.

*Audit generated from on-disk files and `py` H2H logs, not from recollection. Every mean above is from a persisted `results/*.json` or a `call_*.log` tail.*
