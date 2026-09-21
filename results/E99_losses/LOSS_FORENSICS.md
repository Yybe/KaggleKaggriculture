# E99 LOSS FORENSICS — 6 big E94 losses + 1 Apex V1 loss (2026-09-21)

Inputs: `results/E99_losses/episode-<id>-replay.json` (kaggle CLI, all 31–35 MB, valid JSON).
Per-episode artifacts: `<ep>/ours_tape.json`, `<ep>/opp_tape.json` (tools/both_tapes.py),
`<ep>/tapediff.txt` (tools/rawtape_diff.py), `<ep>/daycurve.txt` (tools/e99_daycurve.py,
per-day money for both seats — ground truth; reward == final money), `<ep>/realized2.txt`
(tools/e99_realized2.py, holdings-delta realized sell attribution — approximate: it
undercounts same-step harvest→sell, and `tools/revenue_forensics.py` output is NOT usable
for endgame because it face-values 999-qty dump orders).

We are seat 1 (Shivam_2212) in all 7 episodes. All numbers below are from the artifacts.

---

## Per-episode mechanism summaries

### 111672968 — opp "offhand" (sid 56428201), 101,413 vs 122,321 (−20,908)
**Class A: step-34 crew stall.** Our farmer+ALL hands emit PASS from step 34 through step
48 (15 consecutive empty field steps; resume step 49 with PICKUP WHEAT 4 + 4×HIRE). Opp
executes the scripted `BUILD_PASTURE + WATER` at step 34 and never stalls (1 empty step in
34–71). Total field actions steps 24–71: ours 105 vs opp 143. Day-money delta opens early
(d8 +1,551 opp) and compounds ~+700–1,000/day through d27 (+19,271); the opp's d26–29
999-qty liquidation dump (SELL WHEAT/CARROT/MILK/EGG/WOOL/FERT 999 at steps 697–718) adds
only ~1.6k of the final 20.9k — we also end with an empty shed (END holdings: 2 seeds).
Opp tape steps 24–40 and 84–91 are step-for-step IDENTICAL to the opps of 111645900 and
111604665 → same kernel; steps 84–91 match the ledger's verbatim Gluzdov "One More Wheat"
opening fingerprint (HARVEST@85/88, BUILD_PASTURE@89). Mid-game stream diff: opp sells
MILK 125 vs our 93, STRAWBERRY 169 vs 140 (d18–25); BUILD_PASTURE 14 vs 13.
Shop world: BAKERY/BRUNCH_SPOT/ICE_CREAM_SHOP/PET_CAFE/SMOOTHIE_SHOP.

### 111645900 — opp "JinboWang" (sid 56426176), 112,372 vs 132,672 (−20,300)
**Class A: step-34 crew stall** — identical fingerprint: 15 empty field steps 34–48,
resume 49; opp BUILD_PASTURE+WATER at 34; field acts 24–71: 105 vs 148. Opp histogram is
otherwise a near-exact mirror of ours in all four windows (same HIRE 76/59/87/43, same
PLANT/WATER counts, BUILD_PASTURE 18 vs 17) → same-spine sibling playing the correct
step-34 branch. Delta opens d6–8 (+737/+1,477), compounds to +20,703 by d28. Opp
mid-game edge again MILK (125 vs 94) and STRAWBERRY (177 vs 147), d18–25.
Shop world: BAKERY/BRUNCH_SPOT/ICE_CREAM_SHOP/SMOOTHIE_SHOP/YARN_STORE.

### 111594513 — opp "Ebi" (sid 56386266), 94,460 vs 111,857 (−17,397)
**Class C: bulk wheat round-trip arbitrage + milk volume.** We LEAD by up to 13,499
(d12) and are still ahead at d17 (+5,841); the flip happens d18–d26 (−5,841 → +15,319).
Ebi runs a massive WHEAT buy-low/sell-high trade: BUY_PRODUCT:WHEAT 2,045 (d12–17) +
2,992 (d18–25) + 1,421 (d26–29) ≈ 6,458 units bought vs SELL:WHEAT 2,003+2,952+1,665 ≈
6,620 sold — in the same world our agent trades almost zero wheat (BUY_PRODUCT:WHEAT 4).
Ebi also outsells us MILK 153 vs 102 (d18–25) with 9 cows on 11 pastures (vs our 8/14),
waters far less (297 vs 398, d18–25) and frees crew for trading; realized MILK 84 u
@187.5 vs our 21 u. Net-gain flips exactly when the arb scales (d18: +8,890 vs our +612).
Ebi's known opp_score 2,769.0 (results/E98F/live_eps/opp_forensics.json) — a top-tier
opponent. Shop world: BAKERY/BRUNCH_SPOT/ICE_CREAM_SHOP/PET_CAFE/PIZZA_SHOP.

### 111604665 — opp "A. R. SEKKAT" (sid 56421005), 105,127 vs 118,123 (−12,996)
**Class A: step-34 crew stall** — third instance of the identical fingerprint (15 empty
steps 34–48, resume 49; opp BUILD_PASTURE+WATER@34; field acts 105 vs 143; opp script
steps 24–40/84–91 identical to offhand/JinboWang → same OMW-family kernel). All four
day-windows otherwise mirror (HIRE 77/59/93/43 both sides; PLANT/WATER/FERTILIZE equal).
Delta opens d8 (+1,179), grows linearly ~+400–1,000/day to +12,996. Stream diff: opp
MILK 63 vs 50 (d26–29), EGG 57 vs 46. Shop world: BRUNCH_SPOT/FARMERS_MARKET/PIZZA_SHOP/
SMOOTHIE_SHOP/YARN_STORE.

### 111612464 — opp "Crop Dustas" (sid 56418088), 107,892 vs 117,390 (−9,498)
**Class D: fertilizer-intensive crop grower.** We lead through d18 (−1,132 at d18); opp
out-nets us 6.2k/9.1k/9.5k on d18/19/20 vs our 0.7k/5.0k/5.9k and never gives the lead
back. Opp archetype: BUY_PRODUCT:FERTILIZER 51+82+47 = 180 units (ours 8+41+23 = 72),
FERTILIZE 51/77/25 (ours 23/72/22), DIG 34 in d18–25 (ours 21), only 5 cows + 9 pastures
(ours 8 + 14), sells STRAWBERRY 210 (d18–25, ours 174) + TOMATO 33/78. Notably the OPP
is the one with a slow opening here (19 empty field steps in 34–71; no OMW script) — we
lost to mid-game input intensity, not opening. Our day-18 net collapse (+706) coincides
with our BUY_LAND + wage day. Shop world: BRUNCH_SPOT/FARMERS_MARKET/ICE_CREAM_SHOP/PIZZA_SHOP.

### 111596738 — opp "sue124" (sid 56401171), 106,305 vs 111,890 (−5,585)
**Class A′: the literal step-34 DIG pasture-defer defect.** Opp is a step-by-step MIRROR
of our own agent (steps 33, 35–39 identical; identical 1,364/1,365-unit wheat arb d12–17;
all four window histograms within ±9) — same r78u/OMW/pipe16 lineage — with ONE decisive
difference: **step 34 hand1: ours = DIG on the temp-wheat tile, opp = BUILD_PASTURE**
(pasture restore deferred; our END holdings include an unsold **COW: 1** that sat in shed,
exactly the ledger's ep111482825 "8th COW sits in shed 27 days" fingerprint). Realized
revenues are near-identical (19,841 vs 19,552) — the 5,585 gap is the extra pasture
(d0–11 BUILD_PASTURE 12 vs 11) compounding into MILK 107 vs 98 / STRAWBERRY 173 vs 168
(d18–25) plus the shed cow. Delta stays ≤ +2.6k through d18, opens d19–d29. Known
opp_score 2,640.5. Shop world: BAKERY/BRUNCH_SPOT/FARMERS_MARKET/ICE_CREAM_SHOP/PET_CAFE/
PIZZA_SHOP/YARN_STORE.

### 111662271 — opp "alban" (sid 56433319), Apex V1, 122,619 vs 124,092 (−1,473)
**Class B: settlement front-run race between near-identical kernels.** Only 49/720 steps
diverge. First divergence is step 1: alban BUY_PRODUCT WHEAT 20 + SELL WHEAT 15 vs our
BUY 5 — the ledger's noted OMW "step-0 wheat buy/sell tweak". Field scripts identical;
divergences are market-order timing shifts of 1–3 hours. Decider is day 28 (steps
689–693): alban sells WOOL 15 at h17 (px 177→151, +2,350), MILK 8 at h18, STRAWBERRY 20
at h20 (px 141, +2,557); Apex sells the SAME items 1–3 hours later into the post-dump
price (WOOL 12 @102, STRAWBERRY 20 @64) — day-28 net delta +1,473 = the whole final
margin. Day-money delta is ±8 through d21 and −26..−93 (OUR lead) at d22–25 before the
flip. This is OMW's `front_run` layer (see agents/pub_e80_omw.py line 233: "front_run —
sell before the opponent's scheduled SELL"), which our clean builds do not carry.
Shop world: BRUNCH_SPOT/FARMERS_MARKET/ICE_CREAM_SHOP/SMOOTHIE_SHOP/YARN_STORE (wool world:
both sides SELL WOOL 203–210 d18–25, 17 sheep).

---

## Cross-episode loss-class taxonomy

| Class | Mechanism | Episodes | Margins | Total |
|---|---|---|---|---|
| A | Step-34 crew PASS stall (15 steps, 34–48; opp scripts BUILD_PASTURE+WATER@34) | 111672968, 111645900, 111604665 | −20,908 / −20,300 / −12,996 | −54,204 |
| A′ | Step-34 DIG-on-temp-wheat, pasture defer + shed COW (ledger ep111482825 class) | 111596738 | −5,585 | −5,585 |
| C | Bulk WHEAT round-trip arbitrage (~6.5k units) + milk volume, flip d18+ | 111594513 | −17,397 | −17,397 |
| D | Fertilizer-intensive strawberry/tomato grower (180 fert buys, DIG-heavy), flip d18–19 | 111612464 | −9,498 | −9,498 |
| B | Endgame settlement front-run race vs mirror kernel (sell 1–3 h earlier into peak px) | 111662271 (Apex) | −1,473 | −1,473 |

Class A+A′ = **4 of 6 E94 big losses, −59,789 of the −86,684 big-loss total (69%)**.
Recurring fingerprint across class A: identical early money curves (days 0–5: 22/1, 198/369,
786/574…), delta first opens d6–8 (+577…+1,551), linear compounding ~+500–1,000/day,
opp mid-game MILK +30% and STRAWBERRY +15–20%, opp BUILD_PASTURE = ours+1. The three
class-A opponents are the SAME kernel (identical step-24–40 and 84–91 scripts) of the
Gluzdov "One More Wheat" family; sue124 is our own lineage with the step-34 branch fixed.
NOT observed as loss mechanisms: land buys (BUY_LAND 2–3 both sides everywhere), hire
intensity (±3), TOMATO/PIZZA double-block (tomato sales symmetric; PIZZA_SHOP present in
4/7 worlds on both sides), endgame bulk dump per se (we also empty our shed; dumps move
the margin only ~0.6–1.6k).

---

## Pasture-defect (step-34 DIG pasture-defer) verdict

**CONFIRMED as the dominant loss class, with an important caveat on the fix.**
- Direct tape evidence: 111596738 step 34, ours `[['PASS'],['DIG'],['WATER']]` vs opp
  `[['PASS'],['BUILD_PASTURE'],['WATER']]` + unsold COW:1 in our end shed = the exact
  ep111482825 fingerprint (LEDGER_20260921.md lines 781–787, 996).
- Escalated variant: in 111672968/111645900/111604665 the step-34 branch fails into a
  15-step whole-crew PASS stall (steps 34–48; market arb orders keep flowing; resume at
  step 49), pasture count ends 13/17/10 vs opp 14/18/11.
- **Caveat:** in ALL 7 episodes `tiles[4][2]` at step 29 still holds day-0 WHEAT
  (PLANT/WHEAT/planted_day 0), i.e. farmer-john's `_ow_guard_opening` precondition
  (`step==29`, convert hand2 WATER→BUILD_PASTURE iff tile(4,2) lacks day-0 wheat —
  agents/pub_e98_fjws.py lines 6678–6697, assert in
  kernels_pulled/extracted_agents/farmer-john_all_cells.py lines 7947–7948) would NOT
  fire in any of these worlds. The 12-line guard as written is necessary but not
  sufficient: the graft must fire at the **step-34** decision (hand1 DIG→BUILD_PASTURE)
  and include a stall-breaker for the crew-wide PASS state (steps 34–48), or replicate
  the guard's validity check against the tile/condition that actually breaks at step 34
  in these worlds.

---

## Apex V1 rating verdict (1836.6 despite 22W/1L)

From results/APEX_live_eps/summary.json (24 rows, all createTime 2026-09-21 14:25–15:54Z):
- 22 wins, 1 loss (111662271, −1,473), 1 row still null/validating (ep 111650978).
- Win margins (ours−opp): min +1,800; median **+11,322**; mean +24,931; max +130,530.
  13 of 22 wins ≥ +10k; only 2 wins < +5k. **Apex wins BIG, not small.**
- Therefore 1836.6 is NOT explainable by tiny margins or by the single −1,473 loss.
  Remaining explanations, in order of plausibility: (1) rating snapshot lag/convergence —
  all 24 episodes fell in a 90-minute window and Kaggle sim ratings converge over many
  episodes (E94 needed ~67 eps to reach 2359.4, ~103 for 2712.4); (2) at least one
  episode still validating (111650978 null) — validation-phase episodes don't accrue
  rating; (3) the CLI submissions endpoint 403'd, so the score could not be re-verified
  live. Action: re-pull the submission score after ~50–100 more episodes before drawing
  any strength conclusion. The only real on-tape defect found in Apex is the day-28
  front-run race loss (Class B), which is a queue-timing gap, not an overlay bug: the
  overlay liquidated the right items on the right day, 1–3 hours too late.

---

## Opponent kernel-family fingerprints (tape-level, first-40-step comparison)

| Episode | Opp (sid) | Opening fingerprint | Family verdict |
|---|---|---|---|
| 111672968 | offhand (56428201) | steps 24–40 & 84–91 script identical to the other two class-A opps; BUILD_PASTURE@34, HARVEST@85/88+BUILD_PASTURE@89 walk; mirrors our HIRE 76/plant script | Gluzdov **"One More Wheat"** family (ledger E80/E94 verbatim match) |
| 111645900 | JinboWang (56426176) | same as above | same OMW-family kernel |
| 111604665 | A. R. SEKKAT (56421005) | same as above | same OMW-family kernel |
| 111594513 | Ebi (56386266) | step-25–33 sparse single-worker script (NOT OMW); BUY_SEED CARROT 26/TOMATO 5 opening; from d12 huge BUY_PRODUCT WHEAT ↔ SELL WHEAT cycles | private **wheat-arb trader** variant; closest public relative = "…and-the-wheat-seller" lineage (E98 fjws) but far more aggressive |
| 111612464 | Crop Dustas (56418088) | own slow opening (19 empty steps 34–71), heavy BUY_PRODUCT:FERTILIZER from d12, DIG-heavy | private **fert-intensive grower**; no match in kernels_pulled/extracted_agents set |
| 111596738 | sue124 (56401171) | step-by-step mirror of OUR tape (same 1,364-unit wheat arb, same HIRE/plant/water counts) with BUILD_PASTURE@34 | our own **r78u/OMW/pipe16 lineage** with the step-34 guard fixed (farmer-john/OW-guarded variant or upstream OMW) |
| 111662271 | alban (56433319) | 49/720 divergent steps; step-1 BUY WHEAT 20+SELL 15 tweak; sells 1–3 h earlier at settlements | OMW-lineage sibling with **step-0 tweak + front_run queue layer** (pub_e80_omw.py:233) |

---

## Mechanisms worth grafting onto our base (ranked by evidence)

1. **Step-34 pasture guard + crew-stall breaker** (fix class, not opponent mechanism).
   Evidence: 4/6 big E94 losses, −59,789 (69% of big-loss total); sue124 — our own spine
   with only this branch fixed — beat us by 5,585 with otherwise identical realized
   revenue. Source: farmer-john `_ow_guard_opening` (agents/pub_e98_fjws.py:6678–6697),
   relocated/extended to step 34 (hand1 DIG→BUILD_PASTURE) plus a fallback that breaks
   the steps-34–48 all-PASS state. Gate on the three stall worlds (seeds 1073572348,
   2034928249, 1587058364) + seed 1898931754.
2. **Settlement front-run / earlier cash-sale promotion** (OMW `front_run`, pub_e80_omw.py:233;
   also E98's "market-queue hole-packing"). Evidence: the entire Apex −1,473 margin is
   day-28 h17–21 price impact (WOOL 177→102, STRAW 141→64 between opp's and our
   identical-size sells); alban = mirror kernel + this layer. Cheap, local, endgame-only;
   interacts with the Apex overlay so gate Apex+front_run vs Apex.
3. **Wheat round-trip arbitrage scaler** (Ebi). Evidence: ~6,458 bought / ~6,620 sold
   d12–29 drove a 13.5k-lead → 17.4k-loss flip from d18; our spine already arbitrages in
   worlds where the signal fires (1,364/1,432 in 111596738) but stood down in Ebi's world
   — so this is a world-coverage/threshold extension of an existing mechanism, likely
   small delta. Verify margin per unit (buy/sell spread net of price impact) before graft.
4. **Step-1 wheat buy/sell tweak** (alban BUY 20+SELL 15 vs our BUY 5). Evidence: first
   divergence of a 49-step-divergent mirror; ledger already notes it as OMW's differing
   step vs r78u (LEDGER_20260921.md:624). Tiny, zero-risk to evaluate.
5. **Fert-intensive strawberry/tomato overlay** (Crop Dustas). Evidence: 180-unit fert
   buying + FERTILIZE 77 + DIG 34 flipped a 7.1k deficit into a 9.5k win from d18.
   Ranked last because it is a full strategy axis (conflicts with our 14-pasture herd
   build) and the E57c/TOM20 ledger history shows demand-conditional crop doubling has
   already been gate-refuted once on our spine; only worth revisiting as a world-conditional
   (PIZZA_SHOP+FARMERS_MARKET) overlay.

---

## UPDATE 2026-09-21 (post-fix): A′ caveat RESOLVED — E99 gated KEEP

Root cause was NOT the step-29/34 tile branch: on repro seed 1898931754 a WEED spawns
at (4,2) st24; `_weed_repair` correctly queues the tape's BUILD_PASTURE and DIGs the
weed, but the replay branch only fires on no-op tape acts — the next tape act is a MOVE,
so the queue is dropped and the pasture lands 54 steps late (st89 vs st35).
Fix = one 6-line branch in `_weed_repair` (replay queued BUILD_PASTURE immediately when
its tile is None and the unit still stands on it): agents/pub_e99_pasture_fix.py
(md5 92fde71c), built by tools/build_e99_pasture_fix.py from E94 md5 398eadad.
Gate: std 8 seeds × 2 swaps = 16/16 exact ties (zero regression); defect seed swap1
same-seat +4,838 (111,154 vs 106,316); tile trace PASTURE@st35 confirmed; other 3
defect seeds +0 (inert). farmer-john's OW guard not needed for this class.
Class A 15-step crew stall: still OPEN — no local mirror repro (+0 ties on all 3 stall
seeds); it is an opponent-interaction class. Ledger: results/LEDGER_20260921.md §E99.
