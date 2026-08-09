import json
import glob
import os
import sys
from collections import defaultdict, Counter
import math

REPLAY_DIR = r"c:\Users\xxshi\Desktop\farmmasterV2\SEB'S gameplay\*.json"
OUTPUT_DIR = r"c:\Users\xxshi\Desktop\farmmasterV2\seb_analysis"

os.makedirs(OUTPUT_DIR, exist_ok=True)

all_replays = glob.glob(REPLAY_DIR)

aggregated = {
    "games_analyzed": 0,
    "wins": 0, "losses": 0, "ties": 0,
    "final_banks": [],
    "margins": [],
    "quadrant_unlock_times": [],
    "market_orders": Counter(),
    "sell_by_product": defaultdict(list), # product -> list of amounts sold
    "buy_product": defaultdict(list),
    "buy_seed": defaultdict(list),
    "buy_animal": defaultdict(list),
    "hiring_per_day": defaultdict(list),
    "action_freq_farmer": Counter(),
    "action_freq_hands": Counter(),
    "action_freq_farmer_phase": {i: Counter() for i in range(6)},
    "action_freq_hands_phase": {i: Counter() for i in range(6)},
    "harvested": Counter(),
    "wheat_sold": 0,
    "wheat_fed": 0,
    "peak_crop_counts": defaultdict(list),
    "peak_animal_counts": defaultdict(list),
    "total_hiring_cost": 0,
    "total_revenue": 0
}

game_details = []

def get_seb_seat(info):
    if "TeamNames" in info:
        teams = info["TeamNames"]
        if "seb" in teams[0].lower(): return 0
        if "seb" in teams[1].lower(): return 1
    if "Agents" in info:
        agents = info["Agents"]
        if "seb" in agents[0].lower(): return 0
        if "seb" in agents[1].lower(): return 1
    return 0

def get_phase(day):
    if day < 5: return 0
    if day < 10: return 1
    if day < 15: return 2
    if day < 20: return 3
    if day < 25: return 4
    return 5

def count_tiles(tiles):
    counts = Counter()
    for row in tiles:
        for cell in row:
            if not cell: continue
            if isinstance(cell, str):
                counts[cell] += 1
            elif isinstance(cell, dict):
                # E.g. {"type": "WHEAT", ...} or similar
                if "type" in cell:
                    counts[cell["type"]] += 1
                elif "name" in cell:
                    counts[cell["name"]] += 1
    return counts

# Standard prices for calculations (approximate, adjust as needed)
# Using generic logic: we track actual money changes if possible, but the game has standard prices.
# Better to track money diff, but it might be mixed. We will just use standard heuristics or track actual amounts.

for replay_idx, path in enumerate(all_replays):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        seb_seat = get_seb_seat(data.get("info", {}))
            
        steps = data.get("steps", [])
        if not steps: continue
        
        game_data = {
            "file": os.path.basename(path),
            "seb_seat": seb_seat,
            "bank_timeline": [],
            "daily_income_sell": defaultdict(int),
            "daily_spending": defaultdict(int),
            "quadrant_unlocks": [],
            "market_orders_log": [],
            "daily_farm_composition": {},
            "harvested": Counter(),
            "sold": Counter(),
            "bought": Counter(),
            "seeds_bought": Counter(),
            "animals_bought": Counter(),
            "shed_inventory_snapshots": {},
            "total_hiring_cost": 0,
            "total_revenue": 0
        }
        
        last_money = 0
        
        for step_idx, step_state in enumerate(steps):
            if not step_state or len(step_state) <= seb_seat: continue
            
            player_state = step_state[seb_seat]
            obs = player_state.get("observation", {})
            action = player_state.get("action", {})
            
            day = obs.get("day", step_idx // 24)
            phase = get_phase(day)
            
            farms = obs.get("farms", [])
            seb_farm = farms[seb_seat] if seb_seat < len(farms) else {}
            money = seb_farm.get("money", 0)
            
            game_data["bank_timeline"].append(money)
            
            # Market actions
            market_actions = action.get("market", [])
            
            for m_act in market_actions:
                if not m_act: continue
                if isinstance(m_act, str):
                    parts = m_act.split()
                else:
                    parts = [str(x) for x in m_act]
                    
                if not parts: continue
                cmd = parts[0]
                game_data["market_orders_log"].append({"step": step_idx, "day": day, "order": parts})
                aggregated["market_orders"][cmd] += 1
                
                if cmd == "BUY_LAND":
                    other_orders = [o for o in market_actions if (isinstance(o, str) and not o.startswith("BUY_LAND")) or (isinstance(o, list) and len(o)>0 and o[0] != "BUY_LAND")]
                    game_data["quadrant_unlocks"].append({"step": step_idx, "day": day, "batch": other_orders})
                    aggregated["quadrant_unlock_times"].append(step_idx)
                elif cmd == "SELL":
                    if len(parts) >= 3:
                        prod = parts[1]
                        qty = int(parts[2])
                        game_data["sold"][prod] += qty
                        aggregated["sell_by_product"][prod].append(qty)
                        # We don't have exact prices without hardcoding, so we assume money diff if possible
                        # For now, just logging quantities is key.
                elif cmd == "BUY_PRODUCT":
                    if len(parts) >= 3:
                        prod = parts[1]
                        qty = int(parts[2])
                        game_data["bought"][prod] += qty
                        aggregated["buy_product"][prod].append(qty)
                elif cmd == "BUY_SEED":
                    if len(parts) >= 3:
                        prod = parts[1]
                        qty = int(parts[2])
                        game_data["seeds_bought"][prod] += qty
                        aggregated["buy_seed"][prod].append(qty)
                elif cmd == "BUY_ANIMAL":
                    if len(parts) >= 3:
                        prod = parts[1]
                        qty = int(parts[2])
                        game_data["animals_bought"][prod] += qty
                        aggregated["buy_animal"][prod].append(qty)
                elif cmd == "HIRE":
                    qty = int(parts[1]) if len(parts) >= 2 else 1
                    aggregated["hiring_per_day"][day].append(qty)
            
            # Farmer/Hands Actions
            farmer_act = action.get("farmer", [])
            if farmer_act:
                act_name = farmer_act[0] if isinstance(farmer_act, list) else (farmer_act.split()[0] if isinstance(farmer_act, str) else str(farmer_act))
                aggregated["action_freq_farmer"][act_name] += 1
                aggregated["action_freq_farmer_phase"][phase][act_name] += 1
                if act_name == "HARVEST":
                    prod = farmer_act[1] if isinstance(farmer_act, list) and len(farmer_act)>1 else "UNKNOWN"
                    game_data["harvested"][prod] += 1
                    aggregated["harvested"][prod] += 1
                if act_name == "FEED":
                    if isinstance(farmer_act, list) and len(farmer_act)>1 and farmer_act[1] == "WHEAT":
                        aggregated["wheat_fed"] += 1
                
            hands_acts = action.get("hands", [])
            for ha in hands_acts:
                if ha:
                    act_name = ha[0] if isinstance(ha, list) else (ha.split()[0] if isinstance(ha, str) else str(ha))
                    aggregated["action_freq_hands"][act_name] += 1
                    aggregated["action_freq_hands_phase"][phase][act_name] += 1
                    if act_name == "HARVEST":
                        prod = ha[1] if isinstance(ha, list) and len(ha)>1 else "UNKNOWN"
                        game_data["harvested"][prod] += 1
                        aggregated["harvested"][prod] += 1
                    if act_name == "FEED":
                        if isinstance(ha, list) and len(ha)>1 and ha[1] == "WHEAT":
                            aggregated["wheat_fed"] += 1

            # End of day stats
            if step_idx > 0 and step_idx % 24 == 23:
                tiles = seb_farm.get("tiles", [])
                tile_counts = count_tiles(tiles)
                hands_count = len(seb_farm.get("hands", []))
                quadrants = seb_farm.get("unlocked_quadrants", 1)
                
                game_data["daily_farm_composition"][day] = {
                    "tiles": dict(tile_counts),
                    "hands": hands_count,
                    "quadrants": quadrants
                }
                
                # Snapshot sheds
                if day in [5, 10, 15, 20, 25, 29]:
                    priv = obs.get("private", {})
                    game_data["shed_inventory_snapshots"][day] = priv.get("shed", {})
            
            last_money = money
            
        # Final scores
        if len(steps) > 0:
            last_step = steps[-1]
            if len(last_step) >= 2:
                r0 = last_step[0].get("reward", 0)
                r1 = last_step[1].get("reward", 0)
                my_r = r0 if seb_seat == 0 else r1
                opp_r = r1 if seb_seat == 0 else r0
                aggregated["final_banks"].append(my_r)
                aggregated["margins"].append(my_r - opp_r)
                if my_r > opp_r:
                    aggregated["wins"] += 1
                elif my_r < opp_r:
                    aggregated["losses"] += 1
                else:
                    aggregated["ties"] += 1

        aggregated["games_analyzed"] += 1
        aggregated["wheat_sold"] += game_data["sold"].get("WHEAT", 0)
        game_details.append(game_data)
        
    except Exception as e:
        print(f"Error processing {path}: {e}")

# Write JSON
with open(os.path.join(OUTPUT_DIR, "seb_data.json"), "w") as f:
    json.dump({"aggregated": aggregated, "games": game_details}, f, indent=2)

# Write Report
with open(os.path.join(OUTPUT_DIR, "seb_strategy_report.txt"), "w") as f:
    f.write("=========================================\n")
    f.write("      SEB STRATEGY DEEP ANALYSIS         \n")
    f.write("=========================================\n\n")
    
    f.write("=== 1. KEY STRATEGY METRICS ===\n")
    f.write(f"Games Analyzed: {aggregated['games_analyzed']}\n")
    f.write(f"Win/Loss/Tie: {aggregated['wins']} / {aggregated['losses']} / {aggregated['ties']}\n")
    win_rate = (aggregated['wins'] / max(1, aggregated['games_analyzed'])) * 100
    f.write(f"Win Rate: {win_rate:.1f}%\n")
    avg_bank = sum(aggregated['final_banks']) / max(1, len(aggregated['final_banks']))
    avg_margin = sum(aggregated['margins']) / max(1, len(aggregated['margins']))
    f.write(f"Avg Final Bank: {avg_bank:.2f}\n")
    f.write(f"Avg Margin over Opponent: {avg_margin:.2f}\n")
    f.write(f"Total Wheat Sold: {aggregated['wheat_sold']}\n")
    f.write(f"Total Wheat Fed (Actions): {aggregated['wheat_fed']}\n\n")

    f.write("=== 2. LAND EXPANSION ===\n")
    q_times = aggregated['quadrant_unlock_times']
    f.write(f"Total quadrant unlock events detected: {len(q_times)}\n")
    if q_times:
        avg_step = sum(q_times)/len(q_times)
        f.write(f"Average Unlock Step: {avg_step:.1f} (Approx Day {avg_step/24:.1f})\n")
    
    f.write("\nNotable Unlock Batches (Market Orders happening simultaneously with BUY_LAND):\n")
    # Show first 10 examples
    count_shown = 0
    for g in game_details:
        for u in g["quadrant_unlocks"]:
            f.write(f"  Game: {g['file']} | Day: {u['day']} | Step: {u['step']} | Other Orders in Batch: {u['batch']}\n")
            count_shown += 1
            if count_shown >= 10: break
        if count_shown >= 10: break

    f.write("\n=== 3. MARKET ORDERS ANALYSIS ===\n")
    f.write("Total Market Order Frequencies:\n")
    for cmd, cnt in aggregated['market_orders'].most_common():
        f.write(f"  {cmd}: {cnt}\n")
        
    f.write("\nTotal Seeds Bought (across all games):\n")
    for prod, amts in aggregated['buy_seed'].items():
        f.write(f"  {prod}: {sum(amts)} seeds\n")

    f.write("\nTotal Animals Bought (across all games):\n")
    for prod, amts in aggregated['buy_animal'].items():
        f.write(f"  {prod}: {sum(amts)} animals\n")

    f.write("\nTotal Products Sold (across all games):\n")
    for prod, amts in aggregated['sell_by_product'].items():
        f.write(f"  {prod}: {sum(amts)} units (Avg {sum(amts)/max(1, len(amts)):.1f} per order)\n")

    f.write("\n=== 4. FARMER & HANDS ACTIONS ===\n")
    f.write("--- Farmer Action Frequencies ---\n")
    total_farmer_actions = sum(aggregated['action_freq_farmer'].values())
    for act, cnt in aggregated['action_freq_farmer'].most_common():
        f.write(f"  {act}: {cnt} ({(cnt/max(1, total_farmer_actions))*100:.1f}%)\n")
        
    f.write("\n--- Hands Action Frequencies ---\n")
    total_hands_actions = sum(aggregated['action_freq_hands'].values())
    for act, cnt in aggregated['action_freq_hands'].most_common():
        f.write(f"  {act}: {cnt} ({(cnt/max(1, total_hands_actions))*100:.1f}%)\n")

    f.write("\n=== 5. PRODUCTION FLOW ===\n")
    f.write("Harvested Items (Based on HARVEST actions):\n")
    for prod, cnt in aggregated['harvested'].most_common():
        f.write(f"  {prod}: {cnt}\n")

    f.write("\n=== 6. SHED INVENTORY (Sample from first game) ===\n")
    if game_details:
        g1 = game_details[0]
        for day, inv in g1["shed_inventory_snapshots"].items():
            f.write(f"  Day {day}: {inv}\n")
            
    f.write("\n=== 7. DAILY FARM COMPOSITION (Sample from first game) ===\n")
    if game_details:
        g1 = game_details[0]
        for day, comp in g1["daily_farm_composition"].items():
            if day % 5 == 0:
                f.write(f"  Day {day}: Hands={comp['hands']}, Quads={comp['quadrants']}, Tiles={comp['tiles']}\n")

print("Analysis complete. Saved to", OUTPUT_DIR)
