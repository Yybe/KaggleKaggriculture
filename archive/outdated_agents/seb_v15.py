import math
import copy

CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}

BASE_PRICE = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
    "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100,
}

CRASH_RISK = {"MELON": True, "WOOL": True, "STRAWBERRY": True, "MILK": True}
SELL_CHUNK = 5
SHED_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}
PASS = {"farmer": ["PASS"], "hands": [], "market": []}

SEB_MELON_TARGET = 16
SEB_WHEAT_TARGET = 10
SEB_STRAWBERRY_TARGET = 45
SEB_COW_TARGET = 8
SEB_SHEEP_TARGET = 12
SEB_HANDS_TARGET = 12
SEB_PASTURE_TARGET = 20

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

def _in_bonus_window(crop, age_days):
    cd = CROPS[crop]
    if cd["ongoing"]:
        return age_days >= cd["first_yield_day"]
    ws = (cd["max_yield_day"] + 1) // 2
    return ws <= age_days <= cd["max_yield_day"]

def _count_tiles(farm, pred):
    return sum(1 for row in farm["tiles"] for t in row if pred(t))

def _v8_counts(farm, shed):
    n_melon = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT" and t["crop"] == "MELON")
    n_wheat = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT" and t["crop"] == "WHEAT")
    n_straw = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT" and t["crop"] == "STRAWBERRY")
    cows_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "COW")
    sheep_placed = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "SHEEP")
    pastures = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PASTURE")
    return (n_melon, n_wheat, n_straw, cows_placed, sheep_placed, pastures)

def _crop_choice_seb(day, wheat_plants, melon_plants, straw_plants, has_wheat_seed, has_melon_seed, has_straw_seed):
    if day <= 2 and wheat_plants < 7 and has_wheat_seed:
        return "WHEAT"
    if day <= 8 and melon_plants < SEB_MELON_TARGET and has_melon_seed:
        return "MELON"
    if 8 <= day <= 14 and straw_plants < SEB_STRAWBERRY_TARGET and has_straw_seed:
        return "STRAWBERRY"
    if wheat_plants < SEB_WHEAT_TARGET and has_wheat_seed and day <= 26:
        return "WHEAT"
    return None

def _scan_tasks_seb(farm, private, day, hour, seed_choice, inv, sheds, plant_budget):
    tasks = {}
    board = farm["tiles"]
    n = len(board)
    n_pastures = 0
    shed_cows = sheds.get("COW", 0)
    shed_sheep = sheds.get("SHEEP", 0)
    shed_fert = sheds.get("FERTILIZER", 0)
    placed_cows = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "COW")
    placed_sheep = _count_tiles(farm, lambda t: isinstance(t, dict) and t.get("animal") == "SHEEP")
    cow_place_budget = min(shed_cows, max(0, SEB_COW_TARGET - placed_cows))
    sheep_place_budget = min(shed_sheep, max(0, SEB_SHEEP_TARGET - placed_sheep))
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
                    ready = (cd["ongoing"] or tile["yield_units"] >= cd["max_yield"] or age >= cd["max_yield_day"])
                    if ready:
                        tasks[(x, y)] = (V8P_HARVEST, ["HARVEST"], None)
                    elif tile["consecutive_unwatered"] >= 1 and not tile["watered_today"]:
                        tasks[(x, y)] = (V8P_WATER_CRIT, ["WATER"], None)
                    elif not tile["watered_today"]:
                        if (tile.get("fertilized_until_day", -1) < day and _in_bonus_window(crop, age) and (inv.get("FERTILIZER", 0) > 0 or shed_fert > 0)):
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
    can_plant = (budget > 0 and seed_choice is not None and seeds_left > 0 and hour < 22)
    herd_planned = min(SEB_PASTURE_TARGET, shed_cows + shed_sheep + placed_cows + placed_sheep + 2)
    build_pastures = max(0, herd_planned - n_pastures)

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

def _next_task(farm, unit_pos, tasks, claimed):
    fx, fy = unit_pos
    best = None
    for (tx, ty), (prio, action, req) in tasks.items():
        if (tx, ty) in claimed:
            continue
        dist = abs(tx - fx) + abs(ty - fy)
        urgent = prio <= V8P_WATER_CRIT
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
    fx, fy = pos
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


# V14 Market Logic Overlays
_PRICE_FLOOR = 1
_DEMAND_ALPHA = 0.25
_MARKET_PARAMS = {
    "WHEAT": (25, 10000, 400, "sqrt", 0.8, "log", 0.2),
    "CARROT": (35, 10000, 450, "log", 0.2, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "linear", 0.4, "sqrt", 0.6),
    "STRAWBERRY": (120, 10000, 100, "sqrt", 0.7, "linear", 1.6),
    "MELON": (250, 10000, 300, "log", 0.2, "sq", 3.6),
    "EGG": (50, 10000, 332, "linear", 0.4, "log", 0.2),
    "MILK": (160, 10000, 122, "sqrt", 0.6, "linear", 1.6),
    "WOOL": (200, 10000, 105, "log", 0.2, "sq", 3.2),
    "FERTILIZER": (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}

_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

_SELLABLE = tuple(_MARKET_PARAMS)
_LIQUIDATION_ORDER = (
    "CARROT", "EGG", "FERTILIZER", "MELON", "MILK",
    "STRAWBERRY", "TOMATO", "WHEAT", "WOOL",
)

def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)

def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }

def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        return math.sqrt(value)
    if name == "log":
        return math.log1p(value)
    if name == "log10":
        return math.log10(1.0 + value)
    return value

def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))

def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )

def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices = _get(market, "prices", {}) or {}
    current_inventory = int(_get(inventory, item, 10000) or 0)
    current_quote = float(_get(prices, item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)

def _demand_per_day(obs, configuration, item):
    town = _get(obs, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    turns_per_day = int(_get(configuration, "turnsPerDay", 24) or 24)
    shop_interval = max(1, int(_get(configuration, "townShopSellInterval", 4) or 4))
    demand = 0.0
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (turns_per_day / shop_interval) * (2 if len(products) == 1 else 1)
    if item != "FERTILIZER":
        center_interval = max(1, int(_get(configuration, "townCenterSellInterval", 24) or 24))
        demand += turns_per_day / center_interval
    return demand

def _order_score(obs, configuration, order):
    score = _impact_score(obs, order)
    if score <= 0 or not _is_sell(order):
        return score
    item = str(order[1])
    quantity = max(0, int(order[2]))
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    current_inventory = int(_get(inventory, item, 10000) or 0)
    demand = max(0.25, _demand_per_day(obs, configuration, item))
    excess = max(0.0, current_inventory + quantity - 10000)
    urgency = min(1.0, (excess / demand) / 10.0)
    return score * (1.0 + _DEMAND_ALPHA * urgency)

def _rank_sell_slots(obs, action, configuration=None):
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows = [
        (_order_score(obs, configuration, order), -index, list(order))
        for index, order in enumerate(market)
        if _is_sell(order)
    ]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    ranked = iter(row[2] for row in rows)
    action["market"] = [next(ranked) if _is_sell(order) else order for order in market]
    return action

def _terminal_liquidation(obs, action, step):
    if step < 716:
        return action
    action = _copy_action(action)
    shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    planned = {item: 0 for item in _SELLABLE}
    for order in action.get("market", []):
        if _is_sell(order):
            planned[str(order[1])] += max(0, int(order[2]))
    for item in _LIQUIDATION_ORDER:
        available = max(0, int(_get(shed, item, 0) or 0))
        extra = available if step >= 718 else max(0, available - planned[item])
        if extra and len(action["market"]) < 10:
            action["market"].append(["SELL", item, extra])
    return action


def agent(obs, configuration=None):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    if not farms or player >= len(farms):
        return PASS
    farm = farms[player]
    private = obs.get("private", {}) or {}
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    step = obs.get("step", 0)
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

    market = []
    wheat_in_shed = shed.get("WHEAT", 0)
    wheat_reserve = animals_placed * 3
    wheat_need = max(0, wheat_reserve - wheat_in_shed - seeds.get("WHEAT", 0))

    hire_cost = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89][farm.get("hires_today", 0)] if farm.get("hires_today", 0) < 11 else 999
    
    if day == 0:
        want_hands = 7
    elif day <= 10:
        want_hands = 7 + (day * 5) // 10
    else:
        want_hands = SEB_HANDS_TARGET
        
    if len(farm.get("hands", [])) < want_hands and money >= hire_cost + 20:
        market.append(["HIRE"])

    n_extra = len(farm.get("unlocked_quadrants", ["NW"])) - 1
    land_due = (day >= 4 and n_extra == 0) or (day >= 6 and n_extra == 1) or (day >= 10 and n_extra == 2)
    land_price = [1000, 2000, 4000][n_extra] if n_extra < 3 else 0
    need_money = land_price + (300 if n_extra < 2 else 200) if land_due else 300

    sellable = [k for k in shed if k in _SELLABLE]
    for k in sellable:
        qty = shed[k]
        if qty > 0:
            if k == "WHEAT" and qty <= animals_placed * 3: continue
            if day >= 25 or money < need_money:
                market.append(["SELL", k, qty])

    cow_budget = SEB_COW_TARGET - cows_total
    sheep_budget = SEB_SHEEP_TARGET - sheep_total
    wheat_for_feed = wheat_in_shed + n_wheat * 3
    if day >= 3 and n_pastures > animals_placed:
        if cow_budget > 0 and money >= need_money + 550 and wheat_for_feed >= 2:
            market.append(["BUY_ANIMAL", "COW", 1])
        elif sheep_budget > 0 and money >= need_money + 400 and wheat_for_feed >= 2:
            market.append(["BUY_ANIMAL", "SHEEP", 1])

    if animals_placed > 0 and wheat_in_shed < animals_placed * 2:
        buy_amount = min(animals_placed * 2 - wheat_in_shed, 4)
        if buy_amount > 0 and money >= 25 * buy_amount:
            market.append(["BUY_PRODUCT", "WHEAT", buy_amount])

    if land_due:
        if money >= land_price + (300 if n_extra < 2 else 200):
            market.append(["BUY_LAND"])

    n_melon_total = n_melon + seeds.get("MELON", 0)
    if day <= 8 and n_melon_total < SEB_MELON_TARGET:
        want = min(SEB_MELON_TARGET - n_melon_total, 3)
        if money >= 80 * want + 300:
            market.append(["BUY_SEED", "MELON", want])

    n_wheat_total = n_wheat + seeds.get("WHEAT", 0)
    if n_wheat_total < SEB_WHEAT_TARGET and money >= 30 and day <= 26:
        market.append(["BUY_SEED", "WHEAT", min(SEB_WHEAT_TARGET - n_wheat_total, 2)])

    n_straw_total = n_straw + seeds.get("STRAWBERRY", 0)
    free_tiles = sum(1 for row in farm["tiles"] for t in row if t is None)
    if 8 <= day <= 14 and hour == 0 and n_straw_total < SEB_STRAWBERRY_TARGET and money >= 400:
        want = min(SEB_STRAWBERRY_TARGET - n_straw_total, free_tiles, 4)
        if want > 0:
            market.append(["BUY_SEED", "STRAWBERRY", want])

    market = market[:10]

    seed_choice = _crop_choice_seb(day, n_wheat, n_melon, n_straw,
                                  seeds.get("WHEAT", 0) > 0,
                                  seeds.get("MELON", 0) > 0,
                                  seeds.get("STRAWBERRY", 0) > 0)
    plant_budget = (1 + n_hands) * 12
    tasks = _scan_tasks_seb(farm, private, day, hour, seed_choice, inv_farmer, shed, plant_budget)
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

    action = {
        "farmer": farmer_act if isinstance(farmer_act, list) else ["PASS"],
        "hands": hands_actions,
        "market": market
    }
    
    action = _rank_sell_slots(obs, action, configuration)
    action = _terminal_liquidation(obs, action, step)
    
    return action
