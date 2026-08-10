"""Quick inspection of one replay to understand game schema."""
import json, sys

fp = sys.argv[1] if len(sys.argv) > 1 else "replays_new/seb/episode-91192902-replay.json"
d = json.load(open(fp, "r"))
steps = d["steps"]
print("Rewards:", d.get("rewards"))
print("Num steps:", len(steps))

# Step 0 observation for both seats
for seat in [0, 1]:
    obs = steps[0][seat]["observation"]
    farm = obs["farms"][seat]
    mk = obs["market"]
    print(f"\nSeat {seat} step0:")
    print(f"  money={farm['money']}, hands={len(farm['hands'])}, quad={farm['unlocked_quadrants']}, tiles={len(farm['tiles'])}")
    print(f"  market keys: {list(mk.keys())}")
    if "products" in mk:
        print(f"  market products sample: {list(mk['products'].keys())[:6]}")
    if "seeds" in mk:
        print(f"  market seeds: {list(mk['seeds'].keys())}")
    if "animals" in mk:
        print(f"  market animals: {list(mk['animals'].keys())}")

# Show first 10 step actions for both seats
for t in range(1, min(11, len(steps))):
    for seat in [0, 1]:
        act = steps[t][seat].get("action", {}) or {}
        if act:
            print(f"\nStep {t} Seat {seat}:")
            print(f"  farmer={act.get('farmer')}")
            print(f"  hands={act.get('hands')}")
            mkt = act.get("market", [])
            if mkt:
                print(f"  market({len(mkt)})={mkt}")

# Show day/hour progression
for t in [0, 24, 48, 72, 96, 120, 240, 480, 719]:
    if t < len(steps):
        obs = steps[t][0]["observation"]
        print(f"\nStep {t}: day={obs['day']}, hour={obs['hour']}")
        for seat in [0, 1]:
            farm = obs["farms"][seat]
            print(f"  Seat {seat}: money={farm['money']:.0f}, hands={len(farm['hands'])}, quads={farm['unlocked_quadrants']}, tiles={len(farm['tiles'])}")
