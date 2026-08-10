"""Deep forensic comparison of Episode 91684995: V17 vs THUNDER THUNDER."""
import json
import os

def analyze():
    with open('replays_new/v17 losing/91684995.json', 'r', encoding='utf-8') as f:
        ep = json.load(f)

    steps = ep['steps']
    print(f"Total steps: {len(steps)}")
    
    # We want to trace:
    # 1. Money trajectory (step-by-step or day-by-day)
    # 2. Cumulative sales revenue per item for V17 (P0) vs THUNDER (P1)
    # 3. Shed contents over time
    # 4. Hands hired over time
    # 5. Crop tiles and animal counts
    # 6. Market transaction prices and revenues
    
    p0_revenue_by_item = {}
    p1_revenue_by_item = {}
    
    p0_money_history = []
    p1_money_history = []
    
    # Track market prices across steps
    prices_history = []
    
    # In kaggriculture replays, let's inspect the market orders and the resulting money changes
    for s in range(len(steps)):
        s_data = steps[s]
        p0_act = s_data[0].get('action') or {}
        p1_act = s_data[1].get('action') or {}
        
        # Check observations
        obs0 = s_data[0].get('observation') or {}
        if 'farms' in obs0 and len(obs0['farms']) >= 2:
            m0 = obs0['farms'][0].get('money', 0)
            m1 = obs0['farms'][1].get('money', 0)
            p0_money_history.append((s, m0))
            p1_money_history.append((s, m1))
            
        mkt = obs0.get('market')
        if mkt and isinstance(mkt, dict):
            prices_history.append((s, {k: v.get('price') for k, v in mkt.items() if isinstance(v, dict)}))

    print(f"Recorded money points: {len(p0_money_history)}")
    if p0_money_history:
        print("\n--- Day-by-Day Money Comparison (V17 vs THUNDER) ---")
        for s, m0 in p0_money_history:
            if s % 24 == 0 or s == len(steps) - 1:
                m1 = next(x[1] for x in p1_money_history if x[0] == s)
                day = s // 24
                print(f"Day {day:2d} (Step {s:3d}): V17=${m0:7.1f} | THUNDER=${m1:7.1f} | Diff=${m0-m1:+7.1f}")

    # Now let's calculate all sales and actual revenue received in 91684995!
    # Let's replay 91684995 locally using the exact actions from the replay to inspect the engine events!
    from kaggle_environments import make
    
    p0_actions = [steps[s][0].get('action') or {} for s in range(len(steps))]
    p1_actions = [steps[s][1].get('action') or {} for s in range(len(steps))]
    
    # Note that steps[0] is dummy, so actions start from step 1
    p0_tape = p0_actions[1:]
    p1_tape = p1_actions[1:]
    
    print(f"\nReplaying episode 91684995 with seed {ep['info']['seed']}...")
    
    def agent_p0(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        return p0_tape[min(step, len(p0_tape)-1)]
        
    def agent_p1(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        return p1_tape[min(step, len(p1_tape)-1)]

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": ep['info']['seed']}, debug=False)
    env.run([agent_p0, agent_p1])
    
    r0 = env.state[0].get("reward", 0)
    r1 = env.state[1].get("reward", 0)
    print(f"Replay Result: V17 Reward = {r0} (actual was {ep['rewards'][0]}), THUNDER Reward = {r1} (actual was {ep['rewards'][1]})")

if __name__ == '__main__':
    analyze()
