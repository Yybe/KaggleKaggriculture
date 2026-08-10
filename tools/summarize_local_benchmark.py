"""Summarize local agents benchmark results."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open('results/local_live.jsonl', 'r', encoding='utf-8') as f:
    matches = [json.loads(line) for line in f]

print(f"Total Local Agent Matches Recorded: {len(matches)}")
by_opp = {}
for m in matches:
    opp = m['opp']
    if opp not in by_opp:
        by_opp[opp] = []
    by_opp[opp].append(m)

print("\n" + "="*95)
print(f"{'Local Opponent':<18} | {'Games':>5} | {'Record':>12} | {'Win Rate':>9} | {'Mean Score (V18 vs Opp)':>25} | {'Mean Delta':>12}")
print("="*95)

for opp, rows in sorted(by_opp.items()):
    deltas = [r['delta'] for r in rows]
    scores_v18 = [r['score_v18'] for r in rows]
    scores_opp = [r['score_opp'] for r in rows]
    wins = sum(1 for d in deltas if d > 0)
    losses = sum(1 for d in deltas if d < 0)
    ties = sum(1 for d in deltas if d == 0)
    n = len(deltas)
    wr = (wins / n) * 100 if n else 0
    md = sum(deltas) / n if n else 0
    ms_v18 = sum(scores_v18) / n if n else 0
    ms_opp = sum(scores_opp) / n if n else 0
    print(f"{opp:<18} | {n:5d} | {wins:3d}W/{losses:3d}L/{ties:1d}T | {wr:8.1f}% | {ms_v18:9.0f} vs {ms_opp:9.0f} | {md:+12.1f}")
print("="*95)
