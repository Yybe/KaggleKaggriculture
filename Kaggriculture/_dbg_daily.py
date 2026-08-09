import sys, os
sys.path.insert(0, '.')
import agents_lib
from kaggle_environments import make

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_dbg_daily.log')
env = make('kaggriculture', configuration={'seed': 42}, debug=False)

def wrap(obs):
    day = obs['day']
    hour = obs['hour']
    if hour == 0:
        farm = obs['farms'][0]
        private = obs.get('private', {}) or {}
        shed = private.get('shed', {})
        seeds = private.get('seeds', {})
        n_hands = len(farm.get('hands', []))
        n_pastures = 0
        cows = sheep = melons = wheat = straw = 0
        for row in farm['tiles']:
            for t in row:
                if not isinstance(t, dict):
                    continue
                if t.get('kind') == 'PASTURE':
                    n_pastures += 1
                elif t.get('animal') == 'COW':
                    cows += 1
                elif t.get('animal') == 'SHEEP':
                    sheep += 1
                elif t.get('kind') == 'PLANT':
                    c = t['crop']
                    if c == 'MELON': melons += 1
                    elif c == 'WHEAT': wheat += 1
                    elif c == 'STRAWBERRY': straw += 1
        with open(LOG, 'a') as f:
            f.write('d{:02d} money={:>6.0f} hands={} cow={}+{} sheep={}+{} mel={} whe={} str={} past={} shedW={} fert={} seedM={} seedW={} seedS={}\n'.format(
                day, farm['money'], n_hands, cows, shed.get('COW', 0), sheep, shed.get('SHEEP', 0),
                melons, wheat, straw, n_pastures, shed.get('WHEAT', 0), shed.get('FERTILIZER', 0),
                seeds.get('MELON', 0), seeds.get('WHEAT', 0), seeds.get('STRAWBERRY', 0)))
    return agents_lib.baseline_v8(obs)

if os.path.exists(LOG):
    os.remove(LOG)
env.run([wrap, 'random'])
print('final:', env.steps[-1][0].reward)
