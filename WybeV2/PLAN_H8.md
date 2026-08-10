# WybeV2 H8 — Canvas & Ledger (Experiment per RESEARCH_RULEBOOK §1-§4)

Date: 2026-08-09 | Project: WybeV2 (HS-derived agent) | Base: submission_v63_backup.py
Supersedes: the v7 patch loop (dead end, see ledger row below).

---

## LEDGER — previous experiments (rows so far)

| ID | hypothesis | mechanism lever | regime | N | mean Δ | verdict | traces | date |
|---|---|---|---|---|---|---|---|---|
| H1 | "v7 pasture cap ties pasture to pending animals" | pasture build gate | sanity vs PASS | 3 | n/a (29/12/10) | **REJECTED — REGRESSION, REVERTED** | debug_v6_collapse.txt | 08-09 |
| H2 | "v7 = v6.3 + HS animal pipeline + HS sell discipline" (multi-lever) | opening, animals, sell gates, targets (≥4 levers) | sanity vs PASS | 3 | n/a (29/12/10) | **REJECTED — G3 violation, unattributable, abandoned** | debug_v6_collapse.txt | 08-09 |
| H0 | v6.3 baseline (no animals, wheat+STR engine) | — | sanity vs PASS | 3 | v6.3 = 22,274/16,987/24,257 (mean 21,173) | **ACCEPTED as base** [F] | sanity_v7.py output | 08-09 |
| **H8** | **"v6.3 dies at ~21K because it has NO animal income loop; HS animal pipeline lifts sanity above the v6.3 mean"** | opening SHEEP×2 + pasture build + PICKUP/PLACE/FEED/CARE + FERT drip (D2+, any price, chunk 4) + WOOL (≥140) + feed buy cap 3/day | sanity vs PASS | 3 | v8 = 28,123/26,217/31,952 (mean **28,764** vs 21,173, Δ+7,591) | **ACCEPTED — H9 next: H2H vs V16a (8-seed family, ≥6/8 + positive mean)** | sanity_H8_v8.txt, inst_H8_v8_loop.txt | 08-09 |
| **H9** | **"v8 animal pipeline closes the gap to V16a"** | H2H vs V16a, frozen 8-seed × 2 seats, interval=24 (scoring config) | H2H gate (≥6/8 + positive mean) | 16 | **0W/16L, mean Δ −122,482** (v8 avg 22,112 vs V16a 144,594; min −140,253, max −69,932) | **REJECTED — decisive. 6.5x production gap, not sell-timing. v6.3/v8 line abandoned as competitive; pivot to top-1/top-2 strategy implementation** | h2h_H9_v8_vs_v16.txt, PLAN_H9.md | 08-09 |

Rulebook note: the "880/1529/873" numbers in earlier session notes were [R]-recollection and
FAILED re-verification (29/12/10) — treated as never having existed (G10).

---

## EXPERIMENT CANVAS — H8 (this cycle)

Observation (all [F], file-verified today):
- v6.3 (no animals): 22,274/16,987/24,257 vs PASS. Healthy money curve (2.5K→18K), ~50 plants, weeds ≤16.
- v7 (animals + multi-lever): 29/12/10 vs PASS. Money collapse (3,000→616→54→7), shed WHEAT piles to 82
  with no SELL, weeds explode 2→41 by D27, animals escape.
- HS ground truth (30 replays, deep_hs_full.txt [F]): opening = 3 HIRE + SHEEP×4 + COW×1 + MELON×5 +
  WHEAT×5 (+CARROT 1 on step 2) ≈ all-in to $14 by D1. Survival = FERTILIZER drip sells from D2
  (4-16/day), WOOL from D6 (15), MILK from D8, MELON waves D10(24)/D20(18), STR wave D14-24 (26-30/day),
  WHEAT mega-dump D26-28 (34+52+162). Feed wheat bought 1-4 units/step (306/game avg). 281 hires.
  3 quads only (NE D7, SW D11, never SE).

Hypothesis (ONE mechanism): **v6.3 dies at ~21K because it has NO animal income loop.
Adding the HS animal pipeline (sheep D0 → pastures → place → feed/care → FERT drip D2 + WOOL D6)
on top of the FROZEN v6.3 crop engine lifts sanity vs PASS above the v6.3 mean (21,173).**

Intervention (EXACTLY ONE mechanism): add animal pipeline ONLY. Everything else stays v6.3:
- v6.3 crop engine byte-identical: _plant_choice, _str_target, sell discipline for crops, buy seeds/land/hire.
- NEW: opening adds SHEEP×2 (HS runs 4+1 cow; a 2-sheep stake is the smallest falsifiable version,
  cost $1000, leaves the v6.3 engine funded — the v7 lesson: all-in opening + engine starving = death).
- NEW: pasture build (shed_animals>0 → build), PICKUP/PLACE/PLACE-routing, FEED/CARE, FERT drip sell
  (gate: any price, chunk 4, from D2 — HS sells fert even at low cash), WOOL sell (gate ≥140 or endgame).
- Feed wheat: buy 1-4/day when shed wheat low (HS cadence), NEVER a 20-bulk buy (v7 overspend suspect).

Measurement: 3-seed sanity vs PASS (1000000, 9000000, 3330000). Success = every seed > 8,000 AND
mean ≥ v6.3 mean (21,173). Also record per-step SELL/BUY/money on seed 1000000 for the loop check.

Gate (pre-registered): vs PASS on the 3 seeds — PASS = all 3 > 8,000 and mean ≥ 21,173.
Then (next cycle, H9) H2H vs V16a on the frozen 8-seed family (≥6/8 + positive mean) — NOT this cycle.

Conclusion: **GATE PASS (2026-08-09, [F]).** v8 = 28,123/26,217/31,952 vs PASS
(mean 28,764 ≥ 21,173; all > 8,000). Δ+7,591 vs v6.3 base.
Loop check (inst_H8_v8_loop.txt, seed 1000000 [F]): SHEEP×2 bought D0, 2 pastures
built D0-D1, FERT drip 28 units from D2, WOOL 33 units from D14, feed buys capped
(12 total — NO v7 runaway; shed WHEAT spikes 74 are harvested inventory, sold same
day), money curve 3K→24K. One sheep escaped by D2 (feed-latency: FEED pri 25 loses
row-sweep to crop WATER pri 5 while units busy — surviving sheep carries the loop).
H9: H2H vs V16a on frozen 8-seed family (≥6/8 + positive mean), then feed-priority
fix if H2H shows the escape costing more than the feed tax.

---

## Build discipline for this cycle (rulebook §5 guardrails)
- G3: ONE lever (animals). No wheat-bank dump, no STR-38, no melon waves this cycle — those are H9+ cycles.
- G8: every run writes to disk (sanity_H8_*.txt).
- G10: every number tagged [F] from today's runs; no session-recollection numbers.
- Instrument before hypothesizing: the v7 collapse mechanism is verified by the existing trace + the
  new instrumented run BEFORE any build decision (rulebook §2.2).
