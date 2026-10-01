# Sparring pool + how we run gates (2026-09-21)

Everything here is public-lineage code (Apache-2.0 kernels or the reference bundle you
already have) plus our own builds. No private third-party agents.

## Harness (the boring prerequisite)
- kaggle-environments **1.32.7** + hinge, python 3.12. On 1.32.5 episodes RUN but every
  reward silently shifts — pin the interpreter or your deltas are garbage.
- `tools/diag_bench_seeds.py A.py B.py SEED_CSV OUT.txt --interval 24`
  config `{"episodeSteps":720,"seed":S,"townCenterSellInterval":24}`.
- Runs are EXACT-deterministic: same two files + same seeds = same numbers on any machine.
- Count seed-level (both seats averaged). A ±delta that flips sign under seat swap is a
  market-priority artifact, not a loss. Always keep a byte-identical control tape.

## Seed banks we use
- r1 (tuning): 1000000,2000000,3330000,5000000,6000000,7770000,8000000,9000000
- r2 (holdout): 1110000,2220000,4440000,5550000,6660000,8880000,9990000,1111111
- fresh (never tuned on): 30000000..30015000 step 1000; older fresh-32: 20001000..20032000 step 1000

## Opponent tiers

### Tier 0 — our own reference points (md5 pins)
| file | what it is |
|---|---|
| `crop_roi30_h20.py` md5 2fb63954442b1059d644c9c23371e098 | submitted champion (your crop_roi30 + day-20 horizon gate) |
| `v219_r78u.py` md5 319aad8c48675c51432ccec8f35264b8 | h20 + V219 SE/tomato UNION gate |
| `h20b.py` md5 18333374b6ac58157cbda5731a447f91 | h20 + CL mature-wheat tail (+27/+28/game) |
| `r78ub.py` md5 a4b6cc1965d08263acb176c7dd6c9aee | r78u + CL tail — current strongest, live ref 56424512 |

### Tier 1 — spine baselines (from your bundle, `reference_bundle_20260920/agents/`)
`pub_metav4_early.py` (champ), `pub_metav4.py`, `pub_metav4_crop.py`,
`pub_demand_timing.py`, `v33_shields.py`, `salemali7_3000score.py`, `kaggle_v22/v23/v26*`.
Note: `kaggle_champion_v15.py` / `kaggle_v14_*.py` are UNRUNNABLE locally — they import
the missing `kaggle_boat84_v14` module. If you have it, that's the one real gap in the pool.

### Tier 2 — public counter-kernels (extracted agent .py, in `lab_20260921/kernels/`)
v48-fast-routes (40-40), beat-v48 (100-0 day-6), countering-the-big-3, demystifying-2900,
farmer-john-and-the-idle-seller, soil-remembers-rain, pipe16/idle-workers/2950-peak
(one agent, md5 d7487…), one-more-wheat, v50/v51/v52/v53 flock series,
visible-price-switch-lab, 2945-farm, 2965-master-hybrid, metav4-farm-v13, shop-router-0909
(the yhay81 one needs an external actions.json — not benchable as staged).
h20's record vs this tier: 128 games, zero losing seed, +40..+3299.

### Tier 3 — the current top-tier proxies (NEW, this is what you asked for)
Audit-notebook kernels ship the real agent as an embedded archive, not as `def agent` —
extract `main.py` out of `ARCHIVE_BYTES` (base64 tar.gz) or `BLOB` (base85+gzip):
| file | md5 | source kernel | what it is |
|---|---|---|---|
| `proxy_top2.py` | 9b3e87de8ec94f8a6f5665306b9f2665 | guruprasaathas111 "TOP 2 Master Engine V4" == Gluzdov "More Wheat Smarter Sales" (byte-identical notebooks) | public V39 spine + CL wheat layers = an h20b-class mirror |
| `proxy_beyond48.py` | d4025cae1367757b31de783954a74a5c | jaxa623 "[2780] Beyond 48-0" (K0006) | V43 "Recovering Lost Harvests" + single-order step-0 wheat wrappers |

Latest gate results vs Tier 3 (r1 seeds, both seats, all seat-invariant):
- r78ub vs proxy_top2: 4W/0L/4T seed-level, mean +566 (max +3115)
- r78ub vs proxy_beyond48: 8W/0L/0T, +717..+7389
- h20 vs proxy_top2: 2W/6L — loses exactly −27/−28 (proof it's h20b-class)
- h20 vs proxy_beyond48: 8W/0L, +3299
- fresh-16 (30000000..30015000) r78ub vs proxy_top2: 8W/1L/7T; the lone −145 (30003000)
  reproduces score-identically for h20b → shared-line wobble, not a r78ub regression.

## Promotion law we hold everything to
Zero seed-level losses vs base on ≥2 independent seed sets → then vs Tier 1 → Tier 2/3,
no (opponent, seed) cell where the challenger is worse than base beyond seat-priority
artifacts. A variant that can't pass this doesn't ship, regardless of mean delta.
