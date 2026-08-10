"""Full dissection of THUNDER THUNDER sub 55373222 & 55381094 vs V17."""
import json
import glob
import os
import sys
sys.path.insert(0, '.')
import submission
from collections import Counter, defaultdict

def dissect():
    v17_actions = submission._REBALANCE_ACTIONS
    tape_files = sorted(glob.glob('replays_new/tape_library/*.json'))
    
    sub1_tapes = []
    sub2_tapes = []
    sub1_meta = []
    sub2_meta = []
    
    for fp in tape_files:
        with open(fp, 'r', encoding='utf-8') as f:
            d = json.load(f)
        aligned_route = d['route'][1:]
        if d['sub'] == '55373222':
            sub1_tapes.append(aligned_route)
            sub1_meta.append(d)
        else:
            sub2_tapes.append(aligned_route)
            sub2_meta.append(d)
            
    print(f"Sub 1 (55373222): {len(sub1_tapes)} episodes")
    print(f"Sub 2 (55381094): {len(sub2_tapes)} episodes")
    
    def ser(a):
        return json.dumps(a, sort_keys=True, separators=(',', ':'))
        
    def ser_m(a):
        return json.dumps(a.get('market', []), sort_keys=True, separators=(',', ':'))

    def ser_f(a):
        return json.dumps(a.get('farmer', []), sort_keys=True, separators=(',', ':'))

    def ser_h(a):
        return json.dumps(a.get('hands', []), sort_keys=True, separators=(',', ':'))

    # Check internal variance within Sub 1 across 114 episodes
    sub1_variance_steps = []
    for s in range(719):
        variants = set(ser(t[s]) for t in sub1_tapes)
        if len(variants) > 1:
            sub1_variance_steps.append((s, len(variants)))
            
    print(f"\nSub 1 (55373222) internal variation steps across 114 eps: {len(sub1_variance_steps)}/719")
    if sub1_variance_steps:
        print("Sample variation steps in Sub 1:")
        for s, n_var in sub1_variance_steps[:10]:
            c = Counter(ser(t[s]) for t in sub1_tapes)
            print(f"  Step {s:3d} (Day {s//24:2d}.{s%24:2d}): {n_var} variants -> Top: {c.most_common(1)[0][1]}/{len(sub1_tapes)}")

    # Check internal variance within Sub 2 across 21 episodes
    sub2_variance_steps = []
    for s in range(719):
        variants = set(ser(t[s]) for t in sub2_tapes)
        if len(variants) > 1:
            sub2_variance_steps.append((s, len(variants)))
            
    print(f"\nSub 2 (55381094) internal variation steps across 21 eps: {len(sub2_variance_steps)}/719")
    if sub2_variance_steps:
        print("Sample variation steps in Sub 2:")
        for s, n_var in sub2_variance_steps[:10]:
            c = Counter(ser(t[s]) for t in sub2_tapes)
            print(f"  Step {s:3d} (Day {s//24:2d}.{s%24:2d}): {n_var} variants -> Top: {c.most_common(1)[0][1]}/{len(sub2_tapes)}")

    # Compute consensus route for Sub 1 and Sub 2
    def get_consensus_aligned(tapes):
        cons = []
        for s in range(719):
            c = Counter(ser(t[s]) for t in tapes)
            cons.append(json.loads(c.most_common(1)[0][0]))
        return cons

    sub1_cons = get_consensus_aligned(sub1_tapes)
    sub2_cons = get_consensus_aligned(sub2_tapes)

    # Let's compare V17 base actions vs Sub 1 vs Sub 2
    print("\n=======================================================")
    print("V17 vs SUB 1 (55373222) vs SUB 2 (55381094) CONSENSUS")
    print("=======================================================")
    
    diff_v17_sub1 = sum(1 for a, b in zip(v17_actions, sub1_cons) if ser(a) != ser(b))
    diff_v17_sub2 = sum(1 for a, b in zip(v17_actions, sub2_cons) if ser(a) != ser(b))
    diff_sub1_sub2 = sum(1 for a, b in zip(sub1_cons, sub2_cons) if ser(a) != ser(b))
    
    print(f"Diffs V17 vs Sub 1: {diff_v17_sub1}/719")
    print(f"Diffs V17 vs Sub 2: {diff_v17_sub2}/719")
    print(f"Diffs Sub 1 vs Sub 2: {diff_sub1_sub2}/719")

    # Let's categorize the differences:
    # 1. Early game (Steps 0-120)
    # 2. Mid game (Steps 120-456)
    # 3. Late game (Steps 456-719)
    for phase_name, s_start, s_end in [("Early (0-120)", 0, 120), ("Mid (120-456)", 120, 456), ("Late (456-719)", 456, 719)]:
        d_v17_s1 = sum(1 for s in range(s_start, s_end) if ser(v17_actions[s]) != ser(sub1_cons[s]))
        d_v17_s2 = sum(1 for s in range(s_start, s_end) if ser(v17_actions[s]) != ser(sub2_cons[s]))
        d_s1_s2 = sum(1 for s in range(s_start, s_end) if ser(sub1_cons[s]) != ser(sub2_cons[s]))
        print(f"  {phase_name}: V17 vs S1: {d_v17_s1} | V17 vs S2: {d_v17_s2} | S1 vs S2: {d_s1_s2}")

if __name__ == '__main__':
    dissect()
