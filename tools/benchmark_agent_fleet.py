"""Reusable fleet benchmark: test ANY candidate agent vs the 8 distinct
behavior groups + the current champion (V18 APEXX).

Unlike the one-off rebenchmark, this is the STANDARD harness for testing a new
agent: it always fights the fixed, canonical opponent set from
agents/fleet_registry.py (8 distinct groups + champion) on the canonical
FRESH_SEEDS set, with both seat orders to control for seat bias.

Usage:
    python tools/benchmark_agent_fleet.py --candidate agents.my_new_agent
    python tools/benchmark_agent_fleet.py --candidate agents.kaggle_v18_apexx \
        --label v18_apexx            # benchmark the champion vs the 8 distinct
    python tools/benchmark_agent_fleet.py --candidate agents.kaggle_v14_tweaked \
        --seeds 4 --label v14_fast   # quick smoke on first N seeds

CANDIDATE RESOLUTION (in priority order):
  1. If the module exposes <label>_cls / a class named after `--fresh-cls`
     (default: look for the module-level CAPS'FreshCls' or 'V18ApexAgent'),
     we instantiate a FRESH instance per match (stateful agents).
  2. Otherwise we use the module's `agent` callable directly.

Outputs:
    results/benchmark_<label>.jsonl   (raw per-match lines)
    results/benchmark_<label>.json    (aggregated summary)
    console table
"""
import os, sys, json, time, importlib, argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
sys.path.insert(0, BASE)

from agents import fleet_registry as reg


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Benchmark a candidate agent vs the canonical fleet.")
    p.add_argument("--candidate", required=True,
                   help="Dotted module path of the candidate (e.g. agents.my_new_agent)")
    p.add_argument("--label", default=None,
                   help="Short label for output files (default: last component of candidate)")
    p.add_argument("--seeds", type=int, default=len(reg.FRESH_SEEDS),
                   help="Number of FRESH_SEEDS to use (default: all)")
    p.add_argument("--fresh-cls", default=None,
                   help="Class name in candidate module to instantiate per match (stateful). "
                        "Defaults to auto-detect: V18ApexAgent or <Label>Cls.")
    p.add_argument("--opponents", default="all",
                   help="all | distinct | list of canonical labels (comma-separated)")
    p.add_argument("--workers", type=int, default=14)
    p.add_argument("--include-champion", action="store_true",
                   help="Also include the current champion as an opponent even when "
                        "candidate IS the champion (self-play sanity).")
    return p.parse_args(argv)


def _resolve_candidate(cand_module, label, fresh_cls_name):
    """Build a plain picklable spec dict for the candidate.

    The actual import is done at worker time inside play_match via
    reg.load_callable, so the dict only ever carries strings (spawn-safe)."""

    # Auto-detect a stateful class if none given.
    if fresh_cls_name is None:
        for cand in (label, "V18ApexAgent"):
            try:
                mod = importlib.import_module(cand_module)
                if hasattr(mod, cand):
                    cls = getattr(mod, cand)
                    if isinstance(cls, type):
                        fresh_cls_name = cand
                        break
            except Exception:
                pass

    return {
        "label": label,
        "module": cand_module,
        "attr": "agent",
        "fresh_cls": fresh_cls_name,
    }


def _build_opponents(opponents_arg, include_champion, candidate_label):
    fleet = dict(reg.DISTINCT_FLEET)
    if include_champion or candidate_label != reg.CHAMPION_SPEC["label"]:
        fleet[reg.CHAMPION_SPEC["label"]] = dict(reg.CHAMPION_SPEC)
    if opponents_arg == "distinct":
        fleet = dict(reg.DISTINCT_FLEET)
    elif opponents_arg not in ("all", "distinct"):
        keep = [k.strip() for k in opponents_arg.split(",") if k.strip()]
        fleet = {k: v for k, v in fleet.items() if k in keep}
    return fleet


def play_match(task):
    """task = (cand_spec, opp_label, opp_spec, seed, swap)."""
    from kaggle_environments import make
    cand_spec, opp_label, opp_spec, seed, swap = task
    cand_fn = reg.load_callable(cand_spec, fresh_instance=True)
    opp_fn = reg.load_callable(opp_spec, fresh_instance=True)
    fn0 = opp_fn if swap else cand_fn
    fn1 = cand_fn if swap else opp_fn
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        st = env.state
        r0 = float(st[0].get("reward", 0) or 0)
        r1 = float(st[1].get("reward", 0) or 0)
        score_cand = r1 if swap else r0
        score_opp = r0 if swap else r1
        return opp_label, seed, swap, score_cand, score_opp, None
    except Exception as e:
        return opp_label, seed, swap, 0.0, 0.0, str(e)[:120]


def main():
    args = parse_args()
    label = args.label or args.candidate.rsplit(".", 1)[-1]
    seeds = reg.FRESH_SEEDS[: args.seeds]
    opponents = _build_opponents(args.opponents, args.include_champion, label)
    cand_spec = _resolve_candidate(args.candidate, label, args.fresh_cls)

    os.makedirs("results", exist_ok=True)
    jsonl_path = f"results/benchmark_{label}.jsonl"
    summary_path = f"results/benchmark_{label}.json"

    all_tasks = []
    for opp_label, opp_spec in opponents.items():
        for s in seeds:
            all_tasks.append((cand_spec, opp_label, opp_spec, s, False))
            all_tasks.append((cand_spec, opp_label, opp_spec, s, True))

    print(f"FLEET BENCHMARK: candidate={args.candidate!r} label={label}")
    print(f"  opponents: {len(opponents)} ({', '.join(opponents)})")
    print(f"  seeds: {len(seeds)} ({label} on {len(all_tasks)} matches, 2 seats x {len(seeds)} seeds)")
    t0 = time.time()

    jsonl_out = open(jsonl_path, "w", encoding="utf-8")
    completed = 0
    results_by_opp = {}

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        fut_map = {ex.submit(play_match, t): t for t in all_tasks}
        for fut in as_completed(fut_map):
            opp_label, seed, swap, sc, so, err = fut.result()
            completed += 1
            if err:
                print(f"  [{completed}/{len(all_tasks)}] ERR {opp_label} seed {seed} swap {swap}: {err}", flush=True)
                continue
            delta = sc - so
            rec = {"opp": opp_label, "seed": seed, "swap": swap,
                   "score_cand": sc, "score_opp": so, "delta": delta,
                   "outcome": "WIN" if delta > 0 else ("LOSS" if delta < 0 else "TIE")}
            jsonl_out.write(json.dumps(rec) + "\n")
            jsonl_out.flush()
            results_by_opp.setdefault(opp_label, []).append(delta)
            if completed % 24 == 0 or completed == len(all_tasks):
                print(f"  progress {completed}/{len(all_tasks)} in {time.time()-t0:.1f}s", flush=True)

    jsonl_out.close()

    summary = {}
    print("\n" + "=" * 95)
    print(f"{'Opponent':<16} | {'Games':>5} | {'Record':>10} | {'Win%':>6} | {'Mean Delta':>12} | {'Min':>10} | {'Max':>10}")
    print("-" * 95)
    for opp_label, deltas in sorted(results_by_opp.items()):
        wins = sum(1 for d in deltas if d > 0)
        losses = sum(1 for d in deltas if d < 0)
        ties = sum(1 for d in deltas if d == 0)
        n = len(deltas)
        wr = (wins / n) * 100 if n else 0
        md = sum(deltas) / n if n else 0
        mind = min(deltas) if deltas else 0
        maxd = max(deltas) if deltas else 0
        print(f"{opp_label:<16} | {n:5d} | {wins:2d}W/{losses:2d}L/{ties:1d}T | {wr:5.1f}% | {md:+12.1f} | {mind:+10.0f} | {maxd:+10.0f}")
        summary[opp_label] = {"games": n, "wins": wins, "losses": losses, "ties": ties,
                              "win_rate": wr, "mean_delta": md, "min_delta": mind, "max_delta": maxd}
    print("=" * 95)

    meta = {
        "candidate": args.candidate,
        "label": label,
        "seeds": seeds,
        "seed_pool": "FRESH_SEEDS (disjoint from original 8 gate)",
        "opponents_arg": args.opponents,
        "summary": summary,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"\nSaved: {jsonl_path}  {summary_path}  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
