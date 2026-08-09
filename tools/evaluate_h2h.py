"""Evaluation script to run head-to-head simulations between candidate agents and V14."""
import os
import sys
import time
import statistics
from concurrent.futures import ProcessPoolExecutor

# Add paths
sys.path.insert(0, os.path.abspath('agents'))
sys.path.insert(0, os.path.abspath('Kaggriculture'))

from harness import resolve_agent

def play_match(args):
    agent_a_path, agent_b_path, seed, swap = args
    import importlib.util
    from kaggle_environments import make
    
    # Import agent A
    spec_a = importlib.util.spec_from_file_location("mod_a", agent_a_path)
    mod_a = importlib.util.module_from_spec(spec_a)
    spec_a.loader.exec_module(mod_a)
    
    # Import agent B
    spec_b = importlib.util.spec_from_file_location("mod_b", agent_b_path)
    mod_b = importlib.util.module_from_spec(spec_b)
    spec_b.loader.exec_module(mod_b)
    
    p0 = mod_b.agent if swap else mod_a.agent
    p1 = mod_a.agent if swap else mod_b.agent
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([p0, p1])
        r0 = float(env.steps[-1][0].reward)
        r1 = float(env.steps[-1][1].reward)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return seed, swap, score_a, score_b, None
    except Exception as e:
        return seed, swap, None, None, str(e)

def run_h2h(agent_a_path, agent_b_path, n_seeds=25, workers=14):
    """Runs paired seats on n_seeds (total 2*n_seeds games) to cancel first-player advantage."""
    t0 = time.perf_counter()
    tasks = []
    for s in range(n_seeds):
        seed = 1000 + s * 37
        tasks.append((agent_a_path, agent_b_path, seed, False))
        tasks.append((agent_a_path, agent_b_path, seed, True))
    
    n_total = len(tasks)
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(play_match, tasks):
            results.append(r)
    
    dt = time.perf_counter() - t0
    
    ok = [r for r in results if r[4] is None and r[2] is not None]
    errs = [r for r in results if r[4] is not None]
    
    wins_a = sum(1 for r in ok if r[2] > r[3])
    wins_b = sum(1 for r in ok if r[3] > r[2])
    ties = sum(1 for r in ok if r[2] == r[3])
    
    scores_a = [r[2] for r in ok]
    scores_b = [r[3] for r in ok]
    deltas = [r[2] - r[3] for r in ok]
    
    print(f"\n========================================================")
    print(f"H2H Evaluation: {os.path.basename(agent_a_path)} vs {os.path.basename(agent_b_path)}")
    print(f"Games: {n_total} (ok={len(ok)}, err={len(errs)}, wall={dt:.1f}s, rate={n_total/dt:.1f} g/s)")
    if ok:
        print(f"  A ({os.path.basename(agent_a_path)}): {wins_a} wins ({wins_a/len(ok)*100:.1f}%) | Avg={statistics.mean(scores_a):.0f} | Med={statistics.median(scores_a):.0f}")
        print(f"  B ({os.path.basename(agent_b_path)}): {wins_b} wins ({wins_b/len(ok)*100:.1f}%) | Avg={statistics.mean(scores_b):.0f} | Med={statistics.median(scores_b):.0f}")
        print(f"  Ties: {ties} ({ties/len(ok)*100:.1f}%)")
        print(f"  Avg Delta (A - B): {statistics.mean(deltas):+.0f} | Med Delta: {statistics.median(deltas):+.0f}")
        print(f"  Min Delta: {min(deltas):+.0f} | Max Delta: {max(deltas):+.0f}")
    print(f"========================================================\n")
    return wins_a, wins_b, ties, deltas

if __name__ == '__main__':
    v14_path = os.path.abspath('agents/kaggle_boat84_v14.py')
    run_h2h(v14_path, v14_path, n_seeds=5)
