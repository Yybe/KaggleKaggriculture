"""Generic head-to-head runner on the Apex gate harness (R1 / R2 / Fresh banks).

Usage: python tools/run_h2h.py CAND OBS [r1|r2|fresh|all]
"""
import os, sys, importlib.util, statistics
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_candidate_breakthrough import SEEDS_R1, SEEDS_R2, SEEDS_FRESH, eval_h2h

BANKS = {"r1": SEEDS_R1, "r2": SEEDS_R2, "fresh": SEEDS_FRESH}


def report(cand, obs, which):
    print(f"\n=== {os.path.basename(cand)} vs {os.path.basename(obs)} (seats balanced per seed) ===")
    for name in (BANKS if which == "all" else [which]):
        w, l, t, m, deltas = eval_h2h(cand, obs, BANKS[name])
        print(f"{name:<6} n={len(deltas)*2:<3} {w}W/{l}L/{t}T  mean {m:+9.1f}")
        print(f"       per-seed deltas: {', '.join(f'{d:+.0f}' for d in sorted(deltas))}")


if __name__ == "__main__":
    report(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "all")
