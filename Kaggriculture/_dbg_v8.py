from kaggle_environments import make
import agents_lib

env = make('kaggriculture', configuration={'seed': 42}, debug=False)
day = -1
summary = []


def wrap(obs):
    global day
    d = obs['day']
    h = obs.get('hour', 0)
    act = agents_lib.baseline_v8(obs)
    if d != day:
        if day >= 0:
            f = obs['farms'][0]
            priv = obs['private']
            n_m = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PLANT' and t['crop'] == 'MELON')
            n_w = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PLANT' and t['crop'] == 'WHEAT')
            n_s = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PLANT' and t['crop'] == 'STRAWBERRY')
            n_cow = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('animal') == 'COW')
            n_sheep = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('animal') == 'SHEEP')
            n_past = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PASTURE')
            n_free = sum(1 for r in f['tiles'] for t in r if t is None)
            prices = (obs.get('market', {}) or {}).get('prices', {})
            summary.append(
                f"d{day:02d} h={h:02d}: $={f['money']:.0f} m={n_m} w={n_w} s={n_s} "
                f"cow={n_cow} shp={n_sheep} past={n_past} free={n_free} "
                f"hands={len(f.get('hands', []))} "
                f"pMEL={prices.get('MELON', '?')} pSTR={prices.get('STRAWBERRY', '?')} "
                f"pMILK={prices.get('MILK', '?')} pWHE={prices.get('WHEAT', '?')} "
                f"shed={dict((k, v) for k, v in priv['shed'].items() if v)} "
                f"seeds={dict((k, v) for k, v in priv['seeds'].items() if v)} "
                f"mkt={act.get('market', [])}")
        day = d
    return act


env.run([wrap, 'random'])
fin = env.steps[-1]
print('final:', fin[0].reward)
for line in summary:
    print(line)
