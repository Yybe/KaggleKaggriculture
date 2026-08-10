"""
WybeV2 v7 "Wheat-Bank" — Kaggriculture Agent
=============================================
Reverse-engineered from HealthStone (leaderboard #2, 70% WR, avg 94.5K, beats
SEB 8/9 H2H). Engine truth: tiles[y][x], pos=[x,y], board=10x10. Shed center.
Shed access: (4,4)NW (5,4)NE (4,5)SW (5,5)SE. Hands spawn LOCKED shed-adj,
vanish EOD. HIRE fib cost. SELL from shed only.

THE DECODED MECHANISM (from 30 HealthStone replays):
- Wheat has a LOG price curve -> absorbs late-game gluts (stays ~$18-20).
- Premium dumps (STR/MILK/WOOL) SELF-CRASH the shared curve (linear/sq -> $1).
- HealthStone wins by: sheep-first wool (D6), a wheat BANK dumped D26-29
  (310 units), STR wave mid-game (~38 plants D15), and NEVER buying the 4th
  quadrant (3 quads: NW+NE+SW). 14.4 animals, 281 total hires.
- v6.3 died (20K avg) because it had NO animal pipeline. v7 adds the full
  animal loop: BUY_ANIMAL -> BUILD_PASTURE -> PICKUP (shed) -> PLACE -> FEED
  (wheat) -> CARE -> HARVEST milk/wool -> COLLECT_FERTILIZER.

PHASE PLAN (HS-aligned):
  D0    : 3 hires, 4 sheep + 1 cow, 5 melon + 5 wheat + 1 carrot (all-in ~$14).
          Build 5 pastures, place animals, feed.
  D1-4  : Feed/care animals. Fertilizer drips out. Small wheat feed buys.
  D5-9  : First wheat harvest + WOOL sells. Cows ramp to ~9. NE land D7.
  D10   : MELON wave (24). STR expansion starts. SW land D11.
  D10-15: STR -> ~38 plants. Cash explodes. Milk/wool/fert steady.
  D15-22: STR harvest cycles. Wheat bank builds. Hire 10-13/day.
  D23-29: HOLD wheat, dump the BANK D26-29 (D28 peak). Liquidate all >=710.

SELL DISCIPLINE:
  WHEAT: sell surplus above feed buffer all game; hold then dump late.
  FERT : drip 4 when price >= 60.   STR : drip 4 when >= 85.
  MILK : drip 4 when >= 110.        WOOL: drip 4 when >= 140.
  MELON: sell at D10 wave + D20 wave.  Endgame: sell EVERYTHING >= 710.
"""

SHED_ACCESS = {(4, 4), (5, 4), (4, 5), (5, 5)}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
HARVEST_CAP = {"WHEAT": 4, "CARROT": 3, "MELON": 6}
MAX_YIELD_DAY = {"WHEAT": 4, "CARROT": 3, "MELON": 10}
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
ANIMAL_PRODUCT = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _obs(obs):
    s = obs.get("player", 0)
    f = obs.get("farms", [{}])[s]
    p = obs.get("private", {}) or {}
    m = obs.get("market", {}) or {}
    return dict(
        step=obs.get("step", 0), day=obs.get("day", 0), hour=obs.get("hour", 0),
        money=float(f.get("money", 0) or 0),
        tiles=f.get("tiles", []), farmer=f.get("farmer", [4, 4]),
        hands=f.get("hands", []) or [],
        quads=f.get("unlocked_quadrants", ["NW"]),
        hires=int(f.get("hires_today", 0) or 0),
        shed=dict(p.get("shed", {}) or {}),
        seeds=dict(p.get("seeds", {}) or {}),
        invs=p.get("inventories", [{}]),
        prices=m.get("prices", {}),
    )


def _t(o, x, y):
    t = o["tiles"]
    if 0 <= y < len(t) and 0 <= x < len(t[y]):
        return t[y][x]
    return "LOCKED"


def _mv(sx, sy, dx, dy):
    ddx, ddy = dx - sx, dy - sy
    if ddx == 0 and ddy == 0:
        return None
    if abs(ddx) >= abs(ddy):
        return ["EAST"] if ddx > 0 else ["WEST"]
    return ["SOUTH"] if ddy > 0 else ["NORTH"]


def _near_shed(x, y):
    return (x, y) in SHED_ACCESS


def _shed_unlocked(o, x, y):
    """A shed-adjacent cell is usable only if its quadrant is unlocked."""
    if (x, y) not in SHED_ACCESS:
        return False
    q = ("NW" if x < 5 and y < 5 else
         "NE" if x >= 5 and y < 5 else
         "SW" if x < 5 and y >= 5 else "SE")
    return q in o["quads"]


def _count(o, kind, crop=None):
    n = 0
    for row in o["tiles"]:
        for cell in row:
            if not isinstance(cell, dict):
                continue
            if cell.get("kind") == kind:
                if crop is None or cell.get("crop") == crop:
                    n += 1
    return n


def _count_animal_type(o, animal):
    n = 0
    for row in o["tiles"]:
        for cell in row:
            if isinstance(cell, dict) and cell.get("kind") in ("PASTURE", "COOP") \
                    and cell.get("animal") == animal:
                n += 1
    return n


def _empty_tiles(o):
    out = []
    for y, row in enumerate(o["tiles"]):
        for x, cell in enumerate(row):
            if cell is None and (x, y) not in SHED_ACCESS:
                out.append((x, y))
    return out


def _shed_animals(o):
    shed = o["shed"]
    return {a: int(shed.get(a, 0) or 0) for a in ("COW", "SHEEP", "GOOSE") if int(shed.get(a, 0) or 0) > 0}


def _unplaced_animals(o):
    """Animals still waiting in the shed (bought but not placed on a tile).
    NOTE (v7 bugfix): the old code had `placed[a] <= 0`, which blocked the 2nd+
    animal of any type from ever being placed (once 1 sheep was placed, all
    later sheep rotted in the shed, kept want_pasture true forever, and the
    farm became 49 pastures + 0 crops). Animals in the shed are BY DEFINITION
    unplaced -- the placed count is irrelevant here."""
    shed = o["shed"]
    return {a: int(shed.get(a, 0) or 0) for a in ("COW", "SHEEP", "GOOSE")
            if int(shed.get(a, 0) or 0) > 0}


def _animal_pending_place(o):
    """Unplaced animals in shed AND empty matching structure on field."""
    up = _unplaced_animals(o)
    out = {}
    for a in up:
        struct = "PASTURE" if a in ("COW", "SHEEP") else "COOP"
        empty = 0
        for row in o["tiles"]:
            for cell in row:
                if isinstance(cell, dict) and cell.get("kind") == struct and cell.get("animal") is None:
                    empty += 1
        if empty > 0:
            out[a] = min(up[a], empty)
    return out


def _str_target(o):
    """HS runs ~38 STR plants by D15. Cap 38, scale by quads."""
    return min(38, 6 + 6 * (len(o["quads"]) - 1) + 8 * (o["day"] >= 10))


def _wheat_target(o):
    """Wheat bank: ramps to ~38 plants by D25, 3 quads, minus STR/melon tiles."""
    nq = len(o["quads"])
    if o["day"] < 8:
        return max(10, 8 * nq)
    if o["day"] < 15:
        return max(14, 12 * nq)
    if o["day"] < 22:
        return max(20, 18 * nq)
    return max(30, 26 * nq)


def _melons_wanted(o):
    if o["day"] < 3:
        return 5
    if o["day"] < 11:
        return 5
    if o["day"] < 18:
        return 8
    return 0


def _plant_choice(o):
    """Phase-aware crop choice. Wheat is the cash engine + bank; STR the
    mid-game premium. Strawberry never as a fallback. MELON is deliberately
    skipped: on engine 1.32.6 no town shop buys it (town-center-only drain)
    and its sq glut curve crashes it to $1 (v6.3 evidence)."""
    seeds, day = o["seeds"], o["day"]
    n_str = _count(o, "PLANT", "STRAWBERRY")
    if 10 <= day < 22 and n_str < _str_target(o) and int(seeds.get("STRAWBERRY", 0) or 0) > 0:
        return "STRAWBERRY"
    if int(seeds.get("WHEAT", 0) or 0) > 0 and day < 28:
        n_wht = _count(o, "PLANT", "WHEAT")
        if n_wht < _wheat_target(o):
            return "WHEAT"
    return None


# =========================================================================
# TASK ENGINE: crop/animals unified with the v6.3 row-sweep patrol
# =========================================================================

def _build_tasks(o):
    tasks = []
    day = o["day"]
    animals_unfed = []

    for y, row in enumerate(o["tiles"]):
        for x, cell in enumerate(row):
            if cell == "LOCKED":
                continue
            if cell is None:
                if (x, y) in SHED_ACCESS:
                    continue
                # Pasture build: ONLY while shed animals need a home. With
                # Bug A/B fixed (animals CAN be placed now), shed_animals
                # drops as animals get placed, so this self-terminates instead
                # of the old 49-pasture disease. Early fleet ~5 for the D0
                # opening buys. (A stricter cap tying pasture to pending
                # animals was tested and REGRESSED 880 -> 29: with fewer
                # pastures the crop engine overshoots, runs out of seeds/money
                # mid-game, weeds explode -- revert kept.)
                shed_animals = sum(_shed_animals(o).values())
                want_pasture = shed_animals > 0 or (
                    day < 3 and _count(o, "PASTURE") + _count(o, "COOP") < 5)
                if want_pasture and day < 25:
                    tasks.append((x, y, 18, ["BUILD_PASTURE"]))
                    continue
                crop = _plant_choice(o)
                if crop:
                    tasks.append((x, y, 30, ["PLANT", crop]))
                continue
            if not isinstance(cell, dict):
                continue

            kind = cell.get("kind", "")
            if kind == "WEED":
                tasks.append((x, y, 10, ["DIG"]))
            elif kind == "PLANT":
                crop = cell.get("crop", "")
                yld = int(cell.get("yield_units", 0) or 0)
                age = day - int(cell.get("planted_day", day))
                cap = HARVEST_CAP.get(crop)
                if cap is not None:
                    if day >= 28 and yld > 0:
                        tasks.append((x, y, 12, ["HARVEST"]))
                    elif yld >= cap or age > MAX_YIELD_DAY.get(crop, 99):
                        tasks.append((x, y, 15, ["HARVEST"]))
                    elif not cell.get("watered_today", False):
                        tasks.append((x, y, 5, ["WATER"]))
                else:
                    if yld > 0 and day >= 27:
                        tasks.append((x, y, 12, ["HARVEST"]))
                    elif not cell.get("watered_today", False):
                        tasks.append((x, y, 5, ["WATER"]))
                    elif yld > 0:
                        tasks.append((x, y, 15, ["HARVEST"]))
            elif kind in ("PASTURE", "COOP"):
                animal = cell.get("animal")
                if animal:
                    if not cell.get("fed_today", False):
                        animals_unfed.append((x, y))
                        tasks.append((x, y, 22, ["FEED"]))
                    elif not cell.get("cared_today", False):
                        tasks.append((x, y, 20, ["CARE"]))
                    elif int(cell.get("yield_units", 0) or 0) > 0:
                        tasks.append((x, y, 24, ["HARVEST"]))
                    elif cell.get("fertilizer_available", False):
                        tasks.append((x, y, 26, ["COLLECT_FERTILIZER"]))
                else:
                    # Empty pasture with an unplaced matching animal -> place.
                    for a, n in _animal_pending_place(o).items():
                        struct = "PASTURE" if a in ("COW", "SHEEP") else "COOP"
                        if kind == struct and n > 0:
                            tasks.append((x, y, 16, ["PLACE", a]))
                            break

    # Shed logistics: PICKUP wheat feed when animals are unfed and units carry
    # no wheat; PICKUP animals when there is an empty structure waiting.
    shed_cells = [c for c in sorted(SHED_ACCESS) if _shed_unlocked(o, *c)]
    if animals_unfed:
        tasks.append((None, None, 3, ["PICKUP", "WHEAT", 20]))
    for a in _animal_pending_place(o):
        tasks.append((None, None, 4, ["PICKUP", a, 1]))
    return tasks, animals_unfed


def _pickup_site(o, item):
    """Best shed-adjacent unlocked cell for a PICKUP of `item`."""
    best, best_dist = None, 10 ** 9
    for c in sorted(SHED_ACCESS):
        if _shed_unlocked(o, *c):
            return c  # first unlocked is fine (all unlocked by D7+)
    return (4, 4)


def _assign_unit(o, tasks, assigned, ux, uy, inv, unit_index, n_units, animals_unfed):
    tile = _t(o, ux, uy)

    # 1. Spawned on a LOCKED tile -> exit into unlocked land.
    if tile == "LOCKED":
        if ux >= 5:
            return ["WEST"]
        if uy >= 5:
            return ["NORTH"]
        return _mv(ux, uy, 3, 3) or ["PASS"]

    def _ok(t):
        tx, ty, pri, act = t
        if ty is not None and (tx, ty) in assigned:
            return False
        if act[0] == "PLANT" and int(o["seeds"].get(act[1], 0) or 0) <= 0:
            return False
        if act[0] == "FEED" and inv.get("WHEAT", 0) <= 0:
            return False
        if act[0] == "PLACE" and inv.get(act[1], 0) <= 0:
            return False
        if act[0] == "PICKUP" and ty is None:
            # Only pick up when we are AT the shed cell.
            if not _near_shed(ux, uy):
                return False
        if act[0] == "PICKUP" and ty is None and act[1] in ("COW", "SHEEP", "GOOSE"):
            # only claim if an empty matching structure actually exists
            if act[1] not in _animal_pending_place(o):
                return False
        if act[0] == "PICKUP" and ty is None and act[1] == "WHEAT" and not animals_unfed:
            return False
        return True

    # 2. Standing on an unclaimed task tile -> act now.
    for t in tasks:
        if t[1] is not None and t[0] == ux and t[1] == uy and _ok(t):
            assigned.add((t[0], t[1]))
            return t[3]

    # 2b. Shed logistics: if we are at a shed cell and a PICKUP task exists.
    for t in tasks:
        if t[1] is None and _ok(t):
            act = t[3]
            if act[0] == "PICKUP" and _near_shed(ux, uy):
                return act

    # 2c. Carry to structure: standing on empty pasture carrying the animal.
    if tile and isinstance(tile, dict) and tile.get("kind") in ("PASTURE", "COOP") \
            and tile.get("animal") is None:
        for a in ("COW", "SHEEP", "GOOSE"):
            if inv.get(a, 0) > 0:
                struct = "PASTURE" if a in ("COW", "SHEEP") else "COOP"
                if tile.get("kind") == struct:
                    return ["PLACE", a]

    # 2d. Carrying an animal but NOT on an empty matching structure -> walk
    # to the nearest empty pasture/coop of the right kind (Bug B fix: units
    # used to pick up an animal and then wander off to crop rows, never
    # placing it -- while shed animals stacked up and kept want_pasture true).
    carried = [a for a in ("COW", "SHEEP", "GOOSE") if inv.get(a, 0) > 0]
    if carried:
        a = carried[0]
        struct = "PASTURE" if a in ("COW", "SHEEP") else "COOP"
        best, best_d = None, 10 ** 9
        for y, row in enumerate(o["tiles"]):
            for x, cell in enumerate(row):
                if isinstance(cell, dict) and cell.get("kind") == struct \
                        and cell.get("animal") is None:
                    d = abs(x - ux) + abs(y - uy)
                    if d < best_d:
                        best_d = d
                        best = (x, y)
        if best:
            return _mv(ux, uy, best[0], best[1]) or ["PASS"]

    rows = [y for y, r in enumerate(o["tiles"]) if any(c != "LOCKED" for c in r)]
    pref_y = rows[unit_index % len(rows)] if rows else uy

    # 3. Row sweep: nearest unclaimed task in my preferred row.
    row_tasks = [t for t in tasks if t[1] is not None and t[1] == pref_y and _ok(t)]
    if row_tasks:
        t = min(row_tasks, key=lambda t: abs(t[0] - ux) + t[2])
        assigned.add((t[0], t[1]))
        return _mv(ux, uy, t[0], t[1]) or ["PASS"]

    # 4. Own row clean -> busiest other row.
    counts = {}
    for t in tasks:
        # Only real row indices (int) participate in row-count balancing;
        # shed-logistics tasks use t[1] is None and never reach here.
        if isinstance(t[1], int) and _ok(t):
            counts[t[1]] = counts.get(t[1], 0) + 1
    if counts:
        best_y = max(counts, key=lambda y: (counts[y], -abs(y - uy)))
        best = [t for t in tasks if t[1] == best_y and _ok(t)]
        if best:
            t = min(best, key=lambda t: abs(t[0] - ux) + t[2])
            assigned.add((t[0], t[1]))
            return _mv(ux, uy, t[0], t[1]) or ["PASS"]

    # 5. Need wheat for feeding? Walk to shed to pick up.
    if animals_unfed and inv.get("WHEAT", 0) <= 0:
        sx, sy = _pickup_site(o, "WHEAT")
        if not _near_shed(ux, uy):
            return _mv(ux, uy, sx, sy) or ["PASS"]

    # 5b. Unplaced animals waiting in shed + empty structures on the field
    # -> walk to the shed and pick one up (Bug B fix: no task ever routed
    # units back to the shed, so animals were bought but never placed).
    if _animal_pending_place(o):
        sx, sy = _pickup_site(o, "ANY")
        if not _near_shed(ux, uy):
            return _mv(ux, uy, sx, sy) or ["PASS"]
        for t in tasks:
            if t[1] is None and _ok(t) and t[3][0] == "PICKUP" \
                    and t[3][1] in ("COW", "SHEEP", "GOOSE"):
                return t[3]

    return ["PASS"]


# =========================================================================
# MARKET
# =========================================================================

def _sell_orders(o, max_n):
    shed, day, step, prices = o["shed"], o["day"], o["step"], o["prices"]
    orders = []
    endgame = step >= 710 or day >= 29

    if endgame:
        for item in ("STRAWBERRY", "MELON", "MILK", "WOOL", "WHEAT", "CARROT",
                     "TOMATO", "EGG", "FERTILIZER"):
            if len(orders) >= max_n:
                break
            q = int(shed.get(item, 0) or 0)
            if q > 0:
                orders.append(["SELL", item, q])
        return orders

    def _drip(item, gate, chunk):
        q = int(shed.get(item, 0) or 0)
        px = int(prices.get(item, 0) or 0)
        while q > 0 and len(orders) < max_n and px >= gate:
            c = min(q, chunk)
            orders.append(["SELL", item, c])
            q -= c

    # WHEAT: sell above the feed buffer (12) all game; hold the bank late.
    q = int(shed.get("WHEAT", 0) or 0)
    feed_need = sum(1 for row in o["tiles"] for cell in row
                    if isinstance(cell, dict) and cell.get("kind") in ("PASTURE", "COOP")
                    and cell.get("animal"))
    buffer = max(12, feed_need * 2)
    if q > buffer and len(orders) < max_n:
        orders.append(["SELL", "WHEAT", q - buffer])

    # MELON: sell at the D10 and D20 waves (melon price crashes late).
    if 9 <= day <= 12 or 19 <= day <= 22:
        _drip("MELON", 150, 12)

    # FERTILIZER: steady drip (animal byproduct).
    _drip("FERTILIZER", 60, 4)

    # STRAWBERRY: premium gate.
    _drip("STRAWBERRY", 85, 4)

    # MILK / WOOL.
    _drip("MILK", 110, 4)
    _drip("WOOL", 140, 4)

    return orders[:max_n]


def _buy_orders(o, max_n):
    money, day, hour = o["money"], o["day"], o["hour"]
    hires, quads, seeds = o["hires"], o["quads"], o["seeds"]
    orders = []

    # OPENING (step 0) — v6.3-proven engine + a SMALL sheep stake (2, not 4+1):
    # 4 sheep + 1 cow burned $2400/3000, left ~$146, and the feed purchases
    # drained the rest while crops starved of labor -> animals escaped, 0 income.
    # Keep the D6 wool promise with 2 sheep; fund the wheat engine.
    if o["step"] == 0:
        return [["HIRE"], ["HIRE"], ["HIRE"],
                ["BUY_ANIMAL", "SHEEP", 2],
                ["BUY_SEED", "WHEAT", 5], ["BUY_SEED", "CARROT", 1]][:max_n]

    # HIRE every morning (no cash guard: sells process first in the queue).
    if hour == 0:
        if day <= 1:
            target = 3
        elif day <= 4:
            target = 6
        elif day <= 9:
            target = 8
        elif day <= 15:
            target = 10
        else:
            target = 13
        want = target - hires
        for _ in range(min(want, max_n - len(orders))):
            orders.append(["HIRE"])

    # ANIMALS: ramp cows D5-9 (HS reaches ~9 cows, ~5 sheep).
    n_cow = _count_animal_type(o, "COW") + int(o["shed"].get("COW", 0) or 0)
    n_sheep = _count_animal_type(o, "SHEEP") + int(o["shed"].get("SHEEP", 0) or 0)
    cow_target = 2 if day < 5 else (5 if day < 8 else 8)
    if day >= 5 and n_cow < cow_target and money > 1200 and len(orders) < max_n:
        orders.append(["BUY_ANIMAL", "COW", 1])
    if n_sheep < 4 and money > 1500 and len(orders) < max_n:
        orders.append(["BUY_ANIMAL", "SHEEP", 1])

    # FEED: buy wheat when shed buffer runs low (animals eat it).
    feed_need = sum(1 for row in o["tiles"] for cell in row
                    if isinstance(cell, dict) and cell.get("kind") in ("PASTURE", "COOP")
                    and cell.get("animal"))
    shed_wheat = int(o["shed"].get("WHEAT", 0) or 0)
    if feed_need > 0 and shed_wheat < feed_need * 2 and money > 100 and len(orders) < max_n:
        want = min(feed_need * 3 - shed_wheat, 20)
        afford = max(0, int((money - 60) // 25))
        n = min(want, afford, 20)
        if n > 0:
            orders.append(["BUY_PRODUCT", "WHEAT", n])

    # SEEDS: wheat bank + STR wave + melon waves.
    nq = len(quads)
    str_tgt = _str_target(o)
    wht_tgt = _wheat_target(o)
    reserve = min(500, max(150, money * 0.35))
    targets = {"WHEAT": wht_tgt}
    if 10 <= day < 22:
        targets["STRAWBERRY"] = str_tgt
    for crop, tgt in targets.items():
        if len(orders) >= max_n:
            break
        have = int(seeds.get(crop, 0) or 0)
        if have >= tgt:
            continue
        afford = max(0, int((money - reserve) // SEED_COST[crop]))
        cap = 4 if crop == "STRAWBERRY" else 99
        n = min(tgt - have, afford, cap, max_n - len(orders))
        if n > 0:
            orders.append(["BUY_SEED", crop, n])

    # BUY LAND: NE D7, SW D11, NEVER SE (HS never buys the 4th quadrant).
    if nq < 2 and money > 1100 and day >= 6 and len(orders) < max_n:
        orders.append(["BUY_LAND"])
    elif nq < 3 and money > 2300 and day >= 10 and len(orders) < max_n:
        orders.append(["BUY_LAND"])

    return orders[:max_n]


# =========================================================================
# MAIN
# =========================================================================

def agent(obs, configuration=None):
    try:
        o = _obs(obs)
        step = o["step"]
        tasks, animals_unfed = _build_tasks(o)
        assigned = set()
        n_units = 1 + len(o["hands"])

        fx, fy = o["farmer"]
        finv = o["invs"][0] if o["invs"] else {}
        if step == 0:
            # Market animals land in the shed AFTER this turn; move toward the
            # shed so PICKUP can start on step 1 (HS farmer builds pasture first).
            farmer_action = ["BUILD_PASTURE"] if _t(o, fx, fy) is None else \
                (_mv(fx, fy, 3, 3) or ["PASS"])
        else:
            farmer_action = _assign_unit(o, tasks, assigned, fx, fy, finv, 0, n_units, animals_unfed)

        hand_actions = []
        for i, hp in enumerate(o["hands"]):
            inv = o["invs"][i + 1] if (i + 1) < len(o["invs"]) else {}
            hand_actions.append(_assign_unit(o, tasks, assigned, hp[0], hp[1], inv,
                                             i + 1, n_units, animals_unfed))

        if step == 0:
            market = _buy_orders(o, 10)
        else:
            s = _sell_orders(o, 10 if (step >= 710 or o["day"] >= 29) else 6)
            market = s + _buy_orders(o, 10 - len(s))

        return {"farmer": farmer_action, "hands": hand_actions, "market": market[:10]}
    except Exception:
        h = obs.get("farms", [{}])[obs.get("player", 0)].get("hands", []) or []
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in h], "market": []}
