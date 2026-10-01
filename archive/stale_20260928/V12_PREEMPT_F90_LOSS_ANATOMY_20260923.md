# V12 preempt_f90 — Fresh-loss anatomy vs V11 (2026-09-23)

Engine: `kaggle-environments==1.32.7`, `townCenterSellInterval=24`, `SEEDS_FRESH = range(30000000, 30016000, 1000)`,
both seats per seed. Candidate `agents/pub_v57_apex_v12_preempt_f90.py` vs `agents/pub_v57_apex_v11_dump.py`.
Artifacts: `results/f90_lossmine/` (`h2h_fresh.log/.json`, `trace_<seed>_<swap>.json`, `report.log`),
scripts `scratch/f90_lossmine_0923_{h2h,anatomy,report}.py`. Instrumented traces reproduce the gate
scores exactly (verified on all 5 loser-seat games).

## 1. Per-seed delta table (f90 − V11; seatA = f90@p0/v11@p1, seatB = f90@p1/v11@p0)

| seed | f90@p0 | v11@p1 | f90@p1 | v11@p0 | mean delta |
|---|---|---|---|---|---|
| 30000000 | 129865 | 129671 | 129865 | 129671 | **+194.0** |
| 30001000 | 65704 | 65699 | 65704 | 65699 | +5.0 |
| 30002000 | 111177 | 111016 | 111177 | 111016 | +161.0 |
| 30003000 | 83611 | 83603 | 83611 | 83603 | +8.0 |
| 30004000 | 110783 | 110774 | 110783 | 110774 | +9.0 |
| **30005000** | 113290 | 113291 | 113290 | 113291 | **−1.0** |
| 30006000 | 113503 | 113208 | 113503 | 113208 | +295.0 |
| **30007000** | 97492 | 97494 | 97492 | 97494 | **−2.0** |
| **30008000** | 63331 | 63412 | 63409 | 63334 | **−3.0** (seat ±~80) |
| **30009000** | 65326 | 65451 | 65443 | 65328 | **−5.0** (seat ±~120) |
| 30010000 | 97320 | 96394 | 97320 | 96394 | +926.0 |
| 30011000 | 102722 | 102715 | 102722 | 102715 | +7.0 |
| **30012000** | 134862 | 134863 | 134862 | 134863 | **−1.0** |
| 30013000 | 142606 | 142597 | 142606 | 142597 | +9.0 |
| **30014000** | 88708 | 88710 | 88708 | 88710 | **−2.0** |
| **30015000** | 133047 | 133052 | 133047 | 133052 | **−5.0** |

9W/7L, mean +99.7 (reproduces the gate exactly). The 7 losses total **−19** against +1,620 of wins;
each loss is ≤ 0.004% of score. For 14/16 seeds both seats score identically → zero cross-seat market
interaction; the layer's effect is intra-agent, not competitive.

## 2. Anatomy of the 3 worst losers (f90@p0 traces; V11 = same spine)

**Revenue by item is identical to the dollar for every item except WHEAT** on all three seeds.
Preemption telemetry: `preempts=6, repay_units=36` — every fire is WHEAT.
FERTILIZER@90 never fires (h23 shed ≤ 10 and price ≤ 76 wherever shed≥6: step 263 px 76, step 359 px 55-56);
MILK/WOOL/STRAWBERRY never hold ≥6 shed units at hour 23 (sold same-day).

| seed | WHEAT f90 | WHEAT v11 | dRev | other items | discards f90/v11 | gap<-1000 |
|---|---|---|---|---|---|---|
| 30009000 | 415u@40.2 = 16,700 | 418u@40.3 = 16,835 | **−135** | 0 | 8u / 8u identical (d25: FERT2+WOOL6) | never (max −135) |
| 30015000 | 370u@36.8 = 13,624 | 370u@36.8 = 13,629 | −5 | 0 | 0 / 0 | never |
| 30008000 | 259u@36.4 = 9,429 | 259u@36.4 = 9,432 | −3 | 0 | 0 / 0 | never |

Preempted wheat prices (6 units/fire, hours: steps 263/287/431/455/479/503):
30009000 @39-44, 30015000 @38-41, 30008000 @38-39. The debt repay cropped the parent's *intraday*
(hour 2-13) wheat orders, which on these seeds executed at **the same price ±1** → net −3…−5.
Sell-hour histograms: f90 shifts ~36 wheat units from hours 2-13 into hour 23; V11 hour-23 wheat = 3-10u.

- **30009000 is the only real mechanism loss**: f90 sold **3 fewer wheat units total (415 vs 418)** —
  the pre-then-repay cycle leaked 3 units out of the final liquidation → −$123 of the −$125 seat-0 delta.
  Seat B (+115) and the 3-unit leak trade places; mean −5.
- 30008000/30009000 are the only seat-asymmetric seeds: commit interleaving (player-0-before-player-1 per
  unit in `_process_market`) swings ±80-125 — a coin-flip on seat, not on strategy.

Winner comparison: **30010000 (+926)** — 10 preempts, wheat fires @42-45 (steps 383-647): WHEAT +240,
STRAWBERRY +690, WOOL +94. **30006000 (+295)** — preempts @42-44. Every material win preempts wheat at
price ≥ 42; every loss preempts at 38-41 or leaks volume.

## 3. Classification of the 7 losing seeds

| class | count | seeds |
|---|---|---|
| (a) withheld sell V11 got at good price | 0 | — |
| (b) f90 self-crashed a price | 0 | — |
| (c) shed-cap discard differential | 0 (discards identical 8u/8u on 30009000, 0 elsewhere) | — |
| (d) production/timing divergence | 0 (every non-WHEAT revenue bit-identical) | — |
| (e) mirror coin-flip ≤1% | **7** | 30005000, 30007000, 30008000, 30009000, 30012000, 30014000, 30015000 |

Within (e): 5 are seat-invariant price-neutral shuffles (|Δ| ≤ 5); 2 (30008/30009000) are seat commit-order
flips; 1 sub-defect is real — the 3-unit WHEAT volume leak on 30009000 (debt repay truncated a parent
order below what the shed could still place, leaving ~$123 unsold).

## 4. What the data points at

Not a production graft, not a per-item floor split across WOOL/MILK/STRAWBERRY (those never hold ≥6
shed units at hour 23 — the fires are 100% WHEAT in every seed played). The winning-vs-losing split is
pure WHEAT preemption price: fires at **≥42 win (+240…+926)**, fires at **38-41 are net-zero-to-negative
(−1…−135)**. Concrete construction for the next candidate:
1. **Raise the WHEAT preemption floor from 30 to 42** (kills the 38-41 no-value fires that produce all
   seven Fresh losses; preserves the ≥42 fires that produced the +926/+295/+194/+161 wins).
2. **Fix the volume leak**: only preempt if the parent has ≥sell_qty more scheduled WHEAT SELL units
   after this step (or exempt the days-28-30 dump window from repay-cropping), so repay never strands
   shed units (30009000: 415 vs 418 = −$123).
3. FERTILIZER@90 and MILK/WOOL/STRAWBERRY@140 are dead code (never fire) — retire or reprice them
   against hour-23 shed availability before attributing any gate movement to them.
