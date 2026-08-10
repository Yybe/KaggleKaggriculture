"""Streaming benchmark V18 Apex against full local agent fleet."""
import os
import sys
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, '.')

import submission as v18_apex
import agents.kaggle_champion_v155 as v155
import agents.kaggle_v16a_counterpreempt as v16a
import agents.kaggle_v23 as v23
import agents.salemali7_3000score as salem
import agents.submission_v16a_backup_20260810 as v17_apex

LOCAL_AGENTS = {
    "v17_apex": v17_apex.agent,
    "v16a_salem": v16a.agent,
    "salemali7_3k": salem.agent,
    "v155_champion": v155.agent,
    "v23_kaito": v23.agent,
}

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]

def play_match_local(args):
    opp_name, seed, swap = args
    from kaggle_environments import make
    
    fn_v18 = v18_apex.agent
    fn_opp = LOCAL_AGENTS[opp_name]
    
    fn0 = fn_opp if swap else fn_v18
    fn1 = fn_v18 if swap else fn_opp
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        st = env.state
        r0 = float(st[0].get("reward", 0) or 0)
        r1 = float(st[1].get("reward", 0) or 0)
        score_v18 = r1 if swap else r0
        score_opp = r0 if swap else r1
        return opp_name, seed, swap, score_v18, score_opp, None
    except Exception as e:
        return opp_name, seed, swap, 0, 0, str(e)

if __name__ == '__main__':
    tasks = []
    for opp_name in LOCAL_AGENTS:
        for s in GATE_SEEDS:
            tasks.append((opp_name, s, False))
            tasks.append((opp_name, s, True))
            
    print(f"Running V18 Apex vs {len(LOCAL_AGENTS)} Local Agents ({len(tasks)} matches)...", flush=True)
    t0 = time.time()
    
    os.makedirs('results', exist_ok=True)
    out_file = open('results/local_live.jsonl', 'w', encoding='utf-8')
    
    completed = 0
    with ProcessPoolExecutor(max_workers=14) as ex:
        futures = {ex.submit(play_match_local, t): t for t in tasks}
        for fut in as_completed(futures):
            completed += 1
            opp_name, seed, swap, score_v18, score_opp, err = fut.result()
            if err:
                print(f"[{completed}/{len(tasks)}] Error vs {opp_name} seed {seed}: {err}", flush=True)
                continue
            delta = score_v18 - score_opp
            rec = {
                "idx": completed, "opp": opp_name, "seed": seed, "swap": swap,
                "score_v18": score_v18, "score_opp": score_opp, "delta": delta,
                "outcome": "WIN" if delta > 0 else ("LOSS" if delta < 0 else "TIE")
            }
            out_file.write(json.dumps(rec) + '\n')
            out_file.flush()
            if completed % 10 == 0 or completed == len(tasks):
                print(f"Progress: {completed}/{len(tasks)} matches ({completed/len(tasks)*100:.1f}%) in {time.time()-t0:.1f}s", flush=True)

    out_file.close()
    print(f"Local agents tournament completed in {time.time()-t0:.1f}s!", flush=True)
