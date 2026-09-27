"""E224 join: paired per-world bank deltas between arms on identical (opp,seed,swap) rows.

usage: python tools/e224_join.py            (joins all arms' CSVs in results/e224_field_gate/)
Prints pairwise paired deltas vs A=sluice_topup7 plus every other pair, per-lineage means,
worst world, favours count, sign-test p (exact binomial one-sided), and applies the
PRE-REGISTERED E224 rule verbatim from results/E224_FIELD_RANK_PREREG_20260928.md.
"""
import csv
import glob
import math
import os
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "results", "e224_field_gate")


def load():
    worlds = defaultdict(dict)   # arm -> (opp,seed,swap) -> bank ; oppf stored too
    for path in sorted(glob.glob(os.path.join(D, "*.csv"))):
        arm = os.path.basename(path)[:-4]
        if arm == "run":
            continue
        with open(path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row["side"] != "us":
                    continue
                key = (row["opp"], int(row["seed"]), row["swap"] == "True")
                worlds[arm][key] = {"bank": float(row["final_money"]), "reward": float(row["reward"]),
                                    "opp": row["opp"]}
    return worlds


def sign_p(n_fav, n):
    if n == 0:
        return float("nan")
    k = max(n_fav, n - n_fav)
    p = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return p


def main():
    w = load()
    arms = [a for a in ["sluice_topup7", "cha22_champion", "cha22_e199_lo96q8", "pixelx_v2"] if a in w]
    if len(arms) < 2:
        print("need >=2 arm csvs in", D, "got", sorted(w))
        return
    base = [a for a in arms if a == "sluice_topup7"]
    pairs = []
    if base:
        pairs = [(a, "sluice_topup7") for a in arms if a != "sluice_topup7"]
    for i, x in enumerate(arms):
        for y in arms[i + 1:]:
            if (x, y) not in pairs and (y, x) not in pairs:
                pairs.append((x, y))
    print(f"{'pair':<44}{'n':>4}{'mean':>9}{'median':>9}{'worst':>9}{'best':>9}{'fav':>6}{'p1s':>7}")
    results = {}
    for x, y in pairs:
        keys = sorted(set(w[x]) & set(w[y]))
        deltas = [w[x][k]["bank"] - w[y][k]["bank"] for k in keys]
        if not deltas:
            print(f"{x+' - '+y:<44}  NO SHARED WORLDS")
            continue
        fav = sum(1 for d in deltas if d > 0)
        p = sign_p(fav, len(deltas))
        print(f"{x+' - '+y:<44}{len(deltas):>4}{sum(deltas)/len(deltas):>9,.0f}"
              f"{sorted(deltas)[len(deltas)//2]:>9,.0f}{min(deltas):>9,.0f}{max(deltas):>9,.0f}"
              f"{fav:>4}/{len(deltas):<2}{p:>7.4f}")
        results[(x, y)] = (deltas, fav, p)
        byo = defaultdict(list)
        for k, d in zip(keys, deltas):
            byo[k[0]].append(d)
        for o in sorted(byo):
            ds = byo[o]
            print(f"    vs {o:<26} n={len(ds)} mean={sum(ds)/len(ds):>9,.0f} worst={min(ds):>9,.0f}")

    print("\n--- pre-registered rule (E224_FIELD_RANK_PREREG_20260928.md) ---")
    champ = "sluice_topup7"
    ok_arms = {}
    for x, y in pairs:
        if y != champ or (x, y) not in results:
            continue
        deltas, fav, p = results[(x, y)]
        n = len(deltas)
        mean = sum(deltas) / n
        byo = defaultdict(list)
        # rebuild byo from stored worlds
        keys = sorted(set(w[x]) & set(w[y]))
        for k in keys:
            byo[k[0]].append(w[x][k]["bank"] - w[y][k]["bank"])
        cond1 = mean > 0
        cond2 = fav >= math.ceil(9 / 15 * n) if n <= 15 else fav >= 9
        cond3 = all(sum(ds) / len(ds) > -1000 for ds in byo.values())
        cond4 = min(deltas) >= -2500
        ok_arms[x] = (mean, cond1, cond2, cond3, cond4, min(deltas))
        print(f"{x}: mean {mean:+,.0f}  fav {fav}/{n}  per-lineage-ok {cond3}  worst {min(deltas):+,.0f}  "
              f"=> {'QUALIFIES' if all([cond1, cond2, cond3, cond4]) else 'fails rule'}")
    if ok_arms:
        qual = {a: v for a, v in ok_arms.items() if all(v[1:5])}
        if qual:
            win = max(qual, key=lambda a: qual[a][0])
            print(f"SUBMISSION WINNER: {win} (mean vs champion {qual[win][0]:+,.0f})")
        else:
            print("NO ARM QUALIFIES: champion of record stays; submission = sluice_topup7")


if __name__ == "__main__":
    main()
