"""E124 firing probe: run each variant against a no-op seat, print money + layer counters.

usage: WybeV2/rank_env/Scripts/python.exe tools/probe_e124_fert_tour.py [variant ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e118_dna_gap import load_agent  # noqa: E402
from kaggle_environments import make  # noqa: E402

VARIANTS = sys.argv[1:] or ['ctrl', 'tour45', 'tour45_sup', 'tour20_sup']
SEEDS = [1000000, 1000001]

for v in VARIANTS:
    path = 'agents/pub_e124_tour_%s.py' % v
    a = load_agent(path, 'e124p_' + v)
    b = load_agent('tools/_noop_agent.py', 'e124p_noop_')
    total = 0.0
    for seed in SEEDS:
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed,
                                                   'townCenterSellInterval': 24}, debug=False)
        env.run([a.agent, b.agent])
        last = env.steps[-1]
        total += (last[0].get('reward') or 0)
    mem = dict(a._E124_MEM)
    print('%-12s money=%9.0f %s' % (v, total, mem), flush=True)
