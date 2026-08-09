"""Dump final-day farmer actions, shed contents, STR plant state for both players."""
import json
import sys


def main():
    path = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 710
    with open(path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    steps = rep["steps"]
    for si in range(start, len(steps)):
        s = steps[si]
        for pid in (0, 1):
            e = s[pid]
            obs = e["observation"]
            act = e.get("action")
            priv = obs.get("private", {}) or {}
            shed = priv.get("shed", {}) or {}
            farm = obs["farms"][pid]
            tiles = farm.get("tiles") or []
            n_str = 0
            str_yield = 0
            for row in tiles:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY":
                        n_str += 1
                        str_yield += int(t.get("yield_units", 0) or 0)
            farmer = act.get("farmer") if act else None
            print(
                "step %d P%d: act=%s shed.STR=%d shed.MILK=%d STRplants=%d STRyield=%d"
                % (si, pid, farmer, shed.get("STRAWBERRY", 0), shed.get("MILK", 0), n_str, str_yield)
            )
        print()


if __name__ == "__main__":
    main()
