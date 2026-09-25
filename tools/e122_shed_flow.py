"""E122: EXECUTED product flow (shed increments) per seat, winners vs champion, one code path.

Declared SELL quantities are engine-clamped sentinels and quoted prices are mirror-sensitive, so E119
could not answer "how many units do they actually produce". The shed is private, per-item and only
changes by harvest/PICKUP in and SELL out, so sum(positive deltas) is a lower bound on units harvested.

usage: python tools/e122_shed_flow.py replays <glob> [max_n]
       python tools/e122_shed_flow.py local <agent.py> <vs.py|self> seed1 seed2 ...
"""
import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) or '.')
from e118_dna_gap import census, load_agent, raw, flat_tiles  # noqa: E402

ITEMS = ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']


def seat_flow(steps, seat):
    gain = Counter()
    drop = Counter()
    harvest_ops = Counter()
    n_care = n_feed = n_water = 0
    prev = None
    last_money = 0
    for i in range(len(steps) - 1):
        try:
            e = raw(steps[i][seat])
            n = raw(steps[i + 1][seat])
        except (TypeError, IndexError, KeyError):
            break
        obs = raw(e.get('observation')) or {}
        nob = raw(n.get('observation')) or {}
        a = raw(e.get('action')) or {}
        shed = {k: int(v or 0) for k, v in ((raw(obs.get('private')) or {}).get('shed') or {}).items()}
        if not isinstance(a, dict):
            a = {}
        ops = [raw(a.get('farmer'))] + [raw(o) for o in (a.get('hands') or [])]
        for op in ops:
            if not op:
                continue
            if op[0] == 'HARVEST':
                harvest_ops['ALL'] += 1
            elif op[0] == 'CARE':
                n_care += 1
            elif op[0] == 'FEED':
                n_feed += 1
            elif op[0] == 'WATER':
                n_water += 1
        if prev is not None:
            for it in ITEMS:
                d = shed.get(it, 0) - prev.get(it, 0)
                if d > 0:
                    gain[it] += d
                elif d < 0:
                    drop[it] += -d
        prev = shed
        nf = (raw(nob.get('farms')) or [])
        if isinstance(nf, list) and len(nf) > seat and isinstance(nf[seat], dict):
            last_money = nf[seat].get('money') or last_money
    acc, _ = census(steps, seats=(seat,))
    r = acc[seat]
    return {'gain': dict(gain), 'drop': dict(drop), 'harvest_ops': dict(harvest_ops),
            'care': n_care, 'feed': n_feed, 'water': n_water, 'money': last_money,
            'crop_td': dict(r['tile_days']), 'fert_ops': r['fert_ops'], 'turns': r['turns']}


def agg(rows):
    n = max(1, len(rows))
    out = {'n': len(rows), 'money': sum(r['money'] for r in rows) / n,
           'harvest_ops': sum(r['harvest_ops'].get('ALL', 0) for r in rows) / n,
           'care': sum(r['care'] for r in rows) / n, 'feed': sum(r['feed'] for r in rows) / n,
           'water': sum(r['water'] for r in rows) / n, 'fert_ops': sum(r['fert_ops'] for r in rows) / n}
    for it in ITEMS:
        out['g_' + it] = sum(r['gain'].get(it, 0) for r in rows) / n
        out['d_' + it] = sum(r['drop'].get(it, 0) for r in rows) / n
        out['td_' + it] = sum(r['crop_td'].get(it, 0) for r in rows) / n
    out['g_ANIMAL'] = sum(sum(v for k, v in r['crop_td'].items()
                              if str(k).startswith('ANIMAL')) for r in rows) / n
    return out


def show(labels):
    names = list(labels)
    print('%-14s' % 'field', ''.join('%14s' % n[:13] for n in names))
    keys = (['n', 'money', 'harvest_ops', 'care', 'feed', 'water', 'fert_ops'] +
            ['g_' + i for i in ITEMS] + ['td_' + i for i in ITEMS] + ['g_ANIMAL'])
    for k in keys:
        print('%-14s' % k, ''.join('%14.1f' % labels[n][k] for n in names))
    for n in names:
        l = labels[n]
        tot = sum(l['g_' + i] for i in ITEMS) or 1
        print('  units/op %.2f  total_gain/game %.0f  top gains %s'
              % (l['g_ANIMAL'] and tot / max(1, l['harvest_ops']) or 0, tot,
                 sorted(((round(l['g_' + i], 1), i) for i in ITEMS), reverse=True)[:5]))


def run_replays(pattern, max_n):
    files = sorted(glob.glob(pattern))[:max_n]
    allrows, win = [], []
    for path in files:
        d = json.load(open(path, encoding='utf-8'))
        last = [raw(d['steps'][-1][s]) for s in (0, 1)]
        for s in (0, 1):
            r = seat_flow(d['steps'], s)
            r['reward'] = (last[s] or {}).get('reward') or 0
            allrows.append(r)
            if r['reward'] >= 100000:
                win.append(r)
        print('done', os.path.basename(path), flush=True)
    json.dump({'all': allrows, 'winners': win}, open('results/e122_flow_replays.json', 'w'), indent=1)
    show({'cohort_all': agg(allrows), 'winner100k+': agg(win or allrows)})


def run_local(agent, vs, seeds):
    from kaggle_environments import make
    rows = []
    a = load_agent(agent, 'e122_a')
    b = load_agent(vs if vs and vs != 'self' else agent, 'e122_b')
    for seed in seeds:
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': int(seed),
                                                   'townCenterSellInterval': 24}, debug=False)
        env.run([a.agent, b.agent])
        for s in (0, 1):
            rows.append(seat_flow(env.steps, s))
        print('seed', seed, flush=True)
    json.dump({'rows': rows, 'agent': agent, 'vs': vs},
              open('results/e122_flow_local.json', 'w'), indent=1)
    show({'champion': agg(rows)})


if __name__ == '__main__':
    import kaggle_environments
    assert kaggle_environments.__version__ == '1.32.7', kaggle_environments.__version__
    if sys.argv[1] == 'replays':
        run_replays(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12)
    else:
        run_local(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, sys.argv[4:])
