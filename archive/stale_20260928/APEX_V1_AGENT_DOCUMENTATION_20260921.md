# Apex V1 Champion Agent: Architecture, Reverse Engineering & Results

**Date**: 2026-09-21  
**Live Submission Ref**: `56433342`  
**File**: `submission.py` / `agents/pub_apex_v1.py`  
**MD5**: `3abd40ee238911772bfc496d61283e119707f81a19797fe2f0b47aa3039ceb5e` lineage + composite layers  
**Engine**: `kaggle-environments` 1.32.7 (Hinge rebalance, `townCenterSellInterval=24`)

---

## 1. Executive Summary & Core Motivation

Our previous submissions (`crop_roi30_h20`, `r78u`, `r78ub`) climbed into the 2700 score bracket on Kaggle, but began encountering:
1. **Unnecessary losses against recent public kernels**: e.g., on seed 2000000 against `farmer-john-and-the-wheat-seller` due to premature opportunistic selling of high-value items (wool, milk) that depressed market prices.
2. **Deterministic clone ties**: On neutral seeds where tomato demand is insufficient, our agent and public clones executed identical step 0–96 baseline schedules, yielding exact $\pm 0$ seed-level ties.
3. **Missed high-EV opportunities**: Public lineages without the V219 Tomato Union Gate and Day-20 Horizon-Discount Fert-ROI under-earned by \$1,000 to \$3,100 on rich seeds.

To solve this, we pulled and reverse-engineered all public kernels released in the past 12 hours from Kaggle CLI, extracted their mechanisms, and synthesized **Apex V1**.

---

## 2. Reverse-Engineered Public Kernels (Past 12h)

Using the Kaggle CLI, we pulled and analyzed:
1. **`lynnsakurai/farmer-john-and-the-wheat-seller` (`pub_farmer_john_v56.py`)**:
   - *Key Discovery*: Introduced the `_OW` layer consisting of `_ow_guard_opening` (step 29 pasture repair), `_ow_gate_delayed_cycle` (step 84 detour skip), and `_ow_close_queue` (market queue defragmentation).
   - *Flaw Identified*: Kept the old strict tomato condition (`money >= 12000 & shops >= 3`) and strict fert ROI (`1.5*cost+50`), losing massive margin on rich seeds.
2. **`ahmedberatozer/kaggriculture-v54-productive-wheat-and-patient` (`pub_v54_productive.py`)**:
   - Hybrid opening with conservative tomato lock.
3. **`flexonafft/kaggriculture-multi-route-farming-agent` (`pub_one_more_wheat.py`)**:
   - Single wheat cycle extension without SE-quadrant expansion.
4. **`crystalbaby/god-s-mode-hacked-stores` (`gods-mode`)**:
   - Store RNG prediction & live price observer. Telemetry confirmed seed stripping in live competition makes full store prediction noisy; however, visible tile supply and demand models were validated.
5. **`kenanzhang9/kaggriculture-a1-t31-guard` (`a1-t31-guard`)**:
   - Tested vs base: 8/8 exact ties.

---

## 3. The Apex V1 Architecture

Apex V1 integrates four verified winning layers on top of the `metav4` spine:

```
+-------------------------------------------------------------------------------+
|                                 APEX V1 STACK                                 |
+-------------------------------------------------------------------------------+
|  4. _OW Guarded Opening & Market Queue Defragmentation Layer                   |
|     - Step 29 pasture restoration guard if opening wheat is altered.          |
|     - Step 84 delayed cycle gate to prevent idle worker detours.              |
|     - Pulls valid cash sales left and zeroes out unexecutable orders.        |
+-------------------------------------------------------------------------------+
|  3. Gluzdov Mature-Wheat CL Tail Layer (+27/+28 per game baseline)             |
|     - Steps 53-57: Extra day of wheat maturation.                             |
|     - Steps 84-91: Deterministic late harvest + pasture rebuild + delivery.   |
+-------------------------------------------------------------------------------+
|  2. V219 SE-Tomato Demand Union Gate                                          |
|     - Native: money >= 12000 & shops >= 3 & price >= 70                       |
|     - Addon: money >= 8000 & shops >= 2 & price >= 78                         |
|     - Unlocks 25 SE tiles for tomato production on rich seeds.               |
+-------------------------------------------------------------------------------+
|  1. Day-20 Horizon Discounted Fert-ROI Gate                                   |
|     - value < (1.3*cost+30 if day<20 else 1.5*cost+50)                        |
|     - Captures early soil productivity; cuts late over-hiring after day 20.   |
+-------------------------------------------------------------------------------+
|  0. Core Chassis: MetaV4 Spine (Routes, Labor Allocation & Unit Model)        |
+-------------------------------------------------------------------------------+
```

---

## 4. Benchmark & Gate Results (Engine 1.32.7 Hinge, Interval 24)

### A. R1 Tuning Seed Bank (8 Seeds x 2 Seats = 16 Games)
| Opponent | R1 Win/Loss/Tie | Mean Delta | Min Delta | Max Delta | Outcome |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`friend_r78ub.py`** | **1W / 0L / 7T** | **+9.2** | +0 | +74 | **Zero Losses** (Upgraded previous best) |
| **`crop_roi30_h20.py`** | **8W / 0L / 0T** | **+568.4** | +27 | +3,143 | **100% Win Rate** |
| **`pub_farmer_john_v56.py`** | **4W / 0L / 4T** | **+565.6** | +0 | +3,115 | **Zero Losses** (Fixed seed 2M defect) |
| **`pub_v54_productive.py`** | **5W / 0L / 3T** | **+574.9** | +0 | +3,115 | **Zero Losses** |
| **`pub_one_more_wheat.py`** | **5W / 0L / 3T** | **+574.9** | +0 | +3,115 | **Zero Losses** |
| **`pub_metav4_early.py`** | **8W / 0L / 0T** | **+608.5** | +28 | +3,143 | **100% Win Rate** |

### B. R2 Holdout Seed Bank (8 Seeds x 2 Seats = 16 Games)
| Opponent | R2 Win/Loss/Tie | Mean Delta | Outcome |
| :--- | :---: | :---: | :--- |
| **`friend_r78ub.py`** | **1W / 0L / 7T** | **+0.9** | Zero Losses |
| **`crop_roi30_h20.py`** | **8W / 0L / 0T** | **+28.2** | 100% Win Rate |
| **`pub_farmer_john_v56.py`** | **4W / 0L / 4T** | **+92.0** | Zero Losses |
| **`pub_v54_productive.py`** | **4W / 0L / 4T** | **+93.0** | Zero Losses |
| **`pub_metav4_early.py`** | **8W / 0L / 0T** | **+120.5** | 100% Win Rate |

### C. 16 Fresh Holdout Seeds (30000000..30015000, 32 Games)
* **vs `friend_r78ub.py`**: **2W / 0L / 14T** (+3.9 mean, **ZERO seed-level losses**)
* **vs `crop_roi30_h20.py`**: **16W / 0L / 0T** (+31.6 mean, **100% Win Rate across all 16 seeds**)
* **vs `pub_farmer_john_v56.py`**: **8W / 1L / 7T** (+103.6 mean)
* **vs `pub_metav4_early.py`**: **15W / 1L / 0T** (+135.5 mean)

---

## 5. Deployment & Submission Record

* **Target File**: `submission.py`
* **Backup / Mirror**: `agents/submission_apex_final.py` & `agents/pub_apex_v1.py`
* **Kaggle Submission Reference**: `56433342`
* **Submission Status**: `SubmissionStatus.COMPLETE`
* **Kaggle Description**: `Apex V1: metav4 spine + h20 fert-ROI d20 + V219 tomato union gate + Gluzdov CL mature-wheat + OW guarded opening & queue defrag`
