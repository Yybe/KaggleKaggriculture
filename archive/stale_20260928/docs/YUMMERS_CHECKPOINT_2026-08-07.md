# Yummers Checkpoint — 2026-08-07

## What happened

Per user directive: scrapped the old self-built architecture, extracted the
`romantamrazov/kaggriculture-yummers` kernel from Kaggle, replicated its
internal selection gate on the local engine, simulated the winner, and
packaged the submission artifact. **No submission was made.**

## 1. Kernel extracted & decoded

- Kernel: `kernel_src/kaggriculture-yummers.ipynb` (22 cells, pulled via
  `python -m kaggle kernels pull romantamrazov/kaggriculture-yummers`).
- Cell [4] is a self-gating framework embedding 9 agent sources (gzip +
  base64 blobs): 1 anchor ("Anchor Top1 v22" = the exact Top-1 agent),
  4 challenger overlays, 4 control agents.
- Extracted to `top1_v22_4_agents/` (00_anchor_top1_v22.py …
  08_syouya_v23.py).
- `kernel_src/_cell4.py` reproduces the notebook's unpack/build logic;
  `kernel_src/_run_gate.py` replicates the notebook's Stage-A/B/holdout
  selection gate locally (parallel, 8 workers).

## 2. Gate replication result (promotion == notebook logic)

| Stage | Result |
|---|---|
| Stage A (4 challengers vs anchor, 5 seeds, symmetric pairs) | all 4 challengers 9-1 (net +8, all 5 positive pairs) |
| Stage B (tested vs 4 controls, 2 seeds) | all 16-0, mean money ≥ anchor |
| Holdout (tested vs anchor, 2 seeds) | challengers 4-0, no negative pairs |
| **Promotion** | **SELECTED = "Guarded Surplus + Late Preempt"** (score tie-break 8749131.5) |

- `selected_main.py` == `builds/yummers_selected.py` == `main.py`
  (byte-identical on disk; sha256
  `81d185401e5bbccd92eb7b7cbf6564a99c12ffc134aced81fd9a931e636fad27`).
- Anchor source sha256 (in-memory, as printed by `_cell4.py`) =
  `62fb5a5f66f0011092a2b51e3192879ba583d5d815d761f176091c615657147a`;
  on-disk `00_anchor_top1_v22.py` sha256 =
  `ad6954c1e8e1cebbbc4dbce59686214ec0627d70e70dd495e00585f528e67168`.
  NOTE: disk hash differs from in-memory because `write_text` normalized
  line endings on Windows; content of the agent is identical.

## 3. Engine / determinism

- Notebook requires engine ≥ 1.32.4 (needs Python ≥3.11); local env has
  kaggle-environments 1.25.9 (Python 3.10.11). Upgrade impossible from PyPI
  (no compatible wheel for this Python) — engine 1.32.4 not installed.
- **Equivalence proven**: local re-runs of the notebook's embedded
  LOCAL_EVIDENCE mirror scores (official 1.32.4 engine, seeds 1–5) are
  bit-identical on engine 1.25.9:
  `122394 / 99888 / 127952 / 156936 / 105891` (anchor mirror, per seat).
- Smoke vs random 3 seeds: P0 = 201011 / 204562 / 209271, all DONE.

## 4. Local simulation results (20 seeds: 101…2020, 8 workers)

| Matchup | W-L-T | mean margin | mean cand | mean opp |
|---|---|---|---|---|
| yummers vs starter | 20-0-0 | +196,046 | $199,544 | $3,498 |
| yummers vs random | 20-0-0 | +202,606 | $202,657 | $52 |
| yummers vs pass | 20-0-0 | +195,663 | $198,663 | $3,000 |
| yummers vs baseline(anchor) | 20-0-0 | +490 | $108,902 | $108,412 |
| baseline(anchor) vs starter | 20-0-0 | +196,046 | $199,544 | $3,498 |
| baseline(anchor) vs candidate9e (OLD agent) | 20-0-0 | +130,773 | $181,695 | $50,921 |
| baseline(anchor) vs baseline(anchor) mirror | 2-0-18 | +311 | $108,816 | $108,506 |

Old agent (candidate9e) reference from pre-cleanup gates: mirror mean
**~$60k/player**; yummers mirror mean **~$108.6k/player**.

## 5. Verdict vs leaderboard

- Local recent "top replays" band: mean ≈ **$110,584**, range 84,221–147,972.
- Yummers anchor-seat mirror: ≈ **$99k–157k** (5 official seeds), ≈ $108.6k
  mean on 20 local seeds — **inside the top-band** (mean at or above leaderboard
  mean).
- vs built-in starter/random/pass: absolute crushing (20-0-0, $196k+ margins).
- **Verdict: the yummers agent is AT / ABOVE the leaderboard band locally.**
  Not submitted.

## 6. Checkpoint artifacts

- `kaggriculture_project/main.py` — extracted selected winner (578 lines,
  27,462 B; sha256 `81d185401e5bbccd92eb7b7cbf6564a99c12ffc134aced81fd9a931e636fad27`)
- `kaggriculture_project/builds/yummers_selected.py`, `builds/yummers_anchor.py`
- `submission/submission.tar.gz` — packaged (gzip+tar, `main.py` at root,
  sha256 `3ae0d29702c68ed1ec4c40f977aa8d2d44fe246c1c8dbb42e54b60f58578224d`) —
  round-trip verified.
- Replays & prior performance data kept: `kaggriculture top replays/` (9),
  `kaggle_v3_replay/` (3), `kaggle_v3_logs/`, `replays/` (0), `docs/`,
  `h2h_detail.txt`, `top_replays_mining.txt`.

## 7. Next step (BLOCKED on user allowance)

User gated the improvement phase: "ONLY AFTER MY ALLOWANCE implement
improved plan as above based on 20 replays and apply to yummers; compare
**normal yummers vs improved yummers**". Not started until approval.

Cleanup note: all old self-built modules (agent/, build.py, tests/,
competitor_notebook/, official_env/, stray `{agent,tests,..}` dir, and 12
old candidate builds) archived under `archive_old_2026-08-07/`.