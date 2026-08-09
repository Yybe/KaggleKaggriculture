"""Kaggriculture top-replay analyzer.

Extracts the signals that matter from full 720-step replays:
  - rewards / money curve (per day)
  - crop & animal mix (per day)
  - hands hired (per day)
  - land unlock timing
  - sell timing & volumes vs market prices
  - fertilizer usage
  - action economy (PLANT/HARVEST/WATER/FERTILIZE/FEED/CARE per crop)
  - late-game (day 20+) behavior

Phase 1: extraction  -> replay_summary.csv, daily_timeline.csv, price_curves.csv
Phase 2: analysis    -> printed findings report + findings.csv
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

REPLAY_DIR = Path(r"C:\Users\chira\Desktop\rot\Kaggriculture\kaggriculture top replays")
OUT_DIR = Path(r"C:\Users\chira\Desktop\rot\Kaggriculture")

CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["COW", "SHEEP", "GOOSE", "CHICKEN"]
PRODUCTS = ["EGG", "MILK", "WOOL", "FERTILIZER"]


def load_replay(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_replay(path: Path):
    """Return (summary_rows, daily_rows, price_rows) for one replay file."""
    replay = load_replay(path)
    steps = replay["steps"]
    rewards = replay["rewards"]
    file_id = replay.get("id", path.stem)
    title = replay.get("title", "")
    agent_names = [i.get("Name", f"P{i}") for i in replay.get("info", {}).get("Agents", [])]
    if len(agent_names) < 2:
        agent_names = ["P0", "P1"]

    summary_rows = []
    daily_rows = []
    price_rows = []
    last_day_prices = {}

    # per player accumulators (reset per file)
    agg = {p: {
        "action_counts": defaultdict(int),          # action op counts (farmer+hands)
        "plant_by_crop": defaultdict(int),          # PLANT actions per crop
        "sell_by_item": defaultdict(int),           # SELL totals per item
        "buy_seed_by_crop": defaultdict(int),       # BUY_SEED totals per crop
        "buy_product_by_item": defaultdict(int),    # BUY_PRODUCT totals per item
        "buy_animal_by_animal": defaultdict(int),   # BUY_ANIMAL totals per animal
        "shed_max": defaultdict(int),               # max observed shed count per animal
        "day_unlock2": None, "day_unlock3": None, "day_unlock4": None,
        "peak_hands": 0, "total_hires": 0, "hire_days": 0,
        "total_buy_land": 0,
        "sell_day_cum": defaultdict(int),           # item -> cumulative sold up to last day
        "cum_sell_by_item": defaultdict(int),
    } for p in (0, 1)}

    # ---- walk steps ----
    for t, step in enumerate(steps):
        day = step[0]["observation"]["day"]
        # prices sampled once per day (at day boundary)
        if t % 24 == 0 or day != (t // 24):
            mkt = step[0]["observation"]["market"]
            prices = mkt.get("prices", {})
            price_rows.append({"file": file_id, "day": day,
                               **{f"price_{k.lower()}": v for k, v in prices.items()}})
            last_day_prices = prices

        for p in (0, 1):
            entry = step[p]
            obs = entry["observation"]
            farm = obs["farms"][p]
            act = entry["action"] or {}
            a = agg[p]

            # ---- money / land / hands (every step, cheap) ----
            money = farm["money"]
            a.setdefault("money_last", money)
            a["money_last"] = money
            a["max_money"] = max(a.get("max_money", 0.0), money)
            a.setdefault("day_money_first", {})
            if day not in a["day_money_first"]:
                a["day_money_first"][day] = money
            a["day_money_last"] = money  # keeps last money of each day

            n_unlocked = len(farm.get("unlocked_quadrants", []))
            if n_unlocked >= 2 and a["day_unlock2"] is None:
                a["day_unlock2"] = day
            if n_unlocked >= 3 and a["day_unlock3"] is None:
                a["day_unlock3"] = day
            if n_unlocked >= 4 and a["day_unlock4"] is None:
                a["day_unlock4"] = day

            n_hands = len(farm.get("hands", []))
            a["peak_hands"] = max(a["peak_hands"], n_hands)
            hires = farm.get("hires_today", 0) or 0
            a["total_hires"] += hires
            if hires > 0:
                a["hire_days"] += 1

            # ---- actions ----
            market_ops = act.get("market") or []
            for op in market_ops:
                if not isinstance(op, list) or not op:
                    continue
                cmd = op[0]
                if cmd == "BUY_SEED" and len(op) >= 3:
                    a["buy_seed_by_crop"][op[1]] += op[2]
                elif cmd == "BUY_PRODUCT" and len(op) >= 3:
                    a["buy_product_by_item"][op[1]] += op[2]
                elif cmd == "BUY_ANIMAL" and len(op) >= 3:
                    a["buy_animal_by_animal"][op[1]] += op[2]
                elif cmd == "SELL" and len(op) >= 3:
                    a["sell_by_item"][op[1]] += op[2]
                    a["cum_sell_by_item"][op[1]] += op[2]
                    a["sell_day_cum"][op[1]] = a["cum_sell_by_item"][op[1]]
                    a.setdefault("sell_day_price", {})[op[1]] = last_day_prices.get(op[1])
                elif cmd == "HIRE":
                    pass  # tracked via hires_today
                elif cmd == "BUY_LAND":
                    a["total_buy_land"] += 1
                a["action_counts"][cmd] += 1

            for agent_act in (act.get("farmer"), *([h for h in act.get("hands") or [] if isinstance(h, list)])):
                if not isinstance(agent_act, list) or not agent_act:
                    continue
                cmd = agent_act[0]
                a["action_counts"][cmd] += 1
                if cmd == "PLANT" and len(agent_act) >= 2:
                    a["plant_by_crop"][agent_act[1]] += 1

            # ---- daily sampling (tiles every 12 steps, 2x/day) ----
            if t % 12 == 0:
                a.setdefault("tile_samples", []).append(
                    (day, farm.get("tiles", []), farm.get("money", 0)))
                a.setdefault("last_tile_day", day)

            # ---- shed max (animals) ----
            priv = obs.get("private") or {}
            shed = priv.get("shed") or {}
            for an in ANIMALS:
                v = shed.get(an, 0) or 0
                if v > a["shed_max"][an]:
                    a["shed_max"][an] = v

    # ---- assemble daily rows from tile samples ----
    # group tile samples by day (keep last sample of each day)
    per_day_tiles = defaultdict(list)
    per_day_money = {}
    for p in (0, 1):
        a = agg[p]
        for (day, tiles, money) in a.get("tile_samples", []):
            per_day_tiles[(p, day)].append((tiles, money))
            per_day_money[(p, day)] = money

    day_set = sorted({d for (_, d) in per_day_tiles.keys()})

    def tile_stats(tiles):
        mix = defaultdict(int)
        fert = 0
        total = 0
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    total += 1
                    mix[t.get("kind")] += 1
                    if t.get("kind") == "PLANT" and t.get("crop"):
                        mix[f"crop_{t['crop']}"] += 1
                    if (t.get("fertilized_until_day") or -1) >= (t.get("planted_day") or 0):
                        fert += 1
        return mix, fert, total

    for p in (0, 1):
        a = agg[p]
        a["day_sells"] = defaultdict(lambda: defaultdict(int))
        a["day_actions"] = defaultdict(lambda: defaultdict(int))
        a["day_plants"] = defaultdict(lambda: defaultdict(int))
        a["day_buys"] = defaultdict(lambda: defaultdict(int))
        a["day_animals"] = defaultdict(lambda: defaultdict(int))

    # back-fill day-level action/plant/sell buckets by scanning again (cheap: reuse dicts)
    for t, step in enumerate(steps):
        day = step[0]["observation"]["day"]
        for p in (0, 1):
            act = step[p]["action"] or {}
            a = agg[p]
            mkt = act.get("market") or []
            for op in mkt:
                if not isinstance(op, list) or not op:
                    continue
                cmd = op[0]
                if cmd == "SELL" and len(op) >= 3:
                    a["day_sells"][day][op[1]] += op[2]
                elif cmd == "BUY_ANIMAL" and len(op) >= 3:
                    a["day_animals"][day][op[1]] += op[2]
                elif cmd == "BUY_SEED" and len(op) >= 3:
                    a["day_buys"][day][op[1]] += op[2]
            for agent_act in [act.get("farmer")] + [h for h in (act.get("hands") or []) if isinstance(h, list)]:
                if not isinstance(agent_act, list) or not agent_act:
                    continue
                cmd = agent_act[0]
                a["day_actions"][day][cmd] += 1
                if cmd == "PLANT" and len(agent_act) >= 2:
                    a["day_plants"][day][agent_act[1]] += 1

    for p in (0, 1):
        a = agg[p]
        for day in day_set:
            tiles_list = per_day_tiles.get((p, day))
            mix = defaultdict(int)
            fert = 0
            total = 0
            money = per_day_money.get((p, day), 0)
            if tiles_list:
                tiles, money = tiles_list[-1]  # last sample of the day
                mix, fert, _ = tile_stats(tiles)
            sells = dict(a["day_sells"].get(day, {}))
            buys = dict(a["day_buys"].get(day, {}))
            plants = dict(a["day_plants"].get(day, {}))
            animals = dict(a["day_animals"].get(day, {}))
            acts = dict(a["day_actions"].get(day, {}))
            daily_rows.append({
                "file": file_id, "player": p, "agent": agent_names[p],
                "day": day, "money": money,
                "hands": None,  # filled below
                "hires_today": None,
                "unlocked": None,
                "n_plant": mix.get("PLANT", 0), "n_pasture": mix.get("PASTURE", 0),
                "n_weed": mix.get("WEED", 0), "tiles_sampled": total,
                **{f"crop_{c}": mix.get(f"crop_{c}", 0) for c in CROPS},
                "fertilized_tiles": fert,
                "sell_melon": sells.get("MELON", 0), "sell_wheat": sells.get("WHEAT", 0),
                "sell_strawberry": sells.get("STRAWBERRY", 0), "sell_carrot": sells.get("CARROT", 0),
                "sell_tomato": sells.get("TOMATO", 0),
                "sell_egg": sells.get("EGG", 0), "sell_milk": sells.get("MILK", 0),
                "sell_wool": sells.get("WOOL", 0), "sell_fertilizer": sells.get("FERTILIZER", 0),
                "buy_wheat_feed": buys.get("WHEAT", 0),
                "buy_seed_melon": buys.get("MELON", 0), "buy_seed_wheat": buys.get("WHEAT", 0),
                "buy_seed_strawberry": buys.get("STRAWBERRY", 0), "buy_seed_carrot": buys.get("CARROT", 0),
                "buy_seed_tomato": buys.get("TOMATO", 0),
                "buy_animal_cow": animals.get("COW", 0), "buy_animal_sheep": animals.get("SHEEP", 0),
                "buy_animal_goose": animals.get("GOOSE", 0), "buy_animal_chicken": animals.get("CHICKEN", 0),
            })

        # attach day-level hands/unlocked/hires from replay walk (we sampled tiles 2x/day only)
        # -> do a light third pass for those three numbers per day
        hands_day = defaultdict(int)
        hires_day = defaultdict(int)
        unlock_day = defaultdict(int)
        for t, step in enumerate(steps):
            day = step[0]["observation"]["day"]
            for pp in (0, 1):
                farm = step[pp]["observation"]["farms"][pp]
                hands_day[(pp, day)] = max(hands_day[(pp, day)], len(farm.get("hands", [])))
                hires_day[(pp, day)] += farm.get("hires_today", 0) or 0
                unlock_day[(pp, day)] = len(farm.get("unlocked_quadrants", []))
        for row in daily_rows:
            d = row["day"]; pp = row["player"]
            row["hands"] = hands_day.get((pp, d), 0)
            row["hires_today"] = hires_day.get((pp, d), 0)
            row["unlocked"] = unlock_day.get((pp, d), 1)

    # ---- summary row ----
    for p in (0, 1):
        a = agg[p]
        crop_mix_by_day = {}
        for row in daily_rows:
            if row["player"] == p:
                for c in CROPS:
                    crop_mix_by_day.setdefault(c, {})[row["day"]] = row[f"crop_{c}"]
        total_plants = sum(a["plant_by_crop"].values())
        summary_rows.append({
            "file": file_id, "player": p, "agent": agent_names[p],
            "reward": rewards[p],
            "final_money": a["money_last"],
            "max_money": a["max_money"],
            "day_unlock2": a["day_unlock2"], "day_unlock3": a["day_unlock3"], "day_unlock4": a["day_unlock4"],
            "peak_hands": a["peak_hands"], "total_hires": a["total_hires"], "hire_days": a["hire_days"],
            "avg_hands_per_day": a["total_hires"] / 30.0,
            "total_buy_land": a["total_buy_land"],
            "total_plants": total_plants,
            **{f"plant_{c}": a["plant_by_crop"].get(c, 0) for c in CROPS},
            **{f"sell_{c}": a["sell_by_item"].get(c, 0) for c in CROPS},
            **{f"sell_{pr}": a["sell_by_item"].get(pr, 0) for pr in PRODUCTS},
            **{f"buy_seed_{c}": a["buy_seed_by_crop"].get(c, 0) for c in CROPS},
            **{f"buy_animal_{an.lower()}": a["buy_animal_by_animal"].get(an, 0) for an in ANIMALS},
            **{f"shed_max_{an.lower()}": a["shed_max"].get(an, 0) for an in ANIMALS},
            "n_fert_actions": a["action_counts"].get("FERTILIZE", 0),
            "n_build_pasture": a["action_counts"].get("BUILD_PASTURE", 0),
            "n_build_coop": a["action_counts"].get("BUILD_COOP", 0),
            "n_feed": a["action_counts"].get("FEED", 0),
            "n_care": a["action_counts"].get("CARE", 0),
            "n_water": a["action_counts"].get("WATER", 0),
            "n_harvest": a["action_counts"].get("HARVEST", 0),
            "n_fertilizer_bought": a["buy_product_by_item"].get("FERTILIZER", 0),
            "crop_mix": crop_mix_by_day,
        })

    return summary_rows, daily_rows, price_rows


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    files = sorted(REPLAY_DIR.glob("*.json"))
    print(f"Found {len(files)} replay files in {REPLAY_DIR}")
    if not files:
        sys.exit(1)

    all_summary, all_daily, all_price = [], [], []
    for i, f in enumerate(files, 1):
        try:
            s, d, p = extract_replay(f)
            all_summary.extend(s)
            all_daily.extend(d)
            all_price.extend(p)
            print(f"  [{i}/{len(files)}] {f.name}  rewards={[r['reward'] for r in s]}")
        except Exception as e:
            print(f"  [{i}/{len(files)}] {f.name} FAILED: {e}")

    # ---- drop the giant crop_mix dict column for CSV; keep it for analysis via daily rows ----
    summary_df = pd.DataFrame(all_summary).drop(columns=["crop_mix"])
    daily_df = pd.DataFrame(all_daily)
    price_df = pd.DataFrame(all_price)

    summary_df.to_csv(OUT_DIR / "replay_summary.csv", index=False)
    daily_df.to_csv(OUT_DIR / "daily_timeline.csv", index=False)
    price_df.to_csv(OUT_DIR / "price_curves.csv", index=False)
    print(f"\nSaved: replay_summary.csv ({len(summary_df)} rows), "
          f"daily_timeline.csv ({len(daily_df)} rows), price_curves.csv ({len(price_df)} rows)")

    # ---- ANALYSIS ----
    print("\n" + "=" * 100)
    print("FINDINGS")
    print("=" * 100)
    analyze(summary_df, daily_df, price_df)


def analyze(summary: pd.DataFrame, daily: pd.DataFrame, price: pd.DataFrame):
    out = []

    def line(s=""):
        print(s)
        out.append(s)

    # ranking
    line("### 1. AGENT RANKING (by final reward)")
    rank = summary.sort_values("reward", ascending=False).reset_index(drop=True)
    rank["rank"] = rank.index + 1
    line(rank[["rank", "file", "agent", "reward", "final_money", "day_unlock3", "peak_hands",
               "total_hires", "buy_animal_cow", "buy_animal_sheep", "buy_animal_goose",
               "n_fert_actions", "n_build_pasture"]].to_string(index=False))
    line()

    # top vs bottom split
    top_n = max(8, len(summary) // 2)
    summary2 = summary.copy()
    summary2["tier"] = pd.qcut(summary2["reward"], 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
    tiers = summary2.groupby("tier", observed=True).agg(
        n=("reward", "size"), avg_reward=("reward", "mean"),
        avg_final_money=("final_money", "mean"),
        avg_day_unlock2=("day_unlock2", "mean"), avg_day_unlock3=("day_unlock3", "mean"),
        avg_peak_hands=("peak_hands", "mean"), avg_total_hires=("total_hires", "mean"),
        avg_plants=("total_plants", "mean"),
        avg_melon=("plant_MELON", "mean"), avg_wheat=("plant_WHEAT", "mean"),
        avg_straw=("plant_STRAWBERRY", "mean"), avg_carrot=("plant_CARROT", "mean"),
        avg_tomato=("plant_TOMATO", "mean"),
        avg_sell_melon=("sell_MELON", "mean"), avg_sell_wheat=("sell_WHEAT", "mean"),
        avg_sell_straw=("sell_STRAWBERRY", "mean"),
        avg_cow=("buy_animal_cow", "mean"), avg_sheep=("buy_animal_sheep", "mean"),
        avg_goose=("buy_animal_goose", "mean"),
        avg_fert_actions=("n_fert_actions", "mean"), avg_fertilizer_bought=("n_fertilizer_bought", "mean"),
        avg_build_pasture=("n_build_pasture", "mean"), avg_feed=("n_feed", "mean"),
    ).sort_index()
    line("### 2. TIER COMPARISON (Q1 = bottom 25%, Q4 = top 25% of agents)")
    line(tiers.to_string())
    line()

    # money curves by tier
    daily2 = daily.merge(summary2[["file", "player", "tier"]], on=["file", "player"])
    money_curve = daily2.groupby(["tier", "day"], observed=True)["money"].mean().unstack(0)
    line("### 3. AVERAGE MONEY CURVE BY TIER (day 0-29)")
    line(money_curve.round(0).to_string())
    line()

    # crop mix evolution by tier: share of planted tiles (crop counts / total plant tiles)
    mix = daily2.groupby(["tier", "day"], observed=True)[
        ["crop_MELON", "crop_STRAWBERRY", "crop_WHEAT", "crop_CARROT", "crop_TOMATO", "n_pasture", "n_weed"]].mean()
    for tier in ["Q1", "Q4"]:
        line(f"--- crop tile mix (avg tile counts) TIER {tier} ---")
        line(mix.loc[tier].round(1).to_string())
        line()

    # market price curves
    pc = price.groupby("day")[["price_melon", "price_strawberry", "price_wheat", "price_carrot",
                               "price_tomato", "price_fertilizer", "price_wool", "price_egg", "price_milk"]].mean()
    line("### 4. AVERAGE MARKET PRICES BY DAY")
    line(pc.round(1).to_string())
    line()

    # sell timing: fraction of total melons sold by each day, per agent
    line("### 5. MELON SELL TIMING (cumulative % of total melons sold by day) — Q1 vs Q4")
    sell = daily2.pivot_table(index=["file", "player"], columns="day", values="sell_melon",
                              aggfunc="sum", fill_value=0)
    total_melon = summary2.set_index(["file", "player"])["sell_MELON"]
    cum = sell.cumsum(axis=1).div(total_melon.replace(0, float("nan")), axis=0).clip(upper=1) * 100
    for day_mark in [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]:
        cols = [c for c in cum.columns if c <= day_mark]
        if not cols:
            continue
        q1 = cum.loc[cum.index.isin(summary2[summary2["tier"] == "Q1"].set_index(["file", "player"]).index), cols[-1]]
        q4 = cum.loc[cum.index.isin(summary2[summary2["tier"] == "Q4"].set_index(["file", "player"]).index), cols[-1]]
        line(f"  by day {day_mark:>2}: Q1 avg {q1.mean():5.1f}% sold | Q4 avg {q4.mean():5.1f}% sold")
    line()

    # late-game pivot: what % of plant tiles are melon on day 20/24/28 by tier
    line("### 6. LATE-GAME PIVOT (avg tile counts on day 20/24/28)")
    for day_mark in [20, 24, 28]:
        row = mix.loc["Q4"].loc[day_mark] if day_mark in mix.loc["Q4"].index else None
        row_q1 = mix.loc["Q1"].loc[day_mark] if day_mark in mix.loc["Q1"].index else None
        line(f"  day {day_mark}: Q4 melon={row['crop_MELON']:.1f} straw={row['crop_STRAWBERRY']:.1f} "
             f"pasture={row['n_pasture']:.1f} weed={row['n_weed']:.1f}  |  Q1 melon={row_q1['crop_MELON']:.1f} "
             f"straw={row_q1['crop_STRAWBERRY']:.1f} pasture={row_q1['n_pasture']:.1f} weed={row_q1['n_weed']:.1f}")
    line()

    # land timing
    line("### 7. LAND UNLOCK TIMING")
    line(summary2.groupby("tier", observed=True)[["day_unlock2", "day_unlock3", "day_unlock4"]].mean().round(1).to_string())
    line()

    # correlation with reward
    line("### 8. CORRELATIONS WITH FINAL REWARD (n=%d)" % len(summary2))
    corr_cols = ["final_money", "max_money", "day_unlock2", "day_unlock3", "peak_hands", "total_hires",
                 "total_plants", "plant_MELON", "plant_STRAWBERRY", "plant_WHEAT",
                 "sell_MELON", "sell_STRAWBERRY", "sell_WHEAT", "sell_EGG", "sell_MILK", "sell_WOOL",
                 "buy_animal_cow", "buy_animal_sheep", "buy_animal_goose",
                 "shed_max_cow", "shed_max_sheep", "shed_max_goose",
                 "n_fert_actions", "n_fertilizer_bought", "n_build_pasture", "n_feed", "n_care"]
    corr = summary2[corr_cols + ["reward"]].corr()["reward"].drop("reward").sort_values()
    line(corr.round(3).to_string())
    line()

    # ---- gross revenue by channel (uses per-game prices) ----
    items = ["MELON", "STRAWBERRY", "WHEAT", "CARROT", "TOMATO", "EGG", "MILK", "WOOL", "FERTILIZER"]
    m = daily.merge(price, on=["file", "day"], how="left")
    rev = {}
    for it in items:
        rev[f"rev_{it.lower()}"] = m[f"sell_{it.lower()}"] * m[f"price_{it.lower()}"].fillna(0)
    revdf = pd.DataFrame(rev)
    revdf["player"] = m["player"]
    revdf["file"] = m["file"]
    revdf = revdf.groupby(["file", "player"]).sum().reset_index()
    s2 = summary.merge(revdf, on=["file", "player"])
    s2["rev_total"] = sum(s2[f"rev_{it.lower()}"] for it in items)
    s2["tier"] = pd.qcut(s2["reward"], 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")

    line("### 9. GROSS REVENUE BY CHANNEL (mean per agent by tier; sell volume x that game's price)")
    rt = s2.groupby("tier", observed=True)[["rev_total"] + [f"rev_{it.lower()}" for it in items]].mean().round(0)
    line(rt.to_string())
    q4 = s2[s2["tier"] == "Q4"]
    tot4 = q4["rev_total"].sum()
    line("Q4 revenue shares: " + " | ".join(f"{it} {100*q4[f'rev_{it.lower()}'].sum()/tot4:.1f}%" for it in items))
    line()

    line("### 10. SAME-BOT MARKET-LUCK SPREAD (Wufang Hong bot across games)")
    wh = summary[summary["agent"] == "Wufang Hong"].sort_values("reward")
    line(f"  Wufang Hong: {len(wh)} appearances, reward {wh['reward'].min():.0f} - {wh['reward'].max():.0f}, "
         f"std {wh['reward'].std():.0f} -> identical bot, score set by market window luck")
    line()

    # ---- big picture ----
    line("### 11. KEY TAKEAWAYS")
    melon_p = pc["price_melon"]
    crash_day = melon_p.idxmin()
    line(f"  - MELON price bottoms at day {crash_day} (min {melon_p.min():.0f}) vs peak {melon_p.max():.0f} (day {melon_p.idxmax()})")
    straw_p = pc["price_strawberry"]
    line(f"  - STRAWBERRY price peak day {straw_p.idxmax()} ({straw_p.max():.0f}), min day {straw_p.idxmin()} ({straw_p.min():.0f})")
    q4 = summary2[summary2["tier"] == "Q4"]
    q1 = summary2[summary2["tier"] == "Q1"]
    line(f"  - Avg reward: Q4={q4['reward'].mean():.0f}  Q1={q1['reward'].mean():.0f}")
    line(f"  - Avg day-3rd-land: Q4={q4['day_unlock3'].mean():.1f}  Q1={q1['day_unlock3'].mean():.1f}")
    line(f"  - Avg peak hands: Q4={q4['peak_hands'].mean():.1f}  Q1={q1['peak_hands'].mean():.1f}")

    # save findings
    (OUT_DIR / "findings.txt").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
