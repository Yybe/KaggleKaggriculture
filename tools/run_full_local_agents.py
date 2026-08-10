"""Fast synchronous benchmark of V18 Apex vs local agents."""
import os
import sys
import json
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, '.')

import submission as v18_apex
import agents.kaggle_champion_v155 as v155
import agents.kaggle_v16a_counterpreempt as v16a
import agents.kaggle_v23 as v23
import agents.salemali7_3000score as salem
import agents.submission_v16a_backup_20260810 as v17_apex
from kaggle_environments import make

LOCAL_AGENTS = {
    "V17 Apex Baseline": v17_apex.agent,
    "Salemali7 3k": salem.agent,
    "V16a Counter-Preempt": v16a.agent,
    "V15.5 Champion": v155.agent,
    "V23 Kaito": v23.agent,
}

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]

if __name__ == '__main__':
    out_file = open('results/full_local_summary.txt', 'w', encoding='utf-8')
    def log(msg):
        print(msg, flush=True)
        out_file.write(str(msg) + '\n')
        out_file.flush()

    log("="*95)
    log(f"{'LOCAL AGENT BENCHMARK: V18 Apex vs Previous Local Agents':^95}")
    log("="*95)
    log(f"{'Local Agent Name':<22} | {'Games':>5} | {'Record':>10} | {'Win Rate':>8} | {'Mean V18 Score vs Opp':>25} | {'Mean Delta':>12}")
    log("-"*95)

    for name, agent_fn in LOCAL_AGENTS.items():
        wins, losses, ties = 0, 0, 0
        deltas, v18_scores, opp_scores = [], [], []
        
        for s in GATE_SEEDS:
            for swap in (False, True):
                fn0 = agent_fn if swap else v18_apex.agent
                fn1 = v18_apex.agent if swap else agent_fn
                try:
                    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
                    env.run([fn0, fn1])
                    r0 = float(env.state[0].get("reward", 0) or 0)
                    r1 = float(env.state[1].get("reward", 0) or 0)
                    sa = r1 if swap else r0
                    sb = r0 if swap else r1
                    d = sa - sb
                    deltas.append(d)
                    v18_scores.append(sa)
                    opp_scores.append(sb)
                    if d > 0: wins += 1
                    elif d < 0: losses += 1
                    else: ties += 1
                except Exception as e:
                    log(f"  Error vs {name} seed {s}: {e}")

        n = len(deltas)
        wr = (wins / n) * 100 if n else 0
        md = sum(deltas) / n if n else 0
        ms_v18 = sum(v18_scores) / n if n else 0
        ms_opp = sum(opp_scores) / n if n else 0
        log(f"{name:<22} | {n:5d} | {wins:2d}W/{losses:2d}L/{ties:1d}T | {wr:7.1f}% | {ms_v18:9.0f} vs {ms_opp:9.0f} | {md:+12.1f}")

    log("="*95)
    out_file.close()
