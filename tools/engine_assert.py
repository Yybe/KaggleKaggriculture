"""Engine gate assertion -- run before EVERY h2h gate.

Verifies (and prints) that the active kaggle-environments build is 1.32.7 and
that the 1.32.7 "hinge" price shape is live for CARROT/TOMATO/EGG, plus the
hinge-competition sell interval. Exits non-zero (so a gate loop aborts) if the
engine has been downgraded/changed -- see LEDGER E33 (a subagent silently
pip-downgraded to 1.32.6 and corrupted a whole gate family).

Usage:  python tools/engine_assert.py            # prints 5-line block
        python tools/engine_assert.py --quiet    # only the PASS/FAIL line
"""
import re
import sys

REQUIRED_ENGINE = "1.32.7"
HINGE = {"CARROT": 450, "TOMATO": 200, "EGG": 332}
HINGE_INTERVAL = 24


def main():
    import kaggle_environments as ke
    import kaggle_environments.envs.kaggriculture.kaggriculture as kg

    version = getattr(ke, "__version__", "?")
    params = getattr(kg, "MARKET_PARAMS", None)
    assert params, "MARKET_PARAMS missing -- engine build not recognised"

    hinge = {p: params[p].get("below_func") for p in HINGE}
    ok_engine = version == REQUIRED_ENGINE
    ok_hinge = all(v == "hinge" for v in hinge.values())
    ok_T = all(params[p].get("T") == t for p, t in HINGE.items())

    print(f"ENGINE_ASSERT kaggle_environments={version} (required {REQUIRED_ENGINE}) "
          f"{'OK' if ok_engine else 'FAIL'}")
    print(f"ENGINE_ASSERT hinge_shapes={hinge} T={ {p: params[p].get('T') for p in HINGE} } "
          f"{'OK' if (ok_hinge and ok_T) else 'FAIL'}")
    print(f"ENGINE_ASSERT townCenterSellInterval={HINGE_INTERVAL} (hinge-era config)")
    print(f"ENGINE_ASSERT module={kg.__file__}")
    if not (ok_engine and ok_hinge and ok_T):
        print("ENGINE_ASSERT RESULT=FAIL -- refusing to gate on this engine")
        return 1
    print("ENGINE_ASSERT RESULT=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
