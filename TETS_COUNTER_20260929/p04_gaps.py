"""E256 p04 - paired our-vs-opponent gap per farm-decision column, over the loss set.

For each loss replay: ours (tetsutani seat) minus the winner seat, per column; plus the money-gap
development by day.  Prints the ranked columns by mean gap and by share of games lost with that gap.
"""
import csv
import json
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

NUM = ["final_money", "money_peak", "quads_max", "unlock_NW", "unlock_NE", "unlock_SW", "unlock_SE",
       "buy_land_ops", "tile_days_planted", "tile_days_empty", "tile_days_fert", "tile_days_watered",
       "td_WHEAT", "td_CARROT", "td_TOMATO", "td_STRAWBERRY", "td_MELON",
       "op_PLANT", "op_HARVEST", "op_WATER", "op_FERTILIZE", "op_CARE", "op_FEED", "op_PICKUP",
       "op_DROP", "op_PLACE", "op_DIG", "op_PASS", "op_MOVE", "op_BUILD_PASTURE", "op_BUILD_COOP",
       "plants", "clears", "replug_latency", "hires_max", "hires_mean", "shed_peak", "shed_end",
       "sell_units", "sell_orders", "buy_seed", "buy_product", "buy_animal", "animals_bought",
       "op_COLLECT_FERTILIZER", "fert_stock_mean", "fert_stock_peak",
       "revenue", "spend", "plant_NW", "plant_NE", "plant_SW", "plant_SE", "final_planted"]


def main():
    rows = list(csv.DictReader(open(os.path.join(OUT, "farm_anatomy.csv"), encoding="utf-8")))
    by_ep = defaultdict(dict)
    for r in rows:
        by_ep[int(r["episode"])][r["ours"] == "1"] = r
    pairs = []
    for ep, seats in sorted(by_ep.items()):
        if True not in seats or False not in seats:
            continue
        ours, opp = seats[True], seats[False]
        kind = ours["kind"]
        d = {"episode": ep, "kind": kind, "label": ours["label"], "ref": ours["ref"],
             "opp_name": opp["agent_name"], "margin": float(ours["margin"] or 0),
             "our_money": float(ours["final_money"] or 0), "opp_money": float(opp["final_money"] or 0)}
        for k in NUM:
            try:
                d[k] = float(ours[k] or 0) - float(opp[k] or 0)
            except (TypeError, ValueError):
                d[k] = 0.0
        pairs.append(d)
    losses = [p for p in pairs if p["kind"] == "L"]
    wins = [p for p in pairs if p["kind"] == "W"]
    print("pairs=%d losses=%d wins=%d" % (len(pairs), len(losses), len(wins)))
    with open(os.path.join(OUT, "paired_gaps.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pairs[0].keys()))
        w.writeheader()
        w.writerows(pairs)

    def report(sel, title):
        if not sel:
            return
        print("\n### %s (n=%d)  mean margin %+.0f" % (title, len(sel),
                                                      statistics.mean(p["margin"] for p in sel)))
        print("%-20s %10s %10s %8s %8s" % ("column", "mean_gap", "median", "n_neg", "n_zero"))
        ranked = []
        for k in NUM:
            vals = [p[k] for p in sel]
            mg = statistics.mean(vals)
            scale = max(abs(mg), 1e-9)
            ranked.append((abs(mg) / scale * abs(mg), k, mg, statistics.median(vals),
                           sum(v < 0 for v in vals), sum(v == 0 for v in vals)))
        ranked.sort(key=lambda x: -abs(x[2]))
        for _, k, mg, md, nn, nz in ranked[:24]:
            print("%-20s %10.1f %10.1f %8d %8d" % (k, mg, md, nn, nz))

    report(losses, "LOSSES - our minus winner")
    report([p for p in losses if p["margin"] <= -3000], "HEAVY LOSSES (margin <= -3000)")
    report([p for p in losses if p["margin"] > -1000], "TAIL LOSSES (margin > -1000, mirror class)")
    report(wins, "WINS - our minus loser (control)")

    # money gap by day (from curves)
    cur = list(csv.DictReader(open(os.path.join(OUT, "money_curves.csv"), encoding="utf-8")))
    gap_by_day = defaultdict(list)
    per = defaultdict(lambda: defaultdict(dict))
    for c in cur:
        if c["kind"] != "L":
            continue
        per[int(c["episode"])][int(c["day"])][c["ours"]] = float(c["money"])
    for ep, days in per.items():
        for day, seats in days.items():
            if "1" in seats and "0" in seats:
                gap_by_day[day].append(seats["1"] - seats["0"])
    print("\n### money gap (ours - winner) by day, losses only")
    for day in sorted(gap_by_day):
        v = gap_by_day[day]
        print("day %2d  mean %+9.0f  median %+9.0f  n=%d" % (day, statistics.mean(v),
                                                             statistics.median(v), len(v)))
    return 0


if __name__ == "__main__":
    main()
