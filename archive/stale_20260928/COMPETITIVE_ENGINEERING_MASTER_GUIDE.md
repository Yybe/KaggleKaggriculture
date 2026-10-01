# Competitive Engineering Master Guide: Base Selection, Strategy Forensics, Modular Grafting & Fleet Validation

**Document Title**: `COMPETITIVE_ENGINEERING_MASTER_GUIDE.md`  
**Purpose**: An end-to-end, self-contained operational workflow manual for any AI or human agent to analyze, reverse-engineer, modify, and validate competitive simulation models in `kaggriculture` (or equivalent multi-agent game environments).

---

## 1. High-Level Architecture & Philosophy

The pipeline operates on four invariant principles:
1. **Never mutate the core 1 MB spine directly**: Base production routes, pathfinding, and task schedulers are tightly coupled. Hand-editing causes catastrophic silent regressions. Always engineer changes as **modular onion-skin wrappers** (`_PARENT = agent; del agent; def agent(...)`).
2. **God's-Eye Forensic Audit Before Code**: Never guess what the model lacks. Inspect action-tape forensics, telemetry deltas, and live replay loss logs under omniscient simulation views.
3. **Seed Ties Are Defects, Not Victories**: In deterministic environments, identical agents produce identical moves. Mirror matches ending in draws indicate an untested interaction layer. Break symmetry on the market/liquidation axis.
4. **Deterministic 3-Tier Gating**: Every candidate must prove statistical dominance across three distinct seed banks (R1, R2, Fresh holdouts) with zero seed-level crashes and verified positive win margins before live deployment.

---

## 2. Phase 1: Base Selection & Lineage Benchmarking

### Objective
Identify whether an existing champion or newly pulled notebook model possesses a superior core chassis, or if its losses stem from interaction/timing defects.

### Step-by-Step Procedure
1. **Ingest and Clean Artifact**:
   - Extract raw code from Kaggle kernel blobs (`base85 + zlib` decoding) into `agents/pub_<name>.py`.
   - Assert entrypoint callability (`agent(observation, configuration)`).
   - Check file integrity via SHA-256 (`tools/check_hashes.py`).

2. **Run Head-to-Head Cross-Lineage Matrix**:
   - Execute parallel pairwise evaluations using `tools/fast_matrix_eval.py` against known public lineages:
     - `metav4` spine (`pub_apex_v1.py` / `pub_metav4_r78u.py`)
     - `funding-order invariant` spine (`pub_v57_funding.py`)
     - `orderbook` spine (`pub_shiiin9_orderbook.py`)
     - `smarter` spine (`pub_v56_smarter.py`)
     - `omw` clean lineage (`pub_e94_omw_clean.py`)

3. **Decision Law**:
   - If candidate beats all current public lineages on R2 and Fresh holdouts (e.g. `pub_v57_funding.py` winning +247.8 mean against Apex V5), adopt it as the **new production chassis**.
   - Inspect specific failure modes on losing banks (e.g. R1 early deficit or endgame liquidation).

---

## 3. Phase 2: Top-Leaderboard DNA & Replay Forensics

### Objective
Extract the hidden strategy parameters of top human/bot teams (Majkel1337, DSM, SpaTaro, THIRD FARM CLUB, 涵哥) from recorded game replay archives.

### Tools & Scripts
- Archive: `WybeV2/datasets/e98f_top10/episodes.parquet`
- Ingestion: `tools/batch_fetch_replays.py` / `tools/fetch_episodes.py`
- Step-by-Step Forensic Parser: `tools/live_loss_anatomy_0920b.py`
- Side-by-Side Comparator: `scratch/inspect_v57_vs_top10.py`

### Key Extracted DNA Metrics

| Metric Category | Telemetry Key | Baseline / V57 Pattern | Top-10 Champion Pattern | Tactical Implication |
|---|---|---|---|---|
| **Labor Curve** | `action['units'] -> HIRE` | 260–280 total hires; rigid window stops | 280–305 hires; 2 extra late-stage hands | Higher end-game carrying & harvest bandwidth |
| **Fertilizer Intensity** | `action['units'] -> FERTILIZE` | 85–126 fertilize ops; dumps 2,362 units to market | **135–249 fertilize ops**; fert sales capped at 170–270 | Champions consume fert for exponential crop value rather than acting as raw fert merchants |
| **Everplant Matrix** | `action['units'] -> PLANT` | `{'WHEAT': 160, 'STRB': 33, 'MELON': 12, 'CARROT': 34, 'TOMATO': 0}` | `{'WHEAT': 110-150, 'STRB': 25-45, 'TOMATO': 20-30, 'CARROT': 60-100}` | Diversified multi-crop rotation tailored to town store unlocks |
| **Market Cadence** | `action['market'] -> SELL` | Rigid step % 24 == 0 waves (synchronized with town center) | Preemptions at step % 24 == 23 + **Days 28–30 bulk dumps** | Avoids price crashes; extracts maximum endgame liquidity |

---

## 4. Phase 3: God's-Eye View Loss Anatomy

### Objective
Inspect losing games step-by-step from an omniscient simulation observer (`env.steps`) to identify the exact step and mechanism where points are lost.

### Forensic Procedure
1. **Replay Ingestion**:
   - Pull replay JSON files of losses (`results/live_replays_0920b/` or local loss reproduction runs).
2. **Trajectory Breakdown**:
   - Track per-step cumulative money, shed inventory, and unit task states for both players simultaneously.
3. **Loss Classification**:
   - **Class (a) Mirror Coinflip**: ≥80% identical action tape, score difference ≤1% (settlement race).
   - **Class (b) Structural Production Gap**: Opponent out-yields on high-margin cash crops or fertilizer utilization.
   - **Class (c) Plumbing Collapse**: Worker starvation, broken routing, dead loops, or empty action lists.
   - **Class (d) Endgame Dump Family**: Opponent hoards produce and emits bulk `SELL <item> 1000` orders on steps 672..719.

### Case Study: `pub_v57_funding.py` Losses
- **Discovery**: Against opponent `涵哥` (Episode 111231254), boards were identical through Day 18. At step 672+ (Days 28–30), the opponent emitted 84 bulk market orders across 9 shed products into peak demand prices, generating +83.8k late-game cash vs our +55.0k (+24,593 margin gap!).
- **Diagnosis**: The base model held substantial harvested inventory in the private shed without market orders to liquidate them before episode step 720.

---

## 5. Phase 4: Modular Onion-Skin Grafting

### Objective
Implement strategy fixes as isolated, append-only wrappers without touching the base source code.

### Construction Rules (Rule 5 & Rule 2)
1. **Base Ingestion**: Read clean base file as text.
2. **Append-Only Wrapper**:
   ```python
   _V57_PARENT = v57_agent

   def v57_candidate_agent(observation, configuration=None):
       # 1. Pre-execution / Early filters (e.g. crop overrides)
       ...
       # 2. Execute base parent chassis
       action = _V57_PARENT(observation, configuration)
       ...
       # 3. Post-execution overlays (e.g. market order injections)
       ...
       return action

   agent = v57_candidate_agent
   kaggle_submission_agent = v57_candidate_agent
   ```
3. **Automated Graft Verification**:
   - Byte size delta check: `assert os.path.getsize(OUT_FILE) > os.path.getsize(BASE_FILE)`.
   - Entrypoint marker check: `assert out_code.count("v57_candidate_agent") >= 2`.
   - Clean module import test: `import candidate; assert callable(candidate.agent)`.

### Graft Exploration History

| Candidate | Mechanism Tested | Outcome vs Base | Root Cause Analysis |
|---|---|---|---|
| **V8** (`pub_v57_apex_v8.py`) | Step-23 Debt Preemption | **0W / 32L** (-165k) | Market orders at step 23 collided with v57's `_cxd_candidates` funding queue, breaking worker hires. |
| **V9** (`pub_v57_apex_v9_exploit.py`) | Tomato Gate + Step-23 Preemption | 13W / 19L (-102.9) | Preemption still thrashed funding slots; tomato gate alone insufficient. |
| **V10** (`pub_v57_apex_v10_clean.py`) | Tomato Gate + Steps 716-719 Sweep | 0W / 0L / 32T (+0.0) | Terminal sweep steps 716-719 had too narrow a window (shed items already locked or empty). |
| **Mature Wheat** (`pub_v57_mature_wheat.py`) | Delay early wheat harvest | 0W / 0L / 32T (+0.0) | Early harvest timing already optimal in v57. |
| **V11 Dump** (`pub_v57_apex_v11_dump.py`) | **Days 28–30 (steps 672..719) Bulk Shed Dump** | **22W / 10L / 0T (+63.5)** | **Dominant Breakthrough**: Consistently empties shed into all remaining open market slots over last 48 steps. |

---

## 6. Phase 5: Multi-Tier Deterministic Gating

### Verification Architecture
Simulations run with `kaggle-environments==1.32.7`, `episodeSteps=720`, `townCenterSellInterval=24`. Each seed is evaluated twice (swapping Player 0 and Player 1 seats) to eliminate seat bias.

```
Total Evaluation: 32 Seeds x 2 Seats = 64 Games
├── Tier 1: R1 Tuning Bank (8 Seeds x 2 = 16 Games)
│   Seeds: [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]
├── Tier 2: R2 Holdout Bank (8 Seeds x 2 = 16 Games)
│   Seeds: [1110000, 2220000, 4440000, 5550000, 6660000, 8880000, 9990000, 1111111]
└── Tier 3: Fresh Holdout Bank (16 Seeds x 2 = 32 Games)
    Seeds: [30000000, 30001000, ..., 30015000]
```

### Acceptance Thresholds
- **Zero Crashes / Timeouts**: All 64 games must complete cleanly without unhandled exceptions.
- **Positive Seed Margin**: Net coin delta must be positive across all banks.
- **Superiority Over Base**: Win rate against original base model must exceed 60%.

---

## 7. Phase 6: Full Public Fleet Cross-Validation

Before deploying any winning candidate to Kaggle, run cross-validation against the entire tournament fleet (64 games per opponent = 384+ games total) via `scratch/bench_v11_full_fleet.py`:

```
Fleet Benchmark Matrix for Apex V11:
- vs pub_v57_funding.py:       22W / 10L /  0T (+63.5 mean delta)
- vs pub_apex_v5.py:           26W /  6L /  0T (+277.9 mean delta)
- vs pub_v56_smarter.py:       28W /  4L /  0T (+201.0 mean delta)
- vs pub_shiiin9_orderbook.py: 22W / 10L /  0T (+146.6 mean delta)
- vs pub_e94_omw_clean.py:     27W /  5L /  0T (+313.0 mean delta)
- vs pub_metav4_r78u.py:       28W /  4L /  0T (+352.7 mean delta)
------------------------------------------------------------------
GRAND TOTAL: 153 WINS / 39 LOSSES / 0 TIES (79.7% WIN RATE)
```

---

## 8. Phase 7: Deployment & Kaggle Submission

### Single-File Packaging
1. Copy winning candidate to root deployment target:
   ```bash
   cp agents/pub_v57_apex_v11_dump.py submission.py
   ```
2. Verify module interface:
   ```bash
   python -c "import submission; assert callable(submission.agent); assert callable(submission.kaggle_submission_agent)"
   ```
3. Deploy via Kaggle CLI:
   ```bash
   kaggle competitions submit -c kaggriculture -f submission.py -m "Apex V11: v57 funding-order invariant base + Days 28-30 bulk cargo dump & terminal sweep (79.7% fleet win rate, 153W/39L)"
   ```
4. Archive documentation:
   Create `APEX_V<N>_AGENT_DOCUMENTATION_YYYYMMDD.md` recording code provenance, benchmark numbers, architecture stack, and commit hashes.

---

## 9. Quick-Reference Checklist for Any Future Base

When handing this workflow to an agent for an arbitrary new model `pub_new.py`:
- [ ] **Step 1**: Benchmark `pub_new.py` vs champion (`pub_apex_v11_dump.py`) across 64 seeds.
- [ ] **Step 2**: If `pub_new.py` wins, run side-by-side strategy DNA extraction (`scratch/inspect_v57_vs_top10.py`).
- [ ] **Step 3**: Identify residual shed inventory and market timing defects via God's-view loss logs.
- [ ] **Step 4**: Build onion-skin graft scripts (`tools/build_new_apex.py`).
- [ ] **Step 5**: Test candidate against parent `pub_new.py` across R1, R2, and Fresh banks.
- [ ] **Step 6**: Validate across the 6-model public sparring fleet.
- [ ] **Step 7**: Deploy to `submission.py` and verify entrypoints.
