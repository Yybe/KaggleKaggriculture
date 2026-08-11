"""Probe v2: static imports exactly like the proven test_vs_local_agents.py pattern."""
import os, sys, time
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, '.')

import agents.kaggle_v18_apexx as v18_apexx
import agents.submission_v16a_backup_20260810 as v17_apex
import agents.kaggle_champion_v155 as v155
import agents.kaggle_v16a_counterpreempt as v16a
import agents.kaggle_v23 as v23
import agents.kaggle_kaito_v23 as kaito_v23
import agents.salemali7_3000score as salem
import agents.kaggle_v26b as v26b
import agents.kaggle_v26_aggr_evidence as v26aggr
import agents.kaggle_boat84_v14 as boat84
import agents.kaggle_anas as anas
import agents.kaggle_flex as flex
import agents.kaggle_champion_v15 as v15
import agents.kaggle_v14_tweaked as v14tw
import agents.kaggle_v14_v26style as v14v26
import agents.kaggle_v22_romanrozen as v22
import agents.kaggle_v155_recovery as v155rec
import agents.kaggle_champion_v155_momentum_gate as v155mg
import agents.kathimunishwar_replay_agent as kathi
import agents.seb_route_r0 as seb_r0
import agents.seb_route_v1 as seb_v1
import agents.seb_route_v2 as seb_v2
import agents.seb_v15 as seb_v15
from agents.kaggle_v18_apexx import V18ApexAgent

from kaggle_environments import make

FLEET = [
    ("V18 APEXX",                   v18_apexx.agent),
    ("V17 Apex baseline",           v17_apex.agent),
    ("V15.5 Champion",              v155.agent),
    ("V16a Counter-Preempt",        v16a.agent),
    ("V23 Kaito",                   v23.agent),
    ("kaggle_kaito_v23",            kaito_v23.agent),
    ("Salemali7 3k",                salem.agent),
    ("V26b",                        v26b.agent),
    ("V26 aggr evidence",           v26aggr.agent),
    ("boat84 v14",                  boat84.agent),
    ("anas",                        anas.agent),
    ("flex",                        flex.agent),
    ("champion v15",                v15.agent),
    ("v14 tweaked",                 v14tw.agent),
    ("v14 v26style",                v14v26.agent),
    ("v22 romanrozen",              v22.agent),
    ("v155 recovery",               v155rec.agent),
    ("v155 momentum gate",          v155mg.agent),
    ("kathimunishwar",              kathi.agent),
    ("seb route r0",                seb_r0.agent),
    ("seb route v1",                seb_v1.agent),
    ("seb route v2",                seb_v2.agent),
    ("seb v15",                     seb_v15.agent),
]

print(f"All {len(FLEET)} agents imported. Running 1 smoke match each vs V18 APEXX on seed 424242...")
t0 = time.time()
for name, fn in FLEET:
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 424242}, debug=False)
        env.run([v18_apexx.agent, fn])
        r0 = float(env.state[0].get("reward", 0) or 0)
        r1 = float(env.state[1].get("reward", 0) or 0)
        print(f"  [{name:<22}] delta={r0 - r1:+.0f}")
    except Exception as e:
        print(f"  [{name:<22}] ERR {type(e).__name__}: {str(e)[:100]}")
print(f"probe done in {time.time()-t0:.1f}s")
