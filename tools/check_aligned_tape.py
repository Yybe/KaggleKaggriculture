"""Check alignment after removing the dummy step 0 from replay steps."""
import json
import glob
import sys
sys.path.insert(0, '.')
import submission

v17_actions = submission._REBALANCE_ACTIONS
print(f"V17 actions count: {len(v17_actions)}")

# Load a THUNDER tape
tape_files = sorted(glob.glob('replays_new/tape_library/*.json'))
with open(tape_files[0], 'r', encoding='utf-8') as f:
    th_data = json.load(f)

th_route = th_data['route']
print(f"THUNDER raw route length: {len(th_route)}")
print("th_route[0] (dummy step):", th_route[0])
print("th_route[1] (agent act at step 0):", th_route[1])
print("v17_actions[0] (agent act at step 0):", v17_actions[0])

# Strip dummy step 0 from THUNDER route
th_actions = th_route[1:]
print(f"THUNDER aligned actions length: {len(th_actions)}")

# Now compare v17_actions vs th_actions (first 719 steps)
def ser(a):
    return json.dumps(a, sort_keys=True, separators=(',', ':'))

diffs = sum(1 for a, b in zip(v17_actions[:719], th_actions[:719]) if ser(a) != ser(b))
print(f"\nAltered/Differing steps between V17 and THUNDER (Episode {th_data['ep']}, sub {th_data['sub']}): {diffs}/719")

# Let's inspect all differences between V17 and THUNDER for sub 55373222 and sub 55381094
