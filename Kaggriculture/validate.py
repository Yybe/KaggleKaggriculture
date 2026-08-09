"""Parallel multi-seed validation for main.agent with meta metrics.

Usage:
    python validate.py --interval 12 --b starter --n 32
    python validate.py --interval 24 --b random --n 32
    python validate.py --interval 12 --b main:agent --n 16   # self-play

Reports per-regime score distribution (mean/median/max) plus meta-metric
aggregates: forbidden-buy count, melon sell-out by day 12, animals alive at
the end, and shed melon leftover.
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

BANNED_PRODUCT_BUYS = {"FERTILIZER"}
BANNED_ANIMAL_BUYS = {"GOOSE"}
BANNED_SEED_BUYS = {"CARROT", "TOMATO"}
BANNED_FARMER_OPS = {"BUILD_COOP"}
MELON_DEADLINE_DAY = 12
MAX_UNLOCKED = 3


def resolve_agent(spec):
    if isinstance(spec, str) and spec in BUILTINS:
        return spec
    mod_name, _, fn = spec.partition(":")
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        return spec
    return getattr(mod, fn)


def _play_one(args):
    spec_a, spec_b, steps, seed, index, interval, track = args
    from kaggle_environments import make

    a = resolve_agent(spec_a)
    b = resolve_agent(spec_b)
    meta = {"forbidden": 0, "melon_sold_by_day": {}, "melon_sold_total": 0}

    def wrap(fn, is_tracked):
        def agent(obs, configuration=None):
            act = fn(obs, configuration)
            if not is_tracked:
                return act
            day = int((obs or {}).get("day", 0) or 0)
            for order in act.get("market") or []:
                order = list(order or [])
                if not order:
                    continue
                op = order[0]
                if len(order) >= 2:
                    if op == "BUY_PRODUCT" and order[1] in BANNED_PRODUCT_BUYS:
                        meta["forbidden"] += 1
                    if op == "BUY_ANIMAL" and order[1] in BANNED_ANIMAL_BUYS:
                        meta["forbidden"] += 1
                    if op == "BUY_SEED" and order[1] in BANNED_SEED_BUYS:
                        meta["forbidden"] += 1
                    if op == "BUY_LAND" and day >= 0:
                        pass  # capped in guard; count separately below
                    if op == "SELL" and order[1] == "MELON":
                        meta["melon_sold_total"] += int(order[2])
                        meta["melon_sold_by_day"][day] = (
                            meta["melon_sold_by_day"].get(day, 0) + int(order[2])
                        )
            op0 = (act.get("farmer") or ["PASS"])[0]
            if op0 in BANNED_FARMER_OPS:
                meta["forbidden"] += 1
            return act

        return agent

    try:
        env = make(
            "kaggriculture",
            configuration={
                "episodeSteps": steps,
                "seed": seed,
                "townCenterSellInterval": interval,
            },
            debug=False,
        )
        env.run([wrap(a, True), wrap(b, False)])
        fin = env.steps[-1]
        obs = fin[0].observation
        reward = float(fin[0].reward)
        opp_reward = float(fin[1].reward)

        farm = obs.farms[0]
        private = obs.private
        animals = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
        melon_tiles = 0
        for row in farm["tiles"]:
            for tile in row:
                if isinstance(tile, dict) and "animal" in tile:
                    animals[tile["animal"]] = animals.get(tile["animal"], 0) + 1
                if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON":
                    melon_tiles += 1
        shed_melon = int((private.get("shed") or {}).get("MELON", 0) or 0)
        unlocked = len(farm.get("unlocked_quadrants") or [])

        sold_by_12 = sum(
            n for d, n in meta["melon_sold_by_day"].items() if d <= MELON_DEADLINE_DAY
        )
        return (
            index, reward, opp_reward,
            {
                "forbidden": meta["forbidden"],
                "animals": animals,
                "melon_sold_total": meta["melon_sold_total"],
                "melon_sold_by_day_12": sold_by_12,
                "melon_rotted": shed_melon + melon_tiles,
                "shed_melon_end": shed_melon,
                "melon_tiles_end": melon_tiles,
                "unlocked": unlocked,
            },
            0,
        )
    except Exception as e:
        return index, None, None, None, str(e)[:200]


def run_batch(spec_a, spec_b, n, steps=720, workers=WORKERS, seed_base=42, interval=12):
    t0 = time.perf_counter()
    args = [(spec_a, spec_b, steps, seed_base + i, i, interval, True) for i in range(n)]
    results = [None] * n
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for index, ra, rb, meta, err in ex.map(_play_one, args, chunksize=1):
            results[index] = (ra, rb, meta, err)
    dt = time.perf_counter() - t0

    ok = [(ra, rb, m) for ra, rb, m, err in results if err == 0 and ra is not None]
    errs = [e for _, _, _, e in results if e]
    wins_a = sum(1 for ra, rb, _ in ok if ra > rb)
    wins_b = sum(1 for ra, rb, _ in ok if rb > ra)
    ties = len(ok) - wins_a - wins_b

    meta_agg = {
        "forbidden_total": sum(m["forbidden"] for _, _, m in ok),
        "melon_rotted_total": sum(m["melon_rotted"] for _, _, m in ok),
        "melons_sold_by_day_12": [m["melon_sold_by_day_12"] for _, _, m in ok],
        "animals_end": [m["animals"] for _, _, m in ok],
        "unlocked_max": max((m["unlocked"] for _, _, m in ok), default=0),
        "unlocked_min": min((m["unlocked"] for _, _, m in ok), default=0),
    }
    all_alive = all(
        m["animals"]["GOOSE"] == 0 and m["animals"]["COW"] == 8 and m["animals"]["SHEEP"] == 6
        for _, _, m in ok
    )

    print(f"interval={interval}  Games: {n}  ok={len(ok)}  errors={len(errs)}  "
          f"wall={dt:.1f}s  ({workers} workers)")
    if ok:
        scores_a = [ra for ra, _, _ in ok]
        print(f"  A({spec_a}): win={wins_a} ({wins_a / len(ok) * 100:.0f}%)  "
              f"avg={statistics.mean(scores_a):.0f}  med={statistics.median(scores_a):.0f}  "
              f"min={min(scores_a):.0f}  max={max(scores_a):.0f}  sd={statistics.pstdev(scores_a):.0f}")
        print(f"  B({spec_b}): win={wins_b} ({wins_b / len(ok) * 100:.0f}%)  ties={ties}")
        print(f"  META forbidden={meta_agg['forbidden_total']}  "
              f"melon_rotted={meta_agg['melon_rotted_total']}  "
              f"melons_sold_by_12={statistics.mean(meta_agg['melons_sold_by_day_12']):.1f} (per game)  "
              f"unlocked=[{meta_agg['unlocked_min']},{meta_agg['unlocked_max']}]  "
              f"animals_all_alive={all_alive}")
    else:
        print(f"All {n} games errored (first: {errs[:1]})")
    return results, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="main:agent", help="agent spec for player 0")
    ap.add_argument("--b", default="starter", help="agent spec for player 1")
    ap.add_argument("--n", type=int, default=32, help="number of games")
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--interval", type=int, default=12,
                    help="townCenterSellInterval: 12=legacy, 24=rebalance")
    args = ap.parse_args()
    run_batch(args.a, args.b, args.n, args.steps, args.workers, args.seed, args.interval)


if __name__ == "__main__":
    main()
