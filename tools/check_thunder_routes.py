"""Check how many unique routes exist across all 135 THUNDER episodes."""
import json
import glob
import os
from collections import Counter

tape_dir = r'replays_new/tape_library'
tape_files = sorted(glob.glob(os.path.join(tape_dir, '*.json')))

def ser(a):
    return json.dumps(a, sort_keys=True, separators=(',', ':'))

# For each sub, let's find the unique routes
for sub_id in ['55373222', '55381094']:
    files = [fp for fp in tape_files if f'_{sub_id}_' in fp]
    routes = []
    for fp in files:
        with open(fp, 'r', encoding='utf-8') as f:
            d = json.load(f)
        routes.append((d['route'][1:], d['ep'], d['seed'], d['opp'], d['reward_self'], d['reward_opp']))
        
    print(f"\n=======================================================")
    print(f"SUBMISSION {sub_id} ({len(routes)} episodes)")
    print(f"=======================================================")
    
    # Compute base consensus
    cons = []
    for s in range(719):
        c = Counter(ser(r[0][s]) for r in routes)
        cons.append(json.loads(c.most_common(1)[0][0]))
        
    # Check how each episode differs from consensus
    diff_distribution = Counter()
    diff_details = []
    for r, ep, seed, opp, rself, ropp in routes:
        diffs = sum(1 for s in range(719) if ser(r[s]) != ser(cons[s]))
        diff_distribution[diffs] += 1
        diff_details.append((diffs, ep, seed, opp, rself, ropp))
        
    print(f"Difference distribution from consensus route:")
    for d_count, num_eps in sorted(diff_distribution.items()):
        print(f"  {num_eps} episodes have {d_count} diffs from consensus")
        
    # Sample episodes with 0 diffs vs >0 diffs
    print("\nSample episodes:")
    for d_count, ep, seed, opp, rself, ropp in sorted(diff_details, key=lambda x: x[0])[:5]:
        print(f"  diffs={d_count:3d} | ep={ep} | seed={seed:10d} | opp={opp[:15]:15s} | score={rself:7.0f} vs {ropp:7.0f}")
    for d_count, ep, seed, opp, rself, ropp in sorted(diff_details, key=lambda x: x[0])[-5:]:
        print(f"  diffs={d_count:3d} | ep={ep} | seed={seed:10d} | opp={opp[:15]:15s} | score={rself:7.0f} vs {ropp:7.0f}")
