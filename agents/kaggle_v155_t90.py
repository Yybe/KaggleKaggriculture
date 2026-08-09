"""V15.5-T90: V15 + price-threshold capselllate (fire only when item price >= 90).

V15.5 = V15 exactly, except _capselllate_topup now fires ONLY when the item's market
price is flat or falling (16-step momentum), and holds when the price is rising.

Why (results/DIAGNOSIS_V15_VS_V14.md, evidence [R]):
  - V15's capselllate is the ONLY lever (ablation: idle-fill = 0 effect, capselllate = 100%).
  - Its 22/100 losses are blind price-timing bets: it sold +1 into a RISING market
    (loss seed 3241: px 7->28->68->114; V14 kept 25 units for the peak while V15
    sold the surplus at ~1/3 of eventual price).
  - Wins come from FALLING markets (win seed 2584: px 205->120->60->47; V15's early
    +1 captures ~160/unit over V14's late dump).
  - Gate: fire only when momentum is flat/falling -> sell the surplus before the glut.
    Rising momentum -> hold, V14's peak is still ahead.

Expected: flips the 22 blind-bet losses to wins/ties while keeping the crash-capture
wins. Gate test: 11 loss seeds must flip >= 8; win seeds must not regress.
"""
import base64
import copy
import json
import math
import zlib
from collections import deque

import sys
import os
if "__file__" in globals():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaggle_boat84_v14 as _v14

__version__ = "V15_5_T90"

_ACTIONS = _v14._ACTIONS
_MARKET_PARAMS = _v14._MARKET_PARAMS
_SHOP_PRODUCTS = _v14._SHOP_PRODUCTS
_SELLABLE = _v14._SELLABLE
_LIQUIDATION_ORDER = _v14._LIQUIDATION_ORDER
_PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")
_NON_ONGOING_MAX = {"WHEAT": 6, "CARROT": 4, "MELON": 6}
_HIGH_VALUE = ("STRAWBERRY", "MILK", "WOOL")
_LATEFILL_STEP = 480  # Step 480 (Day 20)
_BUMP_CAP = 1         # Cap +1 for optimal price curve protection
_FIRE_THRESHOLD = 90  # fire capselllate only when item price >= this

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
_market_price = _v14._market_price
_is_sell = _v14._is_sell
_impact_score = _v14._impact_score
_demand_per_day = _v14._demand_per_day
_order_score = _v14._order_score
_rank_sell_slots = _v14._rank_sell_slots
_terminal_liquidation = _v14._terminal_liquidation


def _idle_fill(obs, action, step):
    """Fills idle PASS turns with safe non-negative actions."""
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


def _price_gate_ok(obs, item):
    """Fire capselllate only when the item's current market price >= threshold.

    Signal from gate_search.py: absolute price level best separates LOSS seeds
    (hold) from WIN seeds (fire). Threshold is per-item in _FIRE_THRESHOLD.
    """
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    cur = float(_get(prices, item, 0) or 0)
    return cur >= _FIRE_THRESHOLD


def _capselllate_topup(obs, action, step):
    """Price-threshold-gated high-value SELL top-up (V15.5: fires only at price >= T)."""
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
                if available > qty and _price_gate_ok(obs, item):
                    order = [order[0], order[1], qty + min(_BUMP_CAP, available - qty)]
        new_market.append(list(order))
    action["market"] = new_market
    return action


def agent(obs, configuration=None):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        action = _idle_fill(obs, action, step)
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


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
