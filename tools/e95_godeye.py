"""E95 god's-eye view: re-run one ladder world for BOTH E94 and r78u (each in a
fresh subprocess to avoid module-cache mirrors), verify the per-step action hash
chain matches results/e95_ladder.jsonl (same world), then print a day-by-day
state comparison + action/state divergences.

Usage: python tools/e95_godeye.py --opp salem2900 --seed 1000000 --swap 0 [--full]
"""
import argparse, hashlib, json, pathlib, subprocess, sys, os

BASE = pathlib.Path(__file__).resolve().parents[1]

ap = argparse.ArgumentParser()
ap.add_argument("--opp", required=True)
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--swap", type=int, choices=(0, 1), required=True)
ap.add_argument("--var", choices=("e94", "r78u"))
ap.add_argument("--full", action="store_true")
args = ap.parse_args()

SNAP = lambda v: BASE / "results" / f"e95_godeye.{args.opp}.{args.seed}.{args.swap}.{v}.json"


def play_one(var):
    # child mode: load everything lazily so parent stays light
    sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE / "tools"))
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    import e95_ladder as L
    assert L.md5(L.CHAMP) == L.CHAMP_MD5 and L.md5(L.E94) == L.E94_MD5
    L.assert_engine()
    path, band, _ = L.POOL[args.opp]
    opp_fn = L.noop_agent if path == "__noop__" else L.entry(L.load(path, "gd_opp"))
    vpath = L.E94 if var == "e94" else L.CHAMP
    fn = L.entry(L.load(vpath, f"gd_{var}"))
    chain, snaps = [], []

    def wrap(obs, cfg=None):
        if isinstance(obs, str):
            obs = json.loads(obs)
        a = fn(obs, cfg)
        chain.append(hashlib.sha1(L.norm(a).encode()).hexdigest()[:8])
        if len(snaps) < 719 and obs["hour"] in (0, 23):
            priv = obs["private"]
            priv = json.loads(priv) if isinstance(priv, str) else priv
            me = obs["player"]
            farm = obs["farms"][me]
            tiles = [t for row in farm["tiles"] for t in row if isinstance(t, dict)]
            snaps.append({
                "step": obs["step"], "day": obs["day"], "hour": obs["hour"],
                "money": farm["money"], "omoney": obs["farms"][1 - me]["money"],
                "crops": sorted(t.get("crop") for t in tiles if t.get("crop")),
                "unlocked": sum(1 for row in farm["tiles"] for t in row
                                if t != "LOCKED" and t is not None),
                "shed": {k: v for k, v in (priv.get("shed") or {}).items() if v},
                "seeds": {k: v for k, v in (priv.get("seeds") or {}).items() if v},
                "shops": [s.get("name") if isinstance(s, dict) else s
                          for s in (obs["town"]["unlocked_shops"] or [])],
                "act": a,
            })
        return a

    f0, f1 = (wrap, opp_fn) if not args.swap else (opp_fn, wrap)
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": args.seed,
                                               "townCenterSellInterval": L.INTERVAL}, debug=False)
    try:
        env.run([f0, f1])
    except Exception as e:
        print("CRASH", repr(e)[:200])
    rw = [float(env.state[i].get("reward", 0) or 0) for i in (0, 1)]
    SNAP(var).write_text(json.dumps({"chain": chain, "snaps": snaps, "our": rw[args.swap]}))
    print(f"{var} done reward={rw[args.swap]:.0f} snaps={len(snaps)}")


def report():
    exp = {}
    for line in (BASE / "results" / "e95_ladder.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if (r["opp"], r["seed"], r["swap"]) == (args.opp, args.seed, args.swap):
            exp[r["var"]] = r
    if set(exp) != {"e94", "r78u"}:
        raise SystemExit("ladder rows incomplete for this world")
    print(f"world {args.opp} seed{args.seed} swap{args.swap}")
    res = {}
    for v in ("e94", "r78u"):
        d = json.loads(SNAP(v).read_text(encoding="utf-8"))
        ok = d["chain"] == exp[v]["hashes"]
        print(f"{v}: reward {d['our']:.0f} ladder {exp[v]['our']:.0f} | chain match: {ok}"
              f"{'' if ok else '  <-- WORLD DRIFT'}")
        res[v] = {s["step"]: s for s in d["snaps"]}
    steps = sorted(set(res["e94"]) & set(res["r78u"]))
    act_div = [s for s in steps
               if json.dumps(res["e94"][s]["act"], sort_keys=True) !=
                  json.dumps(res["r78u"][s]["act"], sort_keys=True)]
    mat = next((s for s in steps if (res["e94"][s]["money"], res["e94"][s]["unlocked"],
                tuple(sorted(res["e94"][s]["crops"]))) !=
                (res["r78u"][s]["money"], res["r78u"][s]["unlocked"],
                 tuple(sorted(res["r78u"][s]["crops"])))), None)
    print(f"action divergences: {len(act_div)} steps; first material state divergence: step {mat}")

    def h24(s):  # snapshots at hour 0 and 23 of each day
        return s["day"] * 100 + s["hour"]
    days = sorted({res["e94"][s]["day"] for s in steps})
    show = days if args.full else days[::3]
    print(f"\n{'day':>3} | {'E94 $':>9} {'r78 $':>9} {'d$':>9} | {'E94 t':>5} {'r78 t':>5} | E94 shed vs r78 shed")
    for dy in show:
        ds = [s for s in steps if res["e94"][s]["day"] == dy]
        if not ds or not all(res["r78u"].get(s) for s in ds):
            continue
        pick = [s for s in ds if res["e94"][s]["hour"] == 23] or [ds[-1]]
        e, r = res["e94"][pick[-1]], res["r78u"][pick[-1]]
        print(f"{dy:>3} | {e['money']:>9.0f} {r['money']:>9.0f} {e['money']-r['money']:>+9.0f} |"
              f" {len(e['crops']):>5} {len(r['crops']):>5} | {e['shed']} vs {r['shed']}")

    print("\nfirst 30 action divergences:")
    for s in act_div[:30]:
        e, r = res["e94"][s], res["r78u"][s]
        print(f"  s{s} d{e['day']}h{e['hour']}  E94: {json.dumps(e['act'],sort_keys=True)[:105]}")
        print(f"  {'':>{len(str(s))+10}}  r78: {json.dumps(r['act'],sort_keys=True)[:105]}")


if args.var:
    sys.exit(play_one(args.var))

for v in ("e94", "r78u"):
    with open(SNAP(v).with_suffix(".run.txt"), "w", encoding="utf-8") as fh:
        subprocess.run([sys.executable, str(BASE / "tools" / "e95_godeye.py"),
                        "--opp", args.opp, "--seed", str(args.seed),
                        "--swap", str(args.swap), "--var", v], check=True,
                       stdout=fh, stderr=subprocess.DEVNULL)
report()
