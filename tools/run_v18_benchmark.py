"""Complete, robust tournament benchmark runner for V18 Apex."""
import os
import sys
import json
import time
from concurrent.futures import ProcessPoolExecutor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, '.')
import tools.sim_worker as sim_worker

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]
LOSING_SEEDS = [1176492926, 449229689]
FRESH_SEEDS = [100000 + i * 7919 for i in range(20)]

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
        for r in ex.map(sim_worker.simulate_match, tasks):
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
    
    # 1. 8-Seed Gate
    all_results["gate_8_seeds"] = run_suite("v18_apex", ["v17_apex", "th1", "th2"], GATE_SEEDS, "8-Seed Gate")
    
    # 2. Losing Seeds
    all_results["losing_seeds"] = run_suite("v18_apex", ["v17_apex", "th1", "th2"], LOSING_SEEDS, "Losing Seeds")
    
    # 3. 20 Fresh Seeds
    all_results["fresh_20_seeds"] = run_suite("v18_apex", ["v17_apex", "th1", "th2"], FRESH_SEEDS, "20 Fresh Seeds")
    
    with open('results/v18_final_benchmark.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print("\nFinal tournament results saved to results/v18_final_benchmark.json successfully!", flush=True)
