import sys, os
sys.path.insert(0, '.')
import agents_lib
from kaggle_environments import make

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_dbg_d7.log')
env = make('kaggriculture', configuration={'seed': 42}, debug=False)

def wrap(obs):
    day = obs['day']
    hour = obs['hour']
    with open(LOG, 'a') as f:
        f.write('obs day={} hour={}\n'.format(day, hour))
    if day == 7 and hour == 0:
        farm = obs['farms'][0]
        private = obs.get('private', {}) or {}
        shed = private.get('shed', {})
        seeds = private.get('seeds', {})
        n_hands = len(farm.get('hands', []))
        pl = []
        for row in farm['tiles']:
            for t in row:
                if isinstance(t, dict) and t.get('kind') == 'PLANT':
                    pl.append((t['crop'], t['planted_day'], t.get('yield_units'),
                               t.get('consecutive_unwatered'), t.get('watered_today'),
                               t.get('fertilized_until_day', -1)))
        with open(LOG, 'a') as f:
            f.write('DAY7 h=0 hands={} money={:.0f} shed={} seeds={}\n plants={}\n'.format(
                n_hands, farm['money'], dict(shed), dict(seeds), pl))
        inv0 = private.get('inventories', [{}])[0]
        sc = agents_lib._crop_choice_v8(day,
                                        sum(1 for c, *_ in pl if c == 'WHEAT'),
                                        sum(1 for c, *_ in pl if c == 'MELON'),
                                        sum(1 for c, *_ in pl if c == 'STRAWBERRY'),
                                        seeds.get('WHEAT', 0) > 0,
                                        seeds.get('MELON', 0) > 0,
                                        seeds.get('STRAWBERRY', 0) > 0)
        tasks = agents_lib._scan_tasks_v8(farm, private, day, hour, sc, inv0, shed,
                                          (1 + n_hands) * 12)
        from collections import Counter
        kinds = Counter(str(v[1]) for v in tasks.values())
        with open(LOG, 'a') as f:
            f.write(' seed_choice={} n_tasks={} kinds={}\n'.format(sc, len(tasks), dict(kinds)))
        fp = farm['farmer']
        act, _ = agents_lib._unit_action(farm, private, fp, tasks, set(), shed, inv0)
        with open(LOG, 'a') as f:
            f.write(' farmer@{} -> {}\n'.format(tuple(fp), act))
    return agents_lib.baseline_v8(obs)

if os.path.exists(LOG):
    os.remove(LOG)
env.run([wrap, 'random'])
print('final:', env.steps[-1][0].reward)
