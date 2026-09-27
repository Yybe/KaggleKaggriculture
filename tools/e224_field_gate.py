"""E224 absolute-field gate: runs each arm against 5 unrelated lineages on the SAME fresh
seeds (both seat orders), writing per-game rows so between-arm deltas are paired.

usage: python tools/e224_field_gate.py [arm1.py arm2.py ...]   (default: the 4 registered arms)
Seeds: 15243000 + i*1117, i in [0,3)  - registry E224, unseen by any arm.
Engine pin asserted (kaggle-environments==1.32.7). Output: results/e224_field_gate/<arm>.csv
"""
import csv
import importlib.util
import io
import os
import statistics as st
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO = r"C:/Users/xxshi/Desktop/farmmasterV2"
sys.path.insert(0, os.path.join(REPO, "tools"))
from test_candidate_breakthrough import engine_pin_error  # noqa: E402

_pin = engine_pin_error()
if _pin:
    raise SystemExit("ENGINE PIN REFUSED: " + _pin)

CROPS = {"CARROT", "MELON", "STRAWBERRY", "TOMATO", "WHEAT"}
PANEL = [
    "agents/pub_dynroute85.py",
    "agents/pub_e69_soilrouter.py",
    "agents/salemali7_3094.py",
    "agents/pub_farmer_john_v56.py",
    "agents/friend_r78ub.py",
]
SEEDS = [15243000, 15244117, 15245234]
OUT_DIR = os.path.join(REPO, "results", "e224_field_gate")
os.makedirs(OUT_DIR, exist_ok=True)

DEFAULT_ARMS = [
    "agents/sluice_topup7.py",
    "agents/cha22_champion.py",
    "agents/cha22_e199_lo96q8.py",
    "agents/pixelx_v2.py",
]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def seat_features(steps, seat):
    crops, peak_crew, first_land, hires_day = {}, 0, None, {}
    money = []
    for t, step in enumerate(steps):
        farm = step[0]["observation"]["farms"][seat]
        day = t // 24
        money.append(farm.get("money", 0))
        hires_day[day] = max(hires_day.get(day, 0), farm.get("hires_today", 0) or 0)
        peak_crew = max(peak_crew, len(farm.get("hands") or []))
        a = step[seat].get("action") or {}
        for order in (a.get("market") or []):
            if isinstance(order, list) and order and order[0] == "BUY_LAND" and first_land is None:
                first_land = day
        for unit in [a.get("farmer") or []] + list(a.get("hands") or []):
            if isinstance(unit, list) and unit and unit[0] == "PLANT" and len(unit) > 1 and unit[1] in CROPS:
                crops[unit[1]] = crops.get(unit[1], 0) + 1
    row = {"final_money": money[-1] if money else 0, "peak_crew": peak_crew,
           "total_hires": sum(hires_day.values()), "first_land_day": first_land,
           "tiles_planted": sum(crops.values())}
    for c in CROPS:
        row[f"plants_{c.lower()}"] = crops.get(c, 0)
    return row


def one_game(job):
    import traceback
    cand, opp, seed, swap = job
    try:
        from kaggle_environments import make
        ma = _load(cand, f"c_{os.path.basename(cand)}_{seed}_{swap}")
        mo = _load(opp, f"o_{os.path.basename(opp)}_{seed}_{swap}")
        ca = ma.agent if not swap else mo.agent
        cb = mo.agent if not swap else ma.agent
        env = make("kaggriculture", configuration={
            "episodeSteps": 720, "seed": seed, "townCenterSellInterval": 24}, debug=False)
        env.run([ca, cb])
        ours = 1 if swap else 0
        fs = seat_features(env.steps, ours)
        fo = seat_features(env.steps, 1 - ours)
        fs["reward"] = float(env.steps[-1][ours].reward)
        fo["reward"] = float(env.steps[-1][1 - ours].reward)
        return {"cand": os.path.basename(cand), "opp": os.path.basename(opp), "seed": seed,
                "swap": swap, "err": "", "us": fs, "oppf": fo}
    except Exception as exc:  # noqa: BLE001
        return {"cand": os.path.basename(cand), "opp": os.path.basename(opp), "seed": seed,
                "swap": swap, "err": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-300:]}",
                "us": None, "oppf": None}


def run(agent, panel, seeds, out_csv):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    abs_agent = agent if os.path.isabs(agent) else os.path.join(REPO, agent)
    panel = [os.path.join(REPO, p) for p in panel if os.path.exists(os.path.join(REPO, p))]
    tasks = [(abs_agent, p, s, sw) for p in panel for s in seeds for sw in (False, True)]
    print(f"\n{'='*78}\n{os.path.basename(abs_agent)}  vs {len(panel)} lineages x {len(seeds)} seeds "
          f"x 2 seats = {len(tasks)} games", flush=True)
    print(f"  sha1 {__import__('hashlib').sha1(open(abs_agent,'rb').read()).hexdigest()}  "
          f"{os.path.getsize(abs_agent)} B", flush=True)
    rows = []
    jobs = 6
    while True:
        try:
            with ProcessPoolExecutor(max_workers=jobs, max_tasks_per_child=1) as ex:
                futs = {ex.submit(one_game, t): t for t in tasks}
                for i, fu in enumerate(as_completed(futs)):
                    try:
                        rows.append(fu.result())
                    except Exception as exc:  # noqa: BLE001
                        t = futs[fu]
                        rows.append({"cand": os.path.basename(t[0]), "opp": os.path.basename(t[1]),
                                     "seed": t[2], "swap": t[3],
                                     "err": f"POOL: {type(exc).__name__}: {exc}", "us": None, "oppf": None})
                    if (i + 1) % 10 == 0:
                        print(f"  {i+1}/{len(futs)} games done", flush=True)
            break
        except Exception as exc:  # noqa: BLE001
            jobs //= 2
            print(f"  pool failed ({type(exc).__name__}); jobs={jobs}", flush=True)
            if jobs < 1:
                print("  falling back to sequential", flush=True)
                rows = [one_game(t) for t in tasks]
                break
    errs = [r for r in rows if r["err"]]
    ok = [r for r in rows if r["us"]]
    print(f"  completed {len(ok)}, errors {len(errs)}", flush=True)
    for e in errs[:4]:
        print(f"    ERR {e['opp']} seed {e['seed']} swap {e['swap']}: {e['err'][:200]}", flush=True)
    cols = ["final_money", "reward", "tiles_planted", "plants_tomato", "plants_carrot",
            "plants_wheat", "plants_strawberry", "plants_melon", "peak_crew", "total_hires"]
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["cand", "opp", "seed", "swap", "side"] + cols)
        for r in ok:
            for side, f in (("us", r["us"]), ("opp", r["oppf"])):
                wr.writerow([r["cand"], r["opp"], r["seed"], r["swap"], side] + [f.get(c) for c in cols])
    win = sum(1 for r in ok if r["us"]["reward"] > r["oppf"]["reward"])
    tie = sum(1 for r in ok if r["us"]["reward"] == r["oppf"]["reward"])
    print(f"  FIELD RECORD: {win}W/{len(ok)-win-tie}L/{tie}T over {len(ok)} games  "
          f"win%={100*win/max(len(ok),1):.1f}", flush=True)
    print(f"  mean bank ours {st.mean(r['us']['final_money'] for r in ok):,.0f}  "
          f"opp {st.mean(r['oppf']['final_money'] for r in ok):,.0f}", flush=True)
    print(f"  profile: tiles {st.mean(r['us']['tiles_planted'] for r in ok):.1f}  "
          f"tomato {st.mean(r['us']['plants_tomato'] for r in ok):.1f}  "
          f"carrot {st.mean(r['us']['plants_carrot'] for r in ok):.1f}  "
          f"wheat {st.mean(r['us']['plants_wheat'] for r in ok):.1f}  "
          f"crew {st.mean(r['us']['peak_crew'] for r in ok):.1f}  "
          f"hires {st.mean(r['us']['total_hires'] for r in ok):.1f}", flush=True)
    byo = {}
    for r in ok:
        byo.setdefault(r["opp"], []).append(r)
    print("  per-opponent: bank mean / win%", flush=True)
    for o, rs in sorted(byo.items()):
        w = sum(1 for r in rs if r["us"]["reward"] > r["oppf"]["reward"])
        print(f"    {os.path.basename(o):<28} n={len(rs):>2} bank={st.mean(r['us']['final_money'] for r in rs):>9,.0f} "
              f"oppBank={st.mean(r['oppf']['final_money'] for r in rs):>9,.0f} win={w}/{len(rs)}", flush=True)
    return ok


def main():
    args = [a for a in sys.argv[1:]]
    arms = args or DEFAULT_ARMS
    for a in arms:
        path = a if os.path.isabs(a) else os.path.join(REPO, a)
        if not os.path.exists(path):
            print(f"MISSING ARM: {a}")
            continue
        out = os.path.join(OUT_DIR, os.path.basename(a).replace(".py", "") + ".csv")
        run(path, PANEL, SEEDS, out)


if __name__ == "__main__":
    main()
