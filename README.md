# Kaggriculture Agent — KaggleKaggriculture

Competition agent for **Kaggriculture** (Kaggle `kaggle-environments`). Current
champion: **V15.5 "Dead-Inventory Recovery"** (`agents/kaggle_champion_v155.py`,
bundled as `submission.py`). Fully self-contained single-file agents, zero
runtime dependencies.

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

### Era 4 — V15.5: the current champion (local, fully verified)

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

Side experiments preserved (not promoted): `kaggle_v155_t90/t120/t150/t180.py`
(price-threshold capselllate variants), `kaggle_v14_tweaked.py`,
`kaggle_v14_v26style.py`, `kaggle_v26_aggr_evidence.py`, `seb_route_v1.py`,
`kaggle_anas.py`, `kaggle_flex.py`, `kaggle_kaito_v23.py`, `kaggle_v22_romanrozen.py`.

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
submission.py                  <- V15.5 champion bundle — THE SUBMISSION
build_v15_submission.py        <- rebuilds submission.py (champion + V14 inline)
agents/                        <- all agent code (current + every preserved variant)
  kaggle_champion_v155.py      <- V15.5 champion (current, imports V14)
  kaggle_v155_recovery.py      <- V15.5 candidate (identical body)
  kaggle_champion_v155_momentum_gate.py  <- old V15.5 (backup)
  kaggle_champion_v15.py       <- V15 champion (baseline)
  kaggle_boat84_v14.py         <- V14 (BOATLEE_84) foundation route + tape
  kaggle_v23.py, kaggle_v26b.py, kaggle_v26_aggr_evidence.py, seb_route_*, ...
tools/                         <- research/diagnostic scripts (no agent code)
  diag_bench.py                <- deterministic H2H runner (N seeds x 2 seats)
  analyze_v14.py, gate_search.py, trace_loss.py, tune_v14_enhanced.py, ...
v15_losses/                    <- forensics scripts, probes, tape dump, ALL H2H evidence
results/                       <- diagnosis/forensics/upgrade docs + 100-game tables
                                   (+ leaderboard_snapshot_2026-08-08.zip)
notebooks/                     <- research notebooks (v23 route, v14 tape, 4-quadrant)
logs/                          <- benchmark run/err output, separated by model era
  v155_validation/             <- fresh50/sanity/revalidation runs of the V15.5 gate
  v23_vs_v14/                  <- v23 vs v14 bench logs
  v15_debug/                   <- debug_output traces
replays_seb/                   <- SEB's live game replays (reverse-engineering data)
seb_analysis/                  <- SEB/v14 strategy data + reports
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

# Fresh-seed robustness (seeds never used in tuning)
python v15_losses\diag_bench_offset.py agents\kaggle_champion_v155.py agents\kaggle_champion_v15.py 40 out_ext.txt 40

# Rebuild + verify + submit
python build_v15_submission.py
python tools\diag_bench.py submission.py agents\kaggle_champion_v15.py 10 smoke.txt --swap-both
kaggle competitions submit -c kaggriculture -f submission.py -m "message"
```

The engine is **deterministic** (V14 vs V14 mirror = 16/16 exact ties), so every
delta is a real mechanism — a loss is never a coin flip. Any new experiment must
follow `RESEARCH_RULEBOOK.md` + the V15.5 workflow in `results/V15_TO_V155.md` —
plan the canvas, check the ledger, pre-register the gate, THEN code.
