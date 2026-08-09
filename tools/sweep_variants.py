"""Sweep script to test different V14 enhancement variants against the original V14."""
import os
import sys
import copy
import time
import statistics
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath('agents'))
sys.path.insert(0, os.path.abspath('Kaggriculture'))

import kaggle_boat84_v14 as _v14

# Base components from V14
_ACTIONS = _v14._ACTIONS
_HIGH_VALUE = ("STRAWBERRY", "MILK", "WOOL", "MELON")
_NON_ONGOING_MAX = {"WHEAT": 6, "CARROT": 4, "MELON": 6}
_ONGOING = {"TOMATO", "STRAWBERRY"}

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
_preempt_shift = _v14._preempt_shift
_tile_at = _v14._tile_at
_weed_repair_action = _v14._weed_repair_action
_rank_sell_slots = _v14._rank_sell_slots
_terminal_liquidation = _v14._terminal_liquidation


def run_variant_agent(obs, config):
    idle_fill_mode = config.get("idle_fill_mode", "safe")
    capsell_step = config.get("capsell_step", 456)
    bump_cap = config.get("bump_cap", 2)
    bump_items = config.get("bump_items", _HIGH_VALUE)

    def idle_fill(obs, action, step):
        if idle_fill_mode == "none":
            return action
        seat = _seat(obs)
        farm = _farm(obs, seat)
        private = _get(obs, "private", {}) or {}
        inventories = list(_get(private, "inventories", []) or [])
        positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
        units = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]

        for index, (position, planned) in enumerate(zip(positions, units)):
            if not planned or planned[0] != "PASS":
                continue
            tile = _tile_at(farm, position)
            if not isinstance(tile, dict):
                continue
            inv = inventories[index] if index < len(inventories) else {}
            kind = tile.get("kind")

            if kind == "PLANT":
                crop = tile.get("crop")
                yield_units = int(tile.get("yield_units", 0) or 0)
                if crop in _NON_ONGOING_MAX:
                    if yield_units >= _NON_ONGOING_MAX[crop]:
                        units[index] = ["HARVEST"]
                    elif not tile.get("watered_today", False):
                        units[index] = ["WATER"]
                elif crop in _ONGOING:
                    if yield_units > 0:
                        units[index] = ["HARVEST"]
                    elif not tile.get("watered_today", False):
                        units[index] = ["WATER"]
            elif "animal" in tile and idle_fill_mode == "full":
                yield_units = int(tile.get("yield_units", 0) or 0)
                if yield_units > 0:
                    units[index] = ["HARVEST"]
                elif tile.get("consecutive_unfed", 0) >= 1 and not tile.get("fed_today", False) and inv.get("WHEAT", 0) > 0:
                    units[index] = ["FEED", "WHEAT"]
                elif tile.get("fertilizer_available", False):
                    units[index] = ["COLLECT_FERTILIZER"]
                elif not tile.get("cared_today", False):
                    units[index] = ["CARE"]

        action["farmer"] = units[0] if units else ["PASS"]
        action["hands"] = units[1:]
        return action

    def capselllate(obs, action, step):
        if step < capsell_step or step >= 716:
            return action
        action = _copy_action(action)
        private = _get(obs, "private", {}) or {}
        shed = dict(_get(private, "shed", {}) or {})
        market = list(action.get("market") or [])
        
        for order in market:
            if len(order) >= 3 and order[0] == "SELL" and order[1] in bump_items:
                item = order[1]
                planned_qty = max(0, int(order[2]))
                available = max(0, int(shed.get(item, 0) or 0))
                surplus = available - planned_qty
                if surplus > 0:
                    bump = min(surplus, bump_cap)
                    order[2] = planned_qty + bump
                    shed[item] = max(0, available - (planned_qty + bump))
        action["market"] = market
        return action

    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        action = idle_fill(obs, action, step)
        action = _repay_shift(obs, action, step)
        action = _rank_sell_slots(obs, action, None)
        action = _preempt_shift(obs, action, step)
        action = capselllate(obs, action, step)
        action = _terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])], "market": []}


def play_eval_game(args):
    config, seed, swap = args
    from kaggle_environments import make
    
    agent_a = lambda obs, configuration=None: run_variant_agent(obs, config)
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


def evaluate_agent(name, config, n_seeds=15, workers=14):
    t0 = time.perf_counter()
    tasks = []
    for s in range(n_seeds):
        seed = 1000 + s * 43
        tasks.append((config, seed, False))
        tasks.append((config, seed, True))
    
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(play_eval_game, tasks):
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
    print(f"[{name}] {len(ok)} games: Win={wins_a} ({win_rate:.1f}%), Loss={wins_b}, Tie={ties} | Mean Delta={mean_delta:+.0f} | Avg A={statistics.mean(scores_a):.0f} vs B={statistics.mean(scores_b):.0f} ({dt:.1f}s)")
    return win_rate, mean_delta, wins_a, wins_b, ties


if __name__ == '__main__':
    print("Starting parameter sweep vs V14 (kaggle_boat84_v14)...")
    
    variants = [
        ("V1: Idle Fill Only (safe)", {"idle_fill_mode": "safe", "capsell_step": 999}),
        ("V2: Idle Fill Only (full)", {"idle_fill_mode": "full", "capsell_step": 999}),
        ("V3: Capselllate Only (+2, >=456)", {"idle_fill_mode": "none", "capsell_step": 456, "bump_cap": 2}),
        ("V4: Capselllate Only (+1, >=456)", {"idle_fill_mode": "none", "capsell_step": 456, "bump_cap": 1}),
        ("V5: Capselllate Only (+3, >=456)", {"idle_fill_mode": "none", "capsell_step": 456, "bump_cap": 3}),
        ("V6: Capselllate (+2, >=380)", {"idle_fill_mode": "none", "capsell_step": 380, "bump_cap": 2}),
        ("V7: Capselllate (+2, >=500)", {"idle_fill_mode": "none", "capsell_step": 500, "bump_cap": 2}),
        ("V8: Combined (safe fill + +1 late)", {"idle_fill_mode": "safe", "capsell_step": 456, "bump_cap": 1}),
        ("V9: Combined (safe fill + +2 late)", {"idle_fill_mode": "safe", "capsell_step": 456, "bump_cap": 2}),
        ("V10: Combined (full fill + +1 late)", {"idle_fill_mode": "full", "capsell_step": 456, "bump_cap": 1}),
        ("V11: Combined (full fill + +2 late)", {"idle_fill_mode": "full", "capsell_step": 456, "bump_cap": 2}),
    ]
    
    results_table = []
    for name, cfg in variants:
        wr, md, wa, wb, ties = evaluate_agent(name, cfg, n_seeds=10)
        results_table.append((name, wr, md, wa, wb, ties))
    
    print("\n" + "="*80)
    print("SWEEP RESULTS SUMMARY")
    print("="*80)
    for name, wr, md, wa, wb, ties in sorted(results_table, key=lambda x: (-x[1], -x[2])):
        print(f"  {name:<40} Win Rate: {wr:5.1f}% | Delta: {md:+6.0f} | W-L-T: {wa}-{wb}-{ties}")
