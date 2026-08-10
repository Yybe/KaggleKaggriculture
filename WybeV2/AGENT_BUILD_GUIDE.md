You are building an agent for the Kaggle competition "Kaggriculture" — a 1v1 farming
economy. The scoring engine is kaggle-environments 1.32.6. The engine source is the
GROUND TRUTH and is installed locally. READ THESE FIRST, before writing any code:

- Engine: C:\Users\xxshi\AppData\Local\Programs\Python\Python311\Lib\site-packages\kaggle_environments\envs\kaggriculture\kaggriculture.py
- Spec:   C:\Users\xxshi\AppData\Local\Programs\Python\Python311\Lib\site-packages\kaggle_environments\envs\kaggriculture\README.md
- Config: C:\Users\xxshi\AppData\Local\Programs\Python\Python311\Lib\site-packages\kaggle_environments\envs\kaggriculture\kaggriculture.json

Your deliverable: ONE self-contained Python file, `submission.py`, exporting:

    def agent(obs, config=None) -> dict:
        return {"farmer": [...], "hands": [[...], ...], "market": [[...], ...]}

The engine calls this once per turn for 720 turns (30 days x 24 hours). The winner
has the most money at turn 720. No external libraries. Runtime budget: well under
1 second per call (eval actTimeout = 1s).

===== OBSERVATION FORMAT (exact) =====
Top level: {"player": int, "day": int, "hour": int, "step": int,
            "farms": [farm, farm], "market": {...}, "town": {...}, "private": {...}}

farm (yours is obs["farms"][obs["player"]]):
  "money": float
  "tiles": [[tile, ...], ...]        # 2D grid indexed tiles[y][x]; y is the row!
  "farmer": [x, y]                   # farmer position
  "hands": [[x, y], ...]             # hands hired THIS day (empty each morning until re-hired)
  "unlocked_quadrants": ["NW", ...]  # NW is free; NE=1000, SW=2000, SE=4000
  "hires_today": int                 # drives next HIRE cost

tile value: None (empty, unlocked) | "LOCKED" (quadrant not bought) | dict:
  PLANT:   {"kind":"PLANT","crop":"WHEAT|CARROT|TOMATO|STRAWBERRY|MELON",
            "planted_day":int,"watered_today":bool,"consecutive_unwatered":int,
            "yield_units":int,"max_lifespan_step":int,"fertilized_until_day":int}
  WEED:    {"kind":"WEED"}
  ANIMAL:  {"kind":"COOP|PASTURE","animal":"GOOSE|COW|SHEEP|None","placed_day":int,
            "yield_units":int,"fed_today":bool,"consecutive_unfed":int,
            "cared_today":bool,"fertilizer_available":bool,"pending_care_bonus":int}

private (yours only): {"shed": {item:count}, "seeds": {crop:count},
                       "inventories": [farmer_inv, hand_inv, ...]}   # cap 100 items, seeds separate
market (shared):      {"inventory": {item:int}, "prices": {item:int}}
town (shared):        {"unlocked_shops": ["BAKERY", ...]}  # instances; each consumes every 4 turns

===== ACTION FORMAT (exact) =====
farmer / each hand gets ONE action per turn (list):
  ["PASS"] | ["NORTH"|"SOUTH"|"EAST"|"WEST"]
  ["PLANT", crop] | ["WATER"] | ["HARVEST"] | ["FERTILIZE"]       # crops; tile you stand on
  ["BUILD_COOP"] | ["BUILD_PASTURE"]                              # empty tile you stand on
  ["DIG"]                                                            # weed or empty structure
  ["PICKUP", item, n]   # shed-adjacent ONLY: shed -> your inventory
  ["DROP"]              # shed-adjacent ONLY: inventory -> shed
  ["PLACE", item, n]    # animal onto matching structure you stand on, OR shed-drop if shed-adjacent
  ["FEED"] | ["CARE"] | ["COLLECT_FERTILIZER"]                    # animals on your tile

market: up to 10 orders per turn, processed IN ORDER, one unit at a time:
  ["HIRE"]                        # cost = fib(hires_today): 1,1,2,3,5,8,... per hire per day
  ["BUY_LAND"]                    # NE 1000 -> SW 2000 -> SE 4000
  ["BUY_SEED", crop, n]           # seeds: WHEAT10 CARROT20 TOMATO50 STR100 MELON80
  ["BUY_ANIMAL", animal, n]       # GOOSE300 COW400 SHEEP500 -> lands in shed
  ["BUY_PRODUCT", item, n]        # only WHEAT or FERTILIZER purchasable
  ["SELL", item, n]               # sells FROM THE SHED only; gives money; moves price

===== MECHANICS YOU MUST RESPECT =====
1. Money only increases via SELL orders. Harvest -> inventory -> (end of day auto-drops
   to shed, or DROP at shed) -> SELL next turn. A farm that never sells always loses.
2. Seeds are SHARED by farmer + all hands (private["seeds"]); PLANT consumes 1 seed.
3. WATER every plant every day. A seed planted and not watered the same day counts as
   day-1 missed; 2 consecutive missed days -> tile becomes WEED. Water the day you plant.
4. Hands vanish at end of day. Re-HIRE every morning; 6 hands cost only 20/day (1+1+2+3+5+8).
5. Hands spawn shed-adjacent in NWSE order: (5,4) NE-locked, (4,5) SW-locked, (5,5) SE-locked.
   Any action except movement on a LOCKED tile is a silent no-op. MOVE units onto unlocked
   tiles before PLANT/WATER/etc. LOCKED tiles are passable.
6. Animals: BUY_ANIMAL puts them in the shed. Pipeline = BUILD_PASTURE (cow/sheep) or
   BUILD_COOP (goose) on an empty tile -> stand on it -> PICKUP animal at shed -> MOVE there
   -> PLACE -> FEED daily (consumes wheat from inventory) -> HARVEST product -> COLLECT_FERTILIZER.
   Unfed 2 days -> animal escapes. They are a mid-game strategy, not day 0.
7. Crops: WHEAT seed10/price25, first yield day2, max yield day4, one-time, max 6 (4 unfertilized).
   CARROT seed20/price35, first2, max3, one-time, max4. MELON seed80/price250, first10, max12,
   one-time, max6. TOMATO seed50/price60, first8, then every day x4. STR seed100/price120,
   first10, then every 2 days x4. Ongoing crops decay into weeds after 4 productions.
8. Prices move against you as you sell (shared market, I0=10k, floors at $1). Selling in
   bigger chunks when price is high beats dribbling out. Town center consumes every product
   once per 24 turns; shops every 4 turns. Sell timing matters.
9. At the very end (turns >= 710) sell EVERYTHING in the shed — unsold items count as nothing.
10. Shed capacity is 100 (seeds excluded). Overflow is discarded.

===== BUGS IN THE PREVIOUS ATTEMPT — DO NOT REPEAT =====
- Re-sending the same market orders on consecutive turns (double-spend -> $0 by turn 2).
  Send exactly the orders you want THIS turn. Guard on `step == 0`, never `step <= 1`
  (the engine's first call is step=0, so `step <= 1` fires twice).
- Hiring hands once and expecting them to stay (they reset daily).
- Acting from LOCKED tiles (hands spawn there; move first).
- Buying animals without building structures / placing / feeding / harvesting them.
- Never issuing SELL orders (the game never earns money).
- Assuming tiles are a flat list — they are tiles[y][x], a 2D grid.

===== MINIMUM VIABLE STRATEGY (get a positive score first) =====
Day 0: HIRE 3-4 hands; BUY_SEED WHEAT ~8-10 (melon only after you can water it reliably).
       MOVE everyone to unlocked tiles in the NW quadrant near the shed.
       Plant wheat in a block; water every plant the day it is planted, then daily.
       Harvest wheat at peak (day 4: 4-6 units) into inventory (auto-drops to shed at
       end of day). SELL wheat in bulk while price > 20. Re-hire hands every morning.
       Expand: buy NE land (~day 5-8), plant more wheat/carrot, then melon/STR for mid-game.
       Days 25+: focus on high-value crops; turns 700+: full liquidation, SELL everything.
       Only add animals (sheep first: 500 cost, wool 200 base) once crops fund them.

===== TEST HARNESS (write this before the agent) =====
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
    env.run([agent, lambda obs: {"farmer":["PASS"],"hands":[],"market":[]}])  # vs do-nothing
    print("final:", [s[0].reward, s[1].reward])
Acceptance: vs a PASS-only opponent you must exceed 3000 by day 720 (target: 8000+).
Also test vs "random" and vs yourself twice. Keep output free of debug spam.

If the user supplies Seb/HealthStone replay data or notes, read them and adapt your
openings and sell timing, but only after the basic loop above works.
