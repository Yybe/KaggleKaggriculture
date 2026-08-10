# Implementation Plan: Beat boatlee V16-RC2 (V17 Apex Agent)

> [!NOTE]
> **User Memory Notice**: Please note that the `paper_texture.png` file is currently missing in the workspace.

## Problem & Diagnosis

In recent benchmark rounds, our submission **V16a** lost **0W/16L** to both **kaitofukami v27** (mean Δ −13,639) and **boatlee V16-RC2** (mean Δ −14,735). Boatlee V16-RC2 also defeated kaitofukami v27 **15W/1L** (mean Δ +3,613).

### Root Cause Analysis of Boatlee V16-RC2
By extracting and reverse-engineering `WybeV2/boatlee_v16rc2/main.py`, we identified boatlee's exact mechanics and flaws:
1. **Static Replay Engine**: Boatlee relies on a compressed 719-step hardcoded action route (`_REBALANCE_ACTIONS`) with low-entropy `HIRE4` opening.
2. **3-Turn Market Relay (`_rc2_market_relay`)**:
   - At steps 216, 240, 264, boatlee computes public farm signature distance (`_rc2_route_distance(obs) <= 8`).
   - If distance is small (mirror farm detected), it locks on (`locked = True`).
   - For scheduled fertilizer sales at `future_step` (`(future_step % 24) == 17`), boatlee sells ALL available fertilizer **3 turns early** (`step = future_step - 3`, i.e. `step % 24 == 14`).
   - This crashes the fertilizer price for the mirror opponent right before the opponent's scheduled sell turn.
3. **Flaws & Exploits in Boatlee V16-RC2**:
   - **Fixed 3-Turn Lead Vulnerability**: Boatlee always relays at `lead = 3` (`step % 24 == 14`). A **4-turn counter-relay** (`lead = 4`, `step % 24 == 13`) will sell fertilizer **1 turn before boatlee**, reaping maximum price ($100+) and crashing the price to $1 right before boatlee's relay executes!
   - **Debt Repayment Deficit**: Boatlee's `_rc2_repay` logic expects to deduct sold fertilizer at `future_step`. If its early dump yields $1 instead of target prices because we front-ran it, boatlee suffers massive revenue collapse.
   - **Lack of Dynamic Town-Shop Arbitrage**: Boatlee's route cannot dynamically re-route crops or animals to high-yield town shops beyond basic YARN_STORE wool checks.

---

## User Review Required

> [!IMPORTANT]
> - We will create a new agent architecture **`V17 Apex`** in `c:\Users\xxshi\Desktop\farmmasterV2\WybeV2\v17_apex.py` and bundle it to `submission.py`.
> - The strategy combines the dominant 719-step HIRE4 baseline engine with an aggressive **4-Turn Counter-Relay (`_rc3_counter_relay`)**, **Market Front-Running**, and **Dynamic Town-Shop Arbitrage**.

---

## Proposed Changes

### WybeV2 (Benchmark & Agent Core)

#### [NEW] [`v17_apex.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/WybeV2/v17_apex.py)
- Implement `V17 Apex` agent with:
  1. **719-Step Baseline Engine**: Base low-entropy HIRE4 production route with weed repair.
  2. **4-Turn Counter-Relay (`_rc3_counter_relay`)**: Detects opponent mirror signatures and executes 4-step lead fertilizer dumps (`step % 24 == 13`), front-running boatlee's 3-step relay (`step % 24 == 14`).
  3. **Town-Shop Price Arbitrage**: Upweights high-demand goods for active town shops.
  4. **Dynamic Market Ranking**: Ranks market orders by net price impact and urgency score.

#### [MODIFY] [`submission.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/submission.py) & [`build_v16_submission.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/build_v16_submission.py)
- Update build pipeline to bundle `v17_apex.py` as the main submission file.

---

## Verification Plan

### Automated Head-to-Head Benchmarks
Run 16-game H2H benchmarks (8 seeds × 2 seats) using `simulate_h2h.py`:
1. `v17_apex.py` vs `boatlee_v16rc2/main.py`
2. `v17_apex.py` vs `kaitofukami_v27/main.py`
3. `v17_apex.py` vs `submission_salemali7.py`

**Success Criteria**:
- `v17_apex.py` defeats `boatlee_v16rc2` with a winning record (>50% win rate, target >80%) and positive mean delta (> +3,000).
- `v17_apex.py` defeats `kaitofukami_v27`.
- No runtime exceptions or timeouts.
