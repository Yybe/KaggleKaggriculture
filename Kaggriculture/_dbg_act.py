from kaggle_environments import make
import agents_lib
from collections import Counter

env = make('kaggriculture', configuration={'seed': 42}, debug=False)
actions = {}  # day -> Counter of farmer+hand actions


def wrap(obs):
    d = obs['day']
    act = agents_lib.baseline_v8(obs)
    if d not in actions:
        actions[d] = Counter()
    c = actions[d]
    fa = act.get('farmer', ['PASS'])
    c[fa[0] if isinstance(fa, list) and fa else 'PASS'] += 1
    for ha in act.get('hands', []):
        c[ha[0] if isinstance(ha, list) and ha else 'PASS'] += 1
    return act


env.run([wrap, 'random'])
fin = env.steps[-1]
print('final:', fin[0].reward)
for d in sorted(actions):
    c = actions[d]
    total = sum(c.values())
    top = ' '.join(f'{k}x{v}' for k, v in c.most_common(8))
    print(f'd{d:02d} n={total}: {top}')
