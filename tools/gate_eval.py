"""Empirical gate evaluation: for each V15 capselllate fire, compute true gain
(p_now - p_at_next_sell_of_same_item), then score gate candidates.

Usage:
    python gate_eval.py <seed> [seed ...]
Prints per-fire: step, item, p_now, p_next, gain, base_price, p_now/base.
Then a summary: gate candidates (threshold on p_now/base) -> correct/incorrect.
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


def run_seed(seed):
    """Run V15 vs V14. Record every SELL of high-value items (step, item, qty, price)."""
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod15.agent, mod15.agent])  # same agent twice: pure schedule, no opponent asymmetry
    sells = []  # (step, item, qty, price_after? ) we need price BEFORE sell
    prev_px = {}
    for i, st in enumerate(env.steps):
        o = st[0]["observation"]
        px = o["market"]["prices"]
        a = st[0].get("action", {}) or {}
        for order in a.get("market") or []:
            if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                item = str(order[1])
                if item in _HIGH:
                    try:
                        qty = int(order[2])
                    except (TypeError, ValueError):
                        qty = 0
                    # price at the START of this step (before this sell executes)
                    p = float(px.get(item, 0) or 0)
                    sells.append((i, item, qty, p))
        # store price history for later "next sell" lookup
        for g in _HIGH:
            prev_px[(i, g)] = float(px.get(g, 0) or 0)
    return sells, prev_px


def main():
    seeds = [int(x) for x in sys.argv[1:]] or (LOSS_SEEDS + WIN_SEEDS)
    all_fires = []  # (seed, step, item, p_now, p_next, gain)
    for seed in seeds:
        sells, px = run_seed(seed)
        for idx, (step, item, qty, p_now) in enumerate(sells):
            if step < 480 or step >= 716:
                continue
            # next sell of the same item
            nxt = next((s for s in sells[idx + 1:] if s[1] == item), None)
            if nxt is None:
                p_next = px.get((715, item), p_now)
            else:
                p_next = nxt[3]
            gain = p_now - p_next
            base = mod15._MARKET_PARAMS[item][0]
            all_fires.append((seed, step, item, p_now, p_next, gain, base))
    print(f"{'seed':>6} {'step':>4} {'item':<11} {'p_now':>5} {'p_next':>5} {'gain':>6} {'p_now/base':>8}")
    for seed, step, item, p_now, p_next, gain, base in sorted(all_fires, key=lambda r: r[0]):
        print(f"{seed:>6} {step:>4} {item:<11} {p_now:>5.0f} {p_next:>5.0f} {gain:>+6.0f} {p_now/base:>7.0%}")

    # Gate candidates: fire iff p_now/base >= T
    print("\n-- threshold gates on p_now/base --")
    for T in (0.30, 0.40, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90):
        correct = sum(1 for f in all_fires if (f[3] / f[6] >= T) == (f[5] > 0))
        tot = len(all_fires)
        print(f"T={T:.2f}: {correct}/{tot} correct ({correct/tot:.0%})")

    # Gate: fire iff gain sign matches p_now vs base comparison? also momentum variants later.
    # ground-truth distribution
    pos = sum(1 for f in all_fires if f[5] > 0)
    print(f"\nfires: {len(all_fires)} | positive-gain fires: {pos} ({pos/len(all_fires):.0%})")


if __name__ == "__main__":
    main()
