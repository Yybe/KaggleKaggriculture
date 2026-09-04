"""v29 gate bench: candidates vs v28b incumbent (and v3 verbatim) on gate8 + fresh18.

Run with the 1.32.6 venv: WybeV2/rank_env/Scripts/python.exe tools/bench_v29.py [tag]
Writes results/bench_v29_<tag>.jsonl + prints per-candidate summary (W/L/T, mean,
seed-level record, tie rate). Both seats per seed. Control: v29_v28rule must tie
v28b 100% (byte-identical behavior sanity).
"""
import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

GATE_SEEDS = [1000000, 9000000, 3330000, 7770000, 5000000, 6000000, 8000000, 2000000]
FRESH_SEEDS = [314159, 2718281, 1414213, 1732050, 2236067, 2645751, 3162277, 3245553,
               3316624, 3464101, 3588989, 3660254, 2426406, 2469507, 2549509,
               2641391, 2745995, 2871778]

CANDIDATES = [
    ("v30_drip_20_3", "agents/v30_drip.py"),
]

BASELINE = ("v28b", "agents/v28_herdswap.py")


def play(args):
    cand_file, base_file, seed, swap = args
    import importlib
    import importlib.util
    import sys as _sys

    def load(path, name):
        spec = importlib.util.spec_from_file_location(name, str(BASE / path))
        m = importlib.util.module_from_spec(spec)
        _sys.modules[spec.name] = m
        spec.loader.exec_module(m)
        return m.agent

    cand_fn = load(cand_file, f"_c_{abs(hash((cand_file, seed, swap)))%10**8}")
    base_fn = load(base_file, f"_b_{abs(hash((base_file, seed, swap)))%10**8}")
    fn0 = base_fn if swap else cand_fn
    fn1 = cand_fn if swap else base_fn
    try:
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        r0 = float(env.state[0].get("reward", 0) or 0)
        r1 = float(env.state[1].get("reward", 0) or 0)
        sc = r1 if swap else r0
        so = r0 if swap else r1
        return (seed, swap, sc, so, sc - so, None)
    except Exception:
        import traceback
        return (seed, swap, 0, 0, 0, traceback.format_exc()[:400])


def run_set(pool, cand_label, cand_file, base_file, seeds, tag, out):
    tasks = [(cand_file, base_file, s, sw) for s in seeds for sw in (False, True)]
    rows = []
    for r in as_completed_tasks(pool, tasks):
        rows.append(r)
    rows.sort(key=lambda x: (x[0], x[1]))
    w = sum(1 for r in rows if r[4] > 0)
    l = sum(1 for r in rows if r[4] < 0)
    t = sum(1 for r in rows if r[4] == 0)
    mean = sum(r[4] for r in rows) / len(rows)
    # seed-level (sum both seats per seed)
    by_seed = {}
    for seed, _swap, _sc, _so, d, err in rows:
        by_seed[seed] = by_seed.get(seed, 0.0) + d
    sw = sum(1 for v in by_seed.values() if v > 0)
    sl = sum(1 for v in by_seed.values() if v < 0)
    st = sum(1 for v in by_seed.values() if v == 0)
    print(f"{cand_label:<22} {tag:<7} seat W{w}/L{l}/T{t} mean {mean:+8.0f} | seed W{sw}/L{sl}/T{st} | ties {t}/{len(rows)}", flush=True)
    for seed, _swap, sc, so, d, err in rows:
        out.write(json.dumps({"cand": cand_label, "tag": tag, "seed": seed,
                              "our": sc, "opp": so, "delta": d, "err": err}) + "\n")
    out.flush()
    return rows


def as_completed_tasks(pool, tasks):
    futs = [pool.submit(play, t) for t in tasks]
    for f in as_completed(futs):
        yield f.result()


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "gate8"
    seeds = GATE_SEEDS if tag == "gate8" else FRESH_SEEDS
    base_file = BASELINE[1]
    out = open(f"results/bench_v29_{tag}.jsonl", "w", encoding="utf-8")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=8) as pool:
        for label, cfile in CANDIDATES:
            run_set(pool, label, cfile, base_file, seeds, tag, out)
    out.close()
    print(f"done in {time.time()-t0:.0f}s -> results/bench_v29_{tag}.jsonl")


if __name__ == "__main__":
    main()
