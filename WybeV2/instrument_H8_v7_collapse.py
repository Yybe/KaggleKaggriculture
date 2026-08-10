"""H8 instrument: run CURRENT v7 (submission.py) vs PASS on seed 1000000.
Logs per-day: money, shed, animals placed/escaped, SELL/BUY market stream.
Purpose: verify WHY v7 collapses to ~29 (feed overspend? fert gate? misroute?)
before clean-building v8 from v6.3 + animals. [F] evidence for PLAN_H8.md."""
import os, sys, io
old_stderr = sys.stderr
sys.stderr = io.StringIO()
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from kaggle_environments import make
sys.stderr = old_stderr
import submission as vw

LOG = []
DAY = {}   # day -> dict of counters

def _snap(day, money, shed, animals, plants, weeds, seeds, markets, actions):
    shed_str = {k: int(v) for k, v in shed.items() if int(v or 0) > 0}
    seeds_str = {k: int(v) for k, v in seeds.items() if int(v or 0) > 0}
    s = (f"D{day:2d} ${money:>8,.0f} plants={plants} weeds={weeds} "
         f"animals={animals} shed={shed_str} seeds={seeds_str}")
    if markets:
        s += "  M=" + str(markets)
    LOG.append(s)

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
        LOG.append(f"EXC D{day}H{hour}: {e}")

    # tally actions
    d = DAY.setdefault(day, {"act": {}, "M": []})
    for act in [result.get("farmer")] + list(result.get("hands") or []):
        key = act[0] if isinstance(act, list) and act else "?"
        d["act"][key] = d["act"].get(key, 0) + 1
    for m in result.get("market") or []:
        if isinstance(m, (list, tuple)) and m:
            d["M"].append(list(m))

    if hour == 23:
        shed = dict(private.get("shed", {}) or {})
        seeds = dict(private.get("seeds", {}) or {})
        plants = weeds = animals = 0
        for row in farm.get("tiles", []):
            for c in row:
                if isinstance(c, dict):
                    k = c.get("kind", "")
                    if k == "PLANT": plants += 1
                    elif k == "WEED": weeds += 1
                    elif k in ("PASTURE", "COOP") and c.get("animal"):
                        animals += 1
        m_stream = d["M"]
        # summarize: totals per item
        from collections import Counter
        buy = Counter(); sell = Counter(); hire = Counter()
        for m in m_stream:
            if m[0] == "HIRE": hire["HIRE"] += 1
            elif m[0] == "SELL": sell[m[1]] += int(m[2])
            elif m[0] in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT"): buy[f"{m[0]}_{m[1]}"] += int(m[2])
            elif m[0] == "BUY_LAND": buy["BUY_LAND"] += 1
        ms = []
        if buy: ms.append("BUY=" + dict(buy).__str__())
        if sell: ms.append("SELL=" + dict(sell).__str__())
        if hire: ms.append("HIRE=" + str(hire["HIRE"]))
        _snap(day, farm.get("money", 0), shed, animals, plants, weeds, seeds, ms, d["act"])

    return result

def pass_agent(obs, config=None):
    seat = obs.get("player", 0)
    farm = obs.get("farms", [{}])[seat]
    hands = farm.get("hands", []) or []
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in hands], "market": []}

sys.stderr = io.StringIO()
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000000}, debug=False)
env.run([debug_agent, pass_agent])
sys.stderr = old_stderr

state = env.state
r0 = state[0].get("reward", 0) or 0
r1 = state[1].get("reward", 0) or 0
LOG.append(f"\nFINAL: v7(current)={r0:,.0f} vs PASS={r1:,.0f}")

out = "\n".join(LOG)
print(out)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "inst_H8_v7_collapse.txt"), "w") as f:
    f.write(out)
