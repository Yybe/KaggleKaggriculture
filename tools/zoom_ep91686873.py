"""Forensic analysis of Episode 91686873: V17 vs HealthStone."""
import json
from kaggle_environments import make

def inspect_healthstone_match():
    with open('replays_new/v17 losing/91686873.json', 'r', encoding='utf-8') as f:
        ep = json.load(f)

    steps = ep['steps']
    seed = ep['info']['seed']
    p0_tape = [steps[s][0].get('action') or {} for s in range(1, len(steps))]
    p1_tape = [steps[s][1].get('action') or {} for s in range(1, len(steps))]
    
    print(f"Seed: {seed}")
    print(f"Final Scores: V17={ep['rewards'][0]}, HealthStone={ep['rewards'][1]} (Delta={ep['rewards'][0]-ep['rewards'][1]})")

    # Trace day-by-day money and key divergence points
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.reset()
    
    for s in range(719):
        obs0 = env.state[0].get('observation', {})
        farms = obs0.get('farms', [])
        mkt = obs0.get('market', {})
        
        act0 = p0_tape[min(s, len(p0_tape)-1)]
        act1 = p1_tape[min(s, len(p1_tape)-1)]
        
        f0_m = farms[0].get('money', 0) if len(farms)>0 else 0
        f1_m = farms[1].get('money', 0) if len(farms)>1 else 0
        
        if s % 24 == 0 or s == 718:
            day = s // 24
            print(f"Day {day:2d} (Step {s:3d}): V17=${f0_m:7.0f} | HealthStone=${f1_m:7.0f} | Diff=${f0_m-f1_m:+7.0f}")
            
        env.step([act0, act1])

if __name__ == '__main__':
    inspect_healthstone_match()
