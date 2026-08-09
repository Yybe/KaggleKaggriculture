from kaggle_environments import make
import agents_lib

env = make('kaggriculture', configuration={"seed": 42}, debug=False)
state = {'day': -1, 'counts': None}
summary = []


def wrap_v7(obs):
    d = obs['day']
    act = agents_lib.baseline_v7(obs)
    if d != state['day']:
        if state['counts']:
            summary.append(f"d{state['day']:02d}: {state['counts']}")
        state['day'] = d
        state['counts'] = {'won': 0, 'woff': 0, 'move': 0, 'pass': 0, 'other': 0,
                           'plant': 0, 'dig': 0, 'harvest': 0, 'fertilize': 0}
    f = obs['farms'][0]
    units = [f['farmer'], *f['hands']]
    acts = [act['farmer'], *act.get('hands', [])]
    for u, a in zip(units, acts):
        if not isinstance(a, list) or not a:
            state['counts']['pass'] += 1
            continue
        op = a[0]
        if op == 'WATER':
            t = f['tiles'][u[1]][u[0]]
            if isinstance(t, dict) and t.get('kind') == 'PLANT':
                state['counts']['won'] += 1
            else:
                state['counts']['woff'] += 1
        elif op in ('NORTH', 'SOUTH', 'EAST', 'WEST'):
            state['counts']['move'] += 1
        elif op == 'PASS':
            state['counts']['pass'] += 1
        elif op == 'PLANT':
            state['counts']['plant'] += 1
        elif op == 'DIG':
            state['counts']['dig'] += 1
        elif op == 'HARVEST':
            state['counts']['harvest'] += 1
        elif op == 'FERTILIZE':
            state['counts']['fertilize'] += 1
        else:
            state['counts']['other'] += 1
    return act


env.run([wrap_v7, agents_lib.baseline])
if state['counts']:
    summary.append(f"d{state['day']:02d}: {state['counts']}")
for line in summary:
    print(line)
