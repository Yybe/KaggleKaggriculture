import sys
from kaggle_environments import make
from agents_lib import baseline

env = make("kaggriculture", debug=False)

events = {"planted": 0, "harvested": 0, "sold": {}, "died_weed": 0}

def wrap(obs):
    global events
    return baseline(obs)

env.run([wrap, "random"])
fin = env.steps[-1]
obs = fin[0].observation
farms = obs["farms"]
farm = farms[0]
priv = obs["private"]
print("=" * 60)
print(f"FINAL: money={farm['money']:.0f}  status={fin[0].status}")
print(f"day={obs['day']} hour={obs['hour']}  unlocked={farm['unlocked_quadrants']}")
print(f"hands={len(farm['hands'])} hires_today={farm['hires_today']}")
print(f"shed={priv['shed']}")
print(f"seeds={priv['seeds']}")
print(f"inventories={priv['inventories']}")
print(f"prices={dict(obs['market']['prices'])}")
print(f"town shops={obs['town']['unlocked_shops']}")
print("board:")
for row in farm["tiles"]:
    line = []
    for t in row:
        if t is None:
            line.append(".")
        elif t == "LOCKED":
            line.append("#")
        elif isinstance(t, dict):
            k = t.get("kind")
            if k == "WEED":
                line.append("x")
            elif k == "PLANT":
                c = t["crop"][0]
                w = "w" if t["watered_today"] else "-"
                cu = t["consecutive_unwatered"]
                line.append(f"{c}{w}{cu}")
            elif "animal" in t:
                line.append(t["animal"][0].upper())
            elif k == "COOP":
                line.append("C")
            elif k == "PASTURE":
                line.append("P")
            else:
                line.append("?")
        else:
            line.append("?")
    print("  " + " ".join(line))
