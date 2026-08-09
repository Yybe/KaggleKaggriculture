# Kaggriculture — Full Project Report

**Date:** 2026-08-07
**Environment:** Windows, Python 3.12.9, 28 CPU cores, no NVIDIA GPU (CPU-only)
**Package:** `kaggle-environments 1.32.5`

---

## 1. Objective

Beat the starter Kaggriculture agents (the notebook `melon_maxxer` and the built-in
`starter`) by building a faster, smarter farming agent, and prove it with a fast
parallel benchmark harness on this machine's 26 worker cores.

**Final result: 100% win rate against every opponent, ~6x the bank of melon_maxxer.**

---

## 2. What was built

| File | Purpose |
|---|---|
| `agents_lib.py` | The agents: `baseline()` (winner) + `melon_maxxer()` (reference) |
| `harness.py` | 26-worker parallel game runner + statistics |
| `KAGGRICULTURE_GUIDE.md` | Competition guide: exact constants, obs format, action semantics, market economics |
| `_trace.py` | Day-by-day trace of both players' farms (debugging tool) |
| `_debug_game.py` | Final-state board dump (debugging tool) |
| `notebook_extract.txt` | Extracted contents of the starter notebook |

---

## 3. The journey — step by step

### Step 1: Read and decode the starter notebook
Extracted the Kaggle starter notebook to `notebook_extract.txt`. The notebook's
agent (`melon_maxxer`) is simple: buy a MELON seed when you have none, plant it on
any empty tile, water whatever you're standing on, harvest at `max_yield_day`,
sell all melons when price >= 200.

### Step 2: Verify ground truth from environment source
Rather than trusting the notebook's assumptions, I read the actual environment
source at:

```
C:\Users\chira\AppData\Local\Programs\Python\Python312\Lib\site-packages\kaggle_environments\envs\kaggriculture\kaggriculture.py
```

This was the single most valuable decision of the project. Verified:

- **Crops** (exact): WHEAT (seed 10, first_yield 2, max_yield_day 4, max_yield 6,
  one-time), CARROT (20/2/3/4), TOMATO (50/8/8/4, ongoing), STRAWBERRY
  (100/10/10/4, ongoing), MELON (80/10/12/6, one-time)
- **Animals**: GOOSE cost **300** (not 900 — the notebook's guess), COW **400**,
  SHEEP **500**; all produce 1 fertilizer/day when fed
- **Land**: `LAND_ORDER = ["NE", "SW", "SE"]`, prices `[1000, 2000, 4000]`
- **Hands**: cost = `fib(n)` per day's hire — 1, 1, 2, 3, 5, 8... nearly free
- **Starting money: 3000**
- **Market**: every product starts with inventory = I0 = 10,000 → price = base.
  Price = `base ± amp * f(|inv − I0|)` with per-product crash curves. MELON uses a
  **square** above-I0 curve at −360% (brutal crash on glut). WHEAT/EGG use log
  (−20%, resistant)
- **Town center** drains every product except FERTILIZER every 12 steps, with
  day multipliers 4x (day≥20), 2x (day≥10), 1x
- **Shops** (unlock every 3 days) drain their products every 4 steps. **MELON is
  in NO shop** — only the town center consumes it
- **Yield mechanics**: one-time crops start at 1 unit and only grow via watering
  inside the bonus window `(max_yield_day+1)//2 ≤ age ≤ max_yield_day`
  (+1 per water, +2 if fertilized, capped at max_yield). Harvesting at
  `first_yield_day` forfeits yield vs `max_yield_day`
- **Decay**: one-time crops start losing yield after `(planted + max_yield_day + 1) * 24`
  steps, then die → WEED
- **Weeds**: 2 consecutive unwatered days → WEED
- **Animals escape** after 2 unfed days

### Step 3: Built the harness
`harness.py` uses `ProcessPoolExecutor` with `WORKERS = os.cpu_count() - 2 = 26`.
Agents are top-level pure functions (picklable for Windows multiprocessing).
CLI: `python harness.py --a agents_lib:baseline --b random --n 64`.
Achieves **~3–3.7 games/sec** (128 games in ~35s).

### Step 4: Built `baseline()` — a priority-driven agent

Task priorities (lower = more urgent):

```
P_FEED = 0        animal may escape tomorrow
P_WATER_CRIT = 1  plant dies at end of day if not watered
P_HARVEST = 2     plant/animal ready
P_FERTILIZE = 3   plant in bonus window, not fertilized
P_COLLECT = 4     animal fertilizer available
P_WATER_BONUS = 5 plant in watering-bonus window, unwatered
P_PLACE = 6       animal in shed + empty structure
P_PLANT = 7       empty tile + seed
P_DIG = 8         weed
P_BUILD = 9       empty tile + planned structure
P_WATER = 10      routine watering
```

Every farmer + hand picks the highest-priority unclaimed task nearest to them.
Market orders run separately and are capped at 10 per step.

### Step 5: Debugging — the score history

Single-game scores vs random tell the whole story:

| Iteration | Score vs random | What changed |
|---|---|---|
| v1 | 813 | First working agent |
| v2 | 1,897 | Fixed harvest of seedlings (yield_units=1 on fresh plant) |
| v3 | 4,581 | Fixed PICKUP being shed-adjacent only; plant budget to avoid over-planting death spiral |
| v4 | ~5,000 | Chunked crashy sells, wheat feed reserve |
| v5 (start) | 4,893 vs melon_maxxer | Baseline was losing to melon_maxxer (6,092) |

**The big breakthrough — v6: kill the animal spiral.**

Tracing showed the farm dying: by day 6 the agent had bought geese (1,200 gold),
and from day 13 onward the farmer spent EVERY turn feeding 4–5 animals and
collecting fertilizer — **0 plants for 16 straight days**. Animals cost money AND
farmer time; melon_maxxer proved they were unnecessary.

Simultaneously fixed the two other silent leaks:

1. **Sell gate 250 → 200.** MELON inventory starts at I0 (price = base = 250) and
   only the town drains it. Any sale crashes price below 250 (−360% sq curve), so
   a 250 gate meant holding melons forever while melon_maxxer liquidated at 200+.
2. **Harvest at max_yield_day (12), not first_yield_day (10).** One-time crops
   only build yield in the bonus window; early harvest forfeited ~17% of melons.

Result: **30,149 avg bank vs melon_maxxer's 5,659 — a 6x improvement.**

### Step 6: The final strategy (v6)

- Buy melon seeds in bulk (up to 3/step, days 0–18) up to `12 × (1 + hands)`
- Hire 3 hands by day 4 (cost ~4 gold total)
- Plant melons everywhere, water for max yield, harvest at maturity
- Sell melons at ≥200 in chunks of 4 (price management)
- Buy land when money ≥ land_price + 800 and day ≤ 15
- **No animals at all**

---

## 4. Results (final, 64–128 game runs)

| Opponent | Baseline avg | Baseline med | Baseline max | Opponent avg | Win rate | Errors |
|---|---|---|---|---|---|---|
| random | 30,886 | 31,415 | 34,250 | 21 | 100% | 0 |
| starter | 30,886 | 31,415 | 34,250 | 3,502 | 100% | 0 |
| melon_maxxer | 30,149 | 30,611 | 33,414 | 5,659 | 100% | 0 |

Note: melon_maxxer's bank DROPPED from 6,099 (when playing alone) to ~5,660 when
playing us — we flood the shared melon market, crashing the price it relies on.

### Why we win (market economics)

- The town center drains ~140 melons over 30 days; melon_maxxer only ever produces
  ~24. **Production is the bottleneck, not demand.**
- Hands + bulk seeds + land let us produce ~10x more melons.
- Selling at 200+ (not 250) means we never hold inventory waiting for a price
  that only exists before the first sale.
- Because MELON is in no shop, our own flood is the only thing that pushes the
  price down — and in a head-to-head, that flood hurts the opponent first.

---

## 5. Headroom / next steps (untapped)

| Lever | Expected effect |
|---|---|
| Fertilizer (+2 yield/water) | More melons per plant in the same watering budget |
| Sheep → WOOL | A second, separate demand curve (base 200, log-below, −320% sq crash — chunk carefully) |
| Land timing tuning | Currently gated at day ≤ 15, +800 buffer; earlier NE buy may pay more |
| Ongoing crops late-game | TOMATO/STRAWBERRY for day 20+ when melons can't mature |
| Multi-market strategy | Diversify before the melon flood saturates the market |

---

## 6. How to reproduce

```powershell
# Run the baseline vs any opponent
python harness.py --a agents_lib:baseline --b random --n 64
python harness.py --a agents_lib:baseline --b starter --n 64
python harness.py --a agents_lib:baseline --b agents_lib:melon_maxxer --n 64

# Day-by-day trace (baseline vs melon_maxxer)
python _trace.py

# Final board state debug
python _debug_game.py
```

---

## 7. Key lessons

1. **Read the environment source, not the notebook.** The notebook's animal cost
   guesses (900/2200) were wrong (real: 300/400); the yield window, market crash
   curves, shop consumption, and decay rules were all only discoverable in source.
2. **Trace before you tune.** The animal spiral was invisible in aggregate scores
   (avg kept rising) but obvious in a day-by-day trace.
3. **Sell-gate parity matters in shared markets.** A "safe" higher sell threshold
   silently forfeits an entire price band when the market never recovers to it.
4. **Time is the scarcest resource.** Every animal day costs 24 farmer turns that
   could have watered melons. Cheapest actions (hands at 1 gold) dominate expensive
   ones (animals at 300+).
5. **Production beats price-taking.** In a market with a fixed drain, whoever
   produces more captures the band — and in head-to-head, floods the opponent.
