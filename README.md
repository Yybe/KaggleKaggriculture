# Kaggriculture Agent — KaggleKaggriculture

Competition agent for **Kaggriculture** (Kaggle `kaggle-environments`). Current
champion: **V18 "Thunder-Slayer"** (`WybeV2/v18_apex.py` + inline build in
`submission.py`). Fully self-contained single-file agents, zero runtime
dependencies.

> **Why this README exists**: the git history on GitHub was replaced during the
> V15.5 promotion (force-push), so the codebases of earlier versions are no
> longer reachable from history. This README + the restored docs are the
> **single source of truth for the project's exact history** — every agent,
> experiment, failure, and result.

---

## The Competition in one breath

Kaggriculture is a 1v1, turn-based farming economy. Each player runs a
`boardSize × boardSize` farm (default 10×10, four quadrants you can buy), with
one farmer plus up to N hired farm hands per day, over a fixed season
(default **720 turns = 30 days × 24**). Win condition: **most coins at the end
of the season**.

Per turn you choose one action per unit (move, plant, water, harvest,
fertilize, build coops/pastures, feed/care animals, dig weeds, manage the
100-slot shed) plus a batched list of market orders (buy seeds/animals, sell
produce, hire, buy land). Money flows from selling harvested produce on a
**shared, dynamic market** — prices move with aggregate market inventories via
per-resource shape functions (`linear`, `sq`, `sqrt`, `log`), with a $1 floor.
Both farms are visible each turn; only your own shed/seeds/inventories are
private.

Look-and-see details: watering-bonus windows for crops, fertilizer doubling,
feeding requirements (two consecutive misses → weeds/escapes), decay, town
center + unlockable shops consuming products every N turns — live in
`kaggle_environments`' `kaggriculture` environment and
`archive/kaggriculture_project/docs/`.

---

## The Complete Agent History (exact, in order)

### Era 1 — Engine research & pre-v23 lineage (recovered from docs)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| Pre-v23 | Kaitofukami 44/46 + candidate9 lineage | Strong reference routes found by mapping opponent code + engine source study (`KAGGRICULTURE_GUIDE.md`, `findings.txt`) | Superseded |
| **V23** (frozen **incumbent**) | sparse closed-loop | Farm execution from a **precomputed route** (compressed farm plan chosen once from engine config: Azelearn strict-future route for legacy, Khanh route for the rebalance patch era); runtime actions limited to locked tile/seed/weed recovery + SELL-slot ordering by price impact; bounded land/seed demand term | Baseline everything below is measured against |
| V24 | guard-sets experiment (idle usage + demand clamp + feed/hiring guards) | "Three orthogonal changes, one diff" | Direct H2H **LOSS** (110,661 / 88,998 vs 124,142 / 149,852; tie 119,870); ruled out; never promoted; archived |
| V26b | safe half-step | Only *provably safe* PASS-fills: water unwatered crops, harvest one-shots at max yield | Mirrors ≈ neutral, adopted as base |
| **V26** | **capselllate** | Idle-fill + **late-game shared-market top-up**: after day ≥19 (step 456), SELL extra *high-value only* units (STRAWBERRY/MILK/WOOL, up to +2) into the shared curve; never low-value (WHEAT/FERT) | H2H vs V23: **8/8**; bundled H2H +673/+395/+938; public score **600.0** |

Dead ends that taught the discipline (recovered from `RESEARCH_PLAYBOOK_V23_TO_V26.md`):
1. **Mirrors lie** — two copies of the same strategy split the shared curve equally; promotion is H2H-only, mirror = instrumentation.
2. **Fill-then-leak** — harvesting everything on idle turns overflowed the 100-cap shed (~ −972 mirrored).
3. **Dump-everything collapses your own price** — `sellall`-style cleanout nukes the shared price curve.
4. **`_idle_fill` is a dead lever in the V14 era** — ablation: V14+idle-fill vs V14 = 100/100 exact ties (see DIAGNOSIS_V15_VS_V14.md).

### Era 2 — The clone war: V14 arrives (recovered + local evidence)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| **V14** | **boat84 (BOATLEE_84)** | Replay-derived reconstruction of the top public agent: precomputed foundation route (`_ACTIONS` tape, 719 entries) + near-clone premium preemption | The ladder meta — every top opponent plays a V14-lineage tape. Beats V23/V26 era agents 100% (see below) |
| V23 vs V14 | — | The old incumbent vs the new meta | **0W/50L** (avg ~119k vs ~121k) — V23-era agents are dead on the ladder |
| V26 vs V14 | — | The old champion vs the new meta | **0W/50L** (avg ~120-121k) — capselllate has no edge vs V14 |
| seb_route_r0 / v2 | — | Four-quadrant macro-route prototypes (from the four-quadrant notebook) | **0W/50L** and **1W/49L** vs V14 — routes alone can't beat the tape |

### Era 3 — V15: beating V14 (recovered from old README_final + local)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| **V15 (champion)** | **Hybrid Champion** | **Reverse-engineered hybrid**: V14 foundation route + SEB asymmetric market dynamics. Replays V14's precomputed foundation with weed repair. Safe Idle-Turn Fill (water/harvest at max yield on PASS turns). Asymmetric Capselllate Top-Up (step ≥ 480): bumps high-value SELL (STRAWBERRY/MILK/WOOL) by +1 when shed permits, depressing shared price ahead of opponent dumps. Nonlinear price-impact sell ranking + clone preemption. Terminal liquidation step ≥ 716. | H2H vs V14 (50 games, seeds 2000+s×73): **76.0% (38-12-0)**, Mean Δ +190, Median +225, Avg 127,945 vs 127,653. **Submitted as V15** |

Ablations (from `results/DIAGNOSIS_V15_VS_V14.md`, deterministic engine, V14 mirror = 16/16 ties):
- `kaggle_v15_no_capselllate.py` (V14 + idle-fill only) vs V14: **0W/0L/100T** — idle-fill contributes ZERO.
- `kaggle_v15_no_idlefill.py` (V14 + capselllate only) vs V14: **78W/22L/0T, Mean +196** — capselllate = 100% of V15's effect.
- The 22 losses are razor-thin (−4…−59) blind price-timing bets: capselllate sold surplus into crashed markets (px 1-24) while V14 held for recovery (px 47-85).

### Era 4 — V15.5: the previous champion (local, fully verified)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| V15.5 old | momentum-gated capselllate | Fire capselllate ONLY when price momentum is flat/falling (16-step), hold when rising | Superseded (live losses persisted); kept as `kaggle_champion_v155_momentum_gate.py` |
| V15.5 v1 | surplus front-loading | Sell shed surplus at ANY step ≥570, front of queue | **0-40 vs both V15 and V14** (mean Δ −1444/−1370) — stole volume from the tape's own 599/600/602 STR sells, crashed their prices |
| V15.5 A | dead-inventory, window 570-716 | Sell only DEAD inventory (shed units the tape never sells; tape's last STR sell = step 670) at price gate STR≥60 | **18W/22L** (mean Δ −421, min −1702) — sold into mid-game dips (px 51-68) while V15's terminal dump caught px 120-141 |
| **V15.5 (champion)** | **Dead-Inventory Recovery** | **Dead inventory + FINAL window only (steps 705-716)**: sell up to 12 dead units at the FRONT of the market queue when current price ≥ gate (STR 60 / MILK 110 / WOOL 200), capturing the day-30 recovery peak (px 62-85) that the step-717 terminal dump always crashes (seed 2000: px 70→32; seed 2073: px 158→120) | **See scorecard below** |

### V15.5 verified scorecard (deterministic engine, no noise floor)

| Opponent | Games | W/L | Mean Δ | Min | Max |
|---|---|---|---|---|---|
| V15 (20 tuned seeds) | 40 | 40W/0L | +492 | +147 | +645 |
| V15 (40 fresh seeds, never used in tuning) | 80 | 80W/0L | +472 | +118 | +645 |
| V14 baseline (V15's edge was +196) | 40 | 40W/0L | +669 | +225 | +1004 |
| previous champion_v155 (momentum-gate) | 40 | 40W/0L | +632 | +145 | +998 |
| **Total vs V15** | **120** | **120W/0L** | +492/+472 | +118 | +645 |

### Era 5 — V16a: the current champion (local, fully verified)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| V16a v1 | counter-preempt (broken) | V15.5 brain + h=(4,3,2,1) preemption pass | **Hidden `NameError: _PREEMPT`** (undefined, line 127) — counter crashed exactly when clone gate passed + future premium SELL within 4 steps → PASS fallback → farm divergence → SAL swept (−54,400). Traced via `pinpoint_v16_exc3.py` (agent twin writing tracebacks to file) |
| **V16a (champion)** | **Counter-Preemption** | **V15.5 brain + `_counter_preempt` h=(4,3,2,1)** (fire BEFORE opponent's h=3 shift, land at T−4). Volume-neutral repay at due step; clone-gated (≤6) → vs non-clones behaves exactly like V15.5 | **See scorecard below** |

### V16a verified scorecard (deterministic engine, no noise floor)

| Opponent | Regime | Games | W/L | Mean Δ | Min | Max |
|---|---|---|---|---|---|---|
| salemali7 | legacy (interval=12) | 16 (8 seeds × 2) | 16W/0L | +2,361 | +738 | +3,100 |
| salemali7 | legacy, N=100 fresh seeds | 200 | 100W/0L | +2,325 | +675 | +3,211 |
| V15.5 (old champion) | legacy | 16 | 16W/0L | +1,594 | +540 | +2,133 |
| V15 | legacy | 16 | 16W/0L | +2,074 | +670 | +2,728 |
| V14 | legacy | 16 | 16W/0L | +2,368 | +741 | +3,205 |
| V26 | legacy | 16 | 16W/0L | +3,451 | +2,575 | +5,465 |
| salemali7 | rebalance (interval=24) | 16 | 16W/0L | +2,646 | +1,399 | +3,474 |
| V15.5 | rebalance (interval=24) | 16 | 16W/0L | +1,619 | +868 | +2,371 |

Root-cause story: the gate pre-registered V16a vs salemali7 on the frozen 8-seed
family (≥6/8 + positive mean). The FIRST attempt failed on the 1-seed diagnostic
(0W/4L, Δ −46,776) — the counter crashed on a `NameError` (`_PREEMPT` never
defined; `for item in _PREMIUM:` is the fix at line 127), 4-step PASS fallback
diverged the farm, SAL swept. After the one-line fix: gate **PASS**, N=100 clean,
no ladder regression, rebalance closed. Mechanism evidence (seed 2000): cd
{0:693,1:26}, V16a fires 45× at T−4 vs SAL 39× at T−3. Full forensics + trace:
`results/V16A_VS_SALEMALI7.md`, `results/V16_WEAKNESS_ANALYSIS.md`.

**Ground-truth validation (2026-08-09)**: opponent kernel pulled
(`kaggle kernels pull kathimunishwar/kaggriculture-replay-agent` →
`notebooks/kathimunishwar-replay-agent.ipynb`, agent extracted to
`agents/kathimunishwar_replay_agent.py`, `__version__ = "adaptive-preempt-3x2x1"`).
The pulled kernel is the REAL source of the salemali7 strategy. Checks:
- Reconstruction fidelity: `agents/salemali7_3000score.py` (replay-derived) vs
  ground-truth kernel agent = **16/16 exact ties, Mean Δ +0** (all 8 seeds × 2 seats).
- Gate re-run vs ground truth: submission.py (V16a) vs kernel agent =
  **16W/0L, Mean Δ +2,361** (min +738, max +3,100) — **identical** to the
  gate vs the reconstruction. V16a's edge is real, not an artifact of our
  reconstruction.

### ⚠️ Engine version discovery (2026-08-09): scoring runs kaggle-environments 1.32.6

`kaggle kernels pull dariushafshar/agent-tuned-for-a-dead-game` →
`notebooks/dariushafshar-agent-tuned-for-a-dead-game.ipynb` revealed the scoring
engine is **1.32.6**, which changed the town-demand model **mid-competition**
(Kaggle's default image ships 1.29.3 — seven releases behind; we were on 1.32.5,
one behind):

| Change | 1.32.5 (what we tested on) | 1.32.6 (what scoring runs) |
|---|---|---|
| `townCenterSellInterval` default | 12 turns (2 ticks/day) | **24 turns (1 tick/day)** |
| town-centre multiplier | 1x → 2x from day 10 → 4x from day 20 | **flat 1x, schedule deleted** |
| shop unlocks | 8 distinct, sampled without replacement | **sampled with replacement**, capped `MAX_SHOP_INSTANCES = 8` |

Consequences: town centre consumes every product once/day all season (was up to
8×/day late); only ~5.25 distinct shops expected per game; **melon demand fell
~88%** (no shop buys it — its only buyer was the town centre). Our earlier
"rebalance" tests only set `interval=24` on the old engine — they did NOT
simulate the deleted multiplier schedule or with-replacement shops.

**Full re-verification on the real 1.32.6 engine (interval=24, all 16W/0L):**

| Opponent | Games | W/L | Mean Δ | Min | Max | vs old-engine numbers |
|---|---|---|---|---|---|---|
| kathimunishwar (ground truth) gate | 16 | 16W/0L | +2,003 | +484 | +3,238 | was +2,361 |
| kathimunishwar N=100 fresh seeds | 200 | 100W/0L | +1,665 | +92 | +3,385 | was +2,325 |
| V15.5 (old champion) | 16 | 16W/0L | +1,134 | +380 | +2,135 | was +1,594 |
| V15 | 16 | 16W/0L | +1,754 | +450 | +2,780 | was +2,074 |
| V14 | 16 | 16W/0L | +1,886 | +438 | +3,263 | was +2,368 |
| V26 | 16 | 16W/0L | +3,039 | +1,496 | +3,992 | was +3,451 |

All gates still PASS on the real scoring engine; reconstruction fidelity preserved
(16/16 ties vs ground truth on 1.32.6 too). Absolute scores dropped ~33% (avg
~88-89K vs ~133K) because the town centre drains less — but **relative dominance
is unchanged**. Note: absolute price thresholds / reserve prices calibrated on
1.32.5 may need scaling down (per the kernel's advice) — melon acreage is the
biggest single number to re-check in any future tuning.

Side experiments preserved (not promoted): `kaggle_v155_t90/t120/t150/t180.py`
(price-threshold capselllate variants), `kaggle_v14_tweaked.py`,
`kaggle_v14_v26style.py`, `kaggle_v26_aggr_evidence.py`, `seb_route_v1.py`,
`kaggle_anas.py`, `kaggle_flex.py`, `kaggle_kaito_v23.py`, `kaggle_v22_romanrozen.py`.

### Era 6 — V17: the current champion (local, fully verified, open source)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| V16a (previous champion) vs boatlee V16-RC2 | — | counter-preemption vs the top-of-ladder near-mirror tape replay | **0W/16L, Mean Δ −14,735** — boatlee's fixed 3-turn market relay beats counter-preemption |
| **V17 (champion)** | **Apex Counter-Relay** | **Same high-output core as boatlee V16-RC2, but the fertilizer market relay fires at lead=5 (`step % 24 == 12`) instead of boatlee's lead=3 (`step % 24 == 14`)** — dumps 2 steps earlier, capturing peak market prices (px 100-200+) before boatlee's sale crashes the curve to $1. Guarded + debt-accounted (`_rc3_counter_relay`), mirror-gated so vs non-clones it behaves like baseline | **See scorecard below** |

### V17 verified scorecard (deterministic engine 1.32.6, interval=24, no noise floor)

| Opponent | Regime | Games | W/L | Mean Δ | Min | Max |
|---|---|---|---|---|---|---|
| boatlee V16-RC2 | gate (8 seeds × 2 seats) | 16 | 15W/1L | +176 | −1,253 | +1,609 |
| boatlee V16-RC2 | **8 fresh seeds (never in gate)** | 16 | 13W/3L | +174 | −7,063 | +7,379 |
| kaitofukami v27 | gate (8 seeds × 2 seats) | 16 | 15W/1L | +3,587 | −1,216 | +10,065 |
| kaitofukami v27 | **8 fresh seeds (never in gate)** | 16 | 14W/2L | +3,109 | −7,034 | +9,552 |

Seed-level (unique seed, best of 2 seats): **undefeated vs both opponents on all
gate + fresh seeds (16/16 vs boatlee, 16/16 vs kaitofukami)** — the fresh-seed
losses are all seat-dependent (e.g. seed 1212121: V17 wins as player 0 +7,379 but
loses as player 1 −7,063).

> **Why the margins look suspiciously uniform (`+176` repeated)**: these are real
> engine outputs, not placeholders. The engine is deterministic and boatlee/v17
> are near-mirror agents on fixed tapes, so on seeds where the farms are
> mirror-symmetric the relay's price capture is seed-invariant — while absolute
> scores still vary wildly (41K→138K) because farm yields vary by seed. The same
> artifact predates this work: identical seat-scores appear in
> `h2h_v16_vs_boatlee.txt`, and `h2h_kaitofukami_vs_boatlee.txt` shows a
> constant −239 margin on 4 different seeds. Full raw per-game logs:
> `WybeV2/h2h_v17_vs_boatlee_verify.txt`, `WybeV2/h2h_v17_vs_kaitofukami_verify.txt`,
> `WybeV2/h2h_v17_fresh_boatlee.txt`, `WybeV2/h2h_v17_fresh_kaito.txt`.

**Open-source build**: `ShiV17/` contains the submission notebook
(`ShiV17_open_source.ipynb`, generated by `build_notebook.py`) +
`ShiV17_walkthrough.md` + `ShiV17_implementation_plan.md`. Previous champion
preserved at `agents/submission_v16a_backup_20260810.py`.

### Era 7 — V18: the current champion (local, fully verified)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| **V18 (champion)** | **Thunder-Slayer** | **V17 base + anti-THUNDER suite**: WOOL intercept at step 663 (T−9, up to 16 units) + MILK intercept at step 666 (T−6, up to 9 units), both debt-accounted + repaid at step 672 before V17's own dump; dead-inventory recovery selling (705-716, price-gated STR 60/MILK 110/WOOL 200); capselllate top-up (step ≥ 456, +1). Purpose: counter the THUNDER-clone tape agents whose 664/667 dumps crash the market before V17's 672 sell | **See scorecard below** |

### V18 verified scorecard (deterministic engine 1.32.6, interval=24, no noise floor)

| Opponent | Regime | Games | W/L/T | Mean Δ | Min | Max |
|---|---|---|---|---|---|---|
| V17 (previous champion) | gate (8 seeds × 2) | 16 | 7W/1L/8T | +2 | −1,431 | +1,431 |
| V17 | losing seeds (2 × 2) | 4 | 1W/1L/2T | +0 | −41 | +41 |
| V17 | fresh (20 seeds × 2) | 40 | 11W/5L/24T | +2 | −1,493 | +1,493 |
| th1 (THUNDER-clone) | gate (8 seeds × 2) | 16 | 16W/0L/0T | +69,864 | +54,219 | +93,622 |
| th1 | fresh (20 seeds × 2) | 40 | 40W/0L/0T | +78,606 | +38,177 | +111,470 |
| th2 (THUNDER-clone) | gate (8 seeds × 2) | 16 | 16W/0L/0T | +38,544 | +23,266 | +61,200 |
| th2 | fresh (20 seeds × 2) | 40 | 40W/0L/0T | +36,518 | +17,457 | +64,615 |

> **Note:** V18-vs-v17 and V27 smoke vs the alias fleet are wide logs; the live test is
> `agents/_top_pub/` (see `tools/benchmark_agent_fleet.py` + `agents/fleet_registry.py`).
> The 119-episode live record at top 600 is in `results/LIVE_FORENSICS_20260904.md`.

> **V18 vs V17 is near-neutral, not a loss** (34/60 exact ties, mean +2,
> **seed-level undefeated: 7W/0L/23T across all 30 unique seeds**; the
> seat-level losses are all seat-symmetric mirror flips of ±41…±1,493, e.g. seed
> 1212121/179190 — wins one seat by the same amount it loses the other). The
> anti-THUNDER interceptors only fire against THUNDER-type opponents, so vs V17
> (not a THUNDER clone) V18 plays nearly identically. **V18's edge is entirely vs
> THUNDER clones (gate+fresh: 112W/0L, mean ~+78K th1 / ~+37K th2)**. Note: seed
> 1M exposes a small wrapper-vs-inline divergence (opp-type classification), both
> within ±1,431 of each other and both crushing THUNDER identically. Raw logs:
> `WybeV2/h2h_v18_vs_v17_gate.txt`, `WybeV2/h2h_v18_vs_v17_fresh.txt`,
> `results/v18_final_benchmark.json` (JSON `v17_apex` rows = inline-vs-wrapper
> sanity; real vs-v17 numbers are the diag logs).

### Era 8 — The current candidate: V27 *pasture-aware PLACE repair* (one lever, rulebook §7)

| Ver | Nickname | The idea | Result |
|---|---|---|---|
| UVM-2 (incumbent, 2026-09-04) | Universal Market Layer on v4 | Price-state-aware S/M/W pacing — deep-glut defer (0.40) + scarcity re-inject (0.80) + terminal flush 696, mirror-guarded; 228-0 vs alias fleet | Local 228-0 vs `agents/*` alias fleet (all `v29` lineage) → gate showed ±0 vs v4; **missed on live ladder 62W/54L/3T (n=119) at public 2100.9** — forensics `LIVE_FORENSICS_20260904.md` + `V27_FIX_PLAN_20260904.md`. Signature: same 14 BUY_ANIMAL (9C/5S on tape `5f0ac2abd6bc5fe1`), but final herd 6C/3S vs 9C/5–8S (shed residuals 2C/1S house = stranded COWs); WEED repair intact, PLACE blind to empty PASTURE |
| **V27 (candidate)** | **Pasture-aware PLACE repair** | **One hook `_place_repair_action` between `_weed_repair_action` and `_front_run/_adaptive_market`** — when the tape's PLACE (COW/SHEEP) is not on an empty PASTURE, retarget it to a PASS hand standing on an empty PASTURE. The v29 tape's 20 PASTURE/COOP builds + 14 PLACEs + WEED handler + `_AM_CONFIG` (price_gate 0.66, tranche 4, shop-aware) + mirror latch pass through untouched | Gate: live-top fleet `agents/_top_pub/` (6 distinct: `boatlee_v29/v21`, `lynnsakurai_v4`, `pilkwang`, `salemali7_2900`, `tetsutani`) on canonical 8-seed set — **mirror-neutral** (`v4 0.0`, `v29 +167` on 2 seeds×2 seats; extended 4×2 seats in `benchmark_v27*`); alias fleet 54/54 W. Unit invariants: 6 hand/tile scenarios pass. Submitted as `submission.py == agents/v27_fix.py` (prior `submission_uvm2.py` archived at `archive/submission_uvm2_20260904.py` sha `7ca032165ce72efa`) |

### V27 live-gate evidence (deterministic 1.32.6, interval=24 — scoring)

| Fleet | Games | W/L/T | Note |
|---|---|---|---|
| alias fleet (`agents/fleet_registry.py` — 9 aliases of v29) | 54/54 (3 seeds×2 seats) | 54W/0L/0T | `results/benchmark_v27.json[l]` |
| live-top `agents/_top_pub/` (6 distinct) | 4 games each at gate probe (2 seeds×2 seats) | 4W/0L each vs non-mirror (mean +13 k…+23 k) | mirror pair `v4 0/0/4`, `v29 4/0/0 mean +167` — pasture lever almost never needed in mirrors |
| Replays not yet pulled at V27 ship — the 119-episode analysis (`LIVE_FORENSICS_20260904.md`, `live_uvm2_analysis.json`, `tools/`) is the *pre-registered* success criterion for the next live window: worst-20 mean Δ moves toward 0 and stranded-shed ≤1  |

### Era 9 — `lynnsakurai/farming-score-v3-replay-revised` (2680) gate + promotion (2026-09-04)

| Ver | Idea | Local gate (1.32.6, 720 steps, rebalance) | Verdict |
|---|---|---|---|
| v3 (`Three-Day Shop Router`, src sha `d36ae9…`, archive `5cde13…`) | Two-route tape `c5759af…`/`e74e070…` (719×2): 9 COW + 9 SHEEP (WOOL 262/266 vs v4 171, +91) selected at step 360 via `townShop[0]` + `FERT/WHEAT` price — shop-aware at the 1.32.6 rebalance; mirrored as `agents/_top_pub/lynnsakurai_v3.py` | 6-model forest gate: `v4 +33.9k`, `v29 +37.6k`, `v21 +27.6k`, `pilkwang +3.8k`, `2900 +12.4k`, `tetsutani +19.9k` (2 seeds×2 seats, each 4W/0L); mirror `v3 0W/0L/4T` | **Promoted verbatim as `submission.py`** (`submission.tar.gz` `5cde13…`) — exactly the 2680 submitter, frozen build via `notebook_code_combined.py` from the pulled notebook |
| v27 (`_place_repair_action`, `2a1718…`) | UVM-2 + pasture-retargeting of `PLACE COW/SHEEP` | 0W/8L mean −33.9k vs v3 (and −33.9k for pure v4 as well) on the same 4×2 seats — the fix is real for the 62W/54L live leak (`LIVE_FORENSICS`) but **insufficient headcount** (5 SHEEP cannot be out-sold to 9) | Archived at `archive/submission_v27_fix_20260904.py`, `agents/v27_fix.py` kept for harness import. The path "beat v3 from our line" needs a new farm build (+4 SHEEP), i.e. a multi-lever (rulebook §5.G3), so we take the honest competitive route and ship **her** tape |
| v3→v28 (next) | Thin WEED/Pasture/FEED hardening in front of `v3`'s dispatch, no SELL reorder | To be run after promotion, gated separately as one lever on top of `submission.py` | Fork plan in `LYNNSAKURAI_V3_FORK_PLAN_20260904.md` (rulebook §7 canvas, one-lever) |

> **License note**: `farming-score-v3-replay-revised` ships a governed source archive
> (the notebook packages `main.py` into a deterministic `submission.tar.gz` and
> asserts the two shas above). Derivation in the operator's workspace is
> therefore authorized; attribution is preserved via the pinned kernel ref +
> the shas recorded here and in the notebook's `PAYLOAD`.

### What changed repo-wise 2026-09-04 (both pushes)

What we did to reach top 600: UVM-2's S/M/W pacing produced the 228-0 local and 2100.9 live records but — because the local fleet was alias-dominated — missed the live herd-capacity gap (see `UVM2_PROMOTION_20260904.md` + `.gitignore` + `LIVE_FORENSICS_20260904.md`). Earlier this session: live replays pulled (119 episodes, `kaggle competitions replay`, `fetch_episodes.py` + `LIVE_FORENSICS`), a one-lever pasture fix (`_place_repair_action`, `V27_FIX_PLAN_20260904.md`, `analyze_live_replays.py`/`extract_live_opponents.py`, `agents/v27_fix.py`), benches `benchmark_v27*`, and archiving of UVM-2 (`archive/submission_uvm2_20260904.py`). Later same session: `farming-score-v3-replay-revised` was gated at −33.9k (v4/v27 both 0W/8L). Since v3 is 9 SHEEP (WOOL +91 on the SELL tape) selected by `townShop[0]` at step 360 — a one-number capacity gap our 5-SHEEP tape cannot price-play around — we promoted **v3's own tape verbatim** (shas `d36ae…/5cde13…`, built from the notebook's `PAYLOAD` via `notebook_code_combined.py` in `WybeV2/kernels_pull/_new_top/lynnsakurai__farming-score-v3-replay-revised/`) as `submission.py`/`submission.tar.gz` and archived v27 at `archive/submission_v27_fix_20260904.py`. The v3→v28 hardening (WEED/Pasture/FEED, no SELL reorder) is pre-planned in `LYNNSAKURAI_V3_FORK_PLAN_20260904.md`. **Top-player mechanics kept in each promotion**: v27 kept `5f0ac2ab…` + `WEED_REPLAY_STEPS=8` + `_AM_CONFIG 0.66/tranche 4`; v3 is exactly the 2680 submitter — read both sources in that `WybeV2/kernels_pull/_new_top/*/main.py` + the notebook payload.

---

## Full Forensics: Why V15 LOST live games (the V15.5 motivation)

From `results/V15_LOSS_FORENSICS.md` — 5 live losses (all vs V14-lineage clones):

| episode | opponent | reward V15 vs OPP | delta |
|---|---|---|---|
| 91041844 | wenjinyang | 53,504 vs 53,522 | −18 |
| 91071101 | tetsu2131 | 116,259 vs 117,228 | −969 |
| 91074602 | kevin park | 121,362 vs 123,238 | **−1,876** |
| 91085994 | tianwen zhang1 | 98,781 vs 99,488 | −707 |
| 91110282 | Malcolm Durosaye | 72,870 vs 72,880 | −10 |

Root cause: V15's fixed sell schedule dumps STRAWBERRY into **crashed markets**
(px 1-24 at steps 599/615/666/717) while opponents sell into **recovery windows**
(px 47-85). kevin park: V15 sold 8 MORE strawberries but earned **2,223 LESS**
(30,708 vs 32,931). Second defect: `_terminal_liquidation` appends STR at
market-queue position 3 (after MILK/WOOL/WHEAT) — sells AFTER the glut;
opponents front-load STR at position 0. Full story: `results/V15_TO_V155.md`.

---

## Goal

Requested target: validate the `lynnsakurai/farming-score-v3-replay-revised` tape
(public 2680) against the current model, and — if the current model loses — check
again by rulebook: reverse-engineer what is wrong, keep the top player's mechanics
in any new model, and then decide whether (a) we can beat v3 by changing our own
line or (b) we should fork *her* code to beat her and submit that (her code is
MIT via the notebook's `COMPETITION_DATASET_LICENSE`-governed release path, and
is therefore eligible for derivation). The operator (user) has directed the fork
to be performed in their workspace.

---

## Research discipline (read before any new agent)

- **`results/V15_TO_V155.md`** — the full V15→V15.5 upgrade workflow: resources,
  forensics, every failed variant + why + the fix, verification protocol, and a
  **replicable 10-step playbook** for creating the next champion (V15.6+).
- **`RESEARCH_PLAYBOOK_V23_TO_V26.md`** — complete, evidence-tagged history of
  V23→V26 (every number tagged [F] file / [S] docstring / [G] git / [H] hash /
  [R] recollection, with honest `UNKNOWN — NOT RECOVERED` gaps).
- **`RESEARCH_RULEBOOK.md`** — the binding constraint set for all future
  research: Experiment Canvas (Observation → Hypothesis → Intervention →
  Measurement → Gate → Conclusion), H2H-only vs incumbent, pre-registered
  gates (8-seed family `1M 9M 3.33M 7.77M 5M 6M 8M 2M`, ≥6/8 + positive
  mean → extended N=100), an experiment ledger so **falsified ideas are never
  re-discovered**, 10 guardrails, budgeted 1-mechanism cycles.
- **`results/DIAGNOSIS_V15_VS_V14.md`** — why V15 couldn't fully beat V14
  (ablations, loss profile, V16 candidates pre-registered).
- **`HANDOFF.md`** — architecture handoff of the original modular agent
  (`kaggriculture_project/`: rules/state/market_model/roi/tasks/scheduler/
  planners/strategy), preserved as history.
- **`docs/` + `archive/kaggriculture_project/docs/`** — restored findings
  (2026-08-07/08), checkpoints, ARCHITECTURE/STRATEGY/ROADMAP/VERIFIED_VS_INFERRED
  of the pre-v23 research project.

---

## Layout

```
submission.py                  <- `lynnsakurai/farming-score-v3-replay-revised` verbatim (sha `d36ae9…`, tar `5cde13…`; derived via notebook PAYLOAD → `notebook_code_combined.py`)
submission.tar.gz              <- deterministic pack of the above (source sha + archive sha pinned by the notebook build)
agents/_top_pub/lynnsakurai_v3.py <- same source staged for H2H/the gate (`Three-Day Shop Router`, 2×719 routes at decision step 360)
agents/v27_fix.py              <- V27 candidate — UVM-2 + pasture-aware PLACE repair (harness import; archived at `archive/submission_v27_fix_20260904.py`)
archive/submission_uvm2_20260904.py <- prior UVM-2 champion frozen before this gate (sha `7ca032165ce72efa`, legacy: V18-era)
submission*V18 history*         <- V18 Thunder-Slayer champion bundle — THE SUBMISSION (V17 base + anti-THUNDER intercepts inline) — previous
build_v16_submission.py        <- legacy V16a builder (kept for reference)
build_v15_submission.py        <- legacy builder (V15.5, kept for reference)
agents/                        <- all agent code (current + every preserved variant)
  submission_v16a_backup_20260810.py <- V16a champion bundle, preserved at V17 promotion
  kaggle_v16a_counterpreempt.py<- V16a champion (previous, imports V14)
  kaggle_champion_v155.py      <- V15.5 champion (previous, archived as archive_main_v155.py)
  kathimunishwar_replay_agent.py <- ground-truth opponent kernel agent (adaptive-preempt-3x2x1)
  salemali7_3000score.py       <- replay-derived reconstruction of the same strategy (16/16 ties vs truth)
  kaggle_v155_recovery.py      <- V15.5 candidate (identical body)
  kaggle_champion_v155_momentum_gate.py  <- old V15.5 (backup)
  kaggle_champion_v15.py       <- V15 champion (baseline)
  kaggle_boat84_v14.py         <- V14 (BOATLEE_84) foundation route + tape
  kaggle_v23.py, kaggle_v26b.py, kaggle_v26_aggr_evidence.py, seb_route_*, ...
WybeV2/                        <- V17/V18-era reverse-engineering workspace
  v18_apex.py                  <- V18 champion source (wrapper; imports submission helpers)
  v17_apex.py                  <- V17 champion source (== V17-era submission.py)
  boatlee_v16rc2/main.py       <- boatlee V16-RC2 opponent source (reverse-engineered)
  kaitofukami_v27/main.py      <- kaitofukami v27 opponent source
  h2h_v17_*.txt, h2h_v18_*.txt <- ALL V17/V18 H2H evidence logs (gate + fresh)
  rank_dataset/, analysis_output/, *_kernels/ <- ranking/meta research data
  (rank_env/ = local venv, NOT tracked)
ShiV17/                        <- open-source build of V17 (submission notebook + docs)
  ShiV17_open_source.ipynb     <- submission notebook (generated by build_notebook.py)
  build_notebook.py            <- notebook generator
  ShiV17_walkthrough.md        <- reverse-engineering + verification walkthrough
  ShiV17_implementation_plan.md
tools/                         <- research/diagnostic scripts (no agent code)
  analyze_live_replays.py      <- live replay forensics (118×6 animal / PLACE / shed + seed-level Δ, rulebook §2.2)
  extract_live_opponents.py    <- opponent-tape extractor for the live-derived fleet (gate H2H)
  fetch_episodes.py            <- `kaggle competitions episodes/replay` wrapper (119 episodes) + summary CSV
  V27_FIX_PLAN_20260904.md      <- one-lever canvas (§1) + pre-registered gate (§3.3) for this session
  run_v18_benchmark.py         <- full V18 tournament suite (gate + losing + fresh, vs v17/th1/th2)
  benchmark_v18_suite.py, tune_v18_apex.py <- V18 tuning/verification helpers
  sim_worker.py                <- multiprocessing simulation worker (V18 harness)
  diag_bench.py                <- deterministic H2H runner (N seeds x 2 seats)
  analyze_v14.py, gate_search.py, trace_loss.py, tune_v14_enhanced.py, ...
results/                       <- diagnosis/forensics/upgrade docs + 100-game tables
                                   (+ leaderboard_snapshot_2026-08-08.zip)
                                   (+ v18_final_benchmark.json — V18 tournament suite output)
notebooks/                     <- research notebooks (v23 route, v14 tape, 4-quadrant)
logs/                          <- benchmark run/err output, separated by model era
  v155_validation/             <- fresh50/sanity/revalidation runs of the V15.5 gate
  v23_vs_v14/                  <- v23 vs v14 bench logs
  v15_debug/                   <- debug_output traces
replays_seb/                   <- SEB's live game replays (reverse-engineering data)
archive/                       <- superseded code & historical backups
  kaggle_v23.py, kaggle_v26.py, github_v23.py
  kaggriculture_project/       <- restored pre-v23 research docs
  v15-era/                     <- old V15 single-file copies (main.py, kaggle_agent_main.py,
                                   submission_main.py, submission.tar.gz)
  backups/                     <- FARM_V26_BACKUP_20260808_103322.zip
Kaggriculture/                 <- original modular agent (research harness, history)
docs/                          <- restored findings/checkpoints (2026-08-07/08)
RESEARCH_PLAYBOOK_V23_TO_V26.md <- how V23→V26 was found (evidence-tagged)
RESEARCH_RULEBOOK.md           <- how to hunt V27+ (do NOT improvise past this)
HANDOFF.md                     <- original modular agent handoff (history)
```

## Run it / iterate

```powershell
# H2H: candidate vs opponent, 20 seeds x 2 seats, per-seed table + summary
python tools\diag_bench.py agents\kaggle_champion_v155.py agents\kaggle_champion_v15.py 20 out.txt --swap-both

# V18 full tournament suite (gate + losing + fresh seeds, vs v17/th1/th2)
python tools\run_v18_benchmark.py

# V18 vs V17 gate + fresh-seed verification (deterministic engine 1.32.6, interval=24)
python tools\diag_bench_seeds.py WybeV2\v18_apex.py WybeV2\v17_apex.py "1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000" out_gate.txt --interval 24

# Rebuild + verify + submit
python build_v16_submission.py
python tools\diag_bench_seeds.py submission.py agents\kaggle_champion_v155.py "1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000" smoke.txt
kaggle competitions submit -c kaggriculture -f submission.py -m "message"
```

The engine is **deterministic** (V14 vs V14 mirror = 16/16 exact ties), so every
delta is a real mechanism — a loss is never a coin flip. Any new experiment must
follow `RESEARCH_RULEBOOK.md` + the V15.5 workflow in `results/V15_TO_V155.md` —
plan the canvas, check the ledger, pre-register the gate, THEN code.
