"""V15 A-blade-A: V15 minus capselllate top-up (idle-fill kept). Single-lever ablation.
Identical to kaggle_champion_v15 except agent() skips the _capselllate_topup call.
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
from kaggle_champion_v15 import _idle_fill

__version__ = "V15_no_capselllate"

_ACTIONS = _v14._ACTIONS
_MARKET_PARAMS = _v14._MARKET_PARAMS
_SHOP_PRODUCTS = _v14._SHOP_PRODUCTS
_SELLABLE = _v14._SELLABLE
_LIQUIDATION_ORDER = _v14._LIQUIDATION_ORDER

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


def agent(obs, configuration=None):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        action = _idle_fill(obs, action, step)
        action = _repay_shift(obs, action, step)
        action = _rank_sell_slots(obs, action, None)
        action = _preempt_shift(obs, action, step)
        # -- capselllate deliberately DISABLED --
        action = _terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }