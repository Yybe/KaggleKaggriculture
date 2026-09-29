"""E258/E259 liveness probe + 3-arm paired absolute gate.

Stage 1 (probe): 2 seeds, candidate vs parent, assert mutation counters non-zero and errors == 0.
Stage 2 (H2H R1): per-seed deltas vs the parent - all-ties means inert, all-negative means regression.
Stage 3 (absolute): C258 and C259 each paired against PARENT on identical worlds vs four out-of-fleet
lineages, 4 fresh seeds x both seats. Promotion bar fixed before the run (E224 rule, applied verbatim):
every lineage mean > -1,000/seat AND no row worse than -2,500 AND pooled mean > 0. A mean that is merely
"not catastrophic" is a reject: parity is not progress.
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

ARMS = {
    "C258": os.path.join(REPO, "agents", "tetsutani_e258_fertbuy_veto.py"),
    "C259": os.path.join(REPO, "agents", "tetsutani_e259_idle_replant.py"),
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
PROBE_SEEDS = [15243003, 15243004]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stage_probe():
    import kaggle_environments
    assert kaggle_environments.__version__ == "1.32.7"
    print("engine", kaggle_environments.__version__, flush=True)
    for arm in ("C258", "C259"):
        for seed in PROBE_SEEDS:
            cand = load(ARMS[arm], "%s_%d" % (arm, seed))
            par = load(ARMS["PARENT"], "par_%d" % seed)
            for k in cand.agent.telemetry:
                cand.agent.telemetry[k] = 0
            env = kaggle_environments.make("kaggriculture", configuration={
                "townCenterSellInterval": 24, "episodeSteps": 720, "seed": seed})
            env.run([cand.agent, par.agent])
            rw = [float(env.steps[-1][i].reward) for i in range(2)]
            t = dict(cand.agent.telemetry)
            extra = getattr(cand.agent, "bycrop", {})
            print("%s seed %d rewards %s tel %s bycrop %s" % (arm, seed, rw, t, extra), flush=True)
            key = "orders_dropped" if arm == "C258" else "converted"
            assert t["steps"] >= 700 and t["errors"] == 0, t
            assert t[key] > 0, ("LAYER INERT", arm, t)
    print("PROBE PASS both arms mutate actions", flush=True)


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


def stage_absolute():
    tasks = [(a, o, s, sw) for o in OPPS for s in SEEDS for sw in (False, True) for a in ARMS]
    print("absolute games=%d" % len(tasks), flush=True)
    rows, t0 = [], time.time()
    with ProcessPoolExecutor(max_workers=12, max_tasks_per_child=1) as ex:
        for i, r in enumerate(ex.map(run_abs, tasks), 1):
            rows.append(r)
            if i % 32 == 0:
                print("  %d/%d %.0fs" % (i, len(tasks), time.time() - t0), flush=True)
    with open(os.path.join(OUT, "e2589_absolute.csv"), "w", newline="", encoding="utf-8") as fh:
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
    summary = {}
    for cand in ("C258", "C259"):
        per_lin = defaultdict(list)
        for key, arms in by_row.items():
            if cand in arms and "PARENT" in arms:
                per_lin[key[0]].append(arms[cand]["bank"] - arms["PARENT"]["bank"])
        allv = [d for v in per_lin.values() for d in v]
        means = {opp: statistics.mean(v) for opp, v in per_lin.items()}
        verdict = ("PASS" if means and min(means.values()) > -1000 and min(allv) >= -2500
                   and statistics.mean(allv) > 0 else "REJECT")
        print("\n### %s paired vs PARENT  pooled n=%d mean %+.1f median %+.1f worst %+.1f win %d/%d  %s"
              % (cand, len(allv), statistics.mean(allv), statistics.median(allv), min(allv),
                 sum(x > 0 for x in allv), len(allv), verdict), flush=True)
        for opp, v in sorted(per_lin.items()):
            print("   %-46s n=%d mean %+8.1f worst %+9.1f pos %d"
                  % (opp, len(v), statistics.mean(v), min(v), sum(x > 0 for x in v)), flush=True)
        summary[cand] = {"pooled_mean": statistics.mean(allv), "worst": min(allv),
                         "lineages": means, "verdict": verdict}
    json.dump(summary, open(os.path.join(OUT, "e2589_summary.json"), "w"), indent=1)
    return summary


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "probe"):
        stage_probe()
    if which in ("all", "abs"):
        stage_absolute()
    sys.exit(0)
