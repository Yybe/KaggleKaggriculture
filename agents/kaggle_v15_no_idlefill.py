"""V15 B-blade-B: V15 minus idle-fill (capselllate kept). Single-lever ablation.
Identical to kaggle_champion_v15 except agent() skips the _idle_fill call.
"""
import base64
import copy
import json
import math
import zlib

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaggle_boat84_v14 as _v14

__version__ = "V15_no_idlefill"

_ACTIONS = _v14._ACTIONS
_MARKET_PARAMS = _v14._MARKET_PARAMS
_SHOP_PRODUCTS = _v14._SHOP_PRODUCTS
_SELLABLE = _v14._SELLABLE
_LIQUIDATION_ORDER = _v14._LIQUIDATION_ORDER
_HIGH_VALUE = ("STRAWBERRY", "MILK", "WOOL")
_LATEFILL_STEP = 480
_BUMP_CAP = 1

_get = _v14._get
_copy_action = _v14._copy_action
_seat = _v14._seat
_farm = _v14._farm
_align_hands = _v14._align_hands
_projected_shed = _v14._projected_shed
_public_signature = _v14._public_signature
_clone_distance = _v14._clone_distance
_shift_state = _v14._shift_state
_repay_shift = _v14._repay_shift
_future_sells = _v14._future_sells
_preempt_shift = _v14._preempt_shift
_tile_at = _v14._tile_at
_weed_repair_action = _v14._weed_repair_action
_rank_sell_slots = _v14._rank_sell_slots
_terminal_liquidation = _v14._terminal_liquidation


def _capselllate_topup(obs, action, step):
    """Bumps high-value sell quantities late game (unchanged from V15)."""
    if step < _LATEFILL_STEP or step >= 716:
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
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        # -- idle-fill deliberately DISABLED --
        action = _repay_shift(obs, action, step)
        action = _rank_sell_slots(obs, action, None)
        action = _preempt_shift(obs, action, step)
        action = _capselllate_topup(obs, action, step)
        action = _terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }