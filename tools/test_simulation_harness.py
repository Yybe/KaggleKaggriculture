"""Local simulation benchmark harness for V17 vs THUNDER-1 vs THUNDER-2."""
import json
import glob
import os
import sys
import copy
from collections import Counter
from kaggle_environments import make

sys.path.insert(0, '.')
import submission

# Load THUNDER consensus routes
tape_dir = r'replays_new/tape_library'
sub1_files = [fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55373222_' in fp]
sub2_files = [fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55381094_' in fp]

def get_consensus(files):
    eps = [json.load(open(fp, 'r', encoding='utf-8'))['route'][1:] for fp in files]
    cons = []
    for s in range(719):
        c = Counter(json.dumps(ep[s], sort_keys=True, separators=(',', ':')) for ep in eps)
        cons.append(json.loads(c.most_common(1)[0][0]))
    return cons

thunder1_route = get_consensus(sub1_files)
thunder2_route = get_consensus(sub2_files)

# Dynamic wrappers for THUNDER agents: route replay + basic weed repair / livestock / wool
def make_route_agent(route):
    def agent_fn(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        s = min(max(0, step), len(route) - 1)
        action = copy.deepcopy(route[s])
        
        # apply weed repair if needed
        action = submission._weed_repair_action(obs, action, route, s)
        return submission._align_hands(action, obs)
    return agent_fn

th1_agent = make_route_agent(thunder1_route)
th2_agent = make_route_agent(thunder2_route)

# Standard benchmark seed families
GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]
LOSING_SEEDS = [1176492926, 449229689] # The 2 seeds from the losing matches folder!

def run_match(agent_a, agent_b, seed, swap=False):
    if swap:
        fn0, fn1 = agent_b, agent_a
    else:
        fn0, fn1 = agent_a, agent_b
        
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([fn0, fn1])
    st = env.state
    r0 = st[0].get("reward", 0) or 0
    r1 = st[1].get("reward", 0) or 0
    
    if swap:
        return r1, r0 # return (agent_a_score, agent_b_score)
    else:
        return r0, r1

def evaluate_pair(name_a, agent_a, name_b, agent_b, seeds):
    print(f"\n=======================================================")
    print(f"H2H EVALUATION: {name_a} vs {name_b} ({len(seeds)} seeds x 2 seats = {len(seeds)*2} games)")
    print(f"=======================================================")
    wins, losses, ties = 0, 0, 0
    deltas = []
    
    for seed in seeds:
        for swap in [0, 1]:
            ra, rb = run_match(agent_a, agent_b, seed, swap=bool(swap))
            delta = ra - rb
            deltas.append(delta)
            if delta > 0:
                wins += 1
                outcome = "WIN "
            elif delta < 0:
                losses += 1
                outcome = "LOSS"
            else:
                ties += 1
                outcome = "TIE "
            print(f"Seed {seed:10d} (swap={swap}): {name_a}={ra:7.0f} | {name_b}={rb:7.0f} | delta={delta:+7.0f} | {outcome}")
            
    mean_delta = sum(deltas) / len(deltas)
    win_rate = (wins / len(deltas)) * 100
    print(f"\nRESULT: {wins}W / {losses}L / {ties}T ({win_rate:.1f}% Win Rate) | Mean Delta: {mean_delta:+7.1f}")
    return wins, losses, ties, mean_delta

if __name__ == '__main__':
    # 1. Run V17 vs THUNDER-1
    evaluate_pair("V17", submission.agent, "THUNDER_1", th1_agent, GATE_SEEDS)
    # 2. Run V17 vs THUNDER-2
    evaluate_pair("V17", submission.agent, "THUNDER_2", th2_agent, GATE_SEEDS)
    # 3. Run on the exact losing seed 1176492926
    evaluate_pair("V17", submission.agent, "THUNDER_1", th1_agent, LOSING_SEEDS)
    evaluate_pair("V17", submission.agent, "THUNDER_2", th2_agent, LOSING_SEEDS)
