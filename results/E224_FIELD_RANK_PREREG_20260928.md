# E224 — absolute-field rank of the four candidate files (PRE-REGISTRATION, written before any E224 data)

Date: 2026-09-28. Operator directive in force: build/validate the next submission and submit once
validation is done. One submission authorized ("SUBMIT ONCE UR DONE").

## Question

Which of the four held files is strongest under the **absolute-field** estimator (rulebook §24/§27-V4),
and therefore which single file should occupy the next finals-relevant submission slot?

The two currently-active submissions are `sluice_v8_counterd` (2203.2 live) and `sluice_v8c_blockperm`
(2054.7 live, = current `submission.py`, sha 17a8db) — both field-measured weak (−52/seed class).
`sluice_topup7` (2353.1 live) is third-latest and therefore inactive. The finals re-play the latest two
submissions fresh (Kaggriculture.md §5/§13), so the slot decision is an absolute-strength decision, not
a live-rating decision.

## Arms (sha1, bytes)

| arm | file | note |
|---|---|---|
| A | `agents/sluice_topup7.py` 057c4038, 506,419 B | champion of record (user-stated "SLUICETOPUPV7"), live 2353.1 |
| B | `agents/cha22_champion.py` ee3ebfa9, 501,563 B | A's parent minus the shed top-up layer; +659.8/seat over A on 48 unseen worlds (SUMMIT confirmation panel) |
| C | `agents/cha22_e199_lo96q8.py` ec0f0edc, 508,860 B | B-family + q8 preempt; field win-rate 93.8%/87.5% in EXP-OC-031; "candidate of record" per 2026-09-26 memory |
| D | `agents/pixelx_v2.py` b47af1bd, 515,948 B | newest build (2026-09-27); beat A on mirror banks (r1 8W/0L, r2 7W/1L, fresh 14W/2L) which per rulebook §24 measures symmetry-breaking only; **field estimator never applied to it** |

## Design

- Engine pin `kaggle-environments==1.32.7`, `episodeSteps=720`, `townCenterSellInterval=24`, `debug=False`,
  seed in `configuration`. Asserted inside the tool (`engine_pin_error()`).
- Opponents (5 of the rulebook §27-V4 six; the 30-game compute cap of the operating protocol forces
  5×3×2 instead of 6×8×2): `pub_dynroute85`, `pub_e69_soilrouter`, `salemali7_3094`,
  `pub_farmer_john_v56`, `friend_r78ub` — all unrelated lineages to every arm.
- Seeds: `15243000 + 1117*i`, i=0..2 (registry E224; repo-wide grep = 0 prior uses; unseen by all arms).
- Per arm: 5 opponents × 3 seeds × both seat orders = **30 games** (protocol §4). Seat-collapsed to
  15 distinct `(opp,seed)` worlds; between-arm comparison is **paired** on identical `(opp,seed,swap)` rows.
- Metric: final bank (`reward` at step 719) and the population features (tiles, tomato, carrot, wheat,
  strawberry, peak crew, hires) per seat.

## Pre-registered decision rule (fixed before reading any E224 result)

For each arm X ∈ {B, C, D}, compute the paired per-world bank delta `X − A` on the 15 shared worlds
(and B vs C, B vs D, C vs D secondarily).

**Submission winner** = the arm with the **highest mean paired delta vs A** subject to ALL of:
1. mean paired delta vs A > 0;
2. favourable on ≥ 9 of 15 worlds (sign test one-sided p ≤ 0.015 at 9/15);
3. no opponent lineage has mean paired delta < −1,000;
4. worst single world ≥ −2,500.

If no arm qualifies, **A stays champion and A is the submission** (re-submitting the strongest
confirmed file into the active-pair window; still strictly better than the v8_counterd/v8c_blockperm
pair now active, per SUMMIT + EXP-OC-031 field evidence).

If C or B wins: submission = winner. If D wins: submission = D, plus a confirmation pass on a second
fresh 30-game set before the submit (protocol §9: one 30-game set does not establish superiority).

Ties (mean delta within ±100 and overlapping per-world signs): prefer the arm with the higher absolute
mean bank; if still tied, prefer A (no change without evidence).

## Estimator disclosure (rulebook §24 mandatory format, per arm, filled by the tool log)

`ESTIMATOR: absolute-field · OPPONENTS: 5 unrelated lineages (no shared spine with any arm) ·
SEEDS: 15243000, 15244117, 15245234 (unseen by all arms) · WORST WORLD: <filled from data>`

## After the gate

- Fill the results into `E224_FIELD_RANK_20260928.md` (loss-first, per-seed deltas, W/L per bank).
- Copy the winner over `submission.py` (sha-verified against the arm file), submit ONCE via
  `kaggle competitions submit -c kaggriculture`, record submission id + timestamp in the report and
  memory. Note for the operator: one submission leaves `v8_counterd` in the other active slot; a second
  submission (their call) would displace it.
