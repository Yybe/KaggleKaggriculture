"""E260 - counter arm built from the E257 reject reason (the reopen condition in H-083).

H-083 measured that idle-hand COLLECT_FERTILIZER loses 367/seat because the shed caps at 100 units and
collected fertilizer displaces produce. So the collection only pays if it comes with a release valve.
Release valve exists in the replay data: `TOWN_CENTER_PRODUCTS` excludes FERTILIZER
(`kaggriculture.py:114`), so fertilizer can only leave via a market SELL order - and the winning seats in
our heavy losses sell ~11x more fertilizer than we do (112,366 vs 10,200 units summed over 17 episodes).

Mechanism (one arm, two coupled legs, both dict-correct):
  leg 1  idle hand (committed op exactly ["PASS"]) standing on an animal tile whose
         `fertilizer_available` is true -> COLLECT_FERTILIZER;
  leg 2  when shed FERTILIZER exceeds the KEEP floor, append `["SELL","FERTILIZER",qty]` to
         `action['market']` (qty capped per step) so the collected stock leaves the shed.

Probe asserts BOTH legs mutate (converted > 0 and sell_added > 0): a collect-only arm is H-083 again.
Gate bar (fixed now, before reading numbers): pooled paired absolute mean > 0, no lineage mean below
-1,000/seat, no row worse than -2,500, win share >= 50 %. Anything else is a reject - no deploy, no
submit, submission.py untouched.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_FILE = os.path.join(ROOT, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py")
OUT_FILE = os.path.join(ROOT, "agents", "tetsutani_e260_collect_dump.py")

LAYER = '''

# --- E260 COLLECT-AND-DUMP FERTILIZER (idle hands in, market order out) ---
_E260_PARENT = agent
del agent

_E260_KEEP = 5
_E260_MAX_SELL_PER_STEP = 12
_E260_FIRES = {"steps": 0, "collect": 0, "sell_orders": 0, "sell_units": 0, "errors": 0}


def agent(observation, configuration=None):
    action = _E260_PARENT(observation, configuration)
    try:
        _E260_FIRES["steps"] += 1
        if isinstance(action, dict):
            seat = int(observation.get("player", 0) or 0)
            farms = observation.get("farms") or []
            farm = farms[seat] if seat < len(farms) else {}
            private = observation.get("private") or {}
            shed = private.get("shed") or {}
            tiles = farm.get("tiles") or []
            # leg 1: collect with idle hands only
            pos = [farm.get("farmer") or [0, 0]] + list(farm.get("hands") or [])
            slots = [action.get("farmer")] + list(action.get("hands") or [])
            out_farmer = action.get("farmer")
            out_hands = list(action.get("hands") or [])
            got = 0
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
                t = tiles[fy][fx]
                if isinstance(t, dict) and "animal" in t and t.get("fertilizer_available"):
                    if idx == 0:
                        out_farmer = ["COLLECT_FERTILIZER"]
                    else:
                        out_hands[idx - 1] = ["COLLECT_FERTILIZER"]
                    got += 1
            if got:
                _E260_FIRES["collect"] += got
                action = dict(action)
                action["farmer"] = out_farmer
                action["hands"] = out_hands
            # leg 2: dump the surplus so the shed stays open (cadenced so we do not flood our own price)
            step = int(observation.get("step", 0) or 0)
            stock = int(shed.get("FERTILIZER", 0) or 0)
            if stock > _E260_KEEP and step % 4 == 3:
                qty = min(stock - _E260_KEEP, _E260_MAX_SELL_PER_STEP)
                mk = list(action.get("market") or [])
                mk.append(["SELL", "FERTILIZER", qty])
                action = dict(action)
                action["market"] = mk
                _E260_FIRES["sell_orders"] += 1
                _E260_FIRES["sell_units"] += qty
    except Exception:
        _E260_FIRES["errors"] += 1
    return action


agent.telemetry = _E260_FIRES
'''


def main():
    src = open(BASE_FILE, encoding="utf-8", errors="replace").read()
    out = src.rstrip("\n") + "\n" + LAYER
    open(OUT_FILE, "w", encoding="utf-8", newline="\n").write(out)
    txt = open(OUT_FILE, encoding="utf-8").read()
    assert txt.count("_E260_PARENT") == 2
    assert txt.count("agent.telemetry = _E260_FIRES") == 1
    print("e260 bytes", len(out.encode("utf-8")), "delta",
          len(out.encode("utf-8")) - len(src.encode("utf-8")),
          "sha256", hashlib.sha256(out.encode("utf-8")).hexdigest()[:16])
    import py_compile
    py_compile.compile(OUT_FILE, doraise=True)
    print("py_compile PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
