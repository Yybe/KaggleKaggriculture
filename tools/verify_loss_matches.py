"""Verify V18 APEXX agent against all 27 loss matches in kernels/v17 v18 losing matches."""
import json
import glob
import os
import sys
import time

sys.path.insert(0, '.')
import submission
from agents.kaggle_v18_apexx import V18ApexAgent
from kaggle_environments import make

def verify_all():
    loss_dir = r'C:\Users\xxshi\Desktop\FARMMASTER\kernels\v17 v18 losing matches'
    files = glob.glob(os.path.join(loss_dir, '*_LOSS.json'))
    print(f"Loaded {len(files)} loss entries from '{loss_dir}'")
    
    agent_apexx = V18ApexAgent()
    
    wins = 0
    losses = 0
    ties = 0
    results = []
    
    for idx, fp in enumerate(files):
        with open(fp, 'r', encoding='utf-8') as f:
            ep = json.load(f)
            
        opp_name = ep.get('opp', 'UNKNOWN')
        seed = ep.get('seed', 0)
        route_opp = ep.get('route_opp', [])
        r_self_orig = ep.get('reward_self', 0)
        r_opp_orig = ep.get('reward_opp', 0)
        
        # Build opponent replay fn
        def opp_agent(obs, configuration=None):
            step = int(obs.get("step", 0) or 0)
            s = min(max(0, step), len(route_opp) - 1)
            action = copy.deepcopy(route_opp[s])
            action = submission._weed_repair_action(obs, action, route_opp, s)
            return submission._align_hands(action, obs)
            
        import copy
        
        # Test V18 APEXX as player 0 vs opponent replay as player 1
        try:
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
            env.run([agent_apexx, opp_agent])
            r0 = float(env.state[0].get("reward", 0) or 0)
            r1 = float(env.state[1].get("reward", 0) or 0)
            d = r0 - r1
            if d > 0:
                wins += 1
                status = "WIN"
            elif d < 0:
                losses += 1
                status = "LOSS"
            else:
                ties += 1
                status = "TIE"
            results.append((ep.get('ep'), opp_name, r0, r1, d, status, r_self_orig, r_opp_orig))
            print(f"[{idx+1:2d}/{len(files)}] Ep {ep.get('ep')}: vs {opp_name:22s} | APEXX=${r0:7.1f} vs Opp=${r1:7.1f} | Delta=${d:+7.1f} ({status}) | Orig: ${r_self_orig:.0f} vs ${r_opp_orig:.0f}")
        except Exception as e:
            print(f"[{idx+1:2d}/{len(files)}] Ep {ep.get('ep')}: vs {opp_name:22s} | ERROR: {e}")
            
    print("\n" + "="*80)
    print(f"TOTAL LOSS MATCH REVERIFICATION RESULTS: {wins} WINS / {losses} LOSSES / {ties} TIES")
    print("="*80)

if __name__ == '__main__':
    verify_all()
