"""E95 ladder validation: E94 (pub_e94_omw_clean, FROZEN md5 398eadad...) vs r78u,
same worlds, across a behavior+tier ladder. Resumable JSONL. One subprocess per
opponent (module-cache mirror pitfall), invoked by tools/e95_run_all.sh --all
or directly:  --opponent LABEL

Protocol per (opponent, seed, swap):
  game A: variant=E94   seat(0 or 1) vs opponent
  game B: variant=r78u  same seat assignment
Logs GAME JSON lines: {opp, tier, seed, swap, var, our, opp_rw, delta, status,
secs, our_hashchain (sha1 of our per-step normalized action, len 720)}
Analysis (transitions, first divergence, bands) = tools/e95_analyze.py.

Engine pins identical to bench_e80_gate8: 1.32.7 + HINGE_GAIN + champion md5.
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

E94 = BASE / "agents" / "pub_e94_omw_clean.py"
E94_MD5 = "398eadad5d61d54d6a2c5d6a30f93c18"
CHAMP = BASE / "agents" / "pub_metav4_r78u.py"
CHAMP_MD5 = "319aad8c48675c51432ccec8f35264b8"

SEEDS = [1000000, 9000000, 3330000, 7770000]
INTERVAL = 24
OUT = BASE / "results" / "e95_ladder.jsonl"

P = lambda *parts: str(BASE.joinpath(*parts))
POOL = {
    # label: (path, tier_band, approx_live_era)
    "noop":           ("__noop__",                "floor",       0),
    "apexx":          (P("agents", "kaggle_v18_apexx.py"),              "<2400",  "~2100-2200 era"),
    "kagman_parent":  (P("agents", "e93a_kagman_parent", "parent_agent.py"), "<2400", "~2194 Shop0909"),
    "farm2945":       (P("agents", "pub_2945farm.py"),                  "2400-2600", "2511.1 live"),
    "alperen":        (P("agents", "pub_alperen_fil.py"),               "2400-2600", "~2600 class"),
    "metav4":         (P("agents", "pub_metav4.py"),                    "2600-2800", "~2700 lineage"),
    "metav4_early":   (P("agents", "pub_metav4_early.py"),              "2600-2800", "2781.9 live"),
    "h20":            (P("agents", "crop_roi30_h20.py"),                "2600-2800", "~2722 finals-era"),
    "pipe16":         (P("agents", "pub_e80_pipe16.py"),                "2650-2750 cluster", "old-gate clone"),
    "peak2950":       (P("agents", "pub_2950peak.py"),                  "2650-2750 cluster", "2950 claim"),
    "farm2945v2":     (P("agents", "pub_e90_2945farm_v2.py"),           "2650-2750 cluster", "rebake mirror"),
    "v44y4":          (P("agents", "pub_e91_v44y_4layer.py"),           "2650-2750 cluster", "2820 claim"),
    "omw_old":        (P("agents", "pub_e80_omw.py"),                   "2650-2750 cluster", "OMW w/o our gates"),
    "salem2900":      (P("agents", "pub_salem_2900.py"),                "strong", "2900"),
    "tamura":         (P("agents", "live_replay", "opp_tamura_aicon_d45969a0.py"), "strong", "~3000-era live tape"),
    "boatlee29":      (P("agents", "_top_pub", "boatlee_v29.py"),       "top", "e61 pool"),
    "salem3094":      (P("agents", "salemali7_3094.py"),                "top", "3094"),
}


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


def noop_agent(obs, cfg=None):
    return {"action": "PASS"}


def hchain(hashes):
    return hashlib.sha1(json.dumps(hashes).encode()).hexdigest()[:12]


def assert_engine():
    import kaggle_environments as ke
    v = str(getattr(ke, "__version__", "?"))
    assert "1.32.7" in v, f"engine pin broken: {v}"
    import kaggle_environments.envs.kaggriculture.kaggriculture as kg
    src = pathlib.Path(kg.__file__).read_text(encoding="utf-8", errors="replace")
    assert "HINGE_GAIN" in src, "wrong engine build"
    return v


def norm(a):
    if not isinstance(a, dict):
        return ""
    return json.dumps([a.get("farmer"), a.get("hands"), a.get("market")], sort_keys=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    args = ap.parse_args()
    key = args.opponent
    path, band, approx = POOL[key]

    assert md5(CHAMP) == CHAMP_MD5, "champion modified!"
    assert md5(E94) == E94_MD5, "E94 modified! (validation must run on frozen build)"
    version = assert_engine()

    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                done.add((r["opp"], r["seed"], r["swap"], r["var"]))
            except Exception:
                pass

    from kaggle_environments import make

    def play(fn_ours, fn_opp, seed, swap):
        f0, f1 = (fn_ours, fn_opp) if not swap else (fn_opp, fn_ours)
        chain = []

        def rec(fn, is_ours):
            def w(obs, cfg=None):
                a = fn(obs, cfg)
                if is_ours:
                    chain.append(norm(a))
                return a
            return w

        our_idx = 0 if not swap else 1
        env = make("kaggriculture", configuration={
            "episodeSteps": 720, "seed": seed,
            "townCenterSellInterval": INTERVAL}, debug=False)
        t0 = time.perf_counter()
        crash = None
        try:
            env.run([rec(f0, our_idx == 0), rec(f1, our_idx == 1)])
        except Exception as e:
            crash = repr(e)[:200]
        st = [str(env.state[i].get("status", "?")) for i in (0, 1)]
        rw = [float(env.state[i].get("reward", 0) or 0) for i in (0, 1)]
        our, orw = (rw[0], rw[1]) if not swap else (rw[1], rw[0])
        cs, bs = (st[0], st[1]) if not swap else (st[1], st[0])
        if crash:
            our, orw = 0.0, max(orw, 1e6)
        if cs in ("ERROR", "INVALID", "TIMEOUT"):
            our, orw = 0.0, max(orw, 1e6)
        if bs in ("ERROR", "INVALID", "TIMEOUT"):
            orw, our = 0.0, max(our, 1e6)
        return {"opp": key, "tier": band, "seed": seed, "swap": int(swap),
                "our": our, "opp_rw": orw, "delta": our - orw,
                "our_status": cs, "opp_status": bs,
                "secs": round(time.perf_counter() - t0, 1),
                "steps_logged": len(chain), "chain": hchain(chain),
                "crash": crash, "engine": version,
                "hashes": [hashlib.sha1(c.encode()).hexdigest()[:8] for c in chain]}

    opp_fn = noop_agent if path == "__noop__" else None
    for var, vpath in (("e94", E94), ("r78u", CHAMP)):
        vmod = load(vpath, f"e95_{var}")
        vfn = entry(vmod)
        if opp_fn is None:
            omod = load(path, "e95_opp")
            opp_fn = entry(omod)
        for seed in SEEDS:
            for swap in (0, 1):
                if (key, seed, swap, var) in done:
                    continue
                g = play(vfn, opp_fn, seed, swap)
                g["var"] = var
                with OUT.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(g) + "\n")
                print(f"[{key}] {var} seed{seed} swap{swap} delta{g['delta']:+.0f} "
                      f"({g['our_status']}/{g['opp_status']})", flush=True)
    assert md5(CHAMP) == CHAMP_MD5, "champion modified during run!"
    assert md5(E94) == E94_MD5, "E94 modified during run!"


if __name__ == "__main__":
    sys.exit(main())
