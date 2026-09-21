"""E97: direct H2H E94 (HybridOpening) vs friend r78ub (EarlyCycle), same worlds.

If the two openings are behaviorally equivalent on near-tie worlds, rewards
differ only by seat-side mirror noise; cells with |delta|>100 = real divergence.
Engine 1.32.7+HINGE pinned; both file md5s asserted. Resumable JSONL.
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

A = BASE / "agents" / "pub_e94_omw_clean.py"
A_MD5 = "398eadad5d61d54d6a2c5d6a30f93c18"
B = BASE / "agents" / "friend_r78ub.py"
B_MD5 = "a4b6cc1965d08263acb176c7dd6c9aee"
SEEDS = [1000000, 9000000, 3330000, 7770000, 5000000, 6000000, 8000000, 2000000]
INTERVAL = 24
OUT = BASE / "results" / "e97_h2h_e94_r78ub.jsonl"


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
    raise RuntimeError("no agent entry in " + mod.__name__)


def main():
    assert md5(A) == A_MD5, "E94 modified!"
    assert md5(B) == B_MD5, "r78ub modified!"
    import kaggle_environments as ke
    assert "1.32.7" in str(getattr(ke, "__version__", "?")), "engine pin broken"
    import kaggle_environments.envs.kaggriculture.kaggriculture as kg
    assert "HINGE_GAIN" in pathlib.Path(kg.__file__).read_text(encoding="utf-8", errors="replace")

    from kaggle_environments import make
    fa = entry(load(A, "e97_a"))
    fb = entry(load(B, "e97_b"))

    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["seed"], r["swap"]))

    for seed in SEEDS:
        for swap in (0, 1):
            if (seed, swap) in done:
                continue
            f0, f1 = (fa, fb) if not swap else (fb, fa)
            env = make("kaggriculture", configuration={
                "episodeSteps": 720, "seed": seed,
                "townCenterSellInterval": INTERVAL}, debug=False)
            crash = None
            t0 = time.perf_counter()
            try:
                env.run([f0, f1])
            except Exception as e:
                crash = repr(e)[:200]
            st = [str(env.state[i].get("status", "?")) for i in (0, 1)]
            rw = [float(env.state[i].get("reward", 0) or 0) for i in (0, 1)]
            if swap:
                rw.reverse()
                st.reverse()
            r = {"seed": seed, "swap": swap, "e94": rw[0], "r78ub": rw[1],
                 "delta": rw[0] - rw[1], "st_e94": st[0], "st_r78ub": st[1],
                 "crash": crash, "secs": round(time.perf_counter() - t0, 1)}
            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(r) + "\n")
            print(r, flush=True)

    rows = [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines()]
    d = [r["delta"] for r in rows]
    pos = sum(1 for x in d if x > 0)
    neg = sum(1 for x in d if x < 0)
    print(f"H2H E94 vs r78ub: E94wins {pos} / r78ubwins {neg} / ties {len(d)-pos-neg}"
          f" mean {sum(d)/len(d):.1f} games={len(d)}")


if __name__ == "__main__":
    main()
