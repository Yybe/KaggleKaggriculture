"""Real-time streaming tournament benchmark for V18 Apex."""
import os
import sys
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, '.')

import tools.sim_worker as sim_worker

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]
LOSING_SEEDS = [1176492926, 449229689]
FRESH_SEEDS = [100000 + i * 7919 for i in range(12)]

def run_tournament(tasks, out_fp, max_workers=14):
    os.makedirs(os.path.dirname(out_fp), exist_ok=True)
    out_file = open(out_fp, 'w', encoding='utf-8')
    
    print(f"Starting tournament of {len(tasks)} matches across {max_workers} workers...", flush=True)
    t0 = time.time()
    
    completed = 0
    results_by_opp = {}
    
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        future_map = {ex.submit(sim_worker.simulate_match, t): t for t in tasks}
        for fut in as_completed(future_map):
            completed += 1
            name_a, name_b, seed, swap, score_a, score_b, err = fut.result()
            if err:
                print(f"[{completed}/{len(tasks)}] ERROR in {name_a} vs {name_b} seed {seed}: {err}", flush=True)
                continue
                
            delta = score_a - score_b
            res_dict = {
                "idx": completed,
                "agent_a": name_a,
                "agent_b": name_b,
                "seed": seed,
                "swap": swap,
                "score_a": score_a,
                "score_b": score_b,
                "delta": delta,
                "outcome": "WIN" if delta > 0 else ("LOSS" if delta < 0 else "TIE")
            }
            out_file.write(json.dumps(res_dict) + '\n')
            out_file.flush()
            
            if name_b not in results_by_opp:
                results_by_opp[name_b] = []
            results_by_opp[name_b].append(delta)
            
            if completed % 10 == 0 or completed == len(tasks):
                print(f"Progress: {completed}/{len(tasks)} matches completed ({completed/len(tasks)*100:.1f}%) in {time.time()-t0:.1f}s", flush=True)

    out_file.close()
    dt = time.time() - t0
    print(f"\nTournament completed in {dt:.1f}s ({dt/len(tasks):.2f}s/match).", flush=True)
    
    print("\n" + "="*85, flush=True)
    print(f"{'Opponent':<15} | {'Games':>5} | {'Record':>10} | {'Win Rate':>8} | {'Mean Delta':>10} | {'Min Delta':>10} | {'Max Delta':>10}", flush=True)
    print("="*85, flush=True)
    
    for opp, deltas in sorted(results_by_opp.items()):
        wins = sum(1 for d in deltas if d > 0)
        losses = sum(1 for d in deltas if d < 0)
        ties = sum(1 for d in deltas if d == 0)
        n = len(deltas)
        wr = (wins / n) * 100 if n else 0
        md = sum(deltas) / n if n else 0
        mind = min(deltas) if deltas else 0
        maxd = max(deltas) if deltas else 0
        print(f"{opp:<15} | {n:5d} | {wins:2d}W/{losses:2d}L/{ties:1d}T | {wr:7.1f}% | {md:+10.1f} | {mind:+10.1f} | {maxd:+10.1f}", flush=True)
    print("="*85, flush=True)

if __name__ == '__main__':
    all_tasks = []
    
    # 1. 8-Seed Gate (16 games vs each opponent: V17, TH1, TH2) = 48 games
    for opp in ["v17_apex", "th1", "th2"]:
        for s in GATE_SEEDS:
            all_tasks.append(("v18_apex", opp, s, False))
            all_tasks.append(("v18_apex", opp, s, True))
            
    # 2. Losing Seeds (4 games vs each) = 12 games
    for opp in ["v17_apex", "th1", "th2"]:
        for s in LOSING_SEEDS:
            all_tasks.append(("v18_apex", opp, s, False))
            all_tasks.append(("v18_apex", opp, s, True))
            
    # 3. 12 Fresh Seeds (24 games vs each) = 72 games
    for opp in ["v17_apex", "th1", "th2"]:
        for s in FRESH_SEEDS:
            all_tasks.append(("v18_apex", opp, s, False))
            all_tasks.append(("v18_apex", opp, s, True))
            
    print(f"Total tournament matches prepared: {len(all_tasks)}")
    run_tournament(all_tasks, 'results/tournament_live.jsonl', max_workers=14)
