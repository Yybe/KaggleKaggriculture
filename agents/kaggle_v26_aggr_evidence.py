"""v26: v23 + idle-turn fill.

Identical to v23 in every planned action (/market orders, weed repair, regime
selection).  The only difference: on unit turns where the plan says PASS, this
agent runs the unit to a proven-safe counterfactual instead of standing idle:

  1. HARVEST a standing crop/animal whenever harvesting it right now cannot
     lose anything vs. the plan's timing:
       - non-ongoing crops (WHEAT/CARROT/MELON): only when yield_units is
         already at its max (no further growth possible);
       - ongoing crops (TOMATO/STRAWBERRY) and all animals: whenever
         yield_units > 0 (collections are independent capacity turns, and
         taking them earlier never reduces the total ever collectable).
  2. WATER an unwatered PLANT (guards the 2-consecutive-unwatered -> WEED
     death and is a no-op outside the growth window; strictly non-negative).

Nothing else changes; the market queue remains v23's (reordered by v23's own
scoring inside the base call).
"""
import importlib.util
import json
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
    action = {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }
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


def agent(obs, configuration=None):
    action = _v23.agent(obs, configuration)
    return _fill(action, obs)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)