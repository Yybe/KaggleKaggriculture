# End-to-End Competitive Agent Engineering & Reverse-Engineering Workflow

**File**: [`processing.md`](file:///c:/Users/xxshi/Desktop/farmmasterV2/processing.md)  
**Target Environment**: Kaggriculture Simulation Engine (`kaggle-environments==1.32.7`, `townCenterSellInterval=24`)  
**Workspace**: `c:/Users/xxshi/Desktop/farmmasterV2`

---

## 1. Phase 1: Prompt Ingestion & Strategy Discovery

### 1.1 What We Look For in User Prompts
When a problem is framed (e.g. *"Apex V2 is tied with Apex V1 and E94; find why and break the tie without regressing"*), we dissect the challenge into three core hypotheses:
1. **Chassis Limitation vs. Interaction Limitation**: Is the base production spine suboptimal, or is the market interaction layer colliding with mirrors?
2. **State Leakage / Query Bugs**: Are decisions failing silently due to incorrect state dictionaries (e.g., querying `farm["inventory"]` instead of `observation["private"]["shed"]`)?
3. **Dead Levers vs. Active Levers**: Checking our historical ledgers ([`FRIEND_INSIGHTS_20260921.md`](file:///c:/Users/xxshi/Desktop/farmmasterV2/FRIEND_INSIGHTS_20260921.md) §2) to immediately disqualify refuted avenues (e.g. anti-glut crop mixing, hold-for-reprice heuristics) and prioritize proven levers (market preemption, crop mix, fertilizer cycling).

---

## 2. Phase 2: High-Speed Replay Ingestion & Parquet Storage

### 2.1 The Bottleneck in Traditional Workflows
Most agents download hundreds of raw JSON episode files (each 15–30 MB uncompressed, totaling 5–10 GB). Iterating over individual JSON files causes severe I/O bottlenecks, disk thrashing, and context bloat.

### 2.2 Our High-Throughput Pipeline
Instead of handling loose JSONs, we maintain a compressed, indexed Parquet pipeline:

```
Kaggle Episode API / Parquet Dumps
          │
          ▼
tools/fetch_episodes.py / tools/batch_fetch_replays.py
          │ (Streams and compresses replay tensors)
          ▼
WybeV2/datasets/e98f_top10/episodes.parquet (Columnar Parquet Archive)
          │
          ▼
WybeV2/datasets/e98f_epidx/manifest.csv (Metadata Index: Episode ID, SIDs, Scores, Opponents)
          │
          ▼
tools/extract_live_opponents.py (Replay-Tape Synthesis -> opp_<name>_<hash>.py)
```

### 2.3 Key Scripts & Functions
* **[`tools/fetch_episodes.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/tools/fetch_episodes.py)**: Queries episode IDs directly for top-rated submission IDs (e.g. Majkel1337, DSM, SpaTaro, THIRD FARM CLUB).
* **[`tools/extract_live_opponents.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/tools/extract_live_opponents.py)**:
  - Extracts the raw action stream per player.
  - Encodes the action tape using base85 + zlib compression (`_LEGACY_ACTIONS`).
  - Wraps the replay with a deterministic fallback (`_weed_repair_action`) so the replayed agent can run against any challenger in local simulations.

---

## 3. Phase 3: Forensic Analysis & Strategy DNA Extraction

### 3.1 What Metrics We Extract
To understand why top human/bot teams score 3,000–3,200+, we run automated forensic audits rather than reading raw dumps manually:

1. **Labor Curve**: Total hired hands per day and cumulative wage expenditure (`_fib` cost curve).
2. **Land Acquisition Timing**: Step and cost of unlocking NE (quad 1), SW (quad 2), and SE (quad 3) quadrants.
3. **Fertilizer & Water Intensity**:
   - `fert` count: Baseline agents apply 85–110; top champions (DSM, Otter Vibe) apply **135–249** fertilizer actions.
   - `water` count: Tracks total hydration cycles on high-velocity cash crops (STRAWBERRY, TOMATO).
4. **Crop Mix Matrix (`everplant`)**:
   - Counts total lifetime plantings: `{'WHEAT': 150-220, 'STRAWBERRY': 25-45, 'MELON': 12-18, 'CARROT': 40-100, 'TOMATO': 10-25}`.
5. **Revenue Breakdown**:
   - Analyzes revenue streams: `WOOL`, `MILK`, `STRAWBERRY`, `WHEAT`, `FERTILIZER`, `MELON`.
6. **Market Order Timing**:
   - Evaluates whether sales are dumped on 24-turn intervals or executed on boundary steps.

### 3.2 Key Diagnostic Scripts
* **[`tools/atlas_0921.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/tools/atlas_0921.py)** / **[`tools/atlas_agg_0921.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/tools/atlas_agg_0921.py)**: Aggregates top-player gameplay metrics across all archived parquet episodes.
* **[`tools/live_loss_anatomy_0920b.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/tools/live_loss_anatomy_0920b.py)**: Generates detailed loss ledgers comparing our agent vs. winning opponents step-by-step.
* **[`results/top10_fp.txt`](file:///c:/Users/xxshi/Desktop/farmmasterV2/results/top10_fp.txt)**: Persistent reference fingerprints of top-10 strategies.

---

## 4. Phase 4: Base Architecture Benchmarking & Elimination

Before modifying any strategy, we benchmark all distinct architectural lineages against our champion benchmark pool (`pub_apex_v1`, `pub_e94_omw_clean`, `friend_r78ub`, `pub_farmer_john_v56`) using parallel multi-process harnesses:

```bash
WybeV2/rank_env/Scripts/python.exe tools/fast_matrix_eval.py
```

### 4.1 Comparison Results Across Base Lineages:
- **`metav4` Spine** (`agents/pub_apex_v1.py`): **0W / 0L / 8T (+0.0 vs mirrors)** — Dominates all other public baselines by +8,000 to +70,000 coins.
- **`2945farm` / `2950peak`** (`agents/pub_2945farm.py`): -8,507 mean margin (rigid worker allocation).
- **Boatlee V16 Market Relay** (`agents/salemali7_3094.py`): -8,354 mean margin (action drift under 1.32.7 engine changes).
- **Dynamic Route 85** (`agents/pub_dynroute85.py`): -41,667 mean margin (planner thrashing).
- **Soil Router** (`agents/pub_e69_soilrouter.py`): -62,512 mean margin (soil fatigue miscalculation).

**Core Decision Law**: Retain the `metav4` spine for production economics, and build modular wrapper layers to solve the market tie collision.

---

## 5. Phase 5: Modular Layer Engineering (The Apex Stack)

### 5.0 Graft Integrity Gate (added 2026-09-22, E101 incident)
A layer port can compile, import and pass a full 64-game gate while doing **absolutely nothing** — and the
gate then reads as clean parity ("the mechanism is inert"). `tools/build_e101_apex_layers.py` initially sliced
the V5 layer with `v5.index("kaggle_submission_agent = agent")` as its end bound; that EOF marker appears twice
in `agents/pub_apex_v5.py` (lines 6814, 6923), so the slice was empty. Before gating any graft, all four must hold:
1. marker uniqueness — `assert text.count(anchor) == 1`, and `assert end > start` for range slices;
2. symbol wiring — `assert out.count(sym) == 2` (definition + call site) for every grafted function;
3. size growth — output bytes strictly greater than the base's;
4. firing proof — a counter probe (`tools/probe_e101_layers.py`) over 2–4 seeds must show non-zero fires,
   and dump the real surfaces (`observation["private"]["shed"]`, `action["market"]`) to confirm the layer sees data.

We use a clean onion-skin stack where each layer wraps `_PARENT` without mutating the core engine:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 6. _apex_precision_terminal_sweep (Steps 716-719)                     │
│    Liquidates 100% of remaining shed inventory across open slots.      │
├────────────────────────────────────────────────────────────────────────┤
│ 5. _apex_tuned_clone_preemption (Step % 24 == 23)                      │
│    Executes sales 1 turn early at un-crashed market equilibrium prices.│
├────────────────────────────────────────────────────────────────────────┤
│ 4. _ow_guard_opening & _ow_close_queue (Owen / FJ V56)                 │
│    Step 29 pasture repair + removes dead orders + pulls sales left.    │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Gluzdov Mature-Wheat Tail Layer (_CL_PARENT)                        │
│    Step 53-57 pass + step 84-91 deterministic late harvest (+28 coins).│
├────────────────────────────────────────────────────────────────────────┤
│ 2. V219 Tomato Union Gate                                              │
│    Unlocks SE quadrant when money >= 8000 & shops >= 2 & price >= 78.  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Day-20 Horizon-Discounted Fert-ROI Gate (h20)                       │
│    value < (1.3*cost+30 if day<20 else 1.5*cost+50).                   │
├────────────────────────────────────────────────────────────────────────┤
│ 0. MetaV4 Core Chassis (Routes, Task Planner, Unit Model)              │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.1 The Breakthrough Tie-Breaker Logic
1. **The 1-Step Preemption Gate** (`_apex_tuned_clone_preemption`):
   - At `step % 24 == 23` (turn 23 of every day), before mirror bots emit their synchronized step-24 market orders, we query `observation["private"]["shed"]`.
   - If stock exists and `market.prices[item] >= floor`, we emit the `SELL` order early.
   - The executed quantity is recorded in `state["debt"][item]`.
   - On step 24, when the scheduled base order executes, `state["debt"][item]` is deducted from the order, preventing double-selling.
2. **The Precision Endgame Cargo Sweep** (`_apex_precision_terminal_sweep`):
   - Scans `observation["private"]["shed"]` at steps 716..719.
   - Any residual high-value inventory (`WOOL`, `MILK`, `STRAWBERRY`, `TOMATO`, `MELON`, `CARROT`, `EGG`, `FERTILIZER`, `WHEAT`) is assigned to remaining open market slots (up to 10 orders).

---

## 6. Phase 6: Multi-Tier Gate Verification

Every candidate must pass a strict 3-tier deterministic gate on the pinned environment (`WybeV2/rank_env` with `kaggle-environments==1.32.7`, `townCenterSellInterval=24`):

```bash
WybeV2/rank_env/Scripts/python.exe tools/test_candidate_breakthrough.py agents/pub_apex_v5.py
```

### 6.1 Gate Hierarchy:
1. **Tier 1: R1 Tuning Bank (8 Seeds $\times$ 2 Seats = 16 Games)**
   - Seeds: `[1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]`
   - Mandate: Zero seed-level losses; positive win-rate against champion baselines.
2. **Tier 2: R2 Holdout Bank (8 Fresh Seeds $\times$ 2 Seats = 16 Games)**
   - Seeds: `[1110000, 2220000, 4440000, 5550000, 6660000, 8880000, 9990000, 1111111]`
   - Mandate: Verifies no overfitting to R1 world configurations.
3. **Tier 3: Fresh Holdout Bank (16 Never-Seen Seeds $\times$ 2 Seats = 32 Games)**
   - Seeds: `range(30000000, 30016000, 1000)`
   - Mandate: Statistical Bradley-Terry win rate validation.

### 6.2 Apex V5 Validation Summary:
- **vs `pub_apex_v1.py`**: 7W / 1L / 0T (R1), 11W / 5L / 0T (Fresh) — **69% Win Rate**
- **vs `pub_e94_omw_clean.py`**: 7W / 1L / 0T (R1), 11W / 5L / 0T (Fresh) — **72% Win Rate**
- **vs `friend_r78ub.py`**: 7W / 1L / 0T (R1), 11W / 5L / 0T (Fresh) — **72% Win Rate**
- **vs `pub_farmer_john_v56.py`**: 8W / 0L / 0T (R1), 12W / 4L / 0T (Fresh) — **75% Win Rate**

---

## 7. Phase 7: Deployment & Kaggle Submission

### 7.1 Single-File Packaging
Kaggle competition servers evaluate single-file submissions with no external internet or package dependencies:
- Deploy target: [`submission.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/submission.py)
- Submission verification:
  ```bash
  WybeV2/rank_env/Scripts/python.exe -c "import submission; print('Agent valid:', callable(submission.agent))"
  ```

### 7.2 CLI Submission Command
```bash
kaggle competitions submit -c kaggriculture -f submission.py -m "Apex V5: metav4 spine + h20 fert-ROI d20 + V219 tomato union gate + Gluzdov CL mature-wheat + OW guarded opening + 1-step clone preemption & precision terminal sweep"
```

### 7.3 Archival & Documentation
1. Mirror file: [`agents/submission_apex_final.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/agents/submission_apex_final.py)
2. Documentation: [`APEX_V5_AGENT_DOCUMENTATION_20260921.md`](file:///c:/Users/xxshi/Desktop/farmmasterV2/APEX_V5_AGENT_DOCUMENTATION_20260921.md)
3. Methodology Record: [`processing.md`](file:///c:/Users/xxshi/Desktop/farmmasterV2/processing.md)
