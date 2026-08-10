"""Summarize exact structural differences between V17, THUNDER-1, THUNDER-2, and HealthStone."""
import json
import os
import glob
import sys
sys.path.insert(0, '.')
import submission
from collections import Counter

def run_summary():
    v17_actions = submission._REBALANCE_ACTIONS
    print(f"V17 actions length: {len(v17_actions)}")
    
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
    
    def ser(a):
        return json.dumps(a, sort_keys=True, separators=(',', ':'))
        
    def ser_m(a):
        return json.dumps(a.get('market', []), sort_keys=True, separators=(',', ':'))

    def ser_f(a):
        return json.dumps(a.get('farmer', []), sort_keys=True, separators=(',', ':'))

    def ser_h(a):
        return json.dumps(a.get('hands', []), sort_keys=True, separators=(',', ':'))

    # Compare step counts
    print(f"THUNDER-1 vs THUNDER-2 diffs: {sum(1 for a, b in zip(thunder1, thunder2) if ser(a) != ser(b))}/720")
    print(f"V17 vs THUNDER-1 diffs: {sum(1 for a, b in zip(v17_actions[:719], thunder1[:719]) if ser(a) != ser(b))}/719")
    print(f"V17 vs THUNDER-2 diffs: {sum(1 for a, b in zip(v17_actions[:719], thunder2[:719]) if ser(a) != ser(b))}/719")
    
    # Check HealthStone
    hs_files = sorted(glob.glob(r'replays_new/healthstone/*.json'))
    print(f"\nHealthStone replays available: {len(hs_files)}")
    
    # Extract HealthStone tape from one replay
    hs_tape = None
    if hs_files:
        with open(hs_files[0], 'r', encoding='utf-8') as f:
            hs_rep = json.load(f)
        teams = hs_rep.get('info', {}).get('TeamNames', [])
        hs_slot = teams.index('HealthStone') if 'HealthStone' in teams else 0
        hs_tape = [step[hs_slot]['action'] for step in hs_rep['steps']]
        print(f"HealthStone tape length: {len(hs_tape)}")
        print(f"V17 vs HealthStone diffs: {sum(1 for a, b in zip(v17_actions[:719], hs_tape[:719]) if ser(a) != ser(b))}/719")

    # Let's inspect early game (Days 0-5) across V17, THUNDER-1, THUNDER-2, HealthStone
    print("\n=======================================================")
    print("EARLY GAME COMPARISON (Steps 0 to 48):")
    print("=======================================================")
    for s in range(49):
        m_v17 = v17_actions[s].get('market', []) if s < len(v17_actions) else []
        m_th1 = thunder1[s].get('market', [])
        m_th2 = thunder2[s].get('market', [])
        m_hs = hs_tape[s].get('market', []) if hs_tape else []
        
        if m_v17 or m_th1 or m_th2 or m_hs:
            print(f"Step {s:2d} (Day {s//24}.{s%24:2d}):")
            if m_v17: print(f"  V17:   {m_v17}")
            if m_th1: print(f"  TH1:   {m_th1}")
            if m_th2: print(f"  TH2:   {m_th2}")
            if m_hs:  print(f"  HS:    {m_hs}")

if __name__ == '__main__':
    run_summary()
