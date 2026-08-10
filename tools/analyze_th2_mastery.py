"""Analyze TH2 production route and evaluate Candidate using TH2 as base route."""
import os
import sys
import json
import time
sys.path.insert(0, '.')
import tools.tune_v18_apex as tune

# Let's test a candidate agent built on TH2's base route!
print("="*70)
print("TESTING CANDIDATES WITH TH2 (SUB 55381094) BASE ROUTE")
print("="*70)

# Candidate with TH2 base route + wool intercept + milk intercept + recovery selling
cfg_th2_apex = {
    "route_name": "th2",
    "wool_intercept_step": 663,
    "wool_intercept_qty": 8,
    "milk_intercept_step": 666,
    "milk_intercept_qty": 9,
    "enable_boatlee_relay": True,
    "enable_recovery": True,
    "bump_cap": 1,
}

# Evaluate vs V17
print("\n--- Candidate (TH2-Apex) vs V17 on 8-Seed Gate ---")
wins, losses, ties, deltas = 0, 0, 0, []
for s in tune.GATE_SEEDS:
    for swap in [False, True]:
        sa, sb, err = tune.play_match_worker((cfg_th2_apex, "v17", s, swap))
        d = sa - sb
        deltas.append(d)
        if d > 0: wins += 1
        elif d < 0: losses += 1
        else: ties += 1
        print(f"Seed {s:10d} (swap={swap}): Candidate={sa:7.0f} vs V17={sb:7.0f} | Delta={d:+7.0f}")
print(f"--> Result vs V17: {wins}W/{losses}L/{ties}T ({wins/len(deltas)*100:.1f}%) | Mean Δ: {sum(deltas)/len(deltas):+7.1f}")

# Evaluate vs TH1
print("\n--- Candidate (TH2-Apex) vs TH1 on 8-Seed Gate ---")
wins, losses, ties, deltas = 0, 0, 0, []
for s in tune.GATE_SEEDS:
    for swap in [False, True]:
        sa, sb, err = tune.play_match_worker((cfg_th2_apex, "th1", s, swap))
        d = sa - sb
        deltas.append(d)
        if d > 0: wins += 1
        elif d < 0: losses += 1
        else: ties += 1
        print(f"Seed {s:10d} (swap={swap}): Candidate={sa:7.0f} vs TH1={sb:7.0f} | Delta={d:+7.0f}")
print(f"--> Result vs TH1: {wins}W/{losses}L/{ties}T ({wins/len(deltas)*100:.1f}%) | Mean Δ: {sum(deltas)/len(deltas):+7.1f}")

# Evaluate vs TH2
print("\n--- Candidate (TH2-Apex) vs TH2 on 8-Seed Gate ---")
wins, losses, ties, deltas = 0, 0, 0, []
for s in tune.GATE_SEEDS:
    for swap in [False, True]:
        sa, sb, err = tune.play_match_worker((cfg_th2_apex, "th2", s, swap))
        d = sa - sb
        deltas.append(d)
        if d > 0: wins += 1
        elif d < 0: losses += 1
        else: ties += 1
        print(f"Seed {s:10d} (swap={swap}): Candidate={sa:7.0f} vs TH2={sb:7.0f} | Delta={d:+7.0f}")
print(f"--> Result vs TH2: {wins}W/{losses}L/{ties}T ({wins/len(deltas)*100:.1f}%) | Mean Δ: {sum(deltas)/len(deltas):+7.1f}")

# Evaluate on losing seeds 1176492926 and 449229689
print("\n--- Candidate (TH2-Apex) on Exact Losing Seeds ---")
for s in tune.LOSING_SEEDS:
    for opp in ["v17", "th1", "th2"]:
        for swap in [False, True]:
            sa, sb, err = tune.play_match_worker((cfg_th2_apex, opp, s, swap))
            d = sa - sb
            print(f"Seed {s:10d} vs {opp:3s} (swap={swap}): Candidate={sa:7.0f} vs Opp={sb:7.0f} | Delta={d:+7.0f}")
