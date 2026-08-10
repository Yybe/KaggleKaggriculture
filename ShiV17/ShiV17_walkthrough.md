# Walkthrough — V17 Apex Agent (Boatlee-Slayer)

> [!NOTE]
> **User Memory Notice**: The file `paper_texture.png` remains missing in the workspace.

## Summary of Accomplishments

We reverse-engineered **boatlee V16-RC2** (`boatlee_v16rc2/main.py`), identified its core mechanics and vulnerabilities, and created **V17 Apex** (`WybeV2/v17_apex.py` & root [`submission.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/submission.py)).

### 1. Reverse Engineering Findings on Boatlee V16-RC2
- **Static Route Core**: Boatlee uses a hardcoded 719-step action sequence (`_REBALANCE_ACTIONS`) with a low-entropy `HIRE4` opening.
- **3-Turn Market Relay (`_rc2_market_relay`)**: Boatlee detects mirror farm signatures at steps 216, 240, 264. When locked on, it dumps all available fertilizer **3 steps early** (`lead = 3`, `step % 24 == 14`) before scheduled sales at `(future_step % 24) == 17`.
- **The Critical Vulnerability**: Boatlee's relay lead is strictly fixed at 3 turns. If an opponent dumps fertilizer **1 turn ahead** (at `lead = 5` / `lead = 4`), the opponent captures peak market prices ($100-$200+ per unit), driving market prices down to $1 before boatlee's turn executes.

### 2. Implementation of V17 Apex
- Created [`v17_apex.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/WybeV2/v17_apex.py) with **5-Turn Counter-Relay (`_rc3_counter_relay`)**.
- When mirror farms are detected, V17 Apex dumps fertilizer at `_RC3_RELAY_LEAD = 5` (`step % 24 == 12`), 2 steps before boatlee's dump (`step % 24 == 14`).
- Bundled into root [`submission.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/submission.py) and verified clean imports.

---

## Verification & Benchmark Results

### 1. Head-to-Head vs Boatlee V16-RC2 (Exact 8-Seed Gate Family x 2 Seats = 16 Games)
- **Previous V16a Record**: **0W / 16L** (0.0% Win Rate, Mean Δ −14,735)
- **New V17 Apex Record**: **15W / 1L** (**93.8% Win Rate**, Mean Δ **+176**)

| Matchup | Seed | Seat Swap | V17 Score | Boatlee Score | Margin | Winner |
|---|---|---|---|---|---|---|
| Seed 1000000 | 1000000 | 0 | 71,363 | 72,616 | −1,253 | Boatlee |
| Seed 1000000 | 1000000 | 1 | 72,794 | 71,185 | **+1,609** | **V17 Apex** |
| Seed 2000000 | 2000000 | 0 | 81,329 | 81,153 | **+176** | **V17 Apex** |
| Seed 2000000 | 2000000 | 1 | 81,329 | 81,153 | **+176** | **V17 Apex** |
| Seed 3330000 | 3330000 | 0 | 85,883 | 85,707 | **+176** | **V17 Apex** |
| Seed 3330000 | 3330000 | 1 | 85,883 | 85,707 | **+176** | **V17 Apex** |
| Seed 5000000 | 5000000 | 0 | 69,799 | 69,623 | **+176** | **V17 Apex** |
| Seed 5000000 | 5000000 | 1 | 69,799 | 69,623 | **+176** | **V17 Apex** |
| Seed 6000000 | 6000000 | 0 | 41,392 | 41,216 | **+176** | **V17 Apex** |
| Seed 6000000 | 6000000 | 1 | 41,392 | 41,216 | **+176** | **V17 Apex** |
| Seed 7770000 | 7770000 | 0 | 88,937 | 88,761 | **+176** | **V17 Apex** |
| Seed 7770000 | 7770000 | 1 | 88,937 | 88,761 | **+176** | **V17 Apex** |
| Seed 8000000 | 8000000 | 0 | 99,589 | 99,413 | **+176** | **V17 Apex** |
| Seed 8000000 | 8000000 | 1 | 99,589 | 99,413 | **+176** | **V17 Apex** |
| Seed 9000000 | 9000000 | 0 | 110,785 | 110,609 | **+176** | **V17 Apex** |
| Seed 9000000 | 9000000 | 1 | 110,785 | 110,609 | **+176** | **V17 Apex** |

### 2. Head-to-Head vs Kaitofukami v27 (8 Games)
- **V17 Apex Record**: **6W / 2L** (**75% Win Rate**, Mean Δ +28)

---

## Conclusion

V17 Apex successfully neutralizes boatlee V16-RC2's market relay, turning a previous **0W/16L** defeat into a dominant **15W/1L (93.8% win rate)** victory. The updated code is saved to [`submission.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/submission.py) and ready for Kaggle deployment.
