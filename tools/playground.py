"""Kaggriculture Playground — local agent battleground with confidence-gated promotion.

Runs head-to-head matchups between extracted Kaggriculture agents on the official
`kaggle_environments` engine, in parallel (~30-90 games per matchup, seat-balanced).
The winner is NEVER decided on a raw win count: a champion only gets promoted when
the margin beats the noise floor (>= MIN_WIN_RATE over >= MIN_GAMES decisive games,
or non-overlapping Wilson 95% CIs).  Development seeds and decision seeds are two
disjoint groups — you never tune on the seeds you later judge on.

FINAL GATE REMINDER: local says "this beats the pool"; the real ladder says "this
beats the actual field".  Use `--export <name>` to produce a ready-to-upload
submission/main.py (sha256 + upload command printed) for the final ladder gate.

Usage:
    python playground.py --a kaggle_v22_romanrozen --b kaggle_v23 --n 32 --phase both
    python playground.py --a kaggle_v22_romanrozen --b kaggle_v23 --n 64 --phase decision
    python playground.py --a kaggle_v23 --b random --n 64 --export kaggle_v23
    python playground.py --vs-pool --a kaggle_v22_romanrozen --b kaggle_v23 --pool random,baseline --n 32
    python playground.py --tournament --agents kaggle_v23,kaggle_v22_romanrozen,baseline --n 16
    python playground.py --list

Retired agents live in archive/ (github_v23 etc.) and are NOT in the registry.

Agent specs: registry name ("kaggle_v23", "kaggle_v22_romanrozen", "baseline",
"baseline_v7", "baseline_v8", "melon_maxxer") / builtin ("random", "starter",
"pass") / custom "path:func".
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import importlib.util
import json
import math
import os
import re
import statistics
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILTIN_OPPONENTS = ("random", "starter", "pass")
RESULTS_DIR = os.path.join(ROOT, "results")

# registry name -> (module file, callable name)
AGENT_REGISTRY = {
    "kaggle_v22_romanrozen": (os.path.join(ROOT, "agents", "kaggle_v22_romanrozen.py"), "agent"),
    "kaggle_v23": (os.path.join(ROOT, "agents", "kaggle_v23.py"), "agent"),
    "kaggle_v26b": (os.path.join(ROOT, "agents", "kaggle_v26b.py"), "agent"),
    # kaggle_v26 retired to archive/ on 2026-08-08 (0-50 decision vs boat84_v14)
    "boat84_v14": (os.path.join(ROOT, "agents", "kaggle_boat84_v14.py"), "agent"),
    "kaggle_flex": (os.path.join(ROOT, "agents", "kaggle_flex.py"), "agent_playground"),
    "kaggle_anas": (os.path.join(ROOT, "agents", "kaggle_anas.py"), "agent"),
    "kaggle_kaito_v23": (os.path.join(ROOT, "agents", "kaggle_kaito_v23.py"), "agent"),
    "baseline": (os.path.join(ROOT, "Kaggriculture", "agents_lib.py"), "baseline"),
    "baseline_v7": (os.path.join(ROOT, "Kaggriculture", "agents_lib.py"), "baseline_v7"),
    "baseline_v8": (os.path.join(ROOT, "Kaggriculture", "agents_lib.py"), "baseline_v8"),
    "melon_maxxer": (os.path.join(ROOT, "Kaggriculture", "agents_lib.py"), "melon_maxxer"),
    "seb_route_v1": (os.path.join(ROOT, "agents", "seb_route_v1.py"), "agent"),
    "seb_route_r0": (os.path.join(ROOT, "agents", "seb_route_r0.py"), "agent"),
    "seb_route_v2": (os.path.join(ROOT, "agents", "seb_route_v2.py"), "agent"),
}

# Promotion policy knobs.
DEFAULT_MIN_GAMES = 30          # decisive games required before any promotion verdict
DEFAULT_MIN_WIN_RATE = 0.55     # noise floor for the margin gate
DEFAULT_CI_Z = 1.96             # 95% Wilson interval
DEFAULT_STEPS = 720             # full game (30 days x 24 turns)
DEV_SEED_BASE = 1_000_000       # development seeds
DECISION_SEED_BASE = 9_000_000  # decision seeds (disjoint from dev)


# --------------------------------------------------------------------------- loading

def _load_callable(file_path, func_name):
    stem = os.path.basename(file_path).rsplit(".", 1)[0]
    spec = importlib.util.spec_from_file_location(f"pg_{stem}", file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, func_name)


def resolve_agent(spec):
    """Return ('builtin', name) or ('callable', fn). Raises on unknown specs."""
    if spec in BUILTIN_OPPONENTS:
        return ("builtin", spec)
    if spec in AGENT_REGISTRY:
        path, fn = AGENT_REGISTRY[spec]
        return ("callable", _load_callable(path, fn))
    if ":" in spec:
        path, fn = spec.rsplit(":", 1)
        if not os.path.isabs(path):
            path = os.path.join(ROOT, path)
        return ("callable", _load_callable(path, fn.strip()))
    raise ValueError(
        f"Unknown agent spec {spec!r}. Registered: {sorted(AGENT_REGISTRY)}; "
        f"builtins: {BUILTIN_OPPONENTS}; or 'path/to/file.py:func'."
    )


# ------------------------------------------------------------------------ statistics

def wilson_ci(k, n, z=DEFAULT_CI_Z):
    """Wilson score interval for a binomial rate k/n at 95% confidence."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


# Two-sided t critical values (95%). From scipy.stats.t.ppf(0.975, df).
_TCRIT_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
    15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080,
    22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
    29: 2.045,
}


def _tcrit(df):
    if df >= 30:
        return 1.96
    return _TCRIT_95.get(df, 2.0)


# ------------------------------------------------------------------- match execution

def _play_one(payload):
    """One full episode on the official engine. Top-level for Windows pickling.
    Agents are resolved inside the worker so specs stay picklable strings."""
    spec_a, spec_b, steps, seed, index, seat = payload
    try:
        from kaggle_environments import make
        _, agent_a = resolve_agent(spec_a)
        _, agent_b = resolve_agent(spec_b)
        first, second = (agent_a, agent_b) if seat == 0 else (agent_b, agent_a)
        env = make(
            "kaggriculture",
            configuration={"episodeSteps": steps, "seed": seed},
            debug=False,
        )
        env.run([first, second])
        r0, r1 = env.steps[-1][0].reward, env.steps[-1][1].reward
        if seat == 0:
            return index, float(r0), float(r1), None
        return index, float(r1), float(r0), None
    except Exception as exc:  # never let one game kill the batch
        return index, None, None, f"{type(exc).__name__}: {exc}"[:300]


def _persist_matchup(tag, spec_a, spec_b, payloads, results, stat):
    """Persist per-game records (seed, seat, scores, winner, delta, error) as CSV
    plus the aggregate stats as JSON under results/. Returns the stats file path."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    tag = re.sub(r"[^A-Za-z0-9_.-]", "_", tag)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.join(RESULTS_DIR, f"{ts}_{tag}")
    csv_path = f"{base}_games.csv"
    stat_path = f"{base}_stats.json"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["tag", "seed", "seat", "spec_a", "spec_b",
             "score_a", "score_b", "winner", "delta", "error"]
        )
        for payload, (ra, rb, err) in zip(payloads, results):
            _, _, _, seed, index, seat = payload
            failed = err is not None or ra is None
            winner = (
                "ERR" if failed
                else "A" if ra > rb else "B" if rb > ra else "TIE"
            )
            delta = "" if failed else f"{float(ra) - float(rb):.0f}"
            writer.writerow([
                tag, seed, seat, spec_a, spec_b,
                "" if failed else f"{float(ra):.0f}",
                "" if failed else f"{float(rb):.0f}",
                winner, delta, err or "",
            ])
    stats = {k: v for k, v in stat.items() if k not in ("bank_a", "bank_b")}
    with open(stat_path, "w", encoding="utf-8") as f:
        json.dump({**stats, "spec_a": spec_a, "spec_b": spec_b, "tag": tag,
                   "ts": ts}, f, indent=2)
    return stat_path


def _record_verdict(stat_path, verdict, reason):
    """Append the gate verdict to the persisted stats JSON for a matchup."""
    if not stat_path or not os.path.isfile(stat_path):
        return
    with open(stat_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["gate_verdict"] = verdict
    data["gate_reason"] = reason
    with open(stat_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_matchup(spec_a, spec_b, n, steps, workers, seed_base, seat_balanced=True, tag=None):
    """Run n games on the given seed group. Returns a stats dict."""
    t0 = time.perf_counter()
    payloads = [
        (spec_a, spec_b, steps, seed_base + i, i, (i % 2) if seat_balanced else 0)
        for i in range(n)
    ]
    results = [None] * n
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for index, ra, rb, err in pool.map(_play_one, payloads, chunksize=1):
            results[index] = (ra, rb, err)
    wall = time.perf_counter() - t0

    ok = [(ra, rb) for ra, rb, e in results if e is None and ra is not None]
    errors = [e for _, _, e in results if e is not None]
    bank_a = [ra for ra, _ in ok]
    bank_b = [rb for _, rb in ok]
    wins_a = sum(1 for ra, rb in ok if ra > rb)
    wins_b = sum(1 for ra, rb in ok if rb > ra)
    ties = len(ok) - wins_a - wins_b
    decisive = wins_a + wins_b
    rate_a = wins_a / decisive if decisive else 0.5
    rate_b = wins_b / decisive if decisive else 0.5
    ci_a = wilson_ci(wins_a, decisive) if decisive else (0.0, 1.0)
    ci_b = wilson_ci(wins_b, decisive) if decisive else (0.0, 1.0)

    stat = {
        "n": n,
        "ok": len(ok),
        "errors": len(errors),
        "wins_a": wins_a,
        "wins_b": wins_b,
        "ties": ties,
        "decisive": decisive,
        "rate_a": rate_a,
        "rate_b": rate_b,
        "ci_a": ci_a,
        "ci_b": ci_b,
        "bank_a": bank_a,
        "bank_b": bank_b,
        "avg_a": statistics.fmean(bank_a) if bank_a else None,
        "avg_b": statistics.fmean(bank_b) if bank_b else None,
        "med_a": statistics.median(bank_a) if bank_a else None,
        "med_b": statistics.median(bank_b) if bank_b else None,
        "wall_s": wall,
        "games_per_s": n / wall if wall else 0.0,
        "errors_detail": errors[:3],
    }
    if tag:
        stat["_stat_path"] = _persist_matchup(tag, spec_a, spec_b, payloads,
                                               results, stat)
    return stat

def gate_verdict(stat, min_games, min_win_rate):
    """Promotion gate. Returns ('PROMOTE'|'HOLD', reason).

    Promotion requires BOTH:
      - >= min_games decisive games, AND
      - winner's rate >= min_win_rate (margin beats noise) OR non-overlapping 95% CIs.
    """
    n = stat["ok"]
    if n < max(1, min_games):
        return ("HOLD", f"only {n} valid games (< {min_games}) — sample too small")
    if stat["errors"] > n * 0.5:
        return ("HOLD", f"{stat['errors']}/{n} games errored — signal is dirty")
    decisive = stat["decisive"]
    if decisive == 0:
        return ("HOLD", "all games tied — nothing to promote on")
    rate_a, rate_b = stat["rate_a"], stat["rate_b"]
    lo_a, hi_a = stat["ci_a"]
    lo_b, hi_b = stat["ci_b"]
    ci_clear = (lo_a > hi_b) or (lo_b > hi_a)
    margin_ok = max(rate_a, rate_b) >= min_win_rate
    if not (ci_clear or margin_ok):
        return (
            "HOLD",
            f"A rate={rate_a:.3f} B rate={rate_b:.3f} — neither clears margin "
            f"{min_win_rate:.2f} nor has non-overlapping CIs "
            f"(A CI=({lo_a:.3f},{hi_a:.3f}) B CI=({lo_b:.3f},{hi_b:.3f}))",
        )
    winner = "A" if rate_a > rate_b else "B"
    basis = "non-overlapping CIs" if ci_clear else f"margin gate ({min_win_rate:.2f})"
    return (
        "PROMOTE",
        f"{winner} over {decisive} decisive games (rate={max(rate_a, rate_b):.3f}, "
        f"basis: {basis}, A CI=({lo_a:.3f},{hi_a:.3f}) B CI=({lo_b:.3f},{hi_b:.3f}))",
    )


def winner_from_stats(dev_stat, dec_stat, min_games, min_win_rate):
    """Which agent would the decision phase promote? 'A'/'B'/None."""
    ref = dec_stat if dec_stat else dev_stat
    if ref is None:
        return None
    verdict, _ = gate_verdict(ref, min_games, min_win_rate)
    if verdict != "PROMOTE":
        return None
    return "A" if ref["rate_a"] > ref["rate_b"] else "B"


# -------------------------------------------------------------------------- reporting

def _fmt(stat):
    med_a = f"{stat['med_a']:.0f}" if stat["med_a"] is not None else "-"
    avg_a = f"{stat['avg_a']:.0f}" if stat["avg_a"] is not None else "-"
    return (
        f"  n={stat['n']} ok={stat['ok']} err={stat['errors']} "
        f"winA={stat['wins_a']} winB={stat['wins_b']} tie={stat['ties']} "
        f"rateA={stat['rate_a']:.3f} medA={med_a} avgA={avg_a} | "
        f"{stat['wall_s']:.1f}s @ {stat['games_per_s']:.1f} games/s"
    )


# ------------------------------------------------------------------ export / upload

def export_agent(name_or_file):
    """Copy an agent (registry name or path:func) to submission/main.py."""
    if name_or_file in AGENT_REGISTRY:
        path, _fn = AGENT_REGISTRY[name_or_file]
    elif ":" in name_or_file:
        path = name_or_file.rsplit(":", 1)[0]
        path = path if os.path.isabs(path) else os.path.join(ROOT, path)
    else:
        path = name_or_file if os.path.isabs(name_or_file) else os.path.join(ROOT, name_or_file)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"no agent file at {path}")
    out_dir = os.path.join(ROOT, "submission")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "main.py")
    with open(path, "r", encoding="utf-8") as f_in, open(out, "w", encoding="utf-8") as f_out:
        f_out.write(f_in.read())
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"exported {os.path.abspath(out)} ({os.path.getsize(out)} bytes, "
          f"sha256={sha[:16]}...)")
    print(f'upload:  kaggle competitions submit -c kaggriculture -f {out} -m "your message"')
    return out


# ---------------------------------------------------------------------- tournament

def vs_pool_match(args):
    """Compare two candidates against a fixed opponent pool (comma-separated
    opponents = one per call). Every candidate gets the identical seeds/seats."""
    opponents = (args.pool or "random").split(",")
    print(f"Kaggriculture pool-compare — {args.a} vs {args.b}, "
          f"opponents={opponents}, {args.n} games/opponent, {args.steps} steps")
    for opp in opponents:
        opp = opp.strip()
        verdict = _pool_compare(args.a, args.b, opp, args.n, args.steps, args.workers,
                               args.decision_seed, args.min_games, args.min_win_rate)
        if verdict:
            print(f"  => {verdict}")
    print("\nNOTE: local pool is the battleground; the real ladder is the final gate.")
    print("      To submit the winner: python playground.py --export <name>")


def _pool_compare(spec_a, spec_b, opponent, n, steps, workers, seed_base,
                  min_games, min_win_rate):
    """One opponent comparison, running both candidates sequentially on the SAME
    seeds and SAME seat (identical opponent trajectory base). Paired design: the
    bank delta between candidates on each seed is the unit of evidence.

    Gate order:
      1. both need >= min_games decisive games vs the pool;
      2. win-rate gate: non-overlapping CIs, else margin gate;
      3. if win-rate CIs overlap (common for open-loop agents that both crush
         the pool), fall back to the paired bank-delta t-interval — promote only
         if the 95% interval of the mean delta excludes 0.
    Returns the verdict string (or None).
    """
    t0 = time.perf_counter()
    sa = run_matchup(spec_a, opponent, n, steps, workers, seed_base)
    sb = run_matchup(spec_b, opponent, n, steps, workers, seed_base)
    wall = time.perf_counter() - t0
    print(f"\n[{spec_a} vs {opponent}]")
    print(_fmt(sa))
    print(f"[{spec_b} vs {opponent}]")
    print(_fmt(sb))
    print(f"  wall={wall:.1f}s")

    dec_a, dec_b = sa["decisive"], sb["decisive"]
    if dec_a == 0 or dec_b == 0:
        return f"HOLD ({opponent}): no decisive games for one side — cannot compare."
    if dec_a < min_games or dec_b < min_games:
        return f"HOLD vs {opponent}: decisive games {dec_a}/{dec_b} < {min_games}"

    ra, rb = sa["wins_a"] / dec_a, sb["wins_a"] / dec_b
    lo_a, hi_a = wilson_ci(sa["wins_a"], dec_a)
    lo_b, hi_b = wilson_ci(sb["wins_a"], dec_b)
    print(f"  win-rate vs {opponent}: {spec_a}={ra:.3f} ({lo_a:.2f},{hi_a:.2f})  "
          f"{spec_b}={rb:.3f} ({lo_b:.2f},{hi_b:.2f})")

    # Step 2: win-rate gates.
    ci_clear = (lo_a > hi_b) or (lo_b > hi_a)
    if ci_clear:
        winner = spec_a if ra > rb else spec_b
        return f"PROMOTE {winner} vs {opponent} (non-overlapping CIs, " \
               f"pool rate {max(ra, rb):.3f})"
    if max(ra, rb) >= min_win_rate and ra != rb:
        winner = spec_a if ra > rb else spec_b
        return f"PROMOTE {winner} vs {opponent} (margin gate, pool rate " \
               f"{max(ra, rb):.3f})"

    # Step 3: paired bank-delta gate (same seeds, same seat -> paired deltas).
    if not (sa["bank_a"] and sb["bank_a"]) or len(sa["bank_a"]) != len(sb["bank_a"]):
        return f"HOLD vs {opponent}: bank arrays mismatch — paired gate unavailable."
    deltas = [a - b for a, b in zip(sa["bank_a"], sb["bank_a"])]
    mean_d = statistics.fmean(deltas)
    n_d = len(deltas)
    if n_d < 2:
        return f"HOLD vs {opponent}: only {n_d} paired games."
    sd = statistics.stdev(deltas) if n_d > 1 else 0.0
    tcrit = 1.96 if n_d >= 30 else _tcrit(n_d - 1)
    half = tcrit * sd / math.sqrt(n_d)
    lo_d, hi_d = mean_d - half, mean_d + half
    print(f"  paired bank delta A-B: mean={mean_d:+.0f} 95% CI=({lo_d:+.0f},{hi_d:+.0f}) "
          f"over {n_d} seeds (same seeds/seats)")
    if lo_d > 0:
        return f"PROMOTE {spec_a} vs {opponent} (paired bank delta " \
               f"{mean_d:+.0f}, CI excludes 0)"
    if hi_d < 0:
        return f"PROMOTE {spec_b} vs {opponent} (paired bank delta " \
               f"{mean_d:+.0f}, CI excludes 0)"
    return f"HOLD vs {opponent}: paired bank delta {mean_d:+.0f} CI " \
           f"({lo_d:+.0f},{hi_d:+.0f}) includes 0 — noise floor."


# ---------------------------------------------------------------------- tournament

def tournament(agent_names, n, steps, workers, min_games, min_win_rate):
    """All-pairs seat-balanced round robin on dev seeds. Local pool ranking only —
    NOT the final gate (the final gate is the real ladder)."""
    print(f"\n=== Tournament ({len(agent_names)} agents x {n} games/pair, {steps} steps) ===")
    total = {name: 0.0 for name in agent_names}
    played = {name: 0 for name in agent_names}
    for i in range(len(agent_names)):
        for j in range(i + 1, len(agent_names)):
            a, b = agent_names[i], agent_names[j]
            print(f"\n-- {a} vs {b} --")
            stat = run_matchup(a, b, n, steps, workers, DEV_SEED_BASE)
            print(_fmt(stat))
            verdict, why = gate_verdict(stat, min_games, min_win_rate)
            print(f"  -> {verdict}: {why}")
            total[a] += stat["rate_a"]
            total[b] += (1 - stat["rate_a"])
            played[a] += stat["ok"]
            played[b] += stat["ok"]
    print("\n Local pool ranking (dev seeds only — informational, NOT the final gate):")
    for name in sorted(total, key=lambda x: total[x], reverse=True):
        print(f"   {name:<14} aggregate_rate={total[name] / max(1, len(agent_names) - 1):.3f}"
              f"  games={played[name]}")


# ---------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="Kaggriculture local agent battleground (confidence-gated promotion)."
    )
    ap.add_argument("--a", default="kaggle_v22_romanrozen", help="challenger spec (default kaggle_v22_romanrozen)")
    ap.add_argument("--b", default="kaggle_v23", help="incumbent spec (default kaggle_v23)")
    ap.add_argument("--n", type=int, default=32, help="games per phase (default 32)")
    ap.add_argument("--steps", type=int, default=DEFAULT_STEPS,
                    help="episode steps (720 = full game; lower = fast smoke)")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() - 2))
    ap.add_argument("--phase", choices=["dev", "decision", "both"], default="both",
                    help="seed groups to run; decision is the verdict phase")
    ap.add_argument("--seed", type=int, default=DEV_SEED_BASE, help="dev seed base")
    ap.add_argument("--decision-seed", type=int, default=DECISION_SEED_BASE,
                    help="decision seed base (disjoint from dev)")
    ap.add_argument("--min-games", type=int, default=DEFAULT_MIN_GAMES)
    ap.add_argument("--min-win-rate", type=float, default=DEFAULT_MIN_WIN_RATE)
    ap.add_argument("--tournament", action="store_true", help="run all-pairs round robin")
    ap.add_argument("--vs-pool", action="store_true",
                    help="compare --a vs --b against a common opponent (--pool), "
                         "same seeds/seats; for agents that tie head-to-head")
    ap.add_argument("--pool", default="random",
                    help="comma-separated opponents for --vs-pool (default random)")
    ap.add_argument("--agents", default=None,
                    help="comma-separated agent list (for --tournament)")
    ap.add_argument("--export", default=None,
                    help="agent spec (name or path:func) -> submission/main.py")
    ap.add_argument("--list", action="store_true", help="list registered agents")
    args = ap.parse_args()

    if args.list:
        for name, (path, fn) in AGENT_REGISTRY.items():
            print(f"{name:<14} {os.path.basename(path)}:{fn}")
        return

    if args.export:
        export_agent(args.export)
        return

    if args.tournament:
        names = (args.agents or ",".join(sorted(AGENT_REGISTRY))).split(",")
        tournament([s.strip() for s in names], args.n, args.steps, args.workers,
                   args.min_games, args.min_win_rate)
        return

    if args.vs_pool:
        vs_pool_match(args)
        return

    print(f"Kaggriculture playground — challenger({args.a}) vs incumbent({args.b})")
    print(f"{args.n} games/phase, {args.steps}-step episodes, {args.workers} workers, "
          f"min_games={args.min_games} min_win_rate={args.min_win_rate:.2f}")

    dev_stat = dec_stat = None
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.phase in ("dev", "both"):
        tag = f"dev_{args.a}_vs_{args.b}_n{args.n}"
        print(f"\n[dev phase] seeds {args.seed}..{args.seed + args.n - 1}")
        dev_stat = run_matchup(args.a, args.b, args.n, args.steps, args.workers,
                               args.seed, tag=tag)
        print(_fmt(dev_stat))
        verdict, why = gate_verdict(dev_stat, args.min_games, args.min_win_rate)
        print(f"  -> dev verdict: {verdict} — {why}")
        _record_verdict(dev_stat.get("_stat_path"), verdict, why)
    if args.phase in ("decision", "both"):
        tag = f"decision_{args.a}_vs_{args.b}_n{args.n}"
        print(f"\n[decision phase] seeds {args.decision_seed}..{args.decision_seed + args.n - 1}")
        dec_stat = run_matchup(args.a, args.b, args.n, args.steps, args.workers,
                               args.decision_seed, tag=tag)
        print(_fmt(dec_stat))
        verdict, why = gate_verdict(dec_stat, args.min_games, args.min_win_rate)
        print(f"  -> decision verdict: {verdict} — {why}")
        _record_verdict(dec_stat.get("_stat_path"), verdict, why)

    winner = winner_from_stats(dev_stat, dec_stat, args.min_games, args.min_win_rate)
    print("\n=== FINAL (decision phase gate) ===")
    if winner is None:
        print("  HOLD — no promotion. Margin does not beat the noise floor.")
        print("  Run more games (--n 64..90) before judging again.")
    else:
        champion = args.a if winner == "A" else args.b
        print(f"  PROMOTE {champion} (won the decision-phase gate).")
        print(f"  Local says 'this beats the pool'. Ladder says 'this beats the field' —")
        print(f"  submit via: python playground.py --export {champion}")


if __name__ == "__main__":
    main()