"""Compare THUNDER routes vs V17 vs Salem vs HealthStone."""
import json
import os
import glob
from collections import Counter

def compare_agents():
    # Load V17 route (which is _REBALANCE_ACTIONS / _LEGACY_ACTIONS from submission.py)
    import sys
    sys.path.insert(0, '.')
    import submission
    v17_actions = submission._REBALANCE_ACTIONS
    print(f"V17 base actions length: {len(v17_actions)}")
    
    # Load THUNDER consensus routes
    tape_dir = r'replays_new/tape_library'
    sub1_files = sorted(glob.glob(os.path.join(tape_dir, '*_55373222_THUNDER.json')))
    sub2_files = sorted(glob.glob(os.path.join(tape_dir, '*_55381094_THUNDER.json')))
    
    def get_consensus(files):
        eps = [json.load(open(fp, 'r', encoding='utf-8'))['route'] for fp in files]
        consensus = []
        for s in range(720):
            acts = Counter(json.dumps(ep[s], sort_keys=True, separators=(',', ':')) for ep in eps)
            consensus.append(json.loads(acts.most_common(1)[0][0]))
        return consensus

    thunder1 = get_consensus(sub1_files)
    thunder2 = get_consensus(sub2_files)
    print(f"THUNDER 55373222 consensus length: {len(thunder1)}")
    print(f"THUNDER 55381094 consensus length: {len(thunder2)}")
    
    def ser(a):
        return json.dumps(a, sort_keys=True, separators=(',', ':'))
        
    def ser_market(a):
        return json.dumps(a.get('market', []), sort_keys=True, separators=(',', ':'))
        
    def ser_farmer(a):
        return json.dumps(a.get('farmer', []), sort_keys=True, separators=(',', ':'))
        
    def ser_hands(a):
        return json.dumps(a.get('hands', []), sort_keys=True, separators=(',', ':'))

    # Compare V17 vs THUNDER1
    diff_total_1 = sum(1 for a, b in zip(v17_actions, thunder1) if ser(a) != ser(b))
    diff_market_1 = sum(1 for a, b in zip(v17_actions, thunder1) if ser_market(a) != ser_market(b))
    diff_farmer_1 = sum(1 for a, b in zip(v17_actions, thunder1) if ser_farmer(a) != ser_farmer(b))
    diff_hands_1 = sum(1 for a, b in zip(v17_actions, thunder1) if ser_hands(a) != ser_hands(b))
    print(f"\nV17 vs THUNDER-1 (55373222): Total diffs = {diff_total_1}/720 | Market diffs = {diff_market_1} | Farmer = {diff_farmer_1} | Hands = {diff_hands_1}")

    # Compare V17 vs THUNDER2
    diff_total_2 = sum(1 for a, b in zip(v17_actions, thunder2) if ser(a) != ser(b))
    diff_market_2 = sum(1 for a, b in zip(v17_actions, thunder2) if ser_market(a) != ser_market(b))
    diff_farmer_2 = sum(1 for a, b in zip(v17_actions, thunder2) if ser_farmer(a) != ser_farmer(b))
    diff_hands_2 = sum(1 for a, b in zip(v17_actions, thunder2) if ser_hands(a) != ser_hands(b))
    print(f"V17 vs THUNDER-2 (55381094): Total diffs = {diff_total_2}/720 | Market diffs = {diff_market_2} | Farmer = {diff_farmer_2} | Hands = {diff_hands_2}")

    # Compare THUNDER1 vs THUNDER2
    diff_1_2 = sum(1 for a, b in zip(thunder1, thunder2) if ser(a) != ser(b))
    diff_m_1_2 = sum(1 for a, b in zip(thunder1, thunder2) if ser_market(a) != ser_market(b))
    print(f"THUNDER-1 vs THUNDER-2: Total diffs = {diff_1_2}/720 | Market diffs = {diff_m_1_2}")

    # Let's inspect where V17 and THUNDER-2 differ in detail
    print("\n--- Detailed Differences: V17 vs THUNDER-2 ---")
    for s in range(720):
        a_v17 = v17_actions[s]
        a_th2 = thunder2[s]
        if ser(a_v17) != ser(a_th2):
            print(f"Step {s:3d} (Day {s//24:2d}.{s%24:2d}):")
            if ser_farmer(a_v17) != ser_farmer(a_th2):
                print(f"  Farmer: V17={a_v17.get('farmer')} vs TH2={a_th2.get('farmer')}")
            if ser_hands(a_v17) != ser_hands(a_th2):
                print(f"  Hands:  V17={a_v17.get('hands')} vs TH2={a_th2.get('hands')}")
            if ser_market(a_v17) != ser_market(a_th2):
                print(f"  Market: V17={a_v17.get('market')} vs TH2={a_th2.get('market')}")

if __name__ == '__main__':
    compare_agents()
