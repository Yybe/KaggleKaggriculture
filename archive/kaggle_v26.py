"""v26: v23 + idle-turn fill + late-game high-value SELL top-up ("capselllate").

Learned from head-to-head vs v23 (8/8 wins in H2H, mirror deltas misleading):
the battle is asymmetric — extra units sold late depress the SHARED market
price curve, which hurts v23's fixed sell plan (big dumps of WOOL/MILK/
STRAWBERRY at steps 624-696) more than it hurts this agent:

  1. Idle-turn fill (proven neutral in mirrors v26b, keeps v23's schedule
     identical because fills are schedule-synced no-ops):
       - HARVEST non-ongoing (WHEAT/CARROT/MELON) only at max yield;
       - HARVEST ongoing (TOMATO/STRAWBERRY) + animals whenever yield > 0;
       - WATER unwatered PLANT (strictly non-negative).
  2. From step >= 19*24=456 (final 10 days) ONLY, and ONLY for high-value
     products (STRAWBERRY 120 / MILK 160 / WOOL 200): bump each v23 SELL
     order by at most +2 units when shed holds more than the planned qty.
     Low-value volume (WHEAT 25 / FERTILIZER 100) is NEVER bumped: selling
     extra cheap units tanks the price curve for less than it's worth.

Nothing else changes; the market queue is v23's (reordered by v23's own
scoring inside the base call).
"""
import importlib.util
import os
import sys

_BASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kaggle_v23.py")
_spec = importlib.util.spec_from_file_location("_kaggle_v23_fillsource", _BASE_FILE)
_v23 = importlib.util.module_from_spec(_spec)
sys.modules["_kaggle_v23_fillsource"] = _v23
_spec.loader.exec_module(_v23)

_NON_ONGOING_MAX = {"WHEAT": 6, "CARROT": 4, "MELON": 6}
_ONGOING = {"TOMATO", "STRAWBERRY"}
_ANIMAL_MAX = {"GOOSE": 4, "COW": 6, "SHEEP": 6}
_HIGH_VALUE = {"STRAWBERRY", "MILK", "WOOL"}
_LATEFILL_STEP = 19 * 24  # final 10 days
_BUMP_CAP = 2


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (list(_get(farm, "tiles", []) or []))[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _fill(action, obs):
    seat = _seat(obs)
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    units = [action["farmer"], *action["hands"]]

    for index, (position, planned) in enumerate(zip(positions, units)):
        if not planned or planned[0] != "PASS":
            continue
        tile = _tile_at(farm, position)
        if not isinstance(tile, dict):
            continue

        if tile.get("kind") == "PLANT":
            crop = tile.get("crop")
            if crop in _NON_ONGOING_MAX:
                cap = _NON_ONGOING_MAX[crop]
                if int(tile.get("yield_units", 0) or 0) >= cap:
                    units[index] = ["HARVEST"]
                elif not tile.get("watered_today", False):
                    units[index] = ["WATER"]
            elif crop in _ONGOING:
                if int(tile.get("yield_units", 0) or 0) > 0:
                    units[index] = ["HARVEST"]
        elif "animal" in tile:
            animal = tile.get("animal")
            cap = _ANIMAL_MAX.get(animal)
            if cap and int(tile.get("yield_units", 0) or 0) > 0:
                units[index] = ["HARVEST"]

    action["farmer"] = units[0] if units else ["PASS"]
    action["hands"] = units[1:]
    return action


def _topup(action, obs):
    """Late-game high-value SELL top-up (+2 cap)."""
    step = int(_get(obs, "step", 0) or 0)
    if step < _LATEFILL_STEP:
        return action
    seat = _seat(obs)
    private = _get(obs, "private", {}) or {}
    shed = dict(private.get("shed") or {})
    market = list(action.get("market") or [])
    new_market = []
    for order in market:
        if (isinstance(order, (list, tuple)) and len(order) >= 3
                and order[0] == "SELL"):
            item = str(order[1])
            if item in _HIGH_VALUE:
                try:
                    qty = int(order[2])
                except (TypeError, ValueError):
                    qty = 0
                available = int(shed.get(item, 0) or 0)
                if available > qty:
                    order = [order[0], order[1], qty + min(_BUMP_CAP, available - qty)]
        new_market.append(list(order))
    action["market"] = new_market
    return action


def agent(obs, configuration=None):
    action = _v23.agent(obs, configuration)
    action = {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }
    action = _fill(action, obs)
    action = _topup(action, obs)
    return action


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)