"""Deep analysis of all 135 THUNDER THUNDER episodes in tape_library."""
import json
import os
import glob
from collections import Counter, defaultdict

def analyze_thunder_library():
    tape_dir = r'replays_new/tape_library'
    tape_files = sorted(glob.glob(os.path.join(tape_dir, '*.json')))
    print(f"Loading {len(tape_files)} THUNDER episodes...")
    
    episodes = []
    for fp in tape_files:
        with open(fp, 'r', encoding='utf-8') as f:
            episodes.append(json.load(f))
            
    print(f"Loaded {len(episodes)} episodes.")
    
    # 1. Action Tape Clustering & Determinism
    # Serialize each 720-step route
    def serialize_action(a):
        return json.dumps(a, sort_keys=True, separators=(',', ':'))
        
    def serialize_market_only(a):
        return json.dumps(a.get('market', []), sort_keys=True, separators=(',', ':'))

    def serialize_farmer_only(a):
        return json.dumps(a.get('farmer', []), sort_keys=True, separators=(',', ':'))
        
    def serialize_hands_only(a):
        return json.dumps(a.get('hands', []), sort_keys=True, separators=(',', ':'))

    # Check step 0 and step 1 actions across all episodes
    step0_counter = Counter()
    step1_counter = Counter()
    for ep in episodes:
        route = ep['route']
        step0_counter[serialize_action(route[0])] += 1
        step1_counter[serialize_action(route[1])] += 1
        
    print("\n--- Step 0 Actions Across 135 Episodes ---")
    for act, cnt in step0_counter.most_common(5):
        print(f"  [{cnt} eps]: {act}")
        
    print("\n--- Step 1 Actions Across 135 Episodes ---")
    for act, cnt in step1_counter.most_common(5):
        print(f"  [{cnt} eps]: {act}")

    # Compare pairwise routes to find unique base routes
    # Let's count differences between routes
    routes_raw = [ep['route'] for ep in episodes]
    routes_ser = [[serialize_action(a) for a in r] for r in routes_raw]
    
    # Cluster routes by similarity to route 0
    diffs_to_r0 = []
    for i, r in enumerate(routes_ser):
        d = sum(1 for a, b in zip(routes_ser[0], r) if a != b)
        diffs_to_r0.append((d, episodes[i]['sub'], episodes[i]['ep'], episodes[i]['seed'], episodes[i]['reward_self']))
        
    diff_counts = Counter(x[0] for x in diffs_to_r0)
    print("\n--- Route Differences to Episode 0 ---")
    for diff, cnt in sorted(diff_counts.items()):
        sample = next(x for x in diffs_to_r0 if x[0] == diff)
        print(f"  {cnt} episodes have {diff} differing steps (Sample: ep={sample[2]}, sub={sample[1]}, score={sample[4]})")

    # Let's inspect differences between sub 55373222 and sub 55381094
    sub_1 = [ep for ep in episodes if ep['sub'] == '55373222']
    sub_2 = [ep for ep in episodes if ep['sub'] == '55381094']
    print(f"\nSub 55373222 count: {len(sub_1)}, Sub 55381094 count: {len(sub_2)}")

    # For each sub, compute per-step agreement (consensus route)
    for sub_name, sub_eps in [('55373222', sub_1), ('55381094', sub_2)]:
        if not sub_eps: continue
        print(f"\n--- Analysis of Submission {sub_name} ({len(sub_eps)} episodes) ---")
        consensus = []
        low_agree_steps = []
        for s in range(720):
            acts = Counter(serialize_action(ep['route'][s]) for ep in sub_eps)
            top_act, top_cnt = acts.most_common(1)[0]
            consensus.append(json.loads(top_act))
            if top_cnt < len(sub_eps):
                low_agree_steps.append((s, top_cnt, len(sub_eps), len(acts)))
        print(f"  Consensus has {720 - len(low_agree_steps)} / 720 100% identical steps across all episodes.")
        print(f"  Differing steps: {len(low_agree_steps)}")
        if low_agree_steps:
            print("  First 10 differing steps:")
            for s, top_cnt, total, n_choices in low_agree_steps[:10]:
                print(f"    Step {s} (Day {s//24}.{s%24}): {top_cnt}/{total} agreement ({n_choices} distinct variants)")

        # Market sales analysis in consensus
        sales = []
        buys = []
        for s, act in enumerate(consensus):
            m = act.get('market', [])
            for ord in m:
                if ord[0] == 'SELL':
                    sales.append((s, ord[1], ord[2]))
                elif ord[0] in ('BUY_SEED', 'BUY_PRODUCT', 'BUY_ANIMAL', 'BUY_LAND', 'HIRE'):
                    buys.append((s, ord[0], ord[1:] if len(ord)>1 else []))
        print(f"  Total consensus SELL orders: {len(sales)}")
        print(f"  Total consensus BUY/HIRE orders: {len(buys)}")
        print("  Key SELL windows in consensus:")
        for s, item, qty in sales:
            if s >= 400 or qty > 5:
                print(f"    Step {s:3d} (Day {s//24:2d}.{s%24:2d}): SELL {item} {qty}")

if __name__ == '__main__':
    analyze_thunder_library()
