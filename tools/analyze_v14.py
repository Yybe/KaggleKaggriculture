"""Decode and analyze V14's embedded action tape to understand its exact strategy."""
import base64
import json
import zlib
import os
from collections import Counter, defaultdict

# Load V14's action tape
import sys
sys.path.insert(0, r"c:\Users\xxshi\Desktop\farmmasterV2\agents")
from kaggle_boat84_v14 import _ACTIONS

print(f"V14 action tape: {len(_ACTIONS)} steps")

os.makedirs(r"c:\Users\xxshi\Desktop\farmmasterV2\seb_analysis", exist_ok=True)

# Analyze the action tape in detail
report = []
report.append("=" * 80)
report.append("V14 ACTION TAPE REVERSE ENGINEERING")
report.append("=" * 80)

# 1. Market orders analysis
all_market_orders = defaultdict(list)  # type -> [(step, details)]
land_buys = []
hires_by_day = defaultdict(int)
seed_buys = defaultdict(int)  # crop -> total
animal_buys = defaultdict(int)
product_buys = defaultdict(int)
sells = defaultdict(lambda: {"total_qty": 0, "steps": [], "qtys": []})

for step, action in enumerate(_ACTIONS):
    day = step // 24
    hour = step % 24
    market = action.get("market", []) or []
    for order in market:
        if not order:
            continue
        cmd = order[0]
        if cmd == "BUY_LAND":
            land_buys.append({"step": step, "day": day, "hour": hour})
        elif cmd == "HIRE":
            hires_by_day[day] += 1
        elif cmd == "BUY_SEED":
            item = order[1] if len(order) > 1 else "?"
            qty = int(order[2]) if len(order) > 2 else 1
            seed_buys[item] += qty
        elif cmd == "BUY_ANIMAL":
            item = order[1] if len(order) > 1 else "?"
            qty = int(order[2]) if len(order) > 2 else 1
            animal_buys[item] += qty
        elif cmd == "BUY_PRODUCT":
            item = order[1] if len(order) > 1 else "?"
            qty = int(order[2]) if len(order) > 2 else 1
            product_buys[item] += qty
        elif cmd == "SELL":
            item = order[1] if len(order) > 1 else "?"
            qty = int(order[2]) if len(order) > 2 else 0
            sells[item]["total_qty"] += qty
            sells[item]["steps"].append(step)
            sells[item]["qtys"].append(qty)
        all_market_orders[cmd].append({"step": step, "order": order})

# 2. Farmer/hand actions analysis
farmer_actions = Counter()
hand_actions = Counter()
farmer_by_phase = defaultdict(Counter)
farmer_actions_by_step = []

for step, action in enumerate(_ACTIONS):
    day = step // 24
    phase = min(day // 5, 5)
    farmer = action.get("farmer", ["PASS"]) or ["PASS"]
    farmer_cmd = farmer[0] if farmer else "PASS"
    farmer_actions[farmer_cmd] += 1
    farmer_by_phase[phase][farmer_cmd] += 1
    farmer_actions_by_step.append(farmer_cmd)
    
    hands = action.get("hands", []) or []
    for hand in hands:
        hand_cmd = hand[0] if hand else "PASS"
        hand_actions[hand_cmd] += 1

# 3. Hand count over time
hand_counts = []
for step, action in enumerate(_ACTIONS):
    hands = action.get("hands", []) or []
    hand_counts.append(len(hands))

# Report
report.append("\n--- LAND EXPANSION ---")
for lb in land_buys:
    # Find co-occurring orders in same step
    co_orders = [o["order"] for o in all_market_orders.get("SELL", []) if o["step"] == lb["step"]]
    co_orders += [o["order"] for o in all_market_orders.get("HIRE", []) if o["step"] == lb["step"]]
    report.append(f"  Step {lb['step']} (Day {lb['day']}, Hour {lb['hour']})")
    if co_orders:
        report.append(f"    Co-orders: {co_orders}")

report.append(f"\n  Total lands bought: {len(land_buys)}")
if land_buys:
    report.append(f"  Quadrants unlocked: NW (start) + {len(land_buys)} expansions")

report.append("\n--- HIRING ---")
total_hires = sum(hires_by_day.values())
report.append(f"  Total HIRE orders: {total_hires}")
for day in sorted(hires_by_day.keys()):
    report.append(f"  Day {day}: {hires_by_day[day]} hires")

report.append(f"\n  Max hands in tape: {max(hand_counts) if hand_counts else 0}")
report.append(f"  Avg hands: {sum(hand_counts)/len(hand_counts):.1f}")

report.append("\n--- SEED PURCHASES ---")
for item, qty in sorted(seed_buys.items(), key=lambda x: -x[1]):
    report.append(f"  {item}: {qty} seeds")

report.append("\n--- ANIMAL PURCHASES ---")
for item, qty in sorted(animal_buys.items(), key=lambda x: -x[1]):
    report.append(f"  {item}: {qty}")

report.append("\n--- PRODUCT PURCHASES (BUY_PRODUCT) ---")
for item, qty in sorted(product_buys.items(), key=lambda x: -x[1]):
    report.append(f"  {item}: {qty}")

report.append("\n--- SELL ORDERS ---")
for item in sorted(sells.keys()):
    s = sells[item]
    first_step = min(s["steps"]) if s["steps"] else -1
    last_step = max(s["steps"]) if s["steps"] else -1
    report.append(f"  {item}: total_qty={s['total_qty']}, n_orders={len(s['steps'])}, "
                  f"first_step={first_step} (day {first_step//24}), last_step={last_step} (day {last_step//24})")

# Sell timing breakdown
report.append("\n--- SELL TIMELINE (by day) ---")
sell_by_day = defaultdict(lambda: defaultdict(int))
for item, s in sells.items():
    for step, qty in zip(s["steps"], s["qtys"]):
        sell_by_day[step // 24][item] += qty

for day in sorted(sell_by_day.keys()):
    items_str = ", ".join(f"{k}:{v}" for k, v in sorted(sell_by_day[day].items(), key=lambda x: -x[1]))
    report.append(f"  Day {day}: {items_str}")

report.append("\n--- FARMER ACTIONS (overall) ---")
for cmd, count in farmer_actions.most_common():
    report.append(f"  {cmd}: {count} ({count/len(_ACTIONS)*100:.1f}%)")

report.append("\n--- FARMER ACTIONS (by phase) ---")
phase_names = ["D0-4", "D5-9", "D10-14", "D15-19", "D20-24", "D25-29"]
for phase in sorted(farmer_by_phase.keys()):
    name = phase_names[phase] if phase < len(phase_names) else f"D{phase*5}+"
    report.append(f"\n  {name}:")
    for cmd, count in farmer_by_phase[phase].most_common():
        report.append(f"    {cmd}: {count}")

report.append("\n--- HAND ACTIONS (overall) ---")
for cmd, count in hand_actions.most_common():
    report.append(f"  {cmd}: {count}")

# 4. Detect PLANT commands and what's planted
plant_timeline = defaultdict(list)
for step, action in enumerate(_ACTIONS):
    farmer = action.get("farmer", []) or []
    if farmer and farmer[0] == "PLANT" and len(farmer) > 1:
        plant_timeline[farmer[1]].append(step)
    for hand in (action.get("hands", []) or []):
        if hand and hand[0] == "PLANT" and len(hand) > 1:
            plant_timeline[hand[1]].append(step)

report.append("\n--- PLANTING TIMELINE ---")
for crop, steps in sorted(plant_timeline.items()):
    first_day = min(steps) // 24
    last_day = max(steps) // 24
    report.append(f"  {crop}: {len(steps)} plants, days {first_day}-{last_day}")
    # Show by day
    by_day = Counter(s // 24 for s in steps)
    for d in sorted(by_day.keys()):
        report.append(f"    Day {d}: {by_day[d]} plants")

# 5. BUILD_PASTURE and BUILD_COOP 
builds = defaultdict(list)
for step, action in enumerate(_ACTIONS):
    farmer = action.get("farmer", []) or []
    if farmer and farmer[0] in ("BUILD_PASTURE", "BUILD_COOP"):
        builds[farmer[0]].append(step)
    for hand in (action.get("hands", []) or []):
        if hand and hand[0] in ("BUILD_PASTURE", "BUILD_COOP"):
            builds[hand[0]].append(step)

report.append("\n--- STRUCTURE BUILDS ---")
for cmd, steps in sorted(builds.items()):
    first_day = min(steps) // 24
    last_day = max(steps) // 24
    report.append(f"  {cmd}: {len(steps)} builds, days {first_day}-{last_day}")

# 6. Key strategy summary
report.append("\n" + "=" * 80)
report.append("V14 STRATEGY SUMMARY")
report.append("=" * 80)
report.append(f"Total quadrants: NW + {len(land_buys)} = {1 + len(land_buys)}")
report.append(f"Total hires: {total_hires}")
report.append(f"Total seeds bought: {dict(seed_buys)}")
report.append(f"Total animals: {dict(animal_buys)}")
report.append(f"Total sells: { {k: v['total_qty'] for k, v in sells.items()} }")
report.append(f"Total BUY_PRODUCT: {dict(product_buys)}")

# Write report
report_text = "\n".join(report)
print(report_text)

with open(r"c:\Users\xxshi\Desktop\farmmasterV2\seb_analysis\v14_reverse_engineering.txt", "w") as f:
    f.write(report_text)

# Save raw data
v14_data = {
    "land_buys": land_buys,
    "hires_by_day": dict(hires_by_day),
    "seed_buys": dict(seed_buys),
    "animal_buys": dict(animal_buys),
    "product_buys": dict(product_buys),
    "sells": {k: {"total_qty": v["total_qty"], "n_orders": len(v["steps"]),
                   "first_step": min(v["steps"]) if v["steps"] else -1,
                   "last_step": max(v["steps"]) if v["steps"] else -1}
              for k, v in sells.items()},
    "farmer_actions": dict(farmer_actions),
    "hand_actions": dict(hand_actions),
    "plant_timeline_summary": {crop: {"count": len(steps), "first_day": min(steps)//24, "last_day": max(steps)//24}
                               for crop, steps in plant_timeline.items()},
    "total_hires": total_hires,
    "max_hands": max(hand_counts) if hand_counts else 0,
}

with open(r"c:\Users\xxshi\Desktop\farmmasterV2\seb_analysis\v14_data.json", "w") as f:
    json.dump(v14_data, f, indent=2)

print("\n\nSaved to seb_analysis/v14_reverse_engineering.txt and v14_data.json")
