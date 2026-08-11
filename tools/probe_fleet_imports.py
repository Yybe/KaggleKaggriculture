"""Probe: verify all candidate local-agent modules import, expose callable agent, and play one match.
Used to build the definitive fleet list before the new-seed rebenchmark.
"""
import os, sys, time, importlib
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, '.')

from kaggle_environments import make

# candidate modules: (label, module_path)
CANDIDATES = [
    ("V18 APEXX (champ)",        "agents.kaggle_v18_apexx"),
    ("V17 Apex baseline",        "agents.submission_v16a_backup_20260810"),
    ("V15.5 Champion",           "agents.kaggle_champion_v155"),
    ("V16a Counter-Preempt",     "agents.kaggle_v16a_counterpreempt"),
    ("V23 Kaito",                "agents.kaggle_v23"),
    ("kaggle_kaito_v23",         "agents.kaggle_kaito_v23"),
    ("Salemali7 3k",             "agents.salemali7_3000score"),
    ("V26b",                     "agents.kaggle_v26b"),
    ("V26 aggr evidence",        "agents.kaggle_v26_aggr_evidence"),
    ("boat84 v14",               "agents.kaggle_boat84_v14"),
    ("anas",                     "agents.kaggle_anas"),
    ("flex",                     "agents.kaggle_flex"),
    ("champion v15",             "agents.kaggle_champion_v15"),
    ("v14 tweaked",              "agents.kaggle_v14_tweaked"),
    ("v14 v26style",             "agents.kaggle_v14_v26style"),
    ("v22 romanrozen",           "agents.kaggle_v22_romanrozen"),
    ("v155 recovery",            "agents.kaggle_v155_recovery"),
    ("v155 momentum gate",       "agents.kaggle_champion_v155_momentum_gate"),
    ("kathimunishwar",           "agents.kathimunishwar_replay_agent"),
    ("seb route r0",             "agents.seb_route_r0"),
    ("seb route v1",             "agents.seb_route_v1"),
    ("seb route v2",             "agents.seb_route_v2"),
    ("seb v15",                  "agents.seb_v15"),
    ("boatlee_v16rc2 kernel",    "boatlee_v16rc2.main"),
    ("kaitofukami_v27 kernel",   "kaitofukami_v27.main"),
    ("tetsutani_kernel",         "tetsutani_kernel.main"),
]

results = []
t0 = time.time()
for label, mod in CANDIDATES:
    try:
        m = importlib.import_module(mod)
        fn = getattr(m, "agent", None)
        if fn is None:
            results.append((label, "NO .agent", 0))
            print(f"[{label:<24}] NO .agent attr")
            continue
        if not callable(fn):
            results.append((label, "not callable", 0))
            print(f"[{label:<24}] agent not callable")
            continue
        # smoke: one tiny match vs v18 apexx on a cheap seed
        from agents.kaggle_v18_apexx import agent as champ
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 424242}, debug=False)
        env.run([champ, fn])
        r0 = float(env.state[0].get("reward", 0) or 0)
        r1 = float(env.state[1].get("reward", 0) or 0)
        results.append((label, "OK", r0 - r1))
        print(f"[{label:<24}] OK  delta_vs_v18={r0 - r1:+.0f}")
    except Exception as e:
        results.append((label, f"ERR: {type(e).__name__}: {str(e)[:90]}", 0))
        print(f"[{label:<24}] ERR {type(e).__name__}: {str(e)[:90]}")

print(f"\nprobe done in {time.time()-t0:.1f}s")
