"""Extract opponent action tapes from live kaggriculture episode replays.

Reads replay JSONs, picks the opponent (non-Shivam_2212) seat, and writes a
standalone replay-opponent agent file per episode:

    agents/live_replay/opp_<epid>_<name>.py

containing `_ACTIONS` (their per-step actions, incl. market orders) plus the
same tape-replay wrapper the champion uses (weed repair + hand alignment),
with the adaptive-market layer disabled. These are local stand-ins for the
live top-600 meta agents.

Usage:
  python tools/extract_live_opponents.py <replay.json> [<out_dir>]
"""
import ast
import json
import os
import sys


def our_seat(data):
    names = [str(n).lower() for n in data.get("info", {}).get("TeamNames", [])]
    for i, n in enumerate(names):
        if "shivam" in n:
            return i
    return 0


def safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)[:40]


def extract(replay_path, out_dir):
    data = json.load(open(replay_path, encoding="utf-8"))
    seat = our_seat(data)
    opp = 1 - seat
    steps = data.get("steps", [])
    tape = []
    for step in steps:
        entry = step[opp]
        action = entry.get("action") or {}
        if not isinstance(action, dict):
            action = {}
        tape.append(
            {
                "farmer": list(action.get("farmer") or ["PASS"]),
                "hands": [list(h or ["PASS"]) for h in (action.get("hands") or [])],
                "market": [list(o) for o in (action.get("market") or [])],
            }
        )
    teams = data.get("info", {}).get("TeamNames", [])
    name = safe_name(str(teams[opp]))
    ep_id = data.get("id", "unknown")[:8]
    rewards = data.get("rewards", [])
    our_name = str(teams[seat])

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"opp_{name}_{ep_id}.py")

    tape_literal = json.dumps(tape, separators=(",", ":"))
    body = TAPE_AGENT_TEMPLATE.format(
        tape_literal=tape_literal,
        source=os.path.basename(replay_path),
        teams=json.dumps(teams),
        rewards=json.dumps(rewards),
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(body)
    ast.parse(body)  # must be valid python
    print(f"{out_path}  steps={len(tape)} teams={teams} rewards={rewards} our_seat={seat}")
    return out_path


TAPE_AGENT_TEMPLATE = '''"""Replay-opponent extracted from a live episode (tape + champion wrapper).

Source: {source}
Teams: {teams}
Live rewards: {rewards}
The adaptive-market layer is disabled; only tape replay + weed repair run.
"""
import base64
import copy
import json
import zlib


_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    __TAPE_B85__
))).decode("utf-8") if False else json.loads(zlib.decompress(base64.b85decode(
    __TAPE_B85__
)))


_WEED_STATE = {{0: {{}}, 1: {{}}}}
_WEED_REPLAY_STEPS = 8
_SHOP_PRODUCTS = {{
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}}


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _copy_action(action):
    action = copy.deepcopy(action or {{}})
    return {{
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }}


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {{}}


def _align_hands(action, obs):
    action = _copy_action(action)
    expected = len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
    return action


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _trace_actor_action(step, actor):
    trace = _ACTIONS[min(max(int(step), 0), len(_ACTIONS) - 1)] or {{}}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action(obs, action, step):
    action = _align_hands(action, obs)
    seat = _seat(obs)
    game = _WEED_STATE.setdefault(seat, {{}})
    if step == 0 or step < int(game.get("last_step", -1)):
        game = {{"last_step": step, "active": {{}}}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active = game.setdefault("active", {{}})

    for actor, transaction in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - int(transaction["start"])
        if age == 1:
            unit_actions[index] = list(transaction["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[index] = _trace_actor_action(step - 1, actor)
        else:
            active.pop(actor, None)

    for index, (position, intended) in enumerate(zip(positions, unit_actions)):
        actor = "farmer" if index == 0 else index - 1
        if actor in active or not isinstance(intended, list) or not intended:
            continue
        if intended[0] not in ("BUILD_PASTURE", "PLANT"):
            continue
        tile = _tile_at(farm, position)
        if not isinstance(tile, dict) or tile.get("kind") != "WEED":
            continue
        active[actor] = {{"start": step, "intended": list(intended)}}
        unit_actions[index] = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    return _align_hands(action, obs)


def agent(obs, configuration=None):
    try:
        fallback = int(_get(obs, "day", 0) or 0) * 24 + int(_get(obs, "hour", 0) or 0)
        step = min(max(0, int(_get(obs, "step", fallback) if _get(obs, "step", None) is not None else fallback)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {{
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }}


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''


def _b85(obj):
    import base64
    import zlib

    blob = zlib.compress(json.dumps(obj).encode("utf-8"), 9)
    return base64.b85encode(blob).decode("ascii")


def main():
    replay_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join("agents", "live_replay")
    data = json.load(open(replay_path, encoding="utf-8"))
    seat = our_seat(data)
    opp = 1 - seat
    steps = data.get("steps", [])
    tape = []
    for step in steps:
        entry = step[opp]
        action = entry.get("action") or {}
        if not isinstance(action, dict):
            action = {}
        tape.append(
            {
                "farmer": list(action.get("farmer") or ["PASS"]),
                "hands": [list(h or ["PASS"]) for h in (action.get("hands") or [])],
                "market": [list(o) for o in (action.get("market") or [])],
            }
        )
    teams = data.get("info", {}).get("TeamNames", [])
    name = safe_name(str(teams[opp]))
    ep_id = str(data.get("id", "unknown"))[:8]
    rewards = data.get("rewards", [])

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"opp_{name}_{ep_id}.py")
    template = TAPE_AGENT_TEMPLATE
    body = template.replace("__TAPE_B85__", _b85(tape)).replace("{source}", os.path.basename(replay_path)).replace(
        "{teams}", json.dumps(teams)
    ).replace("{rewards}", json.dumps(rewards))
    # The template uses doubled braces for .format safety; we used replace, so
    # undo the doubling by parsing: write via format with a dummy mapping.
    body = template.replace("__TAPE_B85__", _b85(tape))
    body = body.format(
        source=os.path.basename(replay_path),
        teams=json.dumps(teams),
        rewards=json.dumps(rewards),
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(body)
    ast.parse(body)
    print(f"{out_path} steps={len(tape)} teams={teams} rewards={rewards} our_seat={seat}")


if __name__ == "__main__":
    main()
