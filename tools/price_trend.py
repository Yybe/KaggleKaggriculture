"""Price-trend check for loss vs win seeds (rulebook G5: instrument first).

For each seed, run V14 vs V14 (agents irrelevant; market prices are exogenous
to agent identity) and sample STRAWBERRY/MILK/WOOL prices at late steps.

Usage:
    python price_trend.py
Prints per seed: p(440) p(480) ... p(700) and trend label (rising/flat/falling)
for the last 240 steps window (>= 480).
"""
import os
import sys
import importlib.util
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath("agents"))
sys.path.insert(0, os.path.abspath("Kaggriculture"))

LOSS_SEEDS = [3241, 3533, 3971, 3168, 2292, 3898, 4774, 3387, 4482, 4044, 2511]
WIN_SEEDS = [2584, 2657, 3679, 3095, 2219, 2146, 2803, 2876, 3460, 2365, 2000]

STEPS = [440, 480, 520, 560, 600, 640, 660, 680, 700]


def _probe(args):
    seed = args
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([lambda o, c: "PASS", lambda o, c: "PASS"])
    series = {}
    for i, st in enumerate(env.steps):
        if i in STEPS:
            px = st[0]["observation"]["market"]["prices"]
            series[i] = {g: int(px.get(g, 0)) for g in ("STRAWBERRY", "MILK", "WOOL")}
    return seed, series


def trend(vals):
    """vals: list of prices at STEPS. Classify slope over the >=480 window."""
    sub = [v for s, v in zip(STEPS, vals) if s >= 480]
    if len(sub) < 2:
        return "?"
    first, last = sub[0], sub[-1]
    if last > first * 1.15:
        return "RISING"
    if last < first * 0.85:
        return "FALLING"
    return "flat"


def main():
    with ProcessPoolExecutor(max_workers=14) as ex:
        res = list(ex.map(_probe, LOSS_SEEDS + WIN_SEEDS))
    by_seed = {r[0]: r[1] for r in res}
    print(f"{'seed':>6} {'grp':<4} | " + " ".join(f"{s:>4}" for s in STEPS) + " | STR MIL WOOL trend")
    for seed in LOSS_SEEDS + WIN_SEEDS:
        grp = "LOSS" if seed in LOSS_SEEDS else "WIN "
        s = by_seed[seed]
        for g in ("STRAWBERRY", "MILK", "WOOL"):
            vals = [s[st][g] for st in STEPS]
            print(f"{seed:>6} {grp:<4} | " + " ".join(f"{v:>4}" for v in vals) + f" | {g[:3]} {trend(vals)}")


if __name__ == "__main__":
    main()
