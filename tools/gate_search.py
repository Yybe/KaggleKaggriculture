"""Seed-level gate signal search: V15 vs V14 per seed, collect capselllate fires
with candidate signals, find which signal+threshold best separates LOSS seeds
(should HOLD most fires) from WIN seeds (should FIRE most fires).

Usage:
    python gate_search.py
"""
import importlib.util
import sys
import os

sys.path.insert(0, os.path.abspath("agents"))

spec = importlib.util.spec_from_file_location("v15", r"agents\kaggle_champion_v15.py")
mod15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod15)

from kaggle_environments import make

_HIGH = ("STRAWBERRY", "MILK", "WOOL")
LOSS_SEEDS = [3241, 3533, 3971, 3168, 2292, 3898, 4774, 3387, 4482, 4044, 2511]
WIN_SEEDS = [2584, 2657, 3679, 3095, 2219, 2146, 2803, 2876, 3460, 2365, 2000]
WINDOWS = (16, 32, 48, 64, 96, 128, 192, 240)


def run_seed(seed):
    """V15 vs V14. Record (step, item, qty, p_now) for every high-value SELL >= 480."""
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod15.agent, mod15.agent])
    px_hist = {}  # (step, item) -> price
    fires = []
    for i, st in enumerate(env.steps):
        o = st[0]["observation"]
        px = o["market"]["prices"]
        for g in _HIGH:
            px_hist[(i, g)] = float(px.get(g, 0) or 0)
        a = st[0].get("action", {}) or {}
        for order in a.get("market") or []:
            if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                item = str(order[1])
                if item in _HIGH and 480 <= i < 716:
                    try:
                        qty = int(order[2])
                    except (TypeError, ValueError):
                        qty = 0
                    fires.append((i, item, qty, float(px.get(item, 0) or 0)))
    return fires, px_hist


def signals(fires, px_hist, step, item):
    """Candidate per-fire signals. All are 'higher = more likely good to fire'."""
    out = {}
    p_now = px_hist.get((step, item), 0.0)
    base = float(mod15._MARKET_PARAMS[item][0])
    out["p_now"] = p_now
    out["p/base"] = p_now / base if base else 0.0
    for w in WINDOWS:
        p_past = px_hist.get((max(480, step - w), item), p_now)
        out[f"mom{w}"] = p_now - p_past
        out[f"mom{w}/b"] = (p_now - p_past) / base if base else 0.0
    # price at 480 baseline
    p480 = px_hist.get((480, item), p_now)
    out["vs480"] = p_now - p480
    out["vs480/b"] = (p_now - p480) / base if base else 0.0
    return out


def main():
    seed_fires = {}  # seed -> list of (step, item, signals)
    for seed in LOSS_SEEDS + WIN_SEEDS:
        fires, px_hist = run_seed(seed)
        rows = []
        for step, item, qty, p in fires:
            rows.append((step, item, signals(fires, px_hist, step, item)))
        seed_fires[seed] = rows

    labels = {s: (s in LOSS_SEEDS) for s in LOSS_SEEDS + WIN_SEEDS}  # True = LOSS seed

    # Evaluate each signal: for threshold T, count fires fired (sig >= T).
    # Seed is 'held' if <50% of its fires fired; 'fired' otherwise.
    best = []
    for sig in ("p/base", "mom16/b", "mom32/b", "mom48/b", "mom64/b", "mom96/b",
                "mom128/b", "mom192/b", "mom240/b", "vs480/b", "p_now", "vs480"):
        for T in ([i / 100 for i in range(-60, 121, 5)] if sig.endswith("/b") or sig.startswith("mom")
                  else [i for i in range(0, 260, 10)]):
            held, fired = [], []
            for seed in LOSS_SEEDS + WIN_SEEDS:
                rows = seed_fires[seed]
                if not rows:
                    continue
                n_fire = sum(1 for r in rows if r[2][sig] >= T)
                is_held = n_fire < len(rows) / 2
                (held if is_held else fired).append(seed)
            loss_held = [s for s in held if labels[s]]
            win_held = [s for s in held if not labels[s]]
            loss_fired = [s for s in fired if labels[s]]
            win_fired = [s for s in fired if not labels[s]]
            score = len(loss_held) + len(win_fired)
            best.append((score, sig, T, len(loss_held), len(loss_fired), len(win_held), len(win_fired)))

    best.sort(key=lambda x: (-x[0], -x[3], -x[6]))
    print("score | sig T | loss_held loss_fired win_held win_fired")
    for score, sig, T, lh, lf, wh, wf in best[:20]:
        print(f"{score:>5} | {sig:>10} T={T:>6} | loss_held={lh:>2} loss_fired={lf:>2} win_held={wh:>2} win_fired={wf:>2}")


if __name__ == "__main__":
    main()
