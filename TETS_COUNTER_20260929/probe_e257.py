"""E257 probe - prove the fert-throughput layer actually converts hands in real games.

Runs candidate vs the parent spine for 2 seeds, one seat each, and asserts non-zero fire counters
(steps, converted, collect, feed, fert) plus errors == 0.  This is the Rule-1 phase-5 liveness proof
that must precede any gate; the godview_v2 graft passed its own 'fires' report while being inert
because it counted opportunities, not mutations.
"""
import importlib.util
import os
import sys

import kaggle_environments

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
CAND = os.path.join(ROOT, "agents", "tetsutani_e257_fertflow.py")
PARENT = os.path.join(ROOT, "kernels_pull_20260929", "tetsutani_step1009_fortyfirst_closure.py")
SEEDS = [15243003, 15243004, 15243005]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    print("engine", kaggle_environments.__version__)
    assert kaggle_environments.__version__ == "1.32.7", kaggle_environments.__version__
    for seed in SEEDS:
        cand = load(CAND, "cand_%d" % seed)
        parent = load(PARENT, "par_%d" % seed)
        for k in cand.agent.telemetry:
            cand.agent.telemetry[k] = 0
        env = kaggle_environments.make("kaggriculture", configuration={
            "townCenterSellInterval": 24, "episodeSteps": 720, "seed": seed})
        env.run([cand.agent, parent.agent])
        rw = [float(env.steps[-1][i].reward) for i in range(2)]
        tel_keys = sorted(cand.agent.telemetry)
        assert "converted" in tel_keys, tel_keys
        t = dict(cand.agent.telemetry)
        print("seed %d rewards %s tel %s" % (seed, rw, t), flush=True)
        assert t["steps"] >= 700, t
        assert t["errors"] == 0, t
        assert t["converted"] > 0, ("LAYER INERT", t)
    print("PROBE PASS: layer converts idle hands in live games")
    return 0


if __name__ == "__main__":
    sys.exit(main())
