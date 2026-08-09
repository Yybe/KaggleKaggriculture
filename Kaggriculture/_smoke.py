"""Smoke test: one game per regime for main.agent, reporting meta metrics."""
import json
import sys
import traceback

from kaggle_environments import make

import main

BANNED_PRODUCT_BUYS = {"FERTILIZER"}
BANNED_ANIMAL_BUYS = {"GOOSE"}
BANNED_SEED_BUYS = {"CARROT", "TOMATO"}
BANNED_FARMER_OPS = {"BUILD_COOP"}
MELON_DEADLINE_DAY = 12


def run_regime(interval, seed):
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed, "townCenterSellInterval": interval},
        debug=True,
    )
    recorded = {"forbidden": 0, "forbidden_detail": [], "melon_sells": {}, "farm_ops": {}}
    violations = []

    def agent_wrapper(obs, configuration=None):
        act = main.agent(obs, configuration)
        market = act.get("market") or []
        for order in market:
            if order and order[0] == "BUY_PRODUCT" and order[1] in BANNED_PRODUCT_BUYS:
                recorded["forbidden"] += 1
                recorded["forbidden_detail"].append(("BUY_PRODUCT", order, obs.get("day")))
            if order and order[0] == "BUY_ANIMAL" and order[1] in BANNED_ANIMAL_BUYS:
                recorded["forbidden"] += 1
                recorded["forbidden_detail"].append(("BUY_ANIMAL", order, obs.get("day")))
            if order and order[0] == "BUY_SEED" and order[1] in BANNED_SEED_BUYS:
                recorded["forbidden"] += 1
                recorded["forbidden_detail"].append(("BUY_SEED", order, obs.get("day")))
            if order and order[0] == "SELL" and order[1] == "MELON":
                day = obs.get("day", 0)
                recorded["melon_sells"][day] = recorded["melon_sells"].get(day, 0) + int(order[2])
        for op in [act.get("farmer", ["PASS"])[0], *[h[0] for h in (act.get("hands") or [])]]:
            recorded["farm_ops"][op] = recorded["farm_ops"].get(op, 0) + 1
            if op in BANNED_FARMER_OPS:
                recorded["forbidden"] += 1
                recorded["forbidden_detail"].append(("FARMER", op, obs.get("day")))
        return act

    try:
        env.run([agent_wrapper, "starter"])
    except Exception as e:
        traceback.print_exc()
        return {"interval": interval, "seed": seed, "error": str(e), "recorded": recorded}

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

    shed_melon = private.get("shed", {}).get("MELON", 0)
    melon_sold_by_12 = sum(v for d, v in recorded["melon_sells"].items() if d <= MELON_DEADLINE_DAY)
    melon_sold_total = sum(recorded["melon_sells"].values())

    result = {
        "interval": interval,
        "seed": seed,
        "reward": reward,
        "opponent_reward": opp_reward,
        "unlocked": list(farm["unlocked_quadrants"]),
        "animals_end": animals,
        "shed_melon_end": shed_melon,
        "melon_tiles_end": melon_tiles,
        "melon_sold_total": melon_sold_total,
        "melon_sold_by_day_12": melon_sold_by_12,
        "forbidden_count": recorded["forbidden"],
        "forbidden_detail": recorded["forbidden_detail"][:5],
        "top_farm_ops": sorted(recorded["farm_ops"].items(), key=lambda kv: -kv[1])[:8],
    }
    return result


if __name__ == "__main__":
    for interval in (12, 24):
        for seed in (42, 1337):
            r = run_regime(interval, seed)
            print(json.dumps(r, indent=2))
            print("-" * 60)
