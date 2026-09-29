"""E256 p05 - heaviest-loss side-by-side detail (ours vs the seat that beat us)."""
import csv
import json
from collections import defaultdict

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
COLS = ["final_money", "sell_units", "sell_orders", "tile_days_planted", "tile_days_fert",
        "op_FERTILIZE", "op_COLLECT_FERTILIZER", "op_FEED", "op_CARE", "op_PICKUP", "op_WATER",
        "hires_max", "animals_bought", "buy_product", "buy_seed", "buy_land_ops",
        "revenue", "spend", "shed_peak", "fert_stock_peak", "fert_stock_mean",
        "td_WHEAT", "td_TOMATO", "td_STRAWBERRY", "td_CARROT", "td_MELON", "op_PASS", "op_MOVE",
        "replug_latency", "quads_max", "unlock_SE", "plant_SE", "tile_days_empty"]


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def main():
    rows = list(csv.DictReader(open(os.path.join(OUT, "farm_anatomy.csv"), encoding="utf-8")))
    by_ep = defaultdict(dict)
    for r in rows:
        by_ep[r["episode"]]["ours" if r["ours"] == "1" else "opp"] = r
    pairs = [(e, d["ours"], d["opp"]) for e, d in by_ep.items() if "ours" in d and "opp" in d]
    losses = sorted([p for p in pairs if p[1]["kind"] == "L"], key=lambda p: f(p[1]["margin"]))
    wins = sorted([p for p in pairs if p[1]["kind"] == "W"], key=lambda p: -f(p[1]["margin"]))
    for title, sel in (("HEAVIEST LOSSES", losses[:6]), ("BIGGEST WINS (control)", wins[:2])):
        print("\n=====", title)
        for e, o, p in sel:
            print("--- ep %s margin %+.0f  %s  vs %s" % (e, f(o["margin"]), o["label"], p["agent_name"]))
            print("   %-24s %12s %12s %10s" % ("column", "OURS", "WINNER", "gap"))
            for c in COLS:
                print("   %-24s %12.0f %12.0f %+10.0f" % (c, f(o[c]), f(p[c]), f(o[c]) - f(p[c])))
            so, sp = json.loads(o["sell_item"]), json.loads(p["sell_item"])
            keys = sorted(set(so) | set(sp), key=lambda k: -(sp.get(k, 0)))
            print("   sell_item ours/winner:", {k: (so.get(k, 0), sp.get(k, 0)) for k in keys[:10]})
            bo, bp = json.loads(o["buy_item"]), json.loads(p["buy_item"])
            print("   buy_item ours:", {k: v for k, v in sorted(bo.items(), key=lambda x: -x[1])[:6]},
                  "| winner:", {k: v for k, v in sorted(bp.items(), key=lambda x: -x[1])[:6]})
    return 0


if __name__ == "__main__":
    main()
