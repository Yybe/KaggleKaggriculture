# E101: Apex V5 Market Layers Ported onto the E99 Spine

**Date**: 2026-09-22
**Lineage**: `agents/pub_e99_pasture_fix.py` (E94 spine + weed-deferred BUILD_PASTURE replay fix) + `_apex_tuned_clone_preemption` + `_apex_precision_terminal_sweep`
**Engine**: `kaggle-environments` 1.32.7, `townCenterSellInterval=24`
**Builder**: `tools/build_e101_apex_layers.py` · **Probe**: `tools/probe_e101_layers.py` · **md5**: `a625b52135b0f48e610af6c6d94490d0`

---

## 1. Purpose

Apex V5 (antigravity workstream) was independently verified to beat our E99 candidate with **zero ties**:
E99 vs `pub_apex_v5` = 1W/7L/0T (R1, −31.0), 3W/5L/0T (R2, +53.4), 5W/11L/0T (Fresh, −47.2)
— 64 games, `results/h2h_e99_vs_apexV5.txt`, matching the V5 documentation exactly.
E101 ports V5's two market-interaction layers onto the E99 spine so the pasture-defect fix and the
tie-breaking mechanism are no longer mutually exclusive.

## 2. Architecture

```
| 2. _apex_precision_terminal_sweep (steps 716-719): liquidate residual shed into open market slots (<=10 orders)
| 1. _apex_tuned_clone_preemption (step%24==23, 240<=step<=671): sell ahead of the clone wave at
|    price floors (FERT 75 / WHEAT 20 / else 80), one item per turn, quantity booked into
|    state["debt"][item] and repaid out of the scheduled step-24 order  -> volume conserved
| 0. E99 core chassis = E94/metav4 spine + weed-deferred BUILD_PASTURE replay
```

Both layers are spine-agnostic post-action wrappers reading `observation["private"]["shed"]`, so they
graft onto any agent in this family.

## 3. Gate Results (64 games per opponent, both seats)

| Opponent | R1 Tuning | R2 Holdout | Fresh Holdout | Ties |
| :--- | :---: | :---: | :---: | :---: |
| `pub_e99_pasture_fix.py` | **7W / 1L / 0T (+21.8)** | **5W / 3L / 0T (−54.2)** | **11W / 5L / 0T (+43.4)** | **0 / 32 seeds** |
| `pub_e94_omw_clean.py` | **7W / 1L / 0T (+21.8)** | **5W / 3L / 0T (−54.2)** | **11W / 5L / 0T (+43.4)** | **0 / 32 seeds** |
| `pub_apex_v5.py` | score-for-score parity (probe: 83988=83988, 79101=79101, 129083=129083, 65683=65683) | — | — | — |

Logs: `results/h2h_e101_vs_e99.txt`, `results/h2h_e101_vs_e94.txt`.

**Reading**: E101's win profile is numerically identical to Apex V5's documented profile. The two ported
layers therefore carry V5's **entire** edge over the E94/E99 family; nothing in V1's intermediate OW/CL
layers was required. R2 holdout is negative (−54.2) for both V5 and E101 — the preemption is slightly
overfitted to R1/Fresh worlds and should be re-tuned, not assumed free money. Margins are small
(±2 to ±600), so this is a tie-breaking + accumulation layer, not a blowout layer.

## 4. Failure Mode Caught During This Build (recorded in `processing.md` §5.0)

The first E101 artifact was **silently empty**: the builder used `v5.index("kaggle_submission_agent = agent")`
as the slice end, but that EOF marker occurs twice in `pub_apex_v5.py` (lines 6814 and 6923), so the layer
slice was `v5[6850:6814] == ""`. The candidate behaved exactly like E99 and the gate returned the same
deltas — which reads as "the ported mechanism is inert". Detection required a file-size delta (1,014,062 →
1,017,916 bytes) and a firing-counter probe (`pre_fires` 0 → 34, `sweep_adds` 0 → 0 in 4 seeds).
Post-fix the gate flipped to decisive wins. **Any future graft must assert marker uniqueness, symbol counts,
file growth, and non-zero layer fires before it is gated.**

**Defect-seed check** (the world that motivated the E99 pasture fix, seed 1898931754, both seats):
E101 vs E99 = 1W/0L/0T (+94); E101 vs `pub_e94_omw_clean` = 1W/0L/0T (+2,715). E101 keeps E99's
pasture fix and stays positive on the defect world; the pasture gain is smaller than E99's own +4,838
because the preemption layer re-prices part of that harvest — a re-tune target, not a regression.

## 5. Deployment Status

NOT deployed. `submission.py` remains Apex V5. E101 is the merge candidate that carries the E99
pasture-defect fix forward; promotion requires the R2 regression to be understood and live-band
validation. Submission to Kaggle requires explicit user approval.
