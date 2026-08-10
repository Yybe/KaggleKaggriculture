"""Clean H2H Evaluation Harness with flushed stdout and suppressed OpenSpiel spam."""
import os
import sys
import json
import glob
import copy
from collections import Counter

# Suppress OpenSpiel spam
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '.')
import submission
from kaggle_environments import make

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

def make_route_agent(route):
    def agent_fn(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        s = min(max(0, step), len(route) - 1)
        action = copy.deepcopy(route[s])
        action = submission._weed_repair_action(obs, action, route, s)
        return submission._align_hands(action, obs)
    return agent_fn

th1_agent = make_route_agent(thunder1_route)
th2_agent = make_route_agent(thunder2_route)

# Extract HealthStone tape
hs_files = sorted(glob.glob(r'replays_new/healthstone/*.json'))
hs_route = None
if hs_files:
    with open(hs_files[0], 'r', encoding='utf-8') as f:
        hs_rep = json.load(f)
    teams = hs_rep.get('info', {}).get('TeamNames', [])
    hs_slot = teams.index('HealthStone') if 'HealthStone' in teams else 0
    hs_route = [step[hs_slot]['action'] for step in hs_rep['steps']][1:]
    hs_agent = make_route_agent(hs_route)
else:
    hs_agent = None

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]
LOSING_SEEDS = [1176492926, 449229689]

def run_match(fn0, fn1, seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([fn0, fn1])
    st = env.state
    r0 = st[0].get("reward", 0) or 0
    r1 = st[1].get("reward", 0) or 0
    return r0, r1

def evaluate(name_a, agent_a, name_b, agent_b, seeds, tag=""):
    print(f"\n=======================================================", flush=True)
    print(f"H2H: {name_a} vs {name_b} | {tag} ({len(seeds)} seeds x 2 seats = {len(seeds)*2} games)", flush=True)
    print(f"=======================================================", flush=True)
    wins, losses, ties = 0, 0, 0
    deltas = []
    
    for seed in seeds:
        for swap in (0, 1):
            if swap == 0:
                ra, rb = run_match(agent_a, agent_b, seed)
            else:
                rb, ra = run_match(agent_b, agent_a, seed)
            delta = ra - rb
            deltas.append(delta)
            if delta > 0:
                wins += 1
                res = "WIN "
            elif delta < 0:
                losses += 1
                res = "LOSS"
            else:
                ties += 1
                res = "TIE "
            print(f"  Seed {seed:10d} (seat={swap}): {name_a}={ra:7.0f} vs {name_b}={rb:7.0f} | delta={delta:+7.0f} | {res}", flush=True)
            
    win_rate = (wins / len(deltas)) * 100
    mean_delta = sum(deltas) / len(deltas)
    print(f"--> TOTAL: {wins}W / {losses}L / {ties}T ({win_rate:.1f}%) | Mean Delta: {mean_delta:+7.1f}\n", flush=True)
    return wins, losses, ties, mean_delta

if __name__ == '__main__':
    # 1. Baseline: V17 vs THUNDER-1
    evaluate("V17", submission.agent, "THUNDER_1", th1_agent, GATE_SEEDS, "8-Seed Gate")
    # 2. Baseline: V17 vs THUNDER-2
    evaluate("V17", submission.agent, "THUNDER_2", th2_agent, GATE_SEEDS, "8-Seed Gate")
    # 3. Exact losing seeds
    evaluate("V17", submission.agent, "THUNDER_1", th1_agent, LOSING_SEEDS, "Losing Seeds")
    evaluate("V17", submission.agent, "THUNDER_2", th2_agent, LOSING_SEEDS, "Losing Seeds")
    if hs_agent:
        evaluate("V17", submission.agent, "HealthStone", hs_agent, GATE_SEEDS, "8-Seed Gate")
        evaluate("V17", submission.agent, "HealthStone", hs_agent, LOSING_SEEDS, "Losing Seeds")
