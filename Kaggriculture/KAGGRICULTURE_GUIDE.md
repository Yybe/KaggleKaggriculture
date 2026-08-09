# Kaggriculture — Complete Competition Guide

> Generated from the official starter notebook (`kaggriculture-getting-started.ipynb`)
> **plus** the actual competition environment source code
> (`kaggle_environments/envs/kaggriculture/kaggriculture.py`, v1.32.5, 1072 lines).
> All constants below are **ground truth from the source**, not estimates.

---

## 1. Competition Overview

| Item | Value |
|---|---|
| Game | Two-player competitive farming simulation (agent vs agent) |
| Host | Kaggle (Google) |
| Season | Fixed 30 days × 24 turns/day = **720 turns** |
| Prize pool | $50,000 total — top 10 get $5,000 each |
| Entry deadline | **September 23, 2026** |
| Scoring / Win condition | **Highest final bank balance** (unsold shed inventory does **not** count; ties possible) |
| Ranking | Skill-rating based, from head-to-head ladder games |
| Submission | `main.py`, `tar.gz`, or `zip` containing `main.py`; or a notebook producing `submission.py` / `submission.tar.gz` |
| Act timeout | 1 second per turn (keep inference fast) |

This is a pure **agent / simulation** competition — not tabular ML. Success = strong
rule-based logic + market timing + action efficiency, then optionally search/RL on top.

---

## 2. Setup & Starting State

- Each player starts with **$3,000** on a **10×10** board (100 tiles).
- The board is split into four **5×5 quadrants**: `NW`, `NE`, `SW`, `SE`.
  - `NW` is unlocked at start. The rest are `"LOCKED"` strings on the tile grid.
- Main farmer spawns on the first free **shed-access tile** in NWSE preference.
- Starting seeds: **none**. Starting inventory: **none**.
- **Shed**: central storage, **capacity 100 non-seed items**. Seeds never touch the shed.
  - Overflow is silently **discarded at end of day**.
- Opponent's farm is **fully visible** (money, tiles, farmer position, hands, unlocked
  quadrants). Opponent's `private` (shed / seeds / inventories) is **hidden**.
- **Market and Town are shared** between both players.

### Land Expansion
```python
LAND_ORDER = ["NE", "SW", "SE"]
LAND_PRICES = [1000, 2000, 4000]
```
Buying unlocks that quadrant's tiles (`"LOCKED"` → `None`). There is exactly one `BUY_LAND`
cost tier per quadrant, in that fixed order.

### Farm Hands (hired daily)
- Hands are hired via `HIRE` market order. Cost = `_fib(hires_today)` where
  `_fib(0)=1, _fib(1)=1, _fib(2)=2, _fib(3)=3, _fib(4)=5, ...` (Fibonacci).
- **Hire costs reset every day** (`hires_today` resets at end of day).
- Hands spawn on the least-occupied free shed-access tile and **disappear at end of day**.
- Each hand gets its own inventory (indexed 1..n in `private.inventories`).

---

## 3. Crops (Exact Constants)

```python
CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}
```

| Crop | Seed $ | First yield (day) | Max yield (day) | Max units | Type | Notes |
|---|---|---|---|---|---|---|
| WHEAT | 10 | 2 | 4 | 6 | one-time | Also animal feed |
| CARROT | 20 | 2 | 3 | 4 | one-time | Fastest cash loop |
| TOMATO | 50 | 8 | 8 | 4 | ongoing | Yields every 1 day, 4 total |
| STRAWBERRY | 100 | 10 | 10 | 4 | ongoing | Yields every 2 days, 4 total |
| MELON | 80 | 10 | 12 | 6 | one-time | High value, slow, crashes hard on glut |

### Plant lifecycle mechanics (from source)
- `_new_plant`: `planted_day=day`, `watered_today=False`, `consecutive_unwatered=1`
  (**planting day counts as unwatered**), `yield_units = 0 if ongoing else 1`,
  `max_lifespan_step = (day + max_yield_day + 1) * turns_per_day` for one-time crops.
- **Watering**: every day or the plant accumulates `consecutive_unwatered`. At end of
  day, if `consecutive_unwatered >= 2` → tile becomes a **WEED**.
- **One-time crops** get a watering bonus only in the second half of growth:
  ```
  window_start = (max_yield_day + 1) // 2
  if window_start <= age_days <= max_yield_day:   # watered on that day
      yield_units += 2 if fertilized else 1
  ```
  So you get **2 units** per bonus-window watering if the plant is **fertilized**, else 1.
  WHEAT: window days 2–4. CARROT: day 2. MELON: days 6–12.
- **Ongoing crops**: base yield **+1** on each production day, but **+2** if the plant was
  **watered AND fertilized** that day. Production days: `days_since_first % interval == 0`,
  capped at `max_yield` total productions.
- **Fertilizer**: `FERTILIZE` sets `fertilized_until_day = day + 2` (active for the rest of
  day, day+1, day+2 = 3 days inclusive). Consumes 1 FERTILIZER from the farmer's inventory.
- **Decay**: after `max_lifespan_step` (one-time crops), yield decays −1 every 2 steps
  (`(step - mls) % 2 == 0`). At 0 → **WEED**. Ongoing crops get `max_lifespan_step` set only
  after their final production.

---

## 4. Animals (Exact Constants)

```python
ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
```

| Animal | Cost $ | Structure | First yield (day) | Interval | Max held | Product |
|---|---|---|---|---|---|---|
| GOOSE | 300 | COOP | 4 | every 1 day | 4 | EGG |
| COW | 400 | PASTURE | 8 | every 2 days | 6 | MILK |
| SHEEP | 500 | PASTURE | 6 | every 3 days | 6 | WOOL |

### Animal lifecycle mechanics (from source)
- Buy animal via `BUY_ANIMAL` → lands in **shed** (counts against the 100 cap!). To deploy:
  build the structure (`BUILD_COOP` / `BUILD_PASTURE` on empty tile), `PICKUP` the animal
  from the shed (must stand on a shed-access tile), walk to the structure, `PLACE`.
- **Feeding**: must be fed **1 WHEAT per day** (from the unit's inventory). At end of day,
  unfed → `consecutive_unfed += 1`; **`>= 2` → animal escapes forever** (structure remains,
  empty).
- **Production**: on production days (`days_since_first % interval == 0`), `yield_units +=
  1 + pending_care_bonus`, capped at `max_held`. Bonus only consumed **if fed that day**.
- **CARE** action: sets `cared_today=True`. If an animal is **both fed AND cared** on a
  production day, `pending_care_bonus += 1` → **+1 extra product on next production day**.
- **Fertilizer**: every day (fed or not, as long as it hasn't escaped), `fertilizer_available
  = True`. `COLLECT_FERTILIZER` grabs 1 FERTILIZER into inventory.
- `HARVEST` on an animal tile moves `yield_units` of its product into the unit's inventory.
- `DIG` does **NOT** remove a placed animal (silent no-op). It removes plants, weeds, and
  empty structures.

---

## 5. Observation Format (per turn)

```python
obs = {
  "player": 0 | 1,                    # your id
  "day": 0..29, "hour": 0..23,        # day + turn-within-day (0-indexed)
  "farms": [                          # BOTH players' public state
    {
      "money": 3000.0,
      "tiles": [[None | "LOCKED" | dict, ...] x10, ...],   # tiles[y][x]
      "farmer": [x, y],
      "hands": [[x, y], ...],          # today's hands
      "unlocked_quadrants": ["NW"],
      "hires_today": 0,                # drives next HIRE price
    }, {...opponent...}
  ],
  "market": {                          # SHARED
    "inventory": {item: count, ...},   # 9 products
    "prices":    {item: $, ...},       # current prices
  },
  "town": {"unlocked_shops": [shop_name, ...]},   # SHARED
  "private": {                         # YOURS ONLY (hidden)
    "shed":        {item: count, ..., "GOOSE": n, "COW": n, "SHEEP": n},
    "seeds":       {crop: count, ...},
    "inventories": [ {item: n, ...},   # [0]=farmer, [1..]=hands (today)
                     {item: n, ...}, ...],
  },
}
```

### Tile dict shapes
- **Empty**: `None` (owned, free).
- **Locked**: `"LOCKED"` (unowned quadrant).
- **Plant**: `{kind:"PLANT", crop, planted_day, watered_today, consecutive_unwatered,
  yield_units, max_lifespan_step, fertilized_until_day}`.
- **Weed**: `{kind:"WEED"}` — must be `DIG`ged.
- **Empty structure**: `{kind:"COOP"|"PASTURE"}`.
- **Occupied structure**: adds `{animal, placed_day, yield_units, fed_today,
  consecutive_unfed, cared_today, fertilizer_available, pending_care_bonus}`.

---

## 6. Actions (returned dict)

```python
return {
  "farmer": ["PLANT", "WHEAT"],     # one action list
  "hands":  [["WATER"], ["MOVE..."]],   # one action per hired hand, same order as obs
  "market": [["SELL", "MELON", 3], ["BUY_SEED", "WHEAT", 2]],   # max 10 orders
}
```

### Unit actions (farmer + hands)
| Action | Args | Effect |
|---|---|---|
| `NORTH/SOUTH/EAST/WEST` | — | Move 1 tile (movement allowed onto LOCKED; ops on LOCKED are no-ops) |
| `PASS` | — | Do nothing |
| `PLANT` | `crop` | Plant seed on empty owned tile; consumes seed; planting day = unwatered |
| `WATER` | — | Water plant on current tile (once/day) |
| `HARVEST` | — | Collect `yield_units` of plant/animal product into inventory; clears tile for one-time crops |
| `FERTILIZE` | — | Consume 1 FERTILIZER; plant fertilized through day+2 |
| `DIG` | — | Remove plant/weed/empty structure on current tile (NOT placed animals) |
| `BUILD_COOP` / `BUILD_PASTURE` | — | Build empty structure on empty tile |
| `FEED` | — | Feed animal 1 WHEAT from inventory |
| `CARE` | — | Care for animal (bonus if also fed on production day) |
| `COLLECT_FERTILIZER` | — | Take 1 FERTILIZER from animal tile |
| `PICKUP` | `item` [,n] | From shed (must stand on shed-access tile) → inventory |
| `PLACE` | `item` [,n] | Place animal on matching empty structure OR drop shed item (shed-adjacent) |
| `DROP` | — | Drop ALL carried inventory into shed (shed-adjacent, capacity 100) |

**Important semantics:**
- All invalid/illegal actions are **silent no-ops**.
- Shed ops only work from the 4 **shed-access tiles**: `(4,4) (5,4) (4,5) (5,5)` on a 10×10
  board (inner 2×2 around the center).
- Seeds live only in `private.seeds`; they never enter inventory or shed.
- If multiple units try to `PLANT` the same crop this turn and total demand > seeds on hand,
  **all** PLANT requests for that crop are dropped that turn.
- `SELL` requires the item in the **shed** (not farmer inventory).
- Sold-at-$1 items do **not** increase market supply (anti-glut relief valve).

### Market orders (max 10/turn, processed simultaneously with opponent)
| Order | Args | Price |
|---|---|---|
| `BUY_SEED` | `crop`, n | Fixed (CROPS[seed]) |
| `BUY_ANIMAL` | `animal`, n | Fixed (ANIMALS[cost]) — goes to shed |
| `BUY_PRODUCT` | `WHEAT`/`FERTILIZER`, n | Market price — goes to shed |
| `SELL` | `product`, n | Market price per unit, from shed |
| `HIRE` | — | Fibonacci cost, one hand |
| `BUY_LAND` | — | Next tier (1000/2000/4000) |

**Market execution model (critical):** orders are executed **per-unit in lockstep**. At each
unit step both players get the *same pre-commit price quote*, then both commit. This means
a simultaneous buy/sell of the same item nets zero price movement; but a big SELL order from
you drops the price mid-order, so **splitting large sells into smaller orders over turns**
(not within one order) is what actually avoids self-inflicted price crashes. Within a single
`SELL n` order, later units quote at the *post-commit* inventory → you eat your own price drop.

---

## 7. Market Economics (Exact Pricing Model)

```python
# price(inv) = base + sign * amp * f(|inv - I0|)
#   sign = +1 below I0 (scarcity premium), -1 above I0 (glut discount)
#   amp  = target * base / f(T)   (selling T units moves price by target*base)
#   f    in {linear, sq, sqrt, log, log10}; log uses ln(1+x)
MARKET_I0 = 10000      # baseline inventory
PRICE_FLOOR = 1        # absolute floor
```

| Product | Base $ | T | Below I0 (scarcity) | Above I0 (glut) |
|---|---|---|---|---|
| WHEAT | 25 | 400 | sqrt, +80% @ T | log, −20% @ T |
| CARROT | 35 | 450 | log, +20% | sqrt, −70% |
| TOMATO | 60 | 200 | linear, +40% | sqrt, −60% |
| STRAWBERRY | 120 | 100 | sqrt, +70% | **linear, −160%** |
| MELON | 250 | 300 | log, +20% | **sq, −360%** |
| EGG | 50 | 332 | linear, +40% | log, −20% |
| MILK | 160 | 122 | sqrt, +60% | linear, −160% |
| WOOL | 200 | 105 | log, +20% | **sq, −320%** |
| FERTILIZER | 100 | 200 | linear, +40% | linear, −40% |

**Read this table carefully:**
- **MELON, WOOL, STRAWBERRY, MILK crash brutally on glut** (sq/linear with large targets).
  One oversupplied player can nuke these to $1. Never dump these all at once.
- **WHEAT and EGG are glut-resilient** (log, −20%) — you can dump them more freely.
- **Scarcity gives big premiums** on STRAWBERRY (+70%), MILK (+60%), EGG/TOMATO (+40%),
  FERTILIZER (+40%). Selling into scarcity (inventory < 10,000) is where the money is.

### Town demand (price support)
```python
SHOPS = {
  "BAKERY":         ["EGG", "WHEAT"],
  "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
  "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
  "YARN_STORE":     ["WOOL"],
  "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
  "PET_CAFE":       ["CARROT"],
  "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
  "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
```
- **Shops unlock every 3 days** (random order), starting day 3. Each shop drains 2 units of
  its products (1-product shops drain 2× = multiplier 2) **every 4 steps**.
- **Town center drains every non-fertilizer product every 12 steps**, with demand multiplier
  by day: days ≥20 → **4×**, days ≥10 → 2×, else 1×.
- Net effect: prices are supported (and late-season demand rises 4×), so holding inventory
  into days 20+ is usually smart — but risk gluts from your own (or opponent's) selling.

---

## 8. The Starter Notebook (melon_maxxer) — Analysis

The notebook's agent, `melon_maxxer(obs)`:

1. Buys 1 melon seed whenever it has 0 and money ≥ 80.
2. Walks to nearest target: harvest (priority 0) > water (1) > plant (2), Manhattan-greedy.
3. Sells melons from shed only if `MELON price >= 200` (threshold).
4. Never hires, never buys land, never fertilizes, only grows melons.

Notebook result: **reward=6099** vs random agent (which scores 0).

### Documented flaws (notebook's own "What's wrong with this agent")
- Never hires farm hands or buys land → 1 farmer stuck on 25 tiles.
- Only grows melons → no diversification when other crops pay better.
- Never fertilizes → leaves the watering-bonus yield on the table.
- **Dumps entire shed in one SELL order** → crashes melon price below threshold mid-sale.

### Undocumented flaws (from source-code analysis)
- Sells `shed["MELON"]` in one order — the source shows per-unit lockstep pricing, so a big
  order eats its own price drop (wheat `sq` crash). Should split sells across turns.
- No wheat → can never start animals; no FERTILIZER source.
- Greedy movement can step onto LOCKED tiles and waste turns.
- No daily prioritization of critical watering (a melon about to die is skipped if a harvest
  is farther away — actually priority 0 harvest wins over water).
- Melon matures at day 10–12 and one-time crop lifespan decays at day 13; if planted after
  day ~13 it can never mature — no late-game planting cutoff.

---

## 9. Built-in Opponents (source of truth)

```python
agents = {"pass": pass_agent, "random": random_agent, "starter": starter_agent}
```
- `pass`: `{"farmer":["PASS"],"hands":[],"market":[]}` — always 0.
- `random`: random moves/plant/water/harvest, buys a random seed 10% of turns, plants 30% of
  turns with whatever seeds it has. Never sells. Scores ~0.
- `starter`: carrot loop — plant carrot on current tile, water, harvest at max_yield_day,
  sell all carrots, buy 1 carrot seed. **Doesn't move.** Very weak.

---

## 10. Agent Development Roadmap

### Phase 0 — Local harness (DONE in this repo)
- `harness.py`: multiprocessing parallel game runner using all **28 CPU cores**.
- Benchmark: single-game time with `debug=False`, then N games in parallel.
- Opponents: `"random"`, `"starter"`, `"pass"`, self-play, melon_maxxer.

### Phase 1 — Strong rule-based baseline (`agent_baseline.py`)
Priority loop every turn (farmer + hands share a task queue):
1. **Market first**: sell shed inventory with good prices (split orders, respect glut risk),
   buy seeds/animals/fertilizer/wheat per plan, hire hands when action bottlenecked, buy land
   when it pays off.
2. **Task prioritization**:
   - Critical: FEED animals (about to escape), WATER plants about to become weeds.
   - High: HARVEST anything ready (plants + animal products).
   - Medium: WATER in bonus windows (fertilized first), FERTILIZE plants before bonus window.
   - Collect fertilizer from animals daily.
   - Plant high-ROI crops on empty tiles (early: wheat/carrot loops; then melon; animals).
   - DIG weeds / clear empty structures.
   - Move (Manhattan greedy / BFS) to best target.
3. **Economy**:
   - Early (d0–8): wheat/carrot fast cash, expand land ASAP, hire 1–3 hands, start geese.
   - Mid (d8–20): ongoing crops + melons + animals, fertilizer loop, monitor prices.
   - Late (d20–30): never let plants/animals die; harvest everything; sell into town 4× demand;
     convert all assets to cash before final turn; stop planting crops that can't mature.

### Phase 2 — Climb the ladder
- Download public episodes/replays (e.g. `georgymamarin/kaggriculture-episodes`).
- Plot bank curves, crop mix, land/hire timing, sell timing vs top bots.
- Tune thresholds via grid search on the parallel harness (hundreds/thousands of games).

### Phase 3 — Top-5 techniques
- Beam search / MCTS over macro-plans (crop allocation, expansion, animal count).
- Imitation learning on strong episodes; RL self-play (reward = final bank difference).
- Market modeling: predict price trajectory from your+opponent production + town demand;
  optimize sell schedule.
- Portfolio of specialized strategies (expansion / animal-heavy / crop-heavy / melon-late),
  selected by game state and opponent style.

---

## 11. Speed Strategy (28-core CPU, no GPU detected)

- **Official env**: one full 720-turn game ≈ 0.5–5 s (agent-dependent). With 28 cores and
  `multiprocessing.Pool`, throughput is ~10–30× single-core → **hundreds–thousands of games
  per minute**.
- Speed levers:
  - `debug=False`, never `render()` (huge).
  - Keep the agent pure-Python and cheap (<1 ms/turn).
  - Reuse one `env` per worker where possible (test: `env.run()` resets state).
  - Use `episodeSteps` 200–300 for fast smoke tests, full 720 for finals.
  - `concurrent.futures.ProcessPoolExecutor` on Windows spawn; agents must be
    top-level/picklable functions.
- **GPU**: `nvidia-smi` not found on this machine → no CUDA GPU here. (The environment
  reports CPU-only.) If a GPU is available on the Kaggle box, it's only useful for RL /
  imitation-learning training, never for the 1-second act step. All ladder validation is
  CPU.
- Future massive scale (100k+ games): build a **lightweight custom simulator** reimplementing
  the rules above in NumPy/Numba (~10–50 ms/game, 20–200× faster than official env), which
  enables grid-search, tournaments, and RL data collection.

---

## 12. Submission Notes

- Submit `main.py` (or `tar.gz`/`zip` containing it), or a notebook producing
  `submission.py` / `submission.tar.gz`.
- `main.py` must define an agent callable — the notebook used
  `from submission import melon_maxxer` style, but the competition standard is a file with
  `agent(obs)` or a defined function referenced at submit time (check the competition's
  agents.py dataset file for the exact entry point).
- Act timeout: **1 second**. Keep it deterministic/seeded during development.
- Never crash: wrap the whole agent in try/except returning a PASS dict.

---

## 13. Key Takeaways (TL;DR)

1. **Turns are the scarce resource** — action efficiency beats raw production.
2. **Early cash compounds** — wheat/carrot loops fund land, hands, and animals.
3. **Geese are the best animal** (egg every day, resilient price); wool/melon crash hardest.
4. **Never let plants/animals die** — that's pure sunk loss.
5. **Sell smart**: split orders across turns, sell into scarcity, hold into day-20+ town demand.
6. **Fertilizer loop**: animals → fertilizer → double watering bonuses → more yield.
7. **Opponent awareness**: they're visible; watch for market flooding and pivot.
8. **Benchmark everything** on the 28-core harness before submitting.
