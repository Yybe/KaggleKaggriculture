"""Sweep the E101t preemption variants against the E99 spine (no preemption) on a seed bank.

Usage: WybeV2/rank_env/Scripts/python.exe tools/sweep_e101t.py [r1|r2|fresh] [TAG ...]
Resumable: skips tags already present in the output log.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_candidate_breakthrough import SEEDS_R1, SEEDS_R2, SEEDS_FRESH, eval_h2h
from build_e101t_variants import VARIANTS

BANKS = {"r1": SEEDS_R1, "r2": SEEDS_R2, "fresh": SEEDS_FRESH}
OPP = "agents/pub_e99_pasture_fix.py"


def main():
    bank = sys.argv[1] if len(sys.argv) > 1 else "r2"
    tags = sys.argv[2:] or list(VARIANTS)
    out_path = f"results/e101t_{bank}.txt"
    done = set()
    if os.path.exists(out_path):
        done = {ln.split()[0] for ln in open(out_path) if ln.startswith("pub_e101t_")}
    with open(out_path, "a") as f:
        for tag in tags:
            cand = f"agents/pub_e101t_{tag}.py"
            if not os.path.exists(cand):
                continue
            if os.path.basename(cand) in done:
                print("skip", tag, flush=True)
                continue
            w, l, t, m, deltas = eval_h2h(cand, OPP, BANKS[bank])
            line = (f"{os.path.basename(cand):<22} {bank:<6} {w}W/{l}L/{t}T mean {m:+9.1f}  "
                    + ", ".join(f"{d:+.0f}" for d in sorted(deltas)))
            print(line, flush=True)
            f.write(line + "\n")
            f.flush()


if __name__ == "__main__":
    main()
