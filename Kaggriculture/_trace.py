from kaggle_environments import make
from agents_lib import baseline_v7, melon_maxxer

env = make("kaggriculture", debug=False)

last_day = -1
summary = []
m_obs = {}


def _stats(obs, player):
    farm = obs["farms"][player]
    priv = obs["private"]
    plants = sum(1 for r in farm["tiles"] for t in r
                 if isinstance(t, dict) and t.get("kind") == "PLANT")
    weeds = sum(1 for r in farm["tiles"] for t in r
                if isinstance(t, dict) and t.get("kind") == "WEED")
    animals = sum(1 for r in farm["tiles"] for t in r
                  if isinstance(t, dict) and "animal" in t)
    shed = {k: v for k, v in priv["shed"].items() if v > 0}
    seeds = {k: v for k, v in priv["seeds"].items() if v > 0}
    return (f"m={farm['money']:5.0f} p={plants:2d} w={weeds:1d} a={animals} "
            f"shed={shed} seeds={seeds} hands={len(farm['hands'])}")


def wrap(obs):
    global last_day
    day = obs["day"]
    if day != last_day:
        last_day = day
        m = m_obs.get("private", {})
        mpriv = m.get("shed", {})
        mseeds = m.get("seeds", {})
        mf = obs["farms"][1]
        mstat = (f"m={mf['money']:5.0f} p={sum(1 for r in mf['tiles'] for t in r if isinstance(t, dict) and t.get('kind')=='PLANT'):2d} "
                 f"a={sum(1 for r in mf['tiles'] for t in r if isinstance(t, dict) and 'animal' in t)} "
                 f"shed={ {k: v for k, v in mpriv.items() if v > 0} } "
                 f"seeds={ {k: v for k, v in mseeds.items() if v > 0} }")
        summary.append(f"d{day:02d} B[{_stats(obs, 0)}] M[{mstat}]")
    return baseline_v7(obs)


def wrap_m(obs):
    m_obs["private"] = obs["private"]
    return melon_maxxer(obs)


env.run([wrap, wrap_m])
for line in summary:
    print(line)
