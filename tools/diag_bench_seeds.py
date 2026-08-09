"""Seed-list H2H runner for the frozen rulebook gate family.

Usage:
    python diag_bench_seeds.py <agent_a.py> <agent_b.py> <seed_csv> <out.txt> [--interval N]
    # seed_csv e.g. "1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000"
    # runs each seed on both seats (2 games/seed), writes per-game table + summary.
    # --interval N sets townCenterSellInterval (12 = legacy, 24 = rebalance).
"""
import os
import sys
import time
import statistics
import importlib.util
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath("agents"))
sys.path.insert(0, os.path.abspath("Kaggriculture"))


def _play_single(args):
    agent_a_file, agent_b_file, seed, swap, interval = args
    from kaggle_environments import make

    def _load(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    mod_a = _load(agent_a_file, "mod_eval_a")
    mod_b = _load(agent_b_file, "mod_eval_b")
    p0 = mod_b.agent if swap else mod_a.agent
    p1 = mod_a.agent if swap else mod_b.agent
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed,
                                                   "townCenterSellInterval": interval}, debug=False)
        env.run([p0, p1])
        r0 = float(env.steps[-1][0].reward)
        r1 = float(env.steps[-1][1].reward)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return seed, swap, score_a, score_b, None
    except Exception as e:
        return seed, swap, None, None, str(e)


def run(agent_a_path, agent_b_path, seeds, out_path="diag_seeds_out.txt", interval=12):
    t0 = time.perf_counter()
    tasks = []
    for seed in seeds:
        tasks.append((agent_a_path, agent_b_path, seed, False, interval))
        tasks.append((agent_a_path, agent_b_path, seed, True, interval))

    results = []
    with ProcessPoolExecutor(max_workers=14) as ex:
        for r in ex.map(_play_single, tasks):
            results.append(r)

    dt = time.perf_counter() - t0
    ok = [r for r in results if r[4] is None and r[2] is not None]
    errs = [r for r in results if r[4] is not None]

    # per-seed aggregate (mean of the 2 seats for seed-level win counting)
    by_seed = {}
    for r in ok:
        seed, swap, a, b = r[0], r[1], r[2], r[3]
        by_seed.setdefault(seed, []).append((a, b))
    seed_wins = 0
    seed_losses = 0
    seed_ties = 0
    for seed, pairs in by_seed.items():
        mean_a = statistics.mean([p[0] for p in pairs])
        mean_b = statistics.mean([p[1] for p in pairs])
        if mean_a > mean_b:
            seed_wins += 1
        elif mean_b > mean_a:
            seed_losses += 1
        else:
            seed_ties += 1

    wins_a = sum(1 for r in ok if r[2] > r[3])
    wins_b = sum(1 for r in ok if r[3] > r[2])
    ties = sum(1 for r in ok if r[2] == r[3])
    deltas = [r[2] - r[3] for r in ok]

    name_a = os.path.basename(agent_a_path)
    name_b = os.path.basename(agent_b_path)

    lines = []
    lines.append(f"\n{'='*76}")
    lines.append(f"DIAG BENCH SEED-LIST: {name_a} vs {name_b} (interval={interval})")
    lines.append(f"Seeds: {len(seeds)} x 2 seats = {len(tasks)} games | Ok: {len(ok)} | Errs: {len(errs)} | Time: {dt:.1f}s")
    if ok:
        lines.append(f"  {name_a}: {wins_a} W ({wins_a/len(ok)*100:.1f}%), {wins_b} L, {ties} T | seed-level: {seed_wins}W/{seed_losses}L/{seed_ties}T")
        lines.append(f"  Mean Delta: {statistics.mean(deltas):+.0f} | Median: {statistics.median(deltas):+.0f} "
                     f"| Min: {min(deltas):+.0f} | Max: {max(deltas):+.0f}")
        lines.append(f"  {name_a} Avg: {statistics.mean([r[2] for r in ok]):.0f} | "
                     f"{name_b} Avg: {statistics.mean([r[3] for r in ok]):.0f}")
        lines.append("  -- per-game (seed, swap, a, b, delta) --")
        for seed, swap, a, b, _ in sorted(ok):
            lines.append(f"    seed={seed:7d} swap={int(swap)}  a={int(a):7d}  b={int(b):7d}  d={int(a-b):+6d}")
        losses = sorted([r for r in ok if r[2] < r[3]], key=lambda r: r[2] - r[3])
        if losses:
            lines.append("  -- LOSES (a < b), most-negative first:")
            for seed, swap, a, b, _ in losses:
                lines.append(f"    seed={seed:7d} swap={int(swap)}  a={int(a):7d}  b={int(b):7d}  d={int(a-b):+6d}")
    if errs:
        lines.append("  -- ERRORS --")
        for seed, swap, a, b, e in errs:
            lines.append(f"    seed={seed:7d} swap={int(swap)}  {e}")
    lines.append("=" * 76 + "\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    return seed_wins, seed_losses, seed_ties, deltas


if __name__ == "__main__":
    a = sys.argv[1]
    b = sys.argv[2]
    seeds = [int(x) for x in sys.argv[3].split(",")]
    out = sys.argv[4] if len(sys.argv) > 4 else "diag_seeds_out.txt"
    interval = 12
    if "--interval" in sys.argv:
        interval = int(sys.argv[sys.argv.index("--interval") + 1])
    run(os.path.abspath(a), os.path.abspath(b), seeds, out, interval)
