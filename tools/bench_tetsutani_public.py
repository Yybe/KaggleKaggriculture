"""Public-code verification: our v32 vs tetsutani's ACTUAL public agent
(native agent.so bundle) inside Linux docker.

Runs inside: python:3.11-slim + kaggle-environments==1.32.6.
Usage: python tools/bench_tetsutani_public.py [n_seeds]
"""
import importlib
import importlib.util
import json
import pathlib
import sys

BASE = pathlib.Path("/work")
sys.path.insert(0, str(BASE))

SEEDS = [1000000, 9000000, 3330000, 7770000, 5000000, 6000000]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    from kaggle_environments import make

    tetsu = load(BASE / "tetsutani_main.py", "tetsutani_public")
    ours = load(BASE / "v32_submission.py", "v32_ours")

    rows = []
    for seed in SEEDS[:n]:
        for swap in (False, True):
            fn0, fn1 = (tetsu.agent, ours.agent) if swap else (ours.agent, tetsu.agent)
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
            env.run([fn0, fn1])
            r0 = float(env.state[0].get("reward", 0) or 0)
            r1 = float(env.state[1].get("reward", 0) or 0)
            our, opp = (r1, r0) if swap else (r0, r1)
            rows.append({"seed": seed, "swap": swap, "our": our, "opp": opp, "delta": our - opp})
            print(f"seed {seed} swap{int(swap)}: our {our:.0f} vs tetsutani {opp:.0f} delta {our-opp:+.0f}", flush=True)
    w = sum(1 for r in rows if r["delta"] > 0)
    l = sum(1 for r in rows if r["delta"] < 0)
    t = sum(1 for r in rows if r["delta"] == 0)
    mean = sum(r["delta"] for r in rows) / len(rows)
    print(f"\nTOTAL v32 vs tetsutani public bundle: W{w}/L{l}/T{t} mean {mean:+.0f}")
    json.dump(rows, open("/work/out_tetsutani_bench.json", "w"))


if __name__ == "__main__":
    main()
