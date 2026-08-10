"""Zoom into Day 20-21 and Day 27-28 in Episode 91684995."""
import json
from kaggle_environments import make

def inspect_windows():
    with open('replays_new/v17 losing/91684995.json', 'r', encoding='utf-8') as f:
        ep = json.load(f)

    steps = ep['steps']
    
    # Replay environment and step-by-step track everything
    seed = ep['info']['seed']
    p0_tape = [steps[s][0].get('action') or {} for s in range(1, len(steps))]
    p1_tape = [steps[s][1].get('action') or {} for s in range(1, len(steps))]
    
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    
    # Run step-by-step
    env.reset()
    
    for s in range(720):
        # Current state before step
        obs0 = env.state[0].get('observation', {})
        farms = obs0.get('farms', [])
        mkt = obs0.get('market', {})
        
        act0 = p0_tape[min(s, len(p0_tape)-1)]
        act1 = p1_tape[min(s, len(p1_tape)-1)]
        
        # Check window 1: steps 480 to 510 (Day 20 - 21)
        # Check window 2: steps 660 to 680 (Day 27 - 28)
        # Check window 3: steps 710 to 720 (Endgame)
        is_window = (480 <= s <= 510) or (660 <= s <= 680) or (710 <= s <= 719)
        
        m0 = act0.get('market', [])
        m1 = act1.get('market', [])
        
        if is_window and (m0 or m1 or s in (480, 504, 672, 696, 719)):
            day = s // 24
            hour = s % 24
            f0_m = farms[0].get('money', 0) if len(farms)>0 else 0
            f1_m = farms[1].get('money', 0) if len(farms)>1 else 0
            
            # get current prices
            prices = {k: v.get('price') for k, v in mkt.items() if isinstance(v, dict)} if isinstance(mkt, dict) else {}
            
            print(f"Step {s:3d} (Day {day:2d}.{hour:2d}) | Money: V17=${f0_m:.0f}, THUNDER=${f1_m:.0f} (Diff=${f0_m-f1_m:+.0f})")
            print(f"  Prices: {prices}")
            if m0: print(f"  V17  Market: {m0}")
            if m1: print(f"  THUN Market: {m1}")
            
        env.step([act0, act1])

if __name__ == '__main__':
    inspect_windows()
