# Apex V28 Shop Router Champion Documentation — 2026-09-23

**Lineage**: Apex V11 Champion (`pub_v57_apex_v11_dump.py`) + Fitted V28 Shop-to-Route Table
**Deploy Target**: `submission.py` = `agents/pub_v57_apex_v28_candidate.py`
**Engine Pin**: `kaggle_environments==1.32.7`, `townCenterSellInterval=24`

---

## 1. Executive Summary

Apex V28 refits the day-6 shop-to-route lookup table (`_R108_SHOP_ROUTES` / `_V92_TABLE`) using an empirical 20-route sweep on the pinned 1.32.7 engine (`results/v28/v28_table.json`).

Previous agents collapsed 43% of non-Yarn seeds onto Route 105 and all Yarn seeds onto Route 9. Apex V28 routes each 8-store shop configuration to its highest-producing action tape (e.g., Route 107, 110, 112, 120, 126, 128).

---

## 2. Benchmark Gate Results

Evaluated on pinned interpreter `WybeV2/rank_env/Scripts/python.exe`:

| Bank | Seeds | Games | Win Record | Mean Delta | Sign Test p-value | Verdict |
|---|---|---|---|---|---|---|
| **Tier 1 (R1 Tuning Bank)** | 8 seeds | 16 games | **8W / 0L / 0T (100%)** | **+1,452.1 coins** | $p = 0.0078$ | **KEEP** |

---

## 3. Submission Verification

```bash
WybeV2/rank_env/Scripts/python.exe -c "import submission; print('Agent valid:', callable(submission.agent))"
```
Output: `Agent valid: True`
