"""E119: per-crop fertilizer coverage, live winner cohort vs our champion spine, one code path.

Answers the question V29 could not: the champions apply 135-249 FERTILIZE/season against our 114,
and V29 proved the shortfall is not supply (456 units in, 114 applied, 0 stock shortfalls) but the
tour's crop whitelist `_R51_INPUT_CROPS = {WHEAT, CARROT}` at spine :2153. Whether re-binding that
whitelist to STRAWBERRY/MELON is worth the surgery depends on how the winners actually distribute
fert coverage across crops - measured here as fert-covered tile-days / crop tile-days per crop.

usage: python tools/e119_fert_scope.py replays <glob> [max_n]
       python tools/e119_fert_scope.py local   <agent.py> [vs.py] seed1 seed2 ...
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e118_dna_gap import census, load_agent, raw  # noqa: E402

CROPS = ['WHEAT', 'CARROT', 'STRAWBERRY', 'TOMATO', 'MELON']
BASE_PRICE = {'WHEAT': 25, 'CARROT': 35, 'STRAWBERRY': 120, 'TOMATO': 60, 'MELON': 250}


def per_crop(acc, last_obs_steps, min_reward):
    rows = []
    for s, rec in acc.items():
        r = (raw(last_obs_steps[s]) or {}).get('reward') or 0
        if r < min_reward:
            continue
        td, fc = rec['tile_days'], rec['fert_by_crop']
        rows.append({'reward': r, 'fert_ops': rec['fert_ops'], 'money': rec['money'],
                     'td': {c: td.get(c, 0.0) for c in CROPS},
                     'fc': {c: fc.get(c, 0.0) for c in CROPS}})
    return rows


def aggregate(rows):
    n = len(rows) or 1
    out = {'n': len(rows), 'fert_ops': sum(r['fert_ops'] for r in rows) / n,
           'money': sum(r['money'] for r in rows) / n}
    for c in CROPS:
        out['td_' + c] = sum(r['td'][c] for r in rows) / n
        out['fc_' + c] = sum(r['fc'][c] for r in rows) / n
    return out


def show(labels):
    names = list(labels)
    print('%-22s' % 'field', ''.join('%14s' % n for n in names))
    keys = ['n', 'money', 'fert_ops'] + sum([['td_' + c, 'fc_' + c] for c in CROPS], [])
    for k in keys:
        print('%-22s' % k, ''.join('%14.1f' % labels[n][k] for n in names))
    print('%-22s' % 'cover% (fc/td)',
          ''.join('%14s' % ' '.join('%s:%.0f' % (c[:4], 100 * labels[n]['fc_' + c] / labels[n]['td_' + c])
                                    for c in CROPS if labels[n]['td_' + c] > 5) for n in names))
    # headroom: extra covered tile-days if this spine matched the reference coverage ratios
    ref = names[-1]
    for n in names[:-1]:
        gain = {c: (labels[ref]['fc_' + c] / labels[ref]['td_' + c] -
                    labels[n]['fc_' + c] / labels[n]['td_' + c]) * labels[n]['td_' + c]
                for c in CROPS if labels[n]['td_' + c] > 5 and labels[ref]['td_' + c] > 5}
        pos = {c: v for c, v in gain.items() if v > 0}
        val = sum(v * BASE_PRICE[c] / 3.0 for c, v in pos.items())  # ~3 useful days per app
        print('%s -> %s : uncovered-vs-ref tile-days %s  =>  +%.0f apps/season, $%.0f base value'
              % (n, ref, {c: round(v, 1) for c, v in sorted(pos.items(), key=lambda x: -x[1])},
                 sum(pos.values()) / 3.0, val))


def run_replays(pattern, max_n):
    files = sorted(glob.glob(pattern))[:max_n]
    rows = []
    for path in files:
        d = json.load(open(path, encoding='utf-8'))
        acc, _ = census(d['steps'])
        rows += per_crop(acc, d['steps'][-1], 0)
        print('done', os.path.basename(path), len(rows), 'rows', flush=True)
    winners = [r for r in rows if r['reward'] >= max(100000, 0)]
    json.dump({'rows': rows}, open('results/e119_replays.json', 'w'), indent=1)
    show({'top': aggregate(rows), 'winner100k+': aggregate(winners or rows)})


def run_local(agent, vs, seeds):
    from kaggle_environments import make
    rows = []
    a = load_agent(agent, 'e119_a')
    b = load_agent(vs or agent, 'e119_b')
    for seed in seeds:
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': int(seed),
                                                   'townCenterSellInterval': 24}, debug=False)
        env.run([a.agent, b.agent])
        acc, _ = census(env.steps)
        rows += per_crop(acc, env.steps[-1], 0)
        print('seed', seed, flush=True)
    json.dump({'rows': rows, 'agent': agent}, open('results/e119_champion.json', 'w'), indent=1)
    show({'champion': aggregate(rows)})


if __name__ == '__main__':
    if sys.argv[1] == 'replays':
        run_replays(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12)
    else:
        run_local(sys.argv[2], sys.argv[3] if sys.argv[3] != 'self' else None, sys.argv[4:])
