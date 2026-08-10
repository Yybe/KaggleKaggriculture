"""
VersionWybe Simulation Runner
==============================
Runs VersionWybe vs V16 (or other agents) head-to-head in the Kaggle environment.
"""
import os
import sys
import time
import argparse
import importlib.util

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FARMMASTER_ROOT = os.path.dirname(os.path.abspath(__file__))
# For V16
V16_PATH = r"C:\Users\xxshi\Desktop\farmmasterV2\submission.py"

def load_agent_from_file(filepath, module_name="loaded_agent"):
    """Dynamically load an agent from a .py file."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    # Look for agent function
    if hasattr(mod, "agent"):
        return mod.agent
    elif hasattr(mod, "_kaggle_submission_entrypoint"):
        return mod._kaggle_submission_entrypoint
    else:
        raise ValueError(f"No agent function found in {filepath}")


def run_single_game(seed, agent_a_fn, agent_b_fn, episode_steps=720):
    """Run a single game and return results."""
    from kaggle_environments import make

    start = time.time()
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": episode_steps, "seed": seed},
        debug=False,
    )
    env.run([agent_a_fn, agent_b_fn])
    elapsed = time.time() - start

    state = env.state
    reward_a = state[0].get("reward", 0) or 0
    reward_b = state[1].get("reward", 0) or 0
    status_a = state[0].get("status", "")
    status_b = state[1].get("status", "")

    return {
        "seed": seed,
        "reward_a": reward_a,
        "reward_b": reward_b,
        "margin": reward_a - reward_b,
        "winner": "A" if reward_a > reward_b else ("B" if reward_b > reward_a else "TIE"),
        "status_a": status_a,
        "status_b": status_b,
        "elapsed": round(elapsed, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="VersionWybe H2H Simulator")
    parser.add_argument("--games", type=int, default=8, help="Number of games")
    parser.add_argument("--agent_a", type=str, default="versionwybe",
                        help="Agent A: 'versionwybe' or path to .py file")
    parser.add_argument("--agent_b", type=str, default="v16",
                        help="Agent B: 'v16' or path to .py file")
    parser.add_argument("--steps", type=int, default=720)
    parser.add_argument("--base_seed", type=int, default=1000000)
    args = parser.parse_args()

    # Load agents
    if args.agent_a == "versionwybe":
        vw_path = os.path.join(os.path.dirname(__file__), "submission.py")
        agent_a = load_agent_from_file(vw_path, "versionwybe_agent")
        agent_a_name = "VersionWybe"
    else:
        agent_a = load_agent_from_file(args.agent_a, "agent_a_mod")
        agent_a_name = os.path.basename(args.agent_a)

    if args.agent_b == "v16":
        agent_b = load_agent_from_file(V16_PATH, "v16_agent")
        agent_b_name = "V16"
    else:
        agent_b = load_agent_from_file(args.agent_b, "agent_b_mod")
        agent_b_name = os.path.basename(args.agent_b)

    print(f"=== VersionWybe H2H Simulator ===")
    print(f"Matchup: {agent_a_name} (Seat 0) vs {agent_b_name} (Seat 1)")
    print(f"Games: {args.games} | Steps: {args.steps}")
    print(f"{'='*60}")

    results = []
    total_start = time.time()

    for i in range(args.games):
        seed = args.base_seed + i * 17
        print(f"[Game {i+1}/{args.games}] Seed={seed}...", end=" ", flush=True)

        try:
            res = run_single_game(seed, agent_a, agent_b, args.steps)
            results.append(res)
            print(f"{agent_a_name}={res['reward_a']:,} vs {agent_b_name}={res['reward_b']:,} | "
                  f"margin={res['margin']:+,} | {res['winner']} | {res['elapsed']}s"
                  f"{' ERROR:'+res['status_a'] if 'ERROR' in str(res['status_a']) else ''}"
                  f"{' ERROR:'+res['status_b'] if 'ERROR' in str(res['status_b']) else ''}")
        except Exception as e:
            print(f"FAILED: {e}")
            results.append({
                "seed": seed, "reward_a": 0, "reward_b": 0,
                "margin": 0, "winner": "ERROR", "status_a": str(e),
                "status_b": "", "elapsed": 0,
            })

    total_elapsed = time.time() - total_start

    # Summary
    valid = [r for r in results if r["winner"] != "ERROR"]
    if valid:
        wins_a = sum(1 for r in valid if r["winner"] == "A")
        wins_b = sum(1 for r in valid if r["winner"] == "B")
        ties = sum(1 for r in valid if r["winner"] == "TIE")
        avg_margin = sum(r["margin"] for r in valid) / len(valid)
        avg_a = sum(r["reward_a"] for r in valid) / len(valid)
        avg_b = sum(r["reward_b"] for r in valid) / len(valid)

        print(f"\n{'='*60}")
        print(f"RESULTS ({len(valid)} games, {total_elapsed:.1f}s total)")
        print(f"{'='*60}")
        print(f"{agent_a_name}: {wins_a}W / {wins_b}L / {ties}T = {wins_a/len(valid)*100:.0f}% win rate")
        print(f"Avg score: {agent_a_name}={avg_a:,.0f}  {agent_b_name}={avg_b:,.0f}")
        print(f"Avg margin: {avg_margin:+,.0f}")
        print(f"{'='*60}")
    else:
        print("\nAll games failed!")


if __name__ == "__main__":
    main()
