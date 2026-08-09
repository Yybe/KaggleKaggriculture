"""Probe the steps structure of a SEB replay."""
import json
import glob
import os

pattern = os.path.join(r"c:\Users\xxshi\Desktop\farmmasterV2", "SEB*gameplay", "*.json")
files = sorted(glob.glob(pattern))
print(f"Found {len(files)} files")

with open(files[0], 'r') as f:
    data = json.load(f)

steps = data['steps']
print(f"steps: list len={len(steps)}")
print(f"steps[0]: type={type(steps[0]).__name__}, len={len(steps[0])}")

# Each step is a list of 2 player states
step0 = steps[0]
print(f"\nstep[0][0] (player 0 at step 0):")
p0 = step0[0]
print(f"  keys: {list(p0.keys())}")
print(f"  status: {p0.get('status')}")
print(f"  reward: {p0.get('reward')}")
if 'action' in p0:
    print(f"  action type: {type(p0['action']).__name__}")
    if isinstance(p0['action'], dict):
        print(f"  action keys: {list(p0['action'].keys())[:15]}")
        print(f"  action sample: {json.dumps(p0['action'], indent=2)[:500]}")
if 'observation' in p0:
    obs = p0['observation']
    print(f"  observation keys: {list(obs.keys())[:20]}")
    print(f"  obs.step: {obs.get('step')}")
    print(f"  obs.player: {obs.get('player')}")

# Check a mid-game step
step100 = steps[100]
p0_100 = step100[0]
print(f"\nstep[100][0]:")
if 'action' in p0_100 and p0_100['action']:
    act = p0_100['action']
    print(f"  action: {json.dumps(act, indent=2)[:800]}")

# Check who is SEB - look at info
info = data.get('info', {})
print(f"\nInfo: {json.dumps(info, indent=2)[:500]}")

# Check rewards
print(f"\nFinal rewards: {data['rewards']}")
print(f"Statuses: {data['statuses']}")

# Look at last step
last = steps[-1]
print(f"\nLast step ({len(steps)-1}):")
for i, p in enumerate(last):
    print(f"  player {i}: reward={p.get('reward')}, status={p.get('status')}")
