"""Fast, robust benchmark suite for V18 Apex with JSON export and UTF-8 console output."""
import os
import sys
import json
import copy
import time
from concurrent.futures import ProcessPoolExecutor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Suppress OpenSpiel spam
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")

# Load precomputed routes
with open('tools/routes_precomputed.json', 'r', encoding='utf-8') as f:
    PRECOMPUTED = json.load(f)

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]
LOSING_SEEDS = [1176492926, 449229689]

def play_match_worker(args):
    agent_a_name, agent_b_name, seed, swap = args
    import sys
    sys.path.insert(0, '.')
    import submission
    import WybeV2.v18_apex as v18_apex
    from kaggle_environments import make

    th1_route = PRECOMPUTED["th1"]
    th2_route = PRECOMPUTED["th2"]

    def th1_agent(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        s = min(max(0, step), len(th1_route) - 1)
        action = copy.deepcopy(th1_route[s])
        action = submission._weed_repair_action(obs, action, th1_route, s)
        action = submission._v16_convert_livestock(action, obs, s)
        action = submission._v16_wool_controller(action, obs, s)
        return submission._align_hands(action, obs)

    def th2_agent(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        s = min(max(0, step), len(th2_route) - 1)
        action = copy.deepcopy(th2_route[s])
        action = submission._weed_repair_action(obs, action, th2_route, s)
        action = submission._v16_convert_livestock(action, obs, s)
        action = submission._v16_wool_controller(action, obs, s)
        return submission._align_hands(action, obs)

    agents = {
        "v18_apex": v18_apex.agent,
        "v17_apex": submission.agent,
        "th1": th1_agent,
        "th2": th2_agent,
    }
    
    fn_a = agents[agent_a_name]
    fn_b = agents[agent_b_name]
    
    fn0 = fn_b if swap else fn_a
    fn1 = fn_a if swap else fn_b
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        st = env.state
        r0 = float(st[0].get("reward", 0) or 0)
        r1 = float(st[1].get("reward", 0) or 0)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return agent_a_name, agent_b_name, seed, swap, score_a, score_b, None
    except Exception as e:
        return agent_a_name, agent_b_name, seed, swap, 0, 0, str(e)

def run_suite(agent_a_name, opp_names, seeds, tag="", max_workers=14):
    tasks = []
    for opp in opp_names:
        for s in seeds:
            tasks.append((agent_a_name, opp, s, False))
            tasks.append((agent_a_name, opp, s, True))
            
    print(f"\n[{tag}] Running {len(tasks)} matches for {agent_a_name} vs {opp_names} across {max_workers} workers...", flush=True)
    t0 = time.time()
    
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        for r in ex.map(play_match_worker, tasks):
            results.append(r)
            
    dt = time.time() - t0
    print(f"[{tag}] Completed {len(tasks)} matches in {dt:.1f}s ({dt/len(tasks):.2f}s/match effective).", flush=True)
    
    by_opp = {}
    for name_a, name_b, seed, swap, score_a, score_b, err in results:
        if err:
            print(f"  Error in match {name_a} vs {name_b} seed {seed}: {err}", flush=True)
            continue
        if name_b not in by_opp:
            by_opp[name_b] = []
        by_opp[name_b].append({
            "seed": seed, "swap": swap, "score_a": score_a, "score_b": score_b, "delta": score_a - score_b
        })
        
    print("\n" + "="*85, flush=True)
    print(f"{'Opponent':<15} | {'Games':>5} | {'Record':>10} | {'Win Rate':>8} | {'Mean Delta':>10} | {'Min Delta':>10} | {'Max Delta':>10}", flush=True)
    print("="*85, flush=True)
    
    summary = {}
    for opp, rows in by_opp.items():
        deltas = [r["delta"] for r in rows]
        wins = sum(1 for d in deltas if d > 0)
        losses = sum(1 for d in deltas if d < 0)
        ties = sum(1 for d in deltas if d == 0)
        n = len(deltas)
        wr = (wins / n) * 100 if n else 0
        md = sum(deltas) / n if n else 0
        mind = min(deltas) if deltas else 0
        maxd = max(deltas) if deltas else 0
        print(f"{opp:<15} | {n:5d} | {wins:2d}W/{losses:2d}L/{ties:1d}T | {wr:7.1f}% | {md:+10.1f} | {mind:+10.1f} | {maxd:+10.1f}", flush=True)
        summary[opp] = {
            "games": n, "wins": wins, "losses": losses, "ties": ties, "win_rate": wr,
            "mean_delta": md, "min_delta": mind, "max_delta": maxd, "matches": rows
        }
    print("="*85, flush=True)
    return summary

if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    all_results = {}
    
    # 1. Gate Benchmark: V18 Apex vs V17, TH1, TH2
    all_results["gate_8_seeds"] = run_suite("v18_apex", ["v17_apex", "th1", "th2"], GATE_SEEDS, "8-Seed Gate")
    
    # 2. Exact Losing Seeds Benchmark
    all_results["losing_seeds"] = run_suite("v18_apex", ["v17_apex", "th1", "th2"], LOSING_SEEDS, "Losing Seeds")
    
    # 3. 25 Fresh Seeds (50 Games each)
    fresh_seeds = [100000 + i * 7919 for i in range(25)]
    all_results["fresh_25_seeds"] = run_suite("v18_apex", ["v17_apex", "th1", "th2"], fresh_seeds, "25 Fresh Seeds")
    
    with open('results/benchmark_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print("\nBenchmark results saved to results/benchmark_results.json successfully!")
