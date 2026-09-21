# Agent Operating Manual — Kaggriculture Competitive Engineering

**Source of truth**: [`processing.md`](processing.md) (7-phase workflow) + [`APEX_V5_AGENT_DOCUMENTATION_20260921.md`](APEX_V5_AGENT_DOCUMENTATION_20260921.md) + [`kaggriculture_compressed_replay_retrieval.ipynb`](kaggriculture_compressed_replay_retrieval.ipynb).
This file is the mandatory pre-flight. Read it before reading memory, before planning, before writing an agent.

## Rule 0 — Read the directory before you reason about it

Every session, before any analysis or code: run `ls *.md` and open the docs that exist
(`processing.md`, `APEX_V*_AGENT_DOCUMENTATION_*.md`, `FRIEND_INSIGHTS_*.md`, `FRIEND_SPARRING_POOL_*.md`,
`RESEARCH_RULEBOOK.md`, `AGENT_BUILD_GUIDE.md`). Memory notes are a *index*, the directory is the *evidence*.
Claiming an axis is "closed" without re-reading the current docs and tools is a prohibited failure mode.

## Rule 1 — The 7-phase workflow (execute in order, don't improvise a phase)

1. **Prompt ingestion → 3 hypotheses**: chassis limit vs. *interaction* limit; state-query bugs (`observation["private"]["shed"]`,
   never `farm["inventory"]`); dead vs active levers (check the `FRIEND_INSIGHTS_*` ledger first).
2. **Replay ingestion**: Parquet pipeline, never loose JSON. `tools/fetch_episodes.py` / `tools/batch_fetch_replays.py`
   → `WybeV2/datasets/e98f_top10/episodes.parquet` → `WybeV2/datasets/e98f_epidx/manifest.csv`
   → `tools/extract_live_opponents.py` for base85+zlib action tapes (`agents/live_replay/`).
   Header scan reads only the first 64 KiB per replay; shards are `zstd` level 10.
3. **Forensics / strategy DNA**: `tools/atlas_0921.py`, `tools/atlas_agg_0921.py`, `tools/live_loss_anatomy_0920b.py`.
   Metrics: labor curve, quad unlock timing, fert/water counts (champions run 135–249 fert vs our 85–110),
   `everplant` crop matrix, revenue split, market order timing.
4. **Base-lineage elimination before modification**: `WybeV2/rank_env/Scripts/python.exe tools/fast_matrix_eval.py`.
   Core Decision Law: keep the **metav4 spine**, fix the **market interaction layer**.
5. **Modular onion layers**: build via append-only `tools/build_*.py` scripts that concatenate base + wrapper
   (`_N_PARENT = agent; del agent; def agent(...)`), never by hand-editing the 1 MB spine. Each layer = one mechanism.
   **Every graft must be proven live before it is gated** — a silently-inert graft gates as a clean tie and reads as
   "zero regression": (a) assert the anchor/marker counts in both source and output (`assert out.count(sym) == 2`),
   (b) assert slice bounds (`rindex` vs `index` — duplicated EOF markers produce an empty layer),
   (c) `import` the output and assert the layer symbols exist on the module, (d) run a firing-counter probe
   (`tools/probe_e101_layers.py` pattern) over 2–4 seeds and require non-zero fires, plus a byte-size delta vs the base.
6. **3-tier deterministic gate** on pinned `kaggle-environments==1.32.7`, `townCenterSellInterval=24`:
   R1 (8 seeds), R2 holdout (8 seeds), Fresh holdout (16 seeds), both seats per seed —
   `tools/test_candidate_breakthrough.py` / `tools/run_h2h.py CAND OBS [r1|r2|fresh|all]`.
   Assert the engine version inside every gate log.
7. **Deploy + document**: single-file `submission.py`, mirror to `agents/`, write `*_AGENT_DOCUMENTATION_YYYYMMDD.md`
   (lineage, architecture stack table, benchmark matrix, deployment record) and update `processing.md`.

## Rule 2 — Tie-breaking law (the actual ceiling)

Identical-spine agents share steps 0–84, land expansion and sell schedules → **seed-level ties are a defect, not a result**.
A gate that returns ties is an *untested* candidate, not a validated one. Break symmetry on the market axis:
- `_apex_tuned_clone_preemption`: sell at `step % 24 == 23` (one turn before the clone wave) when
  `prices[item] >= floor`, inside `240 <= step <= 671`, **one item per turn**, and book the executed quantity into
  `state["debt"][item]`; repay it out of the scheduled step-24 order so total volume is conserved.
  Without the debt ledger a preempt is a double-sell that crashes your own price — that is why earlier front-run attempts lost.
- `_apex_precision_terminal_sweep`: liquidate 100% residual shed inventory into open market slots (≤10 orders) at steps 716–719.
- Never re-run base scans: the public pool is metav4/pipe16 clones only.

## Rule 3 — Ledger discipline

Every refuted axis is recorded with its *construction*, not just its sign, so a future attempt can differ materially
instead of repeating a defeated implementation. Before declaring an axis dead, state what mechanism was tried and what
the antigravity-layer alternative would be (debt-accounted preemption, shadow-price ordering, terminal sweep).

## Rule 4 — Reporting

Loss-first, number-first: per-seed deltas, W/L/T per bank, engine pin, artifact paths. No plans, no status prose.
