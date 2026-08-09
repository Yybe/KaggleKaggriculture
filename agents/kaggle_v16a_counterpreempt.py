"""V16a: Counter-Preemption (deep-horizon h=4-first).

V15.5 champion runtime (weed repair, idle fill, repay, rank, capselllate,
dead-inventory recovery, terminal liquidation) + ONE change: the preemption
pass runs with horizons (4, 3, 2, 1) instead of V14's h=1-only.

Why h=4-first (the V16 weakness-analysis finding):
- salemali7 (adaptive-preempt-3x2x1) shifts its own tape's future premium sells
  at horizon 3 first, landing at T-3 with one active shift at a time.
- On the identical tape, V16a at horizon 4 lands at T-4 -- EXACTLY ONE STEP
  before salemali7's earliest shift. The pre-crash price peak is captured by
  us; salemali7 sells into the market after our dump (double-dump inversion
  against it). Live mirror evidence: tape-599's 22 STR @ px 39 (T-4) vs px 11
  after the shift; tape-666's 25 STR @ px 66 (T-4) vs px 1 post-shift.
- Volume-neutral: due = step + horizon, repaid exactly at the due step (the
  tape's own SELL order is reduced by the shifted quantity). Total supply
  unchanged -- only the seller of the peak changes.
- Clone-gated (clone_distance <= 6): vs non-clone opponents V16a behaves
  exactly like V15.5 (no regression in general play).

Pre-registered gate: H2H vs salemali7, 8-seed family
(1M 9M 3.33M 7.77M 5M 6M 8M 2M), >=6/8 wins + positive mean delta.
"""
import base64
import copy
import json
import math
import zlib

import sys
import os
if "__file__" in globals():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaggle_boat84_v14 as _v14

__version__ = "V16a_CounterPreempt"

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

_RECOVERY_START = 705     # Step 705 (Day 29.4): only sell dead inventory in the FINAL
_RECOVERY_STOP = 717      # recovery window (709-716 peaks); terminal liquidation runs at 717
_RECOVERY_CHUNK = 12      # Max DEAD units sold per item per step
_RECOVERY_GATES = {
    "STRAWBERRY": 60,
    "MILK": 110,
    "WOOL": 200,
}
_RECOVERY_PRIORITY = ("STRAWBERRY", "MILK", "WOOL")

# --- V16a counter-preemption parameters (horizons 4-first is THE change) ---
_PREEMPT_ENABLED = True
_PREEMPT_HORIZONS = (4, 3, 2, 1)   # deep: one step BEFORE salemali7's h=3-first
_PREEMPT_FRACTION = 2.0
_PREEMPT_MAX_BATCH = 30
_PREEMPT_MAX_CLONE_DISTANCE = 6
_PREEMPT_MIN_PRICE_RATIO = 0.0
_PREEMPT_MIN_FUTURE_QUANTITY = 4
_PREEMPT_START = 120
_PREEMPT_STOP = 680

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
_tile_at = _v14._tile_at
_weed_repair_action = _v14._weed_repair_action
_market_price = _v14._market_price
_is_sell = _v14._is_sell
_impact_score = _v14._impact_score
_demand_per_day = _v14._demand_per_day
_order_score = _v14._order_score
_rank_sell_slots = _v14._rank_sell_slots
_terminal_liquidation = _v14._terminal_liquidation


def _future_sells_at(step, horizon):
    """Premium SELL quantities the tape will place at step + horizon."""
    if step + horizon >= len(_ACTIONS):
        return {}
    result = {}
    for raw in (_ACTIONS[step + horizon].get("market") or []):
        if len(raw) >= 3 and raw[0] == "SELL" and raw[1] in _PREMIUM:
            result[raw[1]] = result.get(raw[1], 0) + max(0, int(raw[2]))
    return result


def _counter_preempt(obs, action, step):
    """Shift future premium tape sells 4 steps early (one step before salemali7's
    h=3-first), repaying the exact quantity at the due step. Clone-gated."""
    if not _PREEMPT_ENABLED or not (_PREEMPT_START <= step < _PREEMPT_STOP):
        return action
    state = _shift_state(obs, step)
    if state.get("due") or _clone_distance(obs) > _PREEMPT_MAX_CLONE_DISTANCE:
        return action
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    remaining = _projected_shed(obs, action)
    for raw in market:
        if len(raw) >= 3 and raw[0] == "SELL":
            item = raw[1]
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - max(0, int(raw[2])))
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}

    for horizon in _PREEMPT_HORIZONS:
        future = _future_sells_at(step, horizon)
        if not future:
            continue
        shifted = {}
        trial_market = list(market)
        trial_remaining = dict(remaining)
        for item in _PREMIUM:
            future_quantity = max(0, int(future.get(item, 0) or 0))
            if future_quantity < _PREEMPT_MIN_FUTURE_QUANTITY:
                continue
            base_price = float(_MARKET_PARAMS[item][0])
            current_price = float(_get(prices, item, 0) or 0)
            # At the $1 floor, SELL does not add market inventory: moving a unit
            # earlier cannot create queue pressure on the clone.
            if current_price <= 1:
                continue
            if current_price < base_price * _PREEMPT_MIN_PRICE_RATIO:
                continue
            target = min(
                max(0, int(trial_remaining.get(item, 0) or 0)),
                future_quantity,
                _PREEMPT_MAX_BATCH,
                max(1, int(round(future_quantity * _PREEMPT_FRACTION))),
            )
            if target <= 0 or len(trial_market) >= 10:
                continue
            trial_market.append(["SELL", item, target])
            trial_remaining[item] = max(0, int(trial_remaining.get(item, 0) or 0) - target)
            shifted[item] = target
        if shifted:
            action["market"] = trial_market[:10]
            state["due_step"] = step + horizon
            state["due"] = shifted
            return action
    return action


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


def _capselllate_topup(obs, action, step):
    """Bumps high-value sell quantities late game to inflict asymmetric price pressure on opponent."""
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


def _recovery_sell(obs, action, step):
    """Front-loads DEAD shed inventory into late-game price-recovery windows."""
    if step < _RECOVERY_START or step >= _RECOVERY_STOP:
        return action
    seat = _seat(obs)
    private = _get(obs, "private", {}) or {}
    shed = dict(private.get("shed") or {})
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    market = list(action.get("market") or [])

    planned_now = {item: 0 for item in _SELLABLE}
    for order in market:
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
            planned_now[str(order[1])] += max(0, int(order[2]))

    future_tape = {item: 0 for item in _SELLABLE}
    for t in range(step + 1, len(_ACTIONS)):
        entry = _ACTIONS[t]
        if not isinstance(entry, dict):
            continue
        for order in (entry.get("market") or []):
            if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                future_tape[str(order[1])] += max(0, int(order[2]))

    new_orders = []
    for item in _RECOVERY_PRIORITY:
        if len(market) + len(new_orders) >= 10:
            break
        available = max(0, int(shed.get(item, 0) or 0))
        dead = available - planned_now.get(item, 0) - future_tape.get(item, 0)
        if dead < 1:
            continue
        price = int(prices.get(item, 0) or 0)
        if price < _RECOVERY_GATES.get(item, 0):
            continue
        chunk = min(dead, _RECOVERY_CHUNK)
        new_orders.append(["SELL", item, chunk])
    if new_orders:
        action["market"] = new_orders + market
    return action


def agent(obs, configuration=None):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        action = _idle_fill(obs, action, step)
        action = _repay_shift(obs, action, step)
        action = _rank_sell_slots(obs, action, None)
        action = _counter_preempt(obs, action, step)   # V16a: h=(4,3,2,1) replaces V14's h=1
        action = _capselllate_topup(obs, action, step)
        action = _recovery_sell(obs, action, step)
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
