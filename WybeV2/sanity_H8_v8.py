"""H8 gate: submission_v8 (v6.3 crop engine + HS animal pipeline) vs PASS
on the 3 frozen sanity seeds. PASS = all 3 > 8,000 AND mean >= 21,173
(v6.3 mean, per PLAN_H8.md). Output also written to sanity_H8_v8.txt."""
import importlib.util, sys, io, os

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.agent

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = load_agent(os.path.join(HERE, "submission_v8.py"), "v8mod")

old_stderr = sys.stderr
sys.stderr = io.StringIO()
sys.path.insert(0, HERE)
from kaggle_environments import make
sys.stderr = old_stderr

SEEDS = [1000000, 9000000, 3330000]

def pass_agent(obs, config=None):
    seat = obs.get("player", 0)
    farm = obs.get("farms", [{}])[seat]
    hands = farm.get("hands", []) or []
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in hands], "market": []}

rows = []
for seed in SEEDS:
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([V8, pass_agent])
    state = env.state
    r0 = state[0].get("reward", 0) or 0
    r1 = state[1].get("reward", 0) or 0
    st0 = state[0].get("status", "")
    st1 = state[1].get("status", "")
    rows.append((seed, r0, r1, st0, st1))
    print(f"seed={seed:7d}  v8={r0:>9,.0f}  PASS={r1:>9,.0f}  margin={r0-r1:>+10,.0f}  "
          f"st0={st0}  st1={st1}", flush=True)

print("\nSUMMARY")
mean = 0
for seed, r0, r1, st0, st1 in rows:
    print(f"  seed={seed:7d}  v8={r0:>9,.0f}  PASS={r1:>9,.0f}  margin={r0-r1:>+10,.0f}")
    mean += r0
mean /= len(rows)
all_above_8000 = all(r0 > 8000 for _, r0, _, _, _ in rows)
print(f"  MEAN v8 = {mean:,.0f}  (v6.3 mean = 21,173)  all>8000 = {all_above_8000}")
print(f"  GATE PASS = {all_above_8000 and mean >= 21173}")
