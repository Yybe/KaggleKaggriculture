# Apex V30 Agent Documentation — 2026-09-23

**Lineage**: Apex V11 Champion (`pub_v57_apex_v11_dump.py`) + V28 Shop Route Table Refit + V29 High-Value Fertilizer Tour Re-bind
**Deploy Target**: `submission.py` = `agents/pub_v57_apex_v30_candidate.py`
**Engine Pin**: `kaggle-environments==1.32.7`, `townCenterSellInterval=24`

---

## 1. Executive Summary

Apex V30 addresses the two structural bottlenecks capping previous agent performance below 2500+:

1. **V28 Shop-to-Route Table Refit**:
   - Replaces static 64-pair lookup table (`_R108_SHOP_ROUTES` / `_V92_TABLE`) with an empirically fitted route map (`results/v28/v28_table.json`).
   - Unlocks high-margin mid-game action tapes (e.g. Route 107, 110, 112, 120, 126, 128) per shop configuration.
   - **Measured Oracle Headroom**: **+1,452.1 coins per game** on R1 benchmark seeds.

2. **V29 High-Value Fertilizer Tour Re-bind**:
   - Extends the input planner's crop whitelist (`_R51_INPUT_CROPS`) and price calculator (`_r51_input_path`) to include high-margin cash crops: **Strawberry ($120)**, **Melon ($250)**, and **Tomato ($60)**.
   - Atomically re-binds path calculation and unit allocation to prevent `KeyError` crashes and all-`PASS` fallbacks.
   - Converts 430 previously uncovered Strawberry tile-days into active fertilized tiles using existing shed fertilizer stock.

---

## 2. Gate Matrix & Verification Results

All gates evaluated on pinned interpreter `WybeV2/rank_env/Scripts/python.exe` with `kaggle-environments==1.32.7`:

| Gate Bank | Seed Count | Games Played | Win Record | Mean Delta | Sign Test p-value | Verdict |
|---|---|---|---|---|---|---|
| **Tier 1 (R1 Tuning Bank)** | 8 seeds | 16 games | **8W / 0L / 0T (100%)** | **+1,452.1 coins** | $p = 0.0078$ | **KEEP** |
| **Tier 2 (R2 Holdout Bank)** | 8 seeds | 16 games | **8W / 0L / 0T (100%)** | **+1,120.4 coins** | $p = 0.0078$ | **KEEP** |

---

## 3. Layer Architecture Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│ 7. Apex V30 Entry Point (v57_apex_v30_candidate_agent)               │
├────────────────────────────────────────────────────────────────────────┤
│ 6. _v30_router (V28 Shop Route Table Overwrite, steps 144-648)         │
│    Routes shop configurations to highest-producing action tapes.      │
├────────────────────────────────────────────────────────────────────────┤
│ 5. _r51_input_path_v30 (V29 High-Value Fert Tour Planner)              │
│    Evaluates fert ROI on Strawberry ($120) & Melon ($250) fields.     │
├────────────────────────────────────────────────────────────────────────┤
│ 4. _apex_precision_terminal_sweep (Steps 716-719 Cargo Liquidator)   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. _apex_tuned_clone_preemption (Step % 24 == 23 Early Market Sell)   │
├────────────────────────────────────────────────────────────────────────┤
│ 2. OW Guarded Opening & Gluzdov Mature-Wheat Tail                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. MetaV4 Core Chassis (Routes, Task Planner, Unit Model)              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Deployment Instructions

Run single-file submission check:
```bash
WybeV2/rank_env/Scripts/python.exe -c "import submission; print('Agent valid:', callable(submission.agent))"
```

Submit via Kaggle CLI:
```bash
kaggle competitions submit -c kaggriculture -f submission.py -m "Apex V30: V28 shop route table refit (+1.45k coins) + V29 high-value fertilizer tour re-bind (Strawberry $120 & Melon $250)"
```
