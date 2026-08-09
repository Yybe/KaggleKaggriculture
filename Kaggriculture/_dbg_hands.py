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
    # Log at midday (h==12) so hands hired that morning are visible, and at
    # day boundary for money/shed deltas.
    if h == 12 and d != day:
        f = obs['farms'][0]
        priv = obs['private']
        n_m = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PLANT' and t['crop'] == 'MELON')
        n_w = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PLANT' and t['crop'] == 'WHEAT')
        n_s = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PLANT' and t['crop'] == 'STRAWBERRY')
        n_cow = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('animal') == 'COW')
        n_past = sum(1 for r in f['tiles'] for t in r if isinstance(t, dict) and t.get('kind') == 'PASTURE')
        summary.append(
            f"d{d:02d} h12: $={f['money']:.0f} m={n_m} w={n_w} s={n_s} cow={n_cow} "
            f"past={n_past} hands={len(f.get('hands', []))} "
            f"shed={dict((k, v) for k, v in priv['shed'].items() if v)} "
            f"seeds={dict((k, v) for k, v in priv['seeds'].items() if v)}")
        day = d
    return act


env.run([wrap, 'random'])
fin = env.steps[-1]
print('final:', fin[0].reward)
for line in summary:
    print(line)
