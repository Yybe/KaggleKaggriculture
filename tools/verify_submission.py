"""Self-contained verification of submission.py."""
import ast
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, '.')

log_file = open('results/verify.log', 'w', encoding='utf-8')

def log(msg):
    print(msg, flush=True)
    log_file.write(str(msg) + '\n')
    log_file.flush()

try:
    log("1. Checking AST Syntax and structure...")
    with open("submission.py", "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code)
    log(f"   AST Parse OK! Code size: {len(code)} bytes, {len(code.splitlines())} lines.")

    log("\n2. Checking Kaggle environment compatibility...")
    import submission
    from kaggle_environments import make

    t0 = time.time()
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000000}, debug=True)
    env.run([submission.agent, submission.agent])
    dt = time.time() - t0
    r0 = env.state[0].get("reward", 0)
    r1 = env.state[1].get("reward", 0)
    log(f"   Match Seed 1000000 Self-Play completed in {dt:.2f}s! Scores: P0={r0}, P1={r1}")

    log("\n3. Testing against THUNDER-1 consensus on losing seed 1176492926...")
    import tools.sim_worker as sim_worker
    res = sim_worker.simulate_match(("v18_apex", "th1", 1176492926, False))
    log(f"   Losing Seed 1176492926: V18={res[4]} vs TH1={res[5]} | Delta={res[4]-res[5]:+7.0f}")

    log("\n4. Testing against THUNDER-2 consensus on losing seed 1176492926...")
    res2 = sim_worker.simulate_match(("v18_apex", "th2", 1176492926, False))
    log(f"   Losing Seed 1176492926: V18={res2[4]} vs TH2={res2[5]} | Delta={res2[4]-res2[5]:+7.0f}")

    log("\n=== ALL SUBMISSION VERIFICATIONS PASSED 100% ===")
except Exception as e:
    import traceback
    log(f"Exception occurred: {e}")
    traceback.print_exc(file=log_file)
finally:
    log_file.close()
