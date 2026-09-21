"""E99 probe: does the step-34 crew stall / DIG-pasture-defer reproduce locally on live defect seeds?

Runs E94 vs E94 (mirror) on each live-loss seed, dumps replay JSON, counts
empty field steps in 34-48 for both seats and prints step-33..36 hand actions.
Usage: WybeV2/rank_env/Scripts/python.exe tools/e99_probe.py [seeds...]
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import sys
import time

BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

E94 = BASE / "agents" / "pub_e94_omw_clean.py"
E94_MD5 = "398eadad5d61d54d6a2c5d6a30f93c18"
INTERVAL = 24
OUT = BASE / "results" / "E99_losses"
DEFECT_SEEDS = [1073572348, 2034928249, 1587058364, 1898931754]


def md5(p):
    return hashlib.md5(pathlib.Path(p).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def entry(mod):
    for fn in ("agent", "kaggle_agent", "kaggle_submission_agent"):
        f = getattr(mod, fn, None)
        if callable(f):
            return f
    raise RuntimeError("no agent entry")


def assert_engine():
    import kaggle_environments as ke
    v = str(getattr(ke, "__version__", "?"))
    assert "1.32.7" in v, f"engine pin broken: {v}"
    import kaggle_environments.envs.kaggriculture.kaggriculture as kg
    src = pathlib.Path(kg.__file__).read_text(encoding="utf-8", errors="replace")
    assert "HINGE_GAIN" in src, "wrong engine build"
    return v


def empty_field_steps(tape, lo, hi):
    n = 0
    for st in range(lo, hi + 1):
        if st >= len(tape):
            break
        e = tape[st]
        acts = [e.get("farmer")] + list(e.get("hands") or [])
        if all((not a) or a == ["PASS"] or a == "PASS" for a in acts):
            n += 1
    return n


def field_tape(replay, seat):
    tape = []
    for step in replay.get("steps", []):
        entry_ = step[seat]
        action = entry_.get("action") or {}
        if not isinstance(action, dict):
            action = {}
        tape.append({"farmer": list(action.get("farmer") or ["PASS"]),
                     "hands": [list(h or ["PASS"]) for h in (action.get("hands") or [])]})
    return tape


def main():
    seeds = [int(s) for s in sys.argv[1:]] or DEFECT_SEEDS
    assert md5(E94) == E94_MD5, "E94 md5 mismatch: " + md5(E94)
    ver = assert_engine()
    print("engine", ver)
    from kaggle_environments import make
    mod = load(E94, "e94_probe")
    fn = entry(mod)
    for seed in seeds:
        t0 = time.perf_counter()
        env = make("kaggriculture", configuration={
            "episodeSteps": 720, "seed": seed,
            "townCenterSellInterval": INTERVAL}, debug=False)
        env.run([fn, fn])
        rw = [float(env.state[i].get("reward", 0) or 0) for i in (0, 1)]
        replay = env.toJSON() if hasattr(env, "toJSON") else None
        if replay is None:
            replay = json.loads(json.dumps(env._replay)) if hasattr(env, "_replay") else {}
        path = OUT / f"probe_replay_{seed}.json"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(replay, fh)
        out = {"seed": seed, "rewards": rw, "secs": round(time.perf_counter() - t0, 1)}
        for seat in (0, 1):
            tape = field_tape(replay, seat)
            out[f"seat{seat}_empty_34_48"] = empty_field_steps(tape, 34, 48)
            out[f"seat{seat}_s33_36"] = [
                {"st": st, "farmer": tape[st]["farmer"], "hands": tape[st]["hands"]}
                for st in range(33, 37) if st < len(tape)]
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
