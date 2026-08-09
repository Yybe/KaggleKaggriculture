import kaggle_environments.envs.kaggriculture.kaggriculture as kg
from kaggle_environments import make
import agents_lib

# --- transaction logging ---
txs = []
_orig_commit = kg._commit_unit


def patched_commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    if ok:
        txs.append((farm.get('day', '?'), op, item, price))
    return ok


kg._commit_unit = patched_commit

env = make('kaggriculture', configuration={'seed': 42}, debug=False)
day = -1
summary = []


def wrap(obs):
    global day
    d = obs['day']
    act = agents_lib.baseline_v8(obs)
    if d != day:
        if day >= 0:
            f = obs['farms'][0]
            priv = obs['private']
            mkt = obs.get('market', {}) or {}
            summary.append(
                f"d{day:02d}: $={f['money']:.0f} "
                f"shed={dict((k, v) for k, v in priv['shed'].items() if v)} "
                f"seeds={dict((k, v) for k, v in priv['seeds'].items() if v)} "
                f"inv_MELON={mkt.get('inventory', {}).get('MELON', '?')} "
                f"p_MELON={mkt.get('prices', {}).get('MELON', '?')}")
        day = d
    return act


env.run([wrap, 'random'])
fin = env.steps[-1]
print('final:', fin[0].reward)
for line in summary:
    print(line)
print('--- transactions ---')
from collections import Counter
cnt = Counter()
by_day = {}
for d, op, item, price in txs:
    cnt[(op, item)] += 1
    by_day.setdefault(d, []).append((op, item, price))
for d in sorted(by_day):
    ops = by_day[d]
    # summarize per day
    agg = Counter()
    tot = 0
    for op, item, price in ops:
        agg[(op, item)] += 1
        if op == 'SELL':
            tot += price
    s = ' '.join(f"{k[0]}:{k[1]}x{v}" for k, v in sorted(agg.items()))
    print(f"day {d}: {s} | SELL total=${tot}")
