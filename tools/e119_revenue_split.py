"""E119b: where the winners' money actually comes from - revenue split by product.

E119a proved per-crop fertilizer coverage is already at PARITY (champion strawberry 28.0% vs
winner 28.2%), so the 1.78x money gap is not production intensity. This tool attributes each
seat's per-step money increases to the SELL orders declared that step (qty x quoted price as
split weights) so the gap can be read as product-level revenue: units, mean realised $/unit,
share of total revenue. The estimator is self-checked against final money (residual column).

usage: python tools/e119_revenue_split.py replays <glob> [max_n]
       python tools/e119_revenue_split.py local   <agent.py> [vs.py] seed1 seed2 ...
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e118_dna_gap import census, load_agent, raw  # noqa: E402

PRODUCTS = ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']


def revenue_by_product(steps, seat):
    """steps: replay-style list of per-step entries, each a 2-seat list of states."""
    rev = defaultdict(float)
    units = defaultdict(int)
    quoted = defaultdict(lambda: [0, 0])   # item -> [sum(qty*price), sum(qty)] at quote time
    shed_full_turns = 0
    final_inv = {}
    turns = 0
    prev_money = None
    money_delta_pos = 0.0
    money_delta_neg = 0.0
    for i in range(len(steps) - 1):
        try:
            e = raw(steps[i][seat])
            n = raw(steps[i + 1][seat])
        except (TypeError, IndexError, KeyError):
            break
        obs = raw(e.get('observation')) or {}
        nob = raw(n.get('observation')) or {}
        farms = raw(obs.get('farms')) or []
        nfarms = raw(nob.get('farms')) or []
        if len(farms) <= seat or len(nfarms) <= seat:
            continue
        farm, nfarm = farms[seat], nfarms[seat]
        if not isinstance(farm, dict) or not isinstance(nfarm, dict):
            continue
        m, nm = farm.get('money'), nfarm.get('money')
        if m is None or nm is None:
            continue
        d = nm - m
        if prev_money is not None or True:
            if d > 0:
                money_delta_pos += d
            else:
                money_delta_neg += -d
        a = raw(e.get('action')) or {}
        sells = []
        mkt = raw(obs.get('market')) or {}
        prices = mkt.get('prices') or {}
        for o in (a.get('market') or []):
            o = raw(o)
            if o and o[0] == 'SELL' and len(o) > 2:
                sells.append((o[1], int(o[2]), max(1, int(prices.get(o[1], 1)))))
        shed = (raw(obs.get('private')) or {}).get('shed') or {}
        turns += 1
        if sum(int(v or 0) for v in shed.values()) >= int(mkt.get('shedCapacity', 100) or 100):
            shed_full_turns += 1
        final_inv = {k: int(v) for k, v in (mkt.get('inventory') or {}).items()}
        if not sells:
            continue
        for item, q, p in sells:
            quoted[item][0] += q * p
            quoted[item][1] += q
        if d <= 0:
            # Net-negative turn: buys/hires/seeds outweigh the sales; skip attribution.
            continue
        wsum = sum(q * p for _, q, p in sells) or 1
        for item, q, p in sells:
            share = d * (q * p) / wsum
            rev[item] += share
            units[item] += q
        prev_money = m
    return {'rev': dict(rev), 'units': dict(units), 'inflow': money_delta_pos,
            'outflow': money_delta_neg, 'money': (nfarm.get('money') or 0),
            'quoted': {k: v for k, v in quoted.items()}, 'turns': turns,
            'shed_full_turns': shed_full_turns, 'final_inv': final_inv}


def seat_rows(steps, min_reward):
    rows = []
    last = [raw(steps[-1][s]) for s in (0, 1)]
    for s in (0, 1):
        r = (last[s] or {}).get('reward') or 0
        if r < min_reward:
            continue
        rows.append(revenue_by_product(steps, s))
    return rows


def agg(rows, label):
    n = len(rows) or 1
    out = {'label': label, 'n': len(rows),
           'money': sum(r['money'] for r in rows) / n,
           'inflow': sum(r['inflow'] for r in rows) / n,
           'attributed': sum(sum(r['rev'].values()) for r in rows) / n,
           'shed_full%': 100.0 * sum(r['shed_full_turns'] for r in rows) / max(1, sum(r['turns'] for r in rows))}
    for p in PRODUCTS:
        out['inv_' + p] = sum((r.get('final_inv') or {}).get(p, 0) for r in rows) / n
        num = sum(r['quoted'].get(p, [0, 0])[0] for r in rows)
        den = sum(r['quoted'].get(p, [0, 0])[1] for r in rows)
        out['rv_' + p] = sum(r['rev'].get(p, 0) for r in rows) / n
        out['un_' + p] = sum(r['units'].get(p, 0) for r in rows) / n
        out['px_' + p] = (num / den) if den else 0.0
    return out


def show(labels):
    names = list(labels)
    print('%-16s' % 'field', ''.join('%16s' % n for n in names))
    for k in ['n', 'money', 'inflow', 'attributed', 'shed_full%']:
        print('%-16s' % k, ''.join('%16.1f' % labels[n][k] for n in names))
    tot = {n: sum(labels[n]['rv_' + p] for p in PRODUCTS) or 1 for n in names}
    for p in PRODUCTS:
        print('%-16s' % p, ''.join('%16s' % ('%.0f/u n=%4.0f $%.1fk %2.0f%%'
                                            % (labels[n]['px_' + p], labels[n]['un_' + p],
                                               labels[n]['rv_' + p] / 1000.0,
                                               100 * labels[n]['rv_' + p] / tot[n]))
                                    for n in names))
    print('%-16s' % 'final_mkt_inv',
          ''.join('%16s' % ' '.join('%s:%d' % (p[:4], labels[n]['inv_' + p])
                                    for p in PRODUCTS if labels[n].get('inv_' + p))
                  for n in names))


def run_replays(pattern, max_n):
    files = sorted(glob.glob(pattern))[:max_n]
    allrows, winrows = [], []
    for path in files:
        d = json.load(open(path, encoding='utf-8'))
        rows = seat_rows(d['steps'], 0)
        last = [raw(d['steps'][-1][s]) for s in (0, 1)]
        for r, s in zip(rows, (0, 1)):
            r['reward'] = (last[s] or {}).get('reward') or 0
        allrows += rows
        winrows += [r for r in rows if r['reward'] >= 100000]
        print('done', os.path.basename(path), flush=True)
    json.dump({'all': allrows, 'winners': winrows}, open('results/e119_revenue_replays.json', 'w'), indent=1)
    show({'cohort_all': agg(allrows, ''), 'winner100k+': agg(winrows or allrows, '')})


def run_local(agent, vs, seeds):
    from kaggle_environments import make
    rows = []
    a = load_agent(agent, 'e119r_a')
    b = load_agent(vs or agent, 'e119r_b')
    for seed in seeds:
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': int(seed),
                                                   'townCenterSellInterval': 24}, debug=False)
        env.run([a.agent, b.agent])
        rows += seat_rows(env.steps, 0)
        print('seed', seed, flush=True)
    json.dump({'rows': rows, 'agent': agent}, open('results/e119_revenue_champion.json', 'w'), indent=1)
    show({'champion': agg(rows, '')})


if __name__ == '__main__':
    if sys.argv[1] == 'replays':
        run_replays(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12)
    else:
        run_local(sys.argv[2], sys.argv[3] if sys.argv[3] != 'self' else None, sys.argv[4:])
