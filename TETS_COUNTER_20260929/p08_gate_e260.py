"""E260 gate - probe both legs, then the paired absolute estimator (8 seeds, 4 lineages).

Bar fixed in build_e260_collect_dump.py before any number was read: pooled paired mean > 0, no lineage
mean below -1,000/seat, no row worse than -2,500, win share >= 50 %.
"""
import csv
import importlib.util
import json
import os
import statistics
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CAND = os.environ.get("COUNTER_CAND") or os.path.join(REPO, "agents", "tetsutani_e260_collect_dump.py")
TAG = os.environ.get("COUNTER_TAG") or "e260"
PROBE_SEEDS = [int(x) for x in (os.environ.get("COUNTER_PROBE_SEEDS") or "15243015,15243016").split(",")]
PARENT = os.path.join(REPO, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py")
OPPS = [
    "agents/independent_phase_a13_eight_lane_20260924.py",
    "agents/independent_phase_a15_full_wheat_20260924.py",
    "agents/oblate_orderbook_full.py",
    "agents/friend_r78ub.py",
]
SEEDS = [15243000 + 1117 * i for i in range(15, 23)]
OUT = os.path.join(REPO, "TETS_COUNTER_20260929", "out")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def probe():
    import kaggle_environments
    assert kaggle_environments.__version__ == "1.32.7"
    for seed in PROBE_SEEDS:
        cand = load(CAND, "c260_%d" % seed)
        par = load(PARENT, "p260_%d" % seed)
        for k in cand.agent.telemetry:
            cand.agent.telemetry[k] = 0
        env = kaggle_environments.make("kaggriculture", configuration={
            "townCenterSellInterval": 24, "episodeSteps": 720, "seed": seed})
        env.run([cand.agent, par.agent])
        rw = [float(env.steps[-1][i].reward) for i in range(2)]
        t = dict(cand.agent.telemetry)
        print("probe seed %d rewards %s tel %s" % (seed, rw, t), flush=True)
        assert t["steps"] >= 700 and t["errors"] == 0, t
        assert any(v > 0 for k, v in t.items() if k not in ("steps", "errors")), ("LAYER INERT", t)
    print("PROBE PASS both legs mutate", flush=True)


def run_abs(args):
    from agent_loader import load_agent, verify_game_liveness
    from kaggle_environments import make
    import kaggle_environments
    arm, opp, seed, swap = args
    try:
        pa = load_agent(CAND if arm == "CAND" else PARENT)
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
        return dict(status="OK", arm=arm, opp=os.path.basename(opp), seed=seed, swap=swap,
                    bank=r_us, opp_bank=float(env.steps[-1][1].reward), vs_margin=r_us - float(env.steps[-1][1].reward))
    except Exception as exc:
        return dict(status="ERROR:%r" % exc, arm=arm, opp=opp, seed=seed, swap=swap)


def gate():
    tasks = [(a, o, s, sw) for o in OPPS for s in SEEDS for sw in (False, True) for a in ("CAND", "PARENT")]
    print("E260 absolute games=%d seeds=%d opps=%d pin=1.32.7" % (len(tasks), len(SEEDS), len(OPPS)), flush=True)
    rows, t0 = [], time.time()
    with ProcessPoolExecutor(max_workers=12, max_tasks_per_child=1) as ex:
        for i, r in enumerate(ex.map(run_abs, tasks), 1):
            rows.append(r)
            if i % 32 == 0:
                print("  %d/%d %.0fs" % (i, len(tasks), time.time() - t0), flush=True)
    with open(os.path.join(OUT, "%s_absolute.csv" % TAG), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["arm", "opp", "seed", "swap", "bank", "opp_bank",
                                           "vs_margin", "status"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    ok = [r for r in rows if r["status"] == "OK"]
    print("OK %d/%d" % (len(ok), len(rows)))
    by_row = defaultdict(dict)
    for r in ok:
        by_row[(r["opp"], r["seed"], r["swap"])][r["arm"]] = r
    per_lin = defaultdict(list)
    for key, arms in by_row.items():
        if "CAND" in arms and "PARENT" in arms:
            per_lin[key[0]].append(arms["CAND"]["bank"] - arms["PARENT"]["bank"])
    allv = [d for v in per_lin.values() for d in v]
    means = {o: statistics.mean(v) for o, v in per_lin.items()}
    winshare = sum(x > 0 for x in allv) / len(allv)
    verdict = ("PASS" if statistics.mean(allv) > 0 and min(means.values()) > -1000
               and min(allv) >= -2500 and winshare >= 0.5 else "REJECT")
    print("\nC260 paired vs PARENT n=%d mean %+.1f median %+.1f worst %+.1f best %+.1f win %.0f%% -> %s"
          % (len(allv), statistics.mean(allv), statistics.median(allv), min(allv), max(allv),
             100 * winshare, verdict), flush=True)
    for o, v in sorted(per_lin.items()):
        print("   %-46s n=%d mean %+9.1f median %+9.1f worst %+10.1f pos %d/%d"
              % (o, len(v), statistics.mean(v), statistics.median(v), min(v),
                 sum(x > 0 for x in v), len(v)), flush=True)
    json.dump({"pooled_mean": statistics.mean(allv), "median": statistics.median(allv),
               "worst": min(allv), "winshare": winshare, "lineages": means,
               "lineage_rows": {o: v for o, v in per_lin.items()}, "verdict": verdict},
              open(os.path.join(OUT, "%s_summary.json" % TAG), "w"), indent=1, default=str)
    return verdict


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "probe"):
        probe()
    if which in ("all", "gate"):
        gate()
    sys.exit(0)
