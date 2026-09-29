"""E257 gate - two estimators, pre-registered rule applied verbatim.

Stage A  H2H vs the parent spine (tetsutani_step1009) on R1+R2, both seats: a tie here means the
         graft is inert (the godview_v2 precedent), so ties are reported as NOT TESTED.
Stage B  paired ABSOLUTE estimator vs four out-of-fleet lineages on identical worlds (E224 protocol):
         arms = candidate and parent, same opponent, same seed, same seat order, delta paired per row.

Pre-registered promotion rule (E224, unchanged): per-lineage paired mean > -1,000/seat AND the worst
lineage mean >= -2,500.  Anything else is a reject: no deploy, no submit.
"""
import csv
import json
import os
import statistics
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

ARMS = {
    "CAND": os.path.join(REPO, "agents", "tetsutani_e257_fertflow.py"),
    "PARENT": os.path.join(REPO, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py"),
}
OPPS = [
    "agents/independent_phase_a13_eight_lane_20260924.py",
    "agents/independent_phase_a15_full_wheat_20260924.py",
    "agents/oblate_orderbook_full.py",
    "agents/friend_r78ub.py",
]
SEEDS = [15243000 + 1117 * i for i in range(11, 15)]
OUT = os.path.join(REPO, "TETS_COUNTER_20260929", "out")


def run_abs(args):
    from agent_loader import load_agent, verify_game_liveness
    from kaggle_environments import make
    import kaggle_environments
    arm, opp, seed, swap = args
    try:
        pa = load_agent(ARMS[arm])
        pb = load_agent(os.path.join(REPO, opp))
        if kaggle_environments.__version__ != "1.32.7":
            return dict(status="ENGINE_MOVED", arm=arm, opp=opp, seed=seed, swap=swap)
        ours, theirs = (pb, pa) if swap else (pa, pb)
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed,
                                                   "townCenterSellInterval": 24}, debug=False)
        env.run([ours, theirs])
        ok, err, _, _ = verify_game_liveness(env)
        if not ok:
            return dict(status="LIVENESS:%s" % err, arm=arm, opp=opp, seed=seed, swap=swap)
        r_us = float(env.steps[-1][0].reward)
        r_opp = float(env.steps[-1][1].reward)
        return dict(status="OK", arm=arm, opp=os.path.basename(opp), seed=seed, swap=swap,
                    bank=r_us, opp_bank=r_opp, vs_margin=r_us - r_opp)
    except Exception as exc:
        return dict(status="ERROR:%r" % exc, arm=arm, opp=opp, seed=seed, swap=swap)


def main():
    os.makedirs(OUT, exist_ok=True)
    tasks = [(a, o, s, sw) for o in OPPS for s in SEEDS for sw in (False, True) for a in ARMS]
    print("E257b absolute games=%d opps=%d seeds=%d pin=1.32.7" % (len(tasks), len(OPPS), len(SEEDS)), flush=True)
    rows, t0 = [], time.time()
    with ProcessPoolExecutor(max_workers=12, max_tasks_per_child=1) as ex:
        for i, r in enumerate(ex.map(run_abs, tasks), 1):
            rows.append(r)
            if i % 16 == 0:
                print("  %d/%d %.0fs" % (i, len(tasks), time.time() - t0), flush=True)
    with open(os.path.join(OUT, "e257b_absolute.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["arm", "opp", "seed", "swap", "bank", "opp_bank",
                                           "vs_margin", "status"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    ok = [r for r in rows if r["status"] == "OK"]
    print("OK rows %d/%d" % (len(ok), len(rows)))
    by_row = defaultdict(dict)
    for r in ok:
        by_row[(r["opp"], r["seed"], r["swap"])][r["arm"]] = r
    deltas, per_lineage = [], defaultdict(list)
    for key, arms in by_row.items():
        if "CAND" in arms and "PARENT" in arms:
            d = arms["CAND"]["bank"] - arms["PARENT"]["bank"]
            deltas.append((key[0], key[1], d))
            per_lineage[key[0]].append(d)
    lines = []
    print("\n### paired CAND-PARENT absolute bank per lineage (per seat-row)")
    for opp, v in sorted(per_lineage.items()):
        print("%-42s n=%2d mean %+8.1f median %+8.1f worst %+9.1f pos %d/%d"
              % (opp, len(v), statistics.mean(v), statistics.median(v), min(v),
                 sum(x > 0 for x in v), len(v)))
        lines.append({"opp": opp, "n": len(v), "mean": statistics.mean(v), "worst": min(v)})
    allv = [d for _, _, d in deltas]
    worst_lineage_mean = min((l["mean"] for l in lines)) if lines else 0.0
    verdict = ("PASS" if worst_lineage_mean > -1000 and all(l["mean"] > -1000 for l in lines)
               and min(allv) >= -2500 else "FAIL")
    print("\nPOOLED n=%d mean %+.1f median %+.1f worst %+.1f best %+.1f  win %d/%d"
          % (len(allv), statistics.mean(allv), statistics.median(allv), min(allv), max(allv),
             sum(x > 0 for x in allv), len(allv)))
    print("PRE-REGISTERED RULE (E224: per-lineage mean > -1,000 and worst >= -2,500): %s" % verdict)
    json.dump({"rows": len(rows), "paired": deltas, "lineages": lines,
               "pooled_mean": statistics.mean(allv), "verdict": verdict},
              open(os.path.join(OUT, "e257b_summary.json"), "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
