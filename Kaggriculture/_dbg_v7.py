from kaggle_environments import make
import agents_lib

env = make('kaggriculture', debug=False)
last_day = -1
summary = []


def stats(farm, priv):
    plants = sum(1 for r in farm['tiles'] for t in r
                 if isinstance(t, dict) and t.get('kind') == 'PLANT')
    weeds = sum(1 for r in farm['tiles'] for t in r
                if isinstance(t, dict) and t.get('kind') == 'WEED')
    geese = sum(1 for r in farm['tiles'] for t in r
                if isinstance(t, dict) and t.get('animal') == 'GOOSE')
    shed = {k: v for k, v in priv['shed'].items() if v > 0}
    return (f"m={farm['money']} p={plants} w={weeds} g={geese} h={len(farm['hands'])} "
            f"shed={shed}")


def wrap_v7(obs):
    global last_day
    day = obs['day']
    if day != last_day:
        last_day = day
        f = obs['farms'][0]
        p = obs.get('market', {}).get('prices', {})
        summary.append(f"d{day:02d} v7[{stats(f, obs['private'])}] "
                       f"v6[m={obs['farms'][1]['money']}] mel={p.get('MELON')} egg={p.get('EGG')}")
    return agents_lib.baseline_v7(obs)


env.run([wrap_v7, agents_lib.baseline])
for line in summary:
    print(line)
