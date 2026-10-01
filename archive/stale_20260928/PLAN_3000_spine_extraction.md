# PLAN: 2800 → 3000+ via top-player spine extraction

Context: scout 56387781 (`agents/pub_metav4_early.py`) live 2784.3, 48W/8L (2026-09-20).
Top-10 cut = 3020 (Majkel1337 3234, DSM 3177, Unknown Mother-Goose 3061, THIRD FARM CLUB 3053, SpaTaro 3048).
Keep 56387781 running — pool-relative rating drifts up for free.

## Closed levers (do NOT re-open)
- Overlay/wrapper surface: 9 refuted (see LEDGER E42–E52, memory `project-production-overlay-laws`).
- Sell-timing overlays: v37/v40/v41/dpt all lose (`project-sell-timing-overlay-refuted`).
- Fert-retention: refuted by inspection — `_r85_fertilizer` sells only above plan reserve; fert sales are top-5 revenue.
- Donor panel: CLOSED, 88 runnable public donors, champ undefeated (`results/donor_sweep.log`, LEDGER H30).
- metav4_plus v233-gate tweak: AUDIT-REFUTED (LEDGER E52 AUDIT). Loss doesn't reproduce locally; early beats same Kawatta tape +14,202 WITH commit. Never believe a replay-cured "turnaround" without an early-control run on the same seed.
- 5/8 live losses = exact tape-mirror coinflips. Unfixable (E42–E47 laws). Mirror gates cannot measure opponent-conditional fixes.

## Real gap
Loss class = fertilizer-intensity crop-max spines: opp fert 135–182 vs ours 85–110 (keiz -6,227; KawattaTaido -12,045). Top-10 run private/native spines. Need that plan class.

## Steps

### 1. Pull top-10 replay tapes
- Fetch recent high-rated episodes for: Majkel1337, DSM, Unknown Mother-Goose, THIRD FARM CLUB, SpaTaro, M&M&P&Q, ymg_aq, Orbital Terraformer, QQ, Otter Vibe.
- `kaggle competitions episodes kaggriculture ...` + `tools/extract_live_opponents.py`; save under `results/top10_tapes/`.
- Existing pipeline reference: `agents/live_replay/opp_*.py` (zlib+b85 action-tape replay + weed repair, adaptive-market disabled).

### 2. Fingerprint each spine
- Rebuild each as a tape-replay donor agent (`opp_<name>_*.py`).
- Run vs champ; produce anatomy like `results/bigloss_0920_fp.txt`: land, water, fert count, plant mix, harvests, revenue lines (wheat/milk/wool/fert-sales), SE/land buys, crew count.
- Classify: PLAN (route table + fert reserve, re-synthesizable) vs REACTIVITY (price-read we can graft).

### 3. Build path (in EV order)
- **3a. Spine graft (preferred):** any top tape beating champ on ≥2 of 3 gate8 fleet checks → port its fert-route/crew plan onto our base as a NEW SPINE (not overlay). How metav4_early was made.
- **3b. Plan synthesis:** if tapes are crop-max with fert-reserve ≥135 + different sell order → re-tune E182 planner route table offline (`agents/pub_metav4_early.py` line ~2598 route reserve `max(14, cache[route]+dedicated)`).

### 4. Gates (mandatory, every challenger)
- Engine assert FIRST: `WybeV2/rank_env/Scripts/python.exe tools/engine_assert.py` (must PASS, engine 1.32.7 + hinge; LEDGER E33 law).
- Gate8: `tools/diag_bench_seeds.py BASE CHALLENGER 1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000 OUT --interval 24` (8 seeds x 2 seats, ~60-80s).
- Promote vs `agents/pub_metav4_early.py` + fleet set (`pub_demand_timing`, `pub_metav4`, distinct-8 shields) — challenger must win outright, 0 ties tolerated, on ≥2 independent gate8 runs.
- Run sweeps detached + resumable (`nohup`, `tools/donor_screen.sh` pattern) — Bash bg has 10-min cap (memory `project-gate-sweep-ops`).
- Bench integrity (memory `project-bench-integrity-pitfalls`): fresh process per agent, hash both files before trusting a ladder, check engine version after any subagent run.

### 5. Submit
- Only with explicit user approval (standing rule). Staged file pattern: `submission_<name>.py` byte-identical to agent, record md5 in `results/LEDGER_YYYYMMDD.md`.
- Last-two-submissions rule: submitting replaces old 56365513, keeps 56387781 alive as comparison.

## Done-criteria
- Changelog: `results/LEDGER_20260921.md` (E53+) with tape list, fingerprints, gate logs under `results/`.
- Memory update: `project-2700-bottleneck-fert.md` when a spine candidate passes or the class is refuted.
