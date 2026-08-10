"""Summarize tournament results with full statistical breakdowns."""
import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open('results/tournament_live.jsonl', 'r', encoding='utf-8') as f:
    matches = [json.loads(line) for line in f]

print(f"Total Matches Recorded: {len(matches)}")

by_opp = {}
by_category = {"8-Seed Gate": {}, "Losing Seeds": {}, "Fresh Seeds": {}}

GATE_SEEDS = {1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000}
LOSING_SEEDS = {1176492926, 449229689}

for m in matches:
    opp = m["agent_b"]
    s = m["seed"]
    if opp not in by_opp:
        by_opp[opp] = []
    by_opp[opp].append(m)
    
    cat = "8-Seed Gate" if s in GATE_SEEDS else ("Losing Seeds" if s in LOSING_SEEDS else "Fresh Seeds")
    if opp not in by_category[cat]:
        by_category[cat][opp] = []
    by_category[cat][opp].append(m)

print("\n" + "="*90)
print(f"{'OVERALL TOURNAMENT SUMMARY: V18 Apex vs Opponents':^90}")
print("="*90)
print(f"{'Opponent':<15} | {'Games':>5} | {'Record':>12} | {'Win Rate':>9} | {'Mean Score (Self vs Opp)':>25} | {'Mean Delta':>12}")
print("-"*90)

for opp, rows in sorted(by_opp.items()):
    deltas = [r["delta"] for r in rows]
    scores_a = [r["score_a"] for r in rows]
    scores_b = [r["score_b"] for r in rows]
    wins = sum(1 for d in deltas if d > 0)
    losses = sum(1 for d in deltas if d < 0)
    ties = sum(1 for d in deltas if d == 0)
    n = len(deltas)
    wr = (wins / n) * 100 if n else 0
    md = sum(deltas) / n if n else 0
    ms_a = sum(scores_a) / n if n else 0
    ms_b = sum(scores_b) / n if n else 0
    print(f"{opp:<15} | {n:5d} | {wins:3d}W/{losses:3d}L/{ties:1d}T | {wr:8.1f}% | {ms_a:9.0f} vs {ms_b:9.0f} | {md:+12.1f}")
print("="*90)

for cat_name, opp_dict in by_category.items():
    print(f"\n--- {cat_name} Breakdown ---")
    for opp, rows in sorted(opp_dict.items()):
        deltas = [r["delta"] for r in rows]
        wins = sum(1 for d in deltas if d > 0)
        losses = sum(1 for d in deltas if d < 0)
        ties = sum(1 for d in deltas if d == 0)
        n = len(deltas)
        wr = (wins / n) * 100 if n else 0
        md = sum(deltas) / n if n else 0
        print(f"  vs {opp:<12}: {wins:2d}W / {losses:2d}L / {ties:1d}T ({wr:5.1f}%) | Mean Delta: {md:+10.1f}")
