"""Dump full SELL timeline for both players across the whole replay."""
import json
import sys


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    steps = rep["steps"]
    print("step | P0 sells | P1 sells | STR px | MILK px | WOOL px")
    for si in range(len(steps)):
        s = steps[si]
        obs0 = s[0]["observation"]
        act0 = s[0].get("action")
        act1 = s[1].get("action")
        m0 = act0.get("market", []) if isinstance(act0, dict) else []
        m1 = act1.get("market", []) if isinstance(act1, dict) else []
        sl0 = [o for o in m0 if isinstance(o, (list, tuple)) and o and o[0] == "SELL"]
        sl1 = [o for o in m1 if isinstance(o, (list, tuple)) and o and o[0] == "SELL"]
        if sl0 or sl1:
            pr = obs0["market"]["prices"]
            print(
                f'{si:4d} | {sl0} | {sl1} | {pr["STRAWBERRY"]:3d} | {pr["MILK"]:3d} | {pr["WOOL"]:3d}'
            )


if __name__ == "__main__":
    main()
