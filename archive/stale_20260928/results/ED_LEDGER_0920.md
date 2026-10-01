# E55 LEDGER — ED "early dump / sell pull-forward" challenger (2026-09-20B)

Challenger: `agents/pub_metav4_ed.py`
Builder: `tools/build_metav4_ed.py` (idempotent; rebuild byte-identical — md5 stable)
Variant md5: `31245757e249bb06a00607edab0678a4` | 6718 lines total | overlay graft = 118 appended lines (86 code lines)
Control md5: `agents/pub_metav4_early.py` = `10f9ecf625db2c1fdf47010d0f666ab0` — **file untouched, 0 spine lines edited**
Raw outputs: `results/ed_gates_0920/` (smoke_full.log, gate8_*.txt, sweep.log)
Status: **NOT SUBMITTED, NOT PROMOTED.** Recommend: KILL.

---

## 1. Evidence read before building

* `results/LIVE_FORENSICS_20260920B.md` — 11 new live losses; 涵哥 −24,593, kwa −2,531, TFC −7,411; dumper fingerprint = 84 orders of `SELL <item> 1000` on schedule {28:×3, 29:×24, 30:×57}.
* `results/live_replays_0920b/_dumper_collision.txt` — our d27-30 realization 65.0k px vs 76.5k at d24-26 prices (涵哥 board); kwa 43.6k vs 51.1k; TFC 22.9k vs 31.7k. Our sell-hour histogram d27-30: `{22: 55, 23: 1028}`.
* Mechanism claimed: the baked tape liquidates ~1090 shed units at d27 h23 plus d28/d29 tranches (`future_sells` pub_metav4_early.py:891 → `_terminal_liquidation` :897, gated `step>=718`), and the dumper family sells into that same window.

## 2. Hypothesis (class: sell-timing, NOT hold-for-reprice)

Empty the shed *before* the window (evenings d24/25/26, hour ≥ 20, sell 1/3 of eligible shed per product, wheat protected by a feed floor) so the tape's later bulk SELLs degrade to engine no-ops, and clear d27/28/29 production daily.
This is the OPPOSITE class of the refuted hold-for-reprice family, and it is the empirical follow-up to the analytic refutation already in memory (`project-sell-timing-overlay-refuted.md`: exact price-impact replay math said +2.0..2.2k, flips none).

## 3. Implementation (`_ED_WINDOW`, appended graft)

```python
_ED_WINDOW = {24:(20,3), 25:(20,3), 26:(20,3), 27:(22,1), 28:(22,1), 29:(22,1)}  # (first hour, shed divisor)
wheat floor = ceil(animals * (30 - day) * 1.2)   # animals = COOP/PASTURE tiles with non-empty 'animal'
per product: free = shed - already-planned-SELLs (- floor if WHEAT); sell ceil(free/share)
orders merged into the parent's market list, same product summed, capped at 10 orders/turn by price*units
```
**Documented deviation from the brief:** the clear-day tranche fires at hour ≥ 22, not 23 — `LAST_ACT_STEP = 718` is d29 h22, so step 719 (d29 h23) is never an acting step and an h23-only gate would silently drop the last clear. Consequence: 6 fires per seat per game (3 evenings + 3 clears) instead of the 3 the brief predicted.

**E53g-class hardening (real bug found in review, fixed before any run):** aggregate telemetry + a global "already fired" set were reset only at `step==0 and player==0`. The bench harness reuses processes and runs the variant on seat 1 in half the games, so the latch would persist and the overlay would silently never fire in later episodes. Now state is **per seat**, reset at that seat's own step 0 (`_ED_ST[seat] = _ed_fresh()`), which also yields per-seat fire counts.

Synthetic-obs preflight in the builder verifies: 1 fire/day inside the window, product merge, wheat floor respected, 10-order cap, same-day latch, pass-through outside the window, per-seat reset.

## 4. SMOKE — PASS (`results/ed_gates_0920/smoke_full.log`)

8 gate seeds × both seat orders, ED vs `pub_metav4_early`, plus 4 champion-vs-champion controls (16 + 4 games).

| law | result |
|---|---|
| wrapper never returns None | `none=0` all 16 games |
| overlay exceptions | `errs=0` all 16 games |
| overlay actually fires | `fires=6` per seat per game, 16/16 games |
| obs[t] POST-action pairing | `pairing_mismatch=0`, `env.steps[i]` ↔ acting step i (offset set `{0}`) |
| wheat feed floor arithmetic | exact on every fire event (`floor == ceil(animals*(30-day)*1.2)`) |
| feed census d12-29 (both seats) | **IDENTICAL** to the champion seat in every game (e.g. d27 13/17, d28 8/17 both sides) |
| money within ±15k of champ seat | max \|delta\| = **+382** |

Per-game ED−champ money: +382, +382, +17, +17, **−43, −43**, +2, +2, **−3, −3**, 0, 0, +6, +6, 0, 0.
Units pulled forward per game: 14, 3, 7, 5, 1, 2, 1, 3 (mean **4.5 units/game**, max 14).

Example telemetry (seed 1000000, both seats):
```
fire s0 d24 h20 +2 orders  2 units animals=17 wheat_floor=123
fire s0 d25 h20 +1 orders  1 units animals=17 wheat_floor=102
fire s0 d26 h20 +2 orders  8 units animals=17 wheat_floor=82
fire s0 d27 h22 +0 orders  0 units animals=17 wheat_floor=62   (parent queue already {'FERTILIZER': 997})
fire s0 d28 h22 +1 orders  3 units animals=17 wheat_floor=41
fire s0 d29 h22 +0 orders  0 units animals=17 wheat_floor=21
```

### Decisive mechanism finding (the premise is falsified at the shed level)
At the trigger hours **the shed is already almost empty** (d24 h20 = 9 units, d25 h20 = 44, d26 h20 = 22 — mostly wheat inside the feed floor), because the tape sells continuously through the day and the standing stock sits in the **field CARRY inventories (40-55 units)**, which `SELL` cannot draw from. The forensics' "~1090 units at hour 23 of day 27" is a **planned** order, not a realized dump: step 671 (d27 h23) shows `planned={'FERTILIZER': 997, 'WHEAT': 1}` → `realised={'FERTILIZER': -8, 'WHEAT': -27}`, money +0 — the engine clamps a SELL to shed contents, so the bulk line is a **no-op sentinel**. There is nothing to pull forward; hence mean |Δ| vs the champion = tens of px, not thousands.

## 5. GATES — all 16/16 files in `results/ed_gates_0920/` (gate8 = 8 seeds × 2 seats, `tools/diag_bench_seeds.py --interval 24`, engine assert 1.32.7 PASS, `Ok:16 Errs:0` everywhere)

| # | matchup | ED W-L-T (game) | seed-level | mean px | control (champ, same seeds) | Δ vs control |
|---|---|---|---|---|---|---|
| 1 | vs champ `pub_metav4_early` | 8-4-4 | 4W/2L/2T | **+45** | n/a (self) | min −43 / max +382 |
| 2 | vs 涵哥_29ee77a6 | 16-0-0 | 8W/0L | +111,884 | +111,887 | **−3** |
| 3 | vs kwa_67f80680 | 16-0-0 | 8W/0L | +102,520 | +102,544 | **−24** |
| 4 | vs tamura_aicon_d45969a0 | 16-0-0 | 8W/0L | +107,697 | +107,704 | **−7** |
| 5 | vs Yanis_Belami_03d5c442 | 16-0-0 | 8W/0L | +106,893 | +106,894 | **−1** |
| 6 | vs THIRD_FARM_CLUB_f5afac52 (live −7,411 board) | 16-0-0 | 8W/0L | +97,262 | +97,264 | **−2** |
| 7 | vs THIRD_FARM_CLUB_21154212 | 16-0-0 | 8W/0L | +54,751 | +54,748 | +3 |
| 8 | vs THIRD_FARM_CLUB_ed81ab50 | 16-0-0 | 8W/0L | +71,665 | +71,642 | +23 |
| 9 | vs THIRD_FARM_CLUB_67d48464 | 16-0-0 | 8W/0L | +100,791 | +96,547 *(ctrl run for this tape: `ctrl_champ_vs_opp_TFC_67d48464.txt`)* | **+4,244** |
| F1 | fleet: vs `pub_demand_timing` | 16-0-0 | 8W/0L | +1,003 | +921 | +82 |
| F2 | fleet: vs `pub_metav4` | 16-0-0 | 8W/0L | +95 | +50 | +45 |

Gate clauses from the plan: gate8-vs-champ passes only on the weak clause (mean +45 ≥ 0, 4L is not >4L; it does **not** clear ≥6W/≤1L — it is 4W/2L at seed level, i.e. a coin-tie inside engine noise). Fleet rule (step-4): **no new losses** — both fleet matchups are 16W/0L, better than control by +82/+45 px. Dumper-family: 6 of 7 tapes move by −24..+23 px = zero effect.

### Baseline correction: the champion self-mirror is EXACTLY +0, not +2,062
A cross-talk figure of "champ-vs-champ gate8 = +2,062 mean margin" circulated while this entry was being written. It is wrong for this harness, and the correction matters because it was used to argue ED "+closes the seat advantage":
* `results/ed_gates_0920/gate8_vs_selfmirror_champ.txt` (run for this entry, same 8 seeds, `--interval 24`): **0 W / 0 L / 16 T, Mean Delta +0, Min +0, Max +0**.
* Independently, the pre-existing `results/mirror_metav4_early_gate4.txt` (4 seeds): 0W/0L/8T, Mean Delta +0.
* The harness is positionally symmetric: every gate file shows swap=0 and swap=1 rows with identical a/b scores, so there is no seat advantage to close.
* Provenance of the 2,062: `results/h20_pub_evgen0917_gate8.txt` line 21 — it is the seed-8000000 delta of `crop_roi30_h20.py vs pub_evgen0917.py` (a different agent pair), repeated identically in the other `h20_*` files.
So ED vs champ is measured against a true 0.0 baseline: +45 mean px with 2 losing seeds is noise-plus-a-negligible-cost, with no offsetting "advantage closure".


### Tape sell-schedule scan (new evidence, decoded from the replay tapes)
Planned `SELL` units per day, d24-29 (bulk = single order ≥100u):
```
涵哥    105, 115,  94, 3171, 24090, 57174   bulk {27:2996, 28:23962, 29:56981}
Yanis   120, 267, 347, 3145, 24076, 57152   bulk {27:2996, 28:23960, 29:56981}
tamura  114, 113,  95, 3125, 24078, 57143   bulk {27:2996, 28:23967, 29:56981}
kwa      69,  84,  76,  102,   117,   166
TFC f5afac52  80, 51, 106, 96, 125, 1159    bulk {29:900}
TFC 67d48464  42, 83,  83,  24,  84,  388
```
So the dumper family really does concentrate on d27-29 — and locally we still beat all of them by ~100k on every gate seed, i.e. **the live collision does not reproduce in the harness** (consistent with the earlier dumper-repro finding). Pull-forward therefore has no local loss to fix, and its own cost is 2 seeds at −43/−3 px.

### The one non-zero result, and why it does not rescue the class
ED vs TFC_67d48464 is +4,244 (positive on 7/8 seeds, +11,371 at seed 1e6) and it is causal (same seed = same world, only the overlay differs; the gain is in *our* bank, opponent unchanged). But ED moved ≤14 units there, so +11.6k cannot be the intended "avoid dumping into a crash" channel — it is a **price-path perturbation** through the shared market curve (an early SELL raises market inventory, changing prices everyone else realizes later). Its sign is tape-idiosyncratic: on the six other dumper tapes the identical perturbation is −24..+23 px. A lever whose sign flips with the opponent's tape is not a promotable edge, and harvesting it would be seeding-lottery fitting (E34/E53b/E54 precedent).

## 6. VERDICT — **KILL** (no gate "failed" in the disqualifying sense; the variant is simply worthless and its premise is dead)

1. Not promotable: gate8 vs the champion is 4W/2L/2T at +45 mean px against a **true 0.0 self-mirror baseline** — statistically a tie, decided by 1-14 units of activity. (Power caveat accepted: 8 gate seeds is thin, so "+45 with 2 tiny losing seeds" cannot even be called a small negative with confidence — the point is that nothing clears the promotion bar, not that the variant is proven harmful.)
2. Zero transferable benefit on the target class: 涵哥/kwa/tamura/Yanis/TFC deltas are −24..+23 px vs the champion's own controls.
3. Root cause is empirical now, not analytic: the d27 h23 "1090-unit liquidation" is a **planned no-op** (`planned 997 → realised 8`, money +0) and the live-season stock that actually gets dumped sits in **field carry**, which `SELL` cannot reach. The overlay has nothing to move.
4. The only measurable effect (+4.2k on one TFC tape) is a shared-price-curve butterfly with an unstable sign — the same failure mode that killed E53b/E53g/E54.
5. Cost: +118 live lines plus market-slot occupation in hours 20-23 of d24-29 that competes with the parent's 10-order cap; the two −px seeds (−43, −3) are consistent with that ordering cost, though 8 seeds cannot prove it either way.

**Open lead worth keeping** (do not build on it without a bigger lever): the market is a *shared* price curve, so a small, well-timed early SELL can move an opponent's — and our own — late realization by ~10k. A deliberate version of that needs the price-impact math in the plan layer (how much inventory the town/shops drain per interval vs the dumper's tranche), not a shed-emptying rule. The live d27-30 price crash remains **unreproducible on these 8 seeds**, so any future sell-timing work must first find a harness world where it happens.

## 7. Disposition of files
`agents/pub_metav4_ed.py` — KEEPER AS DEPRECATED EXPERIMENT, **DO NOT SUBMIT**. Nothing promoted; champion `pub_metav4_early.py` (10f9ecf6) and scout 56387781 unchanged and live.
Tools: `tools/build_metav4_ed.py`, `tools/ed_smoke_0920.py`, `tools/ed_gates_0920.sh` (resumable).
Logs: `results/ed_gates_0920/{smoke_full.log, sweep.log, gate8_vs_champ.txt, gate8_vs_selfmirror_champ.txt, gate8_vs_opp_*.txt (7 dumper tapes), gate8_vs_pub_demand_timing.txt, gate8_vs_pub_metav4.txt, ctrl_champ_vs_opp_TFC_67d48464.txt}` — 12 gate runs + 1 mirror baseline + 1 added control, all `Ok:16 Errs:0`.
(Note: `results/ed_gates_0920/e55_gate8_*` names were never used — the sweep writes `gate8_*`; `smoke.log` is the first, crashed smoke attempt, superseded by `smoke_full.log`. No ED artifacts exist under any other name.)
