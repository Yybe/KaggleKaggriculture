"""Debug: log momentum-gate decisions vs V15 on a seed."""
import importlib.util
import sys
import os

sys.path.insert(0, os.path.abspath("agents"))

spec = importlib.util.spec_from_file_location("v155", r"agents\kaggle_champion_v155.py")
mod155 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod155)
spec2 = importlib.util.spec_from_file_location("v15", r"agents\kaggle_champion_v15.py")
mod15 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(mod15)

from kaggle_environments import make

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 2584

log = []
orig_ok = mod155._price_momentum_ok


def spy(obs, item):
    r = orig_ok(obs, item)
    m = obs.get("market", {}) or {}
    px = m.get("prices", {}) or {}
    h = mod155._PRICE_HISTORY.get((obs.get("player"), item))
    hist = list(h) if h else []
    log.append(
        (obs.get("step"), obs.get("player"), item,
         px.get(item), r, hist[0] if hist else None, hist[-1] if hist else None)
    )
    return r


mod155._price_momentum_ok = spy

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": SEED}, debug=False)
env.run([mod155.agent, mod15.agent])

print(f"seed={SEED} final: player0={env.steps[-1][0].reward:.0f} player1={env.steps[-1][1].reward:.0f}")
print("gate decisions (player 0 = V15.5):")
for row in log:
    if row[0] >= 480 and row[1] == 0:
        mark = "FIRE" if row[4] else "HOLD"
        print(f"step={row[0]:>3} {row[2]:<11} cur={row[3]:>5} {mark} past16={row[5]} cur16={row[6]}")
