"""Probe: seed 2073 (worst V15.5-dead loss, delta -1702) - dump 660..719.

Logs BOTH players' full market order lists, STR/MILK/WOOL prices, sheds, money.
Focus: when does _recovery_sell fire, at what quoted price, and what revenue
actually lands (money deltas). Reveals why dead-inventory selling LOSES vs V15.
"""
import io
import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath("agents"))
sys.path.insert(0, os.path.abspath("Kaggriculture"))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_v155_dead_2073.log")
LOG = io.StringIO()


def logp(msg):
    LOG.write(msg + "\n")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    mod_a = _load(os.path.abspath("agents/kaggle_v155_recovery.py"), "mod_a")
    mod_b = _load(os.path.abspath("agents/kaggle_champion_v15.py"), "mod_b")
    from kaggle_environments import make

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 2073}, debug=False)
    env.run([mod_a.agent, mod_b.agent])
    steps = env.steps
    logp("total steps: %d" % len(steps))
    final0 = steps[-1][0].reward
    final1 = steps[-1][1].reward
    logp("final reward: P0(v155dead)=%s P1(v15)=%s delta=%s" % (final0, final1, (float(final0) - float(final1))))

    prev_mon0 = None
    prev_mon1 = None
    prev_shed0 = {}
    prev_shed1 = {}
    for si in range(660, len(steps)):
        s = steps[si]
        o0 = s[0].observation
        o1 = s[1].observation
        a0 = s[0].get("action")
        a1 = s[1].get("action")
        m0 = a0.get("market", []) if isinstance(a0, dict) else []
        m1 = a1.get("market", []) if isinstance(a1, dict) else []
        p0 = o0.get("market", {}).get("prices", {}) if o0 else {}
        inv0 = o0.get("market", {}).get("inventory", {}) if o0 else {}
        shed0 = o0.get("private", {}).get("shed", {}) if o0 else {}
        shed1 = o1.get("private", {}).get("shed", {}) if o1 else {}
        mon0 = o0.get("farms", [{}])[0].get("money") if o0 and o0.get("farms") else None
        mon1 = o1.get("farms", [{}])[1].get("money") if o1 and o1.get("farms") else None

        line = "step %d | P0 mkt=%s | P1 mkt=%s" % (si, m0, m1)
        line += " | STR px=%.0f inv=%.0f | MILK px=%.0f | WOOL px=%.0f" % (
            p0.get("STRAWBERRY", 0), inv0.get("STRAWBERRY", 0),
            p0.get("MILK", 0), p0.get("WOOL", 0))
        line += " | shed0 STR=%s MILK=%s WOOL=%s WHEAT=%s" % (
            shed0.get("STRAWBERRY", 0), shed0.get("MILK", 0), shed0.get("WOOL", 0), shed0.get("WHEAT", 0))
        line += " | shed1 STR=%s MILK=%s WOOL=%s" % (
            shed1.get("STRAWBERRY", 0), shed1.get("MILK", 0), shed1.get("WOOL", 0))
        line += " | $0=%s $1=%s" % (mon0, mon1)

        # revenue estimate for this step's STR sales (shed drops = STR units sold this step)
        if prev_mon0 is not None and prev_shed0:
            sold0 = max(0, int(prev_shed0.get("STRAWBERRY", 0)) - int(shed0.get("STRAWBERRY", 0)))
            sold1 = max(0, int(prev_shed1.get("STRAWBERRY", 0)) - int(shed1.get("STRAWBERRY", 0)))
            rev0 = float(mon0) - float(prev_mon0)
            rev1 = float(mon1) - float(prev_mon1)
            if sold0 or sold1:
                line += " | STRsold P0=%d P1=%d | d$0=%s d$1=%s" % (sold0, sold1, rev0, rev1)
        line += " | lateflag"
        logp(line)
        prev_mon0 = mon0
        prev_mon1 = mon1
        prev_shed0 = dict(shed0)
        prev_shed1 = dict(shed1)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(LOG.getvalue())
    print("probe written to %s" % OUT)


if __name__ == "__main__":
    main()
