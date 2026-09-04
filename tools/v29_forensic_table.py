"""Per-game forensic feature table for v28b live episodes (v29 canvas input).

Action parsing mirrors tools/revenue_forensics.py (action.market orders,
price snapshot from seat 0 obs before the step). Adds late-window px
(steps>=600), last-sell-day per item, and stranded end-shed valued at late px.

Usage: py -3 tools/v29_forensic_table.py <dir1> [<dir2> ...] <out_json>
"""
import glob
import json
import os
import sys
from collections import defaultdict

OUR = "shivam_2212"
ITEMS = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG",
         "MILK", "WOOL", "FERTILIZER", "GOOSE", "COW", "SHEEP"}


def seat_of(data):
    names = [str(n).lower() for n in data.get("info", {}).get("TeamNames", [])]
    for i, n in enumerate(names):
        if OUR in n:
            return i
    return 0


def game(path):
    data = json.load(open(path, encoding="utf-8"))
    seat = seat_of(data)
    steps = data["steps"]
    rewards = data.get("rewards", [])
    row = {"file": os.path.basename(path).replace("-replay.json", ""),
           "seed": data.get("info", {}).get("seed"),
           "our": rewards[seat], "opp": rewards[1 - seat],
           "delta": rewards[seat] - rewards[1 - seat]}

    px_late = defaultdict(list)
    px_all = defaultdict(list)
    rev = {0: defaultdict(float), 1: defaultdict(float)}
    qty = {0: defaultdict(int), 1: defaultdict(float)}
    last_sell_day = {0: defaultdict(int), 1: defaultdict(int)}

    for idx, step in enumerate(steps):
        obs0 = step[0].get("observation", {}) or {}
        px = (obs0.get("market") or {}).get("prices") or {}
        day = obs0.get("day")
        for item, p in px.items():
            px_all[item].append(float(p))
            if idx >= 600:
                px_late[item].append(float(p))
        for s in (0, 1):
            orders = (step[s].get("action") or {}).get("market") or []
            for o in orders:
                if not isinstance(o, (list, tuple)) or len(o) < 3:
                    continue
                kind, item, q = str(o[0]).upper(), o[1], o[2]
                if item not in ITEMS or not q:
                    continue
                if "SELL" in kind and item in px:
                    rev[s][item] += q * float(px[item])
                    qty[s][item] += q
                    if day is not None:
                        last_sell_day[s][item] = max(last_sell_day[s][item], day)

    def avg(d, k):
        return round(sum(d[k]) / len(d[k]), 1) if d.get(k) else None

    row["wool_px_late"] = avg(px_late, "WOOL")
    row["milk_px_late"] = avg(px_late, "MILK")
    row["wool_px_avg"] = avg(px_all, "WOOL")
    row["milk_px_avg"] = avg(px_all, "MILK")
    row["straw_px_late"] = avg(px_late, "STRAWBERRY")

    # end-state farms + shed
    for s, tag in ((seat, "our"), (1 - seat, "opp")):
        obs = steps[-1][s].get("observation", {}) or {}
        farms = obs.get("farms") or []
        f = farms[s] if len(farms) > s else {}
        animals = defaultdict(int)
        for r in f.get("tiles", []) or []:
            for t in r or []:
                if isinstance(t, dict) and t.get("animal"):
                    animals[t["animal"]] += 1
        row[f"{tag}_animals"] = dict(animals)
        row[f"{tag}_rev"] = {k: round(v) for k, v in sorted(rev[s].items(), key=lambda kv: -kv[1])}
        row[f"{tag}_wool_qty"] = int(qty[s].get("WOOL", 0))
        row[f"{tag}_milk_qty"] = int(qty[s].get("MILK", 0))
        row[f"{tag}_last_wool_day"] = last_sell_day[s].get("WOOL")
        row[f"{tag}_last_milk_day"] = last_sell_day[s].get("MILK")

    # our stranded shed valued at late px
    priv = (steps[-1][seat].get("observation", {}) or {}).get("private", {}) or {}
    shed = priv.get("shed", {}) or {}
    row["our_end_shed"] = {k: v for k, v in shed.items() if v}
    strand = 0.0
    for k, v in shed.items():
        lp = px_late.get(k)
        if v and lp:
            strand += v * (sum(lp) / len(lp))
    row["our_strand_value_latepx"] = round(strand)
    return row


def main():
    dirs, out = sys.argv[1:-1], sys.argv[-1]
    rows = []
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "*-replay.json"))):
            try:
                rows.append(game(p))
            except Exception as e:  # noqa: BLE001
                print("FAIL", p, repr(e), file=sys.stderr)
    rows.sort(key=lambda r: r["delta"])
    json.dump(rows, open(out, "w", encoding="utf-8"), indent=1)
    hdr = (f"{'file':<22}{'delta':>8}{'wPxL':>6}{'mPxL':>6} | {'ourC/S':>7} {'oppC/S':>7} | "
           f"{'ourW':>5}{'ourM':>5} {'oppW':>5}{'oppM':>5} | {'lastWd':>6} | {'strand$':>8}")
    print(hdr)
    for r in rows:
        a0, a1 = r["our_animals"], r["opp_animals"]
        print(f"{r['file'].replace('episode-',''):<22}{r['delta']:>8.0f}"
              f"{r['wool_px_late'] or 0:>6.0f}{r['milk_px_late'] or 0:>6.0f} | "
              f"{a0.get('COW',0):>3}/{a0.get('SHEEP',0):<3} {a1.get('COW',0):>3}/{a1.get('SHEEP',0):<3} | "
              f"{r['our_wool_qty']:>5}{r['our_milk_qty']:>5} {r['opp_wool_qty']:>5}{r['opp_milk_qty']:>5} | "
              f"{str(r['our_last_wool_day']):>6} | {r['our_strand_value_latepx']:>8}")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
