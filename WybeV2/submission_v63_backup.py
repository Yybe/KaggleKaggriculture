"""
VersionWybe v6 — Kaggriculture Agent
=====================================
Engine truth: tiles[y][x], pos=[x,y], board=10x10.
NW (x<5,y<5) always unlocked. Shed center. Shed access: (4,4)NW (5,4)NE (4,5)SW (5,5)SE.
Hands spawn LOCKED shed-adj, vanish EOD. HIRE fib cost. SELL from shed only.

v6 (2026-08-09) — density + row-sweep + premium ramp. The three changes:
1. SCALE: aggressive seed bank (refill every turn money allows; targets sized to
   unlocked tile count), fill every plantable tile, buy land NE d6+ / SW d14+ /
   SE d20+, up to 8 hands late. 4 shed-adjacent staging tiles stay unplanted.
2. ROW-SWEEP PATROL: each unit owns a row (index % n_rows), sweeps horizontally
   along it (nearest-unclaimed-task within the row), only switches rows
   vertically when its row is clean.
3. MID-GAME PREMIUM: from day 10 a share of tiles runs STRAWBERRY (base 120,
   ongoing 2-day cycle from day 10 of growth). MELON is deliberately skipped:
   on engine 1.32.6 no town shop buys it (town-center-only drain) and its sq
   glut curve crashes it to $1.
Sell discipline: wheat flows out daily (log curve absorbs gluts, keeps shed
under the 100 cap), strawberry only at price >= 85 in 4-unit chunks, everything
liquidated from day >= 29 / step >= 710. One-time crops are harvested at their
unfertilized cap (wheat 4 / carrot 3) or AFTER the bonus window fully closes
(age > max_yield_day — never harvest a day early and lose the last +1).

v6.1 (post-mortem fixes):
- HIRE guard removed: sells process before hires in the market queue, so low
  morning cash must not block hiring (a single hire-starvation day previously
  collapsed watering -> weeds -> income).
- Seeds are bought before land (planting never stalls); 500-coin reserve keeps
  land affordable; carrot dropped (wheat strictly dominates); strawberry seeds
  are bought gradually so the day-10 all-in cannot starve the SW purchase.

v6.2 (cash-flow fixes):
- Strawberry is NEVER a planting fallback (wheat always wins ties) and starts
  day 12 with a smaller target (4 + 4/quadrant, cap 16) — the v6.1 fallback
  over-planted 23 STR, drained cash to ~$400 for a week, and stalled wheat.
- STR seed buys rate-limited to 4/turn; reserve scales with cash
  (min(500, max(150, money*0.4))) so low-money days still refill wheat.
- Land gates tightened (SW > 2500, SE > 4000) so land never empties the bank.

v6.3 (labor-ceiling fixes):
- SE quadrant purchase removed: 8 units cannot water 96 tiles (216 action/day
  ceiling), so a 4th quadrant only cratered cash (D20 $105) and spread labor
  too thin. Farm runs NW+NE+SW (72 tiles).
- STR target raised to 6 + 4/quadrant (cap 18) and seed buys start day 10 so
  the premium is fully planted inside the day 12-15 window.
"""

SHED_ACCESS = {(4, 4), (5, 4), (4, 5), (5, 5)}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
# Harvest caps WITHOUT fertilizer: wheat 4, carrot 3, melon 6.
HARVEST_CAP = {"WHEAT": 4, "CARROT": 3, "MELON": 6}
MAX_YIELD_DAY = {"WHEAT": 4, "CARROT": 3, "MELON": 10}


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _hire_cost_n(already, n):
    return sum(_fib(already + i) for i in range(n))


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


def _owned_rows(o):
    rows = []
    for y, row in enumerate(o["tiles"]):
        if any(c != "LOCKED" for c in row):
            rows.append(y)
    return rows


def _count_crops(o, crop):
    n = 0
    for row in o["tiles"]:
        for cell in row:
            if isinstance(cell, dict) and cell.get("kind") == "PLANT" and cell.get("crop") == crop:
                n += 1
    return n


def _str_target(o):
    """Strawberry plant target: premium share, scaled by quadrants."""
    return min(18, 6 + 4 * (len(o["quads"]) - 1))


def _plant_choice(o):
    """Crop for an empty unlocked tile, phase aware. Strawberry is planted
    ONLY inside its target window (never as a fallback — wheat is the cash
    engine and must always win the tie)."""
    seeds, day = o["seeds"], o["day"]
    if day < 15:
        n_str = _count_crops(o, "STRAWBERRY")
        if day >= 12 and n_str < _str_target(o) and int(seeds.get("STRAWBERRY", 0) or 0) > 0:
            return "STRAWBERRY"
    if int(seeds.get("WHEAT", 0) or 0) > 0 and day < 27:
        return "WHEAT"
    if int(seeds.get("TOMATO", 0) or 0) > 0:
        return "TOMATO"
    return None


# =========================================================================
# WORK ASSIGNMENT: task list + row-sweep patrol
# =========================================================================

def _build_tasks(o):
    """Scan all unlocked tiles, produce prioritized tasks.

    Task: (x, y, priority, action). Lower priority = more urgent.
    Priorities: WATER 5, DIG 10, HARVEST 15, CARE 20, FEED 25, PLANT 30.
    """
    tasks = []
    day = o["day"]

    for y, row in enumerate(o["tiles"]):
        for x, cell in enumerate(row):
            if cell == "LOCKED":
                continue
            if cell is None:
                if (x, y) in SHED_ACCESS:
                    continue  # keep shed staging tiles open
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
                    # One-time crop: harvest at cap, when the bonus window is
                    # FULLY closed (age > max_yield_day — the last watering day
                    # still adds +1, so harvest a day late, never early), or
                    # force-harvest everything on day >= 28.
                    if day >= 28 and yld > 0:
                        tasks.append((x, y, 12, ["HARVEST"]))
                    elif yld >= cap or age > MAX_YIELD_DAY.get(crop, 99):
                        tasks.append((x, y, 15, ["HARVEST"]))
                    elif not cell.get("watered_today", False):
                        tasks.append((x, y, 5, ["WATER"]))
                else:
                    # Ongoing crop (strawberry/tomato): water first, harvest
                    # accumulated yield; force-harvest from day 27.
                    if yld > 0 and day >= 27:
                        tasks.append((x, y, 12, ["HARVEST"]))
                    elif not cell.get("watered_today", False):
                        tasks.append((x, y, 5, ["WATER"]))
                    elif yld > 0:
                        tasks.append((x, y, 15, ["HARVEST"]))

            elif kind in ("PASTURE", "COOP"):
                if "animal" in cell:
                    if not cell.get("fed_today", False):
                        tasks.append((x, y, 25, ["FEED"]))
                    elif not cell.get("cared_today", False):
                        tasks.append((x, y, 20, ["CARE"]))
                    elif int(cell.get("yield_units", 0) or 0) > 0:
                        tasks.append((x, y, 22, ["HARVEST"]))
                    elif cell.get("fertilizer_available", False):
                        tasks.append((x, y, 28, ["COLLECT_FERTILIZER"]))

    return tasks


def _assign_unit(o, tasks, assigned, ux, uy, inv, unit_index, n_units):
    """Decide one action for a unit.

    Row-sweep patrol: the unit prefers its own row (unit_index % n_rows) and
    sweeps horizontally through the nearest unclaimed task there. Only when
    its row is clean does it move vertically toward the busiest other row.
    """
    tile = _t(o, ux, uy)

    # 1. Spawned on a LOCKED tile -> exit into unlocked land.
    if tile == "LOCKED":
        if ux >= 5:
            return ["WEST"]
        if uy >= 5:
            return ["NORTH"]
        return _mv(ux, uy, 2, 2) or ["PASS"]

    def _ok(t):
        tx, ty, pri, act = t
        if (tx, ty) in assigned:
            return False
        if act[0] == "PLANT" and int(o["seeds"].get(act[1], 0) or 0) <= 0:
            return False
        if act[0] == "FEED" and inv.get("WHEAT", 0) <= 0:
            return False
        return True

    # 2. Standing on an unclaimed task tile -> act now.
    for t in tasks:
        if t[0] == ux and t[1] == uy and _ok(t):
            assigned.add((t[0], t[1]))
            return t[3]

    rows = _owned_rows(o)
    pref_y = rows[unit_index % len(rows)] if rows else uy

    # 3. Row sweep: nearest unclaimed task in my preferred row.
    row_tasks = [t for t in tasks if t[1] == pref_y and _ok(t)]
    if row_tasks:
        t = min(row_tasks, key=lambda t: abs(t[0] - ux) + t[2])
        assigned.add((t[0], t[1]))
        return _mv(ux, uy, t[0], t[1]) or ["PASS"]

    # 4. Own row clean -> busiest other row (most eligible tasks).
    counts = {}
    for t in tasks:
        if _ok(t):
            counts[t[1]] = counts.get(t[1], 0) + 1
    if counts:
        best_y = max(counts, key=lambda y: (counts[y], -abs(y - uy)))
        best = [t for t in tasks if t[1] == best_y and _ok(t)]
        if best:
            t = min(best, key=lambda t: abs(t[0] - ux) + t[2])
            assigned.add((t[0], t[1]))
            return _mv(ux, uy, t[0], t[1]) or ["PASS"]

    # 5. Nothing to do.
    return ["PASS"]


# =========================================================================
# MARKET
# =========================================================================

def _sells(o, max_n):
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

    # WHEAT: always flow out — frees shed space; the log curve absorbs gluts.
    q = int(shed.get("WHEAT", 0) or 0)
    if q > 0 and len(orders) < max_n:
        orders.append(["SELL", "WHEAT", q])

    # CARROT: sell when price healthy.
    q = int(shed.get("CARROT", 0) or 0)
    if q > 0 and int(prices.get("CARROT", 35) or 35) >= 28 and len(orders) < max_n:
        orders.append(["SELL", "CARROT", min(q, 8)])

    # STRAWBERRY: hold for premium price, drip 4-unit chunks.
    if day >= 12:
        q = int(shed.get("STRAWBERRY", 0) or 0)
        px = int(prices.get("STRAWBERRY", 120) or 120)
        while q > 0 and len(orders) < max_n and px >= 85:
            c = min(q, 4)
            orders.append(["SELL", "STRAWBERRY", c])
            q -= c

    # FERTILIZER (animal byproduct): sell when price healthy.
    q = int(shed.get("FERTILIZER", 0) or 0)
    if q > 0 and int(prices.get("FERTILIZER", 100) or 100) >= 60 and len(orders) < max_n:
        orders.append(["SELL", "FERTILIZER", min(q, 4)])

    # MILK / WOOL (animal products): premium gates.
    if day >= 14:
        q = int(shed.get("MILK", 0) or 0)
        if q > 0 and int(prices.get("MILK", 160) or 160) >= 110 and len(orders) < max_n:
            orders.append(["SELL", "MILK", min(q, 4)])
        q = int(shed.get("WOOL", 0) or 0)
        if q > 0 and int(prices.get("WOOL", 200) or 200) >= 140 and len(orders) < max_n:
            orders.append(["SELL", "WOOL", min(q, 4)])

    return orders


def _buys(o, max_n):
    money, day, hour = o["money"], o["day"], o["hour"]
    hires, quads, seeds = o["hires"], o["quads"], o["seeds"]
    orders = []

    # OPENER: 3 hires + 22 wheat seeds (cash -> ~2776).
    if o["step"] == 0:
        return [["HIRE"], ["HIRE"], ["HIRE"], ["BUY_SEED", "WHEAT", 22]][:max_n]

    # HIRE every morning. NO cash guard: sells are processed before hires in
    # the market queue, so today's harvests fund this morning's hires; the
    # engine silently drops any order that is still unaffordable.
    if hour == 0:
        target = 3 + (day >= 4) + (day >= 8) + (day >= 12) + (day >= 16)
        want = target - hires
        for _ in range(min(want, max_n - len(orders))):
            orders.append(["HIRE"])

    # BUY SEEDS: refill to targets sized to unlocked tiles. Seeds come before
    # land so planting never stalls. Reserve scales with cash so a low-money
    # period still refills wheat instead of locking up every coin.
    nq = len(quads)
    str_tgt = _str_target(o)
    wht_tgt = max(15, 21 * nq - 4 - str_tgt)
    reserve = min(500, max(150, money * 0.4))
    if day < 6:
        targets = {"WHEAT": max(20, wht_tgt)}
    elif day < 10:
        targets = {"WHEAT": wht_tgt}
    else:
        targets = {"WHEAT": wht_tgt, "STRAWBERRY": str_tgt}

    for crop, tgt in targets.items():
        if len(orders) >= max_n:
            break
        have = int(seeds.get(crop, 0) or 0)
        if have >= tgt:
            continue
        afford = max(0, int((money - reserve) // SEED_COST[crop]))
        # Strawberry seeds are 10x wheat: rate-limit to 4/turn so a single
        # turn cannot drain the cash needed for land or wheat refills.
        cap = 4 if crop == "STRAWBERRY" else 99
        n = min(tgt - have, afford, cap, max_n - len(orders))
        if n > 0:
            orders.append(["BUY_SEED", crop, n])

    # BUY LAND (after seeds — safe money above the reserve). SE stays locked:
    # the 9th-10th units cannot water 96 tiles (216 action/day ceiling), so a
    # 4th quadrant only starves cash and spreads labor too thin.
    if nq < 2 and money > 1100 and day >= 6 and len(orders) < max_n:
        orders.append(["BUY_LAND"])
    elif nq < 3 and money > 2600 and day >= 14 and len(orders) < max_n:
        orders.append(["BUY_LAND"])

    return orders[:max_n]


# =========================================================================
# MAIN
# =========================================================================

def agent(obs, configuration=None):
    try:
        o = _obs(obs)
        step = o["step"]
        tasks = _build_tasks(o)
        assigned = set()
        n_units = 1 + len(o["hands"])

        # Farmer
        fx, fy = o["farmer"]
        finv = o["invs"][0] if o["invs"] else {}
        if step == 0:
            # Seeds only land after the market phase of this turn; move toward
            # the first plant site so planting can start on step 1.
            farmer_action = _mv(fx, fy, 3, 3) or ["PASS"]
        else:
            farmer_action = _assign_unit(o, tasks, assigned, fx, fy, finv, 0, n_units)

        # Hands
        hand_actions = []
        for i, hp in enumerate(o["hands"]):
            inv = o["invs"][i + 1] if (i + 1) < len(o["invs"]) else {}
            hand_actions.append(_assign_unit(o, tasks, assigned, hp[0], hp[1], inv,
                                             i + 1, n_units))

        # Market
        if step == 0:
            market = _buys(o, 10)
        else:
            s = _sells(o, 10 if (step >= 710 or o["day"] >= 29) else 6)
            market = s + _buys(o, 10 - len(s))

        return {"farmer": farmer_action, "hands": hand_actions, "market": market[:10]}
    except Exception:
        h = obs.get("farms", [{}])[obs.get("player", 0)].get("hands", []) or []
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in h], "market": []}
