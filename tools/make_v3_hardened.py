import pathlib, py_compile
base = pathlib.Path("agents/_top_pub/lynnsakurai_v3.py").read_text(encoding="utf-8")

# The base _ROUTES blob is unique — we keep it byte-for-byte, only inject helpers
# after _budget_guard and replace agent().
preamble = open(pathlib.Path(__file__).parent / "v3_hardened_preamble.py", encoding="utf-8").read() if False else ""

hardener = r'''
# ---- One-lever hardening: WEED + pasture-aware PLACE (v3 fork) ----
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8

def _tile_at_v3(farm, pos):
    try:
        x, y = int(pos[0]), int(pos[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"

def _trace_actor_action_v3(step, actor, route):
    trace = _ROUTES[route][min(max(int(step), 0), len(_ROUTES[route]) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])

def _weed_repair_action_v3(obs, action, step, route):
    action = copy.deepcopy(action or {})
    action = {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(o or ["PASS"]) for o in (action.get("hands") or [])],
        "market": [list(o) for o in (action.get("market") or [])],
    }
    seat = _seat(obs)
    farm = _farm(obs, seat)
    expected = len(list(_get(farm, "hands", []) or []))
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
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
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
        tile = _tile_at_v3(farm, pos)
        if not isinstance(tile, dict) or tile.get("kind") != "WEED":
            continue
        active[actor] = {"start": step, "intended": list(intended)}
        unit_actions[idx] = ["DIG"]
    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    expected = len(list(_get(_farm(obs, _seat(obs)), "hands", []) or []))
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
        hands_pos = list(_get(farm, "hands", []) or [])
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
            tile = _tile_at_v3(farm, pos) if pos is not None else "LOCKED"
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
            pasture = (int(positions[target][0]), int(positions[target][1]))
            unit_actions[target] = list(intended)
            unit_actions[idx] = ["PASS"]
            empty = [p for p in empty if p != pasture]
        action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
        action["hands"] = unit_actions[1:n_units]
        expected = len(list(_get(_farm(obs, _seat(obs)), "hands", []) or []))
        hands = list(action.get("hands") or [])
        if len(hands) < expected:
            hands.extend([["PASS"] for _ in range(expected - len(hands))])
        action["hands"] = [list(o or ["PASS"]) for o in hands[:expected]]
        return action
    except Exception:
        return action
'''

new_agent = r'''
def agent(observation, configuration=None):
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

part_before_agent = base.split("def agent(observation, configuration=None):")[0]
out = part_before_agent + hardener + "\n" + new_agent + "\n"
path = pathlib.Path("agents/v3_hardened.py")
path.write_text(out, encoding="utf-8")
print(f"wrote {path} {len(out)} bytes")
py_compile.compile(str(path), doraise=True)
print("compile ok")
