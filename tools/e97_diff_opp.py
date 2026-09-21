"""E97b: E94 vs r78ub SAME-WORLD differential vs third-party tie-band opponents.

e96_gate pinned opp=h20 (diff was 0.0 everywhere). This runs the identical
base-arm/variant-arm protocol against --opp files (metav4_early, pipe16).
Resumable JSONL -> results/e97_diffopp_<tag>.jsonl
"""
import argparse
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

A = BASE / "agents" / "pub_e94_omw_clean.py"
A_MD5 = "398eadad5d61d54d6a2c5d6a30f93c18"
B = BASE / "agents" / "friend_r78ub.py"
B_MD5 = "a4b6cc1965d08263acb176c7dd6c9aee"
INTERVAL = 24


def md5(p):
    return hashlib.md5(pathlib.Path(p).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def entry(mod):
    for fn in ("agent", "kaggle_agent"):
        f = getattr(mod, fn, None)
        if callable(f):
            return f
    raise RuntimeError("no agent entry")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", required=True)
    ap.add_argument("--seeds", required=True)
    args = ap.parse_args()
    assert md5(A) == A_MD5 and md5(B) == B_MD5, "pin broken"
    import kaggle_environments as ke
    assert "1.32.7" in str(getattr(ke, "__version__", "?")), "engine pin broken"
    import kaggle_environments.envs.kaggriculture.kaggriculture as kg
    assert "HINGE_GAIN" in pathlib.Path(kg.__file__).read_text(encoding="utf-8", errors="replace")
    from kaggle_environments import make

    oppath = BASE / args.opp
    tag = oppath.stem
    out = BASE / "results" / f"e97_diffopp_{tag}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["arm"], r["seed"], r["swap"]))

    fa = entry(load(A, f"e97b_a_{tag}"))
    fb = entry(load(B, f"e97b_b_{tag}"))
    fo = entry(load(oppath, f"e97b_o_{tag}"))

    def play(fn, seed, swap, arm):
        f0, f1 = (fn, fo) if not swap else (fo, fn)
        env = make("kaggriculture", configuration={
            "episodeSteps": 720, "seed": seed,
            "townCenterSellInterval": INTERVAL}, debug=False)
        crash = None
        try:
            env.run([f0, f1])
        except Exception as e:
            crash = repr(e)[:200]
        rw = [float(env.state[i].get("reward", 0) or 0) for i in (0, 1)]
        st = [str(env.state[i].get("status", "?")) for i in (0, 1)]
        our, orw = (rw[0], rw[1]) if not swap else (rw[1], rw[0])
        cs = st[0] if not swap else st[1]
        if crash or cs in ("ERROR", "INVALID", "TIMEOUT"):
            our, orw = 0.0, max(orw, 1e6)
        return {"arm": arm, "tag": tag, "seed": seed, "swap": swap,
                "delta": our - orw, "our": our, "opp": orw, "crash": crash}

    for seed in [int(x) for x in args.seeds.split(",")]:
        for swap in (0, 1):
            for arm, fn in (("e94", fa), ("r78ub", fb)):
                if (arm, seed, swap) in done:
                    continue
                r = play(fn, seed, swap, arm)
                with out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(r) + "\n")
                print(arm, seed, swap, r["delta"], flush=True)

    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()
            if json.loads(l)["tag"] == tag]
    per = {}
    for r in rows:
        per.setdefault((r["arm"], r["seed"]), []).append(r["delta"])
    worst = 0.0
    for k in per:
        pass
    seeds = sorted({k[1] for k in per})
    for s in seeds:
        d1 = sum(per[("e94", s)]) / len(per[("e94", s)])
        d2 = sum(per[("r78ub", s)]) / len(per[("r78ub", s)])
        worst = max(worst, abs(d2 - d1))
        print(f"seed {s} e94 {d1:.0f} r78ub {d2:.0f} diff {d2-d1:+.0f}")
    print(f"MAX|DIFF| {worst:.0f} opp={tag}")


if __name__ == "__main__":
    main()
