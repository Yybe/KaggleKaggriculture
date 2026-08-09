"""Instrument: does _idle_fill ever fire on the V14 route? Count conversions per game.
Usage: python diag_idlefill_count.py <n_seeds>
"""
import os
import sys
import importlib.util
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath("agents"))
sys.path.insert(0, os.path.abspath("Kaggriculture"))


def _count_one(seed):
    from kaggle_environments import make

    # Patch: wrap _idle_fill to count how many actions it changes
    spec = importlib.util.spec_from_file_location("mod_v15", os.path.abspath("agents/kaggle_champion_v15.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    counters = {"converted": 0, "calls": 0, "passes_seen": 0}

    orig = mod._idle_fill

    def wrapped(obs, action, step):
        counters["calls"] += 1
        before = [list(a) for a in (action.get("hands") or [])]
        bf = list(action.get("farmer") or ["PASS"])
        out = orig(obs, action, step)
        if out["farmer"] != bf:
            counters["converted"] += 1
        return out

    mod._idle_fill = wrapped
    v14_spec = importlib.util.spec_from_file_location("mod_v14", os.path.abspath("agents/kaggle_boat84_v14.py"))
    v14 = importlib.util.module_from_spec(v14_spec)
    v14_spec.loader.exec_module(v14)

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod.agent, v14.agent])
    r0 = float(env.steps[-1][0].reward)
    r1 = float(env.steps[-1][1].reward)
    return seed, r0, r1, counters["converted"], counters["calls"]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    seeds = [2000 + s * 73 for s in range(n)]
    results = []
    with ProcessPoolExecutor(max_workers=14) as ex:
        for r in ex.map(_count_one, seeds):
            results.append(r)
    total_fire = sum(r[3] for r in results)
    total_calls = sum(r[4] for r in results)
    print(f"Seeds: {n} | idle_fill calls: {total_calls} | farmer-conversions: {total_fire}")
    for seed, r0, r1, conv, calls in results:
        print(f"  seed={seed:6d} v15={int(r0):7d} v14={int(r1):7d} d={int(r0-r1):+6d} conv={conv}")


if __name__ == "__main__":
    main()