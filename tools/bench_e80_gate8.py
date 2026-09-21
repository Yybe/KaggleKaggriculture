"""E80 gate8: two NEW public challengers vs the r78u champion. 8 seeds x 2 swaps, engine 1.32.7.

Challengers (both are Dmitrii Gluzdov "One More Wheat" family, i.e. near-clones of OUR r78u):
  omw    -> agents/pub_e80_omw.py     (Pipe-16 HybridOpening + extra-day wheat maturity overlay)
  pipe16 -> agents/pub_e80_pipe16.py   (nathanjacob Pipe-16: b64+gzip payload, sha256-verified,
                                        byte-identical to the embedded main.py; notebook plumbing
                                        cells -- WORKDIR/main.py write, tar build, FileLink duels
                                        -- live in the outer kernel file and are NOT included)

Integrity gates enforced at process start / around imports:
  * kaggle_environments.__version__ must contain '1.32.7'
  * the imported kaggriculture env source must contain 'HINGE_GAIN' (right patched build)
  * champion md5 319aad8c48675c51432ccec8f35264b8 asserted BEFORE and AFTER import
    (r78u has import-time side effects) and at the end of the run
  * one challenger per FRESH process, each module loaded under a UNIQUE sys.modules name
    (module-cache mirrors: two ~1MB spine modules otherwise shadow each other -> fake ties)
  * a game where one side raises/ERRORs counts as a loss for that side (noted in the log)

Resumable: already-logged (seed, swap) pairs are skipped and re-read for the totals.

Usage:  WybeV2/rank_env/Scripts/python.exe tools/bench_e80_gate8.py --challenger omw
        ... --challenger pipe16 [--probe]     # --probe = single game + telemetry dump
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import time

BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

SEEDS = [1000000, 9000000, 3330000, 7770000, 5000000, 6000000, 8000000, 2000000]
INTERVAL = 24
CHAMPION = BASE / "agents" / "pub_metav4_r78u.py"
CHAMP_MD5 = "319aad8c48675c51432ccec8f35264b8"
CHALLENGERS = {
    "omw": BASE / "agents" / "pub_e80_omw.py",
    "pipe16": BASE / "agents" / "pub_e80_pipe16.py",
    "v53": BASE / "agents" / "pub_e80_v53.py",
    "kagman": BASE / "agents" / "e93_kagman" / "main.py",
    "kagmanp": BASE / "agents" / "e93a_kagman_parent" / "parent_agent.py",
    "omwc": BASE / "agents" / "pub_e94_omw_clean.py",
}
# omw: == sha256 of the pulled submission.tar.gz payload (LEDGER E80); pipe16: == the
# kernel's own EXPECTED_SHA256 for the embedded gzip+base64 main.py.
CHAL_SHA256 = {
    "omw": "10f58185b916392ca39697c83f67f455df81a74dfb6eb1aacd60fd81d50c9970",
    "pipe16": "827ddf2997fa442e80baadebc4cc91ffaeedec1ff333c1fa7d872b0f1d448181",
    "v53": "20fe549dd4573b9fd1dfb32a1782c205fa74f0edfdfd6cbe935079533e0a9d0e",
    "kagman": "0cba779f8e63918d732150b8de8e8d728c177874f93b3c064f3fb5cc906e48f4",
    "kagmanp": "d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b",
    # e94: locally built (tools/build_e94_omw_clean.py), not a public payload — pinned at build.
    "omwc": "20b5cdbd1775dddf42f5e8ad2fc2e2969816607d0a72f51bf2a5645ed496a166",
}
ERR_STATUS = ("ERROR", "INVALID", "TIMEOUT", "Error")


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def assert_champ_md5(tag, log):
    got = md5(CHAMPION)
    log(f"CHAMP_MD5 {tag}: {got} {'OK' if got == CHAMP_MD5 else 'MISMATCH'}")
    assert got == CHAMP_MD5, f"champion file changed ({tag}): {got} != {CHAMP_MD5}"


def assert_engine(log):
    import kaggle_environments as ke
    version = str(getattr(ke, "__version__", "?"))
    log(f"ENGINE_ASSERT kaggle_environments={version} module={ke.__file__}")
    assert "1.32.7" in version, f"engine pin broken: {version}"
    import kaggle_environments.envs.kaggriculture.kaggriculture as kg
    src = pathlib.Path(kg.__file__).read_text(encoding="utf-8", errors="replace")
    has_hinge = "HINGE_GAIN" in src
    log(f"ENGINE_ASSERT kaggriculture={kg.__file__} HINGE_GAIN_in_source={has_hinge} "
        f"HINGE_GAIN={getattr(kg, 'HINGE_GAIN', None)}")
    assert has_hinge, "kaggriculture source lacks HINGE_GAIN -- wrong/older engine build"
    log("ENGINE_ASSERT RESULT=PASS")
    return version


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


def done_keys(path):
    """(seed, swap) pairs already present in a resumable log."""
    out = set()
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"GAME seed=(\d+) swap=(\d+) ", line)
        if m:
            out.add((int(m.group(1)), int(m.group(2))))
    return out


def parse_rows(path):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"GAME seed=(\d+) swap=(\d+) chal=(\S+) base=(\S+) delta=(\S+) "
                     r"cstatus=(\S+) bstatus=(\S+) secs=(\S+)(.*)", line)
        if not m:
            continue
        rows.append({"seed": int(m.group(1)), "swap": int(m.group(2)),
                     "our": float(m.group(3)), "opp": float(m.group(4)),
                     "delta": float(m.group(5)), "cstatus": m.group(6),
                     "bstatus": m.group(7), "secs": float(m.group(8)),
                     "note": m.group(9).strip()})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--challenger", required=True, choices=sorted(CHALLENGERS))
    ap.add_argument("--probe", action="store_true",
                    help="run ONE game and dump both agents' telemetry, no gate")
    args = ap.parse_args()
    key = args.challenger
    cpath = CHALLENGERS[key]

    log_path = BASE / "results" / f"e80_{key}_gate8.log"
    json_path = BASE / "results" / f"e80_{key}_gate8.json"
    log_f = log_path.open("a", encoding="utf-8")

    def log(msg):
        line = str(msg)
        print(line, flush=True)
        log_f.write(line + "\n")
        log_f.flush()

    version = assert_engine(log)
    assert_champ_md5("pre-import", log)

    t0 = time.perf_counter()
    chal_mod = load(cpath, f"e80_chal_{key}")
    base_mod = load(CHAMPION, f"r78u_base_e80_{key}")
    log(f"IMPORT {cpath.name} -> sys.modules['e80_chal_{key}'] "
        f"(champion -> 'r78u_base_e80_{key}'), {(time.perf_counter()-t0):.1f}s")
    log(f"CHAL_MD5 {cpath.name}: {md5(cpath)}")
    assert hashlib.sha256(cpath.read_bytes()).hexdigest() == CHAL_SHA256[key], \
        f"challenger bytes differ from the pinned public payload for {key}"
    assert_champ_md5("post-import", log)

    chal, base = entry(chal_mod), entry(base_mod)
    from kaggle_environments import make

    def play(seed, swap):
        fn0, fn1 = (chal, base) if not swap else (base, chal)
        env = make("kaggriculture", configuration={
            "episodeSteps": 720, "seed": seed,
            "townCenterSellInterval": INTERVAL}, debug=False)
        t = time.perf_counter()
        crash = None
        try:
            env.run([fn0, fn1])
        except Exception as e:  # interpreter-level crash
            crash = repr(e)[:200]
        st = [str(env.state[i].get("status", "?")) for i in (0, 1)]
        rw = [env.state[i].get("reward", 0) for i in (0, 1)]
        r = []
        for i in (0, 1):
            try:
                r.append(float(rw[i] or 0))
            except (TypeError, ValueError):
                r.append(0.0)
        our, opp = (r[0], r[1]) if not swap else (r[1], r[0])
        cs, bs = (st[0], st[1]) if not swap else (st[1], st[0])
        note = ""
        if crash:
            note = f"RUNTIME_CRASH {crash}"
            our, opp = 0.0, 1e9  # challenger loses
        else:
            if cs in ERR_STATUS and bs not in ERR_STATUS:
                note = "CHALLENGER_ERROR->loss"
                our, opp = 0.0, max(opp, 1e6)
            elif bs in ERR_STATUS and cs not in ERR_STATUS:
                note = "BASE_ERROR->challenger_win"
                our, opp = max(our, 1e6), 0.0
            elif cs in ERR_STATUS and bs in ERR_STATUS:
                note = "BOTH_ERROR->tie"
                our = opp = 0.0
        return {"seed": seed, "swap": int(swap), "our": our, "opp": opp,
                "delta": our - opp, "cstatus": cs, "bstatus": bs,
                "secs": time.perf_counter() - t, "note": note}

    if args.probe:
        row = play(SEEDS[0], False)
        print("PROBE", row, flush=True)
        for label, mod in (("challenger", chal_mod), ("champion", base_mod)):
            tele = getattr(mod.agent, "telemetry", None)
            print(f"TELEMETRY {label} ({mod.__name__}): {tele}", flush=True)
        return 0

    log(f"# e80_gate8 challenger={key} agent={cpath.name} engine={version} "
        f"interval={INTERVAL} seeds={SEEDS}")
    skip = done_keys(log_path)
    if skip:
        log(f"RESUME: skipping {len(skip)} logged games")
    for seed in SEEDS:
        for swap in (False, True):
            if (seed, int(swap)) in skip:
                continue
            row = play(seed, swap)
            log(f"GAME seed={row['seed']} swap={row['swap']} chal={row['our']:.0f} "
                f"base={row['opp']:.0f} delta={row['delta']:+.0f} "
                f"cstatus={row['cstatus']} bstatus={row['bstatus']} "
                f"secs={row['secs']:.1f} {row['note']}")

    rows = parse_rows(log_path)
    w = sum(1 for r in rows if r["delta"] > 0)
    l = sum(1 for r in rows if r["delta"] < 0)
    t = sum(1 for r in rows if r["delta"] == 0)
    mean = sum(r["delta"] for r in rows) / len(rows) if rows else 0.0
    margins = sorted(round(r["delta"]) for r in rows)
    log(f"TOTAL e80_{key} vs r78u: W{w}/L{l}/T{t} mean {mean:+.0f} games={len(rows)}")
    json.dump({"challenger": key, "agent": cpath.name, "engine": version,
               "W": w, "L": l, "T": t, "mean_margin": mean, "games": len(rows),
               "margins": margins, "rows": rows},
              json_path.open("w", encoding="utf-8"), indent=1)
    assert_champ_md5("end", log)
    log_f.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
