"""Precompute consensus routes to compact JSON for fast worker loading."""
import json
import glob
import os
from collections import Counter

tape_dir = r'replays_new/tape_library'
sub1_files = sorted([fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55373222_' in fp])
sub2_files = sorted([fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55381094_' in fp])

def get_consensus(files):
    eps = [json.load(open(fp, 'r', encoding='utf-8'))['route'][1:] for fp in files]
    cons = []
    for s in range(719):
        c = Counter(json.dumps(ep[s], sort_keys=True, separators=(',', ':')) for ep in eps)
        cons.append(json.loads(c.most_common(1)[0][0]))
    return cons

th1_route = get_consensus(sub1_files)
th2_route = get_consensus(sub2_files)

os.makedirs('tools', exist_ok=True)
with open('tools/routes_precomputed.json', 'w', encoding='utf-8') as f:
    json.dump({"th1": th1_route, "th2": th2_route}, f)

print(f"Precomputed routes saved to tools/routes_precomputed.json (th1={len(th1_route)}, th2={len(th2_route)})")
