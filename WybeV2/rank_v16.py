"""Local port of raykkretzschmar/kaggriculture-rank-your-agent — rank V16 vs the reference ladder.

Runs on the isolated venv pinned to kaggle-environments==1.32.3 (the version the
reference dataset was measured on). Challenger = root submission.py (V16a).

Pipeline (mirrors the kernel's cells):
  1. engine behavioural check: replay head_to_head_games.csv row 0, banks must match.
  2. smoke test: challenger survives 120 steps vs fallow_finn.
  3. fresh duels: challenger vs every reference rung, SEEDS [9001,9002,9003] x both seats.
  4. reference-vs-reference pairings: reused from baseline_league.csv IF the engine
     check passed, otherwise recomputed fresh on this engine.
  5. Bradley-Terry fit + rank table (prior=0.5, 1500 + 400*log10).
"""
import importlib.util
import itertools
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATASET = HERE / "rank_dataset"
CHALLENGER_PATH = HERE.parent / "submission.py"
CHALLENGER_NAME = "V16a"
SEEDS = [9001, 9002, 9003]
STEPS = 720


def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(f"kagri_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "agent"):
        raise AttributeError(f"{path} defines no `agent` function")
    return module.agent


def _play_one(args):
    a_path, b_path, seed, swap = args
    from kaggle_environments import make

    a = load_agent(a_path, "wa")
    b = load_agent(b_path, "wb")
    pair = [b, a] if swap else [a, b]
    env = make("kaggriculture",
               configuration={"episodeSteps": STEPS, "seed": seed}, debug=False)
    env.run(pair)
    final = env.steps[-1]
    rewards = [s.reward for s in final]
    statuses = [s.status for s in final]
    if swap:
        rewards = rewards[::-1]
        statuses = statuses[::-1]
    return seed, rewards, statuses


def duel(a_path, b_path, seeds=SEEDS, workers=14):
    """Return dict from a_path's perspective: wins_a, wins_b, ties, errors, games, mean_margin_a."""
    tasks = [(a_path, b_path, seed, swap) for seed in seeds for swap in (0, 1)]
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(_play_one, tasks):
            results.append(r)
    wins_a = wins_b = ties = errors = 0
    margins = []
    for seed, rewards, statuses in results:
        mine, theirs = rewards
        if mine is None or theirs is None or any(s in {"ERROR", "INVALID"} for s in statuses):
            errors += 1
            continue
        margins.append(mine - theirs)
        if mine > theirs:
            wins_a += 1
        elif mine < theirs:
            wins_b += 1
        else:
            ties += 1
    return {
        "wins_a": wins_a, "wins_b": wins_b, "ties": ties, "errors": errors,
        "games": wins_a + wins_b + ties,
        "mean_margin_a": round(sum(margins) / len(margins), 1) if margins else 0.0,
    }


def verify_engine_behaviour():
    """Replay one recorded pairing; return (ok, detail)."""
    games = pd.read_csv(DATASET / "head_to_head_games.csv")
    row = games.iloc[0]
    a = load_agent(DATASET / f"{row.agent_a}.py", "va")
    b = load_agent(DATASET / f"{row.agent_b}.py", "vb")
    seat = int(row.seat_of_a)
    pair = [a, b] if seat == 0 else [b, a]
    from kaggle_environments import make
    env = make("kaggriculture",
               configuration={"episodeSteps": 720, "seed": int(row.seed)}, debug=False)
    env.run(pair)
    rewards = [step.reward for step in env.steps[-1]]
    got_a, got_b = round(rewards[seat]), round(rewards[1 - seat])
    ok = (got_a == int(row.bank_a)) and (got_b == int(row.bank_b))
    detail = (f"{row.agent_a} vs {row.agent_b}, seed {row.seed}, seat {seat}: "
              f"expected {int(row.bank_a):,}/{int(row.bank_b):,}, got {got_a:,}/{got_b:,}")
    return ok, detail


def bradley_terry(rows, iterations=10_000, tol=1e-10, prior=0.5):
    pairs = {}
    for r in rows:
        key = (r["agent_a"], r["agent_b"])
        wa, wb = pairs.get(key, (0.0, 0.0))
        pairs[key] = (wa + r["wins_a"] + 0.5 * r["ties"],
                      wb + r["wins_b"] + 0.5 * r["ties"])
    names = sorted({n for pair in pairs for n in pair})
    strength = {n: 1.0 for n in names}
    wins = {n: 0.0 for n in names}
    games = {n: [] for n in names}
    for (a, b), (wa, wb) in pairs.items():
        wins[a] += wa
        wins[b] += wb
        games[a].append((b, wa + wb))
        games[b].append((a, wa + wb))
    for _ in range(iterations):
        delta = 0.0
        for n in names:
            numerator = wins[n] + prior
            denominator = prior / (prior + 1.0) * 2.0
            for other, total in games[n]:
                denominator += total / (strength[n] + strength[other])
            if denominator <= 0:
                continue
            updated = numerator / denominator
            delta = max(delta, abs(updated - strength[n]) / max(updated, 1e-12))
            strength[n] = updated
        geo = math.exp(sum(math.log(max(s, 1e-12)) for s in strength.values()) / len(strength))
        for n in names:
            strength[n] /= geo
        if delta < tol:
            break
    return {n: 1500 + 400 * math.log10(max(s, 1e-12)) for n, s in strength.items()}


def main():
    t0 = time.perf_counter()
    manifest = pd.read_csv(DATASET / "agents_manifest.csv")
    print(f"engine check on {DATASET}:")
    ok, detail = verify_engine_behaviour()
    print(("  PASS  " if ok else "  FAIL  ") + detail)

    rows = []
    # Fresh: challenger vs every rung.
    for _, r in manifest.sort_values("tier").iterrows():
        slug = r.agent_slug
        row = duel(CHALLENGER_PATH, DATASET / r.file)
        row["agent_a"] = CHALLENGER_NAME
        row["agent_b"] = slug
        rows.append(row)
        print(f"  {CHALLENGER_NAME} {row['wins_a']}-{row['wins_b']} {slug}"
              f"  (tier {r.tier}, margin {row['mean_margin_a']:+,.0f})")

    # Reference-vs-reference: reuse dataset precomputation only if engine verified.
    if ok:
        baseline = pd.read_csv(DATASET / "baseline_league.csv")
        rows += baseline.to_dict("records")
        print(f"  reused {len(baseline)} precomputed reference pairings (engine PASS)")
    else:
        print("  engine check FAILED -> recomputing full reference round-robin...")
        for a, b in itertools.combinations(manifest.agent_slug, 2):
            row = duel(DATASET / f"{a}.py", DATASET / f"{b}.py")
            row["agent_a"] = a
            row["agent_b"] = b
            rows.append(row)
            print(f"  {a} {row['wins_a']}-{row['wins_b']} {b}")

    results = pd.DataFrame(rows)
    print(f"\n{len(results)} pairings in {time.perf_counter() - t0:.0f}s   errors: {int(results.errors.sum())}")

    # Rank table.
    ratings = bradley_terry(rows)
    stats = {n: {"wins": 0, "losses": 0, "ties": 0, "margins": []} for n in ratings}
    for r in rows:
        a, b = r["agent_a"], r["agent_b"]
        stats[a]["wins"] += r["wins_a"]; stats[a]["losses"] += r["wins_b"]
        stats[b]["wins"] += r["wins_b"]; stats[b]["losses"] += r["wins_a"]
        stats[a]["ties"] += r["ties"];   stats[b]["ties"] += r["ties"]
        stats[a]["margins"].append(r["mean_margin_a"])
        stats[b]["margins"].append(-r["mean_margin_a"])
    tier_of = dict(zip(manifest.agent_slug, manifest.tier))
    name_of = dict(zip(manifest.agent_slug, manifest.agent_name))
    name_of[CHALLENGER_NAME] = "V16a (ours)"
    out = []
    for n, s in stats.items():
        played = s["wins"] + s["losses"] + s["ties"]
        out.append({
            "agent": name_of.get(n, n), "slug": n, "tier": tier_of.get(n, "you"),
            "bt_rating": round(ratings[n]),
            "record": f"{s['wins']}-{s['losses']}-{s['ties']}",
            "win_pct": round(100 * s["wins"] / played, 1) if played else 0.0,
            "mean_margin": round(sum(s["margins"]) / len(s["margins"])) if s["margins"] else 0,
        })
    table = pd.DataFrame(out).sort_values("bt_rating", ascending=False).reset_index(drop=True)

    print("\n" + table.to_string(index=False))
    table.to_csv(HERE / "rank_v16_result.csv", index=False)
    with open(HERE / "rank_v16_evidence.txt", "w", encoding="utf-8") as f:
        f.write(f"V16a ranking vs reference ladder (engine {__import__('importlib.metadata', fromlist=['version']).version('kaggle-environments')})\n")
        f.write(f"duels: {CHALLENGER_NAME} vs 10 rungs x {len(SEEDS)} seeds x 2 seats | engine check: {'PASS' if ok else 'FAIL'} ({detail})\n\n")
        f.write(table.to_string(index=False))
        f.write("\n\nper-duel rows:\n")
        f.write(results.to_string(index=False))
    print(f"\nevidence: {HERE / 'rank_v16_evidence.txt'}")


if __name__ == "__main__":
    main()