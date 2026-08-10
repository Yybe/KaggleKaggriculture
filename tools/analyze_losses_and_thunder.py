"""Comprehensive analysis of V17 lost matches and THUNDER THUNDER tape library."""
import json
import os
import glob
from collections import Counter, defaultdict

def analyze_losing_match(json_path, label):
    print(f"\n=======================================================")
    print(f"ANALYZING LOSING MATCH: {label} ({os.path.basename(json_path)})")
    print(f"=======================================================")
    with open(json_path, 'r', encoding='utf-8') as f:
        ep = json.load(f)
    
    info = ep.get('info', {})
    teams = info.get('TeamNames', ['P0', 'P1'])
    seed = info.get('seed')
    rewards = ep.get('rewards')
    print(f"Teams: {teams[0]} vs {teams[1]}")
    print(f"Seed: {seed}")
    print(f"Final Rewards: {rewards[0]} vs {rewards[1]} (Delta: {rewards[0] - rewards[1]})")
    
    steps = ep.get('steps', [])
    print(f"Total steps: {len(steps)}")
    
    # Track actions, sales, buys, money, and differences
    p0_orders = Counter()
    p1_orders = Counter()
    p0_sales_vol = Counter()
    p1_sales_vol = Counter()
    p0_buys_vol = Counter()
    p1_buys_vol = Counter()
    
    action_diff_steps = []
    
    for step_idx in range(len(steps)):
        step_data = steps[step_idx]
        p0 = step_data[0]
        p1 = step_data[1]
        
        act0 = p0.get('action') or {}
        act1 = p1.get('action') or {}
        
        # Check action identity (ignoring farmer/hands coordinate differences if mirror)
        m0 = act0.get('market', []) or []
        m1 = act1.get('market', []) or []
        
        for ord in m0:
            p0_orders[ord[0]] += 1
            if ord[0] == 'SELL' and len(ord) >= 3:
                p0_sales_vol[ord[1]] += ord[2]
            elif ord[0] in ('BUY_SEED', 'BUY_PRODUCT') and len(ord) >= 3:
                p0_buys_vol[ord[1]] += ord[2]
                
        for ord in m1:
            p1_orders[ord[0]] += 1
            if ord[0] == 'SELL' and len(ord) >= 3:
                p1_sales_vol[ord[1]] += ord[2]
            elif ord[0] in ('BUY_SEED', 'BUY_PRODUCT') and len(ord) >= 3:
                p1_buys_vol[ord[1]] += ord[2]
                
        # Compare market orders at this step
        if m0 != m1:
            action_diff_steps.append((step_idx, m0, m1))

    print("\nP0 (V17) Market Orders Summary:")
    print("  Orders count:", dict(p0_orders))
    print("  Sales volume:", dict(p0_sales_vol))
    print("  Buys volume:", dict(p0_buys_vol))
    
    print("\nP1 (Opponent) Market Orders Summary:")
    print("  Orders count:", dict(p1_orders))
    print("  Sales volume:", dict(p1_sales_vol))
    print("  Buys volume:", dict(p1_buys_vol))
    
    print(f"\nTotal steps with differing market orders: {len(action_diff_steps)}")
    print("First 20 differing market orders:")
    for step_idx, m0, m1 in action_diff_steps[:20]:
        print(f"  Step {step_idx:3d} (Day {step_idx//24:2d}.{step_idx%24:2d}):")
        print(f"    V17: {m0}")
        print(f"    Opp: {m1}")
        
    print("\nLast 15 differing market orders (Endgame):")
    for step_idx, m0, m1 in action_diff_steps[-15:]:
        print(f"  Step {step_idx:3d} (Day {step_idx//24:2d}.{step_idx%24:2d}):")
        print(f"    V17: {m0}")
        print(f"    Opp: {m1}")

if __name__ == '__main__':
    analyze_losing_match('replays_new/v17 losing/91684995.json', '91684995 vs THUNDER THUNDER')
    analyze_losing_match('replays_new/v17 losing/91686873.json', '91686873 vs HealthStone')
