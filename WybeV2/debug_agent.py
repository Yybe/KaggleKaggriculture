"""Debug v3: Run against PASS opponent, log key steps."""
import os, sys, io, traceback
old_stderr = sys.stderr
sys.stderr = io.StringIO()
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from kaggle_environments import make
sys.stderr = old_stderr
import submission as vw

LOG = []
def debug_agent(obs, config=None):
    step = obs.get("step", -1)
    show = step <= 3 or step in (23, 24, 25, 47, 48, 72, 96, 120, 200, 480, 700, 718)
    seat = obs.get("player", 0)
    farm = obs.get("farms", [{}])[seat]
    private = obs.get("private", {}) or {}

    if show:
        shed = dict(private.get("shed", {}) or {})
        seeds = dict(private.get("seeds", {}) or {})
        money = farm.get("money", 0)
        nh = len(farm.get("hands", []) or [])
        fpos = farm.get("farmer", [0,0])
        hpos = farm.get("hands", [])
        # Count tiles
        plants = weeds = pastures = animals = empty = 0
        for row in farm.get("tiles", []):
            for c in row:
                if c is None: empty += 1
                elif isinstance(c, dict):
                    k = c.get("kind","")
                    if k == "PLANT": plants += 1
                    elif k == "WEED": weeds += 1
                    elif k in ("PASTURE","COOP"):
                        if "animal" in c: animals += 1
                        else: pastures += 1
        shed_items = {k:v for k,v in shed.items() if v > 0}
        seed_items = {k:v for k,v in seeds.items() if v > 0}
        LOG.append(f"S{step:3d} D{obs.get('day',0)}H{obs.get('hour',0):02d} "
                   f"${money:>8,.0f} hands={nh} farmer={fpos} "
                   f"plants={plants} weeds={weeds} pastures={pastures} animals={animals} empty={empty} "
                   f"shed={shed_items} seeds={seed_items}")

    try:
        result = vw.agent(obs, config)
        if show:
            LOG.append(f"  -> F={result.get('farmer')} H={result.get('hands')} M={result.get('market')}")
        return result
    except Exception as e:
        LOG.append(f"  EXCEPTION: {e}")
        LOG.append(traceback.format_exc())
        hands = farm.get("hands", []) or []
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in hands], "market": []}

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
LOG.append(f"\nFINAL: VersionWybe={r0:,.0f} vs PASS={r1:,.0f} (target: >3000)")
LOG.append(f"Status: {state[0].get('status')} vs {state[1].get('status')}")

output = "\n".join(LOG)
print(output)
with open(os.path.join(os.path.dirname(__file__), "debug_v3_output.txt"), "w") as f:
    f.write(output)
