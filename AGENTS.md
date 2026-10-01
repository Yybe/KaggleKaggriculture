# Agent Operating Manual — Kaggriculture Competitive Engineering

**Source of truth**: [`processing.md`](processing.md) (7-phase workflow) + [`knowledge/CURRENT_STATE.md`](knowledge/CURRENT_STATE.md)
(what is actually deployed and measured now) + [`Kaggriculture.md`](Kaggriculture.md) §24–27 (validation law) +
[`kaggriculture_compressed_replay_retrieval.ipynb`](kaggriculture_compressed_replay_retrieval.ipynb).
This file is the mandatory pre-flight. Read it before reading memory, before planning, before writing an agent.

## Rule 0 — Read the directory before you reason about it

Every session, before any analysis or code: run `ls *.md` and open the docs that exist at the root
(`processing.md`, `Kaggriculture.md`, `RESEARCH_RULEBOOK.md`, `AGENT_BUILD_GUIDE.md`) plus
`knowledge/CURRENT_STATE.md`, `knowledge/RETRIEVAL_PRIORITY.md`, `knowledge/REJECTED_HYPOTHESES.md` and
the newest `results/LEDGER_*.md` / `results/E2*_*.md`. Memory notes are an *index*, the directory is the
*evidence*. Claiming an axis is "closed" without re-reading the current docs and tools is a prohibited
failure mode.

**Superseded-lineage quarantine.** `archive/stale_20260928/` holds 58 docs from the Apex V1/V5/V6/V11/V12/
V28/V30, metav4/r78u, friend-r78ub, V23–V29 and Sep-4→Sep-21 report eras. They describe spines we no
longer run and their numbers are not a bar for anything. Do not open them for strategy ideas, doses,
floors or "winning edges" — read one only to recover a construction, and quote it as historical.
`archive/stale_20260928/MANIFEST.md` lists what moved and why. Their refuted mechanisms are restated with
their constructions in `knowledge/REJECTED_HYPOTHESES.md` H-061…H-072.

## Rule 1 — The 7-phase workflow (execute in order, don't improvise a phase)

1. **Prompt ingestion → 3 hypotheses**: chassis limit vs. *interaction* limit; state-query bugs (`observation["private"]["shed"]`,
   never `farm["inventory"]`); dead vs active levers (check `knowledge/REJECTED_HYPOTHESES.md`, H-001…H-072, first —
   never the archived apex/friend-era docs).
2. **Replay ingestion**: Parquet pipeline, never loose JSON. `tools/fetch_episodes.py` / `tools/batch_fetch_replays.py`
   → `WybeV2/datasets/e98f_top10/episodes.parquet` → `WybeV2/datasets/e98f_epidx/manifest.csv`
   → `tools/extract_live_opponents.py` for base85+zlib action tapes (`agents/live_replay/`).
   Header scan reads only the first 64 KiB per replay; shards are `zstd` level 10.
3. **Forensics / strategy DNA**: `tools/atlas_0921.py`, `tools/atlas_agg_0921.py`, `tools/live_loss_anatomy_0920b.py`.
   Metrics: labor curve, quad unlock timing, fert/water counts, `everplant` crop matrix, revenue split, market order
   timing. (The apex-era "champions 135–249 fert vs our 85–110" read is superseded: H-063 measured 114 applied against
   456 supplied on a provably slack cap — the fert gap is logistics, not turn count.)
4. **Base-lineage elimination before modification**: `WybeV2/rank_env/Scripts/python.exe tools/fast_matrix_eval.py`.
   Baseline of record is `agents/cha22_champion.py`; measure a candidate against it *and* against an absolute-field
   estimator (`results/E224_FIELD_RANK_20260928.md`), because a candidate that ties or beats only its own lineage has
   not been tested. The old "keep the metav4 spine, fix the market interaction layer" decision law is RETIRED — that
   spine class and its market overlays are H-061…H-072 territory and `knowledge/CURRENT_STATE.md` classes them as
   mechanism history, not a bar.
5. **Modular onion layers**: build via append-only `tools/build_*.py` scripts that concatenate base + wrapper
   (`_N_PARENT = agent; del agent; def agent(...)`), never by hand-editing the 1 MB spine. Each layer = one mechanism.
   **Every graft must be proven live before it is gated** — a silently-inert graft gates as a clean tie and reads as
   "zero regression": (a) assert the anchor/marker counts in both source and output (`assert out.count(sym) == 2`),
   (b) assert slice bounds (`rindex` vs `index` — duplicated EOF markers produce an empty layer),
   (c) `import` the output and assert the layer symbols exist on the module, (d) run a firing-counter probe
   (`tools/probe_e101_layers.py` pattern) over 2–4 seeds and require non-zero fires, plus a byte-size delta vs the base,
   (e) **prove the layer changes the emitted ACTION, not that it ran**: replay one real observation stream
   through the graft and its parent and require non-zero divergences (pattern:
   `OZER_V57_20260930/probe_v57.py`; use the engine's recorded actions as a replay-fidelity control, and note
   `steps[t+1].action` is the action for `steps[t].observation`, not `steps[t]`). A high internal counter is
   not proof — V57 reported `blocked=3,022` on one world with 0/719 action divergences (H-088).
   **Pulled kernels bind wrong.** `tools/agent_loader.load_agent` resolves by name preference (`agent`
   first); Kaggle runs the last top-level def / `kaggle_submission_agent`. If a pulled file assigns
   `agent = <parent>` before defining its EOF layer, our gates measure the **parent** while the platform runs
   the child — so for every pulled file assert `load_agent(path).__name__` equals the def the platform would
   execute, and gate an explicitly entry-patched copy when it does not.
6. **3-tier deterministic gate** on pinned `kaggle-environments==1.32.7`, `townCenterSellInterval=24`:
   R1 (8 seeds), R2 holdout (8 seeds), Fresh holdout (16 seeds), both seats per seed —
   `tools/test_candidate_breakthrough.py` / `tools/run_h2h.py CAND OBS [r1|r2|fresh|all]`.
   Assert the engine version inside every gate log.
7. **Deploy + document**: single-file `submission.py`, mirror to `agents/`, write `*_AGENT_DOCUMENTATION_YYYYMMDD.md`
   (lineage, architecture stack table, benchmark matrix, deployment record).
   **One such doc per deployed lineage, not per experiment** — per-experiment findings go in the ledger
   (`results/LEDGER_*.md`, `knowledge/REJECTED_HYPOTHESES.md`). The day a lineage stops being the bar, its doc moves to
   `archive/stale_<YYYYMMDD>/` and its refuted mechanisms are restated in `knowledge/REJECTED_HYPOTHESES.md`. Root-level
   proliferation is what forced the 2026-09-28 quarantine of 58 docs.

## Rule 1b — Antigravity docs are READ-ONLY

`processing.md` and the `docs/`-era references inside it are reference material to follow, not to edit. Never append to
or restructure them — my rules go here (`AGENTS.md`) and my findings go in a new file named after my own artifact.
Before touching a file I did not create this session, check `git log --oneline -- <file>`; untracked or
antigravity-authored means hands off. Note: `processing.md` still cites `APEX_V5_AGENT_DOCUMENTATION_20260921.md`,
`FRIEND_INSIGHTS_20260921.md` and the apex-era fleet as if they were current; those paths are now under
`archive/stale_20260928/` and `processing.md` is not mine to correct — `knowledge/CURRENT_STATE.md` is the authority
wherever the two disagree.

## Rule 2 — Tie-breaking law (the actual ceiling)

Identical-spine agents share steps 0–84, land expansion and sell schedules → **seed-level ties are a defect, not a result**.
A gate that returns ties is an *untested* candidate, not a validated one. The durable part of this law, still true on the
cha22 spine:
- Symmetry has to be broken somewhere the opponent can see it, and a sell-side break must **conserve total volume**.
  Re-timing with a per-item debt ledger can pay; withholding supply does not — the units you skip raise the *shared*
  curve your opponent sells into (H-067, v18_clip −106,821).
- An overlay that does not fire gates as a clean tie. Prove fires with a counter before gating (Rule 1 phase 5).
- Ceiling on market/sell overlays is **±0.35…0.6%** of score, measured twice (H-071). Anything promising more has to
  change production on every seed, not the sell schedule.

The apex-era constructions themselves — `_apex_tuned_clone_preemption` (`step % 24 == 23`, window 240–671, floors
75/20/80 and 90/30/140, one item per turn) and `_apex_precision_terminal_sweep` (steps 716–719) — are **spine-specific
historical doses**, fully documented in H-061…H-072 with their gate results (f90: 15W/15L/2T, p = 1.0000 on a 32-seed
holdout). Do not copy a floor, window or dose from them onto `agents/cha22_champion.py`; if a preempt variant is needed,
write a new pre-registered rule and tune it on the current spine.
- Never re-run base scans: the public pool is spine clones only (`knowledge/PUBLIC_AGENT_REGISTRY.md`, base-monoculture finding).

## Rule 3 — Ledger discipline

Every refuted axis is recorded with its *construction*, not just its sign, so a future attempt can differ materially
instead of repeating a defeated implementation. Before declaring an axis dead, state what mechanism was tried and what
the alternative would be. Record it in `knowledge/REJECTED_HYPOTHESES.md` (H-061…H-072 is the template), **not** in a
new root-level `.md` — a mechanism that lives only in a dated report gets re-imported by the next session as if it were
an idea.

## Rule 4 — Reporting

Loss-first, number-first: per-seed deltas, W/L/T per bank, engine pin, artifact paths. No plans, no status prose.
