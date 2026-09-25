"""E125 feed discipline: winners vs champion on the engine's animal-famine law.

Engine (`kaggriculture.py:805-833`, `_daily_refresh_animals`): an animal tile fed on 0 days gets
`consecutive_unfed += 1`, and at `>= 2` the animal **escapes** (tile becomes a bare structure); the
care bonus is only consumed on a *fed* production day (`:826`), and `FEED` costs 1 WHEAT from the
acting unit's carry and is capped at once per animal per day (`:505-513`). So animal output is
governed by feed discipline, not by tending effort.

This tool counts, per seat-game: animal tile-days, how many were fed, how many sat at
`consecutive_unfed >= 1`, escapes, and the units actually collected from animal tiles - for the live
winner tapes and the champion's own games through one code path.

usage: python tools/e125_feed_discipline.py replays <glob> [max_n]
       python tools/e125_feed_discipline.py local   <agent.py> <vs.py|self> seed1 seed2 ...
"""
import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e118_dna_gap import load_agent, raw  # noqa: E402

import kaggle_environments  # noqa: E402
assert kaggle_environments.__version__ == '1.32.7', kaggle_environments.__version__


def flat(farm):
    out = []
    for y, row in enumerate((farm or {}).get('tiles') or []):
        if not isinstance(row, list):
            continue
        for x, t in enumerate(row):
            out.append(((x, y), t if isinstance(t, dict) else {}))
    return out


def seat_feed(steps, seat):
    prev = None
    c = Counter()
    for i in range(len(steps)):
        try:
            e = raw(steps[i][seat])
        except (TypeError, IndexError, KeyError):
            break
        obs = raw(e.get('observation')) or {}
        farms = raw(obs.get('farms')) or []
        if not (isinstance(farms, list) and len(farms) > seat):
            continue
        tiles = dict(flat(farms[seat]))
        a = raw(e.get('action')) or {}
        if not isinstance(a, dict):
            a = {}
        ops = [raw(a.get('farmer'))] + [raw(o) for o in (a.get('hands') or [])]
        fed_here = care_here = 0
        for op in ops:
            if op and op[0] == 'FEED':
                fed_here += 1
            elif op and op[0] == 'CARE':
                care_here += 1
        c['feed_ops'] += fed_here
        c['care_ops'] += care_here
        n_an = n_fed = n_unf1 = n_unf2 = 0
        units = 0
        for pos, t in tiles.items():
            an = t.get('animal')
            if not an:
                if prev is not None and prev.get(pos, {}).get('animal') and \
                        prev.get(pos, {}).get('kind') == t.get('kind'):
                    c['escapes'] += 1        # same structure, animal gone
                continue
            n_an += 1
            if t.get('fed_today'):
                n_fed += 1
            u = int(t.get('consecutive_unfed') or 0)
            if u == 1:
                n_unf1 += 1
            elif u >= 2:
                n_unf2 += 1
            units += int(t.get('yield_units') or 0)
        c['animal_td'] += n_an
        c['fed_td'] += n_fed
        c['unfed1_td'] += n_unf1
        c['unfed2_td'] += n_unf2
        c['pending_units'] += units
        prev = tiles
    fin = steps[-1] if steps else None
    last = raw(fin[seat]) if isinstance(fin, (list, tuple)) and len(fin) > seat else {}
    lf = raw((raw(last.get('observation')) or {}).get('farms')) or []
    c['money'] = (lf[seat].get('money') or 0) if isinstance(lf, list) and len(lf) > seat else 0
    c['reward'] = (last or {}).get('reward') or 0
    return dict(c)


def agg(rows, label):
    n = len(rows) or 1
    g = lambda k: sum(r.get(k, 0) for r in rows) / n
    a = {'label': label, 'n': len(rows), 'money': g('money'), 'animal_td': g('animal_td'),
         'fed_td': g('fed_td'), 'unfed1_td': g('unfed1_td'), 'unfed2_td': g('unfed2_td'),
         'escapes': g('escapes'), 'feed_ops': g('feed_ops'), 'care_ops': g('care_ops'),
         'pending_units': g('pending_units')}
    a['fed%'] = 100.0 * a['fed_td'] / max(1, a['animal_td'])
    a['care_per_animal_td'] = a['care_ops'] / max(1, a['animal_td'])
    return a


def show(labels):
    names = list(labels)
    keys = ['n', 'money', 'animal_td', 'fed_td', 'fed%', 'unfed1_td', 'unfed2_td', 'escapes',
            'feed_ops', 'care_ops', 'care_per_animal_td', 'pending_units']
    print('%-20s' % 'field', ''.join('%14s' % x for x in names))
    for k in keys:
        print('%-20s' % k, ''.join('%14.1f' % labels[n][k] for n in names))


def run_replays(pattern, max_n):
    rows = []
    for path in sorted(glob.glob(pattern))[:max_n]:
        d = json.load(open(path, encoding='utf-8'))
        steps = d if isinstance(d, list) else d['steps']
        for s in (0, 1):
            r = seat_feed(steps, s)
            if r.get('animal_td'):
                rows.append(r)
        print('done', os.path.basename(path), flush=True)
    json.dump(rows, open('results/e125_feed_winners.json', 'w'), indent=1)
    return rows


def run_local(agent, vs, seeds):
    rows = []
    a = load_agent(agent, 'e125_a')
    b = a if vs in ('self', None) else load_agent(vs, 'e125_b')
    for seed in seeds:
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': int(seed),
                                                   'townCenterSellInterval': 24}, debug=False)
        env.run([a.agent, b.agent])
        r = seat_feed(env.steps, 0)
        if r.get('animal_td'):
            rows.append(r)
        print('seed', seed, r, flush=True)
    json.dump(rows, open('results/e125_feed_champion.json', 'w'), indent=1)
    return rows


if __name__ == '__main__':
    from kaggle_environments import make
    if sys.argv[1] == 'replays':
        w = run_replays(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 32)
        c = run_local(sys.argv[4] if len(sys.argv) > 4 else 'agents/futurev1_forecast.py',
                      sys.argv[5] if len(sys.argv) > 5 else 'tools/_noop_agent.py',
                      sys.argv[6:] or ['1000000', '1000001', '1000002', '1000003'])
        show({'winner_100k+': agg([r for r in w if r.get('reward', 0) >= 100000] or w, ''),
              'champion': agg(c, '')})
    else:
        show({'champion': agg(run_local(sys.argv[2], sys.argv[3], sys.argv[4:]), '')})
