"""Evaluate the winning Cap+1 variants across 50 paired games (25 seeds x 2 seats) vs V14."""
import os
import sys
import time
import statistics
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath('agents'))
sys.path.insert(0, os.path.abspath('Kaggriculture'))

import kaggle_boat84_v14 as _v14

_ACTIONS = _v14._ACTIONS
_NON_ONGOING_MAX = {"WHEAT": 6, "CARROT": 4, "MELON": 6}
_HIGH_VALUE = ("STRAWBERRY", "MILK", "WOOL")

_get = _v14._get
_copy_action = _v14._copy_action
_seat = _v14._seat
_farm = _v14._farm
_align_hands = _v14._align_hands
_shift_state = _v14._shift_state
_repay_shift = _v14._repay_shift
_preempt_shift = _v14._preempt_shift
_tile_at = _v14._tile_at
_weed_repair_action = _v14._weed_repair_action
_rank_sell_slots = _v14._rank_sell_slots
_terminal_liquidation = _v14._terminal_liquidation

def create_candidate(bump_cap=1, latefill_step=456, with_fill=True):
    def _fill(action, obs):
        if not with_fill:
            return action
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

    def _topup(action, obs):
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
                if item in _HIGH_VALUE:
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

    def agent(obs, configuration=None):
        try:
            step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
            action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
            action = _fill(action, obs)
            action = _repay_shift(obs, action, step)
            action = _rank_sell_slots(obs, action, None)
            action = _preempt_shift(obs, action, step)
            action = _topup(action, obs)
            action = _terminal_liquidation(obs, action, step)
            return _align_hands(action, obs)
        except Exception:
            farm = _farm(obs, _seat(obs))
            return {
                "farmer": ["PASS"],
                "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
                "market": [],
            }
    return agent


def play_match_candidate(args):
    cfg, seed, swap = args
    from kaggle_environments import make
    agent_a = create_candidate(**cfg)
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


def evaluate_candidate(name, cfg, n_seeds=25, workers=14):
    t0 = time.perf_counter()
    tasks = []
    for s in range(n_seeds):
        seed = 5000 + s * 97
        tasks.append((cfg, seed, False))
        tasks.append((cfg, seed, True))
    
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(play_match_candidate, tasks):
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
    med_delta = statistics.median(deltas) if deltas else 0
    print(f"[{name:<32}] {len(ok)} games: Win={wins_a:>2} ({win_rate:5.1f}%), Loss={wins_b:>2}, Tie={ties} | Mean Delta={mean_delta:+6.0f} | Median Delta={med_delta:+6.0f} ({dt:.1f}s)")
    return win_rate, mean_delta, wins_a, wins_b, ties


if __name__ == '__main__':
    print("Running 50-game verification runs for top Cap+1 variants (25 seeds x 2 seats)...")
    
    candidates = [
        ("Candidate A: Cap+1, step 456, with_fill", {"bump_cap": 1, "latefill_step": 456, "with_fill": True}),
        ("Candidate B: Cap+1, step 480, with_fill", {"bump_cap": 1, "latefill_step": 480, "with_fill": True}),
        ("Candidate C: Cap+1, step 432, with_fill", {"bump_cap": 1, "latefill_step": 432, "with_fill": True}),
        ("Candidate D: Cap+1, step 456, no_fill",   {"bump_cap": 1, "latefill_step": 456, "with_fill": False}),
        ("Candidate E: Cap+2, step 480, with_fill", {"bump_cap": 2, "latefill_step": 480, "with_fill": True}),
    ]
    
    for name, cfg in candidates:
        evaluate_candidate(name, cfg, n_seeds=25)
