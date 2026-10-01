# Route-hunt ledger — 2026-09-24

## E28 — regime-only tape selection

Observation: forced route sweep on V11 changed the score surface by up to 19,316 coins/game; per-world oracle gap was +1,902.9/game across 16 R1+R2 worlds.

Hypothesis: non-YARN and YARN shop regimes have stable best tapes that beat the shipped route table.

Intervention: one mechanism only — day-6 route selection. Fitted table wraps the shipped router; no spine, crop, labor, sell, or terminal code changed.

Measurement: pinned `kaggle-environments==1.32.7`, `townCenterSellInterval=24`, both seats, control rows, route-fire telemetry.

Gate evidence:

| Bank | Worlds | Mean delta | W/L/T | Verdict |
|---|---:|---:|---:|---|
| R2 | 8 | +1,664.8 | 4/2/2 | Reject: losses; sign test p=0.6875 |
| Fresh | 16 | +169.2 | 8/5/3 | Reject: losses; sign test p=0.5811 |

Liveness: route changed in 6/8 R2 worlds and 13/16 Fresh worlds. Control mean delta 0.0. No promotion. Do not submit this graft.

Conclusion: regime-only selection is overfit. Route axis remains open only at finer conditioning (specific shop pair plus observable economy state), not as a global regime rule.

Next hypothesis: derive fresh live-loss anatomy from current V28 losses, then test one opponent-independent state variable. Do not re-run this exact regime intervention.

## E29 — step-240 rival-herd route switch

Observation: rival herd is invariant at step 144 but separates into five states by step 240. Forced-route oracle grouped R1/R2 worlds by those states.

Intervention: one dynamic tape switch at step 240 using `(rival COW, rival SHEEP)`; unknown states keep the shipped tape.

Probe: seeds 1,000,000 / 2,000,000 / 3,330,000 / 7,770,000, both against V11. All four switched and all four lost: deltas `-1946, -1761, -1309, -1008`.

Verdict: **REJECT**. Forced-route oracle does not transfer to mid-game switching; route continuity/state interaction dominates. Do not tune this mapping.

## E30 — sheep-to-cow mix conversion

Intervention: across all 41 tapes, convert at most two planned SHEEP purchases and matching placements to COW. Timing, slots, crops, and all other actions unchanged.

Probe: seeds 1,000,000 / 2,000,000 / 3,330,000 / 7,770,000 against V11. All four lost: `-2761, -8282, -4092, -7259`.

Verdict: **REJECT**. Animal species mix is not a free production upgrade; the tape economics and care schedule are coupled.

## E31 — direct top-tape replay

Intervention: replay extracted live Majkel1337 tape unchanged against V11.

R1: `0W/8L/0T`, mean `-159,289`. Verdict: **REJECT as a general agent**. Live tape is seed/world-specific, not portable.

Useful DNA remains: top tapes build roughly 17–18 pastures and buy 14–18 cows in some worlds; current routes usually build 13–17 and buy 6–9 cows. Next work must abstract that production architecture, not replay the tape.

## E32 — top-tape livestock-action transplant

Intervention: transplant Majkel live-tape livestock unit actions and `BUY_ANIMAL` orders for steps 0–359, while preserving V11 crops, land, and sell orders.

Probe deltas versus V11: seeds 1,000,000 / 2,000,000 / 3,330,000 / 7,770,000 gave `-162,671, -181,016, -196,853, -161,674`.

Verdict: **REJECT**. Top-tape unit positions are world-specific. High-capacity livestock needs a new planner, not action transplantation.
# E33 — Stateful livestock economics (2026-09-24)

Construction: appended a final wrapper after `pub_v57_apex_v11_dump.py`. For
each observed `BUY_ANIMAL` COW/SHEEP order, compared visible MILK/COW-cost ROI
against WOOL/SHEEP-cost ROI with 12% hysteresis; rewrote only same-structure
pasture species, then rewrote carried placement and product sale labels. No
quantity, timing, land, or movement changes.

Liveness: import passed; seed 1,000,000 fired 4 buy and 4 sale rewrites with
zero errors. H2H against V11: seed 1,000,000 delta -3,254; seed 2,000,000 tie.

Verdict: rejected. Price-at-purchase is not enough; the lost value is in the
full feed/care/worker schedule and sale timing. Alternative next axis must use a
real capacity/feed simulation or return to debt-accounted market preemption;
do not repeat fixed or price-only animal swaps.
# E34 — Goose-first HD2 choice (2026-09-24)

Construction: rebinding the existing HD2 decision set from `(COW, SHEEP)` to
`(GOOSE, COW, SHEEP)`, with a 5% choice margin. This was a decision-only
change; no tape timing or placement surgery.

Probe: seed 1,000,000 made one HD2 decision (`keep@241`, goose EV 3032 vs cow
-912), but scored an exact tie with V11. Seed 2,000,000 also tied and did not
fire. Inert as a competitive mechanism.

# E35 — Route-level goose substitution (2026-09-24)

Construction: after day-6 route selection, map no-goose routes to the closest
goose-bearing tape by mid-game command/market signature. One switch fired on
seed 2,000,000; seeds 1,000,000 and 2,000,000 both tied V11.

Verdict: reject both. The missing edge is not isolated goose selection or a
nearby public route. Next alternative is a schedule transplant based on DSM
DNA, with its own land/crop/animal/sale cadence and no public-route protection.
# E36 — Direct DSM tape replay (2026-09-24)

Construction: replayed extracted DSM action tape unchanged, including its
step-1/2 animal purchases, four immediate hires, clip-3 market, and d0/d2/d6
production schedule.

Probe vs V11, engine 1.32.7, interval 24: seed 1,000,000 score 27,888 vs
156,092; seed 2,000,000 score 27,583 vs 164,410. Both completed without crash.

Verdict: direct tape is world-specific, not a deployable strategy. Preserve its
structural DNA only; next construction must be a stateful transplant that
replans the DSM skeleton against observed cash, shops, inventory, and tile
state instead of replaying fixed coordinates/orders.
# E37 — Price-aware tape route scoring (2026-09-24)

Construction: at step 145, score every remaining public tape using observed
prices, subtracting future buys and adding future sells; switch when the best
route beats the current route by 2,000 theoretical value.

Liveness: both probe seeds switched; theoretical gains were +3.79M and +3.81M,
but executed scores were exact ties with V11 on both seeds. The route state is
not a controllable realized-value lever after the chassis has committed its
physical state.

Verdict: reject. Do not spend more time optimizing public route IDs. The next
candidate must alter worker/resource state directly using a bounded planner.
# E38 — Idle animal worker planner (2026-09-24)

Construction: when the inherited action was PASS on an animal tile, replace it
with the first legal task among collect fertilizer, harvest, feed, or care.
Fired 75/45 times on seeds 1M/2M; deltas were -224/+111. Rejected as
over-aggressive.

# E39 — Idle fertilizer-only planner (2026-09-24)

Construction: same wrapper, but only COLLECT_FERTILIZER on an available animal
tile. Fired 60/35 times; deltas were -51/+38. Near-parity, no breakthrough;
rejected.

Next construction must coordinate the opening resource allocation and animal
line as one stateful phase. Single-worker overlays are exhausted.
# E40 — Native-boundary price-aware router (2026-09-24)

Construction: wrapped `_IMPL.chassis.router` so the price-scored route was
selected at the chassis' own day-6 decision, avoiding V36's post-commit swap.

Probe vs V11: seed 1,000,000 delta -40; seed 2,000,000 delta -56,794.
The switch fired on both. Reject: theoretical tape value is not a safe proxy
for executable value, even at the native boundary.

Next: coordinated opening-policy simulation only; route scoring is closed.
# E41 — Coordinated route-0/2 opening policy (2026-09-24)

Construction: changed the complete first-day package on routes 0 and 2:
five→four hires, COW2/SHEEP2→COW1/SHEEP3, and matching carrier/placement
commands. Builder proof passed (`routes=2`, purchase/pick/place edits live).

Probe vs V11: seeds 1,000,000 and 2,000,000 were exact ties. The selected
routes were not 0/2, so the graft was dormant in both worlds.

Verdict: reject as a deployable candidate. Next work must select the opening
policy at step 0/2, not patch dormant route tapes.
# E42 — Step-0 opening selector (2026-09-24)

Construction: wrapped the native router and committed a goose-bearing opening
only when initial egg demand was visible. The selector fired, but the initial
observation has no shops (`initial_shops=''`) and seed 1M prices were
`EGG=50, WOOL=200`, so the policy stayed control. Both probes tied.

Verdict: step-0 shop gating is unavailable; opening selection cannot use shops
until later. Keep the selector as a diagnostic only, not a candidate.

# E43 — Price-only step-0 opening selector (2026-09-24)

Construction: wrapped the native router and selected the goose-bearing route-0
opening only when the initial observed price satisfied `EGG > 1.25*WOOL`;
otherwise delegated to the V11 control route.

Liveness: selector decision fired once per probe. Both seeds exposed
`EGG=50, WOOL=200`, so `goose_policy=0` and control was retained. Engine
1.32.7 / interval 24 scores tied V11 exactly on seeds 1,000,000 and 2,000,000.

Verdict: reject. Price-only step-0 selection is inert on the observed worlds;
do not build more opening wrappers around this signal. The next candidate must
be a policy-level stateful phase planner with executable counterfactuals, not
another route or animal overlay.

# E44 — Native cash-feasibility phase planner (2026-09-24)

Construction: at the native day-6 router, score all 41 route tapes with one
bounded cash/stock simulation. The score charged hires, land, seed, animal, and
product buys; credited only known shed sales; penalized unfunded sells; then
committed one route before execution. No post-commit tape swap.

Liveness: builder/import passed (`+4,219` bytes). Planner selected route 103 on
both probe worlds, scored all 41 routes, and raised zero errors.

Probe vs V11, engine 1.32.7 / interval 24:

- seed 1,000,000: `88,747` vs `90,941` (`-2,194`)
- seed 2,000,000: `79,957` vs `79,701` (`+256`)
- R1: `2W/6L/0T`, mean `-1,781.1`

Verdict: reject. Cash feasibility alone picks a route that is executable but
economically wrong. Do not add more route-score terms. Reopen from trace data:
the missing state is production timing and market interaction, not route cash.

# E45 — Idle-worker marginal high-value fertilizer (2026-09-24)

Construction: after the frozen V11 action, replace only `PASS` with
`FERTILIZE` on live TOMATO/STRAWBERRY/MELON tiles when current price, deadline,
and fertilizer cost passed a strict marginal-value test. No hires, movement,
route, or market edits.

Liveness probe: import passed, but fires were `0` on seeds 1,000,000 and
2,000,000 (`considered=81/229`, `accepted=0`). Scores tied V11 exactly:
`81,232/81,232` and `75,186/75,186`.

Verdict: reject as inert. Parent action stream leaves no idle high-value crop
workers. Next intervention must act at an active boundary (market queue or
planned worker assignment), not a PASS overlay.

# E46 — Premium-only debt preemption (2026-09-24)

Construction: append one `SELL` at step `%24==23` for WOOL/MILK/STRAWBERRY
when price was at least 140 and shed stock at least 6; repay same-item volume
from later parent sells. Added terminal open-slot sweep. Funding orders were
untouched.

Liveness probe: import passed, but all four probes were inert: preempts `0`,
repayments `0`, terminal sweep orders `0`, errors `0`; all four were exact ties.
R1 H2H was `0W/1L/7T`, mean `-31.2` (one `-250` seed delta).

Verdict: reject. Parent queue has no safe open slot/premium stock at the target
boundary. Do not repeat preemption thresholds. Next market test must reorder
existing executable SELLs, preserving queue length and funding positions.

# E47 — Existing SELL shadow-price ordering (2026-09-24)

Construction: sorted only already-issued positive SELL entries by conservative
within-item marginal proceeds. Non-SELL slots, quantities, worker actions, and
total volume stayed invariant.

Liveness: 55/38 multi-SELL cells, 20/18 changed cells on seeds 1M/2M, zero
errors. Direct deltas were `-165` and `+202`.

R1 H2H: `4W/4L/0T`, mean `+11.4`; per-seed deltas
`-463,-168,-165,-161,+152,+202,+338,+356`.

Verdict: reject. Ordering is active but unstable; no holdout run. Keep trace
artifact and do not tune sort direction without a fresh market-impact trace.

# E48 — V47 market-impact trace (2026-09-24)

Construction: recorded pre/post prices, queue composition, and money for every
multi-SELL cell in V47 H2H games. Seed 1M produced 54 trace rows; seed 2M 37.
Observed price changes were often driven by shared opponent sales, so local
before/after price alone cannot identify a safe ordering gain.

Verdict: trace is inconclusive. Do not tune sort direction from these two
worlds. Need paired control/candidate stream alignment or abandon this layer.

# E49 — Existing goose chassis sanity check (2026-09-24)

Construction: tested older independent `pub_apex_v6_goose.py` unchanged against
V11, to check whether a non-V11 animal lineage already provides a viable escape.

R1: `3W/5L/0T`, mean `+179.8`; deltas
`-4534,-1026,-187,-144,-114,+271,+2059,+5113`.

Verdict: reject. Positive mean hides catastrophic seed losses; not deployable.

# E50 — Independent route-free adaptive chassis A1 (2026-09-24)

Construction: new standalone agent with no V11 import, route table, or replay;
live tile targeting, phase crop choice, cargo return, hires, land, and shed
sales.

Probe vs PASS: seed 1M `183`, seed 2M `3,526`.
Probe vs V11: seed 1M `1,522` vs `193,336`; seed 2M `1,504` vs `162,695`.
Diagnostic: `1,787` harvest commands but only `42` requested sale units; farm
loop still has poor crop throughput and timing.

Verdict: reject as a candidate, keep as a clean chassis baseline. Next work is
not another V11 wrapper: fix independent crop throughput before adding animals
or market sophistication.

# E51 — A1 maturity gate + wheat funding (2026-09-24)

Construction: added engine-aligned first-yield checks; removed premature
mixed-crop spending; funded route-free chassis with 180 WHEAT seeds.

Probe vs PASS: seed 1M `3,052`, seed 2M `3,117`.
Probe vs V11: seed 1M `2,940` vs `147,755`; seed 2M `3,002` vs `188,083`.

Diagnostic: 30 plants, 51 successful harvest commands, 60 requested wheat
sales. Baseline now clears PASS, but remains far below meta. Keep only as
independent chassis seed; next layer is land/crop throughput, not V11 wrapping.

# E52 — Independent six-worker / land scale-up (2026-09-24)

Construction: increased daily hires 4→6 and added cash-gated NE/SW land buys
to the route-free A1 wheat chassis.

Probe vs PASS: seed 1M `2,113`, seed 2M `2,507`, both below A1 baseline
`3,052/3,117`.

Verdict: reject and revert. Labor/land spend outruns crop throughput. Next
independent branch is animal production, gated behind the proven four-worker
wheat baseline.

# E53 — Independent A2 one-goose pipeline (2026-09-24)

Construction: appended one live goose to route-free A1: build coop, buy/pickup,
place, reserve wheat, feed, harvest, return cargo. No V11 imports or tapes.

Liveness: both probes bought/built/placed one goose; feeds `10/8`, harvests
`8/6`, errors `0`.

Scores vs PASS: seed 1M `2,828`, seed 2M `3,253`; A1 baseline was
`3,052/3,117`. Mixed sign, no robust gain. Vs V11: `2,789` and `3,090`.

Verdict: reject as upgrade. Animal pipeline works but one goose does not pay
for its opportunity cost. Keep A1 wheat baseline; next independent work must
scale animal economics only with measured crop displacement value.

# E54 — Independent A3 one-sheep pipeline (2026-09-24)

Construction: mechanically swapped the live A2 goose layer to SHEEP/PASTURE
while retaining the route-free A1 wheat chassis, cargo return, feed reserve,
and maturity-gated harvesting. No V11 imports or replay tapes.

Liveness: both probes bought/built/placed one sheep; feeds `11/8`, harvests
`4/3`, errors `0`.

Scores vs PASS: seed 1M `3,050`, seed 2M `3,370`; A1 baseline was
`3,052/3,117`. Vs V11: `2,973` and `3,330` against `138,606/187,987`.

Verdict: reject as robust upgrade: one seed improves materially, one is flat,
and the chassis remains orders below meta. Keep A1. Sheep economics are live;
next independent branch must change throughput/market timing, not swap another
animal skin.

# E55 — Independent A4 cash-to-land melon rush (2026-09-24)

Construction: route-free A1 movement with wheat setup through day 7, then
melon purchases, plus cash-gated NE/SW/SE land unlocks. Four hires/day; no V11
imports, tapes, or wrappers.

Scores vs PASS: seed 1M `572`, seed 2M `841`. Vs V11: `3,788` and `2,347`
against `188,974/170,962`.

Verdict: hard reject. Premium-crop timing without a mature throughput spine
burns cash and strands labor. Return to A1 baseline; next candidate must
improve worker utilization and sale timing before buying premium land/crops.

# E56 — Independent A5 price-threshold selling (2026-09-24)

Construction: A1 production unchanged; suppress SELL orders until price is
8% above base, with forced terminal liquidation from step 696 onward.

Scores vs PASS: seed 1M `3,058`, seed 2M `3,123` versus A1 `3,052/3,117`.
Vs V11: `2,946` and `3,015` versus `147,750/188,078`.

Verdict: reject. Holding inventory creates only noise-level gains; no market
timing edge appears without substantially more production and volume.

# E57 — Independent A6 wheat + cash-gated land (2026-09-24)

Construction: A1 four-worker wheat cycle, four seed purchases through day 24,
and NE/SW/SE land purchases only after cash thresholds. No premium crop and no
V11 lineage.

Scores vs PASS: seed 1M `1,333`, seed 2M `1,149`. Vs V11: `1,390` and
`1,614` against `194,178/174,485`.

Verdict: reject. Land bought without a real routing/throughput scheduler is a
cash sink. The next branch must replace nearest-target dispatch itself, not
just toggle land or crop schedules.

# E58 — Independent A7 sector dispatch (2026-09-24)

Construction: replaced nearest-target-only selection with four deterministic
grid lanes (`(x + 10*y) % 4`), one lane per worker, while retaining fallback
urgency and A1 wheat funding. No V11 code or replay tape.

Scores vs PASS: seed 1M `3,104`, seed 2M `3,168`, beating A1 by `+52/+51`.
Vs V11: `3,045` and `3,091` against `155,901/134,017`.

Verdict: mechanism is live and positive but far below meta. Keep as the new
independent base. Next layer: fertilizer-aware lane scheduling and explicit
worker route reuse; do not spend on land until this scales production.

# E59 — Independent fertilizer lane (2026-09-24)

Construction: A7 lanes buy 4 fertilizer on days 8/16, return each worker to a
fixed shed-access tile on days 9/17, pick up, and route to young plants. A first
attempt was inert because the sell loop immediately liquidated fertilizer;
that state bug was fixed before scoring.

Liveness after fix: fertilizer operations fired `52` times across the two
seed probes; fertilizer market orders executed `4` times per run.

Scores vs PASS: seed 1M `2,641`, seed 2M `2,708`, versus A7 `3,104/3,168`.

Verdict: reject the naive fertilizer lane. Fertilizer is live but its travel
and labor cost exceeds its yield gain on this chassis. Keep A7 as base; next
work must reuse route state and assign fertilizer only when a worker is already
near a high-value plant.

# E60 — Independent A11 persistent route memory (2026-09-24)

Construction: A7 sector dispatch plus per-seat/per-worker persistent tile
targets. A worker retains its target through planting, daily watering, harvest,
and replant; targets are invalidated only when blocked, weeded, or seedless.
No public spine, replay tape, land purchase, or fertilizer.

Scores vs PASS: seed 1M `3,501`, seed 2M `3,577`; versus A7 `3,104/3,168`
(gains `+397/+409`). Vs V11: `3,319` and `3,508`.

Verdict: keep A11 as the independent base. This is the first material
throughput gain. Before any submission, repeat the 8-seed R1/R2/Fresh gates;
next layer is targeted route reuse for fertilizer/land only after a worker is
already in position.

# E61 — Independent A12 six-lane labor scaling (2026-09-24)

Construction: A11 persistent targets with six hires/day and six deterministic
lane residues. This specifically retests labor after route memory, unlike the
earlier reactive six-worker rejection.

Scores vs PASS: `3,862 / 3,723`; A11 was `3,501 / 3,577`. Vs V11:
`3,662` and `3,841`.

Verdict: keep A12 as the current independent champion. Six workers now produce
a positive scale gain; run full holdout gates before further mutation.

# E62 — Independent A13 eight-lane labor scaling (2026-09-24)

Construction: A11 persistent targets with eight hires/day and eight lanes.

Scores vs PASS: `3,185 / 3,753`; Vs V11: `3,698 / 3,146`.

Verdict: reject as unstable. Six workers is the current labor ceiling for this
chassis; do not add labor blindly.

# E63 — Independent A14 late-carrot funding (2026-09-24)

Construction: A12 six-lane controller buys 60 CARROT seeds on day 24 to match
the existing day-24 CARROT phase.

Scores vs PASS: `3,614 / 3,109`; Vs V11: `3,571 / 3,448`.

Verdict: reject. Six late days do not amortize carrot spend and the phase
switch remains economically wrong.

# E64 — Independent A15 full-wheat six-lane (2026-09-24)

Construction: A12 route memory and six workers, but keep WHEAT through day 30
and buy a fourth 60-seed wheat tranche on day 24. No carrot phase, land, or
fertilizer.

Scores vs PASS: `3,958 / 3,803`; Vs V11: `3,654 / 3,937`.

Verdict: keep A15 as current independent champion. It improves both probes
over A12 by `+96/+80`, but remains far below public meta. Next step is the full
R1/R2/Fresh gate, then in-route high-value fertilization—not another crop swap.

# E65 — Independent A16 seven-lane (2026-09-24)

Construction: A15 with seven hires and seven lanes.

Scores vs PASS: `3,638 / 4,002`; Vs V11: `4,104 / 3,915`.

Verdict: reject as unstable versus A15. Six workers remain the default.
