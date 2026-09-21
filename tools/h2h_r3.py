"""R3 holdout: seeds that were NOT used to tune the preemption floors (30016000+).

Guards against the R2 sweep having overfit the 90/30/140 floors.
Usage: WybeV2/rank_env/Scripts/python.exe tools/h2h_r3.py CAND OBS
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_candidate_breakthrough import eval_h2h

SEEDS_R3 = list(range(30016000, 30032000, 1000))          # 16 fresh seeds, never gated on
SEEDS_R4 = list(range(30032000, 30048000, 1000))          # 16 more, disjoint from every sweep
SEEDS_DEFECT = [1898931754]                                # E99 weed-pasture defect seed


def main():
    cand, obs = sys.argv[1], sys.argv[2]
    which = sys.argv[3] if len(sys.argv) > 3 else "r3"
    seeds = {"r3": SEEDS_R3, "r4": SEEDS_R4}.get(which, SEEDS_DEFECT)
    w, l, t, m, deltas = eval_h2h(cand, obs, seeds)
    print(f"{os.path.basename(cand)} vs {os.path.basename(obs)} [{which}] n={len(deltas)*2} "
          f"{w}W/{l}L/{t}T mean {m:+9.1f}")
    print("  per-seed: " + ", ".join(f"{d:+.0f}" for d in sorted(deltas)))


if __name__ == "__main__":
    main()
