"""Kaggriculture agents library.

Pure functions of obs (stateless) so they pickle cleanly for multiprocessing.
All mechanics verified against kaggle_environments v1.32.5 source.
"""
from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS

# ---------------------------------------------------------------------------
# Constants (ground truth from source)
# ---------------------------------------------------------------------------
BASE_PRICE = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
    "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100,
}
# Products that crash hard on glut -> sell in small chunks only
CRASH_RISK = {"MELON": True, "WOOL": True, "STRAWBERRY": True, "MILK": True}
SELL_CHUNK = 4          # max units per SELL order for crashy goods
ANIMAL_PRODUCT = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}

SHED_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}  # 10x10 board shed access

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


# ---------------------------------------------------------------------------
# Melon Maxxer — the starter notebook agent, extracted for comparison
# ---------------------------------------------------------------------------
MELON_SEED_COST = CROPS["MELON"]["seed"]
MELON_MAX_YIELD_DAY = CROPS["MELON"]["max_yield_day"]
SELL_THRESHOLD = 200


def _step_toward(fx, fy, tx, ty):
    if fx > tx:
        return "WEST"
    if fx < tx:
        return "EAST"
    if fy > ty:
        return "NORTH"
    if fy < ty:
        return "SOUTH"
    return None


def _find_target_tile(farm, board_size, have_seed):
    fx, fy = farm["farmer"]
    candidates = []
    for y in range(board_size):
        for x in range(board_size):
            tile = farm["tiles"][y][x]
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile["crop"] == "MELON":
                purpose = None
                if tile["yield_units"] > 0 and tile.get("planted_day") is not None:
                    purpose = "harvest"
                if not tile["watered_today"]:
                    purpose = "water" if purpose is None else purpose
                if purpose:
                    candidates.append((x, y, purpose))
            elif tile is None and have_seed:
                candidates.append((x, y, "plant"))
    if not candidates:
        return None
    priority = {"harvest": 0, "water": 1, "plant": 2}
    candidates.sort(key=lambda c: (priority[c[2]], abs(c[0] - fx) + abs(c[1] - fy)))
    return candidates[0]


def melon_maxxer(obs):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    private = obs.get("private", {}) or {}
    if not farms or player >= len(farms):
        return PASS
    farm = farms[player]
    board_size = len(farm["tiles"])
    fx, fy = farm["farmer"]
    tile = farm["tiles"][fy][fx]
    day = obs.get("day", 0)
    seeds = private.get("seeds", {})
    shed = private.get("shed", {})
    market_prices = (obs.get("market", {}) or {}).get("prices", {})
    melon_price = market_prices.get("MELON", 0)
    market = []
    melons_in_shed = shed.get("MELON", 0)
    if melons_in_shed > 0 and melon_price >= SELL_THRESHOLD:
        market.append(["SELL", "MELON", melons_in_shed])
    if seeds.get("MELON", 0) == 0 and farm["money"] >= MELON_SEED_COST:
        market.append(["BUY_SEED", "MELON", 1])
    farmer = ["PASS"]
    if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile["crop"] == "MELON":
        age = day - tile["planted_day"]
        if age >= MELON_MAX_YIELD_DAY and tile["yield_units"] > 0:
            farmer = ["HARVEST"]
        elif not tile["watered_today"]:
            farmer = ["WATER"]
        else:
            target = _find_target_tile(farm, board_size, seeds.get("MELON", 0) > 0)
            if target:
                step = _step_toward(fx, fy, target[0], target[1])
                if step:
                    farmer = [step]
    elif tile is None and seeds.get("MELON", 0) > 0:
        farmer = ["PLANT", "MELON"]
    else:
        target = _find_target_tile(farm, board_size, seeds.get("MELON", 0) > 0)
        if target:
            step = _step_toward(fx, fy, target[0], target[1])
            if step:
                farmer = [step]
    return {"farmer": farmer, "hands": [], "market": market}


# ---------------------------------------------------------------------------
# Baseline agent — priority-driven multi-crop + animals + hiring + land
# ---------------------------------------------------------------------------
# Task priorities (lower = more urgent)
P_FEED = 0        # animal may escape tomorrow
P_WATER_CRIT = 1  # plant will die at end of day if not watered
P_HARVEST = 2     # plant/animal ready
P_FERTILIZE = 3   # plant in bonus window, not fertilized
P_COLLECT = 4     # animal fertilizer available
P_WATER_BONUS = 5 # plant in watering-bonus window, unwatered
P_PLACE = 6       # animal in inventory + empty structure
P_PLANT = 7       # empty tile + seed
P_DIG = 8         # weed
P_BUILD = 9       # empty tile + planned structure
P_WATER = 10      # routine watering


def _in_bonus_window(crop, age_days):
    cd = CROPS[crop]
    if cd["ongoing"]:
        return age_days >= cd["first_yield_day"]
    ws = (cd["max_yield_day"] + 1) // 2
    return ws <= age_days <= cd["max_yield_day"]


def _crop_choice(day, melon_price, wheat_need, has_melon_seed):
    if wheat_need > 0:
        return "WHEAT"
    if day <= 18 and has_melon_seed:
        return "MELON"
    if day <= 24:
        return "WHEAT"
    return None


def _count_tiles(farm, pred):
    return sum(1 for row in farm["tiles"] for t in row if pred(t))


def _scan_tasks(farm, private, day, hour, seed_choice, inv, sheds, plant_budget):
    tasks = {}
    board = farm["tiles"]
    n = len(board)
    n_coops = 0
    n_pastures = 0
    shed_geese = sheds.get("GOOSE", 0)
    shed_cows = sheds.get("COW", 0)
    geese_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "GOOSE")
    cows_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "COW")
    for y in range(n):
        for x in range(n):
            tile = board[y][x]
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PLANT":
                crop = tile["crop"]
                cd = CROPS[crop]
                age = day - tile["planted_day"]
                first = cd["first_yield_day"]
                if tile["yield_units"] > 0 and age >= first:
                    # One-time crops: only harvest when mature (max_yield reached
                    # or max_yield_day elapsed); early harvest forfeits yield.
                    ready = (cd["ongoing"] or tile["yield_units"] >= cd["max_yield"]
                             or age >= cd["max_yield_day"])
                    if ready:
                        tasks[(x, y)] = (P_HARVEST, ["HARVEST"], None)
                    elif tile["consecutive_unwatered"] >= 1 and not tile["watered_today"]:
                        tasks[(x, y)] = (P_WATER_CRIT, ["WATER"], None)
                    elif not tile["watered_today"]:
                        if "FERTILIZER" in inv and tile.get("fertilized_until_day", -1) < day and _in_bonus_window(crop, age):
                            tasks[(x, y)] = (P_FERTILIZE, ["FERTILIZE"], None)
                        elif _in_bonus_window(crop, age):
                            tasks[(x, y)] = (P_WATER_BONUS, ["WATER"], None)
                        else:
                            tasks[(x, y)] = (P_WATER, ["WATER"], None)
                elif not tile["watered_today"]:
                    # Immature: water keeps it alive; bonus-window waters build yield.
                    if tile["consecutive_unwatered"] >= 1:
                        tasks[(x, y)] = (P_WATER_CRIT, ["WATER"], None)
                    elif _in_bonus_window(crop, age):
                        tasks[(x, y)] = (P_WATER_BONUS, ["WATER"], None)
                    else:
                        tasks[(x, y)] = (P_WATER, ["WATER"], None)
            elif "animal" in tile:
                if tile.get("yield_units", 0) > 0:
                    tasks[(x, y)] = (P_HARVEST, ["HARVEST"], None)
                elif tile.get("consecutive_unfed", 0) >= 1 and not tile.get("fed_today"):
                    tasks[(x, y)] = (P_FEED, ["FEED"], "WHEAT")
                elif tile.get("fertilizer_available"):
                    tasks[(x, y)] = (P_COLLECT, ["COLLECT_FERTILIZER"], None)
                elif not tile.get("fed_today"):
                    tasks[(x, y)] = (P_FEED, ["FEED"], "WHEAT")
            elif kind == "COOP":
                n_coops += 1
                if shed_geese > 0 and geese_placed + shed_geese <= 6:
                    tasks[(x, y)] = (P_PLACE, ["PLACE", "GOOSE"], "GOOSE")
            elif kind == "PASTURE":
                n_pastures += 1
                if shed_cows > 0 and cows_placed + shed_cows <= 4:
                    tasks[(x, y)] = (P_PLACE, ["PLACE", "COW"], "COW")
            elif kind == "WEED":
                tasks[(x, y)] = (P_DIG, ["DIG"], None)

    plants = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT")
    seeds = private.get("seeds", {})
    budget = max(0, plant_budget - plants)
    can_plant = (budget > 0 and seed_choice is not None
                 and seeds.get(seed_choice, 0) > 0 and hour < 22)
    need_coop = shed_geese > 0 and n_coops < min(3, geese_placed + shed_geese)
    need_pasture = shed_cows > 0 and cows_placed + shed_cows <= 4 and n_pastures < 2

    for y in range(n):
        for x in range(n):
            if board[y][x] is not None:
                continue
            if can_plant and budget > 0:
                tasks.setdefault((x, y), (P_PLANT, ["PLANT", seed_choice], None))
                budget -= 1
                continue
            if need_coop:
                tasks.setdefault((x, y), (P_BUILD, ["BUILD_COOP"], None))
                continue
            if need_pasture:
                tasks.setdefault((x, y), (P_BUILD, ["BUILD_PASTURE"], None))
    return tasks


def _next_task(farm, unit_pos, tasks, claimed):
    fx, fy = unit_pos
    best = None
    for (tx, ty), (prio, action, req) in tasks.items():
        if (tx, ty) in claimed:
            continue
        dist = abs(tx - fx) + abs(ty - fy)
        # Emergency (die-risk) tasks outrank distance; else prefer near
        urgent = prio <= P_WATER_CRIT
        score = (prio, 0 if urgent else dist)
        if best is None or score < best[0]:
            best = (score, (tx, ty), prio, action, req)
    return best


def _step_toward_pos(fx, fy, tx, ty):
    if fx > tx:
        return "WEST"
    if fx < tx:
        return "EAST"
    if fy > ty:
        return "NORTH"
    if fy < ty:
        return "SOUTH"
    return None


def _nearest_shed(fx, fy):
    return min(SHED_TILES, key=lambda p: abs(p[0] - fx) + abs(p[1] - fy))


def _unit_action(farm, private, pos, tasks, claimed, shed, inv):
    """Decide one unit's action. Returns (action_list, claimed_tile)."""
    fx, fy = pos

    # Lock-in: a unit carrying an animal must finish placing it before any
    # other task. Without this, watering/harvest priorities divert the unit
    # every turn and the cow is carried in circles until night-drop.
    carried_animal = next((a for a in ("COW", "SHEEP", "GOOSE") if inv.get(a, 0) > 0), None)
    if carried_animal is not None:
        for (tx, ty), (prio, action, req) in tasks.items():
            if (tx, ty) in claimed:
                continue
            if action == ["PLACE", carried_animal]:
                if (fx, fy) == (tx, ty):
                    claimed.add((fx, fy))
                    return action, None
                step = _step_toward_pos(fx, fy, tx, ty)
                return ([step] if step else ["PASS"]), None
        if (fx, fy) in SHED_TILES and any(inv.values()):
            return ["DROP"], None
        return ["PASS"], None

    for (tx, ty), (prio, action, req) in tasks.items():
        if (tx, ty) == (fx, fy):
            if req is not None:
                if inv.get(req, 0) > 0:
                    claimed.add((fx, fy))
                    return action, None
                if shed.get(req, 0) > 0:
                    if (fx, fy) in SHED_TILES:
                        claimed.add((fx, fy))
                        return ["PICKUP", req, 1], None
                    sx, sy = _nearest_shed(fx, fy)
                    step = _step_toward_pos(fx, fy, sx, sy)
                    return ([step] if step else ["PASS"]), None
                return ["PASS"], None
            claimed.add((fx, fy))
            return action, None

    best = _next_task(farm, pos, tasks, claimed)
    if best is None:
        if (fx, fy) in SHED_TILES and any(inv.values()):
            return ["DROP"], None
        return ["PASS"], None

    score, (tx, ty), prio, action, req = best
    if req is not None and inv.get(req, 0) <= 0:
        if shed.get(req, 0) <= 0:
            return ["PASS"], None
        if (fx, fy) in SHED_TILES:
            claimed.add((fx, fy))
            return ["PICKUP", req, 1], None
        sx, sy = _nearest_shed(fx, fy)
        step = _step_toward_pos(fx, fy, sx, sy)
        return ([step] if step else ["PASS"]), None
    if (fx, fy) == (tx, ty):
        claimed.add((fx, fy))
        return action, None
    step = _step_toward_pos(fx, fy, tx, ty)
    return ([step] if step else ["PASS"]), None


def baseline(obs):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    private = obs.get("private", {}) or {}
    if not farms or player >= len(farms):
        return PASS
    farm = farms[player]
    private = obs.get("private", {}) or {}
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    money = farm["money"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    inv_farmer = private.get("inventories", [{}])[0]
    prices = (obs.get("market", {}) or {}).get("prices", {})
    n_hands = len(farm.get("hands", []))

    # ------------------------------------------------------------------ market
    market = []
    last_days = day >= 26
    n_animals_est = _count_tiles(farm, lambda t: isinstance(t, dict) and "animal" in t)
    plants_count = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT")
    n_coops = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "COOP")
    n_pastures = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PASTURE")

    # SELL: melon liquidates at 200+ (melon_maxxer parity; price rarely
    # recovers to base 250 after any sale). Others gate at base; chunk crashy.
    wheat_reserve = n_animals_est * 3
    for prod, count in list(shed.items()):
        if prod in ("GOOSE", "COW", "SHEEP") or count <= 0:
            continue
        if prod == "FERTILIZER":
            if count > 8:
                market.append(["SELL", "FERTILIZER", count - 8])
            continue
        if prod == "WHEAT" and count <= wheat_reserve and not last_days:
            continue
        price = prices.get(prod, 0)
        gate = 200 if prod == "MELON" else BASE_PRICE[prod]
        if last_days or price >= gate:
            chunk = count if (last_days or not CRASH_RISK.get(prod)) else min(count, SELL_CHUNK)
            market.append(["SELL", prod, chunk])

    wheat_in_shed = shed.get("WHEAT", 0)
    wheat_need = max(0, wheat_reserve - wheat_in_shed - seeds.get("WHEAT", 0))
    plant_budget = (1 + n_hands) * 12
    if day <= 18:
        n_melon = seeds.get("MELON", 0)
        want = max(0, plant_budget - n_melon)
        if want > 0 and money >= 80:
            market.append(["BUY_SEED", "MELON", min(want, 3)])
    if seeds.get("WHEAT", 0) == 0 and money >= 10 and wheat_need > 0:
        market.append(["BUY_SEED", "WHEAT", 1])

    if wheat_need > 0 and money >= 25 and wheat_in_shed < 2:
        market.append(["BUY_PRODUCT", "WHEAT", min(wheat_need, 3)])

    urgent_count = 0
    for row in farm["tiles"]:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT" and t.get("consecutive_unwatered", 0) >= 1 and not t.get("watered_today"):
                urgent_count += 1
            if "animal" in t and t.get("consecutive_unfed", 0) >= 1 and not t.get("fed_today"):
                urgent_count += 1
    hire_cost = [1, 1, 2, 3, 5, 8][farm.get("hires_today", 0)] if farm.get("hires_today", 0) < 6 else 999
    overloaded = urgent_count > 1 + n_hands or plants_count > (1 + n_hands) * 10
    expanding = n_hands < 3 and day <= 4 and money >= 200
    if (overloaded or expanding) and money >= hire_cost + 100 and n_hands < 4:
        market.append(["HIRE"])

    # BUY LAND when cash is comfortable
    n_extra = len(farm.get("unlocked_quadrants", ["NW"])) - 1
    land_price = [1000, 2000, 4000][n_extra] if n_extra < 3 else None
    if land_price is not None and money >= land_price + 800 and day <= 15:
        market.append(["BUY_LAND"])

    market = market[:10]

    # ------------------------------------------------------------- unit tasks
    seed_choice = _crop_choice(day, prices.get("MELON", 0), wheat_need, seeds.get("MELON", 0) > 0)
    plant_budget = (1 + n_hands) * 12
    tasks = _scan_tasks(farm, private, day, hour, seed_choice, inv_farmer, shed, plant_budget)
    claimed = set()
    hands_actions = []

    farmer_pos = farm["farmer"]
    farmer_act, _ = _unit_action(farm, private, farmer_pos, tasks, claimed, shed, inv_farmer)
    if isinstance(farmer_act, list) and farmer_act and farmer_act[0] not in ("NORTH", "SOUTH", "EAST", "WEST", "PASS"):
        claimed.add((farmer_pos[0], farmer_pos[1]))

    for h_idx, hpos in enumerate(farm.get("hands", [])):
        hinv = private.get("inventories", [{}])[h_idx + 1] if h_idx + 1 < len(private.get("inventories", [{}])) else {}
        act, _ = _unit_action(farm, private, hpos, tasks, claimed, shed, hinv)
        hands_actions.append(act if isinstance(act, list) else ["PASS"])

    return {"farmer": farmer_act if isinstance(farmer_act, list) else ["PASS"],
            "hands": hands_actions,
            "market": market}


# ---------------------------------------------------------------------------
# v8 agent — the top-meta build (reverse-engineered from the ladder):
#   * 12 MELON early cash + aggressive liquidation by day 12-14
#   * 8 COW + 6 SHEEP = milk+wool+fertilizer core (~50% of income)
#   * Animals produce 1 FERTILIZER/day for free (fertilizer_available=True
#     every refresh, feed or not). Fertilized water gives +2 yield vs +1,
#     which DOUBLES strawberry production rate and halves melon watering.
#   * ~36 STRAWBERRY mass-planted after the first melon wave (day 8-14)
#   * 2 land buys only (NE day 7, SW day 11); never the 4th quadrant
#   * Hands ramp 0 -> 8-10 -> up to 14 by day 11 (re-hired daily, cost
#     resets to fib(0)=1 each morning; HIRE stays first in the queue)
#   * Endgame (day 20-29): replant WHEAT (price rises all game), liquidate
#     everything before step 720 (reward = final bank only)
# Never: geese/chickens, carrots/tomatoes, BUY_PRODUCT FERTILIZER.
#
# Env mechanics this build leans on (verified against source):
#   * COW: 400, PASTURE, first_yield 8, interval 2, max_held 6, MILK base 160
#   * SHEEP: 500, PASTURE, first_yield 6, interval 3, max_held 6, WOOL base 200
#   * Animal yield += 1 on production day; +1 more if fed+cared that day
#     (pending_care_bonus consumed next production day)
#   * Escape after 2 consecutive UNFED days -> tile reverts to structure
#   * FERTILIZE covers day..day+2; WATER bonus = 2 if fertilized_until>=day
#   * STRAWBERRY: seed 100, first_yield 10, interval 2, max_yield 4, ongoing
#   * MELON: seed 80, first_yield 10, max_yield 12, max_yield 6, one-shot
#   * WHEAT: seed 10, first_yield 2, max_yield 4, max_yield 6, one-shot
#   * Land order NE(1000) SW(2000) SE(4000); only 2 buys in the meta
#   * Hands reset nightly; cost = fib(hires_today): 1,1,2,3,5,8,13,21,34,55,89
# ---------------------------------------------------------------------------
V8_MELON_TARGET = 12        # early cash engine
V8_WHEAT_TARGET = 10        # feed the herd + endgame price rise
V8_STRAWBERRY_TARGET = 42   # mass pivot after first melon wave (meta: ~42)
V8_COW_TARGET = 8
V8_SHEEP_TARGET = 6
V8_HANDS_TARGET = 14
V8_PASTURE_TARGET = 14      # 8 cows + 6 sheep
# v8 priority ladder. FEED/WATER_CRIT stay at 0/1 because _next_task's
# `prio <= P_WATER_CRIT` check is hardcoded. Order: survival (feed/crit/
# harvest/fertilize) > placement > weed-dig > pasture-build > routine water >
# new planting. DIG/BUILD sit above PLANT so weeds and pastures never lose to
# planting; BUILD sits below bonus watering so it only claims slack labor.
V8P_FEED = 0
V8P_WATER_CRIT = 1
V8P_HARVEST = 2
V8P_FERTILIZE = 3
V8P_COLLECT = 4
V8P_CARE = 5
V8P_PLACE = 6
V8P_WATER_BONUS = 7
V8P_DIG = 8
V8P_BUILD = 9
V8P_WATER = 10
V8P_PLANT = 11


def _v8_counts(farm, shed):
    n_melon = _count_tiles(farm, lambda t: isinstance(t, dict)
                           and t.get("kind") == "PLANT" and t["crop"] == "MELON")
    n_wheat = _count_tiles(farm, lambda t: isinstance(t, dict)
                           and t.get("kind") == "PLANT" and t["crop"] == "WHEAT")
    n_straw = _count_tiles(farm, lambda t: isinstance(t, dict)
                           and t.get("kind") == "PLANT" and t["crop"] == "STRAWBERRY")
    cows_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "COW")
    sheep_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "SHEEP")
    pastures = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PASTURE")
    return (n_melon, n_wheat, n_straw, cows_placed, sheep_placed, pastures)


def _crop_choice_v8(day, wheat_plants, melon_plants, straw_plants, has_wheat_seed,
                    has_melon_seed, has_straw_seed):
    # Day 0-2: 7 WHEAT + 12 MELON. Wheat matures day 4-5 to feed the herd.
    if day <= 2 and wheat_plants < 7 and has_wheat_seed:
        return "WHEAT"
    # Melon phase comes BEFORE any wheat floor. The old `day<=7 wheat<3` floor
    # shadowed melons forever: when wheat plants died (unwatered while hands
    # are busy) the floor returned WHEAT every scan and melons stalled at 7/12
    # -- the trace showed mel=7 max, seeds MELON=5 never planted. Initial 7
    # wheat + shed reserve + BUY_PRODUCT WHEAT cover the herd feed, so melons
    # get the full planting window d0-8.
    if day <= 8 and melon_plants < V8_MELON_TARGET and has_melon_seed:
        return "MELON"
    # Strawberry mass-plant (recipe: days 8-14).
    if 8 <= day <= 14 and straw_plants < V8_STRAWBERRY_TARGET and has_straw_seed:
        return "STRAWBERRY"
    if wheat_plants < V8_WHEAT_TARGET and has_wheat_seed and day <= 26:
        return "WHEAT"
    return None


def _scan_tasks_v8(farm, private, day, hour, seed_choice, inv, sheds, plant_budget):
    """Task scan for v8. Plant tasks are STRICTLY seed/budget limited so the
    scheduler never floods plant requests the way v7 did (73 plants on day 0,
    67 on day 14 — units burned turns on impossible plants)."""
    tasks = {}
    board = farm["tiles"]
    n = len(board)
    n_pastures = 0
    shed_cows = sheds.get("COW", 0)
    shed_sheep = sheds.get("SHEEP", 0)
    shed_fert = sheds.get("FERTILIZER", 0)
    # REAL placed counts: the pasture loop below used a local task counter
    # that started at 0 each scan, emitting up to 8 PLACE tasks even with 1
    # cow in the shed -> every hand raced empty pastures (PICKUP/DROP thrash).
    placed_cows = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "COW")
    placed_sheep = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "SHEEP")
    # Emit at most one PLACE task per animal actually in the shed (capped by
    # target), so a hand never carries an animal with no unclaimed pasture.
    cow_place_budget = min(shed_cows, max(0, V8_COW_TARGET - placed_cows))
    sheep_place_budget = min(shed_sheep, max(0, V8_SHEEP_TARGET - placed_sheep))
    for y in range(n):
        for x in range(n):
            tile = board[y][x]
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PLANT":
                crop = tile["crop"]
                cd = CROPS[crop]
                age = day - tile["planted_day"]
                first = cd["first_yield_day"]
                if tile["yield_units"] > 0 and age >= first:
                    ready = (cd["ongoing"] or tile["yield_units"] >= cd["max_yield"]
                             or age >= cd["max_yield_day"])
                    if ready:
                        tasks[(x, y)] = (V8P_HARVEST, ["HARVEST"], None)
                    elif tile["consecutive_unwatered"] >= 1 and not tile["watered_today"]:
                        tasks[(x, y)] = (V8P_WATER_CRIT, ["WATER"], None)
                    elif not tile["watered_today"]:
                        if (tile.get("fertilized_until_day", -1) < day
                                and _in_bonus_window(crop, age)
                                and (inv.get("FERTILIZER", 0) > 0 or shed_fert > 0)):
                            tasks[(x, y)] = (V8P_FERTILIZE, ["FERTILIZE"], "FERTILIZER")
                        elif _in_bonus_window(crop, age):
                            tasks[(x, y)] = (V8P_WATER_BONUS, ["WATER"], None)
                        else:
                            tasks[(x, y)] = (V8P_WATER, ["WATER"], None)
                elif not tile["watered_today"]:
                    if tile["consecutive_unwatered"] >= 1:
                        tasks[(x, y)] = (V8P_WATER_CRIT, ["WATER"], None)
                    elif _in_bonus_window(crop, age):
                        tasks[(x, y)] = (V8P_WATER_BONUS, ["WATER"], None)
                    else:
                        tasks[(x, y)] = (V8P_WATER, ["WATER"], None)
            elif "animal" in tile:
                # Feed is life-or-death (escape after 2 unfed days) -> top prio.
                if tile.get("yield_units", 0) > 0:
                    tasks[(x, y)] = (V8P_HARVEST, ["HARVEST"], None)
                elif not tile.get("fed_today"):
                    tasks[(x, y)] = (V8P_FEED, ["FEED"], "WHEAT")
                elif not tile.get("cared_today"):
                    tasks[(x, y)] = (V8P_CARE, ["CARE"], None)
                elif tile.get("fertilizer_available"):
                    tasks[(x, y)] = (V8P_COLLECT, ["COLLECT_FERTILIZER"], None)
            elif kind == "PASTURE":
                n_pastures += 1
                if cow_place_budget > 0:
                    tasks[(x, y)] = (V8P_PLACE, ["PLACE", "COW"], "COW")
                    cow_place_budget -= 1
                elif sheep_place_budget > 0:
                    tasks[(x, y)] = (V8P_PLACE, ["PLACE", "SHEEP"], "SHEEP")
                    sheep_place_budget -= 1
            elif kind == "WEED":
                tasks[(x, y)] = (V8P_DIG, ["DIG"], None)

    plants = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT")
    seeds = private.get("seeds", {})
    budget = max(0, plant_budget - plants)
    seeds_left = seeds.get(seed_choice, 0) if seed_choice else 0
    can_plant = (budget > 0 and seed_choice is not None
                 and seeds_left > 0 and hour < 22)
    # Pastures only for animals already owned (shed+placed) plus a small
    # lookahead so the cow/ship buy gate (needs an empty pasture) can fire;
    # never speculative +6 that ate 12+ tiles of the NW quadrant on day 0.
    herd_planned = min(V8_PASTURE_TARGET,
                       shed_cows + shed_sheep + placed_cows + placed_sheep + 2)
    build_pastures = max(0, herd_planned - n_pastures)

    # PLANT first, BUILD second: the opening must fill the quadrant with
    # melons/wheat, not pastures. BUILD rides below routine watering so it
    # never starves the crops.
    for y in range(n):
        for x in range(n):
            if board[y][x] is not None:
                continue
            if can_plant and budget > 0 and seeds_left > 0:
                tasks.setdefault((x, y), (V8P_PLANT, ["PLANT", seed_choice], None))
                budget -= 1
                seeds_left -= 1
                continue
            if build_pastures > 0:
                tasks.setdefault((x, y), (V8P_BUILD, ["BUILD_PASTURE"], None))
                build_pastures -= 1
    return tasks


def baseline_v8(obs):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    if not farms or player >= len(farms):
        return PASS
    farm = farms[player]
    private = obs.get("private", {}) or {}
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    money = farm["money"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    inv_farmer = private.get("inventories", [{}])[0]
    prices = (obs.get("market", {}) or {}).get("prices", {})
    n_hands = len(farm.get("hands", []))

    (n_melon, n_wheat, n_straw, cows_placed, sheep_placed, n_pastures) = _v8_counts(farm, shed)
    cows_total = cows_placed + shed.get("COW", 0)
    sheep_total = sheep_placed + shed.get("SHEEP", 0)
    animals_placed = cows_placed + sheep_placed
    animals_total = cows_total + sheep_total
    last_days = day >= 26

    # ------------------------------------------------------------------ market
    market = []
    wheat_in_shed = shed.get("WHEAT", 0)
    # Reserve feeds PLACED animals only (shed animals don't eat). Stable floor
    # so we never sell wheat below what the herd needs while it's still eating.
    wheat_reserve = animals_placed * 2 + 4
    wheat_need = max(0, wheat_reserve - wheat_in_shed - seeds.get("WHEAT", 0))

    # HIRE first in the queue — 10-order cap must never starve hiring.
    # Hands reset nightly; cost resets to fib(0)=1 each morning. Ramp to 14 by
    # day 11 per the meta, gated by money floor so hiring never bankrupts us.
    hire_cost = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89][farm.get("hires_today", 0)] \
        if farm.get("hires_today", 0) < 11 else 999
    plants_total = n_melon + n_wheat + n_straw
    # Meta ramp: 0-2 hands day 0-2 (cash goes to seeds+pastures), scale with
    # workload, hit ~14 by day 11 once milk/wool/fertilizer income flows.
    if day <= 2:
        want_hands = min(2, 1 + animals_placed)
    else:
        want_hands = min(V8_HANDS_TARGET, 3 + animals_placed + plants_total // 6)
    # Hire floor lowered from +100 to +20: the old floor killed hiring the
    # moment cash dipped (d09 $18 -> 0 hands -> melons die -> no income ever).
    if len(farm.get("hands", [])) < want_hands and money >= hire_cost + 20:
        market.append(["HIRE"])

    # SELL logic — melons liquidate aggressively (never hold for the late
    # crash); milk/wool/fertilizer/strawberry chunked to avoid glut crashes.
    for prod, count in list(shed.items()):
        if prod in ("GOOSE", "COW", "SHEEP") or count <= 0:
            continue
        if prod == "FERTILIZER":
            keep = 10 + plants_total // 4   # fertilize melons + strawberries
            if count > keep:
                market.append(["SELL", "FERTILIZER", count - keep])
            continue
        if prod == "WHEAT" and count <= wheat_reserve and not last_days:
            continue
        price = prices.get(prod, 0)
        gate = {"MELON": 180, "STRAWBERRY": 110}.get(prod, BASE_PRICE[prod])
        if last_days or price >= gate:
            chunk = count if (last_days or not CRASH_RISK.get(prod)) else min(count, SELL_CHUNK)
            market.append(["SELL", prod, chunk])

    # Animals — cows first (milk is the #1 correlation), then sheep. Day 0-2
    # the meta builds pasture + plants only; animals start day 3 when wheat is
    # maturing (needs feed available). Phase in with cash flow: keep a
    # working-capital floor so 3 cows can never be bought back-to-back and
    # drain the bank before melon income lands (d10-12). Also require an empty
    # pasture (else the animal idles in the shed) and feed on hand.
    # Floor lowered from 400+700 / 500+700 to cost+150: the old floor plus the
    # strawberry cash drain meant money never recovered to 1100 and the herd
    # stayed at 1 cow all game. 8 cows + 6 sheep need ~6200 total, bought
    # incrementally as melon+milk income lands.
    cow_budget = V8_COW_TARGET - cows_total
    sheep_budget = V8_SHEEP_TARGET - sheep_total
    wheat_for_feed = wheat_in_shed + n_wheat * 3
    if day >= 3 and n_pastures > animals_placed:
        if cow_budget > 0 and money >= 400 + 150 and wheat_for_feed >= 2:
            market.append(["BUY_ANIMAL", "COW", 1])
        elif sheep_budget > 0 and money >= 500 + 150 and wheat_for_feed >= 2:
            market.append(["BUY_ANIMAL", "SHEEP", 1])

    # Land: NE day 7 (1000), SW day 11 (2000). Skip SE (4000) forever.
    n_extra = len(farm.get("unlocked_quadrants", ["NW"])) - 1
    land_due = (7 <= day and n_extra == 0) or (11 <= day and n_extra == 1)
    if land_due:
        land_price = [1000, 2000, 4000][n_extra]
        if money >= land_price + 400:
            market.append(["BUY_LAND"])

    # MELON seeds — buy to target, keep a cash floor so animals/hands never starve.
    n_melon_total = n_melon + seeds.get("MELON", 0)
    if day <= 8 and n_melon_total < V8_MELON_TARGET:
        want = min(V8_MELON_TARGET - n_melon_total, 3)
        if money >= 80 * want + 300:
            market.append(["BUY_SEED", "MELON", want])

    # WHEAT seeds — keep the herd fed; 10 plants rotate continuously.
    n_wheat_total = n_wheat + seeds.get("WHEAT", 0)
    if n_wheat_total < V8_WHEAT_TARGET and money >= 30 and day <= 26:
        market.append(["BUY_SEED", "WHEAT", min(V8_WHEAT_TARGET - n_wheat_total, 2)])
    if wheat_need > 0 and money >= 25 and wheat_in_shed < 2:
        market.append(["BUY_PRODUCT", "WHEAT", min(wheat_need, 3)])

    # STRAWBERRY seeds — buy ONCE per day at hour 0, paced to free tiles.
    # The old gate (money >= 200) re-evaluated every hour: the trace showed
    # d08 $835 -> d09 $18 as repeated $200 buys drained the bank before melon
    # income landed, killing HIRE and the whole run. Hour-0 + a 400 floor
    # keeps ~4 seeds/day while protecting the cash runway.
    n_straw_total = n_straw + seeds.get("STRAWBERRY", 0)
    free_tiles = sum(1 for row in farm["tiles"] for t in row if t is None)
    if 8 <= day <= 14 and hour == 0 and n_straw_total < V8_STRAWBERRY_TARGET and money >= 400:
        want = min(V8_STRAWBERRY_TARGET - n_straw_total, free_tiles, 4)
        if want > 0:
            market.append(["BUY_SEED", "STRAWBERRY", want])

    market = market[:10]

    # ------------------------------------------------------------- unit tasks
    seed_choice = _crop_choice_v8(day, n_wheat, n_melon, n_straw,
                                  seeds.get("WHEAT", 0) > 0,
                                  seeds.get("MELON", 0) > 0,
                                  seeds.get("STRAWBERRY", 0) > 0)
    plant_budget = (1 + n_hands) * 12
    tasks = _scan_tasks_v8(farm, private, day, hour, seed_choice, inv_farmer, shed, plant_budget)
    claimed = set()
    hands_actions = []

    farmer_pos = farm["farmer"]
    farmer_act, _ = _unit_action(farm, private, farmer_pos, tasks, claimed, shed, inv_farmer)
    if isinstance(farmer_act, list) and farmer_act and farmer_act[0] not in ("NORTH", "SOUTH", "EAST", "WEST", "PASS"):
        claimed.add((farmer_pos[0], farmer_pos[1]))

    for h_idx, hpos in enumerate(farm.get("hands", [])):
        hinv = private.get("inventories", [{}])[h_idx + 1] if h_idx + 1 < len(private.get("inventories", [{}])) else {}
        act, _ = _unit_action(farm, private, hpos, tasks, claimed, shed, hinv)
        hands_actions.append(act if isinstance(act, list) else ["PASS"])

    return {"farmer": farmer_act if isinstance(farmer_act, list) else ["PASS"],
            "hands": hands_actions,
            "market": market}


# ---------------------------------------------------------------------------
# v7 agent — capped melon core + goose pipeline (EGG + free fertilizer)
#             + strawberry late pivot.
# Key economics (verified from source):
#   * MELON demand is capped (~140 units, town center only). 25 plants x 6 =
#     150 units captures the whole band; more just floods our own market.
#   * GOOSE=300: EGG (base 50, log-resistant) drained by BAKERY+BRUNCH_SPOT
#     and town; fertilizer_available=True EVERY day (no feed required for
#     fertilizer). Feed+CARE = +2 EGG/day capped at 4.
#   * FERTILIZER covers 3 watering days, +2 yield/water in the bonus window.
#     Free goose fertilizer turns 6 required melon waters into 3, freeing
#     ~3 farmer turns per plant for the animal pipeline.
#   * STRAWBERRY (base 120, 4 shops) planted day 12-20 yields 2-3 units by
#     day 28 on otherwise empty tiles.
# ---------------------------------------------------------------------------
P_CARE = 2        # animal care (after feed/water-die, before harvest)
MELON_CAP = 25
GOOSE_TARGET = 4
STRAWBERRY_TARGET = 4


def _crop_choice_v7(day, wheat_need, n_melon_plants, has_melon_seed,
                    wheat_plants, has_wheat_seed, has_strawberry_seed, n_strawberry_plants):
    if day <= 3 and wheat_plants < 3 and has_wheat_seed:
        return "WHEAT"
    if day <= 18 and has_melon_seed and n_melon_plants < MELON_CAP:
        return "MELON"
    if wheat_need > 0 and has_wheat_seed and day <= 24:
        return "WHEAT"
    if 12 <= day <= 20 and has_strawberry_seed and n_strawberry_plants < STRAWBERRY_TARGET:
        return "STRAWBERRY"
    return None


def _scan_tasks_v7(farm, private, day, hour, seed_choice, inv, sheds, plant_budget):
    tasks = {}
    board = farm["tiles"]
    n = len(board)
    n_coops = 0
    shed_geese = sheds.get("GOOSE", 0)
    geese_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "GOOSE")
    shed_fert = sheds.get("FERTILIZER", 0)
    for y in range(n):
        for x in range(n):
            tile = board[y][x]
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PLANT":
                crop = tile["crop"]
                cd = CROPS[crop]
                age = day - tile["planted_day"]
                first = cd["first_yield_day"]
                if tile["yield_units"] > 0 and age >= first:
                    ready = (cd["ongoing"] or tile["yield_units"] >= cd["max_yield"]
                             or age >= cd["max_yield_day"])
                    if ready:
                        tasks[(x, y)] = (P_HARVEST, ["HARVEST"], None)
                    elif tile["consecutive_unwatered"] >= 1 and not tile["watered_today"]:
                        tasks[(x, y)] = (P_WATER_CRIT, ["WATER"], None)
                    elif not tile["watered_today"]:
                        if (tile.get("fertilized_until_day", -1) < day
                                and _in_bonus_window(crop, age)
                                and (inv.get("FERTILIZER", 0) > 0 or shed_fert > 0)):
                            tasks[(x, y)] = (P_FERTILIZE, ["FERTILIZE"], "FERTILIZER")
                        elif _in_bonus_window(crop, age):
                            tasks[(x, y)] = (P_WATER_BONUS, ["WATER"], None)
                        else:
                            tasks[(x, y)] = (P_WATER, ["WATER"], None)
                elif not tile["watered_today"]:
                    if tile["consecutive_unwatered"] >= 1:
                        tasks[(x, y)] = (P_WATER_CRIT, ["WATER"], None)
                    elif _in_bonus_window(crop, age):
                        tasks[(x, y)] = (P_WATER_BONUS, ["WATER"], None)
                    else:
                        tasks[(x, y)] = (P_WATER, ["WATER"], None)
            elif "animal" in tile:
                if tile.get("yield_units", 0) > 0:
                    tasks[(x, y)] = (P_HARVEST, ["HARVEST"], None)
                elif not tile.get("fed_today"):
                    tasks[(x, y)] = (P_FEED, ["FEED"], "WHEAT")
                elif not tile.get("cared_today"):
                    tasks[(x, y)] = (P_CARE, ["CARE"], None)
                elif tile.get("fertilizer_available"):
                    tasks[(x, y)] = (P_COLLECT, ["COLLECT_FERTILIZER"], None)
            elif kind == "COOP":
                n_coops += 1
                if shed_geese > 0 and geese_placed < GOOSE_TARGET:
                    tasks[(x, y)] = (P_PLACE, ["PLACE", "GOOSE"], "GOOSE")
            elif kind == "WEED":
                tasks[(x, y)] = (P_DIG, ["DIG"], None)

    plants = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT")
    seeds = private.get("seeds", {})
    budget = max(0, plant_budget - plants)
    can_plant = (budget > 0 and seed_choice is not None
                 and seeds.get(seed_choice, 0) > 0 and hour < 22)
    need_coop = shed_geese > 0 and n_coops < GOOSE_TARGET

    for y in range(n):
        for x in range(n):
            if board[y][x] is not None:
                continue
            if can_plant and budget > 0:
                tasks.setdefault((x, y), (P_PLANT, ["PLANT", seed_choice], None))
                budget -= 1
                continue
            if need_coop:
                tasks.setdefault((x, y), (P_BUILD, ["BUILD_COOP"], None))
    return tasks


def baseline_v7(obs):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    if not farms or player >= len(farms):
        return PASS
    farm = farms[player]
    private = obs.get("private", {}) or {}
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    money = farm["money"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    inv_farmer = private.get("inventories", [{}])[0]
    prices = (obs.get("market", {}) or {}).get("prices", {})
    n_hands = len(farm.get("hands", []))

    last_days = day >= 26
    geese_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "GOOSE")
    n_geese_total = geese_placed + shed.get("GOOSE", 0)
    n_melon_plants = _count_tiles(farm, lambda t: isinstance(t, dict)
                                  and t.get("kind") == "PLANT" and t["crop"] == "MELON")
    n_strawberry_plants = _count_tiles(farm, lambda t: isinstance(t, dict)
                                       and t.get("kind") == "PLANT" and t["crop"] == "STRAWBERRY")
    n_wheat_plants = _count_tiles(farm, lambda t: isinstance(t, dict)
                                  and t.get("kind") == "PLANT" and t["crop"] == "WHEAT")

    # ------------------------------------------------------------------ market
    market = []
    budget = (1 + n_hands) * 12
    wheat_in_shed = shed.get("WHEAT", 0)
    wheat_reserve = n_geese_total * 4
    wheat_need = max(0, wheat_reserve - wheat_in_shed - seeds.get("WHEAT", 0))

    # Hands reset every day (env resets farm["hands"] nightly) so re-hire
    # daily while the farm has work; cost resets to fib(0)=1 each morning.
    # Scale target hands with workload: animals + plants both consume actions.
    # HIRE goes FIRST in the queue — seed buys must never starve it (10-order cap).
    hire_cost = [1, 1, 2, 3, 5, 8][farm.get("hires_today", 0)] if farm.get("hires_today", 0) < 6 else 999
    plants_total = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT")
    want_hands = min(5, 2 + n_geese_total + plants_total // 8)
    if len(farm.get("hands", [])) < want_hands and money >= hire_cost + 100:
        market.append(["HIRE"])
    if len(farm.get("hands", [])) < 2 and money >= hire_cost + 100:
        market.append(["HIRE"])

    for prod, count in list(shed.items()):
        if prod in ("GOOSE", "COW", "SHEEP") or count <= 0:
            continue
        if prod == "FERTILIZER":
            # Keep a working reserve while melons/strawberry still need it.
            keep = 12 if 5 <= day <= 14 else 8
            if count > keep:
                market.append(["SELL", "FERTILIZER", count - keep])
            continue
        if prod == "WHEAT" and count <= wheat_reserve and not last_days:
            continue
        price = prices.get(prod, 0)
        gate = {"MELON": 200, "STRAWBERRY": 120}.get(prod, BASE_PRICE[prod])
        if last_days or price >= gate:
            chunk = count if (last_days or not CRASH_RISK.get(prod)) else min(count, SELL_CHUNK)
            market.append(["SELL", prod, chunk])

    # MELON seeds: never plant more than current workers can water. 25 plants
    # with 1-2 workers = weeds + reseed bleed. Each worker sustains ~9 plants.
    if day <= 18:
        sustain_cap = min(MELON_CAP, (1 + n_hands) * 9 + 4)
        n_melon_total = n_melon_plants + seeds.get("MELON", 0)
        want = max(0, min(sustain_cap, budget) - n_melon_total)
        reserve = 1200 if day <= 4 else (600 if day <= 8 else 200)
        want = min(want, max(0, int((money - reserve) // 80)))
        if want > 0 and money >= reserve + 80:
            market.append(["BUY_SEED", "MELON", min(want, 3)])

    # Wheat seed early: it must be planted BEFORE the goose arrives so feed
    # exists by day 4. Plant 3 wheat day 0-1 regardless of geese plans.
    wheat_planted_now = n_wheat_plants + seeds.get("WHEAT", 0)
    if wheat_planted_now < 3 and money >= 30 and day <= 3:
        market.append(["BUY_SEED", "WHEAT", min(3 - wheat_planted_now, 2)])
    if seeds.get("WHEAT", 0) == 0 and money >= 10 and wheat_need > 0:
        market.append(["BUY_SEED", "WHEAT", 1])
    if wheat_need > 0 and money >= 25 and wheat_in_shed < 4:
        market.append(["BUY_PRODUCT", "WHEAT", min(wheat_need, 3)])

    # GOOSE pipeline: must NOT cannibalize the melon core. Trace shows buying
    # geese day 3-4 (600 gold) drops the bank below the hand-hiring floor and
    # the farm dies to weeds before melons pay. Defer until after the first
    # melon harvest (day 12) when cash is flowing again.
    wheat_capacity = wheat_in_shed + n_wheat_plants * 6
    if (n_geese_total < GOOSE_TARGET and 12 <= day <= 20 and money >= 900
            and wheat_capacity >= 8):
        market.append(["BUY_ANIMAL", "GOOSE", 1])

    # STRAWBERRY pivot: once melons are capped, buy a small plot.
    n_strawberry_total = n_strawberry_plants + seeds.get("STRAWBERRY", 0)
    if 12 <= day <= 18 and n_strawberry_total == 0 and money >= 400:
        market.append(["BUY_SEED", "STRAWBERRY", 1])

    urgent_count = 0
    for row in farm["tiles"]:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT" and t.get("consecutive_unwatered", 0) >= 1 and not t.get("watered_today"):
                urgent_count += 1
            if "animal" in t and t.get("consecutive_unfed", 0) >= 1 and not t.get("fed_today"):
                urgent_count += 1
    hire_cost = [1, 1, 2, 3, 5, 8][farm.get("hires_today", 0)] if farm.get("hires_today", 0) < 6 else 999
    plants_total = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT")
    overloaded = urgent_count > 1 + n_hands or plants_total > (1 + n_hands) * 10
    # Hands reset every day (env resets farm["hands"] nightly) so re-hire
    # daily while the farm has work; cost resets to fib(0)=1 each morning.
    # Scale target hands with workload: animals + plants both consume actions.
    want_hands = min(5, 2 + n_geese_total + plants_total // 10)
    if len(farm.get("hands", [])) < want_hands and money >= hire_cost + 100:
        market.append(["HIRE"])

    # BUY LAND only after melons pay (day 12+); day-0 land starves seeds/hands.
    n_extra = len(farm.get("unlocked_quadrants", ["NW"])) - 1
    land_price = [1000, 2000, 4000][n_extra] if n_extra < 3 else None
    if land_price is not None and money >= land_price + 800 and 12 <= day <= 20:
        market.append(["BUY_LAND"])

    market = market[:10]

    # ------------------------------------------------------------- unit tasks
    seed_choice = _crop_choice_v7(day, wheat_need, n_melon_plants,
                                  seeds.get("MELON", 0) > 0, n_wheat_plants,
                                  seeds.get("WHEAT", 0) > 0,
                                  seeds.get("STRAWBERRY", 0) > 0, n_strawberry_plants)
    plant_budget = (1 + n_hands) * 12
    tasks = _scan_tasks_v7(farm, private, day, hour, seed_choice, inv_farmer, shed, plant_budget)
    claimed = set()
    hands_actions = []

    farmer_pos = farm["farmer"]
    farmer_act, _ = _unit_action(farm, private, farmer_pos, tasks, claimed, shed, inv_farmer)
    if isinstance(farmer_act, list) and farmer_act and farmer_act[0] not in ("NORTH", "SOUTH", "EAST", "WEST", "PASS"):
        claimed.add((farmer_pos[0], farmer_pos[1]))

    for h_idx, hpos in enumerate(farm.get("hands", [])):
        hinv = private.get("inventories", [{}])[h_idx + 1] if h_idx + 1 < len(private.get("inventories", [{}])) else {}
        act, _ = _unit_action(farm, private, hpos, tasks, claimed, shed, hinv)
        hands_actions.append(act if isinstance(act, list) else ["PASS"])

    return {"farmer": farmer_act if isinstance(farmer_act, list) else ["PASS"],
            "hands": hands_actions,
            "market": market}
