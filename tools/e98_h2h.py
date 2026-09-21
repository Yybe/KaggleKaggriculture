"""E98: generic same-world head-to-head, resumable. Usage:
  python tools/e98_h2h.py --a agents/X.py --b agents/Y.py --tag t [--seeds ...]
Engine 1.32.7+HINGE asserted; md5 of both files logged and re-checked at end.
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
SEEDS = [1000000, 9000000, 3330000, 7770000, 5000000, 6000000, 8000000, 2000000]
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
    raise RuntimeError("no agent entry in " + mod.__name__)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--seeds", default=None)
    args = ap.parse_args()
    pa, pb = BASE / args.a, BASE / args.b
    ma, mb = md5(pa), md5(pb)
    import kaggle_environments as ke
    assert "1.32.7" in str(getattr(ke, "__version__", "?")), "engine pin broken"
    import kaggle_environments.envs.kaggriculture.kaggriculture as kg
    assert "HINGE_GAIN" in pathlib.Path(kg.__file__).read_text(encoding="utf-8", errors="replace")
    from kaggle_environments import make

    seeds = [int(x) for x in args.seeds.split(",")] if args.seeds else SEEDS
    out = BASE / "results" / f"e98_h2h_{args.tag}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["seed"], r["swap"]))

    tag = args.tag.replace("-", "_")
    fa = entry(load(pa, f"e98_a_{tag}"))
    fb = entry(load(pb, f"e98_b_{tag}"))

    for seed in seeds:
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
            ra = {"a_md5": ma[:8], "b_md5": mb[:8], "seed": seed, "swap": swap,
                  "a": rw[0], "b": rw[1], "delta": rw[0] - rw[1],
                  "sa": st[0], "sb": st[1], "crash": crash,
                  "secs": round(time.perf_counter() - t0, 1)}
            with out.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ra) + "\n")
            print(ra, flush=True)

    assert md5(pa) == ma and md5(pb) == mb, "file changed mid-run"
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    d = [r["delta"] for r in rows]
    w = sum(1 for x in d if x > 0)
    l = sum(1 for x in d if x < 0)
    print(f"H2H {args.a} vs {args.b}: Awins {w} Lw {l} ties {len(d)-w-l} mean {sum(d)/len(d):.1f} n={len(d)}")


if __name__ == "__main__":
    main()
