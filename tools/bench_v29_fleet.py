"""v29 fleet gate: candidate vs live-top 6 reversed-engineered models.

8 gate seeds x 2 seats x 6 opponents = 96 games. Run on 1.32.6 venv.
Writes results/bench_v29_fleet.jsonl + per-opponent summary.
"""
import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

GATE_SEEDS = [1000000, 9000000, 3330000, 7770000, 5000000, 6000000, 8000000, 2000000]

TOP_MODELS = [
    ("lynnsakurai_v4", "agents._top_pub.lynnsakurai_v4"),
    ("boatlee_v29", "agents._top_pub.boatlee_v29"),
    ("boatlee_v21", "agents._top_pub.boatlee_v21"),
    ("salemali7_2900", "agents._top_pub.salemali7_2900"),
    ("tetsutani", "agents._top_pub.tetsutani_adaptive"),
    ("pilkwang", "agents._top_pub.pilkwang_kaitofukami_fork"),
]

CAND = ("v33_shields", "agents/v33_shields.py")


def play(args):
    cand_file, opp_mod, seed, swap = args
    import importlib
    import importlib.util
    import sys as _sys

    def load_cand():
        spec = importlib.util.spec_from_file_location(f"_cf_{seed}_{swap}", str(BASE / cand_file))
        m = importlib.util.module_from_spec(spec)
        _sys.modules[spec.name] = m
        spec.loader.exec_module(m)
        return m.agent

    cand_fn = load_cand()
    opp_fn = getattr(importlib.import_module(opp_mod), "agent")
    fn0 = opp_fn if swap else cand_fn
    fn1 = cand_fn if swap else opp_fn
    try:
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        r0 = float(env.state[0].get("reward", 0) or 0)
        r1 = float(env.state[1].get("reward", 0) or 0)
        sc = r1 if swap else r0
        so = r0 if swap else r1
        return (opp_mod, seed, swap, sc, so, sc - so, None)
    except Exception:
        import traceback
        return (opp_mod, seed, swap, 0, 0, 0, traceback.format_exc()[:400])


def main():
    cand_label, cand_file = CAND
    out = open("results/bench_v29_fleet.jsonl", "w", encoding="utf-8")
    tasks = [(cand_file, om, s, sw) for _l, om in TOP_MODELS for s in GATE_SEEDS for sw in (False, True)]
    agg = {}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(play, t) for t in tasks]
        done = 0
        for f in as_completed(futs):
            opp_mod, seed, swap, sc, so, d, err = f.result()
            done += 1
            out.write(json.dumps({"cand": cand_label, "opp": opp_mod, "seed": seed,
                                  "swap": swap, "our": sc, "opp": so, "delta": d, "err": err}) + "\n")
            a = agg.setdefault(opp_mod, [0, 0, 0, 0.0, 0])
            a[0] += d > 0
            a[1] += d < 0
            a[2] += d == 0
            a[3] += d
            a[4] += 1
            if done % 24 == 0:
                print(f"  {done}/{len(tasks)} games...", flush=True)
    out.close()
    W = sum(a[0] for a in agg.values())
    L = sum(a[1] for a in agg.values())
    T = sum(a[2] for a in agg.values())
    print(f"\n{cand_label} vs live-top6: W{W}/L{L}/T{T} ties {T}/{W+L+T}")
    for k, a in sorted(agg.items()):
        print(f"  {k:<22} W{a[0]} L{a[1]} T{a[2]} mean {a[3]/a[4]:+.0f}")
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
