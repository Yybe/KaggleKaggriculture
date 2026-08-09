"""v26b: v23 + conservative idle-turn fill.

Strictly less invasive than v26: only two fills, each provably non-negative:
  1. WATER an unwatered PLANT on a PASS turn (prevents the
     2-consecutive-unwatered -> WEED death; no-op outside the growth window).
  2. HARVEST a one-shot crop only when yield_units is already AT its absolute
     max (the exact yield any later harvest could collect; tile->None matches
     what a planned later harvest would do, just earlier — no shed-conflict
     because the same units are moved, not doubled).

No ongoing-crop/animal harvests (that was v26's -972 leak: extra units
overflow the 100-cap shed and crowd out scheduled drops).  Market orders
remain exactly v23's.
"""
import importlib.util
import os
import sys

_BASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kaggle_v23.py")
_spec = importlib.util.spec_from_file_location("_kaggle_v23_fillsource_b", _BASE_FILE)
_v23 = importlib.util.module_from_spec(_spec)
sys.modules["_kaggle_v23_fillsource_b"] = _v23
_spec.loader.exec_module(_v23)

_NON_ONGOING_MAX = {"WHEAT": 6, "CARROT": 4, "MELON": 6}


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
                if int(tile.get("yield_units", 0) or 0) >= _NON_ONGOING_MAX[crop]:
                    units[index] = ["HARVEST"]
                elif not tile.get("watered_today", False):
                    units[index] = ["WATER"]

    action["farmer"] = units[0] if units else ["PASS"]
    action["hands"] = units[1:]
    return action


def agent(obs, configuration=None):
    action = _v23.agent(obs, configuration)
    return _fill(action, obs)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)