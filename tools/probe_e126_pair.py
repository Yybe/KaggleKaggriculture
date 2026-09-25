"""E126 firing probe: money + layer counters for the care->feed pair graft.

Baseline (champion vs tools/_noop_agent.py, seat 0, from tools/e125_feed_discipline.py):
  seed 1000000 money 154,623 / 1000001 165,851 / 1000002 203,512 / 1000003 198,006.
ctrl must reproduce those bytes-for-bytes; pair must show swaps > 0 to be live at all.

usage: WybeV2/rank_env/Scripts/python.exe tools/probe_e126_pair.py [variant ...] [seed ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e118_dna_gap import load_agent  # noqa: E402
from kaggle_environments import make  # noqa: E402

argv = sys.argv[1:] or ['ctrl', 'pair']
variants = [a for a in argv if not a.isdigit()]
seeds = [int(a) for a in argv if a.isdigit()] or [1000000, 1000001, 1000002, 1000003]
noop = load_agent('tools/_noop_agent.py', 'e126_noop')

for v in variants:
    a = load_agent('agents/pub_e126_pair_%s.py' % v, 'e126_' + v)
    for seed in seeds:
        env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed,
                                                   'townCenterSellInterval': 24}, debug=False)
        env.run([a.agent, noop.agent])
        m = env.steps[-1][0].get('observation') or {}
        money = (m.get('farms') or [{}])[0].get('money')
        print('%-6s seed=%d money=%s %s' % (v, seed, money, dict(a._E126_MEM)), flush=True)
