"""E258/E259 builders - two counter arms on the tetsutani spine, one mechanism each.

E258 fert-buy veto: drop `["BUY_PRODUCT","FERTILIZER",n]` when our own fertilizer position (shed +
carried) already covers n.  Evidence: heaviest loss bought 104 market fertilizer while 486 doses sat
uncollected on animals; winner bought 17.  Cash stays in the farm.

E259 idle-hand replant: convert a hand whose committed op is exactly ["PASS"] and which stands on an
OWNED-EMPTY tile (tile is None) into PLANT of a crop we actually hold seeds for (private.seeds), highest
`first-yield value` order TOMATO > CARROT > MELON > STRAWBERRY > WHEAT.  Evidence: heavy losses carry
tile_days_empty +727 and op_PASS +112 against the winning seat, with td_TOMATO -1,184 - i.e. seeds bought
and land idle while the opponent works both.  No market order is added, no committed op is displaced.

Why not more collection (E257): converting idle hands to COLLECT_FERTILIZER/FEED/FERTILIZE measured
-322/seat head-to-head against this same parent and -79/seat absolute on 32 paired rows
(TETS_COUNTER_20260929/out/gate_run.txt) - shed capacity is 100 units and extra collected fertilizer
displaces produce, so the winner's higher collect rate is a consequence of herd throughput, not a
purchasable wrapper action.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_FILE = os.path.join(ROOT, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py")

LAYER_258 = '''

# --- E258 FERTILIZER-BUY VETO ---
_E258_PARENT = agent
del agent

_E258_FIRES = {"steps": 0, "orders_seen": 0, "orders_dropped": 0, "units_dropped": 0, "errors": 0}


def agent(observation, configuration=None):
    action = _E258_PARENT(observation, configuration)
    try:
        _E258_FIRES["steps"] += 1
        if isinstance(action, dict):
            market = action.get("market") or []
            if any(isinstance(m, list) and len(m) >= 3 and m[0] == "BUY_PRODUCT"
                   and m[1] == "FERTILIZER" for m in market):
                private = observation.get("private") or {}
                have = (private.get("shed") or {}).get("FERTILIZER", 0) or 0
                have += sum((inv.get("FERTILIZER", 0) or 0) for inv in (private.get("inventories") or []))
                kept = []
                for m in market:
                    if (isinstance(m, list) and len(m) >= 3 and m[0] == "BUY_PRODUCT"
                            and m[1] == "FERTILIZER"):
                        _E258_FIRES["orders_seen"] += 1
                        n = int(m[2]) if isinstance(m[2], int) else 1
                        if have >= n:
                            _E258_FIRES["orders_dropped"] += 1
                            _E258_FIRES["units_dropped"] += n
                            have -= n
                            continue
                    kept.append(m)
                if len(kept) != len(market):
                    action = dict(action)
                    action["market"] = kept
    except Exception:
        _E258_FIRES["errors"] += 1
    return action


agent.telemetry = _E258_FIRES
'''

LAYER_259 = '''

# --- E259 IDLE-HAND REPLANT (own seeds into owned-empty tiles under idle hands) ---
_E259_PARENT = agent
del agent

_E259_ORDER = ("TOMATO", "CARROT", "MELON", "STRAWBERRY", "WHEAT")
_E259_FIRES = {"steps": 0, "converted": 0, "errors": 0}
_E259_BYCROP = {}


def agent(observation, configuration=None):
    action = _E259_PARENT(observation, configuration)
    try:
        _E259_FIRES["steps"] += 1
        if isinstance(action, dict):
            seat = int(observation.get("player", 0) or 0)
            farms = observation.get("farms") or []
            farm = farms[seat] if seat < len(farms) else {}
            tiles = farm.get("tiles") or []
            seeds = (observation.get("private") or {}).get("seeds") or {}
            used = {}

            def _avail():
                return [c for c in _E259_ORDER
                        if (seeds.get(c, 0) or 0) - used.get(c, 0) > 0]

            avail = _avail()
            if avail:
                pos = [farm.get("farmer") or [0, 0]] + list(farm.get("hands") or [])
                slots = [action.get("farmer")] + list(action.get("hands") or [])
                out_farmer = action.get("farmer")
                out_hands = list(action.get("hands") or [])
                for idx, cur in enumerate(slots):
                    if not (isinstance(cur, list) and len(cur) == 1 and cur[0] == "PASS"):
                        continue
                    if not avail or idx >= len(pos):
                        continue
                    p = pos[idx]
                    if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                        continue
                    fx, fy = int(p[0]), int(p[1])
                    if not (0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy])):
                        continue
                    if tiles[fy][fx] is not None:
                        continue
                    crop = avail[0]
                    if idx == 0:
                        out_farmer = ["PLANT", crop]
                    else:
                        out_hands[idx - 1] = ["PLANT", crop]
                    _E259_FIRES["converted"] += 1
                    _E259_BYCROP[crop] = _E259_BYCROP.get(crop, 0) + 1
                    used[crop] = used.get(crop, 0) + 1
                    avail = _avail()
                if _E259_FIRES["converted"]:
                    action = dict(action)
                    action["farmer"] = out_farmer
                    action["hands"] = out_hands
    except Exception:
        _E259_FIRES["errors"] += 1
    return action


agent.telemetry = _E259_FIRES
agent.bycrop = _E259_BYCROP
'''


def build(layer, out_name):
    src = open(BASE_FILE, encoding="utf-8", errors="replace").read()
    out = src.rstrip("\n") + "\n" + layer
    path = os.path.join(ROOT, "agents", out_name)
    open(path, "w", encoding="utf-8", newline="\n").write(out)
    txt = open(path, encoding="utf-8").read()
    tag = out_name.split("_")[1].upper()
    assert txt.count("_%s_PARENT" % tag) == 2
    assert txt.count("agent.telemetry = _%s_FIRES" % tag) == 1
    import py_compile
    py_compile.compile(path, doraise=True)
    print(out_name, "bytes", len(out.encode("utf-8")),
          "delta", len(out.encode("utf-8")) - len(src.encode("utf-8")),
          "sha256", hashlib.sha256(out.encode("utf-8")).hexdigest()[:16], "py_compile PASS")
    return path


if __name__ == "__main__":
    build(LAYER_258, "tetsutani_e258_fertbuy_veto.py")
    build(LAYER_259, "tetsutani_e259_idle_replant.py")
    sys.exit(0)
