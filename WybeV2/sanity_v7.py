"""Sanity: WybeV2 v7 submission.py vs PASS on the 3 frozen sanity seeds."""
import os, sys, io
old_stderr = sys.stderr
sys.stderr = io.StringIO()
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from kaggle_environments import make
sys.stderr = old_stderr
import submission as vw

SEEDS = [1000000, 9000000, 3330000]

def pass_agent(obs, config=None):
    seat = obs.get("player", 0)
    farm = obs.get("farms", [{}])[seat]
    hands = farm.get("hands", []) or []
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in hands], "market": []}

rows = []
for seed in SEEDS:
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([vw.agent, pass_agent])
    state = env.state
    r0 = state[0].get("reward", 0) or 0
    r1 = state[1].get("reward", 0) or 0
    st0 = state[0].get("status", "")
    st1 = state[1].get("status", "")
    rows.append((seed, r0, r1, st0, st1))
    print(f"seed={seed:7d}  v7={r0:>9,.0f}  PASS={r1:>9,.0f}  margin={r0-r1:>+10,.0f}  "
          f"st0={st0}  st1={st1}", flush=True)

print("\nSUMMARY")
for seed, r0, r1, st0, st1 in rows:
    print(f"  seed={seed:7d}  v7={r0:>9,.0f}  PASS={r1:>9,.0f}  margin={r0-r1:>+10,.0f}")
