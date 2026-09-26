"""E214 instrument: water headroom + animal feed/escape census on the cha22 stack.

The corrected top-vs-top fingerprint (LEDGER_20260926 §8) shows winners water +48
and feed +20 more than losers. This probe measures, per mirror day:
  * standing crop plants, WATER ops emitted, plants with consecutive_unwatered>=1
    (weed-risk tomorrow), and WEED tiles appearing that day,
  * FEED ops, standing animals, and animals that vanish day-over-day (escape),
so the next lever is sized from facts, not arithmetic.

usage: WybeV2/rank_env/Scripts/python.exe tools/e214_water_feed_census.py [seed ...]
"""
import importlib.util
import os
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))
from test_candidate_breakthrough import engine_pin_error  # noqa: E402
from kaggle_environments import make  # noqa: E402

CAND = os.path.join(BASE, "agents", "cha22_champion.py")


def load(path):
    spec = importlib.util.spec_from_file_location("cand_" + os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    pin = engine_pin_error()
    if pin:
        raise SystemExit(f"ENGINE PIN REFUSED: {pin}")
    seeds = [int(s) for s in sys.argv[1:]] or [1000000, 2000000]
    mod = load(CAND)
    for seed in seeds:
        water = [defaultdict(int) for _ in range(2)]
        feed = [defaultdict(int) for _ in range(2)]
        risk = [defaultdict(int) for _ in range(2)]
        weeds = [defaultdict(int) for _ in range(2)]
        plants = [defaultdict(int) for _ in range(2)]
        animals = [defaultdict(int) for _ in range(2)]

        def wrapped(seat):
            def agent(obs, cfg=None):
                day = int(obs["step"]) // 24
                a = mod.agent(obs, cfg)
                farm = obs["farms"][seat]
                n_p = n_r = n_a = 0
                for row in farm["tiles"]:
                    for tile in row:
                        if not isinstance(tile, dict):
                            continue
                        if tile.get("kind") == "PLANT":
                            n_p += 1
                            if int(tile.get("consecutive_unwatered", 0) or 0) >= 1 and not tile.get("watered_today"):
                                n_r += 1
                        elif "animal" in tile:
                            n_a += 1
                plants[seat][day] = max(plants[seat][day], n_p)
                risk[seat][day] = max(risk[seat][day], n_r)
                animals[seat][day] = max(animals[seat][day], n_a)
                for h in ([a.get("farmer")] if a.get("farmer") else []) + list(a.get("hands") or []):
                    if isinstance(h, list) and h:
                        if h[0] == "WATER":
                            water[seat][day] += 1
                        elif h[0] == "FEED":
                            feed[seat][day] += 1
                return a
            return agent

        env = make("kaggriculture", configuration={"seed": seed, "townCenterSellInterval": 24}, debug=True)
        prev_animals = [None, None]
        orig_step = env.step

        def counting_step(*args):
            acts = args[0] if args else None
            for seat in range(2):
                farm = env.state[seat].observation["farms"][seat]
                n_a = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and "animal" in t)
                if prev_animals[seat] is not None and n_a < prev_animals[seat]:
                    weeds[seat][int(env.state[0].observation["step"]) // 24] += prev_animals[seat] - n_a
                prev_animals[seat] = n_a
            return orig_step(acts)

        env.step = counting_step
        env.run([wrapped(0), wrapped(1)])
        print(f"== seed {seed}  rewards {[s.reward for s in env.state]}", flush=True)
        for seat in range(2):
            print(f" seat {seat}: day | plants max | weed-risk max | WATER | FEED | animals max | escapes", flush=True)
            for d in range(30):
                if plants[seat][d] or animals[seat][d]:
                    print(f"   d{d:02d} | {plants[seat][d]:3d} | {risk[seat][d]:3d} | {water[seat][d]:3d} | {feed[seat][d]:3d} | {animals[seat][d]:3d} | {weeds[seat][d]}", flush=True)
            print(f"  TOTALS water={sum(water[seat].values())} feed={sum(feed[seat].values())} escapes={sum(weeds[seat].values())}", flush=True)


if __name__ == "__main__":
    main()
