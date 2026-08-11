"""NEW-SEED rebenchmark: V18 APEXX (tuned champion) vs all local models.

Controlled experiment: uses a FRESH set of seeds that do NOT overlap the
original 8-seed gate family ([1000000, 2000000, 3330000, 5000000, 6000000,
7770000, 8000000, 9000000]). This tests whether V18 APEXX's champion status
generalizes or was overfit to the original seed family.

Each opponent is played 2x per seed (both seat orders) to control for seat bias.

Outputs:
  results/rebench_fresh_v18apexx.jsonl  (raw per-match lines)
  results/rebench_fresh_v18apexx.json   (aggregated summary)
  results/rebench_fresh_v18apexx.txt    (human table)
"""
import os, sys, json, time, copy
from concurrent.futures import ProcessPoolExecutor, as_completed

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
sys.path.insert(0, BASE)

# Static imports exactly like the proven test_vs_local_agents.py harness.
import agents.kaggle_v18_apexx as v18_apexx
import agents.submission_v16a_backup_20260810 as v17_apex
import agents.kaggle_champion_v155 as v155
import agents.kaggle_v16a_counterpreempt as v16a
import agents.kaggle_v23 as v23
import agents.salemali7_3000score as salem
import agents.kaggle_v26b as v26b
import agents.kaggle_v26_aggr_evidence as v26aggr
import agents.kaggle_v22_romanrozen as v22
import agents.kaggle_champion_v15 as v15
import agents.kaggle_v14_v26style as v14v26
import agents.kaggle_v14_tweaked as v14tw
import agents.kaggle_boat84_v14 as boat84

from agents.kaggle_v18_apexx import V18ApexAgent

# Fresh seed set - deliberately disjoint from the original 8 gate seeds.
# Use deterministic pseudo-random seeds based on prime offset.
FRESH_SEEDS = [314159, 2718281, 1414213, 1732050, 2236067, 2645751,
               3162277, 3245553, 3316624, 3464101, 3588989, 3660254,
               2426406, 2469507, 2549509, 2641391, 2745995, 2871778]

# Opponents to test V18 APEXX against (more than just the 4 used before).
LOCAL_FLEET = {
    "v17_apex":      v17_apex.agent,
    "v155_champion": v155.agent,
    "v16a_counter":  v16a.agent,
    "v23_kaito":     v23.agent,
    "salemali7_3k":  salem.agent,
    "v26b":          v26b.agent,
    "v26_aggr":      v26aggr.agent,
    "v22_romanrozen": v22.agent,
    "champ_v15":     v15.agent,
    "v14_v26style":  v14v26.agent,
    "v14_tweaked":   v14tw.agent,
    "boat84_v14":    boat84.agent,
}

def play_match(task):
    """Play a match where contested seat is the CHAMPION (V18 APEXX).
    task = (opp_key, seed, swap). Return (opp_key, seed, swap, score_champ, score_opp, err)."""
    from kaggle_environments import make
    opp_key, seed, swap = task
    opp_fn = LOCAL_FLEET[opp_key]

    # Champ uses a FRESH instance per match (carries state across steps).
    champ_inst = V18ApexAgent()

    def champ_call(obs, configuration=None):
        return champ_inst(obs, configuration)

    fn0 = opp_fn if swap else champ_call
    fn1 = champ_call if swap else opp_fn

    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        st = env.state
        r0 = float(st[0].get("reward", 0) or 0)
        r1 = float(st[1].get("reward", 0) or 0)
        score_champ = r1 if swap else r0
        score_opp = r0 if swap else r1
        return opp_key, seed, swap, score_champ, score_opp, None
    except Exception as e:
        return opp_key, seed, swap, 0.0, 0.0, str(e)[:120]

def main():
    os.makedirs('results', exist_ok=True)
    all_tasks = []
    for key in LOCAL_FLEET:
        for s in FRESH_SEEDS:
            all_tasks.append((key, s, False))
            all_tasks.append((key, s, True))

    print(f"NEW-SEED REBENCHMARK: V18 APEXX (champ) vs {len(LOCAL_FLEET)} local models")
    print(f"Seeds used: {len(FRESH_SEEDS)} (disjoint from original 8-seed gate).")
    print(f"Total matches: {len(all_tasks)}  (2 seats x {len(FRESH_SEEDS)} seeds x {len(LOCAL_FLEET)} opponents)")
    t0 = time.time()

    jsonl_out = open('results/rebench_fresh_v18apexx.jsonl', 'w', encoding='utf-8')
    completed = 0
    results_by_opp = {}

    with ProcessPoolExecutor(max_workers=14) as ex:
        fut_map = {ex.submit(play_match, t): t for t in all_tasks}
        for fut in as_completed(fut_map):
            opp_key, seed, swap, sc, so, err = fut.result()
            completed += 1
            if err:
                print(f"  [{completed}/{len(all_tasks)}] ERR {opp_key} seed {seed} swap {swap}: {err}", flush=True)
                continue
            delta = sc - so
            rec = {"opp": opp_key, "seed": seed, "swap": swap,
                   "score_champ": sc, "score_opp": so, "delta": delta,
                   "outcome": "WIN" if delta > 0 else ("LOSS" if delta < 0 else "TIE")}
            jsonl_out.write(json.dumps(rec) + '\n')
            jsonl_out.flush()
            results_by_opp.setdefault(opp_key, []).append(delta)
            if completed % 24 == 0 or completed == len(all_tasks):
                print(f"  progress {completed}/{len(all_tasks)} in {time.time()-t0:.1f}s", flush=True)

    jsonl_out.close()

    # Summary
    summary = {}
    print("\n" + "="*95)
    print(f"{'Opponent':<16} | {'Games':>5} | {'Record':>10} | {'Win%':>6} | {'Mean Delta':>12} | {'Min':>10} | {'Max':>10}")
    print("-"*95)
    for opp_key, deltas in sorted(results_by_opp.items()):
        wins = sum(1 for d in deltas if d > 0)
        losses = sum(1 for d in deltas if d < 0)
        ties = sum(1 for d in deltas if d == 0)
        n = len(deltas)
        wr = (wins / n) * 100 if n else 0
        md = sum(deltas) / n if n else 0
        mind = min(deltas) if deltas else 0
        maxd = max(deltas) if deltas else 0
        print(f"{opp_key:<16} | {n:5d} | {wins:2d}W/{losses:2d}L/{ties:1d}T | {wr:5.1f}% | {md:+12.1f} | {mind:+10.0f} | {maxd:+10.0f}")
        summary[opp_key] = {"games": n, "wins": wins, "losses": losses, "ties": ties,
                            "win_rate": wr, "mean_delta": md, "min_delta": mind, "max_delta": maxd}
    print("="*95)

    with open('results/rebench_fresh_v18apexx.json', 'w', encoding='utf-8') as f:
        json.dump({"seeds": FRESH_SEEDS, "summary": summary}, f, indent=2)
    print(f"\nSaved: results/rebench_fresh_v18apexx.json  (elapsed {time.time()-t0:.1f}s)")

if __name__ == '__main__':
    main()
