"""Diagnose v6 collapse: daily snapshots + per-day action tallies + money curve."""
import os, sys, io
old_stderr = sys.stderr
sys.stderr = io.StringIO()
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from kaggle_environments import make
sys.stderr = old_stderr
import submission as vw

LOG = []
ACTION_TALLY = {}   # day -> Counter of unit actions
DAY_END = {}        # day -> (money, plants, weeds, empty, shed_wheat, shed_str)

def debug_agent(obs, config=None):
    step = obs.get("step", -1)
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    seat = obs.get("player", 0)
    farm = obs.get("farms", [{}])[seat]
    private = obs.get("private", {}) or {}

    try:
        result = vw.agent(obs, config)
    except Exception as e:
        hands = farm.get("hands", []) or []
        result = {"farmer": ["PASS"], "hands": [["PASS"] for _ in hands], "market": []}
        LOG.append(f"EXC day{day}h{hour}: {e}")

    # tally actions
    d = ACTION_TALLY.setdefault(day, {})
    for act in [result.get("farmer")] + list(result.get("hands") or []):
        key = act[0] if isinstance(act, list) and act else "?"
        d[key] = d.get(key, 0) + 1
    d["_M"] = d.get("_M", 0) + len(result.get("market") or [])

    # end-of-day snapshot (hour 23)
    if hour == 23:
        shed = dict(private.get("shed", {}) or {})
        seeds = dict(private.get("seeds", {}) or {})
        plants = weeds = empty = 0
        crops = {}
        for row in farm.get("tiles", []):
            for c in row:
                if c is None: empty += 1
                elif isinstance(c, dict):
                    k = c.get("kind", "")
                    if k == "PLANT":
                        plants += 1
                        cr = c.get("crop", "?")
                        crops[cr] = crops.get(cr, 0) + 1
                    elif k == "WEED": weeds += 1
        LOG.append(f"D{day:2d}E ${farm.get('money',0):>8,.0f} plants={plants}({crops}) "
                   f"weeds={weeds} empty={empty} shedW={int(shed.get('WHEAT',0))} "
                   f"shedSTR={int(shed.get('STRAWBERRY',0))} shedTOT={sum(shed.values())} "
                   f"seeds={dict(seeds)}")
        LOG.append(f"    actions={dict(sorted(d.items()))}")

    # hourly money curve days 19-29
    if 19 <= day <= 29 and hour in (0, 6, 12, 18, 23):
        pass  # covered by daily log; keep light

    return result

def pass_agent(obs, config=None):
    seat = obs.get("player", 0)
    farm = obs.get("farms", [{}])[seat]
    hands = farm.get("hands", []) or []
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in hands], "market": []}

sys.stderr = io.StringIO()
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
env.run([debug_agent, pass_agent])
sys.stderr = old_stderr

state = env.state
r0 = state[0].get("reward", 0)
r1 = state[1].get("reward", 0)
LOG.append(f"\nFINAL: VersionWybe={r0:,.0f} vs PASS={r1:,.0f}")

output = "\n".join(LOG)
print(output)
with open(os.path.join(os.path.dirname(__file__), "debug_v6_collapse.txt"), "w") as f:
    f.write(output)
