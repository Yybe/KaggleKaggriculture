"""E212 instrument: is the cha22 spine fert supply-limited or application-limited?

Plays champion-vs-champion mirrors via env.run with recorder-wrapped agents
(the agent call receives the proper observation with 'step'), recording per day:
FERTILIZE ops, COLLECT_FERTILIZER ops, and the max shed FERTILIZER stock seen
that day. High stock + flat applies = application-limited; stock ~0 = supply-
limited (axis dead for this chassis).

usage: WybeV2/rank_env/Scripts/python.exe tools/e212_fert_stock_probe.py [seed ...]
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
        recs = [defaultdict(lambda: [0, 0, 0]) for _ in range(2)]  # day -> [fert, collect, maxstock]

        def wrapped(seat):
            def agent(obs, cfg=None):
                day = int(obs["step"]) // 24
                a = mod.agent(obs, cfg)
                r = recs[seat][day]
                for h in ([a.get("farmer")] if a.get("farmer") else []) + list(a.get("hands") or []):
                    if isinstance(h, list) and h:
                        if h[0] == "FERTILIZE":
                            r[0] += 1
                        elif h[0] == "COLLECT_FERTILIZER":
                            r[1] += 1
                r[2] = max(r[2], int((obs.get("private") or {}).get("shed", {}).get("FERTILIZER", 0) or 0))
                return a
            return agent

        env = make("kaggriculture", configuration={"seed": seed, "townCenterSellInterval": 24}, debug=True)
        env.run([wrapped(0), wrapped(1)])
        print(f"== seed {seed}  rewards {[s.reward for s in env.state]}", flush=True)
        for seat in range(2):
            rows = [f"d{d}:{recs[seat][d][0]}/{recs[seat][d][1]}/{recs[seat][d][2]}" for d in range(30)]
            print(f" seat {seat} fert/collect/maxstock:", " ".join(rows), flush=True)


if __name__ == "__main__":
    main()
