"""E257 builder - graft the fert-throughput counter layer onto the tetsutani spine.

Evidence (TETS_COUNTER_20260929/out/p04.txt, p05.txt; 17 heavy live losses, our seat vs the seat
that beat us): op_FERTILIZE -48.6 mean / -53 median (14 of 17 negative), tile_days_fert -1,226 mean,
op_COLLECT_FERTILIZER -108, op_FEED -71, op_PASS +112 (we idle hands they spend), and we BUY 104
FERTILIZER units while leaving animal fertilizer uncollected.

Engine legality (rank_env kaggriculture.py:475-521): FERTILIZE needs the standing tile to be a PLANT
and 1 FERTILIZER in that unit's own inventory; FEED needs an animal tile not fed_today and 1 WHEAT in
that unit's inventory; COLLECT_FERTILIZER needs an animal tile with fertilizer_available. Unit idx 0 is
the farmer (action['farmer']), idx i+1 is action['hands'][i]; position is [x, y] and the tile is
farm['tiles'][y][x]; inventory list is [farmer, *hands].

The layer only converts slots whose op is exactly ["PASS"], so it never displaces a committed tape op
and never issues a market order: cash-neutral by construction.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_FILE = os.path.join(ROOT, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py")
OUT_FILE = os.path.join(ROOT, "agents", "tetsutani_e257_fertflow.py")

LAYER = '''

# --- E257 FERT-THROUGHPUT COUNTER LAYER (idle hands -> collect/feed/fertilize) ---
_E257_PARENT = agent
del agent

_E257_FIRES = {"steps": 0, "collect": 0, "feed": 0, "fert": 0, "converted": 0, "errors": 0}


def _e257_op_for(tile, inv, day):
    if isinstance(tile, dict) and "animal" in tile:
        if tile.get("fertilizer_available"):
            return "COLLECT_FERTILIZER", "collect"
        if not tile.get("fed_today") and (inv.get("WHEAT", 0) or 0) >= 1:
            return "FEED", "feed"
        return None, None
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        if (tile.get("fertilized_until_day", -1) or -1) < day and (inv.get("FERTILIZER", 0) or 0) >= 1:
            return "FERTILIZE", "fert"
    return None, None


def agent(observation, configuration=None):
    action = _E257_PARENT(observation, configuration)
    try:
        _E257_FIRES["steps"] += 1
        if isinstance(action, dict):
            seat = int(observation.get("player", 0) or 0)
            farms = observation.get("farms") or []
            farm = farms[seat] if seat < len(farms) else {}
            tiles = farm.get("tiles") or []
            invs = (observation.get("private") or {}).get("inventories") or []
            day = int(observation.get("day", 0) or 0)
            pos = [farm.get("farmer") or [0, 0]] + list(farm.get("hands") or [])
            slots = [action.get("farmer")] + list(action.get("hands") or [])
            out_farmer = action.get("farmer")
            out_hands = list(action.get("hands") or [])
            for idx, cur in enumerate(slots):
                if not (isinstance(cur, list) and len(cur) == 1 and cur[0] == "PASS"):
                    continue
                if idx >= len(pos):
                    continue
                p = pos[idx]
                if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                    continue
                fx, fy = int(p[0]), int(p[1])
                if not (0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy])):
                    continue
                inv = invs[idx] if idx < len(invs) else {}
                op, kind = _e257_op_for(tiles[fy][fx], inv or {}, day)
                if not op:
                    continue
                _E257_FIRES[kind] += 1
                _E257_FIRES["converted"] += 1
                if idx == 0:
                    out_farmer = [op]
                else:
                    out_hands[idx - 1] = [op]
            action = dict(action)
            action["farmer"] = out_farmer
            action["hands"] = out_hands
    except Exception:
        _E257_FIRES["errors"] += 1
    return action


agent.telemetry = _E257_FIRES
'''


def main():
    src = open(BASE_FILE, encoding="utf-8", errors="replace").read()
    anchor = "\ndef agent(observation, configuration=None):"
    n_before = src.count(anchor)
    out = src.rstrip("\n") + "\n" + LAYER
    open(OUT_FILE, "w", encoding="utf-8", newline="\n").write(out)
    txt = open(OUT_FILE, encoding="utf-8").read()
    print("anchor_count src", n_before, "out", txt.count(anchor))
    assert txt.count(anchor) == n_before + 1, (n_before, txt.count(anchor))
    assert txt.count("_E257_PARENT") == 2, txt.count("_E257_PARENT")
    assert txt.count("_E257_FIRES") >= 6
    assert txt.count("def _e257_op_for") == 1
    assert txt.count("agent.telemetry = _E257_FIRES") == 1
    delta = len(out.encode("utf-8")) - len(src.encode("utf-8"))
    print("base_bytes", len(src.encode("utf-8")), "out_bytes", len(out.encode("utf-8")), "delta", delta)
    print("sha256", hashlib.sha256(out.encode("utf-8")).hexdigest()[:16])
    import py_compile
    py_compile.compile(OUT_FILE, doraise=True)
    print("py_compile PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
