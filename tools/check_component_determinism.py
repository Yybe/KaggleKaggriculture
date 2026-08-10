"""Examine farmer, hands, and market determinism across all 135 THUNDER episodes."""
import json
import glob
import os
from collections import Counter

tape_dir = r'replays_new/tape_library'
tape_files = sorted(glob.glob(os.path.join(tape_dir, '*.json')))

def ser(a):
    return json.dumps(a, sort_keys=True, separators=(',', ':'))

for sub_id in ['55373222', '55381094']:
    files = [fp for fp in tape_files if f'_{sub_id}_' in fp]
    tapes = []
    for fp in files:
        with open(fp, 'r', encoding='utf-8') as f:
            tapes.append(json.load(f)['route'][1:]) # aligned 719 steps
            
    print(f"\n=======================================================")
    print(f"DETERMINISM BREAKDOWN FOR SUBMISSION {sub_id} ({len(tapes)} episodes)")
    print(f"=======================================================")
    
    farmer_diff_steps = set()
    hands_diff_steps = set()
    market_diff_steps = set()
    
    for s in range(719):
        f_acts = set(ser(t[s].get('farmer', [])) for t in tapes)
        h_acts = set(ser(t[s].get('hands', [])) for t in tapes)
        m_acts = set(ser(t[s].get('market', [])) for t in tapes)
        
        if len(f_acts) > 1:
            farmer_diff_steps.add(s)
        if len(h_acts) > 1:
            hands_diff_steps.add(s)
        if len(m_acts) > 1:
            market_diff_steps.add(s)
            
    print(f"Farmer movement differing steps: {len(farmer_diff_steps)}/719")
    print(f"Hands  movement differing steps: {len(hands_diff_steps)}/719")
    print(f"Market orders   differing steps: {len(market_diff_steps)}/719")
    
    # Check if hands diffs are solely weed-repair or if there are structural route changes
    # Look at consensus route vs an episode that had 0 weeds
    cons_m = [Counter(ser(t[s].get('market', [])) for t in tapes).most_common(1)[0] for s in range(719)]
    cons_f = [Counter(ser(t[s].get('farmer', [])) for t in tapes).most_common(1)[0] for s in range(719)]
    cons_h = [Counter(ser(t[s].get('hands', [])) for t in tapes).most_common(1)[0] for s in range(719)]
    
    f_agreement = sum(cnt for _, cnt in cons_f) / (719 * len(tapes)) * 100
    h_agreement = sum(cnt for _, cnt in cons_h) / (719 * len(tapes)) * 100
    m_agreement = sum(cnt for _, cnt in cons_m) / (719 * len(tapes)) * 100
    
    print(f"Overall agreement: Farmer={f_agreement:.2f}% | Hands={h_agreement:.2f}% | Market={m_agreement:.2f}%")
