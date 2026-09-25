"""E121 builder: strawberry -> tomato tile substitution on top of the champion (FutureV1).

Copy list (E119_FERT_COVERAGE_PARITY_20260925.md S9, from results/e118_cohort_replays.json winners
>=100k vs results/e118_champion_census.json, one code path):
  crop_td_STRAWBERRY  415 winners vs 532 champion   (we are OVER-supplied on the ongoing crop)
  crop_td_TOMATO      162 winners vs  38 champion   (4.2x)   plant 15.4 vs 3.3
  tile_days_total    1245 vs 1286, HARVEST 500 vs 492, hands_ops 6637 vs 6292  -> land and labor at parity
  champion realises milk $184 / straw $242 vs winners $166 / $167 (vs-noop probe) -> price is NOT the gap
=> the missing money is in WHICH ongoing crop the tiles run, not acreage, coverage or timing.

Why this is not a repeat of a refuted construction (Rule 3):
  E118 'plant' redirected WHEAT/CARROT (non-ongoing) plantings to TOMATO -> -138,266/seed; the route that
  owned the tile was a wheat route, so the redirected tomato was never watered/harvested on its own cadence.
  V20 planted tomato into idle-PASS tiles -> inert (route-owned 46/46). E57c doubled an existing tomato block.
  Here the SOURCE is STRAWBERRY: already an ongoing crop on an ongoing-crop route, so the tile keeps its
  water/fertilize/harvest schedule and only the crop identity changes. TOMATO first_yield 8 / interval 1 /
  max_yield 4 vs STRAWBERRY 10 / 2 / 4 (CROPS:12-16), so the same schedule is strictly earlier and denser.

Toggles: N = number of strawberry PLANT ops to convert, MAX_DAY = last day (24 steps) that may be converted.
ctrl (N=0) must be byte-behaviour identical to the parent.

usage: python tools/build_e121_tomato_swap.py [variant ...]   variants: ctrl n10 n20 n40
"""
import os
import py_compile
import sys

BASE = 'agents/futurev1_forecast.py'
OUT_DIR = 'agents'

LAYER = '''
# ---- E121 strawberry->tomato substitution (built by tools/build_e121_tomato_swap.py) ----
import json as _e121_json

_E121_PARENT = agent
del agent

_E121_N = __N__
_E121_MAX_STEP = __MAXSTEP__
_E121_MEM = {'step': -1, 'swaps': 0, 'candidates': 0, 'errors': 0, 'first_error': ''}


def agent(observation, configuration=None):
    action = _E121_PARENT(observation, configuration)
    if not _E121_N:
        return action
    try:
        if not isinstance(action, dict):
            return action
        obs = observation if isinstance(observation, dict) else _e121_json.loads(observation)
        step = int(obs.get('step') or 0)
        if step <= _E121_MEM['step']:
            _E121_MEM.update({'step': -1, 'swaps': 0, 'candidates': 0, 'errors': _E121_MEM['errors'],
                              'first_error': _E121_MEM['first_error']})
        _E121_MEM['step'] = step
        if step > _E121_MAX_STEP or _E121_MEM['swaps'] >= _E121_N:
            return action
        hand_ops = action.get('hands')
        if not isinstance(hand_ops, list):
            return action
        for i, op in enumerate(hand_ops):
            if _E121_MEM['swaps'] >= _E121_N:
                break
            if isinstance(op, list) and len(op) > 1 and op[0] == 'PLANT' and op[1] == 'STRAWBERRY':
                _E121_MEM['candidates'] += 1
                hand_ops[i] = ['PLANT', 'TOMATO']
                _E121_MEM['swaps'] += 1
        action['hands'] = hand_ops
    except Exception as exc:
        _E121_MEM['errors'] += 1
        if not _E121_MEM['first_error']:
            _E121_MEM['first_error'] = '%r @step=%s' % (exc, locals().get('step'))
    return action
# ---- end E121 ----
'''

VARIANTS = {'ctrl': 0, 'n10': 10, 'n20': 20, 'n40': 40}
MAX_DAY = 20


def build(variant):
    n = VARIANTS[variant]
    src = open(BASE, encoding='utf-8', newline='').read()
    n_defs = src.count('def agent(')
    assert n_defs >= 1
    layer = LAYER.replace('__N__', repr(n)).replace('__MAXSTEP__', repr(MAX_DAY * 24))
    out = src.rstrip('\n') + '\n' + layer
    name = 'pub_e121_swap_%s' % variant
    path = os.path.join(OUT_DIR, name + '.py')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(out)
    py_compile.compile(path, doraise=True)
    assert out.count('_E121_PARENT = agent') == 1
    assert out.count('def agent(') == n_defs + 1
    assert '_e121_json' in open(path, encoding='utf-8').read()
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.agent), 'agent not callable'
    assert '_E121_PARENT' in mod.agent.__globals__, 'layer not on top of the stack'
    assert mod.agent.__globals__['_E121_PARENT'] is not mod.agent, 'parent capture is self'
    assert mod._E121_N == n and '_e121_json' in mod.agent.__globals__
    print(name, 'delta_bytes', len(out) - len(src), 'n', n, 'layers', n_defs + 1)
    return path


if __name__ == '__main__':
    for v in (sys.argv[1:] or list(VARIANTS)):
        build(v)
