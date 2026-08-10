"""Clean multiprocessing simulation worker for Kaggriculture."""
import os
import sys
import json
import copy

# Suppress OpenSpiel spam
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '.')
import submission
import WybeV2.v18_apex as v18_apex
from kaggle_environments import make

# Load precomputed consensus routes
_PRECOMPUTED = json.load(open('tools/routes_precomputed.json', 'r', encoding='utf-8'))
_TH1_ROUTE = _PRECOMPUTED["th1"]
_TH2_ROUTE = _PRECOMPUTED["th2"]

def th1_agent(obs, configuration=None):
    step = int(obs.get("step", 0) or 0)
    s = min(max(0, step), len(_TH1_ROUTE) - 1)
    action = copy.deepcopy(_TH1_ROUTE[s])
    action = submission._weed_repair_action(obs, action, _TH1_ROUTE, s)
    action = submission._v16_convert_livestock(action, obs, s)
    action = submission._v16_wool_controller(action, obs, s)
    return submission._align_hands(action, obs)

def th2_agent(obs, configuration=None):
    step = int(obs.get("step", 0) or 0)
    s = min(max(0, step), len(_TH2_ROUTE) - 1)
    action = copy.deepcopy(_TH2_ROUTE[s])
    action = submission._weed_repair_action(obs, action, _TH2_ROUTE, s)
    action = submission._v16_convert_livestock(action, obs, s)
    action = submission._v16_wool_controller(action, obs, s)
    return submission._align_hands(action, obs)

_AGENTS = {
    "v18_apex": v18_apex.agent,
    "v17_apex": submission.agent,
    "th1": th1_agent,
    "th2": th2_agent,
}

def simulate_match(task):
    agent_a_name, agent_b_name, seed, swap = task
    fn_a = _AGENTS[agent_a_name]
    fn_b = _AGENTS[agent_b_name]
    
    fn0 = fn_b if swap else fn_a
    fn1 = fn_a if swap else fn_b
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        st = env.state
        r0 = float(st[0].get("reward", 0) or 0)
        r1 = float(st[1].get("reward", 0) or 0)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return agent_a_name, agent_b_name, seed, swap, score_a, score_b, None
    except Exception as e:
        return agent_a_name, agent_b_name, seed, swap, 0, 0, str(e)
