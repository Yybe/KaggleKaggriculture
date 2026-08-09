"""Systematic parameter tuning for V14-enhanced variants."""
import os
import sys
import copy
import time
import statistics
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath('agents'))
sys.path.insert(0, os.path.abspath('Kaggriculture'))

import kaggle_boat84_v14 as _v14

_ACTIONS = _v14._ACTIONS
_NON_ONGOING_MAX = {"WHEAT": 6, "CARROT": 4, "MELON": 6}

_get = _v14._get
_copy_action = _v14._copy_action
_seat = _v14._seat
_farm = _v14._farm
_align_hands = _v14._align_hands
_projected_shed = _v14._projected_shed
_public_signature = _v14._public_signature
_clone_distance = _v14._clone_distance
_shift_state = _v14._shift_state
_repay_shift = _v14._repay_shift
_future_sells = _v14._future_sells
_tile_at = _v14._tile_at
_weed_repair_action = _v14._weed_repair_action
_rank_sell_slots = _v14._rank_sell_slots
_terminal_liquidation = _v14._terminal_liquidation
_MARKET_PARAMS = _v14._MARKET_PARAMS
_PREMIUM = _v14._PREMIUM

def build_agent_fn(bump_cap=2, latefill_step=456, high_val_tuple=("STRAWBERRY", "MILK", "WOOL"), 
                   preempt_fraction=2.0, preempt_max_batch=30, term_liq_step=716):
    
    def _custom_preempt_shift(obs, action, step):
        if not (120 <= step < 680):
            return action
        state = _shift_state(obs, step)
        if state.get("due") or _clone_distance(obs) > 6:
            return action
        future = _future_sells(step)
        if not future:
            return action
        market = list(action.get("market") or [])
        if len(market) >= 10:
            return action
        remaining = _projected_shed(obs, action)
        for raw in market:
            if len(raw) >= 3 and raw[0] == "SELL":
                item = raw[1]
                remaining[item] = max(0, int(remaining.get(item, 0) or 0) - max(0, int(raw[2])))
        prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
        shifted = {}
        for item in _PREMIUM:
            future_quantity = max(0, int(future.get(item, 0) or 0))
            if future_quantity < 4:
                continue
            base_price = float(_MARKET_PARAMS[item][0])
            if float(_get(prices, item, 0) or 0) < base_price * 0.0:
                continue
            target = min(
                max(0, int(remaining.get(item, 0) or 0)),
                future_quantity,
                preempt_max_batch,
                max(1, int(round(future_quantity * preempt_fraction))),
            )
            if target <= 0 or len(market) >= 10:
                continue
            market.append(["SELL", item, target])
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - target)
            shifted[item] = target
        if shifted:
            action["market"] = market[:10]
            state["due_step"] = step + 1
            state["due"] = shifted
        return action

    def _custom_fill(action, obs):
        seat = _seat(obs)
        farm = _farm(obs, seat)
        positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
        units = [action["farmer"], *action["hands"]]

        for index, (position, planned) in enumerate(zip(positions, units)):
            if not planned or planned[0] != "PASS":
                continue
            tile = _tile_at(farm, position)
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT":
                crop = tile.get("crop")
                if crop in _NON_ONGOING_MAX:
                    if int(tile.get("yield_units", 0) or 0) >= _NON_ONGOING_MAX[crop]:
                        units[index] = ["HARVEST"]
                    elif not tile.get("watered_today", False):
                        units[index] = ["WATER"]

        action["farmer"] = units[0] if units else ["PASS"]
        action["hands"] = units[1:]
        return action

    def _custom_topup(action, obs):
        step = int(_get(obs, "step", 0) or 0)
        if step < latefill_step:
            return action
        seat = _seat(obs)
        private = _get(obs, "private", {}) or {}
        shed = dict(private.get("shed") or {})
        market = list(action.get("market") or [])
        new_market = []
        for order in market:
            if (isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL"):
                item = str(order[1])
                if item in high_val_tuple:
                    try:
                        qty = int(order[2])
                    except (TypeError, ValueError):
                        qty = 0
                    available = int(shed.get(item, 0) or 0)
                    if available > qty:
                        order = [order[0], order[1], qty + min(bump_cap, available - qty)]
            new_market.append(list(order))
        action["market"] = new_market
        return action

    def _custom_liq(obs, action, step):
        if step < term_liq_step:
            return action
        return _terminal_liquidation(obs, action, step)

    def agent(obs):
        try:
            step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
            action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
            action = _custom_fill(action, obs)
            action = _repay_shift(obs, action, step)
            action = _rank_sell_slots(obs, action, None)
            action = _custom_preempt_shift(obs, action, step)
            action = _custom_topup(action, obs)
            action = _custom_liq(obs, action, step)
            return _align_hands(action, obs)
        except Exception:
            farm = _farm(obs, _seat(obs))
            return {
                "farmer": ["PASS"],
                "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
                "market": [],
            }

    return agent


# Wrapper for parallel evaluation with arguments dict
def play_match_config(args):
    cfg, seed, swap = args
    from kaggle_environments import make
    agent_a = build_agent_fn(**cfg)
    agent_b = _v14.agent
    
    p0 = agent_b if swap else agent_a
    p1 = agent_a if swap else agent_b
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([p0, p1])
        r0 = float(env.steps[-1][0].reward)
        r1 = float(env.steps[-1][1].reward)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return score_a, score_b, None
    except Exception as e:
        return None, None, str(e)


def evaluate_config(name, cfg, n_seeds=15, workers=14):
    t0 = time.perf_counter()
    tasks = []
    for s in range(n_seeds):
        seed = 1000 + s * 43
        tasks.append((cfg, seed, False))
        tasks.append((cfg, seed, True))
    
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(play_match_config, tasks):
            results.append(r)
    
    dt = time.perf_counter() - t0
    ok = [r for r in results if r[2] is None and r[0] is not None]
    
    wins_a = sum(1 for r in ok if r[0] > r[1])
    wins_b = sum(1 for r in ok if r[1] > r[0])
    ties = sum(1 for r in ok if r[0] == r[1])
    
    scores_a = [r[0] for r in ok]
    scores_b = [r[1] for r in ok]
    deltas = [r[0] - r[1] for r in ok]
    
    win_rate = wins_a / max(len(ok), 1) * 100
    mean_delta = statistics.mean(deltas) if deltas else 0
    print(f"[{name:<32}] {len(ok)} games: Win={wins_a:>2} ({win_rate:5.1f}%), Loss={wins_b:>2}, Tie={ties} | Mean Delta={mean_delta:+6.0f} ({dt:.1f}s)")
    return win_rate, mean_delta, wins_a, wins_b, ties


if __name__ == '__main__':
    print("Evaluating parameter variations against V14 baseline (30 games each)...")
    
    configs = [
        ("Baseline V26-style (+2, 456, S/M/W)", 
         {"bump_cap": 2, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL")}),
        
        ("Cap +1 (456, S/M/W)", 
         {"bump_cap": 1, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL")}),
         
        ("Cap +3 (456, S/M/W)", 
         {"bump_cap": 3, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL")}),

        ("Step 432 (day 18) (+2, S/M/W)", 
         {"bump_cap": 2, "latefill_step": 432, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL")}),

        ("Step 408 (day 17) (+2, S/M/W)", 
         {"bump_cap": 2, "latefill_step": 408, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL")}),

        ("Step 480 (day 20) (+2, S/M/W)", 
         {"bump_cap": 2, "latefill_step": 480, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL")}),

        ("Items S/M/W/MELON (+2, 456)", 
         {"bump_cap": 2, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL", "MELON")}),

        ("Items STRAW/MILK only (+2, 456)", 
         {"bump_cap": 2, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK")}),

        ("Preempt 2.5x, max 35 (+2, 456)", 
         {"bump_cap": 2, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL"), "preempt_fraction": 2.5, "preempt_max_batch": 35}),

        ("Preempt 1.5x, max 25 (+2, 456)", 
         {"bump_cap": 2, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL"), "preempt_fraction": 1.5, "preempt_max_batch": 25}),

        ("Terminal Liq step 714 (+2, 456)", 
         {"bump_cap": 2, "latefill_step": 456, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL"), "term_liq_step": 714}),

        ("Best Combo A (Cap+2, 432, S/M/W, Liq 714)", 
         {"bump_cap": 2, "latefill_step": 432, "high_val_tuple": ("STRAWBERRY", "MILK", "WOOL"), "term_liq_step": 714}),
    ]
    
    results = []
    for name, cfg in configs:
        wr, md, wa, wb, ties = evaluate_config(name, cfg, n_seeds=15)
        results.append((name, wr, md, wa, wb, ties, cfg))
        
    print("\n" + "="*80)
    print("RANKED TUNING RESULTS (vs kaggle_boat84_v14)")
    print("="*80)
    for name, wr, md, wa, wb, ties, cfg in sorted(results, key=lambda x: (-x[1], -x[2])):
        print(f"  {name:<36} Win Rate: {wr:5.1f}% | Mean Delta: {md:+6.0f} | W-L-T: {wa:>2}-{wb:>2}-{ties}")
