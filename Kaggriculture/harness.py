import traceback
"""Fast parallel Kaggriculture game runner.

Uses every CPU core via ProcessPoolExecutor. Each worker runs one game at a
time; N games run concurrently across the pool.

Usage:
    python harness.py --a baseline --b random --n 100 --steps 720
    python harness.py --a baseline --b starter --n 200
    python harness.py --a agents_lib:melon_maxxer --b random --n 50

Agent spec: builtin name ("random"|"starter"|"pass") or "module:function".
"""
import argparse
import importlib
import os
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor

BUILTINS = {"random", "starter", "pass"}
WORKERS = max(1, os.cpu_count() - 2)


def resolve_agent(spec):
    if isinstance(spec, str) and spec in BUILTINS:
        return spec
    mod_name, _, fn = spec.partition(":")
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        return spec  # let the env try to resolve builtin
    return getattr(mod, fn)


def _play_one(args):
    spec_a, spec_b, steps, seed, index = args
    from kaggle_environments import make

    a = resolve_agent(spec_a)
    b = resolve_agent(spec_b)
    try:
        env = make(
            "kaggriculture",
            configuration={"episodeSteps": steps, "seed": seed},
            debug=True,
        )
        env.run([a, b])
        fin = env.steps[-1]
        if fin[0].reward is None:
            print("AGENT ERROR A:", getattr(fin[0], "error", "Unknown"))
        if fin[1].reward is None:
            print("AGENT ERROR B:", getattr(fin[1], "error", "Unknown"))
        return index, float(fin[0].reward), float(fin[1].reward), 0
    except Exception as e:  # never let one game kill the batch
        traceback.print_exc()
        return index, None, None, str(e)[:200]


def run_batch(spec_a, spec_b, n, steps=720, workers=WORKERS, seed_base=42):
    t0 = time.perf_counter()
    args = [(spec_a, spec_b, steps, seed_base + i, i) for i in range(n)]
    results = [None] * n
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for index, ra, rb, err in ex.map(_play_one, args, chunksize=1):
            results[index] = (ra, rb, err)
    dt = time.perf_counter() - t0

    ok = [(ra, rb) for ra, rb, err in results if err == 0 and ra is not None]
    errs = [e for _, _, e in results if e]
    wins_a = sum(1 for ra, rb in ok if ra > rb)
    wins_b = sum(1 for ra, rb in ok if rb > ra)
    ties = len(ok) - wins_a - wins_b
    if ok:
        scores_a = [ra for ra, _ in ok]
        scores_b = [rb for _, rb in ok]
        print(f"Games: {n}  ok={len(ok)}  errors={len(errs)}  wall={dt:.1f}s  "
              f"rate={n / dt:.1f} games/s  ({workers} workers)")
        print(f"  A({spec_a}): win={wins_a} ({wins_a / max(len(ok), 1) * 100:.0f}%)  "
              f"avg_bank={statistics.mean(scores_a):.0f}  med={statistics.median(scores_a):.0f}  "
              f"max={max(scores_a):.0f}")
        print(f"  B({spec_b}): win={wins_b} ({wins_b / max(len(ok), 1) * 100:.0f}%)  "
              f"avg_bank={statistics.mean(scores_b):.0f}  med={statistics.median(scores_b):.0f}  "
              f"max={max(scores_b):.0f}")
        print(f"  ties={ties}")
    else:
        print(f"All {n} games errored (first: {errs[:1]})")
    return results, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="agents_lib:baseline", help="agent spec for player 0")
    ap.add_argument("--b", default="random", help="agent spec for player 1")
    ap.add_argument("--n", type=int, default=64, help="number of games")
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    run_batch(args.a, args.b, args.n, args.steps, args.workers, args.seed)


if __name__ == "__main__":
    main()
