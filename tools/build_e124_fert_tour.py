"""E124 builder: fertilizer CARRY TOUR (+ supply hold) on top of the champion (FutureV1).

Copy evidence (E122, tools/e122_shed_flow.py, results/e122_flow_{replays,local}.json):
  HARVEST ops 484 winner vs 482 champion -> labor at parity; units/harvest 3.39 vs 2.98.
  FERTILIZE ops 152 vs 95 (0.62x) is the only materially short labor column, and fertilizer is the
  engine's yield multiplier: accrual +2 instead of +1 per tick on watered days (`_advance:798-800`).

Engine contract this construction satisfies (kaggle_environments 1.32.7):
  * `FERTILIZE` spends ONE unit from the acting unit's CARRY, not the shed: `_apply_unit_action:312-321`
    binds `inv = _farmer_inventory(private, idx)` and `:475-482` does `_inv_take(inv,"FERTILIZER",1)`,
    setting `fertilized_until_day = max(old, day+2)`; silent no-op on empty carry or non-PLANT tile.
  * carry is destroyed at end of day (`_drop_inventories_to_shed:843-856`, then `inventories=[{}]`
    at `:878-882`) -> every application needs a same-day PICKUP.
  * `PICKUP` needs the unit on a shed-access tile (`_is_shed_adjacent:138-139`; for boardSize=10 those
    are (4,4),(5,4),(4,5),(5,5)) and is `['PICKUP', item, n]` (`:358-375`).
That is the root cause of V13's "45 blocked ops with carried==0" and of E123's inertness.

Probe finding that added the second toggle: with the tour alone, `no_shed_fert=53` of 65 hijacks and
apps=1 (delta -3,585 on seed 1000000), because `_r85_fertilizer` sells collected fert every turn on days
6-28 — the shed carries ~0 fert. So SUPPRESS must hold a small fert buffer (<= BUFFER units) for the
tour to consume; this is a USE channel, not E120's market-timing bet, and the parent's terminal sweep
still liquidates the residue.

Mechanism: hijack the farmer ONLY on turns where the parent already chose PASS (no scheduled route op is
displaced — the E118/E121 failure class). Walk to a shed-access tile, PICKUP K fert, walk to the nearest
PLANT tile not fertilized through day+2, FERTILIZE, repeat until MAX_APPS.

usage: python tools/build_e124_fert_tour.py [variant ...]
variants: ctrl tour45 tour45_sup tour20_sup
"""
import os
import py_compile
import sys

BASE = 'agents/futurev1_forecast.py'
OUT_DIR = 'agents'

LAYER = '''
# ---- E124 fertilizer carry tour (built by tools/build_e124_fert_tour.py) ----
import json as _e124_json

_E124_PARENT = agent
del agent

_E124_ON = __ON__
_E124_MAX_APPS = __MAXAPPS__
_E124_K = __K__
_E124_RESERVE = __RESERVE__
_E124_SUP = __SUP__
_E124_BUFFER = __BUFFER__
_E124_CROPS = ('WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON')
_E124_MEM = {'step': -1, 'apps': 0, 'pickups': 0, 'walks': 0, 'hijacks': 0, 'no_target': 0,
             'no_shed_fert': 0, 'held_orders': 0, 'errors': 0, 'first_error': ''}


def _e124_get(obj, key, default=None):
    if obj is None:
        return default
    try:
        v = obj.get(key)
    except AttributeError:
        try:
            v = obj[key]
        except (TypeError, KeyError, IndexError):
            return default
    return default if v is None else v


def _e124_move(dx, dy):
    if dx:
        return 'EAST' if dx > 0 else 'WEST'
    if dy:
        return 'SOUTH' if dy > 0 else 'NORTH'
    return None


def agent(observation, configuration=None):
    action = _E124_PARENT(observation, configuration)
    if not _E124_ON:
        return action
    try:
        if not isinstance(action, dict):
            return action
        obs = observation if isinstance(observation, dict) else _e124_json.loads(observation)
        step = int(_e124_get(obs, 'step', 0) or 0)
        if step <= _E124_MEM['step']:
            _E124_MEM.update({'step': -1, 'apps': 0, 'pickups': 0, 'walks': 0, 'hijacks': 0,
                              'no_target': 0, 'no_shed_fert': 0, 'held_orders': 0,
                              'errors': _E124_MEM['errors'], 'first_error': _E124_MEM['first_error']})
        _E124_MEM['step'] = step
        if step >= 696:
            return action
        farms = _e124_get(obs, 'farms') or []
        farm = _e124_get(obs, 'farm')
        if farm is None and farms:
            farm = farms[int(_e124_get(obs, 'player', 0) or 0)]
        if farm is None:
            return action
        pr = _e124_get(obs, 'private')
        shed_fert = int(_e124_get(_e124_get(pr, 'shed') or {}, 'FERTILIZER', 0) or 0)
        want_more = _E124_MEM['apps'] < _E124_MAX_APPS and step < 600
        if _E124_SUP and want_more and shed_fert <= _E124_BUFFER:
            orders = action.get('market')
            if isinstance(orders, list) and any(
                    isinstance(o, list) and len(o) > 1 and o[0] == 'SELL' and o[1] == 'FERTILIZER'
                    for o in orders):
                action['market'] = [o for o in orders if not (
                    isinstance(o, list) and len(o) > 1 and o[0] == 'SELL' and o[1] == 'FERTILIZER')]
                _E124_MEM['held_orders'] += 1
        if not want_more or action.get('farmer') != ['PASS']:
            return action
        tiles = _e124_get(farm, 'tiles') or []
        day = int(_e124_get(obs, 'day') or (step // 24))
        pos = _e124_get(farm, 'farmer') or []
        if not (isinstance(pos, list) and len(pos) == 2):
            return action
        invs = _e124_get(pr, 'inventories') or []
        carry = int(_e124_get(invs[0] if invs else {}, 'FERTILIZER', 0) or 0)
        bs = len(tiles) or 10
        half = bs // 2
        access = {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}
        targets = []
        for y, row in enumerate(tiles):
            if not isinstance(row, list):
                continue
            for x, t in enumerate(row):
                if not isinstance(t, dict):
                    continue
                if t.get('kind') == 'PLANT' and t.get('crop') in _E124_CROPS \\
                        and int(t.get('fertilized_until_day') or -1) < day + 2:
                    targets.append((x, y))
        _E124_MEM['hijacks'] += 1
        if carry <= 0:
            if shed_fert - _E124_RESERVE <= 0:
                _E124_MEM['no_shed_fert'] += 1
                return action
            if tuple(pos) in access:
                action['farmer'] = ['PICKUP', 'FERTILIZER', min(_E124_K, shed_fert - _E124_RESERVE)]
                _E124_MEM['pickups'] += 1
                return action
            gx, gy = min(access, key=lambda p: abs(p[0] - pos[0]) + abs(p[1] - pos[1]))
            m = _e124_move(gx - pos[0], gy - pos[1])
            if m:
                action['farmer'] = [m]
                _E124_MEM['walks'] += 1
            return action
        if not targets:
            _E124_MEM['no_target'] += 1
            return action
        gx, gy = min(targets, key=lambda p: abs(p[0] - pos[0]) + abs(p[1] - pos[1]))
        if (gx, gy) == (pos[0], pos[1]):
            action['farmer'] = ['FERTILIZE']
            _E124_MEM['apps'] += 1
            return action
        m = _e124_move(gx - pos[0], gy - pos[1])
        if m:
            action['farmer'] = [m]
            _E124_MEM['walks'] += 1
    except Exception as exc:
        _E124_MEM['errors'] += 1
        if not _E124_MEM['first_error']:
            _E124_MEM['first_error'] = '%r @step=%s' % (exc, locals().get('step'))
    return action
# ---- end E124 ----
'''

VARIANTS = {'ctrl': (False, 0, 8, 12, False, 24), 'tour45': (True, 45, 8, 12, False, 24),
            'tour45_sup': (True, 45, 8, 12, True, 24), 'tour20_sup': (True, 20, 8, 12, True, 24)}


def build(variant):
    on, max_apps, k, reserve, sup, buffer_ = VARIANTS[variant]
    src = open(BASE, encoding='utf-8', newline='').read()
    n_defs = src.count('def agent(')
    assert n_defs >= 1
    layer = (LAYER.replace('__ON__', repr(on)).replace('__MAXAPPS__', repr(max_apps))
                    .replace('__K__', repr(k)).replace('__RESERVE__', repr(reserve))
                    .replace('__SUP__', repr(sup)).replace('__BUFFER__', repr(buffer_)))
    out = src.rstrip('\n') + '\n' + layer
    name = 'pub_e124_tour_%s' % variant
    path = os.path.join(OUT_DIR, name + '.py')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(out)
    py_compile.compile(path, doraise=True)
    assert out.count('_E124_PARENT = agent') == 1
    assert out.count('def agent(') == n_defs + 1
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.agent), 'agent not callable'
    assert '_E124_PARENT' in mod.agent.__globals__, 'layer not on top of the stack'
    assert mod.agent.__globals__['_E124_PARENT'] is not mod.agent, 'parent capture is self'
    assert (on, max_apps, k, reserve, sup) == (mod._E124_ON, mod._E124_MAX_APPS, mod._E124_K,
                                             mod._E124_RESERVE, mod._E124_SUP)
    assert '_e124_json' in mod.agent.__globals__
    print(name, 'delta_bytes', len(out) - len(src), (on, max_apps, k, reserve, sup), 'layers',
          n_defs + 1)
    return path


if __name__ == '__main__':
    for v in (sys.argv[1:] or list(VARIANTS)):
        build(v)
