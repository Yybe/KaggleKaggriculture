"""Probe: do the grafted V5 layers ever fire on the E99 spine?

Runs a few games with agents/pub_e101_apex_layers.py vs pub_apex_v5.py, wrapping the two
layer functions to count calls, preemption fires, sweep appends, and to dump the real
observation/action surfaces at a preemption-eligible step.
Usage: WybeV2/rank_env/Scripts/python.exe tools/probe_e101_layers.py
"""
import importlib.util, os, sys, json
from kaggle_environments import make

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS = {"pre_calls": 0, "pre_fires": 0, "sweep_calls": 0, "sweep_adds": 0,
         "non_dict_action": 0, "no_private": 0, "market_full": 0, "sample": None}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


e101 = load(os.path.join(BASE, "agents", "pub_e101_apex_layers.py"), "e101_mod")
v5 = load(os.path.join(BASE, "agents", "pub_apex_v5.py"), "v5_mod")

_par_pre = e101._apex_tuned_clone_preemption
_par_sw = e101._apex_precision_terminal_sweep


def pre(obs, action):
    STATS["pre_calls"] += 1
    if not isinstance(action, dict):
        STATS["non_dict_action"] += 1
    else:
        step = int(obs.get("step", 0) or 0)
        if STATS["sample"] is None and step % 24 == 23 and 240 <= step <= 671:
            STATS["sample"] = {"step": step,
                               "action_keys": sorted(action.keys()),
                               "market_len": len(action.get("market") or []),
                               "market": (action.get("market") or [])[:6],
                               "private_keys": sorted((obs.get("private") or {}).keys())[:14],
                               "shed": dict(list((obs.get("private") or {}).get("shed", {}).items())[:8]),
                               "prices": {k: v for k, v in list((obs.get("market") or {}).get("prices", {}).items())[:8]}}
        before = len(action.get("market") or [])
        if len(action.get("market") or []) >= 10:
            STATS["market_full"] += 1
        out = _par_pre(obs, action)
        if len(out.get("market") or []) > before:
            STATS["pre_fires"] += 1
        return out
    return _par_pre(obs, action)


def sweep(obs, action):
    STATS["sweep_calls"] += 1
    before = len(action.get("market") or []) if isinstance(action, dict) else 0
    if isinstance(action, dict) and (obs.get("step", 0) >= 716):
        out = _par_sw(obs, action)
        if len(out.get("market") or []) > before:
            STATS["sweep_adds"] += 1
        return out
    return _par_sw(obs, action)


e101._apex_tuned_clone_preemption = pre
e101._apex_precision_terminal_sweep = sweep

for seed in (1000000, 3330000, 30000000, 30001000):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed,
                                               "townCenterSellInterval": 24}, debug=False)
    env.run([e101.agent, v5.agent])
    print(f"seed {seed}: E101 {env.steps[-1][0].reward} vs V5 {env.steps[-1][1].reward}  stats {STATS['pre_fires']}/{STATS['sweep_adds']}")

print(json.dumps(STATS, indent=2, default=str))
