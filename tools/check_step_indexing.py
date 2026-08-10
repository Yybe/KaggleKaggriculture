"""Verify step indexing between replay steps, tape_library routes, and submission.py."""
import json
import sys
sys.path.insert(0, '.')
import submission

# In submission.py:
# step = min(max(0, int(_get(obs, "step", 0) or 0)), len(actions) - 1)
# action = actions[step]

# Let's inspect episode 91684995 replay steps:
with open('replays_new/v17 losing/91684995.json', 'r', encoding='utf-8') as f:
    ep = json.load(f)

print("Total replay steps in 91684995:", len(ep['steps']))

# Let's print step 0, 1, 2 action and observation step for both players
for s in range(4):
    p0_act = ep['steps'][s][0].get('action')
    p1_act = ep['steps'][s][1].get('action')
    p0_obs_step = ep['steps'][s][0].get('observation', {}).get('step')
    p1_obs_step = ep['steps'][s][1].get('observation', {}).get('step')
    print(f"Replay index {s}:")
    print(f"  P0 obs_step={p0_obs_step}, action={json.dumps(p0_act)[:100] if p0_act else None}")
    print(f"  P1 obs_step={p1_obs_step}, action={json.dumps(p1_act)[:100] if p1_act else None}")

# Now let's compare THUNDER's tape in tape_library vs replay steps
tape = json.load(open('replays_new/tape_library/91646245_55381094_THUNDER.json', 'r', encoding='utf-8'))
print("\nTape length in tape_library:", len(tape['route']))
print("Tape route[0]:", json.dumps(tape['route'][0])[:100])
print("Tape route[1]:", json.dumps(tape['route'][1])[:100])
