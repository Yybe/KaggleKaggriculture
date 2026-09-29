"""E261 - restricted idle-land replant, built from exactly what refuted E259.

E259 (H-085) planted any owned-empty tile under any idle hand: pooled mean +615.5/seat but median
-2,101.5, win share 9/32, worst row -31,280, and -5,959/seat on `a15_full_wheat`. Two worlds carried the
mean, and the losses are the tile's claim on the tape's water/labor budget. So the reopen condition was a
restriction to land the tape has genuinely abandoned, worked only while there is still time to recoup.

Construction (one layer, three gates):
  gate 1  the tile must have been observed empty under our own control for >= 96 consecutive steps
          (4 days) - tracked per episode in module state, reset at step 0;
  gate 2  only days 12..27 (post-commitment window, still >= 3 days of yields left);
  gate 3  only crops we hold >= 5 seeds of, ordered STRAWBERRY > WHEAT (the two the spine actually
          waters on its own routes - no tomato, whose water budget the tape does not carry).
Hand must still be exactly ["PASS"], tile must still be None: never displaces a committed op, never
issues a market order.

Bar (fixed before reading numbers, same as E260): pooled paired absolute mean > 0, no lineage mean
below -1,000/seat, no row worse than -2,500, win share >= 50 %.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_FILE = os.path.join(ROOT, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py")
OUT_FILE = os.path.join(ROOT, "agents", "tetsutani_e261_abandoned_replant.py")

LAYER = '''

# --- E261 ABANDONED-LAND REPLANT (4-day-idle tiles, days 12-27, own surplus seeds) ---
_E261_PARENT = agent
del agent

_E261_IDLE_STEPS = 96
_E261_DAY_LO = 12
_E261_DAY_HI = 27
_E261_MIN_SEEDS = 5
_E261_ORDER = ("STRAWBERRY", "WHEAT")
_E261_FIRES = {"steps": 0, "converted": 0, "errors": 0}
_E261_BYCROP = {}
_E261_IDLE_SINCE = {}


def agent(observation, configuration=None):
    action = _E261_PARENT(observation, configuration)
    try:
        step = int(observation.get("step", 0) or 0)
        if step == 0:
            _E261_IDLE_SINCE.clear()
        _E261_FIRES["steps"] += 1
        if isinstance(action, dict):
            seat = int(observation.get("player", 0) or 0)
            farms = observation.get("farms") or []
            farm = farms[seat] if seat < len(farms) else {}
            tiles = farm.get("tiles") or []
            day = int(observation.get("day", step // 24) or 0)
            seeds = (observation.get("private") or {}).get("seeds") or {}
            pos = [farm.get("farmer") or [0, 0]] + list(farm.get("hands") or [])
            # record abandonment age for every owned-empty tile we can see
            for fy, row in enumerate(tiles):
                for fx, t in enumerate(row):
                    if t is None:
                        _E261_IDLE_SINCE.setdefault((fy, fx), step)
                    else:
                        _E261_IDLE_SINCE.pop((fy, fx), None)
            if _E261_DAY_LO <= day <= _E261_DAY_HI:
                slots = [action.get("farmer")] + list(action.get("hands") or [])
                out_farmer = action.get("farmer")
                out_hands = list(action.get("hands") or [])
                used = {}
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
                    if tiles[fy][fx] is not None:
                        continue
                    first = _E261_IDLE_SINCE.get((fy, fx))
                    if first is None or step - first < _E261_IDLE_STEPS:
                        continue
                    crop = None
                    for c in _E261_ORDER:
                        if (seeds.get(c, 0) or 0) - used.get(c, 0) >= _E261_MIN_SEEDS:
                            crop = c
                            break
                    if not crop:
                        break
                    if idx == 0:
                        out_farmer = ["PLANT", crop]
                    else:
                        out_hands[idx - 1] = ["PLANT", crop]
                    used[crop] = used.get(crop, 0) + 1
                    _E261_FIRES["converted"] += 1
                    _E261_BYCROP[crop] = _E261_BYCROP.get(crop, 0) + 1
                    _E261_IDLE_SINCE.pop((fy, fx), None)
                if used:
                    action = dict(action)
                    action["farmer"] = out_farmer
                    action["hands"] = out_hands
    except Exception:
        _E261_FIRES["errors"] += 1
    return action


agent.telemetry = _E261_FIRES
agent.bycrop = _E261_BYCROP
'''


def main():
    src = open(BASE_FILE, encoding="utf-8", errors="replace").read()
    out = src.rstrip("\n") + "\n" + LAYER
    open(OUT_FILE, "w", encoding="utf-8", newline="\n").write(out)
    txt = open(OUT_FILE, encoding="utf-8").read()
    assert txt.count("_E261_PARENT") == 2
    assert txt.count("agent.telemetry = _E261_FIRES") == 1
    print("e261 bytes", len(out.encode("utf-8")), "delta",
          len(out.encode("utf-8")) - len(src.encode("utf-8")),
          "sha256", hashlib.sha256(out.encode("utf-8")).hexdigest()[:16])
    import py_compile
    py_compile.compile(OUT_FILE, doraise=True)
    print("py_compile PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
