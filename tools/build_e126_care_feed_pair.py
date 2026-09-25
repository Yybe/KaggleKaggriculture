"""E126: pair CARE with FEED by swapping care-ops that can never pay (copy of winner op-discipline).

Mined from the winner tapes with `tools/e125_feed_discipline.py` (22 winner seats at reward >= 100k vs
4 champion seats vs a no-op seat, engine pin 1.32.7):

    field            winner_100k+      champion
    care_ops              360.9         404.0
    feed_ops              370.3         357.5
    pending_units        8051.1        6975.2
    escapes                  7.0          0.2
    fed%                    51.1          48.0

Winners run care/feed = 0.98, the champion runs 1.13 - we CARE more and FEED less, and end up with
13% fewer harvest-ready animal units. The engine makes that loss exact (`kaggriculture.py`):

* `CARE:525-530` only sets `tile["cared_today"]`;
* `:829-830` pays the care bonus into `pending_care_bonus` **only if `fed_today` is also true** that
  day, and `:833` resets both flags;
* `:826` consumes the bonus only on a fed production day;
* `FEED:505-513` is once-per-animal-per-day, costs 1 WHEAT from the acting unit's CARRY
  (`_inv_take(inv, "WHEAT", 1)`), and `:813-820` resets the famine counter (`consecutive_unfed >= 2`
  makes the animal escape).

So a CARE issued on an animal that is never fed that day has **zero effect in every future state**.
By the care/feed counts, the champion wastes >= 43 such ops per game.

This layer is a pure REALLOCATION of ops the spine already spends (no extra land/water/labor/carry
tour, unlike the refuted E124): where the parent emits `['CARE']` for a unit standing on an animal
tile whose `fed_today` is False and whose carry holds WHEAT, the op becomes `['FEED']`. Feeding first
also makes a later same-day CARE by another hand pay, so the swap is never a net loss of care.

usage: python tools/build_e126_care_feed_pair.py ctrl pair
"""
import importlib.util
import os
import py_compile
import sys

BASE = 'agents/futurev1_forecast.py'
OUT = 'agents/pub_e126_pair_%s.py'

LAYER = '''
# ---- E126 care->feed pairing (built by tools/build_e126_care_feed_pair.py) ----
_E126_ON = __ON__
_E126_MEM = {'step': -1, 'swaps': 0, 'care_ops': 0, 'pair_ok': 0, 'no_wheat': 0, 'already_fed': 0,
             'errors': 0, 'first_error': ''}


def _e126_get(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    if isinstance(obj, (list, tuple)):
        try:
            return obj[int(key)]
        except (ValueError, TypeError, IndexError):
            return default
    return getattr(obj, key, default)


def agent(observation, configuration=None):
    action = _E126_PARENT(observation, configuration)
    if not _E126_ON or not isinstance(action, dict):
        return action
    try:
        obs = _e126_get(observation, 'observation') or observation
        step = int(_e126_get(obs, 'step') or 0)
        if step <= _E126_MEM['step']:
            _E126_MEM.update({'step': -1, 'swaps': 0, 'care_ops': 0, 'pair_ok': 0, 'no_wheat': 0,
                              'already_fed': 0, 'errors': _E126_MEM['errors'],
                              'first_error': _E126_MEM['first_error']})
        _E126_MEM['step'] = step
        farms = _e126_get(obs, 'farms') or []
        farm = _e126_get(obs, 'farm')
        if farm is None and farms:
            farm = farms[int(_e126_get(obs, 'player', 0) or 0)]
        if farm is None:
            return action
        tiles = _e126_get(farm, 'tiles') or []
        pr = _e126_get(obs, 'private') or {}
        invs = _e126_get(pr, 'inventories') or []
        hands = _e126_get(farm, 'hands') or []
        acts = list(action.get('hands') or [])
        units = [('farmer', _e126_get(farm, 'farmer'), 0)] + \
                [(str(i), p, i + 1) for i, p in enumerate(hands)]
        for name, pos, idx in units:
            if name == 'farmer':
                op = action.get('farmer')
            else:
                op = acts[int(name)] if int(name) < len(acts) else None
            if not (isinstance(op, list) and len(op) == 1 and op[0] == 'CARE'):
                continue
            if not (isinstance(pos, list) and len(pos) == 2):
                continue
            _E126_MEM['care_ops'] += 1
            y, x = int(pos[1]), int(pos[0])
            try:
                tile = tiles[y][x]
            except IndexError:
                continue
            if not (isinstance(tile, dict) and tile.get('animal')):
                continue
            if tile.get('fed_today'):
                _E126_MEM['already_fed'] += 1
                continue
            inv = invs[idx] if idx < len(invs) else {}
            if int(_e126_get(inv, 'WHEAT', 0) or 0) <= 0:
                _E126_MEM['no_wheat'] += 1
                continue
            if name == 'farmer':
                action['farmer'] = ['FEED']
            else:
                acts[int(name)] = ['FEED']
                action['hands'] = acts
            _E126_MEM['swaps'] += 1
    except Exception as exc:
        _E126_MEM['errors'] += 1
        if not _E126_MEM['first_error']:
            _E126_MEM['first_error'] = '%r @step=%s' % (exc, locals().get('step'))
    return action
# ---- end E126 ----
'''

VARIANTS = {'ctrl': False, 'pair': True}


def build(variant):
    on = VARIANTS[variant]
    src = open(BASE, encoding='utf-8').read()
    n_agent_before = src.count('def agent(')
    layer = LAYER.replace('__ON__', repr(on)).replace(
        '_E126_PARENT', '_E126_PARENT')
    out = src + '\n\n_N_PARENT = agent\ndel agent\ndef _E126_PARENT(observation, configuration=None):\n' \
                '    return _N_PARENT(observation, configuration)\n' + layer + \
        '\nagent = agent\n'
    assert out.count('_N_PARENT = agent') == 1, 'parent anchor'
    assert out.count('def agent(') == n_agent_before + 1, 'agent def count'
    assert '_E126_ON = True' in out or '_E126_ON = False' in out, 'toggle token'
    path = OUT % variant
    open(path, 'w', encoding='utf-8').write(out)
    py_compile.compile(path, doraise=True)
    spec = importlib.util.spec_from_file_location('e126_' + variant, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.agent), 'agent callable'
    assert mod._E126_PARENT is not mod.agent, 'parent is not self'
    assert mod._E126_ON == on, 'toggle readback'
    print('%s delta_bytes %d ON=%s' % (path, len(out) - len(src), mod._E126_ON), flush=True)


if __name__ == '__main__':
    for v in sys.argv[1:] or list(VARIANTS):
        build(v)
