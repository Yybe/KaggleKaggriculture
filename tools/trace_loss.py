"""Step-level divergence tracer for a single seed (rulebook G5: instrument first).

Usage:
    python trace_loss.py <agent_a.py> <agent_b.py> <seed> <window_start>
Prints, for steps >= window_start (default 440):
  step | a_act b_act | a_cash b_cash | a_shed b_shed | market (price->count per good)
Also prints first divergence step (cash/shed/action) and final totals.
"""
import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath("agents"))
sys.path.insert(0, os.path.abspath("Kaggriculture"))

GOODS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    a_path, b_path = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    seed = int(sys.argv[3])
    win_start = int(sys.argv[4]) if len(sys.argv) > 4 else 440
    mod_a = _load(a_path, "mod_trace_a")
    mod_b = _load(b_path, "mod_trace_b")

    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod_a.agent, mod_b.agent])

    steps = env.steps
    print(f"{'step':>5} | {'a_act':<4} {'b_act':<4} | {'a_cash':>8} {'b_cash':>8} | {'a_shed':>24} {'b_shed':>24} | market")
    div_cash = div_shed = div_act = None
    prev_cash = [None, None]
    prev_shed = [None, None]
    prev_act = [None, None]
    for i, st in enumerate(steps):
        o0 = st[0]["observation"]
        o1 = st[1]["observation"]
        a_cash = int(o0["farms"][o0["player"]]["money"])
        b_cash = int(o1["farms"][o1["player"]]["money"])
        a_shed = tuple(int(o0["private"]["shed"][g]) for g in GOODS)
        b_shed = tuple(int(o1["private"]["shed"][g]) for g in GOODS)
        a_act = str(st[0].get("action", "?"))
        b_act = str(st[1].get("action", "?"))
        if div_cash is None and prev_cash[0] is not None and a_cash != prev_cash[0]:
            div_cash = i
        if div_shed is None and prev_shed[0] is not None and a_shed != prev_shed[0]:
            div_shed = i
        if div_act is None and prev_act[0] is not None and a_act != prev_act[0]:
            div_act = i
        prev_cash = [a_cash, b_cash]
        prev_shed = [a_shed, b_shed]
        prev_act = [a_act, b_act]

        if i >= win_start:
            px = o0["market"]["prices"]
            px_s = " ".join(f"{g[:3]}={int(px[g])}" for g in GOODS if g in px)
            interesting = (a_act != "PASS" or b_act != "PASS") and i % 2 == 0
            if interesting or i % 20 == 0:
                print(f"{i:>5} | {a_act:<4} {b_act:<4} | {a_cash:>8} {b_cash:>8} | {px_s[:150]}")

    r0 = float(steps[-1][0].reward)
    r1 = float(steps[-1][1].reward)
    print("\nFirst divergence: cash@%s shed@%s action@%s" % (div_cash, div_shed, div_act))
    print(f"Final: A={r0:.0f}  B={r1:.0f}  delta={r0-r1:+.0f}")


if __name__ == "__main__":
    main()
