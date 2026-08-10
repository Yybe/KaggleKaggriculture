"""
VersionWybe Feature Extraction Pipeline
========================================
Extracts comprehensive per-player, per-game features from Kaggriculture replay JSONs.
Targets: Seb (#1), HealthStone (#2) replays in replays_new/.

Outputs to VersionWybe/analysis_output/:
  - per_game_features.csv      : One row per (game, seat) with all features
  - opening_moves.json         : Step-by-step first 48 actions per game/seat
  - sell_log.csv               : Every SELL order across all games
  - buy_log.csv                : Every BUY order across all games
  - cash_trajectory.csv        : Money at each day boundary per game/seat
  - strategy_profiles.json     : Aggregated profiles for Seb vs HealthStone
"""

import json
import os
import sys
import glob
import csv
from collections import defaultdict, Counter

# ─── CONFIG ──────────────────────────────────────────────────
SEB_DIR = r"C:\Users\xxshi\Desktop\FARMMASTER\replays_new\seb"
HS_DIR  = r"C:\Users\xxshi\Desktop\FARMMASTER\replays_new\healthstone"
MANIFEST = r"C:\Users\xxshi\Desktop\FARMMASTER\replays_new\manifest.json"
OUT_DIR = r"C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\analysis_output"

STEPS_PER_DAY = 24  # 24 steps = 1 game day, 720 steps = 30 days

# ─── HELPERS ─────────────────────────────────────────────────

def identify_target_seat(replay, episode_id, manifest_data, player_label):
    """Determine which seat (0 or 1) belongs to the target player using manifest."""
    # Look up in manifest
    entries = manifest_data.get("seb", []) + manifest_data.get("healthstone", [])
    for entry in entries:
        if entry["episodeId"] == episode_id:
            # The manifest tracks episodes from the perspective of seb/healthstone
            # but we need to figure out which seat they occupy
            break

    # Use info.TeamNames if available
    info = replay.get("info", {})
    teams = info.get("TeamNames", [])

    # For Seb replays: Seb's team matches "sebmallia" or similar
    # For HealthStone: matches "HealthStone"
    # Since we can't rely on team names alone, use the manifest's reward to match
    steps = replay.get("steps", [])
    if not steps:
        return 0

    final_rewards = [steps[-1][i].get("reward", 0) for i in range(2)]

    # Find manifest entry for this episode
    for group in ["seb", "healthstone"]:
        for entry in manifest_data.get(group, []):
            if entry["episodeId"] == episode_id:
                my_reward = entry["myReward"]
                # Match to the seat with the closest reward
                diff0 = abs(final_rewards[0] - my_reward)
                diff1 = abs(final_rewards[1] - my_reward)
                if player_label == group:
                    return 0 if diff0 <= diff1 else 1
                else:
                    return 1 if diff0 <= diff1 else 0

    return 0  # fallback


def extract_episode_id(filename):
    """Extract episode ID from filename like 'episode-91211393-replay.json'."""
    parts = filename.replace(".json", "").split("-")
    for p in parts:
        if p.isdigit() and len(p) >= 7:
            return int(p)
    return 0


def safe_get(d, *keys, default=None):
    """Nested dict get."""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


def count_animals(farm):
    """Count animals by type from farm tiles."""
    counts = defaultdict(int)
    for tile in (farm.get("tiles", []) or []):
        if isinstance(tile, dict) and tile.get("kind") == "ANIMAL":
            animal_type = tile.get("animal_type") or tile.get("type") or "UNKNOWN"
            counts[animal_type] += 1
    return dict(counts)


def count_crops(farm):
    """Count planted crops by type from farm tiles."""
    counts = defaultdict(int)
    for tile in (farm.get("tiles", []) or []):
        if isinstance(tile, dict) and tile.get("kind") == "PLANT":
            crop = tile.get("crop") or "UNKNOWN"
            counts[crop] += 1
    return dict(counts)


# ─── MAIN EXTRACTION ────────────────────────────────────────

def extract_game_features(replay_path, manifest_data, player_label):
    """Extract all features from a single replay file."""
    fname = os.path.basename(replay_path)
    episode_id = extract_episode_id(fname)

    with open(replay_path, "r", encoding="utf-8") as f:
        replay = json.load(f)

    steps = replay.get("steps", [])
    info = replay.get("info", {})
    teams = info.get("TeamNames", ["P0", "P1"])
    num_steps = len(steps)

    target_seat = identify_target_seat(replay, episode_id, manifest_data, player_label)

    results = {}

    for seat in [0, 1]:
        is_target = seat == target_seat
        role = player_label if is_target else "opponent"

        # ─── OPENING ANALYSIS (steps 0-48) ──────────────
        hires_timeline = []   # (step, source) where source = "farmer" | "hand" | "market"
        seed_buys = []        # (step, seed_type, quantity)
        animal_buys = []      # (step, animal_type, quantity)
        expand_land_steps = []
        first_crop_step = None
        first_crop_type = None
        opening_moves = []    # raw actions for first 48 steps

        # ─── FULL GAME TRACKING ────────────────────────
        sell_log = []         # (step, day, item, qty)
        buy_log = []          # (step, day, item, qty)
        farmer_actions = Counter()
        hand_actions = Counter()
        care_count = 0
        water_count = 0
        harvest_count = 0
        feed_count = 0
        fertilize_count = 0
        dig_count = 0
        pass_count = 0
        build_pasture_count = 0

        # ─── CASH TRAJECTORY ────────────────────────────
        cash_by_day = {}  # day -> money

        for t in range(num_steps):
            step_data = steps[t][seat]
            obs = step_data.get("observation", {}) or {}
            action = step_data.get("action", {}) or {}
            day = obs.get("day", t // STEPS_PER_DAY)
            hour = obs.get("hour", t % STEPS_PER_DAY)

            # Farm state at day boundaries
            farms = obs.get("farms", [])
            if seat < len(farms):
                farm = farms[seat]
                if hour == 0 or t == 0:
                    cash_by_day[day] = farm.get("money", 0)
            else:
                farm = {}

            if not isinstance(action, dict):
                continue

            # Record opening moves
            if t <= 48:
                opening_moves.append({
                    "step": t,
                    "day": day,
                    "hour": hour,
                    "farmer": action.get("farmer"),
                    "hands": action.get("hands"),
                    "market": action.get("market"),
                })

            # ─── FARMER ACTIONS ─────────────────────────
            farmer_act = action.get("farmer")
            if isinstance(farmer_act, list) and farmer_act:
                act_type = farmer_act[0]
                farmer_actions[act_type] += 1
                if act_type == "HIRE":
                    hires_timeline.append((t, "farmer"))
                elif act_type == "CARE":
                    care_count += 1
                elif act_type == "WATER":
                    water_count += 1
                elif act_type == "HARVEST":
                    harvest_count += 1
                elif act_type == "FEED":
                    feed_count += 1
                elif act_type == "FERTILIZE":
                    fertilize_count += 1
                elif act_type == "DIG":
                    dig_count += 1
                elif act_type == "PASS":
                    pass_count += 1
                elif act_type == "BUILD_PASTURE":
                    build_pasture_count += 1
                elif act_type == "PLANT" and first_crop_step is None:
                    first_crop_step = t
                    first_crop_type = farmer_act[1] if len(farmer_act) > 1 else "UNKNOWN"
                elif act_type == "EXPAND_LAND":
                    expand_land_steps.append(t)

            # ─── HAND ACTIONS ──────────────────────────
            for hand_act in (action.get("hands") or []):
                if isinstance(hand_act, list) and hand_act:
                    act_type = hand_act[0]
                    hand_actions[act_type] += 1
                    if act_type == "HIRE":
                        hires_timeline.append((t, "hand"))
                    elif act_type == "CARE":
                        care_count += 1
                    elif act_type == "WATER":
                        water_count += 1
                    elif act_type == "HARVEST":
                        harvest_count += 1
                    elif act_type == "FEED":
                        feed_count += 1
                    elif act_type == "FERTILIZE":
                        fertilize_count += 1
                    elif act_type == "DIG":
                        dig_count += 1
                    elif act_type == "PASS":
                        pass_count += 1
                    elif act_type == "BUILD_PASTURE":
                        build_pasture_count += 1
                    elif act_type == "PLANT" and first_crop_step is None:
                        first_crop_step = t
                        first_crop_type = hand_act[1] if len(hand_act) > 1 else "UNKNOWN"
                    elif act_type == "EXPAND_LAND":
                        expand_land_steps.append(t)

            # ─── MARKET ACTIONS ────────────────────────
            for m_act in (action.get("market") or []):
                if not isinstance(m_act, (list, tuple)) or len(m_act) < 1:
                    continue
                cmd = m_act[0]
                if cmd == "HIRE":
                    hires_timeline.append((t, "market"))
                elif cmd == "BUY_SEED" and len(m_act) >= 3:
                    seed_buys.append((t, m_act[1], int(m_act[2])))
                elif cmd == "BUY_ANIMAL" and len(m_act) >= 3:
                    animal_buys.append((t, m_act[1], int(m_act[2])))
                elif cmd == "EXPAND_LAND":
                    expand_land_steps.append(t)
                elif cmd == "SELL" and len(m_act) >= 3:
                    sell_log.append((t, day, m_act[1], int(m_act[2])))
                elif cmd in ("BUY", "BUY_PRODUCT") and len(m_act) >= 3:
                    buy_log.append((t, day, m_act[1], int(m_act[2])))

        # ─── FINAL STATE ───────────────────────────────
        final_obs = steps[-1][seat].get("observation", {}) or {}
        final_farms = final_obs.get("farms", [])
        final_farm = final_farms[seat] if seat < len(final_farms) else {}
        final_reward = steps[-1][seat].get("reward", 0)
        final_money = final_farm.get("money", 0)
        final_hands = len(final_farm.get("hands", []) or [])
        _uq = final_farm.get("unlocked_quadrants", 1)
        final_quads = len(_uq) if isinstance(_uq, list) else int(_uq)
        final_animals = count_animals(final_farm)
        final_crops = count_crops(final_farm)

        # Private info (shed contents)
        final_private = final_obs.get("private", {}) or {}
        final_shed = dict(final_private.get("shed", {}) or {})

        # ─── SELL REVENUE BREAKDOWN ────────────────────
        sell_revenue_by_product = defaultdict(int)
        for (st, dy, item, qty) in sell_log:
            sell_revenue_by_product[item] += qty

        # ─── COMPUTED FEATURES ─────────────────────────
        total_hires = len(hires_timeline)
        hires_day0 = sum(1 for s, _ in hires_timeline if s < STEPS_PER_DAY)
        hires_day1 = sum(1 for s, _ in hires_timeline if STEPS_PER_DAY <= s < 2 * STEPS_PER_DAY)

        total_seeds = sum(q for _, _, q in seed_buys)
        total_animals_bought = sum(q for _, _, q in animal_buys)

        # Animal breakdown
        cows_bought = sum(q for _, t, q in animal_buys if t == "COW")
        sheep_bought = sum(q for _, t, q in animal_buys if t == "SHEEP")
        goose_bought = sum(q for _, t, q in animal_buys if t == "GOOSE")

        # Seed breakdown
        wheat_seeds = sum(q for _, t, q in seed_buys if t == "WHEAT")
        melon_seeds = sum(q for _, t, q in seed_buys if t == "MELON")
        carrot_seeds = sum(q for _, t, q in seed_buys if t == "CARROT")
        strawberry_seeds = sum(q for _, t, q in seed_buys if t == "STRAWBERRY")

        # Sell timing phases
        early_sells = sum(q for s, _, _, q in sell_log if s < 240)  # day 0-9
        mid_sells = sum(q for s, _, _, q in sell_log if 240 <= s < 480)  # day 10-19
        late_sells = sum(q for s, _, _, q in sell_log if s >= 480)  # day 20-29

        # Cash snapshots
        cash_d0 = cash_by_day.get(0, 0)
        cash_d1 = cash_by_day.get(1, 0)
        cash_d2 = cash_by_day.get(2, 0)
        cash_d5 = cash_by_day.get(5, 0)
        cash_d10 = cash_by_day.get(10, 0)
        cash_d15 = cash_by_day.get(15, 0)
        cash_d20 = cash_by_day.get(20, 0)

        # Win/loss
        opp_seat = 1 - seat
        opp_reward = steps[-1][opp_seat].get("reward", 0)
        won = final_reward > opp_reward
        margin = final_reward - opp_reward

        feature_row = {
            "episode_id": episode_id,
            "player_label": player_label,
            "role": role,
            "seat": seat,
            "team_name": teams[seat] if seat < len(teams) else "?",
            "opp_team_name": teams[opp_seat] if opp_seat < len(teams) else "?",
            "won": won,
            "final_reward": final_reward,
            "opp_reward": opp_reward,
            "margin": margin,
            "final_money": round(final_money, 1),
            # Opening
            "total_hires": total_hires,
            "hires_day0": hires_day0,
            "hires_day1": hires_day1,
            "first_hire_step": hires_timeline[0][0] if hires_timeline else -1,
            "total_seeds_bought": total_seeds,
            "wheat_seeds": wheat_seeds,
            "melon_seeds": melon_seeds,
            "carrot_seeds": carrot_seeds,
            "strawberry_seeds": strawberry_seeds,
            "total_animals_bought": total_animals_bought,
            "cows_bought": cows_bought,
            "sheep_bought": sheep_bought,
            "goose_bought": goose_bought,
            "first_animal_step": animal_buys[0][0] if animal_buys else -1,
            "first_expand_step": expand_land_steps[0] if expand_land_steps else -1,
            "num_expands": len(expand_land_steps),
            "first_crop_step": first_crop_step if first_crop_step is not None else -1,
            "first_crop_type": first_crop_type or "",
            # Cash trajectory
            "cash_d0": round(cash_d0, 1),
            "cash_d1": round(cash_d1, 1),
            "cash_d2": round(cash_d2, 1),
            "cash_d5": round(cash_d5, 1),
            "cash_d10": round(cash_d10, 1),
            "cash_d15": round(cash_d15, 1),
            "cash_d20": round(cash_d20, 1),
            # Farm ops
            "care_count": care_count,
            "water_count": water_count,
            "harvest_count": harvest_count,
            "feed_count": feed_count,
            "fertilize_count": fertilize_count,
            "dig_count": dig_count,
            "pass_count": pass_count,
            "build_pasture_count": build_pasture_count,
            # Economy
            "total_sells": len(sell_log),
            "total_sell_qty": sum(q for _, _, _, q in sell_log),
            "early_sell_qty": early_sells,
            "mid_sell_qty": mid_sells,
            "late_sell_qty": late_sells,
            "total_buy_orders": len(buy_log),
            # Final state
            "final_hands": final_hands,
            "final_quads": final_quads,
            "final_cows": final_animals.get("COW", 0),
            "final_sheep": final_animals.get("SHEEP", 0),
            "final_goose": final_animals.get("GOOSE", 0),
            "final_animals_total": sum(final_animals.values()),
            # Shed
            "shed_wheat": final_shed.get("WHEAT", 0),
            "shed_carrot": final_shed.get("CARROT", 0),
            "shed_melon": final_shed.get("MELON", 0),
            "shed_strawberry": final_shed.get("STRAWBERRY", 0),
            "shed_milk": final_shed.get("MILK", 0),
            "shed_wool": final_shed.get("WOOL", 0),
            "shed_egg": final_shed.get("EGG", 0),
            "shed_fertilizer": final_shed.get("FERTILIZER", 0),
        }

        results[seat] = {
            "features": feature_row,
            "sell_log": sell_log,
            "buy_log": buy_log,
            "opening_moves": opening_moves,
            "cash_by_day": cash_by_day,
            "hires_timeline": hires_timeline,
            "seed_buys": seed_buys,
            "animal_buys": animal_buys,
            "sell_revenue_by_product": dict(sell_revenue_by_product),
        }

    return results


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load manifest
    with open(MANIFEST, "r") as f:
        manifest = json.load(f)

    # Build episode -> player label map
    episode_player = {}
    for entry in manifest.get("seb", []):
        episode_player[entry["episodeId"]] = ("seb", entry)
    for entry in manifest.get("healthstone", []):
        episode_player[entry["episodeId"]] = ("healthstone", entry)

    all_features = []
    all_sells = []
    all_buys = []
    all_openings = {}
    all_cash_trajectories = []

    # Process Seb replays
    seb_files = sorted(glob.glob(os.path.join(SEB_DIR, "*.json")))
    hs_files = sorted(glob.glob(os.path.join(HS_DIR, "*.json")))
    print(f"Found {len(seb_files)} Seb replays, {len(hs_files)} HealthStone replays")

    for label, files in [("seb", seb_files), ("healthstone", hs_files)]:
        for fpath in files:
            fname = os.path.basename(fpath)
            episode_id = extract_episode_id(fname)
            print(f"  Processing {fname} ({label})...")

            try:
                results = extract_game_features(fpath, manifest, label)
            except Exception as e:
                print(f"  ERROR processing {fname}: {e}")
                continue

            for seat_idx, data in results.items():
                feat = data["features"]
                all_features.append(feat)

                # Sell log with episode context
                for (st, dy, item, qty) in data["sell_log"]:
                    all_sells.append({
                        "episode_id": episode_id,
                        "player_label": feat["role"],
                        "seat": seat_idx,
                        "step": st,
                        "day": dy,
                        "item": item,
                        "qty": qty,
                    })

                # Buy log
                for (st, dy, item, qty) in data["buy_log"]:
                    all_buys.append({
                        "episode_id": episode_id,
                        "player_label": feat["role"],
                        "seat": seat_idx,
                        "step": st,
                        "day": dy,
                        "item": item,
                        "qty": qty,
                    })

                # Cash trajectories
                for day_num, cash_val in data["cash_by_day"].items():
                    all_cash_trajectories.append({
                        "episode_id": episode_id,
                        "player_label": feat["role"],
                        "seat": seat_idx,
                        "day": day_num,
                        "cash": round(cash_val, 1),
                    })

                # Opening moves
                key = f"{episode_id}_seat{seat_idx}_{feat['role']}"
                all_openings[key] = data["opening_moves"]

    # ─── WRITE CSVs ──────────────────────────────────────────
    # Per-game features
    if all_features:
        keys = all_features[0].keys()
        with open(os.path.join(OUT_DIR, "per_game_features.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(all_features)
        print(f"\nWrote per_game_features.csv ({len(all_features)} rows)")

    # Sell log
    if all_sells:
        keys = all_sells[0].keys()
        with open(os.path.join(OUT_DIR, "sell_log.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(all_sells)
        print(f"Wrote sell_log.csv ({len(all_sells)} rows)")

    # Buy log
    if all_buys:
        keys = all_buys[0].keys()
        with open(os.path.join(OUT_DIR, "buy_log.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(all_buys)
        print(f"Wrote buy_log.csv ({len(all_buys)} rows)")

    # Cash trajectory
    if all_cash_trajectories:
        keys = all_cash_trajectories[0].keys()
        with open(os.path.join(OUT_DIR, "cash_trajectory.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(all_cash_trajectories)
        print(f"Wrote cash_trajectory.csv ({len(all_cash_trajectories)} rows)")

    # Opening moves JSON
    with open(os.path.join(OUT_DIR, "opening_moves.json"), "w") as f:
        json.dump(all_openings, f, indent=1)
    print(f"Wrote opening_moves.json ({len(all_openings)} entries)")

    # ─── STRATEGY PROFILES ───────────────────────────────────
    profiles = {}
    for label in ["seb", "healthstone"]:
        rows = [r for r in all_features if r["role"] == label]
        if not rows:
            continue
        n = len(rows)
        def avg(key):
            if not n: return 0
            vals = []
            for r in rows:
                v = r[key]
                if isinstance(v, (int, float)):
                    vals.append(v)
                elif isinstance(v, list):
                    vals.append(len(v))
            return round(sum(vals) / len(vals), 2) if vals else 0
        def med(key):
            vals = []
            for r in rows:
                v = r[key]
                if isinstance(v, (int, float)):
                    vals.append(v)
                elif isinstance(v, list):
                    vals.append(len(v))
            vals.sort()
            n2 = len(vals)
            if not n2: return 0
            mid = n2 // 2
            return vals[mid] if n2 % 2 else (vals[mid-1] + vals[mid]) / 2

        wins = sum(1 for r in rows if r["won"])

        profiles[label] = {
            "num_games": n,
            "win_rate": round(wins / n * 100, 1),
            "avg_reward": avg("final_reward"),
            "avg_margin": avg("margin"),
            "avg_hires_total": avg("total_hires"),
            "avg_hires_day0": avg("hires_day0"),
            "median_first_hire_step": med("first_hire_step"),
            "avg_seeds": avg("total_seeds_bought"),
            "avg_wheat_seeds": avg("wheat_seeds"),
            "avg_melon_seeds": avg("melon_seeds"),
            "avg_carrot_seeds": avg("carrot_seeds"),
            "avg_strawberry_seeds": avg("strawberry_seeds"),
            "avg_animals": avg("total_animals_bought"),
            "avg_cows": avg("cows_bought"),
            "avg_sheep": avg("sheep_bought"),
            "avg_goose": avg("goose_bought"),
            "avg_expands": avg("num_expands"),
            "avg_cash_d0": avg("cash_d0"),
            "avg_cash_d1": avg("cash_d1"),
            "avg_cash_d2": avg("cash_d2"),
            "avg_cash_d5": avg("cash_d5"),
            "avg_cash_d10": avg("cash_d10"),
            "avg_care": avg("care_count"),
            "avg_water": avg("water_count"),
            "avg_harvest": avg("harvest_count"),
            "avg_feed": avg("feed_count"),
            "avg_fertilize": avg("fertilize_count"),
            "avg_pass": avg("pass_count"),
            "avg_total_sells": avg("total_sells"),
            "avg_total_sell_qty": avg("total_sell_qty"),
            "avg_early_sell_qty": avg("early_sell_qty"),
            "avg_mid_sell_qty": avg("mid_sell_qty"),
            "avg_late_sell_qty": avg("late_sell_qty"),
            "avg_final_hands": avg("final_hands"),
            "avg_final_quads": avg("final_quads"),
            "avg_final_animals": avg("final_animals_total"),
            "avg_final_cows": avg("final_cows"),
            "avg_final_sheep": avg("final_sheep"),
        }

    with open(os.path.join(OUT_DIR, "strategy_profiles.json"), "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"Wrote strategy_profiles.json")

    # --- QUICK SUMMARY ---------------------------------------
    print("\n" + "="*60)
    print("STRATEGY PROFILE COMPARISON")
    print("="*60)
    for label, p in profiles.items():
        print(f"\n{'-'*40}")
        print(f"  {label.upper()} ({p['num_games']} games, {p['win_rate']}% win rate)")
        print(f"{'-'*40}")
        print(f"  Avg reward:     {p['avg_reward']:,.0f}  (margin: {p['avg_margin']:+,.0f})")
        print(f"  Opening hires:  {p['avg_hires_day0']:.1f} d0 / {p['avg_hires_total']:.1f} total")
        print(f"  Seeds:          W={p['avg_wheat_seeds']:.1f} M={p['avg_melon_seeds']:.1f} C={p['avg_carrot_seeds']:.1f} S={p['avg_strawberry_seeds']:.1f}")
        print(f"  Animals:        Cow={p['avg_cows']:.1f} Sheep={p['avg_sheep']:.1f} Goose={p['avg_goose']:.1f}")
        print(f"  Expands:        {p['avg_expands']:.1f}")
        print(f"  Cash d0/d1/d2:  {p['avg_cash_d0']:.0f} / {p['avg_cash_d1']:.0f} / {p['avg_cash_d2']:.0f}")
        print(f"  Cash d5/d10:    {p['avg_cash_d5']:.0f} / {p['avg_cash_d10']:.0f}")
        print(f"  Farm ops:       CARE={p['avg_care']:.0f} WATER={p['avg_water']:.0f} HARVEST={p['avg_harvest']:.0f}")
        print(f"  Sell phases:    early={p['avg_early_sell_qty']:.0f} mid={p['avg_mid_sell_qty']:.0f} late={p['avg_late_sell_qty']:.0f}")
        print(f"  Final state:    hands={p['avg_final_hands']:.0f} quads={p['avg_final_quads']:.1f} animals={p['avg_final_animals']:.0f}")

    print(f"\nAll outputs in: {OUT_DIR}")


if __name__ == "__main__":
    main()
