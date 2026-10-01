# Retrieval Hygiene — what to read, in what order

Retrieval priority for this repository. Nothing here deletes evidence; it decides what normal research
reads **first** and what it must not treat as current. Verified by directory listing 2026-09-25 16:55 UTC.

## Tier definitions and current occupants

### PRIORITY 0 — CURRENT (read these first)
| Item | Path | Why current |
|---|---|---|
| Live leaderboard snapshot | `scan_20260925/kaggriculture-publicleaderboard-2026-09-25T16_42_11.csv` (10,011 teams) | downloaded this session, 2026-09-25 16:42 UTC |
| Public-kernel freshness scan | `scan_20260925/kernels_newest.csv`, `kernels_topvoted.csv`, `ladder_r1.txt`, `probe_*.txt` | same scan |
| Screened public candidates | `knowledge/PUBLIC_AGENT_REGISTRY.md` | verdicts + hashes, dated 2026-09-25 |
| Current competitive state | `knowledge/CURRENT_STATE.md` | P0 roll-up |
| Strongest live submission we own | `agents/cha22_byte_identical.py` (sha1 `a8da73093c8e`, 501,543 B) → 2376.2, ref 56539078 | the only submission of ours inside the last 48 h that scored above 1900 |
| Working baseline for gates | `agents/cha22_champion.py` (sha1 `c17f23f64f7c`) = donor + `agent = ig_agent` | every candidate this cycle is measured against it |
| Newest field replay evidence | `WybeV2/datasets/p6_field_20260925/` (being built), then `WybeV2/datasets/e134_live/`, `p2_chase/` | episodes behind today's ranks 1–13 |
| Current ledger | `results/LEDGER_20260925.md` §1–§47 | all cha22-cycle measurements |

### PRIORITY 1 — VERIFIED RESEARCH MEMORY
`knowledge/RESEARCH_MEMORY.md` (reusable engine/competition laws), `knowledge/REJECTED_HYPOTHESES.md`
(closed levers with their construction). Read before designing any experiment. Methodology stays in
`processing.md` (read-only), constraints in `RESEARCH_RULEBOOK.md`, build mechanics in `AGENT_BUILD_GUIDE.md`.

### PRIORITY 2 — ACTIVE EXPERIMENTS
`gates_cha22/` (154 entries, newest `E208_chain.txt`) — the cha22-era gate logs referenced by
`results/LEDGER_20260925.md` §37–§47. `kernels_pulled/scan_20260925/` — this scan's pulls.
`donors_20260925/py/` — the donor sources the cha22 stack was built from.

### PRIORITY 3 — HISTORICAL (cite, do not bench against)
Champion lineages that the live field has passed: `agents/pub_v57_apex_v35_dumporder.py`,
`agents/submission_apex_final.py`, `agents/futurev1_forecast.py`, `agents/pub_apex_v5.py`,
`agents/pub_metav4_r78u.py`, `agents/friend_r78ub.py`, `agents/pub_e94_omw_clean.py`.
**Docs moved 2026-09-28:** the Apex V1/V5/V6/V11/V12/V28/V30 documentation, the V23–V29 V-era studies
(`V11_LIVE_LOSS_*`, `V12_PREEMPT_F90_*`, `V13_*`, `V28_*`, `V29_*`, `T3_HOLDOUT_*`, `ROUTE_HUNT_LEDGER`,
`ZERO_TIE_STRATEGY`, `TAPES_ARE_THE_STRATEGY`, `E102_*`), the friend-era `FRIEND_INSIGHTS_*/FRIEND_SPARRING_POOL_*`,
`FINDINGS_DSM_BATCH`, the dead V44–V47 canvases, and the Sep 4–21 `results/` reports are all under
`archive/stale_20260928/` (58 files, 420,623 B — `MANIFEST.md` inside). Their refuted constructions are restated in
`knowledge/REJECTED_HYPOTHESES.md` **H-061…H-072**, which is what to read instead. Still at the root and still P3:
`FUTUREV1_*`, `E107_*`, `E118/E119_*`, `E130/E131_*`, `E137_*`, `E104_*`, `E206_*`, `TAPEFORGE_PLAN_*`.
Also historical: `results/LEDGER_20260919…26.md` (20/21 moved to archive), `results/P*`, `results/E1xx_*`.
Useful for *mechanism* history; never as the bar for promotion.

### PRIORITY 4 — ARCHIVE (exclude from normal retrieval)
`archive/` (30 entries, 69 MB, newest `sweep_rejected_20260925/`), `reference_bundle_20260920/` (4.9 MB),
`scratch/` (12 KB, throwaway probes incl. this session's `p8_*`/`p9_*` decoders), single-purpose gate dirs from
closed studies: `gates_futurev1/` (97 entries, **146 MB**), `gates_p5/`, `gates_lineage/` (36 KB),
`gates_contestplant/`, `gates_fertscope/`, `gates_horizonb/` (20 KB), `gates_sweepalloc/`.
Whole-tree sizes for scale (2026-09-25): `WybeV2/` 3.0 GB (of which the datasets under `WybeV2/datasets/`
are the replay evidence), `results/` 1.9 GB, `agents/` 397 MB, `kernels_pulled/` 116 MB,
`gates_futurev1/` 146 MB, `gates_cha22/` 26 MB, `Prediction/` 16 MB, `donors_20260925/` 11 MB.

## Rules

1. **Never infer currency from a filename.** `*champion*`, `*top*`, `*best*`, `*winner*`, `submission.py`
   are not evidence of promotion. Require (a) a hash present in `knowledge/CURRENT_STATE.md`, or
   (b) a live leaderboard/kernel row with a date inside the last 48 h.
2. **A champion is CURRENT only while recent evidence supports it.** Today's example: the memory entry
   "cha22 on top" was still true for the *parent* (2376.2, rank 674) while the deployed *child*
   `cha22_e206_mw_h1q6.py` scored 1400.4 — so "champion" now names a file, not a result. Re-read
   `knowledge/CURRENT_STATE.md` rather than trusting `project-champion-hierarchy-*` notes.
3. **Older than ~2 weeks is not a benchmark.** Purged once already (2026-09-21); do not re-introduce stale
   opponents into gates. GitHub is the backup.
4. **Regenerate, don't accumulate.** Candidate files in `agents/` must be reproducible from a
   `tools/build_*.py` script; sweep copies that gate at or below their parent get deleted, keeping builders
   and one log per decision.
5. **Duplicate-artifact census (for §16 cleanup, no deletions done yet).** Names worth collapsing:
   8 separate `gates_*` directories from closed single-question studies; `submission.py` (1,094,498 B,
   FutureV1, live 1917.8) which is *not* our best live file; `main.py` (1,026,965 B) an unrelated
   earlier single-file build; `agents/cha22_byte_identical.py` vs `agents/cha22_champion.py` (18 B apart,
   the only difference being the entry binding); `kernels_pulled/` holding two size classes of the same
   restored agents (wrapper `.py` + decoded `__BLOB.py`).
   Moving P4 material into `archive/<date>/` is a separate, explicitly-approved step: research correctness first.
