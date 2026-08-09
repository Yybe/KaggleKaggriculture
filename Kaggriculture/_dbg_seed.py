import sys
sys.path.insert(0, '.')
import agents_lib
from kaggle_environments import make

# Fresh env per run, identical seed 42. Is the env truly deterministic?
for i in range(4):
    env = make('kaggriculture', configuration={'seed': 42}, debug=False)
    env.run([agents_lib.baseline_v8, 'random'])
    r = env.steps[-1][0].reward
    print('run{}: seed={} reward={}'.format(i, env.info.get('seed'), r))
