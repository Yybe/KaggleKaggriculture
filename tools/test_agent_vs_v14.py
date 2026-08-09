"""Clean, fast benchmark runner to evaluate any agent against V14 across N seeds with paired seats."""
import os
import sys
import time
import statistics
import importlib.util
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath('agents'))
sys.path.insert(0, os.path.abspath('Kaggriculture'))

def _play_single(args):
    agent_a_file, agent_b_file, seed, swap = args
    from kaggle_environments import make
    
    spec_a = importlib.util.spec_from_file_location("mod_eval_a", agent_a_file)
    mod_a = importlib.util.module_from_spec(spec_a)
    spec_a.loader.exec_module(mod_a)
    
    spec_b = importlib.util.spec_from_file_location("mod_eval_b", agent_b_file)
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


def run_benchmark(agent_a_path, agent_b_path, n_seeds=20, max_workers=14):
    t0 = time.perf_counter()
    tasks = []
    for s in range(n_seeds):
        seed = 2000 + s * 73
        tasks.append((agent_a_path, agent_b_path, seed, False))
        tasks.append((agent_a_path, agent_b_path, seed, True))
    
    n_total = len(tasks)
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        for r in ex.map(_play_single, tasks):
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
    
    name_a = os.path.basename(agent_a_path)
    name_b = os.path.basename(agent_b_path)
    
    print(f"\n==========================================================================")
    print(f"BENCHMARK: {name_a} vs {name_b}")
    print(f"Games: {n_total} ({n_seeds} seeds x 2 seats) | Ok: {len(ok)} | Errs: {len(errs)} | Time: {dt:.1f}s ({n_total/dt:.1f} g/s)")
    if ok:
        win_pct = wins_a / len(ok) * 100
        mean_d = statistics.mean(deltas)
        med_d = statistics.median(deltas)
        print(f"  --> {name_a}: {wins_a} W ({win_pct:.1f}%), {wins_b} L, {ties} T")
        print(f"  --> Mean Delta: {mean_d:+.0f} | Median Delta: {med_d:+.0f} | Min: {min(deltas):+.0f} | Max: {max(deltas):+.0f}")
        print(f"  --> {name_a} Avg Score: {statistics.mean(scores_a):.0f} | {name_b} Avg Score: {statistics.mean(scores_b):.0f}")
    print(f"==========================================================================\n")
    return wins_a, wins_b, ties, deltas

if __name__ == '__main__':
    agent_a = sys.argv[1] if len(sys.argv) > 1 else 'agents/kaggle_v14_tweaked.py'
    agent_b = sys.argv[2] if len(sys.argv) > 2 else 'agents/kaggle_boat84_v14.py'
    n_seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    run_benchmark(os.path.abspath(agent_a), os.path.abspath(agent_b), n_seeds=n_seeds)
