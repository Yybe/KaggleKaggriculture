"""E123 builder: fertilizer SUPPLY-SIDE switch on top of the champion (FutureV1).

Copy evidence (E122, matched non-mirror regime, results/e122_flow_replays.json vs
results/e122_flow_local.json, champion seats only):
  FERTILIZE ops   95/game champion vs 152/game winner 100k+   (0.62x)  <- biggest ratio gap in the labor column
  fert gained into shed 300 vs 263 units -> we COLLECT the same fert and SELL it instead of applying it
  units per HARVEST op 2.98 vs 3.39 (harvest ops 482 vs 484: labor at parity, yield per op is not)
Engine reason (`kaggriculture.py:475-482`, `798-800`): FERTILIZE spends 1 held FERTILIZER, is active
day..day+2, and the accrual bonus is +2 units instead of +1 on watered days -> one application doubles
three days of accrual on a tile. Fert sells at ~$70/u (vs-noop quote) while the doubled units are
strawberry/milk-price goods, so the *use* value beats the *export* value.

Why this is not a repeat (Rule 3): V13 added FERTILIZE ops on the tour and 45 of them were blocked with
carried==0 -> memory law "next fert attempt must change supply side". This layer does exactly that: it
spends inventory the spine currently exports, and only through units that are already idle (PASS) on a
PLANT tile. E112 re-timed fert SALES (-20,487/seed) - different mechanism, no application added.

Toggles: APP (convert idle-PASS-on-PLANT units into FERTILIZE), SUPPRESS (withhold the parent's SELL
FERTILIZER order while shed FERTILIZER > RESERVE), RESERVE (fert units kept for the export stream).
ctrl = both off = byte-behaviour identical to the parent.

usage: python tools/build_e123_fert_use.py [variant ...]   variants: ctrl app app_sup20 app_sup60
"""
import os
import py_compile
import sys

BASE = 'agents/futurev1_forecast.py'
OUT_DIR = 'agents'

LAYER = '''
# ---- E123 fertilizer supply-side switch (built by tools/build_e123_fert_use.py) ----
import json as _e123_json

_E123_PARENT = agent
del agent

_E123_APP = __APP__
_E123_SUP = __SUP__
_E123_RESERVE = __RESERVE__
_E123_CROPS = ('STRAWBERRY', 'TOMATO', 'MELON', 'WHEAT', 'CARROT')
_E123_MEM = {'step': -1, 'apps': 0, 'no_inv': 0, 'already': 0, 'idle_on_plant': 0,
             'suppressed_units': 0, 'errors': 0, 'first_error': ''}


def agent(observation, configuration=None):
    action = _E123_PARENT(observation, configuration)
    if not _E123_APP and not _E123_SUP:
        return action
    try:
        if not isinstance(action, dict):
            return action
        obs = observation if isinstance(observation, dict) else _e123_json.loads(observation)
        step = int(obs.get('step') or 0)
        if step <= _E123_MEM['step']:
            _E123_MEM.update({'step': -1, 'apps': 0, 'no_inv': 0, 'already': 0,
                              'idle_on_plant': 0, 'suppressed_units': 0,
                              'errors': _E123_MEM['errors'], 'first_error': _E123_MEM['first_error']})
        _E123_MEM['step'] = step
        farms = obs.get('farms') or []
        farm = obs.get('farm') or (farms[int(obs.get('player') or 0)] if farms else {})
        if not farm:
            return action
        day = int(obs.get('day') or (step // 24))
        held = int(((obs.get('private') or {}).get('shed') or {}).get('FERTILIZER') or 0)

        def tile_at(x, y):
            tiles = farm.get('tiles') or []
            try:
                row = tiles[y]
                return row[x] if not isinstance(row, dict) else row.get('(%d, %d)' % (x, y))
            except (IndexError, TypeError, KeyError):
                return None

        if _E123_APP and held > _E123_RESERVE:
            pos_farmer = farm.get('farmer') or []
            pos_hands = list(farm.get('hands') or [])
            hand_ops = list(action.get('hands') or [])
            units = [(pos_farmer, 'farmer', None)] + [(p, 'hands', i) for i, p in enumerate(pos_hands)]
            for pos, kind, i in units:
                if held <= _E123_RESERVE:
                    break
                if not (isinstance(pos, list) and len(pos) == 2):
                    continue
                op = action.get('farmer') if kind == 'farmer' else (hand_ops[i] if i < len(hand_ops) else None)
                if not (isinstance(op, list) and op and op[0] == 'PASS'):
                    continue
                t = tile_at(pos[0], pos[1])
                if not (isinstance(t, dict) and t.get('kind') == 'PLANT'
                        and t.get('crop') in _E123_CROPS):
                    continue
                _E123_MEM['idle_on_plant'] += 1
                until = int(t.get('fertilized_until_day') or -1)
                if until >= day + 2:
                    _E123_MEM['already'] += 1
                    continue
                held -= 1
                if kind == 'farmer':
                    action['farmer'] = ['FERTILIZE']
                else:
                    hand_ops[i] = ['FERTILIZE']
                _E123_MEM['apps'] += 1
            if _E123_APP:
                action['hands'] = hand_ops

        if _E123_SUP:
            orders = action.get('market')
            if isinstance(orders, list) and held > _E123_RESERVE:
                kept, moved = [], 0
                for o in orders:
                    if isinstance(o, list) and len(o) > 2 and o[0] == 'SELL' and o[1] == 'FERTILIZER':
                        moved += int(o[2] or 0)
                        continue
                    kept.append(o)
                if moved:
                    action['market'] = kept
                    _E123_MEM['suppressed_units'] += min(moved, held - _E123_RESERVE)
    except Exception as exc:
        _E123_MEM['errors'] += 1
        if not _E123_MEM['first_error']:
            _E123_MEM['first_error'] = '%r @step=%s' % (exc, locals().get('step'))
    return action
# ---- end E123 ----
'''

VARIANTS = {'ctrl': (False, False, 0), 'app': (True, False, 20),
            'app_sup20': (True, True, 20), 'app_sup60': (True, True, 60)}


def build(variant):
    app, sup, reserve = VARIANTS[variant]
    src = open(BASE, encoding='utf-8', newline='').read()
    n_defs = src.count('def agent(')
    assert n_defs >= 1
    layer = (LAYER.replace('__APP__', repr(app)).replace('__SUP__', repr(sup))
                    .replace('__RESERVE__', repr(reserve)))
    out = src.rstrip('\n') + '\n' + layer
    name = 'pub_e123_fert_%s' % variant
    path = os.path.join(OUT_DIR, name + '.py')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(out)
    py_compile.compile(path, doraise=True)
    assert out.count('_E123_PARENT = agent') == 1
    assert out.count('def agent(') == n_defs + 1
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.agent), 'agent not callable'
    assert '_E123_PARENT' in mod.agent.__globals__, 'layer not on top of the stack'
    assert mod.agent.__globals__['_E123_PARENT'] is not mod.agent, 'parent capture is self'
    assert (app, sup, reserve) == (mod._E123_APP, mod._E123_SUP, mod._E123_RESERVE)
    for sym in ('_e123_json',):
        assert sym in mod.agent.__globals__
    print(name, 'delta_bytes', len(out) - len(src), (app, sup, reserve), 'layers', n_defs + 1)
    return path


if __name__ == '__main__':
    for v in (sys.argv[1:] or list(VARIANTS)):
        build(v)
