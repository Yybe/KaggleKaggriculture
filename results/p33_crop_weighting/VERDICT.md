# P33 VERDICT — "which pool" is measured too, and it closes the carrot lane and the tomato lane

`tools/p33_crop_weighting.py` · 170 unique `(ep,seat)` cells, 16 teams with ≥4 episodes, engine pin
1.32.7, read-only over `results/p6_field_20260925/phase_p6.jsonl` (`tile_days` per crop per seat-episode).
No engine run, no gate, no agent edited, **no submission mechanism called**.
Full table: `results/p33_crop_weighting/p33_crop_weighting.txt`.

This answers the question I handed to OpenCode at 18:14 UTC — *is the leaders' wide-cliff crop weighting a
route-generation property or a per-episode reaction?* — with a variance decomposition, and it kills the
last non-zero-sum lever `p32` had left standing.

## Half 1 — ICC of each crop's tile-day share (route trait vs reaction)

| crop | cliff to `$1` | **ICC** | within-team sd | reading |
|---|---:|---:|---:|---|
| **CARROT** | 842 | **0.007** | 0.067 | **not a trait at all** — all within-team noise |
| STRAWBERRY | 62 | 0.130 | 0.090 | reactive |
| WHEAT | log | 0.347 | 0.069 | reactive |
| TOMATO | 529 | **0.562** | 0.052 | partly a trait |
| **MELON** | 158 | **0.701** | 0.013 | **route-fixed** |

**No team has a carrot program.** Carrot share is 0.7% between-team variance — i.e. teams do not hold a
stable carrot weighting; it is whatever the tiles happened to allow. Melon is the opposite (ICC 0.70),
which is consistent with p30's other finding: melon is single-burst, and both its harvest timing and its
plot share are route properties, so it is the least reachable crop, not the most.

## Half 2 — plot-level money, at matched volume (n=170, R²=0.351)

`money ~ 1 + share(CARROT, TOMATO, MELON, STRAWBERRY) + log(tile-days) + n_animals`, WHEAT absorbed:

| term | coefficient (coins per unit of share, i.e. shifting wheat plot-days into this crop) | se | **t** |
|---|---:|---:|---:|
| **CARROT** | **−106,751** | 22,489 | **−4.75** |
| **STRAWBERRY** | **+65,492** | 15,976 | **+4.10** |
| MELON | +47,072 | 69,329 | 0.68 |
| **TOMATO** | +23,449 | 19,676 | **1.19** |
| log tile-days | +23,422 | 15,664 | 1.50 |
| n_animals | −363 | 315 | −1.15 |

Associational, not causal (opponent composition confounds team-level comparisons) — but the signs are
strong and the sample is the whole field panel, not a 3-seed probe.

## The resolution: price resilience is not plot economics

p27 measured that carrot's realised **price** is the only one that *rises* under contest (42.0 → 55.2).
This measures **plot-level revenue**, and it says moving wheat plot-days into carrot **loses ~107k coins
per unit of share (t=−4.75)**. Both are correct and they are not in conflict: carrot's base is 35 and its
cycle is 2 days, so a resilient *price* on a cheap *asset* is still a bad *program*. **The lane p27
recommended is closed at the plot level**, and the caveat I attached to it then (two `unlocked_shops`
regimes, so directional only) turns out to have been understating it — it points the wrong way.

**TOMATO is also closed by this test.** 11/13 leaders plant it, we ship 0 (p27, `behaviors_p6.csv`), and
its share is partly a team trait (ICC 0.56) — but at matched volume its coefficient is **+23,449 ± 19,676,
t=1.19: indistinguishable from zero.** Combined with the natural experiment that already cut the per-plot
yield from my assumed 56 to ~8 units/plot/season (prize ~+3%), the tomato lane now has **two independent
measurements saying it is not where the money is**. Do not open it a third time.

**STRAWBERRY is where the plot money is (+65,492, t=+4.10) — and we are already there.** p27's own note
records our spine running the *highest* strawberry share in the cohort (532 tile-days). Our defect is not
allocation, it is that the pool we are in has a 62-unit cliff, and p28c priced the reachable correction on
strawberry at **+28 coins/seat**.

## Net effect on the objective's axis map

| axis | status after this cycle |
|---|---|
| sell timing / rate / hour / mod23 / order size / commit order | closed (p17/p19/p28/p28b/p28c) |
| item mix as the *explanation* of the gap | 6.5%, closed (p17) |
| opponent mix | closed (p25) |
| lead-time (the one survivor) | real, **positional and zero-sum**, +1,619/seat collectable (p28c/p30/p32) |
| **which pool / crop weighting** | **now closed too** — carrot anti-correlates (t=−4.75), tomato null (t=1.19), melon unreachable (ICC 0.70, headroom +0) |

Everything that is measurable *inside the market and crop-allocation space* now has a number, and none of
them yields a constructible large lever. The only axis left with a price tag above ~2k is **production at
the herd/route level** (E104: overlay −65,875; all 41 routes animal-maxed; COW XOR SHEEP), which is the
abstraction §20 told us to question and which no wrapper in this architecture can reach.

Files: `tools/p33_crop_weighting.py`, `results/p33_crop_weighting/p33_crop_weighting.txt`, this file.
