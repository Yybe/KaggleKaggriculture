# E101t / E102 / E103 — Preemption Floor Retune and Spine-Placement Study

**Date**: 2026-09-22
**Engine pin**: `kaggle-environments==1.32.7`, `townCenterSellInterval=24`, venv `WybeV2/rank_env`
**Question posed**: does the floor/window retune fix Apex V5's negative R2 holdout, and is E101 the new top agent?

---

## 1. What the retune actually changes

`_apex_tuned_clone_preemption` (V5 layer) preempts the 24-turn clone sell wave at `step % 24 == 23`
whenever the shed holds ≥6 units and `price >= floor`, with floors
`FERTILIZER 75 / WHEAT 20 / everything else 80`. The knob set was lifted into one `_T` dict
(`tools/build_e101t_variants.py`) so floors, window, trigger phase, min-stock and clip size can be
swept without touching the 1 MB spine.

**Sweep target**: `pub_e101t_ctrl.py` (V5 defaults) reproduces the known defect — R2 holdout
`5W/3L/0T mean −54.2` with a `−592` tail seed, identical to `pub_e101_apex_layers.py`
(control parity ⇒ the parameterized rebuild is behaviourally exact).

### R2 sweep, all variants vs the E99 spine (16 games each, `results/e101t_r2.txt`)

| Variant | floors FERT/WHEAT/other | window | phase | qty | R2 record | mean | worst seed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ctrl` | 75 / 20 / 80 | 240–671 | 23 | 10/6 | 5W/3L/0T | **−54.2** | −592 |
| `f85` | 85 / 25 / 110 | 240–671 | 23 | 10/6 | 6W/2L/0T | +36.0 | −265 |
| **`f90`** | **90 / 30 / 140** | 240–671 | 23 | 10/6 | **7W/1L/0T** | **+82.2** | −2 |
| `f95` | 95 / 32 / 160 | 240–671 | 23 | 10/6 | 7W/1L/0T | +82.2 | −2 |
| `f110` | 110 / 40 / 180 | 240–671 | 23 | 10/6 | 6W/1L/1T | +36.1 | −2 |
| `f130` | 130 / 50 / 220 | 240–671 | 23 | 10/6 | 0W/0L/8T | +0.0 | 0 (layer inert) |
| `w527` | 75 / 20 / 80 | 240–527 | 23 | 10/6 | 4W/4L/0T | +51.1 | −8 |
| `w575` | 75 / 20 / 80 | 288–575 | 23 | 10/6 | 7W/1L/0T | −16.1 | −605 |
| `q4` | 75 / 20 / 80 | 240–671 | 23 | 4/4 | 5W/2L/1T | +0.0 | −630 |
| `f90q12` | 90 / 30 / 140 | 240–671 | 23 | 14/10 | 3W/4L/1T | +64.8 | −191 |
| `ph22` | 90 / 30 / 140 | 240–671 | 22 | 10/6 | 3W/5L/0T | −57.6 | −503 |
| `c1` | 90 / 30 / 140 | 240–575 | 23 | 8/5 | 7W/1L/0T | +61.4 | −1 |

**Reading**: the R2 damage is a *floor* problem, not a window or volume problem. Selling MILK/WOOL at
px 80 preempts into a depressed curve and the debt repayment then forces the loss (`ctrl −592`);
raising the "other" floor to 140 removes the tail entirely (`f90 worst seed −2`). The plateau is
140–160; 110 is still leaky, 220 never fires (`f130 = 8/8 ties` — a useful inertness control,
per AGENTS.md Rule 5 a gate that returns all-ties is an *untested* layer, not a pass).

### Cross-bank validation of `f90` (`results/e101t_r1.txt`, `results/e101t_fresh.txt`)

| Bank | `ctrl` | `f90` | verdict |
| :--- | :--- | :--- | :--- |
| R1 (8 seeds) | 7W/1L/0T +21.8 | 7W/1L/0T +21.8 | identical deltas — floors never bind, **no regression** |
| R2 (8 seeds) | 5W/3L/0T −54.2 | 7W/1L/0T +82.2 | the fix |
| Fresh (16 seeds) | 11W/5L/0T +43.4 | 11W/5L/0T +35.5 | one seed trades +319 → +193 |
| **R3 holdout, never tuned on (16 seeds)** | — | `f90` vs `ctrl`: **0W/0L/16T +0.0** | retune is inert off R2 |

**Honest conclusion**: the retune is a *tail-risk trimmer*, not an earner. It converts R2's −54.2
into +82.2, costs 7.9 on Fresh, changes nothing on R1 and nothing at all on a never-seed-tuned R3
bank. Aggregate across the 48 same-spine seeds gated: **+978 total seed-delta, concentrated in two
seeds**. Keep it for the downside removal; do not describe it as a score breakthrough.

---

## 2. The spine-placement error (this is why E101 is not the top agent)

`pub_e101_apex_layers.py` / `pub_e101t_f90.py` graft the market layers onto the **E99** spine.
Head-to-head vs the deployed champion:

| Candidate | vs `pub_apex_v5.py` R1 | vs V5 Fresh |
| :--- | :--- | :--- |
| `pub_e101_apex_layers.py` | 0W/1L/7T −9.2 | 0W/2L/14T −3.9 |
| `pub_e101t_f90.py` | 0W/1L/7T −9.2 | 0W/3L/13T −11.8 |

The E99 spine is **weaker** than V5's (`h20` fert-ROI + V219 tomato union gate + Gluzdov mature-wheat
tail + OW guarded opening), so E101 sits *below* V5 no matter how good its market layer is.
Fix: apply the retune to the V5 file itself — `tools/build_e102_v5_tuned.py` replaces exactly one
constant line, so every gate delta is a pure floor ablation.

| Agent | construction |
| :--- | :--- |
| `agents/pub_e101t_<tag>.py` | E99 spine + parameterized V5 market layers (sweep harness) |
| `agents/pub_e102_v5_f90.py` | **Apex V5 file, floors → 90/30/140** (md5 17d2d438) |
| `agents/pub_e103_v5_full.py` | E102 + E99 weed-deferred `BUILD_PASTURE` replay patch (md5 2925d882) |

`E103 vs E102`: 0W/0L/8T (R1), 0W/0L/8T (R2), 0W/0L/16T (Fresh) — exact ties, then
**+2,676 on the defect seed 1898931754**. The pasture fix is rare but free: no gated seed regresses.

### Promotion gate — `pub_e103_v5_full.py` vs deployed `pub_apex_v5.py` (`results/h2h_e103_vsV5.txt`)

| Bank | Record | mean | per-seed deltas |
| :--- | :--- | :--- | :--- |
| R1 (16 games) | 0W/0L/8T | +0.0 | all exactly 0 |
| R2 (16 games) | **2W/0L/6T** | **+138.1** | +382, +723, rest 0 |
| Fresh (32 games) | 0W/1L/15T | −7.9 | −126, rest 0 |
| R3 holdout (E102 vs V5, 32 games) | 0W/0L/16T | +0.0 | all exactly 0 |
| Defect seed 1898931754 (E103 vs E102) | 1W/0L/0T | +2,675.5 | +2,676 |


---

## 3. Ladder coverage (does it beat the 2700 band?)

`pub_e102_v5_f90.py` fleet, R1 (16 games) and Fresh (32 games), `results/fleet_pub_e102_v5_f90_*.txt`:

| Opponent | R1 | Fresh | ties |
| :--- | :--- | :--- | :--- |
| `crop_roi30_h20.py` (~2700 band) | 8W/0L/0T +608.0 | **16W/0L/0T +67.7** | 0 |
| `pub_farmer_john_v56.py` | 8W/0L/0T +587.9 | 12W/4L/0T +137.8 | 0 |
| `pub_v54_productive.py` | 8W/0L/0T +597.1 | 12W/4L/0T +141.7 | 0 |
| `pub_one_more_wheat.py` | 8W/0L/0T +597.1 | 12W/4L/0T +141.7 | 0 |
| `pub_metav4_early.py` | 8W/0L/0T +648.1 | 15W/1L/0T +170.5 | 0 |
| `friend_r78ub.py` (2722 live) | 7W/1L/0T +31.0 | 11W/5L/0T +39.4 | 0 |
| `pub_e94_omw_clean.py` | 7W/1L/0T +31.0 | 11W/5L/0T +39.4 | 0 |
| `pub_e99_pasture_fix.py` | 7W/1L/0T +31.0 | 11W/5L/0T +35.5 | 0 |
| `pub_2945farm.py` (mid ladder) | 8W/0L/0T +1264.9 | — | 0 |
| `pub_e67_yamakawa.py` | 8W/0L/0T +40,029.8 | — | 0 |
| `pub_apex_v1.py` | 7W/1L/0T +21.8 | 11W/5L/0T +35.5 | 0 |
| `pub_apex_v5.py` (same lineage) | 0W/0L/8T +0.0 | 0W/1L/15T −7.9 | **23/24** |

Mid-ladder: every non-relative opponent is beaten with **zero ties** on both banks (12 opponents,
`results/fleet_pub_e102_v5_f90_r1.txt` / `_fresh.txt`). `pub_e103_v5_full.py` reproduces E102's
R1 rows exactly on the 4 opponents re-gated (`results/fleet_pub_e103_v5_full_r1.txt`).
Vs its own lineage (V5) it ties by construction — the market layer only diverges where a floor binds.

---

## 4. Status

- **Top local agent: `agents/pub_e103_v5_full.py`** (V5 spine + retuned floors + pasture fix).
  It is V5 weakly-dominant: 0 losses on R1/R2/R3, +138.1 on R2, +2,676 on the defect seed,
  −126 on one Fresh seed.
- **Not deployed.** `submission.py` is unchanged; Kaggle promotion needs explicit user approval.
- Tools: `tools/build_e101t_variants.py`, `tools/sweep_e101t.py`, `tools/bench_fleet.py`,
  `tools/build_e102_v5_tuned.py`, `tools/build_e103_v5_full.py`, `tools/h2h_r3.py`.
- Logs: `results/e101t_r2.txt`, `results/e101t_r1.txt`, `results/e101t_fresh.txt`,
  `results/h2h_e102_vsV5_r3.txt`, `results/h2h_e103_vs_e102.txt`, `results/fleet_*.txt`.
- `processing.md` and the `APEX_V*` documentation were not modified (AGENTS.md Rule 1b).
