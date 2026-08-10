"""Inspect exact mechanical differences and simulate Sub 1 & Sub 2 vs V17."""
import json
import glob
import os
import sys
sys.path.insert(0, '.')
import submission
from collections import Counter

def inspect_details():
    v17_actions = submission._REBALANCE_ACTIONS
    tape_files = sorted(glob.glob('replays_new/tape_library/*.json'))
    
    sub1_files = [fp for fp in tape_files if '_55373222_' in fp]
    sub2_files = [fp for fp in tape_files if '_55381094_' in fp]
    
    def get_consensus(files):
        eps = [json.load(open(fp, 'r', encoding='utf-8'))['route'][1:] for fp in files]
        cons = []
        for s in range(719):
            c = Counter(json.dumps(ep[s], sort_keys=True, separators=(',', ':')) for ep in eps)
            cons.append(json.loads(c.most_common(1)[0][0]))
        return cons

    sub1_cons = get_consensus(sub1_files)
    sub2_cons = get_consensus(sub2_files)

    # 1. Market Differences: List all market orders side-by-side
    print("=======================================================")
    print("MARKET ORDERS DIFFERENCES (V17 vs Sub 1 vs Sub 2):")
    print("=======================================================")
    for s in range(719):
        m_v17 = v17_actions[s].get('market', [])
        m_s1 = sub1_cons[s].get('market', [])
        m_s2 = sub2_cons[s].get('market', [])
        
        if m_v17 != m_s1 or m_v17 != m_s2 or m_s1 != m_s2:
            day = s // 24
            hour = s % 24
            print(f"Step {s:3d} (Day {day:2d}.{hour:2d}):")
            if m_v17: print(f"  V17:  {m_v17}")
            else:     print(f"  V17:  []")
            if m_s1:  print(f"  S1:   {m_s1}")
            else:     print(f"  S1:   []")
            if m_s2:  print(f"  S2:   {m_s2}")
            else:     print(f"  S2:   []")

if __name__ == '__main__':
    inspect_details()
