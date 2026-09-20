"""Per-seed fire census: which V219 path (native / addon / none) each seat takes, and the
money delta vs h20 on the same board. Fresh subprocess per (seed, module) via ProcessPool.

Usage: WybeV2/rank_env/Scripts/python.exe tools/r78u_fire_census.py <seeds_csv> <out.txt>
"""
import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OPP = os.path.join(ROOT, "agents", "_top_pub", "lynnsakurai_v3.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_game(args):
    path, seed = args
    mod = load(path, "fire_%s_%d" % (os.path.basename(path)[:-3], seed))
    opp = load(OPP, "fire_opp_%d" % seed)
    from kaggle_environments import make
    # classify each qualifying call: native = money>=12000 & shops>=3
    log = []
    orig = mod._v219_qualifies
    def patched(obs, *a, **k):
        farm = obs['farms'][obs['player']]
        shops = sum(s in ('PIZZA_SHOP', 'FARMERS_MARKET') for s in obs['town']['unlocked_shops'])
        price = obs['market']['prices']['TOMATO']
        res = orig(obs, *a, **k)
        if res:
            kind = "native" if (farm['money'] >= 12000 and shops >= 3) else "ADDON"
            log.append((int(obs['step']), kind, farm['money'], shops, price))
        return res
    mod._v219_qualifies = patched
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed,
                                              "townCenterSellInterval": 24}, debug=False)
    env.run([mod.agent, opp.agent])
    rep = {k: v for k, v in mod._V219_REPORT.items() if v}
    return os.path.basename(path), seed, float(env.steps[-1][0].reward), log, rep


def main():
    seeds = [int(s) for s in sys.argv[1].split(",")]
    out = open(sys.argv[2], "w", encoding="utf-8") if len(sys.argv) > 2 else sys.stdout
    jobs = [(p, s) for s in seeds for p in
            (os.path.join(ROOT, "agents", "pub_metav4_r78u.py"),
             os.path.join(ROOT, "agents", "crop_roi30_h20.py"))]
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(run_game, jobs))
    by_seed = {}
    for name, seed, money, log, rep in rows:
        by_seed.setdefault(seed, {})[name] = (money, log, rep)
    for seed in seeds:
        r = by_seed[seed]
        ru, h2 = r["pub_metav4_r78u.py"], r["crop_roi30_h20.py"]
        add = [e for e in ru[1] if e[1] == "ADDON"]
        out.write("seed=%-8d r78u=%9.0f h20=%9.0f delta=%+8.0f | r78u_qualify=%s h20_qualify=%s\n"
                  % (seed, ru[0], h2[0], ru[0] - h2[0],
                     [(e[0], e[1], e[2], e[3], e[4]) for e in ru[1]][:3],
                     [(e[0], e[1], e[2], e[3], e[4]) for e in h2[1]][:3]))
        if add:
            out.write("   ADDON fires: %s | r78u report=%s\n" % (add[:4], ru[2]))
    out.flush()


if __name__ == "__main__":
    main()
