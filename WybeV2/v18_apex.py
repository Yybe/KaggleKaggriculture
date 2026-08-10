"""V18 Apex (Thunder-Slayer) for Kaggriculture.

Unified multi-horizon counter-preemption, anti-thunder wool/milk interception,
boatlee 5-turn fertilizer relay, dead-inventory recovery selling, and
robust production core.
"""
import base64
import copy
import json
import math
import zlib

import sys
import os
sys.path.insert(0, '.')
import submission

_LEGACY_ACTIONS = submission._LEGACY_ACTIONS
_REBALANCE_ACTIONS = submission._REBALANCE_ACTIONS
_V16_OFFICIAL_CONFIGURATION = submission._V16_OFFICIAL_CONFIGURATION

_get = submission._get
_copy_action = submission._copy_action
_seat = submission._seat
_farm = submission._farm
_align_hands = submission._align_hands
_tile_at = submission._tile_at
_weed_repair_action = submission._weed_repair_action
_v16_convert_livestock = submission._v16_convert_livestock
_v16_wool_controller = submission._v16_wool_controller
_rank_sell_slots = submission._rank_sell_slots
_regime = submission._regime
_rc3_market_relay = submission._rc3_market_relay
_rc3_state = submission._rc3_state
_rc3_route_distance = submission._rc3_route_distance

# --- V18 Apex Global State ---
_V18_STATE = {
    0: {
        "last_step": -1,
        "opp_type": "UNKNOWN",
        "wool_intercepted": 0,
        "wool_repaid": False,
        "milk_intercepted": 0,
        "milk_repaid": False,
    },
    1: {
        "last_step": -1,
        "opp_type": "UNKNOWN",
        "wool_intercepted": 0,
        "wool_repaid": False,
        "milk_intercepted": 0,
        "milk_repaid": False,
    },
}

_RECOVERY_GATES = {
    "STRAWBERRY": 60,
    "MILK": 110,
    "WOOL": 200,
}

def _v18_state(obs, step):
    seat = _seat(obs)
    st = _V18_STATE[seat]
    if step == 0 or step < int(st.get("last_step", -1)):
        st = {
            "last_step": step,
            "opp_type": "UNKNOWN",
            "wool_intercepted": 0,
            "wool_repaid": False,
            "milk_intercepted": 0,
            "milk_repaid": False,
        }
        _V18_STATE[seat] = st
    st["last_step"] = step
    
    # Classify opponent based on route distance
    if step in (120, 216, 240, 264):
        dist = _rc3_route_distance(obs)
        if dist <= 12:
            st["opp_type"] = "MIRROR_LIKE"
        else:
            st["opp_type"] = "ASYMMETRIC"
    return st

def _anti_thunder_wool_intercept(obs, action, step, st, route):
    """Intercept WOOL and MILK peak prices before THUNDER dumps."""
    market = list(action.get("market") or [])
    private = _get(obs, "private", {}) or {}
    shed = dict(private.get("shed", {}) or {})
    
    # 1. WOOL Intercept at step 663 (T-9 before THUNDER step 664 dump and V17 step 672 dump)
    if step == 663 and st["wool_intercepted"] == 0:
        avail_wool = int(shed.get("WOOL", 0) or 0)
        qty = min(16, avail_wool)
        if qty > 0 and len(market) < 10:
            market.insert(0, ["SELL", "WOOL", qty])
            st["wool_intercepted"] = qty

    # Repay WOOL at step 672
    if step == 672 and st["wool_intercepted"] > 0 and not st["wool_repaid"]:
        repay = st["wool_intercepted"]
        new_m = []
        for ord in market:
            if len(ord) >= 3 and ord[0] == "SELL" and ord[1] == "WOOL" and repay > 0:
                cur = int(ord[2])
                red = min(cur, repay)
                cur -= red
                repay -= red
                if cur > 0:
                    new_m.append([ord[0], ord[1], cur])
            else:
                new_m.append(ord)
        market = new_m
        st["wool_repaid"] = True

    # 2. MILK Intercept at step 666 (T-6 before THUNDER step 667 dump)
    if step == 666 and st["milk_intercepted"] == 0:
        avail_milk = int(shed.get("MILK", 0) or 0)
        qty = min(9, avail_milk)
        if qty > 0 and len(market) < 10:
            market.insert(0, ["SELL", "MILK", qty])
            st["milk_intercepted"] = qty

    # Repay MILK at step 672
    if step == 672 and st["milk_intercepted"] > 0 and not st["milk_repaid"]:
        repay = st["milk_intercepted"]
        new_m = []
        for ord in market:
            if len(ord) >= 3 and ord[0] == "SELL" and ord[1] == "MILK" and repay > 0:
                cur = int(ord[2])
                red = min(cur, repay)
                cur -= red
                repay -= red
                if cur > 0:
                    new_m.append([ord[0], ord[1], cur])
            else:
                new_m.append(ord)
        market = new_m
        st["milk_repaid"] = True

    action["market"] = market[:10]
    return action

def _v18_recovery_sell(obs, action, step, route):
    """Dead-inventory recovery selling on steps 705 to 716."""
    if not (705 <= step <= 716):
        return action
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
        
    private = _get(obs, "private", {}) or {}
    shed = dict(private.get("shed", {}) or {})
    mkt_info = _get(obs, "market", {}) or {}
    prices = _get(mkt_info, "prices", {}) or {}
    
    for item in ("STRAWBERRY", "MILK", "WOOL"):
        gate = _RECOVERY_GATES.get(item, 0)
        cur_px = int(_get(prices, item, 0) or 0)
        if cur_px >= gate:
            avail = int(shed.get(item, 0) or 0)
            # Future planned sells in base route
            future_planned = 0
            for fut_s in range(step, len(route)):
                for raw in (route[fut_s].get("market") or []):
                    if len(raw) >= 3 and raw[0] == "SELL" and raw[1] == item:
                        future_planned += int(raw[2])
            dead = max(0, avail - future_planned)
            if dead > 0 and len(market) < 10:
                sell_qty = min(12, dead)
                market.insert(0, ["SELL", item, sell_qty])
                
    action["market"] = market[:10]
    return action

def _v18_capselllate(obs, action, step, bump_cap=1):
    """Top-up high value orders on step >= 456 if shed has surplus."""
    if step < 456:
        return action
    market = list(action.get("market") or [])
    private = _get(obs, "private", {}) or {}
    shed = dict(private.get("shed", {}) or {})
    
    new_m = []
    for ord in market:
        if len(ord) >= 3 and ord[0] == "SELL" and ord[1] in ("STRAWBERRY", "MILK", "WOOL"):
            item = ord[1]
            qty = int(ord[2])
            avail = int(shed.get(item, 0) or 0)
            if avail > qty:
                ord = [ord[0], ord[1], qty + min(bump_cap, avail - qty)]
        new_m.append(ord)
    action["market"] = new_m[:10]
    return action

def agent(obs, configuration=None):
    try:
        cfg = configuration or _V16_OFFICIAL_CONFIGURATION
        actions = (
            _REBALANCE_ACTIONS
            if _regime(cfg) == "rebalance"
            else _LEGACY_ACTIONS
        )
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(actions) - 1)
        st = _v18_state(obs, step)
        
        # 1. Base action with weed repair and livestock controls
        action = _weed_repair_action(obs, _copy_action(actions[step]), actions, step)
        action = _v16_convert_livestock(action, obs, step)
        action = _v16_wool_controller(action, obs, step)
        
        # 2. Boatlee 5-turn fertilizer counter-relay
        action = _rc3_market_relay(obs, action, step, cfg)
        
        # 3. Anti-Thunder Wool & Milk Interception
        action = _anti_thunder_wool_intercept(obs, action, step, st, actions)
        
        # 4. Dead-Inventory Recovery Selling (steps 705 to 716)
        action = _v18_recovery_sell(obs, action, step, actions)
        
        # 5. Capselllate
        action = _v18_capselllate(obs, action, step, bump_cap=1)
        
        # 6. Rank market orders by price impact and align hands
        action = _rank_sell_slots(obs, action, cfg)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }
