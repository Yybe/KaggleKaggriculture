"""Forensic analyzer for live kaggriculture episode replays (UVM-2 era).

For each replay JSON in a directory, extract:
  - final rewards/delta and our seat (by team name)
  - our PASS/idle streaks (crash or stall detection)
  - end-state farm composition per player (quadrants, hands, crops, animals)
  - total SELL volume per item per player
  - average realized price proxy: sum(qty) split by step bucket x item
Writes results/<out>.json + prints a compact table.

Usage:
  python tools/analyze_live_replays.py <replay_dir> <out_json>
"""
import glob
import json
import os
import sys
from collections import defaultdict

OUR_NAMES = {"shivam_2212", "shivam2212"}
ITEMS = ("STRAWBERRY", "MILK", "WOOL", "WHEAT", "MELON", "TOMATO", "CARROT", "EGG", "FERTILIZER")
SELL_BUCKETS = ((0, 240), (240, 456), (456, 648), (648, 720))


def our_seat(data):
    names = [str(n).lower() for n in data.get("info", {}).get("TeamNames", [])]
    for i, n in enumerate(names):
        if any(o in n for o in OUR_NAMES):
            return i
    return 0


def count_tiles(farm):
    crops = defaultdict(int)
    animals = defaultdict(int)
    quadrants = len(farm.get("unlocked_quadrants", []) or [])
    hands = len(farm.get("hands", []) or [])
    for row in farm.get("tiles", []) or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            if tile.get("crop"):
                crops[tile["crop"]] += 1
            if tile.get("animal"):
                animals[tile["animal"]] += 1
    return {"quadrants": quadrants, "hands": hands, "crops": dict(crops), "animals": dict(animals), "money": farm.get("money", 0)}


def analyze(path):
    data = json.load(open(path, encoding="utf-8"))
    seat = our_seat(data)
    rewards = data.get("rewards", [])
    steps = data.get("steps", [])
    if len(rewards) < 2 or not steps:
        return None
    opp = 1 - seat

    # market prices (public, same for both seats) + inventory
    last_step = steps[-1][seat]
    obs_last = last_step.get("observation", {})
    farms_last = obs_last.get("farms", [])
    own_end = count_tiles(farms_last[seat]) if len(farms_last) > seat else {}
    opp_end = count_tiles(farms_last[opp]) if len(farms_last) > opp else {}

    sells = {0: defaultdict(int), 1: defaultdict(int)}
    sells_bucket = {0: defaultdict(int), 1: defaultdict(int)}
    idle_turns = {0: 0, 1: 0}
    pass_streak = {0: 0, 1: 0}
    max_pass_streak = {0: 0, 1: 0}
    price_at_sell = defaultdict(list)
    our_action_count = 0

    for idx, step in enumerate(steps):
        market = None
        for s in (0, 1):
            entry = step[s]
            action = entry.get("action") or {}
            if not isinstance(action, dict):
                continue
            market_orders = action.get("market") or []
            for order in market_orders:
                if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                    item, qty = order[1], int(order[2] or 0)
                    sells[s][item] += qty
                    for b0, b1 in SELL_BUCKETS:
                        if b0 <= idx < b1:
                            sells_bucket[s][f"{item}_{b0}_{b1}"] += qty
            farmer_action = action.get("farmer", ["PASS"])
            hands = action.get("hands") or []
            units = [farmer_action] + list(hands)
            unit_moves = [u for u in units if isinstance(u, list) and u and u[0] != "PASS"]
            if not unit_moves and not market_orders:
                pass_streak[s] += 1
                max_pass_streak[s] = max(max_pass_streak[s], pass_streak[s])
            else:
                pass_streak[s] = 0
            if s == seat:
                our_action_count += 1
        obs = step[0].get("observation", {})
        m = obs.get("market", {}) or {}
        prices = m.get("prices", {}) or {}
        market = prices

    for item in ITEMS:
        for s in (0, 1):
            pass
    result = {
        "episode_id": data.get("id"),
        "file": os.path.basename(path),
        "seed": data.get("info", {}).get("seed"),
        "our_seat": seat,
        "rewards": rewards,
        "delta": rewards[seat] - rewards[opp],
        "own_end": own_end,
        "opp_end": opp_end,
        "own_total_sell": dict(sells[seat]),
        "opp_total_sell": dict(sells[opp]),
        "own_sell_buckets": dict(sells_bucket[seat]),
        "opp_sell_buckets": dict(sells_bucket[opp]),
        "max_pass_streak_own": max_pass_streak[seat],
        "max_pass_streak_opp": max_pass_streak[opp],
        "idle_turns_own": idle_turns[seat],
        "n_steps": len(steps),
    }
    return result


def main():
    replay_dir, out_json = sys.argv[1], sys.argv[2]
    results = []
    for path in sorted(glob.glob(os.path.join(replay_dir, "episode-*-replay.json"))):
        try:
            row = analyze(path)
            if row:
                results.append(row)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {os.path.basename(path)}: {exc}")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)

    wins = [r for r in results if r["delta"] > 0]
    losses = [r for r in results if r["delta"] < 0]
    ties = [r for r in results if r["delta"] == 0]
    print(f"analyzed={len(results)} W={len(wins)} L={len(losses)} T={len(ties)}")

    def fmt(r):
        own, opp = r["own_end"], r["opp_end"]
        return (
            f"delta={r['delta']:>8.0f} q={str(r['own_end'].get('quadrants')):>1}/{r['opp_end'].get('quadrants')} "
            f"hands={own.get('hands')}/{opp.get('hands')} "
            f"crops={sum(own.get('crops', {}).values())}/{sum(opp.get('crops', {}).values())} "
            f"animals={sum(own.get('animals', {}).values())}/{sum(opp.get('animals', {}).values())} "
            f"pass_own={r['max_pass_streak_own']} pass_opp={r['max_pass_streak_opp']}"
        )

    losses.sort(key=lambda r: r["delta"])
    print("\n== 20 worst losses ==")
    for r in losses[:20]:
        print(os.path.basename(r["file"])[:36], fmt(r))
    print("\n== ties ==")
    for r in ties:
        print(os.path.basename(r["file"])[:36], fmt(r))
    print("\n== biggest wins ==")
    wins.sort(key=lambda r: -r["delta"])
    for r in wins[:10]:
        print(os.path.basename(r["file"])[:36], fmt(r))


if __name__ == "__main__":
    main()
