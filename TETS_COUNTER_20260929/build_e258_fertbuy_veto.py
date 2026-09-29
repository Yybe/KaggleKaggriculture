"""E258 builder - second counter arm: veto paid fertilizer buys while produced fertilizer is idle.

Evidence (results/E257_TETS_FARM_FORENSICS_20260929.md §2): in the heaviest loss we bought 104
FERTILIZER units at market while leaving 486 doses uncollected on animals; the winner bought 17.
This arm touches only the market plan, never a hand, so it is orthogonal to E257.

Rule: drop a `["BUY_PRODUCT", "FERTILIZER", n]` order when the farm's own fertilizer position
(shed FERTILIZER + carried inventory across units) is >= n. Cash is kept, nothing is added.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_FILE = os.path.join(ROOT, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py")
OUT_FILE = os.path.join(ROOT, "agents", "tetsutani_e258_fertbuy_veto.py")

LAYER = '''

# --- E258 FERTILIZER-BUY VETO (keep cash when our own fertilizer is idle) ---
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
                seat = int(observation.get("player", 0) or 0)
                farms = observation.get("farms") or []
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


def main():
    src = open(BASE_FILE, encoding="utf-8", errors="replace").read()
    out = src.rstrip("\n") + "\n" + LAYER
    open(OUT_FILE, "w", encoding="utf-8", newline="\n").write(out)
    txt = open(OUT_FILE, encoding="utf-8").read()
    assert txt.count("_E258_PARENT") == 2
    assert txt.count("agent.telemetry = _E258_FIRES") == 1
    assert txt.count("def _e257_op_for") == 0
    print("out_bytes", len(out.encode("utf-8")), "delta",
          len(out.encode("utf-8")) - len(src.encode("utf-8")))
    print("sha256", hashlib.sha256(out.encode("utf-8")).hexdigest()[:16])
    import py_compile
    py_compile.compile(OUT_FILE, doraise=True)
    print("py_compile PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
