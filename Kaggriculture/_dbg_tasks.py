import sys
sys.path.insert(0, '.')
import agents_lib
from kaggle_environments import make

env = make('kaggriculture', configuration={'seed': 42}, debug=False)
calls = 0

def wrap(obs):
    global calls
    calls += 1
    day = obs['day']
    hour = obs['hour']
    if day == 7 and hour < 6:
        farm = obs['farms'][0]
        private = obs.get('private', {}) or {}
        shed = private.get('shed', {})
        seeds = private.get('seeds', {})
        n_hands = len(farm.get('hands', []))
        # count plants & their state
        pl = []
        for row in farm['tiles']:
            for t in row:
                if isinstance(t, dict) and t.get('kind') == 'PLANT':
                    pl.append((t['crop'], t['planted_day'], t.get('yield_units'),
                               t.get('consecutive_unwatered'), t.get('watered_today'),
                               t.get('fertilized_until_day', -1)))
        print(f'DAY {day} h={hour} hands={n_hands} money={farm["money"]:.0f} shed={dict(shed)} seeds={dict(seeds)}')
        print(f'  plants={pl}')
        # what would the scan emit?
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
        print(f'  seed_choice={sc} n_tasks={len(tasks)} kinds={dict(kinds)}')
        fp = farm['farmer']
        act, _ = agents_lib._unit_action(farm, private, fp, tasks, set(), shed, inv0)
        print(f'  farmer@{tuple(fp)} -> {act}')
    return agents_lib.baseline_v8(obs)

env.run([wrap, 'random'])
print('final:', env.steps[-1][0].reward)
