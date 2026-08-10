"""Test 1 match timing with exact elapsed time."""
import time
import sys
sys.path.insert(0, '.')
import submission
from kaggle_environments import make

t0 = time.time()
print("Starting match on seed 1000000...")
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000000}, debug=False)
env.run([submission.agent, submission.agent])
dt = time.time() - t0
r0 = env.state[0].get("reward", 0)
r1 = env.state[1].get("reward", 0)
print(f"Match finished in {dt:.2f}s! Result: P0={r0}, P1={r1}")
