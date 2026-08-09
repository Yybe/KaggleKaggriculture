import sys, os
sys.path.insert(0, '.')
import agents_lib
from kaggle_environments import make

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_dbg_mkt.log')
env = make('kaggriculture', configuration={'seed': 42}, debug=False)

def wrap(obs):
    day = obs['day']
    hour = obs['hour']
    act = agents_lib.baseline_v8(obs)
    if hour == 0:
        with open(LOG, 'a') as f:
            f.write('d{:02d} mkt={}\n'.format(day, act.get('market')))
    return act

if os.path.exists(LOG):
    os.remove(LOG)
env.run([wrap, 'random'])
print('final:', env.steps[-1][0].reward)
