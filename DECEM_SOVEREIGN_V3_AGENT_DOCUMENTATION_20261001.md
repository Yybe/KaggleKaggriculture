# Decem Sovereign V3 Agent Documentation — 2026-10-01

## 1. Executive Summary & Lineage Origin
- **Lineage**: Replicated DECEM Leaderboard Top Strategy grafted onto `lean_wflip_v9_standalone.py`.
- **Target Goal**: Eliminate tie-lock stagnations against `lean_wflip_v9_standalone.py` (which caused score stagnation around ~1700 Elo due to shared family lineage) while systematically outperforming mid-tier benchmark opponents (`cha22_champion.py`, `tetsutani_godview_v2.py`, `pub_2945farm.py`).
- **Status**: Deployed to `submission.py` and verified clean.

---

## 2. Architectural Stack & DECEM Replicated Levers

| Layer | Mechanism / Description | Target Effect |
|---|---|---|
| **Base Chassis** | `lean_wflip_v9_standalone.py` | Standalone high-efficiency production & allocation engine |
| **Early Plot Commit** | `_CXTB_MIN_REVENUE = 7000` | Accelerates 4th quadrant unlock & early TOMATO plot allocation |
| **Phase Desync** | Step 192 & Step 312 forced 1-unit `WHEAT` buy | Forces state/order divergence to prevent 100% step mirroring against same-lineage field opponents |
| **Market Preemption** | `step % 24 == 23` shed >= 4 preemption | Dump high-margin inventory (`TOMATO`, `CARROT`, `MILK`, `WOOL`) 1 turn prior to step % 24 sell window |

---

## 3. Comprehensive 4-Opponent Benchmark Matrix (64 Games per Matchup)

### Matchup 1: vs `lean_wflip_v9_standalone.py` (Codebase Champion / Lineage Baseline)
- **R1 Bank (n=16)**: 8W / 0L / 0T | Mean Delta: +7.2 | **0% Ties**
- **R2 Bank (n=16)**: 8W / 0L / 0T | Mean Delta: +6.9 | **0% Ties**
- **Fresh Bank (n=32)**: 14W / 2L / 0T | Mean Delta: -33.6 | **0% Ties**

### Matchup 2: vs `cha22_champion.py`
- **R1 Bank (n=16)**: 7W / 1L / 0T | Mean Delta: +1563.0
- **R2 Bank (n=16)**: 7W / 1L / 0T | Mean Delta: +756.4
- **Fresh Bank (n=32)**: 9W / 7L / 0T | Mean Delta: +539.5

### Matchup 3: vs `tetsutani_godview_v2.py`
- **R1 Bank (n=16)**: 6W / 2L / 0T | Mean Delta: +902.0
- **R2 Bank (n=16)**: 4W / 4L / 0T | Mean Delta: +313.6
- **Fresh Bank (n=32)**: 9W / 7L / 0T | Mean Delta: +607.8

### Matchup 4: vs `pub_2945farm.py`
- **R1 Bank (n=16)**: 8W / 0L / 0T | Mean Delta: +1952.6
- **R2 Bank (n=16)**: 8W / 0L / 0T | Mean Delta: +1408.7
- **Fresh Bank (n=32)**: 15W / 1L / 0T | Mean Delta: +2310.6

---

## 4. Deployment Record
- **Source File**: `agents/decem_sovereign_v3.py`
- **Target Deployment**: `submission.py`
- **Smoke Verification**: Passed (16/16 turns, 7W/1L/0T +1563.0 mean vs `cha22_champion.py`)
- **Timestamp**: 2026-10-01
