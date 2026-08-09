"""V14 + Conservative Idle-Fill + Late Top-Up (V26 champion protocol applied to V14).

Applies the proven V26 promotion protocol directly to the V14 incumbent:
1. Conservative idle-turn fill:
   - WATER unwatered plants on PASS turns (prevents weed death)
   - HARVEST non-ongoing crops (WHEAT, CARROT, MELON) ONLY at max yield
2. Capselllate top-up:
   - At step >= 456 (19*24, final 10 days), bumps existing high-value SELL orders
     (STRAWBERRY 120, MILK 160, WOOL 200) by at most +2 when shed inventory has surplus.
   - Low-value volume (WHEAT 25, FERTILIZER 100) is NEVER bumped.
"""
import copy
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaggle_boat84_v14 as _v14

_NON_ONGOING_MAX = {"WHEAT": 6, "CARROT": 4, "MELON": 6}
_HIGH_VALUE = {"STRAWBERRY", "MILK", "WOOL"}
_LATEFILL_STEP = 19 * 24  # step 456 (final 10 days)
_BUMP_CAP = 2

_get = _v14._get
_seat = _v14._seat
_farm = _v14._farm
_tile_at = _v14._tile_at


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
                if int(tile.get("yield_units", 0) or 0) >= _NON_ONGOING_MAX[crop]:
                    units[index] = ["HARVEST"]
                elif not tile.get("watered_today", False):
                    units[index] = ["WATER"]

    action["farmer"] = units[0] if units else ["PASS"]
    action["hands"] = units[1:]
    return action


def _topup(action, obs):
    step = int(_get(obs, "step", 0) or 0)
    if step < _LATEFILL_STEP:
        return action
    seat = _seat(obs)
    private = _get(obs, "private", {}) or {}
    shed = dict(private.get("shed") or {})
    market = list(action.get("market") or [])
    new_market = []
    for order in market:
        if (isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL"):
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
    action = _v14.agent(obs)
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
