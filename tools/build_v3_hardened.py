"""Build a one-lever hardened fork of lynnsakurai v3 (WEED + pasture-aware PLACE).

We take agents/_top_pub/lynnsakurai_v3.py verbatim as the base — its _ROUTES
bytes (9 SHEEP per route) and _select_route at step 360 and _budget_guard
are kept byte-for-byte, per LYNNSAKURAI_V3_FORK_PLAN rulebook §0.1/§3.5.
The ONE new mechanism is a thin WEED/Pasture wrapper inserted BEFORE
_budget_guard in agent(), with mirrors still ties.

The file written is agents/v3_hardened.py (the candidate for the gate).
"""
import pathlib

base = pathlib.Path("agents/_top_pub/lynnsakurai_v3.py").read_text(encoding="utf-8")

header = '"""v3 + WEED/Pasture one-lever hardener (keeps _ROUTES and _budget_guard verbatim)."""'

preamble = r'''
from __future__ import annotations

import base64
import copy
import json
import math
import zlib


_ROUTES = json.loads(zlib.decompress(base64.b85decode(b''' + base.split("base64.b85decode(b'")[1].split("'))")[0] + "')).decode(\"utf-8\"))""".strip()


# ---- One-lever hardening: WEED-aware replanner + pasture-aware PLACE ----
# This is the ONLY diff vs the 2680 base. It runs after the tape dispatch
# ( _ROUTES[route][step] ) and before _budget_guard. It keeps sells, hires,
# and _select_route untouched — only farm writes are patched.
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8
_HARDEN_STATE = {0: {"last_step": -1}, 1: {"last_step": -1}}


def _tile_at(farm, pos):
    try:
        x, y = int(pos[0]), int(pos[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _farm_hands(farm):
    return list(_get(farm, "hands", []) or [])


def _trace_actor_action_v3(step, actor, route):
    trace = _ROUTES[route][min(max(int(step), 0), len(_ROUTES[route]) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action_v3(obs, action, step, route):
    # Mirrors the V27 _weed_repair_action but parametrized by route.
    action = copy.deepcopy(action or {})
    action = {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(o or ["PASS"]) for o in (action.get("hands") or [])],
        "market": [list(o) for o in (action.get("market") or [])],
    }
    seat = _seat(obs)
    # align hands to real hired count (hires from current step haven't landed yet)
    farm = _farm(obs, seat)
    expected = len(_farm_hands(farm))
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(o or ["PASS"]) for o in hands[:expected]]

    game = _WEED_STATE[seat]
    if step == 0 or step < int(game.get("last_step", -1)):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *_farm_hands(farm)]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active = game.setdefault("active", {})

    for actor, txn in list(active.items()):
        idx = 0 if actor == "farmer" else int(actor) + 1
        if idx >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - int(txn["start"])
        if age == 1:
            unit_actions[idx] = list(txn["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[idx] = _trace_actor_action_v3(step - 1, actor, route)
        else:
            active.pop(actor, None)

    for idx, (pos, intended) in enumerate(zip(positions, unit_actions)):
        actor = "farmer" if idx == 0 else idx - 1
        if actor in active or not isinstance(intended, list) or not intended:
            continue
        if intended[0] not in ("BUILD_PASTURE", "BUILD_COOP", "PLANT"):
            continue
        tile = _tile_at(farm, pos)
        if not isinstance(tile, dict) or tile.get("kind") != "WEED":
            continue
        active[actor] = {"start": step, "intended": list(intended)}
        unit_actions[idx] = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    # re-align after repair
    expected = len(_farm_hands(farm))
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(o or ["PASS"]) for o in hands[:expected]]
    return action


def _place_repair_action_v3(obs, action, step):
    try:
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        if not any(max(0, int(_get(shed, a, 0) or 0)) > 0 for a in ("COW", "SHEEP")):
            return action
        seat = _seat(obs)
        farm = _farm(obs, seat)
        farmer_pos = _get(farm, "farmer")
        hands_pos = _farm_hands(farm)
        unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
        n_units = 1 + len(hands_pos)
        if len(unit_actions) < n_units:
            unit_actions.extend([["PASS"] for _ in range(n_units - len(unit_actions))])
        positions = [farmer_pos, *hands_pos]
        empty = []
        for y, row in enumerate(_get(farm, "tiles", []) or []):
            for x, tile in enumerate(row or []):
                if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and not tile.get("animal"):
                    empty.append((x, y))
        if not empty:
            return action
        for idx, intended in enumerate(list(unit_actions)):
            if not isinstance(intended, list) or not intended or intended[0] != "PLACE":
                continue
            animal = intended[1] if len(intended) >= 2 else None
            if animal not in ("COW", "SHEEP"):
                continue
            if max(0, int(_get(shed, animal, 0) or 0)) <= 0:
                continue
            pos = positions[idx] if idx < len(positions) else None
            tile = _tile_at(farm, pos) if pos is not None else "LOCKED"
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and not tile.get("animal"):
                empty = [p for p in empty if p != (int(pos[0]), int(pos[1]))]
                continue
            target = None
            for cand_idx, cand_pos in enumerate(positions):
                if cand_idx >= len(unit_actions):
                    continue
                if not isinstance(cand_pos, (list, tuple)) or len(cand_pos) < 2:
                    continue
                try:
                    xy = (int(cand_pos[0]), int(cand_pos[1]))
                except Exception:
                    continue
                if xy in empty and unit_actions[cand_idx] == ["PASS"]:
                    target = cand_idx
                    break
            if target is None:
                continue
            pasture = (int(positions[target][0]), int(positions[target][1]))  # type: ignore[index]
            unit_actions[target] = list(intended)
            unit_actions[idx] = ["PASS"]
            empty = [p for p in empty if p != pasture]
        action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
        action["hands"] = unit_actions[1:n_units]
        # keep hand count aligned
        farm = _farm(obs, seat)
        expected = len(_farm_hands(farm))
        hands = list(action.get("hands") or [])
        if len(hands) < expected:
            hands.extend([["PASS"] for _ in range(expected - len(hands))])
        action["hands"] = [list(o or ["PASS"]) for o in hands[:expected]]
        return action
    except Exception:
        return action
'''

# Rebuild the file: keep _ROUTES/_select_route/_budget_guard verbatim,
# inject the hardener, then emit agent() that calls weed+place before budget.
old_agent = base.split("def agent(observation, configuration=None):")[1]

new_agent = '''def agent(observation, configuration=None):
    del configuration
    try:
        seat = _seat(observation)
        step = int(_get(observation, "step", 0) or 0)
        state = _STATE[seat]
        if step == 0 or step < int(state.get("last_step", -1)):
            state = {"last_step": -1, "route": 0}
            _STATE[seat] = state
        if not 0 <= step < _TURNS:
            farm = _farm(observation, seat)
            return {
                "farmer": ["PASS"],
                "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
                "market": [],
            }
        if step == _DECISION_STEP:
            state["route"] = _select_route(observation, seat)
        route = int(state.get("route", 0))
        action = _copy_action(_ROUTES[route][step])
        action = _weed_repair_action_v3(observation, action, step, route)
        action = _place_repair_action_v3(observation, action, step)
        action = _budget_guard(action, observation, route, step)
        state["last_step"] = step
        return action
    except Exception:
        farm = _farm(observation, _seat(observation))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }
'''

# splice: everything up to _budget_guard's end, then inject preamble+new_agent
# easier: rebuild from the decoded _ROUTES + the literal helpers from the base file.
helpers = base.split("_ROUTES =")[0]  # imports + header
tail = base.split("def _budget_guard")[1].split("def agent")[0]  # keep _budget_guard body
# reconstruct verbatim file
out = helpers + "_ROUTES = json.loads(zlib.decompress(base64.b85decode(b'" + base.split("base64.b85decode(b'")[1].split("'))")[0] + "')).decode(\"utf-8\"))\n"
# keep _ITEMS.._STATE and _get.._add_budget_sale.._budget_guard from base
middle = base.split('"))')[1].split("def agent")[0]  # from _ITEMS to end of _budget_guard
out = base.split("def agent")[0]  # everything before agent (includes all helpers + _ROUTES + _budget_guard)
out = out + preamble + "\n" + new_agent

# dedupe: preamble already declares _ROUTES, so drop the base's _ROUTES line
# base already has the imports; preamble re-declares them — dedupe by replacing
# the doubled import block with a single one
path = pathlib.Path("agents/v3_hardened.py")
path.write_text(out, encoding="utf-8")
print(f"wrote {path}  {len(out)} bytes")
import py_compile
py_compile.compile(str(path), doraise=True)
print("compile ok")
