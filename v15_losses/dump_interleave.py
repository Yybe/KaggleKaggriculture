"""Extract per-step market order lists + prices from a replay to verify lockstep interleaving.

For each step in the late game (>= 480), print both players' FULL market order lists
(position order matters!) plus market prices. This reveals whether V15's SELL orders
sit at different positions/steps than the opponent's, causing systematic price damage.
"""
import json
import sys


def load_replay(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 680
    if not path:
        print("usage: dump_interleave.py <replay.json> [start_step]")
        return
    rep = load_replay(path)
    steps = rep["steps"]
    print(f"total steps in replay: {len(steps)}")

    for si in range(start, len(steps)):
        s = steps[si]
        obs0 = s[0]["observation"]
        obs1 = s[1]["observation"]
        act0 = s[0].get("action")
        act1 = s[1].get("action")
        m0 = act0.get("market", []) if isinstance(act0, dict) else []
        m1 = act1.get("market", []) if isinstance(act1, dict) else []
        # only print steps with market activity
        if not m0 and not m1:
            continue
        inv = obs0["market"]["inventory"]
        pr = obs0["market"]["prices"]
        print(f"\n=== step {si} (day {obs0.get('day')} hour {obs0.get('hour')}) ===")
        print(f"  P0 market: {m0}")
        print(f"  P1 market: {m1}")
        for item in ("WHEAT", "FERTILIZER", "STRAWBERRY", "MILK", "WOOL", "MELON"):
            print(f"    {item}: inv={inv[item]} price={pr[item]}")
        # print positions of SELL orders for both players
        for pid, m in ((0, m0), (1, m1)):
            sells = [(i, o) for i, o in enumerate(m) if isinstance(o, (list, tuple)) and o and o[0] == "SELL"]
            if sells:
                print(f"  P{pid} SELL positions: {sells}")
        m0m = obs0.get("farms", [{}])
        m1m = obs1.get("farms", [{}])
        if m0m and m1m:
            print(f"  money: P0={m0m[0].get('money')} P1={m0m[1].get('money')}")


if __name__ == "__main__":
    main()
