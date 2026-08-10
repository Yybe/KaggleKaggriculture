"""Run fresh seeds tournament batch."""
import os
import sys
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, '.')

import tools.sim_worker as sim_worker

FRESH_SEEDS = [100000 + i * 7919 for i in range(12)]

if __name__ == '__main__':
    tasks = []
    for opp in ["v17_apex", "th1", "th2"]:
        for s in FRESH_SEEDS:
            tasks.append(("v18_apex", opp, s, False))
            tasks.append(("v18_apex", opp, s, True))
            
    print(f"Running {len(tasks)} fresh seeds matches across 14 workers...", flush=True)
    t0 = time.time()
    
    out_file = open('results/tournament_live.jsonl', 'a', encoding='utf-8')
    completed = 0
    with ProcessPoolExecutor(max_workers=14) as ex:
        future_map = {ex.submit(sim_worker.simulate_match, t): t for t in tasks}
        for fut in as_completed(future_map):
            completed += 1
            name_a, name_b, seed, swap, score_a, score_b, err = fut.result()
            if err:
                continue
            delta = score_a - score_b
            res_dict = {
                "idx": completed + 51,
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
            if completed % 12 == 0 or completed == len(tasks):
                print(f"Progress: {completed}/{len(tasks)} ({completed/len(tasks)*100:.1f}%) in {time.time()-t0:.1f}s", flush=True)
    out_file.close()
    print(f"Fresh seeds batch complete in {time.time()-t0:.1f}s!")
