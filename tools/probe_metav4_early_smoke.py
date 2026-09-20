"""Smoke-check the pub_metav4 + EarlyCycle composite before spending gate time.

Plays one 720-step game per seat and reports:
  * the EarlyCycle telemetry (selected_opening, temporary_crop_seen,
    delivered_extra_wheat, extension_errors, ...) -- extension_errors must be 0
    and selected_opening must be 'EarlyCycle' for the graft to be live;
  * end rewards for both seats.

Usage: python tools/probe_metav4_early_smoke.py [seed]
"""
import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agents"))
sys.path.insert(0, os.path.join(ROOT, "Kaggriculture"))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
    from kaggle_environments import make
    composite = load(os.path.join(ROOT, "agents", "pub_metav4_early.py"), "smoke_composite")
    rival = load(os.path.join(ROOT, "agents", "pub_2945farm.py"), "smoke_rival")
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed,
                                               "townCenterSellInterval": 24}, debug=False)
    env.run([composite.agent, rival.agent])
    tele = dict(getattr(composite.agent, "telemetry", {}) or {})
    r0 = env.steps[-1][0].reward
    r1 = env.steps[-1][1].reward
    print(f"SMOKE seed={seed} seat0=composite reward={r0} seat1=2945farm reward={r1}")
    print("SMOKE telemetry:", {k: tele.get(k) for k in sorted(tele) if k != "cs_decision"})
    print("SMOKE route0 step5 hands[1]:",
          composite._IMPL.chassis.routes[0][5]["hands"][1],
          "step29 hands[2]:", composite._IMPL.chassis.routes[0][29]["hands"][2],
          "CT_TABLE entries:", len(composite.CT_TABLE))
    ok = (tele.get("selected_opening") == "EarlyCycle"
          and tele.get("extension_errors") == 0
          and tele.get("temporary_crop_seen") == 1
          and tele.get("delivered_extra_wheat", 0) > 0)
    print("SMOKE RESULT=" + ("LIVE_EARLYCYCLE" if ok else "CHECK"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
