# Public Agent Registry — kaggriculture

Retrieval priority: **P0 (CURRENT)**. This file is the authoritative list of public (kernel-visible)
agents and whether any of them supersedes our baseline. Normal research retrieval consults this file
*before* pulling anything new.

## Scan record

| Field | Value |
|---|---|
| Scan performed | 2026-09-25 16:42–16:52 UTC (= 22:12–22:22 IST) |
| Tool | Kaggle CLI 2.2.4 (`kaggle kernels list --competition kaggriculture --sort-by dateCreated|voteCount --page-size 100`) |
| Raw lists | `scan_20260925/kernels_newest.csv` (100 rows), `scan_20260925/kernels_topvoted.csv` (100 rows) |
| Pulls + extraction | `kernels_pulled/scan_20260925/` (notebooks) → `kernels_pulled/scan_20260925/extracted/` (agent sources) |
| Extractors | `tools/extract_kernel_agent.py` (writefile / b64+gzip / literal cells), `scratch/p8_decode_blob.py` and `scratch/p9_decode_packed.py` (base85+zlib+tar `_PACKED_SOURCE` / `_BLOB` cells) |
| Environment for every verification | `WybeV2/rank_env`, `kaggle-environments==1.32.7`, `townCenterSellInterval=24`, `episodeSteps=720` — pin asserted by `tools/e209_live_entry_probe.py` ("engine pin: 1.32.7 ok") |
| Reference opponent for every comparison | `agents/cha22_champion.py` (sha1 `c17f23f64f7c`, 501,561 B) = live baseline, 2376.2 public |

## Discovered and screened this scan

Verdict scale: **SUPERSEDES** (promote to baseline) / **NEUTRAL** (within noise of baseline) /
**WEAKER** / **COPY** (byte-identical to something we already run) / **UNDECODED**.

| Kernel ref | Author | lastRun (UTC) | votes | Extracted size | sha1 (12) | Live entry (platform `get_last_callable`) | vs `cha22_champion` | Verdict |
|---|---|---|---|---|---|---|---|---|
| `abhinav0370/cha22-agent` | Abhinav0370 | 2026-09-24 09:30 | 90 | 501,543 B | `a8da73093c8e` | not probed | — | **COPY** — byte-identical to `agents/cha22_byte_identical.py` (`a8da73093c8e`), i.e. our own baseline circulating publicly |
| `haideptry/the-shepherds-ledger-herd-safe-sovereign` | haideptry | 2026-09-25 04:09 | 8 | 1,051,849 B | `6200df250b2d` | `hs4_ig_agent`, `== gate agent: **False**` | probe seed 7770000 −708; **R1 n=16: 1W/7L/0T, −932.8/seed** | **WEAKER** |
| `statma/kaggriculture-herd-safe-sale-window-race-ca25` | statma | 2026-09-23 11:59 | 11 | 1,033,759 B | `4efdb4ae5985` | `opening_liquidity_agent`, live entry reachable | probe seed 7770000 −734; **R1 n=16: 0W/8L/0T, −1,268.5/seed** | **WEAKER** |
| `wzhengbiao/kaggriculture-v15stack-submit` | WUZB | 2026-09-22 19:00 | 61 | 1,065,705 B (restored from 854,856 B wrapper) | `4d87b5ce03aa` | `v15_submission_entry`, `== gate agent: **False**` | probe seed 7770000 −1,272; **R1 n=16: 1W/7L/0T, −860.9/seed** | **WEAKER** |
| `yasutakababa/kaggriculture-late-purchase-v16-submit` | yasu | 2026-09-23 12:28 | 4 | 1,067,486 B (restored from 857,250 B wrapper) | `8798bbcc5ae8` | `v16_submission_entry`, `== gate agent: **False**` | probe seed 7770000 −1,272 (identical to v15stack); **R1 n=16: 1W/7L/0T, −871.0/seed** | **WEAKER** |
| `haideptry/the-2965-master-hybrid-engine` | haideptry | 2026-09-25 04:08 | 28 | 1,045,228 B | `fc93c8357f26` | `v7_hr_agent`, `== gate agent: **False**` | probe seed 7770000 −1,100; **R1 n=16: 1W/7L/0T, −599.1/seed** | **WEAKER** (closest of the five; same `v7_ig_agent` donor family as the herd-safe stack) |
| `arsgorynich/herd-safe-v3-experimental-risk-aware-feed` | Arsgorynich | 2026-09-23 10:15 | 70 | — (notebook only, extraction pending) | — | — | — | **UNDECODED** — highest-voted member of the "herd safe" family; decode before the next scan |
| `flexonafft/kaggriculture-multi-route-farming-agent` | Igor Zharov | 2026-09-25 15:32 | 112 | — (`_PACKED_SOURCE` b85 chunks, 704 B decoded then failed) | — | — | — | **UNDECODED** — newest high-vote kernel; declares `EXPECTED_SOURCE_BYTES = 148,200`, a *small* agent, i.e. a different size class from the 1.0 MB clone family. Worth the decode effort |
| `guruprasaathas111/kaggriculture-top-2-master-engine-v4` | Guru Prasaath S | 2026-09-25 15:03 | 34 | 11,560 B of 47,943 B decoded (`_c2.py`) | `47b573e3824c` | — | — | **UNDECODED** (only a helper cell recovered; agent cell not found) |
| `statma/kaggriculture-tetsutani-demand-preserving` | statma | 2026-09-23 01:55 | 1 | not attempted | — | — | — | **COPY-adjacent** — a re-publication of the tetsutani demand-preserving family our donor comes from |

Ladder log: `scan_20260925/ladder_r1.txt` (probe logs `scan_20260925/probe_newkernels.txt`,
`probe_newkernels2.txt`).

## Conclusions that hold after this scan

1. **No public kernel supersedes our baseline.** All five extracted, executable public candidates measured
   *below* `cha22_champion` on the pinned engine: probe-seed deltas −599 … −1,272, and R1 (16 games each)
   1W/7L/0T −599.1 (`the-2965-master-hybrid-engine`, the best of the five) / 1W/7L/0T −860.9 /
   1W/7L/0T −871.0 / 1W/7L/0T −932.8 / 0W/8L/0T −1,268.5. Zero ties against our baseline across all 80 games.
   Baseline promotion on public-kernel evidence is therefore **not** warranted (see `CURRENT_STATE.md` §Baseline).
2. **The 2900–3075 top of the field is not publicly observable.** Ranks 1–13
   (`scan_20260925/kaggriculture-publicleaderboard-2026-09-25T16_42_11.csv`) are private submissions.
   Any claim about what the current top field does must come from **replay forensics**, not from pulling a kernel.
3. **Public kernels share our own failure mode.** Three of five extracted kernels resolve live to a name
   that is *not* their `agent` binding (`== gate agent: False`), confirming the
   `get_last_callable` entrypoint rule as a field-wide property, not just our bug. Their published scores and
   their outermost layer may disagree.
4. **The 2900+ band publishes nothing.** `kaggle kernels list --author <u>` was run for the team members of
   ranks 1–13 (denden12, masspeaks, shimishige, boeychenjun, flynnfei, majkel1337, zy1343930734, linkinpony,
   morimo, vadimvasilenko, mtmrs1, jackvd, ethanl67, densike, simann) on 2026-09-25: **zero** public kernels
   matching this competition. Their agents are unreachable as code; only their replay episodes are.
5. **The "herd safe" family is the live public meta** (70 / 11 / 8 votes across three 2026-09-23…25 kernels,
   plus `v15stack` / `late-purchase v16`). All measure weaker than cha22, so it is a *marketing* meta, not a
   competitive one. Re-check if any of them jumps above ~100 votes or a kernel starts claiming 2900+.

## Re-scan 18:42 UTC (freshness check for the capacity mission)

`kaggle kernels list --competition kaggriculture --sort-by dateCreated --page-size 12 --csv`: **no kernel
published after the 16:42 scan**. Movements only: `abhinav0370/cha22-agent` 90 → 91 votes,
`haideptry/the-shepherds-ledger-herd-safe-sovereign` 8 → 9. Nothing materially new, no new lineage, and
therefore no new promotion candidate. Our live position at the same moment: team 16669256 **rank 685, 2365.7**;
child ref 56554887 **2319.6** and still rising. Leader DSM 3073.7; Fourth Quadrant left the top 12.

## Standing rule for future scans

Run, in order: `kaggle kernels list --competition kaggriculture --sort-by dateCreated --page-size 100 --csv`
→ screen for (a) size class outside 0.5–1.1 MB, (b) title/votes claiming ≥2900, (c) any kernel published after the
timestamp above → extract with `tools/extract_kernel_agent.py` → `tools/e209_live_entry_probe.py` (asserts the pin
*and* the live callable) → single-seed probe vs `agents/cha22_champion.py` → only then an R1 bank. Do not open a
long optimisation run before this screen has been refreshed inside 24 h.
