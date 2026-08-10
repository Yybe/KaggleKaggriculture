"""
Deep Opening & Strategy Analysis
==================================
Reads the extraction output to produce the exact step-by-step playbook
for VersionWybe agent construction.
"""
import json, csv, os
from collections import defaultdict, Counter

OUT = r"C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\analysis_output"

# ---- Load data ----
with open(os.path.join(OUT, "opening_moves.json")) as f:
    openings = json.load(f)

with open(os.path.join(OUT, "strategy_profiles.json")) as f:
    profiles = json.load(f)

features = []
with open(os.path.join(OUT, "per_game_features.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        features.append(row)

sells = []
with open(os.path.join(OUT, "sell_log.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        sells.append(row)

buys = []
with open(os.path.join(OUT, "buy_log.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        buys.append(row)

# ==============================================================
# 1. HEALTHSTONE'S EXACT OPENING (Step 1 market orders, first 5 days)
# ==============================================================
print("=" * 70)
print("HEALTHSTONE OPENING ANALYSIS (Step 1 market orders)")
print("=" * 70)

hs_keys = [k for k in openings if "healthstone" in k]
hs_step1_markets = []
for key in hs_keys:
    moves = openings[key]
    for m in moves:
        if m["step"] == 1 and m.get("market"):
            hs_step1_markets.append(m["market"])
            break

# Aggregate step 1 market orders
print(f"\nAnalyzed {len(hs_step1_markets)} HealthStone games, step 1 market orders:")
hire_counts = []
seed_orders = []
animal_orders = []
for market in hs_step1_markets:
    hires = sum(1 for o in market if o and o[0] == "HIRE")
    seeds = [(o[1], o[2]) for o in market if o and o[0] == "BUY_SEED"]
    animals = [(o[1], o[2]) for o in market if o and o[0] == "BUY_ANIMAL"]
    hire_counts.append(hires)
    seed_orders.append(seeds)
    animal_orders.append(animals)

print(f"  Hires: min={min(hire_counts)} max={max(hire_counts)} avg={sum(hire_counts)/len(hire_counts):.1f}")
print(f"  Seed orders (first 5 games):")
for i, (s, a) in enumerate(zip(seed_orders[:5], animal_orders[:5])):
    print(f"    Game {i}: seeds={s}, animals={a}")

# Count seed type frequency across all games
all_seed_types = Counter()
all_seed_qtys = defaultdict(list)
all_animal_types = Counter()
all_animal_qtys = defaultdict(list)
for seeds in seed_orders:
    for stype, qty in seeds:
        all_seed_types[stype] += 1
        all_seed_qtys[stype].append(int(qty))
for animals in animal_orders:
    for atype, qty in animals:
        all_animal_types[atype] += 1
        all_animal_qtys[atype].append(int(qty))

print(f"\n  Step 1 Seed frequency: {dict(all_seed_types)}")
for stype, qtys in all_seed_qtys.items():
    print(f"    {stype}: avg qty={sum(qtys)/len(qtys):.1f}, range=[{min(qtys)},{max(qtys)}]")
print(f"  Step 1 Animal frequency: {dict(all_animal_types)}")
for atype, qtys in all_animal_qtys.items():
    print(f"    {atype}: avg qty={sum(qtys)/len(qtys):.1f}, range=[{min(qtys)},{max(qtys)}]")

# ==============================================================
# 2. SEB'S EXACT OPENING
# ==============================================================
print("\n" + "=" * 70)
print("SEB OPENING ANALYSIS (Step 1 market orders)")
print("=" * 70)

seb_keys = [k for k in openings if "seb" in k and "healthstone" not in k]
seb_step1_markets = []
for key in seb_keys:
    moves = openings[key]
    for m in moves:
        if m["step"] == 1 and m.get("market"):
            seb_step1_markets.append(m["market"])
            break

hire_counts_s = []
seed_orders_s = []
animal_orders_s = []
for market in seb_step1_markets:
    hires = sum(1 for o in market if o and o[0] == "HIRE")
    seeds = [(o[1], o[2]) for o in market if o and o[0] == "BUY_SEED"]
    animals = [(o[1], o[2]) for o in market if o and o[0] == "BUY_ANIMAL"]
    hire_counts_s.append(hires)
    seed_orders_s.append(seeds)
    animal_orders_s.append(animals)

print(f"\nAnalyzed {len(seb_step1_markets)} Seb games:")
print(f"  Hires: min={min(hire_counts_s)} max={max(hire_counts_s)} avg={sum(hire_counts_s)/len(hire_counts_s):.1f}")

all_seed_types_s = Counter()
all_seed_qtys_s = defaultdict(list)
all_animal_types_s = Counter()
all_animal_qtys_s = defaultdict(list)
for seeds in seed_orders_s:
    for stype, qty in seeds:
        all_seed_types_s[stype] += 1
        all_seed_qtys_s[stype].append(int(qty))
for animals in animal_orders_s:
    for atype, qty in animals:
        all_animal_types_s[atype] += 1
        all_animal_qtys_s[atype].append(int(qty))

print(f"  Step 1 Seed frequency: {dict(all_seed_types_s)}")
for stype, qtys in all_seed_qtys_s.items():
    print(f"    {stype}: avg qty={sum(qtys)/len(qtys):.1f}, range=[{min(qtys)},{max(qtys)}]")
print(f"  Step 1 Animal frequency: {dict(all_animal_types_s)}")
for atype, qtys in all_animal_qtys_s.items():
    print(f"    {atype}: avg qty={sum(qtys)/len(qtys):.1f}, range=[{min(qtys)},{max(qtys)}]")

# ==============================================================
# 3. FULL OPENING SEQUENCE (first 3 days = 72 steps)
# ==============================================================
print("\n" + "=" * 70)
print("HEALTHSTONE FULL OPENING (Steps 0-72, first 3 days)")
print("=" * 70)

# Pick the highest-reward HealthStone game for detailed sequence
hs_feat = [r for r in features if r["role"] == "healthstone"]
hs_feat.sort(key=lambda x: int(float(x["final_reward"])), reverse=True)
best_hs = hs_feat[0]
best_hs_key = [k for k in hs_keys if str(best_hs["episode_id"]) in k][0]
print(f"\nBest HealthStone game: ep={best_hs['episode_id']} reward={best_hs['final_reward']} margin={best_hs['margin']}")

best_hs_moves = openings[best_hs_key]
for m in best_hs_moves:
    if m["step"] <= 10 or (m.get("market") and len(m["market"]) > 0):
        farmer = m.get("farmer", "?")
        hands = m.get("hands", [])
        market = m.get("market", [])
        line = f"  Step {m['step']:3d} (D{m['day']}:H{m['hour']:02d})"
        if farmer:
            line += f" F={farmer}"
        if hands:
            hand_summary = [h[0] if isinstance(h, list) and h else "?" for h in hands]
            line += f" H={hand_summary}"
        if market:
            line += f" M={market}"
        print(line)

# ==============================================================
# 4. SELL TIMING PATTERNS
# ==============================================================
print("\n" + "=" * 70)
print("SELL PATTERNS BY PRODUCT (avg qty per game)")
print("=" * 70)

for label in ["healthstone", "seb"]:
    label_sells = [s for s in sells if s["player_label"] == label]
    products = defaultdict(lambda: defaultdict(int))
    game_count = len(set(s["episode_id"] for s in label_sells))
    for s in label_sells:
        day = int(s["day"])
        phase = "early(d0-9)" if day < 10 else "mid(d10-19)" if day < 20 else "late(d20-29)"
        products[s["item"]][phase] += int(s["qty"])

    print(f"\n{label.upper()} sell breakdown (total across {game_count} games):")
    for prod in sorted(products.keys()):
        phases = products[prod]
        total = sum(phases.values())
        print(f"  {prod:15s}: early={phases.get('early(d0-9)',0):5d}  mid={phases.get('mid(d10-19)',0):5d}  late={phases.get('late(d20-29)',0):5d}  total={total:5d}  avg/game={total/game_count:.0f}")

# ==============================================================
# 5. BUY PATTERNS (seed/animal purchases over time)
# ==============================================================
print("\n" + "=" * 70)
print("BUY PATTERNS BY PRODUCT")
print("=" * 70)

for label in ["healthstone", "seb"]:
    label_buys = [b for b in buys if b["player_label"] == label]
    products = defaultdict(lambda: defaultdict(int))
    game_count = len(set(b["episode_id"] for b in label_buys))
    for b in label_buys:
        day = int(b["day"])
        phase = "early(d0-4)" if day < 5 else "mid(d5-14)" if day < 15 else "late(d15-29)"
        products[b["item"]][phase] += int(b["qty"])

    print(f"\n{label.upper()} buy breakdown (total across {game_count} games):")
    for prod in sorted(products.keys()):
        phases = products[prod]
        total = sum(phases.values())
        print(f"  {prod:15s}: early={phases.get('early(d0-4)',0):5d}  mid={phases.get('mid(d5-14)',0):5d}  late={phases.get('late(d15-29)',0):5d}  total={total:5d}  avg/game={total/game_count:.0f}")

# ==============================================================
# 6. FARMER ACTION ON STEP 1 (what does farmer do while market buys?)
# ==============================================================
print("\n" + "=" * 70)
print("FARMER ACTION ON STEP 1")
print("=" * 70)

for label, keys in [("healthstone", hs_keys), ("seb", seb_keys)]:
    farmer_step1 = Counter()
    for key in keys:
        moves = openings[key]
        for m in moves:
            if m["step"] == 1:
                f = m.get("farmer")
                if isinstance(f, list) and f:
                    farmer_step1[f[0]] += 1
                elif isinstance(f, str):
                    farmer_step1[f] += 1
                break
    print(f"  {label}: {dict(farmer_step1)}")

# ==============================================================
# 7. HEAD-TO-HEAD: SEB vs HEALTHSTONE (from manifest)
# ==============================================================
print("\n" + "=" * 70)
print("HEAD-TO-HEAD: SEB vs HEALTHSTONE")
print("=" * 70)

with open(r"C:\Users\xxshi\Desktop\FARMMASTER\replays_new\manifest.json") as f:
    manifest = json.load(f)

seb_vs_hs = [e for e in manifest["seb"] if e["oppTeamName"] == "HealthStone"]
print(f"\nSeb vs HealthStone ({len(seb_vs_hs)} games):")
seb_wins = 0
for g in seb_vs_hs:
    result = "WIN" if g["won"] else "LOSS"
    margin = g["myReward"] - g["oppReward"]
    if g["won"]: seb_wins += 1
    print(f"  ep={g['episodeId']} Seb={g['myReward']:,} vs HS={g['oppReward']:,} margin={margin:+,} {result}")

print(f"\nSeb wins: {seb_wins}/{len(seb_vs_hs)} = {seb_wins/len(seb_vs_hs)*100:.0f}%")

# Also check HealthStone vs Seb (from HS perspective)
hs_vs_seb = [e for e in manifest["healthstone"] if "Sebastian" in e.get("oppTeamName", "")]
print(f"\nHealthStone vs Seb ({len(hs_vs_seb)} games):")
hs_wins = 0
for g in hs_vs_seb:
    result = "WIN" if g["won"] else "LOSS"
    margin = g["myReward"] - g["oppReward"]
    if g["won"]: hs_wins += 1
    print(f"  ep={g['episodeId']} HS={g['myReward']:,} vs Seb={g['oppReward']:,} margin={margin:+,} {result}")

if hs_vs_seb:
    print(f"\nHS wins vs Seb: {hs_wins}/{len(hs_vs_seb)} = {hs_wins/len(hs_vs_seb)*100:.0f}%")

print("\n\nDONE.")
