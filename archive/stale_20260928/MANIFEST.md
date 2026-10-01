# Stale-doc quarantine — 2026-09-28 (executed 22:25–22:35 IST)

58 markdown reports from superseded agent lineages moved out of the working tree into this directory.
Nothing was deleted; nothing was rewritten in place except the pointers listed under "Pointer fixes".
`_inventory.txt` here carries sha1 (12) + bytes + original path for all 58; `_filelist.txt` is the exact move set.

Why mtime is not evidence: every root `.md` reads `Sep 27 20:58` (bulk touch by a concurrent process), so
classification used filename date + `git ls-files` + inbound-reference count from live docs.

## What moved, by family

| family | files | bytes | examples |
|---|---|---|---|
| Apex V1–V30 architecture docs | 12 | 60,172 | `APEX_V1/V5/V6/V11/V12/V28/V30_AGENT_DOCUMENTATION`, `VERIFY_V35_APEX_V12`, `V6_V5_SUPERIORITY_H2H`, `V57_FUNDING_H2H`, `FRIEND_INSIGHTS_20260921`, `FRIEND_SPARRING_POOL_20260921` |
| dead canvases / plans / guides | 9 | 51,169 | V44 phase planner, V45 adaptive fert, V47 shadow price, `PLAN_3000_spine_extraction`, `DECISIVE_MECHANISMS_SURVEY`, `COMPETITIVE_ENGINEERING_MASTER_GUIDE`, `FINDINGS_DSM_BATCH`, `HANDOFF.md` |
| refuted-axis records (Tier E) | 15 | 137,537 | `V12_PREEMPT_F90_*`, `V13_PRODUCTION_GATE`, `T3_HOLDOUT_F90_VS_V11`, `V28_*`, `V29_FERT_SUPPLY_CHAIN`, `ROUTE_HUNT_LEDGER`, `E102_PREEMPT_RETUNE`, `ZERO_TIE_STRATEGY`, `TAPES_ARE_THE_STRATEGY`, `V11_LIVE_LOSS_*`, `LOOP_STATUS_V27_V29`, `RESEARCH_PLAYBOOK_V23_TO_V26` |
| Sep 4–21 `results/` reports | 18 | 146,216 | `V28_FINDINGS_20260904`, `V34/V35*_CANVAS/V35_V36_LEDGER`, `FINDINGS_20260911`, `completion_audit_20260904`, `ENGINE_1327_FINDING`, `KERNEL_SWEEP_20260919`, `LIVE_FORENSICS_20260919/20B`, `WORLDPANEL_0920`, `ED_LEDGER_0920`, `DUMPER_REPRO_0920`, `WORLD_TAGGING_0920`, `LEDGER_20260920`, `HANDOFF_20260921_TOM20`, `E89_price_oracle_brief`, `bench_public_base_20260924_smoke` |
| byte-identical duplicates | 2 | 11,726 | `reference_bundle_20260920/results/KERNEL_SWEEP_20260919.md`, `…/V35_V36_LEDGER_20260911.md` (md5 matched the `results/` copies) |
| Aug-era `docs/` | 2 | 13,803 | `FINDINGS_2026-08-08.md` (V23 vs rank-1 "R1"), `YUMMERS_CHECKPOINT_2026-08-07.md` |
| **total** | **58** | **420,623** | |

`reference_bundle_20260920/results/LEDGER_20260919.md` and `…/LEDGER_20260920.md` were **not** treated as
duplicates — their md5s differ from the `results/` copies, so both stayed where they were.
`results/PIXELX_LINEAGE_20260927.md` stayed: `pixelx_v2` is an E224 arm.

## Evidence preserved first (Rule 3)

The Tier E constructions existed **nowhere else** — `knowledge/REJECTED_HYPOTHESES.md` had 0 hits for
`f90`, `labor`, `V28`, `V29`, `route-hunt`, `E102`, `shadow-price`, `sweepalloc`. They are restated as
**H-061 … H-072** in that file (addendum "apex/V-era axis records", 2026-09-28), each with construction,
gate numbers, rejection reason and reopen condition, so a retry can differ materially without opening
these files.

## Git

No git command wrote anything. Five moved paths are tracked and therefore now read as deleted-but-tracked,
joining the 275 already in that state: `HANDOFF.md`, `E102_PREEMPT_RETUNE_DOCUMENTATION_20260922.md`,
`RESEARCH_PLAYBOOK_V23_TO_V26.md`, `docs/FINDINGS_2026-08-08.md`, `docs/YUMMERS_CHECKPOINT_2026-08-07.md`.
Recover any of them with `git checkout -- <path>`; the rest are untracked and recoverable only from here.

## Pointer fixes made

- `AGENTS.md` — Rule 0 (doc list + quarantine clause), Rule 1 phase 1 (lever ledger is now
  `knowledge/REJECTED_HYPOTHESES.md`), phase 3 (apex fert read marked superseded by H-063), phase 4
  ("keep the metav4 spine, fix the market interaction layer" retired; baseline of record
  `agents/cha22_champion.py` + an absolute-field estimator), Rule 1b, Rule 2 (durable laws kept, the
  `step%24==23` / floors 75-20-80 / 90-30-140 / 716-719 doses demoted to historical and marked
  do-not-copy), Rule 3 (mechanisms go to the ledger, not to a new root `.md`), phase 7 (one doc per
  deployed lineage; a lineage's doc moves to `archive/stale_<date>/` the day it stops being the bar).
- `knowledge/RETRIEVAL_PRIORITY.md` — P3 now names this directory and H-061…H-072.
- `knowledge/REJECTED_HYPOTHESES.md` — provenance line for `FINDINGS_DSM_BATCH.md` repointed here.

## Known dangling references, not corrected

- `processing.md` cites `APEX_V5_AGENT_DOCUMENTATION_20260921.md`, `FRIEND_INSIGHTS_20260921.md` and the
  apex-era fleet as current. Read-only under Rule 1b, so left alone; `AGENTS.md` Rule 1b now says
  `knowledge/CURRENT_STATE.md` wins wherever the two disagree.
- `tools/world_panel.py:3` and `tools/build_metav4_ed.py:5` name moved reports in their docstrings
  ("read X first"). Comment text only — no runtime path, no breakage.
- Historical citations inside `results/public_base_20260924_loss_analysis/REPORT.md`,
  `results/LEDGER_20260919/21.md`, `results/E96/e96_brief.md`, `research/TEAM_RESEARCH.md`,
  `Prediction.Prediction Agents/gates/CHASSIS_RANKING.md` and
  `Prediction.Prediction Agents/findings/CORRECTION_fert_window_invalid_20260926.md` now resolve to this
  directory. Not rewritten — they are another session's records.

## Deliberately retained at the root

`processing.md`, `AGENTS.md`, `Kaggriculture.md` (§24–27 live laws), `RESEARCH_RULEBOOK.md`,
`AGENT_BUILD_GUIDE.md`, `README.md`, `knowledge/*`, `HANDOFF_QODER_20260926.md` (cited by
`MMPQ_GODVIEW_20260928/`), the cha22/futurev1-era records `E104_*`, `E107_*`, `E118_*`, `E119_*`,
`E130/E131_*`, `E137_*`, `E206_*`, `FUTUREV1_*`, `TAPEFORGE_PLAN_*`, and — borderline, left pending your
call — the Sep-24 phase reports `P2_INGESTION_REPORT_*`, `P3_STRATEGY_DNA_*`, `P4_ELIMINATION_MATRIX_*`
(pre-cha22 cycle, 0 inbound references).
