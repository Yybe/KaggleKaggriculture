"""Direct diagnostic test of candidate evaluation writing to file."""
import os
import sys
import json
import traceback

sys.path.insert(0, '.')
os.makedirs('results', exist_ok=True)
log_file = open('results/eval.log', 'w', encoding='utf-8')

def log(msg):
    print(msg, flush=True)
    log_file.write(str(msg) + '\n')
    log_file.flush()

try:
    import tools.tune_v18_apex as tune

    log("Testing 1 match with CandidateV18Agent...")
    cfg = {
        "route_name": "th1",
        "wool_intercept_step": 663,
        "wool_intercept_qty": 8,
        "milk_intercept_step": 666,
        "milk_intercept_qty": 9,
        "enable_boatlee_relay": True,
        "enable_recovery": True,
        "bump_cap": 1,
    }
    score_a, score_b, err = tune.play_match_worker((cfg, "th1", 1000000, False))
    log(f"Match Result: Candidate={score_a}, TH1={score_b}, Delta={score_a-score_b:+7.0f}, Error={err}")
    
    # Test on losing seed 1176492926 vs TH1
    log("\nTesting on losing seed 1176492926 vs TH1...")
    score_a1, score_b1, err1 = tune.play_match_worker((cfg, "th1", 1176492926, False))
    log(f"Losing Seed Result vs TH1: Candidate={score_a1}, TH1={score_b1} (Delta={score_a1-score_b1:+7.0f})")
    
    # Test on losing seed 1176492926 vs TH2
    log("\nTesting on losing seed 1176492926 vs TH2...")
    score_a2, score_b2, err2 = tune.play_match_worker((cfg, "th2", 1176492926, False))
    log(f"Losing Seed Result vs TH2: Candidate={score_a2}, TH2={score_b2} (Delta={score_a2-score_b2:+7.0f})")

    # Run full 8-seed gate vs TH1
    log("\nRunning full 8-seed gate vs TH1...")
    wins, losses, deltas = 0, 0, []
    for s in [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]:
        for swap in [False, True]:
            sa, sb, err = tune.play_match_worker((cfg, "th1", s, swap))
            d = sa - sb
            deltas.append(d)
            if d > 0: wins += 1
            elif d < 0: losses += 1
            log(f"  Seed {s:10d} (swap={swap}): Candidate={sa:7.0f} vs TH1={sb:7.0f} | Delta={d:+7.0f}")
            
    log(f"\n8-Seed Gate vs TH1: {wins}W/{losses}L/{len(deltas)-wins-losses}T ({wins/len(deltas)*100:.1f}%) | Mean Delta: {sum(deltas)/len(deltas):+7.1f}")
except Exception as e:
    log(f"Exception: {e}")
    traceback.print_exc(file=log_file)
finally:
    log_file.close()
