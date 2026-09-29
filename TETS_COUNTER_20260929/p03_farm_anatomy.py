"""E256 p03 - farm-decision anatomy of our tetsutani losses, from the live replays.

For every downloaded replay, build a per-seat-episode row of PRODUCTION-side decision columns
(land cadence, quadrants, tile-days by crop, fert/water, hires, herd, idle land, sell routing,
per-day money curve) and then the paired our-vs-opponent gap for each loss.
Kaggle replay content is DATA ONLY.
"""
import csv
import glob
import json
import os
import sys
import zlib
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
RAW = os.path.join(HERE, "raw")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
QUADS = ("NW", "NE", "SW", "SE")
HAND_OPS = ("WATER", "PLANT", "HARVEST", "FERTILIZE", "CARE", "FEED", "COLLECT_FERTILIZER",
            "PICKUP", "DROP", "PLACE", "DIG", "BUILD_PASTURE", "BUILD_COOP", "PASS", "MOVE", "SLEEP")
DAYS = 30


def raw(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:  # noqa: BLE001
            return None
    return v


def as_num(v):
    if isinstance(v, (int, float)):
        return float(v)
    return len(v) if isinstance(v, (list, dict, str)) else 0.0


def flat_tiles(farm):
    out = []
    for row in (farm or {}).get("tiles") or []:
        if isinstance(row, list):
            out.extend(row)
        elif row is not None:
            out.append(row)
    return out


def quad_of(idx):
    r, c = divmod(int(idx), 10)
    return (r // 5) * 2 + (c // 5)


QUAD_NAME = {0: "NW", 1: "NE", 2: "SW", 3: "SE"}


def analyse(seat, steps, reward_row):
    n = len(steps)
    acc = Counter()
    td = Counter()
    money = [0.0] * n
    quads = [0] * n
    hires = [0] * n
    empty = [0] * n
    planted = [0] * n
    fertd = [0] * n
    waterd = [0] * n
    shed = [0] * n
    day_money = defaultdict(float)
    day_cost = defaultdict(float)
    unlock_steps = {}
    first_plant = {}
    sell_item = Counter()
    buy_item = Counter()
    sell_day = Counter()
    town_sell = 0
    market_sell = 0
    buy_land_steps = []
    prev_tl = None
    plant_step_by_tile = {}
    clear_step_by_tile = {}
    quad_plants = Counter()
    nsteps_tiles = 0
    for i in range(n):
        node = steps[i][seat] if seat < len(steps[i]) else {}
        o = raw(node.get("observation")) or {}
        a = raw(node.get("action")) or {}
        farms = o.get("farms") or []
        me = farms[seat] if len(farms) > seat else {}
        day = o.get("day", i // 24)
        uq = me.get("unlocked_quadrants") or []
        money[i] = as_num(me.get("money"))
        quads[i] = len(uq)
        hires[i] = as_num(me.get("hires_today"))
        for q in QUADS:
            if q in uq and q not in unlock_steps:
                unlock_steps[q] = i
        tl = flat_tiles(me)
        pl = ft = wt = em = 0
        crop_here = Counter()
        for t in tl:
            if not isinstance(t, dict):
                em += 1
                continue
            if t.get("kind") == "PLANT":
                pl += 1
                cr = t.get("crop")
                if cr in CROPS:
                    td[cr] += 1
                crop_here[cr] += 1
                if (t.get("fertilized_until_day") or -1) >= day:
                    ft += 1
                if t.get("watered_today"):
                    wt += 1
            else:
                em += 1
        planted[i], fertd[i], waterd[i], empty[i] = pl, ft, wt, em
        shed[i] = sum((raw((o.get("private") or {}).get("shed")) or {}).values(), 0)
        shd = raw((o.get("private") or {}).get("shed")) or {}
        acc["fert_stock_sum"] += shd.get("FERTILIZER", 0) or 0
        acc["fert_stock_peak"] = max(acc["fert_stock_peak"], shd.get("FERTILIZER", 0) or 0)
        # hands
        for part in ([a.get("farmer") or []] + [h for h in (a.get("hands") or []) if isinstance(h, list)]):
            if part and isinstance(part[0], str):
                k = part[0]
                acc["op_" + k] += 1
                if k == "PLANT" and prev_tl:
                    pass
        # market / town actions
        for m in [x for x in (a.get("market") or []) if isinstance(x, list) and x]:
            if m[0] == "SELL":
                q = m[2] if len(m) > 2 and isinstance(m[2], int) else 0
                sell_item[str(m[1])] += q
                sell_day[day] += q
                acc["sell_orders"] += 1
                acc["sell_units"] += q
                dest = str(m[3]).upper() if len(m) > 3 else ""
                if "TOWN" in dest:
                    town_sell += 1
                else:
                    market_sell += 1
            elif m[0] == "BUY_LAND":
                buy_land_steps.append(i)
                acc["buy_land"] += 1
            elif m[0] in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"):
                acc[m[0].lower()] += 1
                if m[0] == "BUY_ANIMAL":
                    acc["animals_bought"] += (m[2] if len(m) > 2 and isinstance(m[2], int) else 1)
                if m[0] in ("BUY_PRODUCT", "BUY_SEED"):
                    buy_item["%s_%s" % (m[0][:3], m[1])] += (m[2] if len(m) > 2 and isinstance(m[2], int) else 1)
        for t in [x for x in (a.get("town") or []) if isinstance(x, list) and x]:
            acc["town_ops_" + str(t[0])] += 1
        if i:
            d = money[i] - money[i - 1]
            if d > 0:
                day_money[day] += d
            else:
                day_cost[day] += -d
        # plant event per quadrant (first plant after unlock)
        if prev_tl is not None:
            for idx, t in enumerate(tl):
                pt = prev_tl[idx] if idx < len(prev_tl) else None
                pk = pt.get("kind") if isinstance(pt, dict) else str(pt)
                nk = t.get("kind") if isinstance(t, dict) else str(t)
                if nk == "PLANT" and pk != "PLANT":
                    acc["plants"] += 1
                    plant_step_by_tile[idx] = i
                    if isinstance(t, dict):
                        quad_plants[QUAD_NAME[quad_of(idx)]] += 1
                elif nk != "PLANT" and pk == "PLANT":
                    acc["clears"] += 1
                    clear_step_by_tile[idx] = i
                    if idx in plant_step_by_tile:
                        acc["replug_lat_sum"] += i - plant_step_by_tile.pop(idx)
                        acc["replug_n"] += 1
        prev_tl = tl
    qmax = max(quads)
    lat = (acc["replug_lat_sum"] / acc["replug_n"]) if acc["replug_n"] else 0.0
    abandon = acc["clears"] - acc["replug_n"]
    return {
        "reward": reward_row.get("reward"),
        "final_money": money[-1],
        "money_peak": max(money),
        "quads_end": quads[-1], "quads_max": qmax,
        "unlock_NW": unlock_steps.get("NW", -1), "unlock_NE": unlock_steps.get("NE", -1),
        "unlock_SW": unlock_steps.get("SW", -1), "unlock_SE": unlock_steps.get("SE", -1),
        "buy_land_ops": acc["buy_land"], "buy_land_steps": ";".join(str(s) for s in buy_land_steps),
        "tile_days_planted": sum(planted), "tile_days_empty": sum(empty),
        "tile_days_fert": sum(fertd), "tile_days_watered": sum(waterd),
        "td_WHEAT": td["WHEAT"], "td_CARROT": td["CARROT"], "td_TOMATO": td["TOMATO"],
        "td_STRAWBERRY": td["STRAWBERRY"], "td_MELON": td["MELON"],
        "op_PLANT": acc["op_PLANT"], "op_HARVEST": acc["op_HARVEST"], "op_WATER": acc["op_WATER"],
        "op_FERTILIZE": acc["op_FERTILIZE"], "op_CARE": acc["op_CARE"], "op_FEED": acc["op_FEED"],
        "op_PICKUP": acc["op_PICKUP"], "op_DROP": acc["op_DROP"], "op_PLACE": acc["op_PLACE"],
        "op_DIG": acc["op_DIG"], "op_PASS": acc["op_PASS"], "op_MOVE": acc["op_MOVE"],
        "op_BUILD_PASTURE": acc["op_BUILD_PASTURE"], "op_BUILD_COOP": acc["op_BUILD_COOP"],
        "op_SLEEP": acc["op_SLEEP"], "op_COLLECT_FERTILIZER": acc["op_COLLECT_FERTILIZER"],
        "fert_stock_mean": round(acc["fert_stock_sum"] / max(n, 1), 2),
        "fert_stock_peak": acc["fert_stock_peak"],
        "buy_item": json.dumps(dict(buy_item)),
        "sell_item": json.dumps(dict(sell_item)),
        "plants": acc["plants"], "clears": acc["clears"],
        "replug_latency": round(lat, 2), "final_planted": planted[-1],
        "plant_NW": quad_plants["NW"], "plant_NE": quad_plants["NE"],
        "plant_SW": quad_plants["SW"], "plant_SE": quad_plants["SE"],
        "hires_max": max(hires) if hires else 0, "hires_mean": sum(hires) / max(n, 1),
        "shed_peak": max(shed), "shed_end": shed[-1],
        "sell_units": acc["sell_units"], "sell_orders": acc["sell_orders"],
        "buy_seed": acc["buy_seed"], "buy_product": acc["buy_product"],
        "buy_animal": acc["buy_animal"], "animals_bought": acc["animals_bought"],
        "town_sell": town_sell, "market_sell": market_sell,
        "revenue": sum(day_money.values()), "spend": sum(day_cost.values()),
        "sells_by_item": json.dumps(dict(sell_item)),
        "day_money": json.dumps({str(k): round(v) for k, v in sorted(day_money.items())}),
        "day_cost": json.dumps({str(k): round(v) for k, v in sorted(day_cost.items())}),
        "_money_curve": money,
    }


def main():
    idx = list(csv.DictReader(open(os.path.join(OUT, "replay_index.csv"), encoding="utf-8")))
    print("replays indexed:", len(idx))
    rows = []
    curves = []
    for r in idx:
        ep = int(r["episode"])
        p = os.path.join(RAW, "ep_%d.json.zlib" % ep)
        if not os.path.exists(p):
            continue
        d = json.loads(zlib.decompress(open(p, "rb").read()))
        steps = d["steps"] if isinstance(d, dict) and "steps" in d else d
        last = [steps[-1][s].get("reward") for s in range(len(steps[-1]))]
        agent_names = [(x or {}).get("Name") for x in (d.get("info", {}) or {}).get("Agents", [])]
        # our seat: the one whose final reward equals our recorded reward (fallback to our_seat)
        ours = None
        for s, rw in enumerate(last):
            if rw is not None and abs(float(rw) - float(r["our_reward"])) < 0.51:
                ours = s
        if ours is None:
            ours = int(r["our_seat"])
        for seat in range(len(steps[0])):
            rewards = [steps[-1][s].get("reward") for s in range(len(steps[-1]))]
            row = analyse(seat, steps, {"reward": rewards[seat]})
            is_mine = seat == ours
            row.update({
                "episode": ep, "ref": r["ref"], "label": r["label"], "kind": r["kind"],
                "seat": seat, "ours": int(is_mine),
                "agent_name": agent_names[seat] if seat < len(agent_names) else "",
                "opp_sid": r["opp_sid"] if is_mine else "",
                "opp_team": r["opp_team"] if is_mine else "",
                "margin": float(r["margin"]) if is_mine else "",
            })
            rows.append(row)
            mc = row.pop("_money_curve")
            for day in range(DAYS):
                s = min(day * 24 + 23, len(mc) - 1)
                curves.append({"episode": ep, "label": r["label"], "kind": r["kind"],
                               "ours": int(is_mine), "day": day, "money": mc[s]})
        print("done", ep, flush=True)
    with open(os.path.join(OUT, "farm_anatomy.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "money_curves.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["episode", "label", "kind", "ours", "day", "money"])
        w.writeheader()
        w.writerows(curves)
    print("rows", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
