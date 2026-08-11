"""Fast parallel evaluation script for V18 APEXX agent using ThreadPoolExecutor."""
import os
import sys
import json
import glob
import time
from concurrent.futures import ThreadPoolExecutor

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '.')
import submission
from kaggle_environments import make

# 1. Load consensus routes
tape_dir = r'replays_new/tape_library'
sub1_files = [fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55373222_' in fp]
sub2_files = [fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55381094_' in fp]

def get_consensus(files):
    from collections import Counter
    eps = [json.load(open(fp, 'r', encoding='utf-8'))['route'][1:] for fp in files]
    cons = []
    for s in range(719):
        c = Counter(json.dumps(ep[s], sort_keys=True, separators=(',', ':')) for ep in eps)
        cons.append(json.loads(c.most_common(1)[0][0]))
    return cons

_TH1_ROUTE = get_consensus(sub1_files)
_TH2_ROUTE = get_consensus(sub2_files)
_V17_ROUTE = submission._REBALANCE_ACTIONS

ROUTES = {
    "v17": _V17_ROUTE,
    "th1": _TH1_ROUTE,
    "th2": _TH2_ROUTE,
}

from agents.kaggle_v18_apexx import V18ApexAgent

class RouteReplayAgent:
    def __init__(self, route_name):
        self.route_name = route_name
        
    def __call__(self, obs, configuration=None):
        import copy
        route = ROUTES[self.route_name]
        step = int(obs.get("step", 0) or 0)
        s = min(max(0, step), len(route) - 1)
        action = copy.deepcopy(route[s])
        action = submission._weed_repair_action(obs, action, route, s)
        return submission._align_hands(action, obs)

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]

def play_match(args):
    agent_a_name, agent_b_name, seed, swap = args
    if agent_a_name == "apexx":
        agent_a = V18ApexAgent()
    else:
        agent_a = RouteReplayAgent(agent_a_name)
        
    agent_b = RouteReplayAgent(agent_b_name)
    fn0 = agent_b if swap else agent_a
    fn1 = agent_a if swap else agent_b
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        st = env.state
        r0 = float(st[0].get("reward", 0) or 0)
        r1 = float(st[1].get("reward", 0) or 0)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return score_a, score_b, score_a - score_b
    except Exception as e:
        return 0.0, 0.0, 0.0

def run_suite():
    opps = ["th1", "th2", "v17"]
    tasks = []
    task_info = []
    
    for opp in opps:
        for s in GATE_SEEDS:
            for swap in (False, True):
                tasks.append(("apexx", opp, s, swap))
                task_info.append((opp, s, swap))
                
    print(f"Starting thread pool evaluation of {len(tasks)} matches across 4 workers...")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(play_match, tasks))
    t1 = time.time()
    print(f"Evaluation completed in {t1 - t0:.2f} seconds.\n")
    
    by_opp = {}
    for (opp, s, swap), (s_a, s_b, d) in zip(task_info, results):
        by_opp.setdefault(opp, []).append((s, swap, s_a, s_b, d))
        
    print("=" * 70)
    print(f"{'Opponent':<15} | {'Wins':<6} | {'Losses':<6} | {'Ties':<6} | {'Mean Delta':<12}")
    print("=" * 70)
    for opp, res in by_opp.items():
        wins = sum(1 for x in res if x[4] > 0)
        losses = sum(1 for x in res if x[4] < 0)
        ties = sum(1 for x in res if x[4] == 0)
        mean_d = sum(x[4] for x in res) / len(res)
        print(f"{opp:<15} | {wins:<6} | {losses:<6} | {ties:<6} | {mean_d:+12.1f}")
    print("=" * 70)

if __name__ == '__main__':
    run_suite()
