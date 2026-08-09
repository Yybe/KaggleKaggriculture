"""Trace capselllate bump behavior on specific seeds (win vs loss comparison).

For each seed: runs V15 vs V14, records every step >= 456 where V15's final
market order for a high-value item differs from V14's (i.e. the bump fired),
plus V15 shed levels and shared market prices around those steps.

Usage: python diag_trace_bump.py <seed> [seed ...]
"""
import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath("agents"))
sys.path.insert(0, os.path.abspath("Kaggriculture"))

_HIGH = ("STRAWBERRY", "MILK", "WOOL")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sell_orders(action):
    out = []
    for order in (action.get("market") or []):
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
            out.append((str(order[1]), int(order[2])))
    return out


def trace_seed(seed):
    from kaggle_environments import make

    mod15 = _load(os.path.abspath("agents/kaggle_champion_v15.py"), "m15")
    mod14 = _load(os.path.abspath("agents/kaggle_boat84_v14.py"), "m14")

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod15.agent, mod14.agent])

    steps = env.steps
    r0 = float(steps[-1][0].reward)
    r1 = float(steps[-1][1].reward)

    bump_events = []
    price_snapshots = []
    for step, frame in enumerate(steps):
        if step < 456:
            continue
        a0 = (frame[0].get("action") or {})
        a1 = (frame[1].get("action") or {})
        s0 = _sell_orders(a0)
        s1 = _sell_orders(a1)
        # compare high-value quantities
        q0 = {}
        q1 = {}
        for item, qty in s0:
            q0[item] = q0.get(item, 0) + qty
        for item, qty in s1:
            q1[item] = q1.get(item, 0) + qty
        diff = {}
        for item in _HIGH:
            if q0.get(item, 0) != q1.get(item, 0):
                diff[item] = (q0.get(item, 0), q1.get(item, 0))
        if diff:
            bump_events.append((step, diff))
        if step % 48 == 0 or step == 719:
            market = frame[0].get("obs", {}).get("market", {}) or {}
            inv = market.get("inventory", {}) or {}
            prices = market.get("prices", {}) or {}
            price_snapshots.append({
                "step": step,
                "inv": {k: inv.get(k, 0) for k in _HIGH},
                "price": {k: prices.get(k, 0) for k in _HIGH},
            })

    shed_v15 = steps[-1][0].get("obs", {}).get("private", {}).get("shed", {}) or {}
    shed_v14 = steps[-1][1].get("obs", {}).get("private", {}).get("shed", {}) or {}

    print(f"\n=== seed {seed}: v15={int(r0):,} v14={int(r1):,} d={int(r0-r1):+6d} ===")
    print(f"  shed end v15: {dict(shed_v15)}")
    print(f"  shed end v14: {dict(shed_v14)}")
    if bump_events:
        print(f"  bump events (step, item: (v15qty, v14qty)) — {len(bump_events)} total:")
        # compact: group consecutive ranges
        for step, diff in bump_events:
            print(f"    step={step:3d}  {diff}")
    else:
        print("  NO bump events after step 456!")
    print("  price/inventory snapshots (shared market):")
    for snap in price_snapshots:
        print(f"    step={snap['step']:3d} inv={snap['inv']} price={snap['price']}")


if __name__ == "__main__":
    seeds = [int(s) for s in sys.argv[1:]] or [2000, 3241]
    for seed in seeds:
        trace_seed(seed)
