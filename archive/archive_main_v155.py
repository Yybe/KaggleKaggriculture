"""Champion Agent V15.5: Dead-Inventory Recovery Selling (V15 + dead-shed front-loading).

Built from the kevin park forensics (\u0394\u22121876) and the other 4 real V15 losses:

Root cause found: V15's tape dumps STRAWBERRY at fixed late steps that land in
CRASHED markets (px 1-24 at steps 599/615/666/717), while winning opponents sell
into PRICE RECOVERY windows (px 68@598, 32@614, 53@647, 47@665, 85@715, 62@716)
that appear as town shops drain inventory between dumps. The opponent's
12+12+1 STR @ 715/716/717 vs V15's 24 @ 717 alone explains ~1,188 of the kevin
delta; summing all mid-game windows fully accounts for the 2,223 STR revenue gap.

Second defect: V15's _terminal_liquidation APPENDS STR at market-queue position 3
(after MILK/WOOL/WHEAT), so it sells AFTER the glut; the opponent FRONT-LOADS STR
at position 0. In the lockstep engine, position order is execution order, so
front-loaded sells quote against pre-glut inventory.

V15.5 = V15 + dead-inventory _recovery_sell pass:
- DEAD inventory = shed units beyond (a) sells planned this step and (b) every
  SELL the tape will execute at any future step (scanned from _ACTIONS). The
  tape's last STRAWBERRY sell is step 670 - anything still in the shed after
  that would otherwise rot into the terminal liquidation at px ~43 (day-30
  demand collapse) while the shared market price recovers to px 62-85 through
  steps 709-716 as town shops drain inventory.
- FINAL-WINDOW ONLY: recovery fires only on steps 705..716 (the STR recovery
  peak). Firing earlier (570..704) sells into mid-game dips at px 51-68 while
  V15's terminal dump captures 120-141 - variant A was 18W/22L, mean \u0394
  \u2212421. Selling dead STR at the 709-716 peak beats the terminal dump, which
  always crashes the price (seed 2000: px 70->32; seed 2073: px 158->120).
- When the CURRENT market price is >= gate, sell up to 12 units of DEAD
  inventory at the FRONT of the market queue.
- Everything else (capselllate, preempt, rank_sell_slots, terminal liquidation)
  is unchanged from V15.

Empirically verified (champion promotion):
- v1 (surplus front-loading, steps 570..716) was 0-40 vs both V15 and V14
  (mean \u0394 \u22121444/\u22121370): it stole volume from the tape's own
  599/600/602 STR sells and crashed their prices. The dead-inventory filter is
  immune: if the tape will sell the units itself, recovery never fires.
- FINAL (dead-inventory, steps 705..716, gate STR>=60): 120W/0L vs V15 across
  60 distinct seeds (mean \u0394 +492 tuned / +472 fresh, min +118); 40W/0L vs V14
  (mean \u0394 +669 vs V15's +196 baseline); 40W/0L vs the previous
  momentum-gate champion_v155 (mean \u0394 +632).
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

__version__ = "V15_5_Champion"

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
                          # recovery window (709-716 peaks at px 62-158 in probes).
                          # Firing earlier (570-704) sells into mid-game dips at px 51-68
                          # while V15's terminal dump captures 120-141 (seed 2073: -1702).
_RECOVERY_STOP = 717      # Step 717: terminal liquidation runs (day-30 demand collapse)
_RECOVERY_CHUNK = 12      # Max DEAD units sold per item per step (opponent used 11-13)
_RECOVERY_GATES = {       # Only sell DEAD inventory when the CURRENT price is at/above gate
    "STRAWBERRY": 60,     # Observed terminal recovery: 51@701, 59@705, 74@709, 82@713-716
    "MILK": 110,          # MILK peaks 126-135 late; terminal ~89-97
    "WOOL": 200,          # WOOL holds 240-244; gate rarely binds
}
_RECOVERY_PRIORITY = ("STRAWBERRY", "MILK", "WOOL")

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
    """Front-loads DEAD shed inventory into late-game price-recovery windows.

    Dead inventory = shed units beyond (a) the sells planned for this step and
    (b) every SELL the tape will execute at any future step (scanned from
    _ACTIONS). The tape's last STRAWBERRY sell is step 670 - anything still in
    the shed after that would otherwise rot into the terminal liquidation at
    px ~43 (day-30 demand collapse), while the shared market price recovers to
    px 62-85 through steps 709-716 as town shops drain inventory. Selling dead
    STR front-loaded at px >= gate captures that recovery.

    First H2H attempt (0-40) sold SURPLUS (shed beyond this-step planned sells)
    at 578-579, stealing volume from the tape's own 599/600/602 STR sells,
    crashing their prices and handing the opponent the starved-market recovery.
    The dead-inventory filter is immune: if the tape will sell it, we don't.
    """
    if step < _RECOVERY_START or step >= _RECOVERY_STOP:
        return action
    seat = _seat(obs)
    private = _get(obs, "private", {}) or {}
    shed = dict(private.get("shed") or {})
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    market = list(action.get("market") or [])

    # (a) sells already planned for THIS step
    planned_now = {item: 0 for item in _SELLABLE}
    for order in market:
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
            planned_now[str(order[1])] += max(0, int(order[2]))

    # (b) every SELL the tape will execute at future steps (step+1 .. end)
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
        action = _preempt_shift(obs, action, step)
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
