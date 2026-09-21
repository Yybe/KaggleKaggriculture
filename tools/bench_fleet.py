"""Mid-ladder fleet screen: one candidate vs every local opponent lineage on a bank.

Usage: WybeV2/rank_env/Scripts/python.exe tools/bench_fleet.py CAND [r1|r2|fresh|all] [NAME ...]
Resumable: lines are appended to results/fleet_<candstem>_<bank>.txt and existing lines are skipped.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_candidate_breakthrough import SEEDS_R1, SEEDS_R2, SEEDS_FRESH, eval_h2h

BANKS = {"r1": SEEDS_R1, "r2": SEEDS_R2, "fresh": SEEDS_FRESH}

# ladder coverage: our own champion line + the 2700-band public/friend spines + mid-ladder pubs
FLEET = [
    "agents/pub_apex_v5.py",        # current deployed champion
    "agents/pub_apex_v1.py",        # V1 lineage
    "agents/friend_r78ub.py",       # friend twin, 2722 live band
    "agents/crop_roi30_h20.py",     # 2700-band h20 spine
    "agents/pub_farmer_john_v56.py",
    "agents/pub_v54_productive.py",
    "agents/pub_one_more_wheat.py",
    "agents/pub_metav4_early.py",
    "agents/pub_e94_omw_clean.py",
    "agents/pub_e99_pasture_fix.py",
    "agents/pub_2945farm.py",       # ~2400-2600 mid ladder
    "agents/pub_e67_yamakawa.py",
]


def main():
    cand = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "r1"
    only = set(sys.argv[3:])
    stem = os.path.basename(cand).replace(".py", "")
    banks = ["r1", "r2", "fresh"] if which == "all" else [which]
    for bank in banks:
        out_path = f"results/fleet_{stem}_{bank}.txt"
        done = set()
        if os.path.exists(out_path):
            done = {ln.split()[1] for ln in open(out_path) if ln.startswith("FLEET")}
        with open(out_path, "a") as f:
            for opp in FLEET:
                if not os.path.exists(opp):
                    print("missing", opp, flush=True)
                    continue
                name = os.path.basename(opp)
                if only and name not in only:
                    continue
                if name in done:
                    print("skip", name, flush=True)
                    continue
                w, l, t, m, deltas = eval_h2h(cand, opp, BANKS[bank])
                line = (f"FLEET {name:<28} {bank:<6} {w:>2}W/{l}L/{t}T mean {m:+9.1f}  "
                        + ", ".join(f"{d:+.0f}" for d in sorted(deltas)))
                print(line, flush=True)
                f.write(line + "\n")
                f.flush()


if __name__ == "__main__":
    main()
