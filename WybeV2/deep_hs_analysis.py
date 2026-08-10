"""Extract HealthStone's full game action pattern across all 720 steps."""
import json, os
from collections import defaultdict, Counter

OUT = r"C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\analysis_output"
HS_DIR = r"C:\Users\xxshi\Desktop\FARMMASTER\replays_new\healthstone"

# Load one representative HealthStone game (the one with highest reward in a WIN)
manifest = json.load(open(r"C:\Users\xxshi\Desktop\FARMMASTER\replays_new\manifest.json"))
hs_wins = [e for e in manifest["healthstone"] if e["won"]]
hs_wins.sort(key=lambda x: x["myReward"], reverse=True)
best = hs_wins[0]
print(f"Analyzing HealthStone game ep={best['episodeId']} (reward={best['myReward']:,}, vs {best['oppTeamName']})")

fpath = os.path.join(HS_DIR, f"episode-{best['episodeId']}-replay.json")
replay = json.load(open(fpath))
steps = replay["steps"]

# Figure out HealthStone's seat
final_r = [steps[-1][i]["reward"] for i in range(2)]
seat = 0 if abs(final_r[0] - best["myReward"]) < abs(final_r[1] - best["myReward"]) else 1
print(f"HealthStone is seat {seat}, final rewards: {final_r}")

# Track all market orders with their day/step
print("\n=== ALL MARKET BUY ORDERS (non-SELL, non-HIRE) ===")
for t in range(len(steps)):
    act = steps[t][seat].get("action", {}) or {}
    if not isinstance(act, dict): continue
    market = act.get("market", []) or []
    for m in market:
        if not isinstance(m, (list, tuple)) or len(m) < 1: continue
        if m[0] in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT", "EXPAND_LAND"):
            obs = steps[t][seat].get("observation", {}) or {}
            day = obs.get("day", t // 24)
            hour = obs.get("hour", t % 24)
            print(f"  Step {t:3d} (D{day}:H{hour:02d}) {m}")

# Track when HIRES happen
print("\n=== ALL HIRE ORDERS ===")
hire_steps = []
for t in range(len(steps)):
    act = steps[t][seat].get("action", {}) or {}
    if not isinstance(act, dict): continue
    market = act.get("market", []) or []
    hires = sum(1 for m in market if isinstance(m, (list, tuple)) and m and m[0] == "HIRE")
    if hires > 0:
        obs = steps[t][seat].get("observation", {}) or {}
        day = obs.get("day", t // 24)
        hire_steps.append((t, day, hires))
        if t <= 50 or hires > 1:
            print(f"  Step {t:3d} (D{day}) hires={hires}")

total_hires = sum(h for _, _, h in hire_steps)
print(f"  Total hires: {total_hires} across {len(hire_steps)} steps")
print(f"  Hires by day: ", end="")
by_day = defaultdict(int)
for _, d, h in hire_steps:
    by_day[d] += h
for d in sorted(by_day): print(f"D{d}={by_day[d]} ", end="")
print()

# Track farmer+hand action types by day range
print("\n=== ACTION TYPE FREQUENCY BY PHASE ===")
for phase_name, start, end in [("D0-2", 0, 72), ("D3-9", 72, 240), ("D10-19", 240, 480), ("D20-29", 480, 720)]:
    actions = Counter()
    for t in range(start, min(end, len(steps))):
        act = steps[t][seat].get("action", {}) or {}
        if not isinstance(act, dict): continue
        farmer = act.get("farmer")
        if isinstance(farmer, list) and farmer:
            actions[farmer[0]] += 1
        for h in (act.get("hands") or []):
            if isinstance(h, list) and h:
                actions[h[0]] += 1
    print(f"  {phase_name}: {dict(actions.most_common(15))}")

# Track SELL orders by day
print("\n=== SELL SCHEDULE (by day) ===")
sell_by_day = defaultdict(lambda: defaultdict(int))
for t in range(len(steps)):
    act = steps[t][seat].get("action", {}) or {}
    if not isinstance(act, dict): continue
    market = act.get("market", []) or []
    for m in market:
        if isinstance(m, (list, tuple)) and len(m) >= 3 and m[0] == "SELL":
            obs = steps[t][seat].get("observation", {}) or {}
            day = obs.get("day", t // 24)
            sell_by_day[day][m[1]] += int(m[2])

for d in sorted(sell_by_day):
    items = sell_by_day[d]
    total = sum(items.values())
    detail = ", ".join(f"{k}={v}" for k, v in sorted(items.items(), key=lambda x: -x[1]))
    print(f"  Day {d:2d}: total={total:4d}  [{detail}]")

# Track cash + animal count progression
print("\n=== CASH & FARM PROGRESSION ===")
for t in range(0, min(720, len(steps)), 24):  # Every day boundary
    obs = steps[t][seat].get("observation", {}) or {}
    farms = obs.get("farms", [])
    if seat < len(farms):
        farm = farms[seat]
        money = farm.get("money", 0)
        hands = len(farm.get("hands", []) or [])
        tiles = farm.get("tiles", []) or []
        animals = sum(1 for t in tiles if isinstance(t, dict) and t.get("kind") == "ANIMAL")
        plants = sum(1 for t in tiles if isinstance(t, dict) and t.get("kind") == "PLANT")
        quads = farm.get("unlocked_quadrants", "?")
        if isinstance(quads, list): quads = len(quads)
        day = obs.get("day", t // 24)
        print(f"  Day {day:2d}: cash=${money:8,.0f}  hands={hands}  animals={animals}  plants={plants}  quads={quads}")
