"""Single match debug runner with full traceback."""
import sys
import traceback
import os
sys.path.insert(0, '.')
import submission
from kaggle_environments import make
import tools.run_h2h_eval as h2h

try:
    print("Testing 1 match...")
    r0, r1 = h2h.run_match(submission.agent, h2h.th1_agent, 1000000)
    print(f"Match completed: V17={r0}, TH1={r1}")
except Exception as e:
    traceback.print_exc()
