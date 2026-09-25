"""E120 builder: scarcity-conditioned hold-and-release on our own SELL orders (champion FutureV1).

DNA basis (tools/e119_revenue_split.py -> results/e119_rev_replays.log + e119_rev_champion.log,
2026-09-25, one code path for both cohorts, winner seats at reward >= 100k, n=22):

    realised $/unit at quote time        champion      winner >= 100k      engine base
    MILK                                      65                166            160
    WOOL                                      75                197            200
    STRAWBERRY                                72                167            120
    EGG                                       52                 50             50
    WHEAT                                     38                 39             25
    MELON                                    181                182            250
    shed full in                                  0.3% of turns   0.5% of turns

Acreage is parity (E118 gap table) and per-crop fertilizer coverage is parity (E119: strawberry
28.0% vs 28.2%), so the whole 1.78x money gap is PRICE CAPTURE on three lines: we sell milk/wool/
strawberry at 0.4-0.6x base, the winners at 0.9-1.4x base. And we can wait: the shed is empty
99.7% of the season, so holding is not storage-constrained.

Mechanism (exactly one): on a turn where the market price of a gated item is below its base price,
delete the parent's SELL order for that item and bank the quantity; on the first turn where price
>= base, re-emit the banked quantity in one order. Volume is conserved, not suppressed - unlike
the refuted fert-retention idea (LEDGER_20260920: _r85 surplus has no consumer), every banked unit
comes back to market. Preempt turns (step % 24 == 23) are never held, so the FutureV1 forecast /
preemption layer keeps firing unmodified. After step 696 everything is force-released.

Toggles: ctrl = off (must be behaviour-identical to the parent), hold = gated animal+berry lines.
usage: python tools/build_e120_scarcity_hold.py [ctrl hold ...]
"""
import os
import py_compile
import sys

BASE = 'agents/futurev1_forecast.py'
OUT_DIR = 'agents'

LAYER = '''
# ---- E120 scarcity hold-and-release (built by tools/build_e120_scarcity_hold.py) ----
import json as _e120_json
import sys as _e120_sys
import traceback as _e120_tb

_E120_PARENT = agent
del agent

_E120_ON = __ON__
_E120_BASE = {'MILK': 160, 'WOOL': 200, 'STRAWBERRY': 120, 'EGG': 50}
_E120_CAP = 40
_E120_MARGIN = __MARGIN__
_E120_STATES = {}
_E120_MEM = {'defers': 0, 'defer_units': 0, 'releases': 0, 'release_units': 0, 'cap_skips': 0,
             'errors': 0, 'fires': 0, 'first_error': ''}


def agent(observation, configuration=None):
    action = _E120_PARENT(observation, configuration)
    if not _E120_ON:
        return action
    try:
        if not isinstance(action, dict):
            return action
        obs = observation if isinstance(observation, dict) else _e120_json.loads(observation)
        step = int(obs.get('step') or 0)
        player = int(obs.get('player') or 0)
        st = _E120_STATES.get(player)
        if st is None or step <= st['step']:
            st = _E120_STATES[player] = {'step': -1, 'bank': {}}
        st['step'] = step
        if step < 120:
            return action
        force = step >= 696
        market = list(action.get('market') or [])
        mkt = obs.get('market') or {}
        prices = mkt.get('prices') or {}
        bank = st['bank']
        orders = []
        for o in market:
            if isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == 'SELL' and o[1] in _E120_BASE:
                orders.append([o[0], o[1], int(o[2] or 0)])
            else:
                orders.append(o)
        if not force:
            kept = []
            for o in orders:
                if isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == 'SELL' \\
                        and o[1] in _E120_BASE:
                    item, qty = o[1], int(o[2] or 0)
                    px = int(prices.get(item) or 0)
                    if px < int(_E120_BASE[item] * _E120_MARGIN) and step % 24 != 23 and qty > 0:
                        room = _E120_CAP - int(bank.get(item) or 0)
                        take = min(qty, max(0, room))
                        if take > 0:
                            bank[item] = int(bank.get(item) or 0) + take
                            _E120_MEM['defers'] += 1
                            _E120_MEM['defer_units'] += take
                            _E120_MEM['fires'] += 1
                            if take < qty:
                                _E120_MEM['cap_skips'] += 1
                                kept.append(['SELL', item, qty - take])
                            continue
                kept.append(o)
            orders = kept
        release = []
        for item in sorted(bank):
            px = int(prices.get(item) or 0)
            qty = int(bank[item] or 0)
            if qty <= 0:
                bank.pop(item, None)
                continue
            if force or px >= int(_E120_BASE[item] * _E120_MARGIN):
                for i, o in enumerate(orders):
                    if isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == 'SELL' and o[1] == item:
                        orders[i] = ['SELL', item, int(o[2] or 0) + qty]
                        break
                else:
                    if len(orders) < 10:
                        orders.append(['SELL', item, qty])
                    else:
                        continue
                bank.pop(item, None)
                _E120_MEM['releases'] += 1
                _E120_MEM['release_units'] += qty
                _E120_MEM['fires'] += 1
        if _E120_MEM['fires']:
            action = dict(action)
            action['market'] = orders
    except Exception as exc:
        _E120_MEM['errors'] += 1
        if not _E120_MEM['first_error']:
            _E120_MEM['first_error'] = ('%s @step=%s | %s'
                                        % (repr(exc), locals().get('step'),
                                           ' / '.join(_e120_tb.format_exc().splitlines()[-4:])
                                           .replace('\\n', ' ')[:400]))
    return action
# ---- end E120 ----
'''

VARIANTS = {'ctrl': (False, 1.0), 'hold': (True, 1.0), 'hold11': (True, 1.1)}


def build(variant):
    on, margin = VARIANTS[variant]
    src = open(BASE, encoding='utf-8', newline='').read()
    n_defs = src.count('def agent(')
    assert n_defs >= 1
    layer = LAYER.replace('__ON__', repr(on)).replace('__MARGIN__', repr(margin))
    out = src.rstrip('\n') + '\n' + layer
    name = 'pub_e120_%s' % variant
    path = os.path.join(OUT_DIR, name + '.py')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(out)
    py_compile.compile(path, doraise=True)
    assert out.count('_E120_PARENT = agent') == 1
    assert out.count('def agent(') == n_defs + 1, 'agent defs %d -> %d' % (n_defs, out.count('def agent('))
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.agent), 'agent not callable'
    assert '_E120_PARENT' in mod.agent.__globals__, 'layer not on top of the stack'
    assert mod.agent.__globals__['_E120_PARENT'] is not mod.agent, 'parent capture is self'
    assert (on, margin) == (mod._E120_ON, mod._E120_MARGIN)
    assert 'MILK' in mod._E120_BASE and mod._E120_BASE['MILK'] == 160
    # The spine never `import sys`; a bare name in the layer's except-handler raises from inside
    # the handler, kills the seat's episode, and reads as a low-score loss instead of a bug.
    for sym in ('_e120_sys', '_e120_json', '_e120_tb'):
        assert sym in mod.agent.__globals__, 'layer module missing in globals: ' + sym
    print(name, 'delta_bytes', len(out) - len(src), 'variant', variant, (on, margin), 'layers', n_defs + 1)
    return path


if __name__ == '__main__':
    for v in (sys.argv[1:] or list(VARIANTS)):
        build(v)
