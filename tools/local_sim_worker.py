"""Worker for local agents parallel evaluation."""
import os
import sys

# Suppress OpenSpiel spam
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '.')

import submission as v18_apex
import agents.kaggle_champion_v155 as v155
import agents.kaggle_v16a_counterpreempt as v16a
import agents.kaggle_v23 as v23
import agents.salemali7_3000score as salem
import agents.submission_v16a_backup_20260810 as v17_apex
from kaggle_environments import make

LOCAL_AGENTS = {
    "V17 Apex Baseline": v17_apex.agent,
    "Salemali7 3k": salem.agent,
    "V16a Counter-Preempt": v16a.agent,
    "V15.5 Champion": v155.agent,
    "V23 Kaito": v23.agent,
}

def sim_local_match(args):
    name, seed, swap = args
    agent_fn = LOCAL_AGENTS[name]
    fn0 = agent_fn if swap else v18_apex.agent
    fn1 = v18_apex.agent if swap else agent_fn
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        r0 = float(env.state[0].get("reward", 0) or 0)
        r1 = float(env.state[1].get("reward", 0) or 0)
        sa = r1 if swap else r0
        sb = r0 if swap else r1
        return name, seed, swap, sa, sb, None
    except Exception as e:
        return name, seed, swap, 0, 0, str(e)
