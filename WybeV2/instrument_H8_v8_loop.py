"""H8 loop check: verify the animal pipeline actually engaged on seed 1000000.
Records per-day money, animal/feed market orders, FERT/WOOL sells, and field
pasture count. Output -> inst_H8_v8_loop.txt"""
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

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000000}, debug=False)
env.run([V8, lambda obs, config=None: {"farmer": ["PASS"], "hands": [["PASS"] for _ in (obs.get("farms", [{}])[obs.get("player", 0)].get("hands", []) or [])], "market": []}])

print("step day hour money | market orders | shed | pastures")
prev_day = -1
for i, (s0, _) in enumerate(env.steps):
    obs = s0["observation"]
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    if day != prev_day:
        prev_day = day
        p = obs.get("private", {}) or {}
        shed = p.get("shed", {}) or {}
        f = (obs.get("farms", [{}])[obs.get("player", 0)])
        money = f.get("money", 0)
        tiles = f.get("tiles", [])
        pastures = sum(1 for row in tiles for c in row
                       if isinstance(c, dict) and c.get("kind") == "PASTURE" and c.get("animal"))
        shed_s = {k: v for k, v in shed.items() if v and k in ("COW", "SHEEP", "GOOSE", "WHEAT", "FERTILIZER", "WOOL")}
        print(f"S{i:3d} D{day}:H{hour:02d} ${int(money):>6} | shed={shed_s} | pastures={pastures}", flush=True)

# Market-order tally (v8 seat is index 0)
from collections import Counter
cnt = Counter()
for i, (s0, _) in enumerate(env.steps):
    a0 = s0["action"]
    for m in (a0 or {}).get("market", []) or []:
        if m:
            cnt[tuple(m[:2]) if len(m) >= 2 else tuple(m)] += m[2] if len(m) >= 3 else 1
print("\nMARKET TALLY (v8 seat):")
for k, v in sorted(cnt.items()):
    print(f"  {k}: {v}")

print("\nreward:", env.state[0].get("reward"))
