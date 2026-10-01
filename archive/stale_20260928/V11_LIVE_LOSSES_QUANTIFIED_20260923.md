# Live loss anatomy of Apex V11 — 2026-09-23

Deployed champion `agents/pub_v57_apex_v11_dump.py` (= `submission.py`), own live episodes pulled into
`results/V11_live_eps/` (episode ids 112161376-112206933, UTC 2026-09-22 20:57 → 23:25). Artifacts:
`_episodetable.txt`, `_anatomy.json`, `_anatomy_render.txt`, `_flows.txt`, `_almond_mechanics.txt`,
`_deep_almond.txt`, four 32 MB replay JSONs.

## 1. Win record

**37W / 4L** over 41 completed games (one episode had no reward recorded). Best opponent beaten: 133,281.
The four defeats, with the loss sized against the per-game money (~100k):

| episode | opponent | ours | opp | delta | mirror % |
|---|---|---|---|---|---|
| 112184040 | Utkarsh #2 | 115,450 | 116,075 | −625 | 91.4% |
| 112201477 | Andrey Akifev | 107,999 | 108,058 | −59 | 89.4% |
| 112170825 | Andrey Akifev | 74,291 | 74,518 | −227 | 80.6% |
| 112204253 | アルモンド | 71,504 | 73,174 | −1,670 | structural (below) |

## 2. Three of four losses are settlement noise, not strategy

`mirror_identical_steps` from the anatomy tool is 658/720, 644/720 and 580/720. Side-by-side counters show
no axis we can act on: `fertilize_ops` 118 vs 121, `fert_bought_units` 90 vs 92, `collect_fertilizer_ops`
376 vs 377, `harvest` 492 vs 493 — and in two of them **we sold more fertilizer than the winner** (315 vs
291, 215 vs 190). Land timing was byte-equal: `BUY_LAND` steps `[151, 266]` for both seats, 3rd quad
unlocked at step 266 for both. The only other visible difference is herd fill on the final day
(Andrey: SHEEP 11 and no empty pasture; ours: SHEEP 9 with 2 `EMPTY_PASTURE`), worth at most a few hundred
coins on a 108k board.

**Conclusion:** those three are the same class as the f90 T3 coin-flips — a 0.05-0.6% settlement race
between near-identical spines. No overlay fixes a coin flip, which is why fifteen graft candidates all
returned parity.

## 3. The one structural loss prices out exactly

vs アルモンド (`_deep_almond.txt`, mirror only 27.4% — the one genuinely different opponent in the cohort),
same `BUY_LAND` [151, 266] and same quad unlock:

| Quantity | ours | opponent |
|---|---|---|
| `FERTILIZE` ops | **106** | **148** |
| FERTILIZE step distribution | hour 20:46, 15:29, 25:24, 10:7 | hour 15:53, 20:52, 25:23, 10:20 |
| PLANT census | WHEAT 148 / STRB 33 / CARROT 46 / MELON 12 | WHEAT 129 / STRB 27 / CARROT **72** / MELON **18** |
| Hires | 265 | 276 (parity) |
| Water ops | 1,100 | 1,077 |
| Residual shed at step 719 | empty | empty |
| Town auto-sale income | 43.5k | **36.1k** (they give it up) |
| Market inflow | 42.4k | **54.5k** |

Their extra fertilizer is **bought, not collected**: supply-side `BUY_PRODUCT FERTILIZER` into the day-13
price trough — 8 units at step 290, 3 units at step 315. Their carrot line is a drip of 1-2 plants/day from
day 8. The money path: we lead by +3,102 through day 19, then bleed **−$3,709 across days 19-27 (steps
432-671)**, with the crossover at steps 576-600.

Correction to a first reading of the same replay: their six `SELL TOMATO 1000` orders at steps 713-718 are
**phantom sentinels** — they never plant or hold tomato, so a naive tape-sum books them as +38k of revenue
that does not exist. Disregarded here and in the forensics file.

## 4. Ranked gap, from the full forensics pass

`V11_LIVE_LOSS_FORENSICS_20260923.md` ranks the mechanisms by measured money:

1. **Sell routing town→market** — net **+$4.7k** (they trade 7.4k of town auto-sale for 12.1k of market
   inflow at better price percentiles). Tape-internal: the sell decision lives in the route tape, so an
   append-only overlay is capped at the ±0.35% band measured in `TAPES_ARE_THE_STRATEGY_20260923.md`.
   This is the *route re-fit* axis (V28), not a layer.
2. **Fertilizer supply side** — **+42 applications ≈ +$3.7k** of production window in the loss, and
   overlay-reachable with a concrete recipe: market-order-only graft at steps 280-340, fire when
   `prices["FERTILIZER"] <= 25`, emit `["BUY_PRODUCT", "FERTILIZER", n<=8]`, at most 2 orders/turn, and
   check the shed ceiling through `observation["private"]["shed"]`. Caveat stated by the analysis: the
   *demand* side (which tile gets the unit) stays route-internal, so expect partial realisation — that is
   exactly V13's `carried==0` failure mode approached from the supply end.
3. **Crop mix** (carrot/melon drip) — planner-internal on this chassis.
4. Labor, land timing, water, dump sizing — measured **$0** gap in this cohort.

The counter-intuitive detail worth keeping: we **sell more fertilizer than the winners do** in three of the
four losses (315 vs 291, 215 vs 190). Fertilizer is largely a `collect_fertilizer_ops` byproduct
(376/episode), and the spine's ROI gate at `:2438-2441` evaluates an application against the unit's *sale
price*, so it under-applies and over-sells.

The champion's remaining live gap is **fertilizer applied per game and the tomato/crop stream it feeds**,
both quantified at roughly $40 per unit against a 100k board. That is the axis `V29_FERT_SUPPLY_CHAIN` and
`V27` (crop-mix substitution) are built to attack, and it is ~25× larger than the overlay band measured in
`TAPES_ARE_THE_STRATEGY_20260923.md`. Do not spend more cycles on sell timing, land timing, hires or shed
guards — this table says they are mirror noise.

Note the counter-intuitive one: we **sell more fertilizer than the winners do** in three of four losses.
Fertilizer is a byproduct of `collect_fertilizer_ops` (376/episode), and our ROI gate compares an
application against the *sale price* of a unit, so it under-applies and over-sells. That gate is spine
`:2438-2441`.
