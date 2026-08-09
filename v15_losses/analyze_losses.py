"""Analyze V15's 5 real Kaggle losses with the SEB-analysis methodology.

For each replay: extract per-player strategic profiles (land buys, hires, seeds,
animals, sells w/ timing, farmer/hand actions, planting, shed snapshots) and
compare winner vs V15. Mirrors seb_analysis fields for direct comparison.
"""
import json, glob, os, collections

OUT = r"C:\Users\xxshi\Desktop\farmmasterV2\v15_losses"
AN = os.path.join(OUT, "analysis")
os.makedirs(AN, exist_ok=True)

MY_TEAM = "Shivam_2212"


def seat_of(info):
    names = info.get("TeamNames", [])
    return 0 if names[0] == MY_TEAM else 1


def analyze(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    info = d.get("info", {})
    seed = info.get("seed")
    rewards = d.get("rewards", [])
    names = info.get("TeamNames", [])
    me = seat_of(info)
    opp = 1 - me
    steps = d["steps"]

    # per-seat aggregators
    S = [{k: collections.Counter() for k in [
            "farmer", "hands", "market", "hires_by_day", "seed_buys",
            "animal_buys", "product_buys", "land_buys", "sells",
            "sells_by_day", "plant_by_day"]} for _ in range(2)]
    land_batches = [[], []]
    sell_timeline = [[], []]
    shed_snapshots = [[], []]
    hands_over_time = [[], []]
    tiles_unlocked = [[], []]
    water_fertilize = [[], []]
    max_hands = [0, 0]
    pasture = [0, 0]

    for t, st in enumerate(steps):
        for s in (0, 1):
            act = st[s].get("action") or {}
            obs = st[s].get("observation") or {}
            # farmer + hands
            f_act = act.get("farmer") or []
            if f_act:
                S[s]["farmer"][f_act[0]] += 1
            for h in act.get("hands") or []:
                if h:
                    S[s]["hands"][h[0]] += 1
            # market
            for m in act.get("market") or []:
                if not isinstance(m, list) or not m:
                    continue
                op = m[0]
                S[s]["market"][op] += 1
                if op == "HIRE":
                    S[s]["hires_by_day"][obs.get("day", 0)] += 1
                elif op == "BUY_SEED":
                    S[s]["seed_buys"][m[1]] += 1
                elif op == "BUY_ANIMAL":
                    S[s]["animal_buys"][m[1]] += 1
                elif op == "BUY_PRODUCT":
                    S[s]["product_buys"][m[1]] += 1
                elif op == "BUY_LAND":
                    S[s]["land_buys"][t] += 1
                    land_batches[s].append((t, act.get("market")))
                elif op == "SELL" and len(m) >= 3:
                    S[s]["sells"][m[1]] += m[2]
                    S[s]["sells_by_day"][(obs.get("day", 0), m[1])] += m[2]
                    sell_timeline[s].append((t, m[1], m[2]))
            # farm state
            farms = obs.get("farms") or []
            if s < len(farms):
                farm = farms[s]
                nh = len(farm.get("hands") or [])
                hands_over_time[s].append((t, nh))
                max_hands[s] = max(max_hands[s], nh)
                quads = farm.get("unlocked_quadrants") or []
                tiles_unlocked[s].append((t, len(quads)))
                money = farm.get("money", 0)
                if t % 120 == 0 or t == 719:
                    shed_snapshots[s].append((t, money,
                        dict(obs.get("private", {}).get("shed") or {})))
            # farmer water/fertilize
            if f_act and f_act[0] in ("WATER", "FERTILIZE"):
                water_fertilize[s].append((t, f_act[0]))

    return dict(
        path=path, seed=seed, names=names, me=me, rewards=rewards,
        steps=steps, S=S, land_batches=land_batches, sell_timeline=sell_timeline,
        shed_snapshots=shed_snapshots, hands_over_time=hands_over_time,
        tiles_unlocked=tiles_unlocked, max_hands=max_hands,
        water_fertilize=water_fertilize,
    )


def report(r):
    lines = []
    me, opp = r["me"], 1 - r["me"]
    names = r["names"]
    lines.append("=" * 78)
    lines.append(f"SEED {r['seed']} | {names[0]} {r['rewards'][0]:.0f} vs {names[1]} {r['rewards'][1]:.0f}")
    lines.append("=" * 78)
    for s in (me, opp):
        tag = "V15(ME)" if s == me else "OPPONENT"
        S = r["S"][s]
        lines.append(f"\n--- {tag}: {names[s]} ---")
        lines.append(f"  reward: {r['rewards'][s]:.0f}")
        lines.append(f"  max hands: {r['max_hands'][s]} | land buys: {sum(S['land_buys'].values())} "
                     f"@ {sorted(S['land_buys'].keys())}")
        lines.append(f"  seeds: {dict(S['seed_buys'])}")
        lines.append(f"  animals: {dict(S['animal_buys'])}")
        lines.append(f"  product buys: {dict(S['product_buys'])}")
        lines.append(f"  sells: {dict(S['sells'])}")
        # sells by day for high value
        hv = {k: v for (d, k), v in sorted(S['sells_by_day'].items()) if k in
              ("STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "WHEAT")}
        days = sorted(set(d for d, k in S['sells_by_day']))
        per_day = collections.defaultdict(dict)
        for (d, k), v in S['sells_by_day'].items():
            per_day[d][k] = v
        lines.append(f"  sells by day: {dict(per_day)}")
        lines.append(f"  farmer top: {S['farmer'].most_common(8)}")
        lines.append(f"  farmer PASS: {S['farmer'].get('PASS', 0)}/{720} "
                     f"({100*S['farmer'].get('PASS',0)/720:.1f}%)")
        lines.append(f"  hands top: {S['hands'].most_common(6)}")
        lines.append(f"  water/fertilize farmer turns: {len(r['water_fertilize'][s])}")
        # shed snapshots
        lines.append(f"  shed snapshots:")
        for t, money, shed in r["shed_snapshots"][s]:
            hv_sh = {k: v for k, v in shed.items() if v}
            lines.append(f"    step {t:>3} money {money:>8.0f} shed {hv_sh}")
        # quadrant unlock timing
        prev = 0
        for t, q in r["tiles_unlocked"][s]:
            if q > prev:
                lines.append(f"    quadrants {q} @ step {t} (day {t//24})")
                prev = q
    return "\n".join(lines)


def main():
    files = sorted(glob.glob(os.path.join(OUT, "*_replay.json")))
    all_reports = []
    for fp in files:
        r = analyze(fp)
        txt = report(r)
        base = os.path.basename(fp).replace("_replay.json", "")
        with open(os.path.join(AN, f"{base}_report.txt"), "w", encoding="utf-8") as f:
            f.write(txt)
        all_reports.append(r)
        print(f"wrote {base}_report.txt")

    # Cross-game summary table
    print("\n=== CROSS-GAME SUMMARY ===")
    print(f"{'MATCH':<28} {'SEED':>12} {'ME':>8} {'OPP':>8} {'RES':>5} "
          f"{'my_sells_S/M/W':>18} {'opp_sells_S/M/W':>18}")
    for r in all_reports:
        me, opp = r["me"], 1 - r["me"]
        my_sells = sum(r["S"][me]["sells"].get(k, 0) for k in ("STRAWBERRY", "MILK", "WOOL"))
        opp_sells = sum(r["S"][opp]["sells"].get(k, 0) for k in ("STRAWBERRY", "MILK", "WOOL"))
        res = "LOSS" if r["rewards"][me] < r["rewards"][opp] else ("WIN" if r["rewards"][me] > r["rewards"][opp] else "TIE")
        print(f"{os.path.basename(r['path']):<28} {r['seed']:>12} {r['rewards'][me]:>8.0f} "
              f"{r['rewards'][opp]:>8.0f} {res:>5} {my_sells:>18} {opp_sells:>18}")

    # Aggregate strategy deltas
    print("\n=== AGGREGATE (5 losses): V15 vs opponent ===")
    agg = [collections.Counter() for _ in range(2)]
    agg_land = [0, 0]
    agg_hands = [0, 0]
    for r in all_reports:
        me, opp = r["me"], 1 - r["me"]
        for k in ("seed_buys", "animal_buys", "product_buys", "sells"):
            for item, v in r["S"][me][k].items():
                agg[0][f"{k}:{item}"] += v
            for item, v in r["S"][opp][k].items():
                agg[1][f"{k}:{item}"] += v
        agg_land[0] += sum(r["S"][me]["land_buys"].values())
        agg_land[1] += sum(r["S"][opp]["land_buys"].values())
        agg_hands[0] += r["max_hands"][me]
        agg_hands[1] += r["max_hands"][opp]
    items = set(agg[0]) | set(agg[1])
    print(f"{'metric':<30} {'V15 total':>10} {'OPP total':>10}")
    for k in sorted(items):
        print(f"{k:<30} {agg[0].get(k,0):>10} {agg[1].get(k,0):>10}")
    print(f"{'land buys':<30} {agg_land[0]:>10} {agg_land[1]:>10}")
    print(f"{'max hands sum':<30} {agg_hands[0]:>10} {agg_hands[1]:>10}")


if __name__ == "__main__":
    main()
