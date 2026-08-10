"""Extract daily farm macro-route snapshots for HS and SEB games."""
import json, glob

def load_entries(path):
    d = json.load(open(path))
    out = []
    for s in d['steps']:
        for p in s:
            out.append(p)
    return out

def farm_snapshot(entries, target_day):
    for e in entries:
        obs = e['observation']
        if obs['player'] == 0 and obs['day'] == target_day:
            f = obs['farms'][0]
            tiles = f['tiles']
            plants = {'WHEAT': 0, 'CARROT': 0, 'TOMATO': 0, 'STRAWBERRY': 0, 'MELON': 0}
            animals = {'COW': 0, 'SHEEP': 0, 'GOOSE': 0}
            pastures = coops = weeds = 0
            for row in tiles:
                for t in row:
                    if not isinstance(t, dict):
                        continue
                    k = t.get('kind')
                    if k == 'PLANT':
                        c = t.get('crop', '?')
                        plants[c] = plants.get(c, 0) + 1
                    elif k == 'ANIMAL':
                        a = t.get('animal')
                        if a:
                            animals[a] = animals.get(a, 0) + 1
                    elif k == 'PASTURE':
                        pastures += 1
                    elif k == 'COOP':
                        coops += 1
                    elif k == 'WEED':
                        weeds += 1
            private = obs['private']
            shed = private.get('shed', {})
            seeds = private.get('seeds', {})
            money = int(f.get('money', 0) or 0)
            return {
                'money': money,
                'hands': len(f.get('hands', []) or []),
                'quads': len(f.get('unlocked_quadrants', []) or []),
                'plants': plants,
                'animals': animals,
                'pastures': pastures,
                'coops': coops,
                'weeds': weeds,
                'shed_total': sum(v for v in shed.values() if isinstance(v, (int, float))),
                'seeds': {k: v for k, v in seeds.items() if v},
            }
    return None

for label, sub, gfile in [
    ('HEALTHSTONE best', 'healthstone', 'episode-91128753-replay.json'),
    ('SEB best-win', 'seb', 'episode-91192902-replay.json'),
]:
    entries = load_entries(r'C:\Users\xxshi\Desktop\farmmasterV2\replays_new\%s\%s' % (sub, gfile))
    print('=' * 20, label, '=' * 20)
    for day in [0, 1, 2, 5, 10, 15, 20, 25, 28, 29]:
        s = farm_snapshot(entries, day)
        if s:
            line = 'D%-2d money=%7d hands=%2d quads=%d plants=%s animals=%s pasture=%2d shed=%3d seeds=%s' % (
                day, s['money'], s['hands'], s['quads'], s['plants'], s['animals'],
                s['pastures'], s['shed_total'], s['seeds'])
            print(line)
    print()

# Average composition for HS across all 30 games at key days
print('=' * 20, 'HS AVERAGE (30 games)', '=' * 20)
hs_files = sorted(glob.glob(r'C:\Users\xxshi\Desktop\farmmasterV2\replays_new\healthstone\episode-*.json'))
from collections import defaultdict
agg = defaultdict(lambda: {'money': [], 'hands': [], 'quads': [], 'plants': defaultdict(list),
                           'animals': defaultdict(list), 'pastures': [], 'shed': []})
for f in hs_files:
    entries = load_entries(f)
    for day in [5, 10, 15, 20, 25, 29]:
        s = farm_snapshot(entries, day)
        if not s:
            continue
        a = agg[day]
        a['money'].append(s['money'])
        a['hands'].append(s['hands'])
        a['quads'].append(s['quads'])
        a['pastures'].append(s['pastures'])
        a['shed'].append(s['shed_total'])
        for c, n in s['plants'].items():
            a['plants'][c].append(n)
        for c, n in s['animals'].items():
            a['animals'][c].append(n)

for day in sorted(agg):
    a = agg[day]
    n = len(a['money'])
    def avg(lst):
        return sum(lst) / len(lst) if lst else 0
    plants = {c: round(avg(v), 1) for c, v in a['plants'].items() if v}
    animals = {c: round(avg(v), 1) for c, v in a['animals'].items() if v}
    print('D%-2d n=%2d money=%7d hands=%4.1f quads=%4.2f pasture=%4.1f shed=%5.1f plants=%s animals=%s' % (
        day, n, int(avg(a['money'])), avg(a['hands']), avg(a['quads']), avg(a['pastures']),
        avg(a['shed']), plants, animals))
