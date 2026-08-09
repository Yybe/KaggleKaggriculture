import sys
sys.path.insert(0, '.')
import agents_lib
from kaggle_environments import make

# Deterministic no-op opponent: does OUR reward become stable?
def noop(obs):
    return {"farmer": ["PASS"], "hands": []}

for i in range(4):
    env = make('kaggriculture', configuration={'seed': 42}, debug=False)
    env.run([agents_lib.baseline_v8, noop])
    r = env.steps[-1][0].reward
    print('run{}: seed={} reward={}'.format(i, env.info.get('seed'), r))
