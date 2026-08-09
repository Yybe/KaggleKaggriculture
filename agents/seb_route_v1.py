"""seb_route_v1 — Seb's four-quadrant route on the quick-start scheduler core.

Strategy graft (evidence: `four-quadrant-route-breakdown-and-feasibility.ipynb`,
11 public Seb replays + V14 clones, engine 1.32.6; 156 local paired games of
the open-loop R0 prototype):

  * Four-quadrant macro-route with live-state gates instead of a fixed tape:
      - NE buy gate  ~day 4-6   (Seb unlock frames 118-119, price $1,000)
      - SW buy gate  ~day 6-8   (Seb unlock frames 150-159, price $2,000)
      - SE buy gate  ~day 10-11 (Seb unlock frames 252-259, price $4,000)
    Financing honours Seb's visible trick: put SELL orders for the same market
    batch BEFORE BUY_LAND so finishing cash lands before the land charge.
    If the 4th-quadrant financing window fails we keep a healthy three-
    quadrant production path (safe degradation, notebook §6.4).
  * Mass-production targets (Seb route signature medians):
        peak COW 8, peak SHEEP 11 (range 9-16), peak STRAWBERRY 43,
        peak MELON 16 (vs V6's 12), peak hands 12 (vs V6's 14).
  * Adaptive herd: sheep share follows the median WOOL-MILK price gap
    (notebook §2, Spearman 0.77) - buy more SHEEP when wool is rich.
  * Straw plant window ~day 8-14 to 42-43 plants; melons front-loaded d0-8
    for the day-10-12 cash wave that funds SE.
  * Wheat policy: much lower sell volume than the engine meta (feed the
    herd first; Seb sells ~74 vs V6's 305).

Runtime skeleton = the repo's starter scheduler core (baseline_v8 task
scan, priority FEED/CARE/HARVEST/FERTILIZE/PU etc.), which is the single-
hop evolution of the official quick-start `submission.py` agent. All
mechanics verified against kaggle_environments 1.32.5 source field-by-
field from `Kaggriculture/agents_lib.py`.

Every decision is a pure function of the observation (stateless) so this
pickles cleanly for the playground ProcessPoolExecutor.
"""
from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS

# ---------------------------------------------------------------------------
# Ground-truth constants (from agents_lib)
# ---------------------------------------------------------------------------
BASE_PRICE = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
    "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100,
}
CRASH_RISK = {"MELON": True, "WOOL": True, "STRAWBERRY": True, "MILK": True}
SELL_CHUNK = 4
SHED_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}

# ---------------------------------------------------------------------------
# Seb route targets
# ---------------------------------------------------------------------------
SEB_MELON_TARGET = 16
SEB_WHEAT_TARGET = 10
SEB_STRAWBERRY_TARGET = 42
SEB_COW_TARGET = 8
SEB_SHEEP_BASE = 8          # rises when wool is rich
SEB_SHEEP_MAX = 12
SEB_HANDS_TARGET = 12
SEB_PASTURE_SPACE = 20      # 8 cow + up to 12 sheep

# Land: (required day, price). NW is free. Order is fixed by the engine.
LAND_PRICES = {0: 1000, 1: 2000, 2: 4000}
LAND_DUE_DAY = {0: 4, 1: 7, 2: 11}   # Seb NE ~4.9, SW ~6.5, SE ~10.6
LAND_CASH_FLOOR = {0: 500, 1: 800, 2: 1400}  # working capital kept beyond price

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


# ---------------------------------------------------------------------------
# helpers (identical semantics to agents_lib)
# ---------------------------------------------------------------------------

def _count_tiles(farm, pred):
    return sum(1 for row in farm["tiles"] for t in row if pred(t))


def _in_bonus_window(crop, age_days):
    cd = CROPS[crop]
    if cd["ongoing"]:
        return age_days >= cd["first_yield_day"]
    ws = (cd["max_yield_day"] + 1) // 2
    return ws <= age_days <= cd["max_yield_day"]


# Task priorities (lower = more urgent). FEED/WATER_CRIT at 0/1 by contract.
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
    # Day 0-2: 7 WHEAT + 16 MELON. Wheat matures day 4-5 to feed the herd.
    if day <= 2 and wheat_plants < 7 and has_wheat_seed:
        return "WHEAT"
    # Melon phase first (day 0-8) so day-10-12 cash funds the land buys.
    if day <= 8 and melon_plants < SEB_MELON_TARGET and has_melon_seed:
        return "MELON"
    # Strawberry mass-plant (Seb: ~42-43 plants).
    if 8 <= day <= 14 and straw_plants < SEB_STRAWBERRY_TARGET and has_straw_seed:
        return "STRAWBERRY"
    if wheat_plants < SEB_WHEAT_TARGET and has_wheat_seed and day <= 26:
        return "WHEAT"
    return None


def _scan_tasks_v8(farm, private, day, hour, seed_choice, inv, sheds, plant_budget):
    """Task scan: strictly seed/budget-limited plant tasks so the scheduler
    never floods plant requests (v7 lesson)."""
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
    sheep_place_budget = min(shed_sheep, max(0, SEB_SHEEP_MAX - placed_sheep))
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
    # Pasture space only for animals already owned + short lookahead.
    herd_planned = min(SEB_PASTURE_SPACE,
                       shed_cows + shed_sheep + placed_cows + placed_sheep + 2)
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
    """One unit's action: lock-in carried animals, then priority task."""
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
                        # A unit standing on the shed may pick up an item.
                        claimed.add((fx, fy))
                        return ["PICKUP", req, 1], None
                    sx, sy = _nearest_shed(fx, fy)
                    steps = [_step_toward_pos(fx, fy, sx, sy)]
                    return (steps if steps else ["PASS"]), None
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
        steps = [_step_toward_pos(fx, fy, sx, sy)]
        return (steps if steps else ["PASS"]), None
    if (fx, fy) == (tx, ty):
        claimed.add((fx, fy))
        return action, None
    steps = [_step_toward_pos(fx, fy, tx, ty)]
    return (steps if steps else ["PASS"]), None


def _sheep_target(farm, prices):
    """Adaptive herd: sheep rise when wool is rich vs milk (Seb Spearman 0.77)."""
    wool = float(prices.get("WOOL", BASE_PRICE["WOOL"]) or BASE_PRICE["WOOL"])
    milk = float(prices.get("MILK", BASE_PRICE["MILK"]) or BASE_PRICE["MILK"])
    gap = wool - milk
    # ambient gap neutral ~0 on the curves; scale so ±$30 moves it fully.
    return int(round(SEB_SHEEP_BASE + max(-3, min(4, gap / 30))))


def agent(obs, configuration=None):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    private = obs.get("private", {}) or {}
    if not farms or player >= len(farms):
        return PASS
    farm = farms[player]
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

    market = []
    sheep_target = _sheep_target(farm, prices)
    wheat_in_shed = shed.get("WHEAT", 0)
    wheat_reserve = animals_placed * 2 + 4
    wheat_need = max(0, wheat_reserve - wheat_in_shed - seeds.get("WHEAT", 0))

    # ------------------------------------------------------------------ market
    # HIRE first — 10-order cap must never starve hiring.
    hire_cost = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89][farm.get("hires_today", 0)] \
        if farm.get("hires_today", 0) < 11 else 999
    plants_total = n_melon + n_wheat + n_straw
    if day <= 2:
        want_hands = min(2, 1 + animals_placed)
    else:
        want_hands = min(SEB_HANDS_TARGET, 3 + animals_placed + plants_total // 6)
    if len(farm.get("hands", [])) < want_hands and money >= hire_cost + 20:
        market.append(["HIRE"])

    # SELL with crash-safe chunking. Fertilizer keeps a working reserve.
    for prod, count in list(shed.items()):
        if prod in ("GOOSE", "COW", "SHEEP") or count <= 0:
            continue
        if prod == "FERTILIZER":
            keep = 10 + plants_total // 4
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

    # Animals — cows first (milk), then adaptive sheep. Feed/care safe gates.
    cow_budget = SEB_COW_TARGET - cows_total
    sheep_count = SEB_SHEEP_MAX if sheep_target > SEB_SHEEP_BASE else SEB_SHEEP_BASE
    sheep_budget = max(0, sheep_count - sheep_total)
    wheat_for_feed = wheat_in_shed + n_wheat * 3
    if day >= 3 and n_pastures > animals_placed:
        if cow_budget > 0 and money >= 400 + 150 and wheat_for_feed >= 2:
            market.append(["BUY_ANIMAL", "COW", 1])
        elif sheep_budget > 0 and money >= 500 + 150 and wheat_for_feed >= 2:
            market.append(["BUY_ANIMAL", "SHEEP", 1])

    # Land: 4-quadrant with SEB day gates + working-capital floor.
    # Financing mirrors Seb's replay signature: when cash is short of the
    # land price, SELL surplus (never WHEAT/FERT — feed + fertilizer reserves)
    # into the SAME market batch BEFORE BUY_LAND. The engine processes the
    # in-batch SELL first, so its proceeds land before the land charge.
    n_extra = len(farm.get("unlocked_quadrants", ["NW"])) - 1
    if n_extra < 3:
        price = LAND_PRICES[n_extra]
        due_day = LAND_DUE_DAY[n_extra]
        if day >= due_day:
            shortfall = price + LAND_CASH_FLOOR[n_extra] - money
            if shortfall > 0:
                for prod, count in list(shed.items()):
                    if shortfall <= 0:
                        break
                    if prod in ("WHEAT", "FERTILIZER", "GOOSE", "COW", "SHEEP") or count <= 0:
                        continue
                    expect_price = float(prices.get(prod, 0) or BASE_PRICE[prod])
                    if expect_price <= 0:
                        continue
                    chunk = count if not CRASH_RISK.get(prod) else min(count, SELL_CHUNK)
                    market.append(["SELL", prod, chunk])
                    shortfall -= chunk * expect_price
            # Land only fires when the financed batch actually covers the
            # price (sells were planned in this same market queue).
            if shortfall <= 0 and money >= price:
                market.append(["BUY_LAND"])

    # Melon seeds.
    n_melon_total = n_melon + seeds.get("MELON", 0)
    if day <= 8 and n_melon_total < SEB_MELON_TARGET:
        want = min(SEB_MELON_TARGET - n_melon_total, 3)
        if money >= 80 * want + 300:
            market.append(["BUY_SEED", "MELON", want])

    # Wheat seeds.
    n_wheat_total = n_wheat + seeds.get("WHEAT", 0)
    if n_wheat_total < SEB_WHEAT_TARGET and money >= 30 and day <= 26:
        market.append(["BUY_SEED", "WHEAT", min(SEB_WHEAT_TARGET - n_wheat_total, 2)])
    if wheat_need > 0 and money >= 25 and wheat_in_shed < 2:
        market.append(["BUY_PRODUCT", "WHEAT", min(wheat_need, 3)])

    # Strawberry seeds.
    n_straw_total = n_straw + seeds.get("STRAWBERRY", 0)
    free_tiles = sum(1 for row in farm["tiles"] for t in row if t is None)
    if 8 <= day <= 14 and hour == 0 and n_straw_total < SEB_STRAWBERRY_TARGET and money >= 400:
        want = min(SEB_STRAWBERRY_TARGET - n_straw_total, free_tiles, 4)
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


def _kaggle_submission_entrypoint(obs):
    return agent(obs, None)