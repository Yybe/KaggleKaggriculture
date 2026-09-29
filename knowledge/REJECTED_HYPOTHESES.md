# Rejected Hypotheses — closed research directions (cha22 cycle, measurements of 2026-09-25)

One entry per direction that was tried and closed, recorded with its **construction** and not just its
sign, so a retry can differ materially instead of repeating a defeated implementation (`AGENTS.md:58-62`
Rule 3). Refuted variants carried over from earlier cycles are included where this cycle's ledger restates
them with their doses and floors.

Fields per entry: **Hypothesis** / **Experiment IDs** / **Observed result** / **Reason for rejection** /
**Exact conditions** / **Reopenable**. `census` = the seat-averaged fresh-child-process harness that
reproduces `run_h2h` to the coin (12 validations); `gate` = official `tools/run_h2h.py`. Banks: **r1**
(8 seeds), **r2** (8 holdout seeds), **fresh** (16 holdout seeds), both seats per seed. Engine pin
`kaggle-environments==1.32.7`, `townCenterSellInterval=24`, `episodeSteps=720` unless stated otherwise.
LEDGER = `results/LEDGER_20260925.md`, E137DOC = `E137_C22_PREEMPT_20260925.md`, E206DOC =
`E206_MW_H1Q6_AGENT_DOCUMENTATION_20260925.md`.

---

## A. Market / preemption / sell-timing

### H-001 The debt-accounted hour-23 wheat preempt is the missing piece

**Hypothesis** The champion's off-wave selling is not volume-conserving, so a debt-backed preempt at
`step % 24 == 23` converts its near-ties into wins.
**Experiment IDs** E137 (graft), E138 (parked in-spine follow-up).
**Observed result** gate, **r1**: **3W/5L/0T, mean +18.1/seed**, per-seed deltas −8, −8, −4, −2, −1, +2,
+4, +162 (n=16 games). Excluding the +162 world, the other seven average **−2.4**.
**Reason for rejection** Pre-registered bar was *zero seed-level losses* AND mean > 0 AND zero ties — the
loss clause failed, so the ladder, R2 and Fresh banks were deliberately not run (G9: no "one more seed").
The 0T means the graft bound on every seed, so this is a measured negative, not an untested one.
**Exact conditions** Base `agents/cha22_champion.py` (sha1 `c17f23f64f7c5436491eae057aea1a770e2a65f7`),
append-only `_e137_preempt` + `_e137_repay` outside `ig_agent`; window `[240, 671]`, `phase 23`, `mod 24`,
`min_avail 6`, `floors = {FERTILIZER 90, WHEAT 30, other 140}`, `qty = {FERTILIZER 10, other 6}`, one item
per turn, `_E137_ORDER = FERTILIZER, WHEAT, MILK, WOOL, STRAWBERRY`; probe 33 clips / 198 preempted units /
198 repaid units / 0 slot-blocks / 0 errors on 4 seeds.
**Reopenable** no for this shape. Only a change to *what the debt ledger repays* (which item's later order
is clipped) counts as different; the ledger's own stop rule says the +18.1 is bounded because the spine
already floods hour 22-23 with 2,253 units while our layer moves ~50/season into a slot the spine fills
with ~370. (LEDGER:156, 182-243 (§12); E137DOC:264-315 (§5).)

### H-002 Retuning the preempt trigger threshold buys selectivity

**Hypothesis** `floors["other"] 140 → 175` prunes the loss-prone fires without losing the wins.
**Experiment IDs** E151a.
**Observed result** gate, **r1**: **3W/5L/0T, mean +18.1** — identical to the audited graft on all eight
per-seed deltas; probe vs `agents/c22_preempt.py` reads `differing steps 0 -> GRAFT INERT`.
**Reason for rejection** The retune edits a branch that never runs: 33/33 clips are WHEAT, 0 FERTILIZER /
MILK / WOOL / STRAWBERRY. The `other` floor is unreachable through the *availability* gate, not the price
gate (`min_avail = 6` binds, not the floor).
**Exact conditions** Same spine and layer as H-001 with the one line changed; probe seeds 1,000,000 and
3,330,000 (11/14 differing steps vs the champion, i.e. live but unchanged in outcome); hour-23 census over
18 in-window trigger turns × 2 seeds.
**Reopenable** no — a floor change on this layer is measured inert in both directions (see H-005, H-008).
(LEDGER:182-235 (§12); logs `gates_cha22/E151a_r1.txt`, `E151_fire_census.txt`.)

### H-003 Re-ordering the preempt's item list to premium items

**Hypothesis** `_E137_ORDER → (MILK, STRAWBERRY)` makes the layer sell the items that carry price spread.
**Experiment IDs** E151b; extended and closed again at E191 (see H-007).
**Observed result** probe `GRAFT INERT`, 0 differing steps on seeds 1,000,000 and 3,330,000; **not gated**.
**Reason for rejection** Per Rule 2 / R-003 an inert graft is untested, not a tie, so the row carries no
verdict — and the *reason* is inventory, not order: at hour 23 the tape leaves only wheat in the shed.
**Exact conditions** Identical spine, identical trigger set, only the resolution order of items changed.
**Reopenable** only as a different hour (the hour-01 form was built as E206; see H-011).
(LEDGER:195, 209-235 (§12); `gates_cha22/E151b_probe.txt`.)

### H-004 Moving the preempt window to a better hour

**Hypothesis** Some hour of the day has both a premium quote and shed stock to sell into it.
**Experiment IDs** E155 (census, no build).
**Observed result** census, no W/L row: % of in-window turns with shed ≥ 6 / median own price — hour 0
MILK 50 % / 62, WOOL 12 % / 1, STRAWBERRY 35 % / 160, WHEAT 99 % / 41, FERT 94 % / 37; hour 23 MILK 0 % /
60, WOOL 0 % / 1, STRAWBERRY 1 % / 148, WHEAT 49 % / 41, FERT 6 % / 34.
**Reason for rejection** Premium inventory exists only at hours 0-1 — which is the hour the clone wave
*lands*, so there is nothing to front-run (`dpx` +0/−1) — and by hour 23 only WHEAT clears `min_avail`.
MILK never clears its 140 floor anywhere (px 52-69) and WOOL's px is 1-8, so those rows are dead on price
rather than on stock. Preemption is thereby closed on threshold (H-002) **and** window.
**Exact conditions** `tools/e155_preempt_hour_census.py`, 4 seeds × 72 turns per hour, floors WHEAT 30 /
FERTILIZER 90 / other 140, champion-vs-champion.
**Reopenable** no for a threshold/window retune of this layer; yes for a *sell-early-at-the-peak*
construction, which is a different mechanism (H-011). (LEDGER:268-285 (§13).)

### H-005 A higher WHEAT floor separates profitable fires from shuffles

**Hypothesis** v57's pricing of the loss class ("preempts at $38-41 are shuffles, $42-45 are profit")
means raising `floors["WHEAT"]` removes a loss class.
**Experiment IDs** E184 (+ E196's floor-down half, H-008).
**Observed result** census, **fresh** 16 seeds × both seats (32 games, 266 fires, 266/266 WHEAT): worlds
that never fire ≥ 42 (n=6) mean Δ **−1.2**, median −3.0, 2W/4L; worlds that fire ≥ 42 (n=10) mean Δ
**+79.2**, median +3.0, 7W/2L — but every world in the first bucket sits within ±5 of zero.
**Reason for rejection** The low-price fires are mirror noise (≤0.005 % of a ~100 k bank), not a loss
class; and the knob is closed *by construction* — 6/16 fresh worlds never see WHEAT ≥ 42 and world
30014000 never sees ≥ 38, so floor 36 is a provable no-op and every floor ≥ 37 abstains at least one world
into a guaranteed tie. Price min 36 / p25 39 / med 41 / p75 43 / max 45 at fire.
**Exact conditions** `tools/build_e184_preempt_floor.py` EOF rebind (spine untouched, `_E137_T["floors"]
["WHEAT"] == 30` asserted after import); control `agents/cha22_e184_preempt_w30.py` = `c22_preempt` plus a
fire `.append()`.
**Reopenable** no on WHEAT; the same theorem was reproduced independently as v57's V22 4W/0L/4T. Only an
item change gives a price bar something to select (R-010). (LEDGER:874-921 (§28).)

### H-006 Dosing `min_avail`, `qty` and `phase` upward improves the preempt

**Hypothesis** The additive knobs (which can only create fires, so cannot abstain a world) can lift the
mean without touching the record.
**Experiment IDs** E185.
**Observed result** census, **fresh** 16 seeds × both seats, vs `cha22_champion` (shipped E168 reference:
10W/5L/1T, +84.4/seed): `_ma3` 10/5/1 **+84.6** (median +3.0, 282 fires, 16 fires at avail 3-5); `_ma4`
10/5/1 **+84.6** (indistinguishable from `_ma3`); `_q10` **6W/10L/0T** +89.5 (median −2.0, 238 fires, 2241
units); `_ma3q10` 6/10/0 +90.3 (256 fires); `_ph22` 7/8/1 **+8.2** (278 fires, 1668 units).
**Reason for rejection** `min_avail` is dead weight (no world has exactly 3 open market slots on a preempt
turn — the engine's 10-slot book-keeping had already absorbed the case), so 16 extra fires move the mean by
+0.2/seed with a *bit-identical* record; `qty` up is a variance purchase whose zero ties are the tie being
paid for with losses; `phase` 23→22 forfeits the wave's price information and gives away 76 of the 84.
**Exact conditions** Five EOF-dose variants built on `agents/cha22_e168_tom_mono76_preempt.py` by
`tools/build_e185_preempt_dose.py`, screened by `tools/e185_preempt_dose_census.py`, zero gate budget spent.
**Reopenable** no — "the E137/E168 preempt is done; 6/6/23 is the shipped optimum on this spine". Any
future attempt must change what is sold, not how much or how often. (LEDGER:950-985 (§30).)

### H-007 Changing *what* is preempted (item axis) at hour 23

**Hypothesis** Rotating `_E137_ORDER` and applying `min_avail 3` to every item lets the layer sell MILK
and WOOL, the 7.4-7.7 % curves.
**Experiment IDs** E191.
**Observed result** census, **fresh** 16 seeds × both seats: `_scan` control 10/5/1 +84.4 (266 fires, WHEAT
266 — reproduces E168's fresh gate multiset to the coin, control including the tomato world); `_rot` 10/5/1
+84.4 with byte-same deltas; `_ma3all` 10/5/1 +84.6 (282 fires, WHEAT 282); `_rotma3` **9W/6L/1T +51.6**
(286 fires: WHEAT 282, **WOOL 4**).
**Reason for rejection** The joint availability×price census over 576 window-turn observations (18 turns ×
16 seeds × 2 seats) reports WHEAT clears jointly **282 (49.0 %)** and FERTILIZER / MILK / WOOL /
STRAWBERRY **0**; marginals explain it — MILK avail med/p90/max 0/0/11, WOOL 0/0/**3** (so WOOL's
`min_avail 6` is unreachable on its own), FERT px max **76** against a floor of 90 (unreachable code). The
4 WOOL fires that were forced cost **−32.8/seed** and flipped one world from +26 to −537, because hour 23
is a *trough* for the animal items.
**Exact conditions** Four EOF rebinds on `cha22_e168_tom_mono76_preempt.py` via
`tools/build_e191_preempt_item_axis.py`; instrument `tools/e191_preempt_item_census.py`; log
`gates_cha22/E191_item_census2.txt`.
**Reopenable** no at hour 23 (structurally closed). The item-identity direction survives only at another
hour — and there it is H-011. (LEDGER:1041-1086 (§32).)

### H-008 Relaxing the preempt's floor or widening its early window

**Hypothesis** Relax-only doses (`floors["WHEAT"]` down, window `lo` back) can turn tying worlds into
tested worlds without costing the mean.
**Experiment IDs** E196 (census), E197 (gate), and `hi` excluded on principle.
**Observed result** census, **r2+fresh** 24 worlds × both seats vs `cha22_champion`: reference E168
(`lo 240`, floor 30) 12W/8L/**4T** +62.1 (median +0.5, 384 fires, 2304 units); `f24` and `f20`
*identical to the reference on all 24 worlds to the integer*, 384 fires; `lo96` 12/10/2 +60.6 (490 fires,
+106 = +27.6 % volume, days 5-9); `lo48` identical to `lo96` row for row; `lo96f24` **12W/12L/0T +61.2**
(median **−1.2**, 510 fires, 3060 units). Gate of `lo96f24` (E197), pooled 32 seeds:
**18W/13L/1T +178.0** vs E168's 17W/11L/4T +177.5.
**Reason for rejection** The floor is slack in both directions (the champion's own schedule drains the
cheap quotes before hour 23, and the shed is never the binding constraint there either); and the extra
fires are not extra sales — each is booked as debt and repaid by clipping a parent sale, so it converts a
day-5-9 parent price into the hour-23 price on the flattest curve in the game (1.4 % spread). Result:
fires +33 %, dispersion up, mean ±0, median goes negative. Honest label: **testability, not EV**. Against
its own reference E168 the dose is **−0.45/seed** (a wash) at ladder grade.
**Exact conditions** `tools/build_e196_preempt_window.py` EOF rebind keeping E185's symbol names; variants
`lo ∈ {240, 96, 48}`, `floors["WHEAT"] ∈ {30, 24, 20}`, qty 6, `phase 23`, window `hi = 671` unchanged;
log `gates_cha22/E196_preempt_window_census.txt`, 48 games, 0 errors, zero gate budget. `hi` was never
dosed: a fire after step 671 has no later parent SELL to clip, so it stops being volume-conserving and
becomes an unsanctioned extra sale (E57c's failure mode).
**Reopenable** the *tie-killer* use of `lo96f24` is retained (it feeds the deployed lineage); further
dosing of this layer is closed "for the third and final time". (LEDGER:1239-1295 (§36), 1297-1337 (§37),
1358-1375 (§38).)

### H-009 More volume per preempt clip keeps paying for itself

**Hypothesis** Raising `qty` in the volume-conserving preempt raises the win in proportion.
**Experiment IDs** E199 / E205 (dose grid at `lo 96`, `floors["WHEAT"] 24`).
**Observed result** gate, vs `cha22_champion`: **qty 8** r1 **8W/0L/0T +559.0**, r2 6/1/1 +31.0, fresh
9/7/0 +98.6, pooled 32 seeds **23W/8L/1T +196.8**; qty 10 r1 6/2/0 +560.5, pooled **20/10/2 +197.0**;
qty 14 r1 **0W/8L/0T −3,015.5** (r2+fresh not run — the stop rule fired at r1). Fires per 16 r1 games:
156 (q8), 152 (q10), **126 (q14)**.
**Reason for rejection** Raising clip size *lowers* the fire count, because a bigger preempt empties the
shed and its own debt ledger blocks the next window; past 10 the size term dominates negative — the sale
moves its own quote, i.e. E57c reproducing inside the preempt layer at the third dose point.
**Exact conditions** `tools/build_e199_preempt_dose2.py` on `cha22_e168_tom_mono76_preempt.py`, window
`[96, 671]`, `phase 23`, floor WHEAT 24 / FERT 90 / other 140, `min_avail 6`, `qty ∈ {6, 8, 10, 14}`;
official gate log `gates_cha22/E205_q8_vs_cha22_all.txt`, engine asserted inside the log.
**Reopenable** no on qty. The one remaining `+0` in this family (r2 seed 4440000) is proven not to be a
dose artefact but the engine round trip (R-001), so a larger clip cannot fix it either.
(LEDGER:1481-1521 (§41), 1551-1577 (§43).)

### H-010 Retiming the champion's MILK/WOOL sells onto their measured peak hour

**Hypothesis** The spine sells MILK/WOOL at percentile 36.7/46.9; holding them to the measured peak (h01)
reclaims +19-27 % of sold value.
**Experiment IDs** E194 (`mw`, `mwsc`), census only.
**Observed result** census, **fresh** 16 seeds × both seats: `mw` (MILK/WOOL → h01) **0W/16L/0T,
−63,988.3/seed**, 7,149 orders / 38,448 units deferred, 706 orders / 2,058 released (**5.4 %
realisation**), 4,224 forced, `no_room` 18/32 seats, `slot_drops` 0; `mwsc` (+ STRAWBERRY h13, CARROT h0)
0W/16L/0T **−66,596.8**, 10,028 / 74,097 deferred, 822 / 2,708 released (3.7 %), 6,278 forced, `no_room`
44, `slot_drops` 44.
**Reason for rejection** 94.6 % of the withheld volume never came back: the release path is
clock-rate-limited (1 turn per 24 at the item's best hour, or the forced h23 boundary, one order per item)
while the deferral path is not, and the shed is not a bank (overflow silently discarded). The spine also
believes the SELL happened and keeps harvesting into a shed that no longer drains. Run-out is ≈9× the whole
theoretical prize (64 k lost against a +7,232 measured gap).
**Exact conditions** `tools/build_e194_sell_phase.py`, outer `agent` wrapper
(`_E194_PARENT = agent; del agent; def agent(...)`), volume-conserving by construction with forced release
at h23; instrument `tools/e194_sell_phase_census.py`; log `gates_cha22/E194_sell_phase_census.txt`.
**Reopenable** **no** — "no re-dose (other hours, MILK-only, partial volume) is owed a run: every variant
of this shape must withhold volume to work at all." The early-sale form of the same price gap is a
different mechanism and was built (H-011). (LEDGER:1143-1187 (§34).)

### H-011 The peak-hour MILK/WOOL layer is a profit lever (as opposed to a tie-killer)

**Hypothesis** Selling MILK/WOOL early at hour 01, volume-conserving and non-rebuyable, converts the
champion's percentile-37 selling into real money.
**Experiment IDs** E206 / E207 (dose census), E208 (gate + ladder), layer `_E206` deployed as
`agents/cha22_e206_mw_h1q6.py` (ref 56554887).
**Observed result** census then gate vs `cha22_champion`: `h1q6` (hour 1, qty 6) R1 6/2/0 +613.8
(median +122.0), R2+Fresh 12/12/0 +88.3 (median **−13.5**), pooled **18W/14L/0T +219.7**; parent `q8`
23/8/1 +196.8 (median +3.5). Dose family: `h012q6` (hours 0/1/2) pooled 16/16/0 **+179.2**; `h1q10`
17/15/0 **+155.7**; `h1q4` dropped after R1 at 6/2/0 +564.8/+91.0. Official paired gate **against its own
parent** `cha22_e199_lo96q8`: R1 6/2/0 +50.0, R2 3/5/0 −27.5, Fresh 8/8/0 −6.1, pooled **17W/15L/0T
+2.6/seed**. Ladder: on the Fresh bank the layer costs **86-104/seed** against three of four pulled
kernels (e.g. `baseline_x1` +1,525.8 vs q8's +1,628.6; `friend_r78ub` +1,510.5 vs +1,614.9).
**Reason for rejection** The increment is **sub-noise** (+22.9/seed inferred, +2.6/seed paired, SE ≈ ±39
with sd ≈ 220, carried by three worlds +772/+208/+141) while the win rate falls from 23W/8L to 18W/14L.
Volume and window width are already past the optimum: `h1q4`, `h1q10` and `h012q6` all sit below both
parents on the pooled mean. Against a public kernel an early MILK sale moves a quote the opponent is also
riding, so the layer is *negative* in the pool shape the live leaderboard has.
**Exact conditions** Layer `_E206`: MILK/WOOL at `step % 24 ∈ {1}`, window `[240, 671]`, one item per turn,
qty 6 (doses 4/10 also built), `min_avail 6`, fires only when that item carries no debt, same
clip-the-parent repayment as the wheat layer; built on `cha22_e199_lo96q8.py` by
`tools/build_e206_peak_preempt.py`, which asserts the parent dose is exactly
`(lo 96, floorW 24, qty 8, min_avail 6, phase 23)` and that both fire ledgers survive; `fires@avail<6 = 0`
in every dose; logs `gates_cha22/E207_r1_census.txt`, `E207_r2f_census.txt`, `E208_*.txt`.
**Reopenable** no as an EV lever ("the axis is spending its last unit of credibility"). Yes as a
*construction requirement*: a tie-killer that does not move much volume. The one untried direction on the
axis is item identity (STRAWBERRY at h13, CARROT at h00), which the ledger makes conditional on the animal
increment holding on the official gate — and it did not (paired +2.6).
(LEDGER:1628-1690 (§45), 1693-1757 (§46); E206DOC:32-59 (§3).)

### H-012 WHEAT/FERTILIZER phantom orders are costing real queue slots

**Hypothesis** Because WHEAT and FERTILIZER sit outside `_IG_CASH`, cha22's queue is padded with orders
that cannot fill, and a cover-check recovers the slots for free.
**Experiment IDs** E177 (and the §5 E142 queue row), plus E149 (H-013).
**Observed result** no gate: `CAP = 10`, **steps over cap = 0** on seeds 1,000,000 and 2,000,000
(1,440 seat-steps each); live replays corroborate — 0 declared units fell past the 10-orders-per-turn cap
on either seat in 20 games.
**Reason for rejection** The prize is defined by `q[:10]` truncation and truncation never happens, so the
cover-check has nothing to recover; §5's last open row is zero-size.
**Exact conditions** `tools/e177_queue_saturation_census.py` measures exactly §4's bound (dropped
*coverable* units beyond index 10, not wasted intent); cha22 mirror, pinned engine.
**Reopenable** yes, but only for a candidate that lengthens queues (a drip or a 10-order sweep), which
changes the saturation regime; then re-run this census before building anything.
(LEDGER:733-747 (§23); `results/E145_DIVERENCE_20260925.md:154`.)

### H-013 Clamping sell asks to provably-held inventory is unclaimed value

**Hypothesis** Emitting only covered SELL orders lifts realised revenue.
**Experiment IDs** E149.
**Observed result** gate, **r1**: **0W/0L/8T, mean +0.0** (byte-identical); probe `GRAFT INERT`.
**Reason for rejection** `_ig_close_queue` (`:7419`) already zeroes and pulls `_IG_CASH` sells beyond
`projected` — the graft reimplements an existing outer layer, behind the market-write overwrite that makes
all chassis-level edits inert (R-008).
**Exact conditions** Outer graft wrapping `ig_agent` on `agents/cha22_champion.py`.
**Reopenable** no. (LEDGER:152 (§9); E144's challenger scan confirms the same queue-closing stack exists.)

### H-014 The champion's disabled chassis settings are money left on the table

**Hypothesis** Switching on `terminal_liquidation`, `dead_stock`, `room_guard`, `budget_guard`,
`clamp_sells`, `front_run` (all `False` at `:949` against `DEFAULT_SETTINGS` `:264-270`) recovers value.
**Experiment IDs** E146 (four variants), plus E142 (H-034).
**Observed result** gate, **r1**: `terminal_liquidation` **0W/0L/8T +0.0**; probes on
`dead_stock` / `room_guard` / both: `differing steps 0 -> GRAFT INERT` on seeds 1,000,000 and 3,330,000.
**Reason for rejection** Three independent causes: the outer stack rebuilds `result["market"]` from the
tape at ~16 sites so chassis market writes are discarded; the end-of-game shed is already `{}` and steps
716-719 already carry SELLs; and `front_run` is gated behind `cfg["front_run"] and self.opponent_plan`
(`:485`) with `make_agent` (`:981`) passing no plan at all.
**Exact conditions** `tools/build_e146_settings.py`, one flag per variant, entrypoint asserted
`_e146_agent`; probe `tools/tape_diff_probe.py`; logs `gates_cha22/E146_termliq_r1.txt`,
`E146_probe_termliq.txt`, `E146_probe_roomguard.txt`.
**Reopenable** no via a flag; the only route to `front_run` is feeding a rival plan in, which is H-042.
(LEDGER:105-133 (§7).)

### H-015 Turning on the spine's own early-booking / frontloading branches

**Hypothesis** `_ADV_BOOK = False` (`:6207`) and the `_ADV_FRONT` sale-frontloading branch are switched off
by oversight; enabling them makes the champion's pull-forward volume-conserving.
**Experiment IDs** E150; the same hypothesis re-registered as E138.
**Observed result** gate, **r1**: `_ADV_BOOK=True` **2W/5L/1T, mean −60.9**; `_ADV_FRONT=True`
**2W/6L/0T, mean −29.9**. Both probe LIVE (they are not inert).
**Reason for rejection** Live and worse — one of the eight single-mechanism perturbations that make the
champion a measured local optimum. The audit's own residue reading was also mis-signed: `r36_debts` ends at
0 entries / 0 units because the ledger is *never booked* (dead write at `:6266`), not because the champion
conserves volume.
**Exact conditions** In-place constant flips on the champion spine; hour-23 preemption therefore has to
live in an outer graft, and the off-wave emitters `_fx:6635` / `_ev:6692` / `_dp:6796` / `_mp:6869` /
`_mpx:7050` / `_sm:7142` / `_ROOM:1123-1145` / `_r51:2303-2350` / `_t62a:6310-6332` touch no ledger.
**Reopenable** yes, with a different instrument: an asserted one-constant in-spine patch *plus* a
reachability proof that the booked loop is entered — this flip alone is not it.
(LEDGER:153-154, 158-161, 105-128 (§7/§9); E137DOC:100-124 (§2).)

### H-016 Suppressing the floor-dumps on strawberry and MILK (prior cycle, restated)

**Hypothesis** The champion's low-price dumps are shed-pressure relief that a hold-floor can defer
profitably.
**Experiment IDs** `v37_holdfloor`.
**Observed result** **0W/16L** (bank not restated in this cycle's ledger; cited as a constraint, not
re-run).
**Reason for rejection** Those sells *are* the capacity relief — shed cap is 100 per stack-set, so
deferring them is H-010 by another name.
**Exact conditions** Restated at LEDGER:97-98 (§6) as the constraint that makes the winner-matched,
tape-side dose the only admissible production intervention.
**Reopenable** no without an inventory model change (R-009). Confidence for this row is **medium**: the
construction detail lives in an earlier ledger, not in these inputs.

---

## B. Production / crop-mix

### H-017 A cadence-blind crop swap on the route tapes

**Hypothesis** Strawberry→tomato `PLANT` + matching `BUY_SEED` on 100 % of tape sites captures the
winner-matched crop delta.
**Experiment IDs** E148.
**Observed result** gate, **r1**: **0W/8L/0T, mean −38,644/seed**, probe signature `HARVEST −32 / DIG +32`.
**Reason for rejection** Tomato is productive on a 1-day interval against strawberry's 2; the tape waters
and harvests on strawberry's rhythm, so the converted plots miss their window and get dug up. Compounded
by route-action aliasing: the "50 %" dose actually converted **113 of 213** sites.
**Exact conditions** On `cha22_champion` spine, post-decode `_ROUTES` mutation, `tom50` dose; tomato seed 50
vs strawberry 100, first/max yield day 8 vs 10, both `ongoing`, max_yield 4.
**Reopenable** no in this form — tape *content* is not separable from its cadence (H-018 tested the fix).
(LEDGER:155, 163-174 (§10).)

### H-018 The same swap, with the water/harvest cadence regenerated

**Hypothesis** Attaching tomato's cadence kills E148's death signature and the loss with it.
**Experiment IDs** E152.
**Observed result** gate, **r1**: **0W/8L/0T, mean −5,730.6**, per-seed deltas −11557, −6155, −5619,
−5600, −5302, −4737, −4630, −2245; probe LIVE (seed 1,000,000 `differing=43`, 3,330,000 `differing=54`,
first divergence step 155; op deltas `DIG +6, HARVEST +2, WATER −8, MKT:BUY_SEED +4, MKT:SELL +4/+6`).
**Reason for rejection** The death signature is gone but the loss is not: only ~18 % of the per-plot damage
is recovered (−1,171 → −955 per converted plot) and most of the headline improvement is the 5.5× smaller
dose (33 → 6 plots/game). Structurally: 3 of every 4 strawberry harvest slots fall past the tomato rot
step and **489** cannot be moved (no hand standing on that tile at that hour), the vacated plot opens a hole
from ~day 12 that nothing replants (the +6 DIG), and the PASS-only watering rule emitted **0** water ops
while spending 246 existing waters as harvest slots.
**Exact conditions** `tools/build_e152_tomato_cadence.py` → `agents/cha22_e152_tomato_cadence.py`,
+7,111 B append-only graft (2,044 B base64/zlib plan blob), deepcopies routes instead of touching
`_ROUTES`, dose 6 plots × 41 tapes = 246 plots, all day-6 plantings at steps 153-163, asserted fired ==
planned `{'P': 246, 'H': 250, 'W': 0, 'BUY_SEED': 246}`; spine census PLANT TOMATO 0 → 246, PLANT
STRAWBERRY 1353 → 1107; bar = zero seed losses + positive mean + zero ties → failed two of three.
**Reopenable** yes, narrowly, and ranked low: the recorded-not-gated variant is the *latest*-planting
ordering (day ≥ 12), the only dose shape where retiming has nothing to repair — plus a re-plant clause for
the hole. Same-channel retry without both is a repeat. (LEDGER:575-673 (§20).)

### H-019 The tomato unlock is worth switching on as-is

**Hypothesis** `c3: ≥3 shops` → `≥2` (one digit) activates a sound production block at a profit.
**Experiment IDs** E157.
**Observed result** gate vs `cha22_champion`: **R1 3W/0L/5T +569.8** (+0×5, +543, +1215, +2800), **R2
0W/3L/5T −707.2** (−1949, −1895, −1814, +0×5), **Fresh 1W/3L/12T −174.6**, pooled **4W/6L/22T −121.6**.
**Reason for rejection** Live, cleanly attributed (non-tie seeds are exactly the ones the clause census
predicted) and high-magnitude — mean |1,120| over 10 fired worlds — but net-negative as built, and the
bank flip is a *price* boundary not a bank effect: the three R1 wins are the three px ≥ 75 worlds, the
three R2 losses are three px == 71 worlds.
**Exact conditions** `tools/build_e157_tomato_gate.py` → `agents/cha22_e157_tom2shops.py`; one line,
length-preserving; `CROP_MIN_PRICE` asserted still 70 so the edit stays single-mechanism; firing population
expected to rise from 2/16 to ~8/16 seeds.
**Reopenable** yes — and it was: the calibrated monotone bar (H-021, whose E164 dose became the accepted
candidate) is the session's only
positive-mean, zero-loss candidate. Rejected as-is ≠ rejected as an axis. (LEDGER:336-371 (§15).)

### H-020 A flat, higher `CROP_MIN_PRICE` bar inside the two-shop clause

**Hypothesis** Raising the tomato price bar to a constant (74/76) inside the relaxed clause keeps the wins.
**Experiment IDs** E161.
**Observed result** **no interpretable gate row** — both "all" runs wrote the same log path
`gates_cha22/_all.txt` and the second destroyed the first; the reasoning was reconstructed from the E160
dose scan.
**Reason for rejection** Wrong *shape*: a flat bar also **withdraws** worlds the champion already farms
(any shops ≥ 3 world with 70 ≤ px < bar — e.g. seed 30004000 at px 73), so it buys upside at the cost of
someone else's positive.
**Exact conditions** `cha22_e161_tom2_px74.py` / `_px76.py`; log-loss recorded as a bench-integrity defect
(H-047).
**Reopenable** no as a flat bar; the monotone form (bar only where shops < 3) superseded it.
(LEDGER:411-417 (§16).)

### H-021 The monotone bar 74 is the right dose

**Hypothesis** Bar 74 keeps enough of the +543 world to dominate bar 76.
**Experiment IDs** E162 vs E164.
**Observed result** gate vs `cha22_champion`: E162 (bar 74) R1 3W/0L/5T +569.8, R2 0W/0L/8T +0.0, fresh
1W/1L/14T −39.9, pooled **4W/1L/27T +177.1**; E164 (bar 76) R1 2W/0L/6T +501.9, R2 0W/0L/8T +0.0, fresh
1W/0L/15T +35.4, pooled **6W/0L/26T +143.2**.
**Reason for rejection** Bar 74 keeps fresh seed 30012000 at **−1205** and so loses the zero-loss property
that is the promotion bar; bar 76 drops both that world and +543-world 6000000 and is the first candidate
with a positive mean and zero seed losses across all three banks. Both rows reconcile exactly against the
E160 dose-scan table, which is the cross-check that the gate and the scan describe one mechanism.
**Exact conditions** Clause rewritten additively: `prices['TOMATO'] < (70 if shops >= 3 else BAR)`;
`tools/e160_tomato_dose_scan.py` over 40 gate seeds × both seat orders, features read from the candidate's
own observation at step 432.
**Reopenable** no on the bar; the residual 26 ties are structural (H-024). (LEDGER:378-432 (§16).)

### H-022 The terminal-rescue abstention is a handicap that keeping the rescue fixes

**Hypothesis** Keeping `_shadow_terminal` alive while tomato-committed returns ≈1.9 k/season on every
fired world.
**Experiment IDs** E165 (bar 76 + rescue), E166 (champion's 70 bar + rescue), with E167 as the
reachability probe.
**Observed result** gate vs `cha22_champion`: E165 R1 2W/1L/5T +467.1, R2 0W/1L/7T −142.0, fresh
0W/5L/11T −37.0, pooled +62.8 = **−80.4/seed against E164**; E166 R1 3W/1L/4T +538.2, R2 0W/4L/4T −877.0,
fresh 0W/8L/8T −321.8, pooled **−245.6** = **−124.0/seed against E157**.
**Reason for rejection** Damage is monotone in how committed the episode is (bar 70 loses 3.3× what bar 76
loses) because the shadow plan is built without the tomato/sheep workers' route obligations and therefore
*displaces* owed routes rather than adding liquidation. The abstention is protective as designed.
**Exact conditions** `tools/build_e165_shadow_rescue.py`, EOF re-definition of `_shadow_terminal` that pops
`state['committed']` for the call duration and restores it in a `finally`; no spine line altered (assert
`out.count("\r\n") == base.count("\r\n")`, 7482 both sides); probe `tools/e167_rescue_firing_probe.py`
(graft LIVE: `rescues_with_tomatoes=2` on 4/8 seeds; counter ceiling 2/episode because `:1096` is reached
only at step 712).
**Reopenable** no — the axis is closed in both directions. (LEDGER:438-500 (§16-§17).)

### H-023 The tomato sell stream needs to be dripped

**Hypothesis** `_v219` sells ~70-80 units in one stream; a price-gated drip (≤8 u/day while TOMATO ≥ ~85)
with residue to the terminal sweep captures the winners' 3.7 u @ $93.4 profile.
**Experiment IDs** E179 (probe, no build).
**Observed result** census on E164's two firing worlds: **8 clips of 6-20 units across days 26-29,
80 u/seat** — seed 7770000 d26 h14 6@177, h17 6@165, d27 h01 8@159, h20 6@154, h23 14@144, d28 h22
20@135, d29 h15 10@111, h19 10@100; seed 9990000 6@373, 6@354, 8@347, 6@347, 14@330, 20@323, 10@276,
10@247.
**Reason for rejection** The stream *is already* the winner-matched trickle shape, so there is nothing left
to re-time — §24's "still unspent" line was spent by a 2-seed probe instead of a build plus gate.
**Exact conditions** `tools/e179_tomato_clip_profile.py`, mirror, both seats, E164 as the vehicle.
**Reopenable** no on clip size; the question it exposed (the eligibility key) is H-024. (LEDGER:782-813 (§25).)

### H-024 The tomato gate's coverage is a calibration artefact

**Hypothesis** Keying eligibility on the realised window price instead of the day-18 quote would admit
profitable worlds and break the 26 ties.
**Experiment IDs** E180.
**Observed result** census over 32 gate seeds, champion only (sells zero tomato → unperturbed curve):
**0/13** worlds with <2 special shops reach a window mean ≥ $100 (all 13 sit at $63-80; ≥$60 13/13, ≥$80
2/13); Pearson **r(px@18, window mean) = 0.842** over n=32; window > px@18 on **32/32**, mean ratio
**1.57×**, and the ratio is itself shop-driven (thin towns 1.02-1.21×, 4-shop town 2.95×).
**Reason for rejection** The multiplier is the same demand signal measured twice — shops consume tomato —
so `c3 ≥ 2` plus bar 76 already admits every world in the 32-seed space where the realised price clears the
block's cost. The 26 ties are the town-shop schedule, and the tomato axis is now closed on margin (H-023)
*and* coverage.
**Exact conditions** `tools/e180_tomato_price_key.py`; log `gates_cha22/E180_price_key.txt`; break-even
level implied by E160 is a realised ~$119 (a 2-shop world with a day-18 quote of 64 realises 79).
**Reopenable** no — "do not re-open either one without a mechanism that changes the town's shop schedule,
which is engine-side and out of reach." (LEDGER:815-839 (§26).)

### H-025 A shed-aware sell-allocation layer (ZERO_TIE "HALF-A") closes the carrot/egg shortfall

**Hypothesis** Replacing fixed-mix SELL lines with per-step shed-aware sweep-alls recovers the −12…−13 k/day
allocation leak.
**Experiment IDs** E176 (census, no build).
**Observed result** census, cha22 mirror, seeds 1000000/2000000/3330000/5000000: peak shed held per game
CARROT 9.8, EGG 3.5, STRAWBERRY 5.5, MILK 4.5, WOOL 4.0, WHEAT 14.5, FERT 6.8 — **end-of-episode residue
0 units across all 8 seats**.
**Reason for rejection** The champion already emits full-shed sweep-alls (terminal liquidator `:6326`
`market.append(['SELL', it, int(shed[it])])` plus the day-level `_ig_close_queue` pass), so HALF-A is
already in this base and its −13 k premise is stale (it was written against FutureV1, before the tetsutani
queue layers were inherited). The carrot/egg shortfall is **production-limited** — i.e. the H-017/H-018 tape
channel — and the declared-out column (CARROT 151.8, FERTILIZER 1,855.8 per game) is 20-300× the peak
ever held, so reading it as volume violates the declared ≠ flow law.
**Exact conditions** `tools/e176_sell_flow_census.py`; also relevant: those two items are the only rows in
the winner table where realised price already matches and only volume is short (15.9@50.4 vs 3.3@51.3;
19.4@49.1 vs 12.8@53.7).
**Reopenable** no as a market-layer hole. (LEDGER:707-731 (§22).)

### H-026 Scaling the tomato farm by redirect or doubling (prior cycle, restated)

**Hypothesis** More tomato tile-days = more money, by plant-redirect or by doubling the blocks.
**Experiment IDs** `e57c`, `v20-passthrough-tomato`.
**Observed result** tomato plant-redirect **−138,266**; doubling tomato blocks **−9 k … −39 k per firing
world** from self-impact on a `sqrt` above-side curve.
**Reason for rejection** Own price impact; and every idle PASS tile is already route-owned, so an
idle-tile overlay has nowhere to land.
**Exact conditions** Restated as the admissibility constraint on any production dose (winner-matched,
tape/planner edit only) at LEDGER:97-102 (§6).
**Reopenable** no via these two constructions; confidence for the numbers is medium (prior-cycle ledgers,
not re-run here).

---

## C. Livestock / herd

### H-027 The sheep block only needs its shop clause relaxed

**Hypothesis** `_v233_eligible` is a tomato-style single-clause problem: relaxing
`count('YARN_STORE') >= 2` switches on a working mechanism.
**Experiment IDs** E171 (clause census).
**Observed result** census over all 64 day-11 hour-0…3 seat-samples of 8 mirror seeds: c1 quadrant
`32/64` (true only from hour 2), **c2a `YARN_STORE >= 2` = 0/64** (observed max 1, on 2/8 seeds), c2b
`WOOL >= 220` = 16/64, c2c `WHEAT <= 45` 64/64, c3 SE LOCKED 64/64, c4 no SHEEP held 52/64, c5 route-free
64/64, c6 money 64/64 — **`_v233_eligible` overall 0/64**.
**Reason for rejection** Three clauses are *mutually blocking in time*: by hour 2, when the quadrant set
first holds, the farm already owns a sheep (c4 flips to 0), and the price clause is satisfiable only in the
same two seeds that own a yarn shop — which is also where c4 fails. So `>=2 → >=1` changes nothing (still
0/64); reaching the block needs a re-timed investment schedule with its own cadence proof, i.e. an E148-class
mechanism priced at −38,644.
**Exact conditions** `tools/e171_sheep_gate_census.py` (log `gates_cha22/E171_sheep_census.txt`), calls the
real function for ground truth; instrument also covers the cow branch (`_v9_herd` `:3180`).
**Reopenable** yes via the clause, not the code — and that re-entry happened (H-028), closing the axis for
a better reason. (LEDGER:544-573 (§19).)

### H-028 Re-entering the sheep overlay through the relaxed `YARN_STORE >= 1` bar

**Hypothesis** Committing the block where the clause is the only blocker turns the 5 newly-committing worlds
into wins.
**Experiment IDs** E186 (census), E187 (verdict probe), E188 (gate), E189 (price key), E190 (unbuildable).
**Observed result** gate vs `cha22_champion`, pooled 32 seeds: **1W/8L/23T, −1,643.9/seed** — r1 0W/2L/6T
−2,020.1 (deltas −10,356, −5,805, +0×6); r2 1W/2L/5T −977.6 (−13,008, −5,062, **+10,249**, +0×5); fresh
0W/4L/12T −1,788.9 (−13,783, −12,968, −993, −878, +0×12). Price-key table over all 32 seeds: nine
newly-firing worlds all inside **one 20-point bucket** (wool 220-239, yarn 1) mean Δ **−5,845**, median
−5,805, 1W/8L.
**Reason for rejection** Inside that bucket the outcome swings from **+10,249** (r2/2220000, WOOL 221 /
WHEAT 39) to **−878** (fresh/30007000, WOOL 221 / WHEAT 39) at an *identical* quote, so no monotone bar K
with `yarn>=1 AND wool>=K` separates them — E190 is **not buildable**. What decides is herd/route capacity:
the block's own `WOOL < 220` clause plus routes' animal-maxed capacity. The donor's `>=2` is a *capacity
proxy that happens to work*, because two yarn shops only exist on routes with the sheep slot free.
**Exact conditions** `tools/build_e188_sheep_yarn.py` extracts the spine's `_v233_eligible` body verbatim,
changes only the integer, EOF-rebinds `_VE_ELIGIBLE` with
`assert mod._v233_eligible.__globals__["_VE_ELIGIBLE"] is mod._e188_ve_eligible`; `tools/e189_sheep_price_key.py`
re-ran all 32 seeds under the validated census protocol (errors 0, every non-zero delta reproducing the
gate to the coin).
**Reopenable** no with a price key — "Any future livestock attempt must carry a **route-conditioned**
capacity key, never a price key. Do not re-run E188/E189." (LEDGER:987-1036 (§31).)

### H-029 Restoring the `_v9_herd` call that the port dropped

**Hypothesis** The goose→SHEEP/COW herd rewrite present in every donor is missing from cha22, so wiring it
back is a free recovered capability.
**Experiment IDs** E172 (build), E173 (firing probe), E174 (reachability census), E175 (price-window census).
**Observed result** **0/8 R1 mirror seeds fire**, `herd_rewrites=0`, `herd_extra_sold=0`, `herd_errors=0`,
`species` unset; the wired candidate and `baseline_x1` (which ships the call live) produce **identical**
per-seed buy histograms (seed 1000000: COW ×12 @1-176, GOOSE ×4 @241-265, SHEEP ×8 @1-226 on both) and
**identical** scores (81,600 / 75,362 / 80,005 / 72,685), both reporting `herd_species='' rewrites=0`.
**Reason for rejection** A **neutral truncation**. The arm *is* reached (4 goose buys at steps 241-265 ≥ 216)
but `_v9_herd_choose`'s two bars are mutually exclusive with the world at days 9-11: seed 1000000 has
WOOL 148-189 (bar 150 met) yet no `YARN_STORE` and only 1 dairy shop where the COW alternative needs 3;
seed 2000000 has `YARN_STORE` + WOOL 233-238 but never buys a goose at step ≥ 216. Cost: 4 probe runs,
0 gate budget.
**Exact conditions** `tools/build_e172_herd_wire.py`, EOF rebinding of `_V9_HERD_PARENT` (occurs exactly
twice, `:3224`/`:3235`, no later layer re-binds it), +620 B, with a synthetic day-9 goose-purchase unit test
asserting `BUILD_COOP → BUILD_PASTURE`, `PICKUP GOOSE → SHEEP`, `['BUY_ANIMAL','SHEEP',3]`, EGG sale dropped.
**Reopenable** only as an investment-schedule change, not a wiring change; the lesson is the general rule —
measure the callee's own guard before calling a missing call a defect.
(LEDGER:675-705 (§21).)

### H-030 Herd capacity is reachable from the agent side (prior cycle, restated)

**Hypothesis** A planner can place more animals if it reasons about price/cash rather than routes.
**Experiment IDs** E104.
**Observed result** closed from the route side: **17 place / 9 COW-XOR-14 SHEEP routes, all at capacity**.
**Reason for rejection** The binding constraint is the route library's animal maxima, which no in-episode
decision can exceed (consistent with H-028's capacity-over-price finding).
**Exact conditions** Restated at LEDGER:1028-1032 (§31) and 572-573 (§19) as a constraint on livestock
candidates; the primary log is an earlier cycle's.
**Reopenable** no, unless the tape is regenerated with different place routes — which is H-018's channel.

---

## D. Land / labour

### H-031 Dig the weeds sooner: the last zero-cash-cost tile-day class

**Hypothesis** A weed tile the seat's own route later replants is free land; DIG-earlier is money already
on the table, sized at **$56,172 notional** (WHEAT $34,476 / CARROT $21,696).
**Experiment IDs** E178.
**Observed result** census (8 fresh seeds, 719 obs/step, pin + hinge asserted, mystery clears 0, recorder
errors 0): WEED tile-days lived 163.21 (seat0 79.68 / seat1 83.56); "recoverable" (own DIG **and** own
replant) 149.83 td = 91.8 %, 242 episodes; idle length weed→winning DIG n=242, min 1, median 14, **max 20**,
mean 13.9, **>24 steps: 0**, **>72: 0**; dead land 3.88 td = **$0**.
**Reason for rejection** Travel-bound: in **0 of 242** episodes did any of that seat's own units stand on
the weed tile on a turn the engine ignored (PASS, or a plant-op arriving on a weeded tile); 202/242 windows
were never visited at all and the other 40 contained a single move-through, which was the digger's own
arrival. The shipped `weed_repair` layer already fires 1 DIG/episode, so every convertible standing-noop is
converted; the remaining 0-16 steps need *re-routing a worker* — which is H-032.
**Exact conditions** `tools/e178_weed_idle_census.py`, cha22 mirror, output
`results/e178_weed_idle.txt` (`gates_cha22` chain log `results/e178_run.log`); replant lands 1-2 steps
after the DIG so there is no dropped-queue tail to recover either.
**Reopenable** no as a free lever; the priced version is the labour axis. Side benefit: it explains why the
E99 pasture port is *provably* inert (H-034). (LEDGER:841-872 (§27).)

### H-032 Labour re-routing buys tile-days

**Hypothesis** Moving a worker to an idle tile earlier converts the idle quantified in H-031.
**Experiment IDs** the `production-axis-fert-logistics` cycle (restated here, not re-run).
**Observed result** quoted as **0W/8L, −816** (bank not restated in these inputs).
**Reason for rejection** Labour is already saturated — the live-loss anatomy shows hires 267/292, 282/290,
276/288, 267/267, 281/281 and hands 11.4 vs 11.2, i.e. labour does *not* separate winners from cha22
(`results/E145_DIVERENCE_20260925.md:137`).
**Exact conditions** Restated at LEDGER:863-866 (§27) as the reason the residual weed idle is unreachable.
**Reopenable** no on this evidence base. Confidence **low-medium** inside this file: the primary log is not
part of these inputs, so the row is quoted, not verified.

### H-033 A terminal harvest / terminal liquidation overlay exists on this spine

**Hypothesis** Standing crop and shed residue at the death board are a class a tail fix can convert (and
`DROP` was read as the leak inside it).
**Experiment IDs** E192, E195, E154, E146.
**Observed result** census, 16 fresh seeds × 2 swaps, 32/32 games, swap determinism 16/16 byte-identical:
harvestable tiles/board 29.62 ($3,618.9) at index 680, 23.25 ($2,855.8) at 700, **0 / $0 at 718 and 719**,
boards >0 **0/32**; the 80 standing PLANT tiles are 100 % picked_then_rest (mean 4.00 picks/plant),
`standing_unpicked = 0`, `free_at_end = 0`, `never_matured = 0`; shed at death **0 units, $0 notional at
indices 700, 712, 715, 716, 717, 718, 719** with 9 SELLs emitted in the 716-719 window.
**Reason for rejection** There is no residue to convert; `DROP` is a *stow* (`kaggriculture.py:343-355`,
`take = min(n, shed_capacity − sum(shed.values()))`), the delivery half of harvest→shed→sell, and the
"cap reached" reading at 718 was the tool's own forward simulation. Consequence for the tie bar: "the tie
law is not satisfiable by a tail fix — any mechanism that must fire on every world has to act on an
in-season decision."
**Exact conditions** `tools/e192_season_end_standing_census.py`, `tools/e195_shed_at_death.py` (probe seed
30000000, both swaps); pure reads on `cha22_champion` in mirror games, no gate budget.
**Reopenable** only if a production change leaves a genuine tail (see R-013's reconsider clause).
(LEDGER:1189-1237 (§35).)

---

## E. Tape / port

### H-034 Port the E99 weed-deferred `BUILD_PASTURE` fix

**Hypothesis** A port of a fix that measured +4,838 / +6,065 on the defect seed transfers to cha22.
**Experiment IDs** E142 (and the anchor audit E137 §2(e)).
**Observed result** gate, **r1**: **0W/0L/8T +0.0**; probe 0 differing steps on seeds 1,000,000 / 3,330,000.
**Reason for rejection** The mechanism it repairs (a deferred DIG on a weed tile) no longer fires on this
spine at all, so a *correct* port is provably inert — E178 later explained why (H-031).
**Exact conditions** Chassis `_weed_repair` `:542`; anchor string at `:542-545` is verbatim the `ANCHOR` of
`tools/build_e117_v11_full.py:22-26`, and the patched marker
`queue[0][1][0] == "BUILD_PASTURE" and tile is None` occurs **0** times.
**Reopenable** no. (LEDGER:149 (§9), 868-872 (§27); E137DOC:145-148 (§2).)

### H-035 Port `_apex_precision_terminal_sweep` verbatim

**Hypothesis** Rule 2's second named mechanism is missing here and can be dropped in at steps 716-719.
**Experiment IDs** E154; re-tested at E195.
**Observed result** `tools/tape_diff_probe.py` → `differing=0 GRAFT INERT`, "and correctly so".
**Reason for rejection** With the correct field (`observation["private"]["shed"]`; `farm.shed` is null in
this build) the shed reads `{}` from step 713 onward while `_ig_close_queue` keeps *booking* 16-26 units per
turn into it (step 708 `{WHEAT 4, CARROT 3}` booked 0 … step 716 `{}` booked 26 … step 719 `{}` booked 18),
so there is no residual to liquidate; cha22's own `_t62a_agent` (`:6310-6332`) already fires from step 712
and replaces `action['market']`.
**Exact conditions** Donor `submission_apex_final.py:6825`, applied AFTER `ig_agent`, steps 716-719;
`tools/e154_residual_probe.py`.
**Reopenable** no — see also E144's def-diff, which shows both Rule-2 mechanisms are present in apex-final
and net-negative on 7 of 8 r1 seeds while winning one by +2,450. (LEDGER:250, 253-266 (§13); E137DOC:138-143
(§2); `results/E144_LADDER_20260925.md:62-69`.)

### H-036 The day-27 route pin and `_adv_future` re-point are constraints we can relax

**Hypothesis** Ablating route 2's `step >= 648` pin and re-pointing `_adv_future` at the live route frees
tail volume.
**Experiment IDs** E153.
**Observed result** probe 6 differing steps (LIVE); gate, **r1**: **0W/7L/1T, mean −17.9**.
**Reason for rejection** Live and worse: the pin is load-bearing, and it is the same geometry that makes
steps <144 and ≥648 shared by all 41 games — touching it has a 41-game blast radius.
**Exact conditions** `agents/cha22_e153_no_d27.py`; tape library `_ROUTES` at `:946`, 41 routes × 719 steps.
**Reopenable** no for this edit; tape surgery generally requires the aliasing proof E152 introduced (copy
routes, assert fired == planned). (LEDGER:249, 593-598 (§13/§20).)

### H-037 The E133 ladder results measured the champion

**Hypothesis** `agents/cha22_byte_identical.py` is the champion, so its ladder rows are usable.
**Experiment IDs** E133 (11 files, `ALLDONE 15:07:36`); corrected by E136/E140/E144.
**Observed result** all 11 rows dead. The truncated binary's own head-to-head is **0W/2L, −216** vs
`futurev1_forecast`.
**Reason for rejection** Its module-level `agent` binds the stack truncated at line **6282**, while the
champion's entry is `ig_agent` @**7467**; `cha22_champion.py` = donor + `agent = ig_agent` (sha1
`c17f23f64f7c5436491eae057aea1a770e2a65f7` vs `a8da73093c8e`). Gating against it measures a weaker stack.
**Exact conditions** Detector `tools/E140_probe_exports.py` (`inspect.getsourcelines(m.agent)[1]` vs the
deepest export, plus the EOF alias chain), validated on the known-bad control; a fleet sweep showed cha22
was the *only* affected pulled kernel (`agent_is_deepest=YES` elsewhere). Three donor copies
(`demand-preserving-turn-sale-timing.py`, `kaggriculture-master-engine-v3.py`,
`kaggriculture-multi-route-farming-agent.py`) are sha1-duplicates of the truncated file and were excluded
as opponents.
**Reopenable** no — but the detector must be re-run on every newly pulled kernel, because the failure is
silent. (LEDGER:31-38 (§2); `results/E136_CHA22_CHAMPION_LADDER_20260925.md:120-142 (§6-§7)`.)

### H-038 `pub_e94_omw_clean` and `friend_r78ub` are two different opponents, and the step-1 opening lever is a tie-breaker source

**Hypothesis** Their divergent `_ALT_MODE` opening branch changes behaviour against the champion.
**Experiment IDs** E136 §4 (pool triage / symmetry audit).
**Observed result** the two files differ by **13 lines** (`'HybridOpening'` vs `'EarlyCycle'` and its
step-0/1 wheat `BUY_SEED`/`BUY_PRODUCT` tape branch) yet produced **byte-identical per-seed Δ vectors on r1
AND r2** (+962.0 r1, +1757.8 r2 for both).
**Reason for rejection** The opening lever is inert in H2H vs the champion — a divergent-looking graft that
never fires — so the pool contains one opponent here, not two, and the step-1 opening axis is not a source
of tie-breaking.
**Exact conditions** 16 seeds × both seats per bank, pinned 1.32.7, both directions.
**Reopenable** only against an opponent whose own day-1 schedule is sensitive to the opening; not against
this pool. (`results/E136_CHA22_CHAMPION_LADDER_20260925.md:111-116 (§4)`.)

### H-039 `cha22_agent.py` is a new strong public kernel

**Hypothesis** A separately published cha22 file is a distinct rival worth sparring.
**Experiment IDs** E140 §3.6, E136 §7.
**Observed result** gate, **r1**, both directions: **0W/0L/8T, mean 0.0** — a perfect mirror.
**Reason for rejection** Behaviourally identical to the incumbent: 100 % def-set match, diff is a 6-line
attribution header plus a pass-through `def agent(...) return ig_agent(...)`; both resolve
`agent → ig_agent` (the donor through one extra Python frame). Do not add it to the sparring pool; do not
re-gate it as "new strong public kernel".
**Exact conditions** sha1 `0ea5941ccace52c3c05db7e7ab9ba1d18397376e`, 494,742 B, `agent` at L7492 →
`ig_agent`/`cha20_entry_agent`/`kaggle_agent` L7473.
**Reopenable** no. (`results/E140_NEWPOOL_VS_CHA22_20260925.md:45, 82-87, 106`;
`results/E136_CHA22_CHAMPION_LADDER_20260925.md:133-142 (§7)`.)

---

## F. Information / oracle

### H-040 Retarget `BUY_PRODUCT` to the cheap hour (E202, never built)

**Hypothesis** Buying is capacity-free (it consumes cash, not shed room), so the buy side is the one
direction the E194 sell-side law leaves open.
**Experiment IDs** E201 (measurement), E202 (**not built**).
**Observed result** oracle foresight **$3,026/seat-board** (same-day cheapest hour) vs **$173/seat-board**
at H=3 with no foresight ($179 at H=6, $188 at H=12) — **0.20 %** of a ~85 k bank, i.e. about the value of
the already-shipped +178/seed layer. Only 1,571 of 4,041 wheat units (39 %) have a cheaper quote within
three hours.
**Reason for rejection** Pre-registration required a "material H-limited gap"; $173 with a 3-hour oracle is
not material, and realising the oracle number requires knowing tomorrow's cheap hour today — the price-forecast
channel closed by E62/E63. The downside is also asymmetric: `BUY_PRODUCT` WHEAT feeds the application
schedule, so a missed buy is a lost tile-day (production, not storage). Note the second, independent
refusal on the buy side: `BUY_SEED`/`BUY_ANIMAL` pay fixed constants, so no phase story exists for seeds or
animals at all.
**Exact conditions** `tools/e201_fert_buy_phase.py`, 16 mirror games, 4,262 orders / 9,640 units, engine
caveat printed by the tool; FERT buys 375 orders / 1,402 units, modal hours 02/03/04, percentile median 54.1
(dead centre); wheat buys 800 orders / 4,041 units, modal hours 13/05/16/09/21, percentile **77.8**
[57.1, 93.5]; log `gates_cha22/E201_buy_phase.txt`.
**Reopenable** yes, only if a mechanism changes *supply* rather than timing (the direction R-015 leaves
open), or if the H-limited gap re-measures material on a wider seed bank. (LEDGER:1434-1479 (§40).)

### H-041 Forecast the price wave (prior cycle, restated)

**Hypothesis** The RNG is exposed, so the wave is predictable and any phase lever can be made causal.
**Experiment IDs** E62, E63.
**Observed result** closed: the world resets per episode, so **no forecast survives the step boundary**
(restated at LEDGER:1459-1461 (§40)).
**Reason for rejection** Prediction is impossible on this engine; every licensed phase mechanism is
therefore a *fixed clock rule* (e.g. `step % 24`), not a forecast.
**Exact conditions** Restated as a constraint, not re-run here.
**Reopenable** no; confidence medium inside this file (primary logs are prior-cycle).

### H-042 Feed the chassis a rival plan so `front_run` works (prior cycle, restated)

**Hypothesis** `front_run`'s only missing input is `opponent_plan`; feeding one unlocks the Rule-2
preemption.
**Experiment IDs** E108, restated in E146 §7.
**Observed result** refuted as **non-persistent** — and separately, `make_agent` (`:981`) passes no plan and
`:485` gates the branch behind it, so E137's `r36_debts` residue of 0 was never reachable.
**Reason for rejection** A rival plan cannot be carried across episodes by this architecture; reopening
requires feeding one in, which E108 closed.
**Exact conditions** LEDGER:125-128 (§7); E137DOC:100-124 (§2).
**Reopenable** no as a chassis path; the outer debt-ledger graft (H-001/H-008/H-011) is the substitute and
is itself capped.

### H-043 The seat-swap half of every gate is information-free

**Hypothesis** 8/8 r1 worlds with `c0 == c1` and `o0 == o1` to the dollar prove the two farms are
independent, so a gate is 32 samples not 64.
**Experiment IDs** E200 §39 (claim) vs E200 §42 (same instrument, two more banks).
**Observed result** r1 8/8 symmetric, **r2 6/8**, **fresh 13/16** → 27/32 = 84 % symmetric, 5/32 with real
seat effects up to **$476** between the two seats of one seed (r2/5550000 −174/+302; fresh 30005000
−35/+51, 30008000 −93/+61, 30009000 −119/+117 → mean −1).
**Reason for rejection** The claim was inferred from one seed bank — the documented failure mode "never call
an axis closed off one seed bank" — and the price-wave RNG is episode-global. Withdrawn consequences:
cancellation *is* possible, so a `+0` has three causes; and the second seat must stay in every gate.
**Exact conditions** `tools/e200_seat_split_probe.py`, `gates_cha22/E200_r1_split_probe.txt`,
`E200_r2_q8.txt`, `E200_fresh_q8.txt`, engine 1.32.7 asserted.
**Reopenable** no — the corrected statement (84 % symmetric, both seats retained) is the durable one.
(LEDGER:1406-1416 (§39), 1523-1549 (§42).)

### H-044 A single-seat price-path reconstruction can carry money claims

**Hypothesis** Modelling `market_price(item, own inventory)` seat-by-seat reproduces realised revenue.
**Experiment IDs** E145 §4 reconciliation.
**Observed result** modelled SELL credit / money-derived revenue = **1.0416** (cha22), **1.0403**
(winners), per-episode range 1.024-1.063, sign never flips.
**Reason for rejection** `_process_market` (engine 590-624) quotes both players at the same pre-commit
inventory per unit iteration, so when both seats sell the same item in the same turn the true inventory
advances 2 while the model advances 1: the path is a few percent too generous. Executed *quantities* are
unaffected.
**Exact conditions** 20 live episodes, reconstructed cash matched the replay `reward` column **20/20**;
unit-flow identity residual 1,144 units over 20 episodes × 9 items (~0.6 %).
**Reopenable** yes with a two-seat model; until then, money claims use exact seat revenue and per-item
prices are read as ±4 %. (`results/E145_DIVERENCE_20260925.md:149-157`.)

---

## G. Harness / provenance integrity

### H-045 Gate rows produced between 15:07 and 15:52 are evidence

**Hypothesis** Numbers from the shared `rank_env` during the session are valid 1.32.7 results.
**Experiment IDs** E141 (detection); affected: `gates_futurev1/E137_audit_cha22_ig.txt`, everything
E136/E139/E140 in the window, 4 `E133_*` logs.
**Observed result** no W/L rows usable: the harness had been pip-downgraded to **1.32.6** at 15:07:38
(site-packages `kaggriculture.py` mtime) and restored at 15:52.
**Reason for rejection** The only functional difference is the below-side price shape of **CARROT (target
1.00) / TOMATO (0.40) / EGG (0.40)**: `hinge` (linear until the scarcity gap passes T = 450/200/332, then
quadratic with `HINGE_GAIN 8.0`) on 1.32.7 versus `log`/`linear` on 1.32.6 — so a sell-timing or crop-mix
verdict on 1.32.6 measures a different game. Independent proof the pin is load-bearing: the same 4 seeds
read −2/−1/−8/**+31** (mean +5.0) on 1.32.6 and −2/−1/−8/**−4** (mean −3.8) on 1.32.7.
**Exact conditions** Quarantine list and restoration command recorded in §1; `tools/engine_assert.py`
RESULT=PASS after restore.
**Reopenable** never — off-pin artifacts stay quarantined. (LEDGER:6-23 (§1); E137DOC:252-257 (§4).)

### H-046 Engine-pin enforcement can live in procedure instead of code

**Hypothesis** Asserting the pin once at session start is enough.
**Experiment IDs** E141 remediation; also E136's venv incident.
**Observed result** the pin moved mid-session twice: once by a pip downgrade, and once because a pulled
public kernel `pip install`s the engine *at import time*.
**Reason for rejection** A start-of-session check cannot see either. Enforcement is now
`engine_pin_error()` in `eval_h2h` before dispatch (raising `SystemExit: ENGINE PIN REFUSED (gate not run)`)
**and** inside each worker after both agent modules import, plus `WARNING: gate incomplete - only N/M seeds
scored` so a gate can no longer report a silent verdict.
**Exact conditions** `tools/test_candidate_breakthrough.py`; every gate log prints the version measured at
that job's start (`tools/E140_gate_driver.py` re-measures per job).
**Reopenable** no; this is a floor, not a lever. (LEDGER:25-29 (§1); `results/E140_NEWPOOL_VS_CHA22_20260925.md:115-117 (§7)`.)

### H-047 A gate's log path and worker count are safe defaults

**Hypothesis** Shell-quoted log names in a chain, and 12 parallel workers, are harmless.
**Experiment IDs** E161 (log collision), E137 (OOM + spawn bug).
**Observed result** `'$a'_all.txt` expanded `$a` at launch, so both E161 "all" runs wrote
`gates_cha22/_all.txt` and the second destroyed the first — the E161 gate logs are gone. On the shared box,
12-worker gates die with `OpenBLAS error: Memory allocation still failed after 10 retries`, and a driver
without a `__main__` guard broke the Windows spawn pool
(`gates_futurev1/E137_R1_attempt_spawnbug.txt`).
**Reason for rejection** Both destroy evidence silently: one loses the row, the other leaves a partial run
that can read as a verdict.
**Exact conditions** Chains now use literal log names (`tools/e169_chain.sh`, `tools/e170_chain.sh`,
`tools/e198_tiefree_ladder.sh`, `tools/e205_q8_gate_ladder.sh`); gates run through
`tools/E137_gate_driver.py` with `workers=4` and single-threaded BLAS, pin asserted in the header; gates
never overlap because each tool owns a `ProcessPoolExecutor`.
**Reopenable** no. (LEDGER:411-417, 504-506 (§16/§18), 1341-1344 (§38); E137DOC:41-47 (§1).)

### H-048 Gating `mod.agent` proves what Kaggle will run

**Hypothesis** The offline harness imports the module and calls `mod.agent`, so a clean gate means the
deployed file behaves identically.
**Experiment IDs** E209.
**Observed result** the platform does not call `agent`: `kaggle_environments/agent.py:40-64` execs the source
and takes the last callable in insertion order. For `cha22_champion.py` the live name resolves to
`ig_agent`. A layer written as `_E137_PARENT = agent; agent = wrapper` would gate perfectly and deploy as
the unlayered donor — "Silent. Clean gates, zero regression, zero live effect."
**Reason for rejection** CPython keeps a re-bound key in its original slot; `del agent` + `def agent(...)`
moves it, which is why the sanctioned wrapper shape works at all.
**Exact conditions** Probe `tools/e209_live_entry_probe.py` replicates the platform exec and plays one seed
both seats using only the live callables; on the deployed file: `live=agent`,
`last3=['_E137_PARENT','agent','kaggle_submission_agent']`, `== gate agent: True`, live delta +1,363 with
18 preempts / 129 units (q8: +1,222, 10 / 80) — matching the gate's seed-1000000 rows to the dollar.
**Reopenable** no; run the probe on every candidate before every submit. (LEDGER:1765-1811 (§47); E206DOC:72-82 (§5).)

### H-049 Provenance assertions in builders are ceremony

**Hypothesis** Counting the anchor string once is enough to prove a graft landed on the right base.
**Experiment IDs** E137 builder hardening.
**Observed result** `"agent = ig_agent"` matches **twice** in the champion, because line 7481's
`cha20_entry_agent = ig_agent` contains it as a substring; only the newline-anchored count
`src.count("\nagent = ig_agent") == 1` is sound.
**Reason for rejection** A substring collision silently legitimises a wrong slice; combined with
`index`-vs-`rindex` on duplicated EOF markers it produces an *empty* layer that gates as a clean tie.
**Exact conditions** Builder proof table: sha1-locked base, `rindex`-bounded tail check, per-symbol counts
(`def _e137_preempt` == 1, `sym(` == 2 — def plus one call site, `_E137_PARENT = agent` == 1,
`del agent` == base+1), `src in out` append-only check, import-time `mod._E137_PARENT.__name__ == "ig_agent"`,
byte delta +4,937 B asserted > 1,500 B, geometry self-check (trigger set = 18 turns, first 263, last 671).
**Reopenable** no; these are the checks `AGENTS.md:28-32` demands, now with the two failure modes named.
(E137DOC:208-220 (§3); LEDGER:212-216.)

### H-050 A truncated-agent artifact is a strategy result

**Hypothesis** `cha22_byte_identical.py`'s −216 vs FV1 and E135's "86.8 % of SELL units off-wave, wave share
854/6486" describe the champion.
**Experiment IDs** E135 (wrong entrypoint), corrected re-run in E137's audit.
**Observed result** re-measured on the champion at pinned 1.32.7: off-wave SELL units **6,470** (not 4,426
as on 1.32.6), scheduled-wave (`step%24==0`) units **771**, off-wave share **89.4 %**, hour 1 1,201, hour 22
**1,146**, hour 23 **1,107**, beyond-plan unbooked **2,557** units, off-wave by item FERTILIZER 2,797 /
WHEAT 1,000 / STRAWBERRY 754 / MILK 632 / WOOL 520 / CARROT 398 / EGG 189 / MELON 180, 3 seeds, both seats.
**Reason for rejection** The original run pointed at a weaker stack; the corrected numbers are 1.5-11× the
per-hour volumes, which is what turned "the preempt is small but live" into "the hour-23 impact is already
spent by the spine".
**Exact conditions** `tools/e135_audit_cha22.py` re-pointed at `agents/cha22_champion.py`; logs
`gates_futurev1/E137_audit_cha22_ig_ke1327.txt` (pinned) and `E137_audit_cha22_ig.txt` (**quarantined,
1.32.6**).
**Reopenable** no. (LEDGER:40-49 (§3); E137DOC:155-184 (§2).)

---

## H. Capacity / production mechanisms (P10 engine-in-loop censuses, 2026-09-25 18:00–18:50 UTC)

Parent for every row: `agents/cha22_champion.py` (sha1 `c17f23f64f7c`), patched **in memory** by
`tools/p10_capacity_census.py` with per-patch occurrence assertions; 6 R1 seeds (1000000, 2000000, 3330000,
5000000, 6000000, 7770000) × both seats; vs `tools/_noop_agent.py` for the absolute profile and vs the parent
for the paired delta; pin `kaggle-environments==1.32.7`, `townCenterSellInterval=24`. The wrapper-only control
`W0` reproduces the parent to the coin. Full table: `results/P10_CAPACITY_CENSUS_20260925.md` §D.

### H-051 Relaxing the v219 land/tomato bars lets the spine buy capacity
**Hypothesis** We hold 3.14 quads because of the money (12,000), shop (3) and day (18) bars in
`_v219_qualifies` / `_v219_request`.
**Experiment IDs** E1_land_day18, E1_land_day11, E1_land_day07, E3_tomato_day18, C_land7_fertall.
**Observed result** vs-noop behaviour **byte-identical to the parent** (money 158,715, tile-days 1,245, quads
3.33); paired delta −7,178 (0W/4L/2T) at day 18, −864 (0W/1L/5T) at days 11 and 7, −4,232 with tomato kept,
−870 combined-with-fert.
**Reason for rejection** The clause is additionally gated on tape-matched labour
(`len(farm['hands']) + parent_hires == expected`) and `state['committed']`, so price bars cannot open it; where
it does act in a mirror world it destroys value.
**Exact conditions** `agents/cha22_champion.py:1264` money 12,000→7,000; `:1266` shops 3→1; `:1299` `day!=18`
→ 11 / 7; `:1324` `extra` reduced to `[['BUY_LAND']]`.
**Reopenable** no, as a parameter flip; only a labour-aware co-planner reopens the axis (see H-057).

### H-052 Buying the 3rd/4th quadrant earlier is the capacity mechanism
**Hypothesis** Field 9/13 at 4.00 quads with 3rd unlock at step 250–265 vs our 290; earlier land converts into
tile-days and money.
**Experiment IDs** W1_land_from265_r2500, W2_land_from240_r6000, W3_land_from180_r2500,
W4_land_from100_r1000 (outer `BUY_LAND` injection with telemetry fire counters).
**Observed result** **feasible and worthless**: quads_end 4.00, 3rd unlock step 252 (226 at maximal
aggression), fires 1.0–2.8/episode, tile-days 1,245 → 1,244 (1,242 at W4), hires 276 → 266, sold units
1,612 → 1,567, delta **−12,081 / −12,081 / −12,081 / −12,727**, **0W/6L on every variant**.
**Reason for rejection** Purchased tiles are never worked (R-027: our SE grows 0 tile-days on 448 available,
field converts 60–72 % per quadrant); land cost plus displaced hires is a pure loss.
**Exact conditions** reserve 2,500 / 6,000 / 2,500 / 1,000 above `LAND_PRICES[quads−1]`, from steps
265/240/180/100, `max_quads=4`, free market slot required.
**Reopenable** yes, but only with evidence that tile-days rise with quads *in the same run*; land timing alone
is dead (`rho(land3, money) = +0.11`, n=113, p=0.26; `rho(land4, money) = +0.24` with the sign backwards).

### H-053 The fertilizer whitelist (crops, ages, start day, caps) limits applications
**Hypothesis** Raising `V9_FERT_CROPS` / `V9_FERT_FIRST_DAY` / `_R51_INPUT_CROPS` to field intensity
(150–247 ops) is enough.
**Experiment IDs** E2_fert_day7, E2_fert_straw, E2_fert_caps, E2_fert_all.
**Observed result** `FERTILIZE` ops 93.3 → 97.7 (day 7), **93.3 with strawberry added (play byte-identical)**,
94.0 (caps), 98.5 (all three); paired delta −22 / +0 / −94 / −107; tile-days flat or down (1,240).
**Reason for rejection** Field data scales applications with money (`rho(fert coverage, money) = +0.52`) but our
limiter is the application slot, not the permission set (R-028).
**Exact conditions** `V9_FERT_CROPS = ("WHEAT","CARROT")` → +STRAWBERRY; `V9_FERT_FIRST_DAY` 14 → 7;
`_R51_INPUT_CROPS` (2,4,6)/(2,3,4) → (2,7,12)/(2,6,10).
**Reopenable** no for caps/days; yes only if ops rise ≥ 50 % without a purchase.

### H-054 We can buy the fertilizer the field applies
**Hypothesis** Supply is the binding constraint (R-015), so an outer buy rule reaches field intensity.
**Experiment IDs** G1_fert_buy_20_px30, G2_fert_buy_30_px45 (bar 30/45, stock < 10, steps 240–600).
**Observed result** **0 fires**: price test passes **0 of 361** eligible turns — FERTILIZER trades **57–89**
coins in that window (stock < 10 in 334, cash OK 350, free slot 346). DNA byte-identical to parent; delta
−186 / −530.
**Reason for rejection** A bar no market price ever crosses is not a lever.
**Exact conditions** `price <= 30` / `<= 45`, qty 20/30, `money >= price*qty + 4,000`, `len(market) < 10`.
**Reopenable** already reopened and closed by H-055.

### H-055 Buying fertilizer at market price converts into applications and money
**Hypothesis** With the bar at 62–75 (the observed band) purchases raise `ops_FERTILIZE` toward 180+ and money
with it.
**Experiment IDs** H1_fert_px62, H2_fert_px75, H3_fert_px75_straw, H4_fert_px75_day7.
**Observed result** fires 2.0–3.3/episode, sold units 1,612 → 1,646/1,670, market revenue 176,917 → 180,404,
spend 21,202 → 24,914; **`FERTILIZE` ops unchanged at 93.3** (97.7 only when `V9_FERT_FIRST_DAY` also drops);
delta **−554 / −768 / −768 / −699, 0W/6L on all four**.
**Reason for rejection** Bought stock is not applied — stock at application time and the one-per-worker
schedule bind (R-028); the purchase converts into volume at worse net.
**Exact conditions** qty 20, stock trigger < 8, steps 240–600, shed-room cap 100.
**Reopenable** no as a buy-side experiment; application-side (labour) evidence would be new.

### H-056 Tomato is the missing crop
**Hypothesis** 11/13 field teams hold 90–242 tomato tile-days vs our 0; the price bar (70) excludes it.
**Experiment IDs** E3_tomato_bar55 (70 → 55, money 7,000, shops 1); P11 Q4 statistics.
**Observed result** fires and changes the farm (tomato 57.7 tile-days, quads 3.83, hires 284, tile-days
1,245 → 1,303) but money vs noop **155,294 (−3,421)** with spend +2,978, and paired delta **+303 (3W/1L/2T)**
= noise. Field: OLS **−0.92** non-tomato tile-days per tomato tile-day (R² 0.53),
`rho(tomato, money) = −0.08`.
**Reason for rejection** Substitution, not addition; no money signal in replays or in the engine probe.
**Exact conditions** `agents/cha22_champion.py:1264` price literal 70 → 55; `:1266` shops 3 → 1.
**Reopenable** only under additional capacity, itself refuted (H-052); see also E152 (0W/8L −5,730.6) and
E118 plant-redirect (−138,266).

### H-057 The ~700-point gap is buyable capacity
**Hypothesis** Closing production/capacity explains the −708 rating gap to the current leader.
**Experiment IDs** P11 Q5/Q6 arithmetic over the P10 probes.
**Observed result** tile-day price within team **13.59 ± 18.13 coins** (n=132, R² 0.004, CI −22…+49); the $13 k
gap needs **+957 tile-days** (→2,203) and the $24 k gap **+1,766** (→3,012) against a hard ceiling of 3,000, a
field best team-mean of 1,562 and best single episode 1,755. Per-quadrant intensity ours 393 vs field best 390
tile-days/quad.
**Reason for rejection** Arithmetically impossible, and equal per-quadrant intensity shows the difference is
land count plus choreography, not throughput per tile.
**Exact conditions** deduplicated `results/p6_field_20260925/dna_p6.jsonl` (14 duplicate (episode, seat) lines
removed; champion tile-days 1,246, quads 3.17, bank-minus-start 88,072 — the undeduplicated 85,774 figure in
P6 is superseded).
**Reopenable** no for capacity volume. Reaching the field's choreography means engine-in-loop tape generation
with per-step legality (multi-day, unproven), and its static cousins are already dead here: E130-a…d, E131
(−4,133…−45,320), E152.

### H-058 Collecting more fertilizer is a source of money
**Hypothesis** `COLLECT_FERT` capacity (ours 377.5 vs field 394–503) is untapped supply.
**Experiment IDs** P11 Q3.
**Observed result** `rho(COLLECT_FERT, money) = +0.07` (n=132, p=0.43) and
`rho(COLLECT_FERT, tile-days) = −0.62` (p=4e-15).
**Reason for rejection** Collecting competes with growing and carries no money signal; the field's apps come
from stock it already produces and it barely buys (DSM $36, Vadim $0).
**Exact conditions** per-episode `ops_COLLECT_FERT` from `phase_p6.jsonl`, mean-centred per team.
**Reopenable** no.

---

## Note on non-lever entries

E204 is not a research direction and is therefore not registered above: it is the null-mechanism probe chain
(`tools/e204_null_mechanism.sh` → `gates_cha22/E204_chain.txt`, running
`tools/e202_null_world_dump.py` on worlds 7770000 / 5550000 plus the r2 seat audit) that produced the
mechanism behind H-001 and the correction behind H-043.

## Provenance

- `results/LEDGER_20260925.md` §1-§47 — every gate, census, dose and floor quoted above.
- `E137_C22_PREEMPT_20260925.md` §1-§6 — graft construction, builder assertions, fire proof, hour-23 census, pin-flip example.
- `E206_MW_H1Q6_AGENT_DOCUMENTATION_20260925.md` §1-§6 — lineage, layer doses, benchmark matrix, live-entry probe.
- `results/E140_NEWPOOL_VS_CHA22_20260925.md` — entrypoint resolution, pool gates, direction-mirror finding, BOM note.
- `results/E144_LADDER_20260925.md` — 8-challenger pinned ladder, antisymmetry check, apex-final def-diff (Rule-2 mechanisms net-negative on 7/8 seeds).
- `results/E145_DIVERENCE_20260925.md` — live-loss production/monetisation split, money-write law, model bias, labour parity.
- `results/E136_CHA22_CHAMPION_LADDER_20260925.md` — champion ladder, reverse-seat control, venv incident, donor dedupe, `_ALT_MODE` inertness.
- `results/e134_live/agg_out.txt` — DNA table rows used for H-026/H-032 context.
- `AGENTS.md` Rule 1 (phases 5-6), Rule 2, Rule 3 — gate tiers and the tie law that most rejections turn on.
- `E107_TICKDELAY_AXIS_20260924.md`, `E119_FERT_COVERAGE_PARITY_20260925.md`, `archive/stale_20260928/FINDINGS_DSM_BATCH.md`
  — consulted only to check prior-cycle fertilizer/labour numbers (H-030, H-032, H-033 context); where a number could not be verified in this cycle's inputs the row is graded low/medium confidence and says so.

---

## Addendum 2026-09-26 — P15 choreography probe

### H-059 — idle-labour coverage completion (re-task `PASS` hands into WATER / PLANT / walk toward the least-covered unlocked quadrant)
**Construction.** `tools/build_p15_quadcover.py` → `agents/p15_quadcover.py` (sha1 `2b58e6002bd5`),
append-only layer over `agents/cha22_champion.py` (sha1 `c17f23f64f7c`). Window steps 192-690;
trigger = a quadrant that is unlocked, has owned-empty tiles, and is below 55 % coverage; op order
WATER-under-foot → PLANT-under-foot-with-held-seeds → one step toward the nearest owned-empty tile of
the target quadrant. Only hands whose parent op is exactly `PASS` are touched; no money spent, no
market slot used, everything else byte-preserved. Liveness proven before gating (symbol asserts,
module import, telemetry keys, both-seat firing probe: `p15_turns 719, p15_fires 7, p15_water 3,
p15_plant 2, p15_walk 3, p15_no_seed 0, p15_errors 0`).
**Result.** R1 16 games **0W/6L/2T −2,842.5/seed** (worst −22,451); R2 16 games **0W/6L/2T
−2,894.5** (worst −20,762, −1,841); Fresh 32 games **0W/16L/0T −4,531.2** (worst −26,174, −24,381).
Log `gates_p15/P15_quadcover_r1r2fresh.txt`, engine pin asserted inside the run.
**Why it cannot work (state trajectory, not just sign).** Seed 1000000: day 8 `quads=2
planted=[19,18,0,0]`; day 15 `quads=3 planted=[14,18,25,0] empty=[0,0,0,0]`; day 22 `quads=3
planted=[15,17,25,0]`; day 29 `planted=[1,9,11] empty=[14,9,13]`. The 4th quadrant is never *owned*
in that world, so the motif's target state is unreachable, and the 7 fires that do occur land on
tiles the parent had just harvested in days 27-29, displacing the endgame plan — which is where the
−20k/−26k tails come from. 2/8 R1 and 2/8 R2 seeds are exact ties, i.e. the inert-world case R-003
predicts.
**Rejection condition.** Any runtime re-tasking of idle hand-steps into new-quadrant coverage on this
spine is rejected while (a) coverage requires an ownership event the tape does not already schedule
(R-035), and (b) mid-game owned-empty tiles are zero, so idle labour has no unworked land of its own
to convert (R-033). Reopen only for: a **route-selection** construction (prefer an existing
`_ROUTES` variant whose native `BUY_LAND` schedule reaches 4 quadrants by step ≤265), which is not
this construction and is not covered by H-052 (which changed the *buy*, at runtime).
**Related.** R-027 (bought land without a worker leg is never planted) — refined by R-035: our own
tape does plant and water SE at field intensity (25.5 % of plants, ep 113360259) when the buy happens
on the tape's own schedule, so the failure is the injection, not the geometry.

### H-060 — Land-cadence retarget (move the tapes' own `BUY_LAND` orders to the field's 220 / 254 steps)

**Construction (recorded so a retry can differ materially).** `tools/build_p16_cadence.py` →
`agents/p16_land_cadence.py` (sha1 `9207ab4ce12f`): the champion source verbatim, plus an appended
layer that, at import, deep-copies only the affected step dicts of `_IMPL.chassis.routes` (the
`_ROUTES` / `_R108_SHOP_ROUTES` module banks are left pristine) and re-times the land orders: delete
the `BUY_LAND` market order at step 265, append one at **220** and one at **254**, last in each
step's market list so it executes after that step's sells. No cash, no prices, no other order, no
layer, no crop, no market rule touched; the tape bank itself was never rewritten. Inert control with
the same layer disabled: `agents/p16_land_control.py` (sha1 `d7a210f3eb63`) — **0W/0L/12T, Δ = +0.0
on every column**, which is what makes the treatment numbers causal.

**Numbers.** 24 engine-in-loop games (pinned 1.32.7, `townCenterSellInterval=24`, 720 steps), both
seats, seeds 1000000/2000000/3330000/5000000/7770000/9000000.
**0W/10L/2T, mean −1,356.0/seat-episode, median −63.0**; per-seed −64, −64, −7,885, −7,885, −61, −61,
0, 0, −62, −62, −64, −64. Log `results/p16_landcadence/probe_p16.txt`, machine-readable
`games_p16.json`, report `results/P16_LANDCADENCE_20260926.md`.

**Why it fails (economic reason, measured twice).**
1. *Unaffordable in 5 of 6 worlds.* The engine refused the 2000-coin buy at step 221; SW was taken at
   255 for 2000 and the 4000 SE slot never fired. Our live games carry a median **939** coins at step
   220 (floor 859-906 over 216-290) but **12,777** at 254 — the money arrives ~44 steps after the
   field spends it. The field's 45 four-quadrant seat-episodes run the same block at 2-56 coins and
   buy with a median 591 on hand, because their sells/hires/seed plan is built around the land spend.
2. *Self-cannibalising in the one world that could pay.* Seed 2000000 reached the target state (quads
   at 151/221/255, SE owned 179 steps before the parent's 434) and lost **−7,885**: tile-days −3,158,
   harvest −41, water −79, hires −12, sold units −49, block revenue −1,815, block cash floor 230 vs
   1,019, SE plants 0 vs 10. The 6,000 of accelerated land came straight out of the same block's
   hire/seed budget, and the extra quadrant was never worked.
3. *Timing alone is worthless.* The pure subset (11 steps earlier SW, everything else identical)
   gained **0.0 tile-days** and lost 61-64 coins (R-040).

**Rejection condition.** Any construction whose only change is the *step* at which the remaining
quadrants are bought — tape-retimed, runtime-injected (H-059), or route-selected (R-037: 0/41 tapes
qualify) — is rejected on this spine while (a) our revenue plan leaves <2,000 coins at step ≤221 and
the engine prices the 3rd quadrant at 4,000, and (b) ownership converts to tile-days only through a
worker choreography that arrives with the buy, which no single-variable change can supply.

**Scope of this rejection.** It closes the **land / SE / quadrant-capacity line**, including the
proposed TapeForge tape-generation programme, whose premise was that the 150/220/254 cadence is the
missing causal ingredient. It is now measured as a **marker of a different whole-tape cash plan**,
not a purchasable advantage. It does not touch the ≤1-hour market-dose and field-pool items, and it
does not contradict R-035's parity findings — it explains them.

**Reopen only for:** evidence that a *different* spine (not cha22, not the cha22-era tapes) reaches 4
quadrants by 265 **and** works the SE quadrant at field intensity **while** its cash plan is unchanged
— i.e. a cadence that is affordable before any production is displaced. Nothing in this repository
currently offers that, and the 2026-09-30 deadline makes generating it out of scope.

**Related.** R-039 / R-040 (this experiment's laws), H-059 (runtime coverage completion, same target
state reached the wrong way), R-035/R-037/R-038 (ownership-per-episode, no qualifying tape, the
115-step gap), R-033 (dispatch parity — the reason tile-days did not move).

---

## Addendum 2026-09-28 — apex/V-era axis records (H-061…H-072), moved out of the working tree

These twelve directions were closed on the **Apex V5 → V11 → V28/V29 and FutureV1 spines**, not on
`agents/cha22_champion.py`. Their measurements lived only in root-level docs; the ledgers above carried
**zero** hits for `f90`, `labor`, `V28`, `V29`, `route-hunt`, `E102` or `shadow-price`, so the
constructions are restated here before the source files were moved to `archive/stale_20260928/`
(see `archive/stale_20260928/MANIFEST.md`). Nothing below is a live lever; every one is recorded so a
retry differs materially (`AGENTS.md` Rule 3). Engine pin for all of them:
`kaggle-environments==1.32.7`, `townCenterSellInterval=24`, `episodeSteps=720`, both seats per seed.

### H-061 Fert turn-substitution (V13-F `agents/pub_v57_apex_v13_fertmax.py`)
**Construction.** Zero-cost FERTILIZE substituted onto turns the engine was about to drop for want of
WATER, ROI-gated, season cap 240, pause tier disabled by design (`_V13F_PAUSE_MAX = 0`). Parent
`agents/pub_v57_apex_v11_dump.py`.
**Observed result.** Liveness A passed (`fert_injected` 2–6/ep, 30 over 8 episodes, 0 errors); volume B
failed: 948 emitted FERTILIZE vs V11's 924 in the same worlds = **+24 total, +3.0/game (+0.6%)**, margins
+24 +24 −74 −74 +35 +35 +27 +27. Never gated. DROP.
**Reason for rejection.** Census at seed 1000000: 957 zero-cost unit-turns, 797 standing on a PLANT, 52
tile-eligible, and **45/52 blocked by `carried == 0`** — the binding constraint is fertilizer
*logistics*, not wasted turns. The disabled pause tier had 392 would-fires but cost 4 real WATERs/seed.
**Reopenable** no for turn substitution. Only a supply-side construction (H-063's route) differed, and it
is closed too. (V13DOC §Ledger.)

### H-062 Marginal late-window hiring (V13-L `agents/pub_v57_apex_v13_labor.py`)
**Construction.** Days 14–26, hours 8–15, +1 hand/day when ≥6 urgent unwatered tiles were reachable from
the shed within 5 steps and native idle capacity was zero; self-commanded extra hands watered the nearest
urgent tile; cap 6 hires.
**Observed result.** Probe `hire_injected` 6/ep (cap hit exactly), HIRE 2,214 vs V11's 2,166 (+48 =
6/game, 266→272 hires), margins −720 −720 −1042 −1042 −720 −720 −665 −665, mean **−786.8**. Gate R1 vs
V11, 8 seeds both seats: **0W/8L/0T, mean −815.9** → DROP; screen aborted before R2/Fresh per the
`mean ≤ 0` rule.
**Reason for rejection.** The premise under-counted wage plus opportunity cost. 0 ties proves the layer
bound. "Do not re-run this construction." (V13DOC:21-32.)

### H-063 Fertilizer supply chain (V29, never built)
**Construction proposed.** Scheduled PICKUP + haul + tour funded from the existing labour budget, grafted
on `pub_v57_apex_v11_dump.py`.
**Observed result.** Refuted *before* construction by a mirror census (V11-vs-V11, R1 seeds
1000000/2000000/3330000/5000000, both seats): bought 83.0 (60–96), collected 373.5, applied 114.0,
stranded 0.1, end-shed 0, price $1.5 — supply 456 vs 114 applied, so the spine is a **~4× net exporter**
and `input_stock_shortfalls` reads 0.0/ep. Cap slack proved three ways: `MAX_WORKERS` 2→3→4→6 is
**byte-identical** (115.0 FERTILIZE/ep, 77,410 money) while the control `MAX_WORKERS = 0` collapses
applications to 29–36 and *raises* money +$941/+$1,153.
**Exact conditions.** The real cap is a chain, not a stock-out: crop whitelist `_R51_INPUT_CROPS =
{WHEAT, CARROT}` :2153 → ROI `value < 1.5*cost + 50` :2441 → min-3-per-slot :2437 → window gates
:2256-2262 → `_R51_INPUT_MAX_WORKERS = 2` :2152. Strawberry's 107 uncovered tile-days would lift
applications 114→~221 with **zero purchases and zero hires** (FERTILIZE ops STRAWBERRY 61.8 = 53.7%,
WHEAT 37.5, CARROT 15.8). Patching :2153 alone raises KeyError → total-action wipe; a retry must re-bind
`_r51_input_forecast` + `_r51_input_path` + `_r68_joint_plans` as one layer.
**Reopenable** only as that re-bind; not as purchase volume, not as turn substitution (H-061), not as
hires (H-062). (V29DOC §S1-S2c, §Do-not-retry.)

### H-064 Preemption floor retune 75/20/80 → 90/30/140 (E101t sweep, E102/E103)
**Construction.** `_apex_tuned_clone_preemption` on the V5 layer: fire at `step % 24 == 23` when the shed
holds ≥6 units and `price ≥ floor`, floors FERTILIZER/WHEAT/other; one `_T` dict
(`tools/build_e101t_variants.py`) so floors, window, trigger phase, min-stock and clip size sweep without
touching the 1 MB spine. Control `pub_e101t_ctrl.py` reproduced the known R2 defect 5W/3L/0T −54.2 with
the −592 tail, identical to `pub_e101_apex_layers.py`.
**Observed result.** R2, 16 games each: ctrl −54.2 (worst −592) · f85 85/25/110 +36.0 · **f90 90/30/140
7W/1L/0T +82.2 worst −2** · f95 +82.2 · f110 110/40/180 +36.1 · **f130 130/50/220 0W/0L/8T +0.0 = inert
layer, i.e. untested not passed** · w527 +51.1 · w575 −16.1 · q4 +0.0 worst −630 · f90q12 +64.8 ·
ph22 −57.6. R1: ctrl and f90 identical (+21.8, floors never bind). Fresh: ctrl +43.4 vs f90 +35.5.
R3 never-tuned: 0W/0L/16T +0.0.
**Reason for rejection.** It is a **tail-risk trimmer, not an earner**: +978 total seed-delta across 48
same-spine seeds, concentrated in two worlds. Also records a spine-placement error — the E99 spine is
weaker than V5's, so E101 sat *below* V5 however good its market layer (`build_e102_v5_tuned.py` fixes
exactly one constant line). E103 vs V5 across 65 seeds = 4W/1L/61T, +3,654 summed, never deployed.
**Reopenable** no: superseded by H-065 (the same dose on the next spine) and by the cha22-era few-worlds
law. (E102DOC:11-56, 88-149, 153-167.)

### H-065 `f90` — the 90/30/140 preempt as a champion candidate on V11 (V12)
**Construction.** `agents/pub_v12_preempt_f90.py` — correct name `agents/pub_v57_apex_v12_preempt_f90.py`,
1,079,709 B vs V11's 1,076,248 B (**+3,461 B** one layer): `["SELL", item, q]` at `step % 24 == 23` for
one item above floor (FERTILIZER ≥ 90, WHEAT ≥ 30, other ≥ 140), booked into a per-item **debt ledger**
repaid out of the spine's own step-24 order so total volume is conserved. Builder
`tools/build_v57_apex_v12_preempt_f90.py`.
**Observed result.** R1 7/1/0 +130.2 · R2 5/3/0 +262.8 · Fresh 9/7/0 +99.7 · fleet 117/27/0 (81.3%)
+213.9. Then a brand-new 32-seed holdout (`SEEDS_T3 = range(40000000, 40032000, 1000)`, disjointness
asserted in-process, driver `tools/holdout_t3_0923.py`): **15W/15L/2T, mean +87.7, median +0.0, exact
sign test p = 1.0000**, paired t = +1.43 p = 0.1622, Wilcoxon p = 0.2285, bootstrap 95% CI
**[−36.8, +199.6]**, sd 346.5, range −1,296.0…+786.0, pooled across all banks 36W/26L/2T p = 0.2131.
**Reason for rejection.** **30/32 seeds produced an identical f90−V11 delta in both seat orders**, so the
effective sample is 32, not 64 — Rule 2 seat duplication halves every bank. 11/15 losses were within 5
coins; one heavy tail (seed 40029000, −1,296, seat-reproducible). Removing that world post hoc lifts the
mean to +132.3 and is not admissible evidence. Verdict: **NOT ROBUST, V11 stays champion and deployed.**
**Reopenable** no, and it carries the standing gate rule: *do not gate any further sell-timing/market
overlay against this chassis on banks ≤ 16 seeds* (sd 346.5 needs ~120 independent seeds to resolve ±88
at 80% power). (T3DOC:3-96, 103-118.)

### H-066 Why the preempt dose cannot pay — f90 Fresh loss anatomy
**Observed result.** The 7 Fresh losses total **−19 coins** against +1,620 of wins; every loss is ≤0.004%
of score, and on 14/16 seeds both seats score identically → the layer's effect is intra-agent, not
competitive. Revenue by item was identical **to the dollar** for every non-WHEAT item on all three worst
losers; telemetry `preempts=6, repay_units=36`, every fire WHEAT.
**Reason for rejection (mechanism).** Every material win preempts wheat at price ≥ 42 (+926, +295, +194,
+161); **every loss preempts at 38–41**. Repay clips the parent's own hour 2–13 wheat at the same price
±1, netting −3…−5; the single real sub-defect is 415 vs 418 wheat units leaking out of the final
liquidation = −$123. FERTILIZER@90 never fires (h23 shed ≤10 and price ≤76 wherever shed ≥6: step 263
px 76, step 359 px 55-56) and MILK/WOOL/STRAWBERRY never hold ≥6 shed units at hour 23 — **those two
floor groups are dead code**; retire or reprice them before attributing any gate movement to them.
**Reopenable** only as the named next construction: wheat floor 30→42 plus a repay guard requiring ≥q
scheduled later-that-day wheat (never truncate a repay), or exempt the days-28-30 dump window.
(F90LOSS:13-88.)

### H-067 The V12→V26 market-overlay stack (one reference list, all closed)
v12_preempt(75/20/80) +130.2 weaker holdout · v12_pricedump −102.9 · v12_both +85.8 (**stacking cancels**)
· v14_drain −93.5 · v15_shedguard −19.5 (champion discards only 1–2 units/episode — there is no leak) ·
v16_pct −4,211.5 (held produce hits the 100-item cap) · v17_plant −16,923.4 · **v18_clip −106,821.0**
(price 46.6→70.4 while volume 1,560-1,662→392-640: withheld supply raised the *shared* curve the
opponent sold into; funding banked 132k–154k vs our 75k–111k) · v19_phase −2,201.6 (~1,088 units never
sold) · v20_tomato provably inert, 46/46 `blocked_tilelock` · v21_phase −1,162.5 (defers 1,829 units,
99.4% conservation) where f90 = +34.2 · v22_w42 +4.2/+1.8/+15.1 with 14/48 ties = **parity, not
progress** · v23_earlysw −1,113.2 and −5,705.2 vs f90 on Fresh (cash floor binds: first wheat inflow
~240–250 vs the 199–228 DNA band) · v25_revenuegate byte-identical on 15/16 seeds · v26_ob_preempt
−127.1 (host spine already clears the shed by step 23; layer fires ~1/7 as often) · v26_ob_dump −237.6
(252 proposed, 54 executed) · v26_ob_both −127.5.
**Law that survives.** Volume conservation is mandatory, not optional: only *re-timing* with a debt
ledger can pay, and any construction that withholds supply pays the opponent's curve. (F90CAND:53-119,
126-132.)

### H-068 Shop-composition → route table re-fit (V28)
**Construction.** `_R108_SHOP_ROUTES` is order-sensitive: 15 of 36 unordered pairs resolve to two
different routes (BAKERY|BRUNCH 103 vs 105, BAKERY|PIZZA 107 vs 120, BRUNCH|SMOOTHIE 105 vs 121). Graft
`agents/pub_v57_apex_v28_fitted.py` = 1,076,244 B base + 3,265 B layer = 1,079,509 B; selftest PASS on
('YARN_STORE','PET_CAFE') → 105 instead of the shipped 9. Route selection only affects steps 144–647;
forced route 2 at step ≥648.
**Observed result.** T1 census over 64 worlds: 42 ordered / 28 unordered pairs, 14 pairs occur in both
orders, the shipped table reaches only **20 of 41 routes**, 38 distinct tape clusters over 41 tapes, and
routes 0 and 2 correlate **+0.99** (difference ≤768). Resolution floor ~350/game vs the pre-registered
class bar (≥3 training worlds AND argmax beats shipped by ≥+500/game). **T2 oracle and T3 out-of-sample
never ran** — so this is an unstarted experiment, not a negative result; it is closed on the arithmetic
that a 16-world bank cannot re-fit a 64-key table.
**Also found dead:** `_R110_OLD_SHOPS` (64 keys), the `100` default, and `_V93_ROUTE_BY_RIVAL`
(rival_hit false 64/64). The YARN fall-through "bug" is not real. Prior forced-route evidence: E96 g8
force-101 = 3W/3L, g9 force-100 YARN = −35,436 / −25,645. (V28REFIT:46-199, 218-224.)

### H-069 Route-hunt E28–E65 — the largest do-not-retry set, previously recorded nowhere else
E28 regime-only forced route sweep: oracle +1,902.9/game over 16 worlds, but R2 +1,664.8 (4/2/2,
p = 0.6875) and Fresh +169.2 (8/5/3, p = 0.5811) → no promotion, "do not re-run this exact regime
intervention". E29 step-240 rival-(COW,SHEEP) switch, all four losses −1,008…−1,946, "do not tune this
mapping". E30 sheep→cow (≤2 purchases) −2,761…−8,282. E31 direct Majkel1337 tape 0W/8L/0T **−159,289**.
E32 livestock-action transplant, steps 0–359: −161,674 / −181,016 / −196,853 / −162,671. E33 stateful ROI
with 12% hysteresis (goose EV 3,032 vs cow −912) −3,254, "do not repeat fixed or price-only animal
swaps". E34/E35 goose HD2 and route-goose substitution: exact ties. E36 direct DSM tape 27,888 vs
156,092 — world-specific. E37 price-aware route score (step 145, threshold 2,000): +3.79M/+3.81M
*theoretical*, exact ties in play, "do not spend more time optimizing public route IDs". E40
native-boundary price router −40 / −56,794, "route scoring is closed". E41/E42/E43 step-0 selectors
(`initial_shops=''`, EGG=50/WOOL=200, goose_policy=0): exact ties, dormant. E44 cash-feasibility planner
R1 2W/6L/0T −1,781.1, "do not add more route-score terms". E45 idle marginal fertilizer: fires 0,
accepted 0, ties 81,232/81,232 and 75,186/75,186 = inert. E46 debt preemption (price ≥140, stock ≥6):
all inert, R1 0W/1L/7T −31.2. E47 SELL shadow-price ordering 4W/4L/0T +11.4 (−463…+356), reject; E48
trace inconclusive — do not tune sort direction without a fresh market-impact trace.
**⚠ The trap this entry exists to close.** The same ledger records **positive** verdicts — A7 sector
dispatch +52/+51, **A11 route memory +397/+409 ("first material throughput gain")**, A12 six-lane, A15
full-wheat +96/+80 — all measured against `pub_v57_apex_v11_dump.py` on seeds 1M/2M only, and **never
re-tested on the cha22 spine**. They are not live levers; `knowledge/CURRENT_STATE.md` classes the whole
V57/Apex lineage as mechanism history, not a bar. E50–E57's independent A1–A6 chassis (1,149–3,370 vs
V11's class) are rejected outright: A4 melon land 572 vs 841, A6 land 1,333 vs 1,149 cash sink, A5
price-threshold 8% rejected, E52 six-worker/land 2,113 vs 2,507, and E63/A13 eight-lane rejected
because "six workers is the current labour ceiling — do not add labour blindly". (ROUTE-HUNT:5-253.)

### H-070 V28 current-line herd grafts (inert pair)
**Construction.** Append-only herd-parity and herd-swap grafts from `submission.py` SHA-256
`6dc54cb6…6043`, after a 103-episode Kaggle pull (69W/33L/0T, mean live loss −2,115.9, worst episode
112547461 −18,972; opponents 8 COW/6 SHEEP vs our 5 COW/5 SHEEP).
**Observed result.** Herd-parity `buys = 0`, herd-swap `swaps = 0` → **both rejected as inert**, retained
as forensic artifacts only. On that spine V28 beat V11 8W/0L/0T +1,452.1 and lost to E94 1W/7L −1,151.6.
**Reason for rejection.** An overlay that does not fire cannot move score; historical Kaggle scores from
that era are explicitly treated as stale and not used as selection evidence. (V28CURR:4-21.)

### H-071 Overlay ceiling — the reason sell/tie-break layers cap at ±0.6%
**Observed result.** The market ALLOCATION leak (10 slots/day) prices at **−12k…−13k/game**, ~65–70% of
the margin; autopsied router losses of −19k/−19k/−7.6k occurred at **full production DNA parity** (hire,
fert, plant, water within ±2%) with 63–76% mirror classification. Tie-breakers move at most ±0.6%; only
constructions that change production on *every* seed produce zero ties (v57 0 ties/256 games, V11 0
ties/192). V11 fires 41% of its sell orders in hours 0–3 (the trough) where the top 10 sell at hours
22–23.
**Reason for rejection.** The phase/dump behaviour is already *inside* the public action tapes, so an
onion layer cannot reach it: reaching hour 22–23 selling requires **tape-internal surgery in the route
planner**, not a wrapper. A day-27 route override is inert by construction (route forced only at step
≥648). Consequence: the lever is tape *selection*, and only ~20 of 41 routes are selectable — overlays
are capped at ±0.35%. (ZTIE:8-47; TAPESDOC §1-3; F90CAND:78-82.)

### H-072 V11 live-loss cohort (forensic, superseded — do not re-derive)
37W/4L/… cohort read: three of four losses were settlement noise (80–91% mirrors). The two real gaps
priced exactly: sell routing town→market worth **+$4,700** (route-internal, hence H-068/H-071) and
fertilizer **bought** at the day-13 trough, +42 apps ≈ **$3,700**. Labour, land, water and dump-sizing
levers measured **$0**. Superseded by the cha22-era `results/P7_OUR_LOSS_ANATOMY_20260925.md` and
`results/E145_DIVERENCE_20260925.md`; kept so nobody re-prices a dead spine. (V11QUANT, V11FOR.)

### Addendum provenance
`V13_PRODUCTION_GATE_20260923.md`, `T3_HOLDOUT_F90_VS_V11_20260923.md`,
`V12_PREEMPT_F90_CANDIDATE_20260923.md`, `V12_PREEMPT_F90_LOSS_ANATOMY_20260923.md`,
`E102_PREEMPT_RETUNE_DOCUMENTATION_20260922.md`, `V28_SHOP_ROUTE_REFIT_20260923.md`,
`V28_CURRENT_LINE_FORENSICS_20260924.md`, `V29_FERT_SUPPLY_CHAIN_20260923.md`,
`LOOP_STATUS_20260923_V27_V29.md`, `ROUTE_HUNT_LEDGER_20260924.md`, `ZERO_TIE_STRATEGY_20260924.md`,
`TAPES_ARE_THE_STRATEGY_20260923.md`, `V11_LIVE_LOSS_FORENSICS_20260923.md`,
`V11_LIVE_LOSSES_QUANTIFIED_20260923.md`, `RESEARCH_PLAYBOOK_V23_TO_V26.md` — all now under
`archive/stale_20260928/`. Numbers above are transcribed from those files; none was re-measured on the
cha22 spine, which is why every entry is graded spine-specific.

---

## Addendum 2026-09-29 — MMPQ-port candidates on the cha22 spine (H-073…H-075)

Rule 27 session `E251_252_20260929/REPORT_E251_E252_20260929.md`. Engine pin asserted per log.
Field panel = E224's: `pub_dynroute85, pub_e69_soilrouter, pub_2945farm, pub_farmer_john_v56,
friend_r78ub`, seeds `16000000/16000137/16000274`, both seats, collapsed to 15 worlds.
Estimator: **absolute-field** (paired candidate−parent bank, same world).

### H-073 Guarded EGG-shelf herd reallocation (the Oracle's one surviving MMPQ port) on cha22
**Construction.** `tools/build_e251_egg_guarded.py` → `agents/cha22_e251_egg_guarded.py`
(sha256 `530FA64B1E140EBD…`, 506,651 B, +5,088 B append-only layer over `cha22_champion.py`).
Swaps the marginal `BUY_ANIMAL SHEEP`→`GOOSE` at day 6/9/10/11 hour 0, rewrites
`BUILD_PASTURE`→`BUILD_COOP`, funds a `BUY_PRODUCT WHEAT` top-up in the same atomic packet, caps
geese at 8.
**Observed result.** V3: **0/20 worlds differ, `refused_no_tile=12` — INERT**. V4 field: mean
**+0.0**, CI `[+0.0,+0.0]`, **REJECT**. `E251_252_20260929/out/p06_guard_debug.txt` shows why the
inertness is genuine: at every shop-unlock hour the spine has **0 empty tiles** (`empty=0`) and
emits **0 sheep/goose `BUY_ANIMAL`**.
**Reason for rejection.** The port needs a free tile to build on and a marginal animal order to
swap; the cha22 route library has neither on these seeds. This is `H-030` restated from the
wrapper side, and `E104b`'s −65,875 construction class reproduced. **`godview_v1` (the naive
SHEEP→GOOSE swap with no guards) additionally field-gated at −2,231.5/seat, 5/5 lineages negative,
worst −5,564** — the same class at larger amplitude.
**Reopenable** only as a route-level rebuild that reserves coop tiles and animal slots up front
(i.e. `E104` path B, a new tape), never as a wrapper on this spine.

### H-074 Tomato-lane unblock + relaxed V219 gate (e199 minus the market layer)
**Construction.** `tools/build_e252_tomato_carrot.py` → `agents/cha22_e252_tomato_carrot.py`
(sha256 `079CC3D0F7705670…`, 501,754 B). Relaxes the price/shop/money clause to
(`shops≥3 & px≥70`) OR (`shops==2 & px≥76`), money≥9,500; widens the day from 18 to 15–22;
`issuperset({'NW','NE','SW'})`; relaxes the `LOCKED`-tile clause to "no dict tile in rows 5–6 ×
cols 5–9". No carrot topup, no market layer.
**Observed result.** V3: **2/20 worlds differ, 0W/2L, mean −248.7**. V4 field: mean **+0.0**,
CI `[+0.0,+0.0]`, **REJECT** — on the gate's seeds the relaxed clause does not fire at all.
**Reason for rejection.** Consistent with `E224`'s ranking of the *same relax plus a market layer*
(`cha22_e199_lo96q8` = **−2,080/seat, 4/5 lineages negative**): the tomato relax alone is
mirror-positive and rare (E164 fresh 1W/0L/15T +35.4; E168 fresh +84.4 — below the repo's
≥$2,000/game bar), and with the market layer it is field-negative. Axis stays closed (H-056).
**Reopenable** only as the co-designed `tomato ≥ 8 AND crew ≥ 13` block (`E224` §4.4), never as a
bolt-on.

### H-075 `agents/cha22_godview_v1.py` is a promotable candidate
**Hypothesis.** The four-fix union (tomato unblock + relaxed gate + naive SHEEP→GOOSE swap +
carrot topup), built 2026-09-29 and documented in `CHA22_GODVIEW_V1_AGENT_DOCUMENTATION_20260929.md`,
is shippable.
**Observed result.** V1 PASS, V3 live (fires 62 goose swaps) but **6W/14L, mean −2,825.1, worst
−16,030** in the self-fight; V4 field **mean −2,231.5, favours 2/15, boot90 CI [−3,148, −1,361],
all five lineages negative, worst −5,564 → REJECT**.
**Reason for rejection.** It bundles a course-correct `issuperset` (but misses the second,
`LOCKED`-clause blocker) with the unguarded animal swap `E104b` already priced at −65,875, and it
never carried a rule-27 gate — `tools/validate_godview_v1.py` points `CANDIDATE_PATH` at
`cha22_e199_lo96q8.py`, so the log it produced validated the wrong file. `results/VALIDATION_GODVIEW_V1.txt`
decodes to an empty capture.
**Reopenable** no as a union; each clause is adjudicated separately above.

### H-076 EGG-shelf reallocation with the CORRECT buy window and the full packet (closes the axis)
**Hypothesis.** H-073's inertness was a trigger bug, not a spine limit: the cha22 spine emits
`BUY_ANIMAL` at hours 1,4,6,8,10,16,17 and **never at hour 0**, so E251 (gated on `step % 24 == 0`)
never saw a buy to swap. Move the same mechanism onto the real buy hours and move the whole packet
(buy + `PICKUP` + `PLACE` + coop), and the EGG-shelf reallocation should pay.
**Construction.** `tools/build_e251b_egg_realhour.py` -> `agents/cha22_e251b_egg_realhour.py`
(sha256 `E1F92515D387C928...`, 505,560 B, append-only layer over `cha22_champion.py`). Fires on any
hour for days 0-15; swaps `BUY_ANIMAL SHEEP`->`GOOSE` (cap 12), retargets the tape's own
`PICKUP`/`PLACE SHEEP`->`GOOSE`, converts one `BUILD_PASTURE`->`BUILD_COOP` when a coop is owed.
**Observed result.** The trigger fix is confirmed: `fires_swap=92, fires_pickup=116, fires_place=100,
fires_coop=44`, banks differ from the parent on **20/20** worlds, `errors=0`. But the result is
**0W/20L, mean -64,241.1, worst -115,456** (candidate 20k-54k vs parent 85k-136k on every world).
**Reason for rejection.** This is `E104b`'s -65,875 failure class reproduced **by a construction that
fires correctly**, i.e. the loss is not an inertness artefact. The tape-locked choreography is the
binding constraint: the spine's worker schedule, coop/pasture geometry (GOOSE 4/COOP vs SHEEP
6/PASTURE) and its YARN_STORE sell stream are co-designed around the sheep line; retargeting the
animal packet desynchronises the animal logistics chain and starves the wheat/crop engine
(`H-030`, `E104` path (A) verdict). The window bug is recorded for future builders: **measure the
spine's real op hours before gating on `step % 24 == 0`.**
**Reopenable** only as `E104` path (B) - a purpose-built route tape that co-designs herd + feed +
labour + structure geometry up front - never as an append-only wrapper. The wrapper route is now
closed at two different constructions (inert, then correctly-firing-negative).
**Provenance.** `E251_252_20260929/out/p10_animal_timing.txt` (the real buy-hour trace),
`p11_e251b_census.{txt,jsonl}` (fires + per-world deltas),
`E251_252_20260929/REPORT_E251B_20260929.md`.

### H-077 The E224 5-lineage rule-27 panel is reproducible (environment record)
**Observed result.** Mid-session the operator pruned stale files and the panel members
`agents/pub_dynroute85.py`, `pub_e69_soilrouter.py`, `pub_2945farm.py`, `pub_farmer_john_v56.py`
(and `pub_metav4_r78u.py`, `pub_e94_omw_clean.py`, `pub_v57_funding.py`) were removed from disk,
leaving only `__pycache__/*.pyc`. `agents/friend_r78ub.py` survives.
**Consequence.** Any *new* rule-27 V4 gate run after 2026-09-29 must rebuild or re-pull its
opponent panel first; the E224/E253/E254 numbers on record are **not** re-derivable in-tree.
Our own files were unaffected: `submission.py` and `agents/cha22_champion.py` remain
byte-identical, sha256 `A0031C0DDE7E157D...`.
**Reopenable** yes - `tools/extract_live_opponents.py` + `tools/fetch_episodes.py` re-pull from the
live API, and the kernel-pull path in `WybeV2/kernels_pull/` still carries several of the lineage
families.

---

## Addendum 2026-09-29 (2) — the pulled tetsutani "Step1009" kernel (H-078…H-080)

Source: `kaggle kernels pull tetsutani/demand-preserving-turn-sale-timing` ->
`kernels_pull/tetsutani_demand_preserving/`. Notebook cell 9 carries a base85 tar whose pinned
hashes **verify exactly**: archive `33532d53ca12d49f…`, `main.py` `55be5d5f124c8daa…` (1,196,081 B),
members `[LICENSE.txt, NOTICE.txt, main.py]`. Engine pin asserted per log: `1.32.7` / `interval=24`.

### H-078 The 41-pass fixed-sell closure chain can be extended by one more pass (step1010)
**Construction.** `tools/build_e261_step1010.py` -> `agents/cha22_e261_step1010.py`
(sha256 `1c8bb3310bd49198…`, +1,307 B). The kernel is 41 chained
`..._final_fixedsell_closure_agent` wrappers, each calling `_s793_reorder` on its parent's action;
step1010 appends the 42nd with the identical body (no threshold/model/item/quantity change).
**Observed result.** V1 PASS. V3: `calls=2157, changed=2, errors=0`; direct self-comparison
2/3 worlds differ, margins `+183 / 0 / -116`.
**Reason for rejection.** `_s793_reorder` is **idempotent at this point** - the chain has reached a
fixed point, so the 42nd pass touches ~2 turns per season and cannot move a score (rule 25). This is
why the author stopped at Step1009. **The family tweak ("apply one more pass") is exhausted**; a
further pass is not a lever. Provenance: `E251_252_20260929/out/p22_step1010_census.txt`.

### H-079 Step1009 is a promotable upgrade over `cha22_champion`
**Hypothesis.** The pulled kernel is measurably stronger than our deployed file, so it should replace it.
**Observed result.** Head-to-head it does win: **8W/2L, mean +564.4/seat** vs `cha22_champion`
and **10W/0L, +600.2** vs `sluice_topup7` (5 unseen seeds, both seats, identical banks across seats).
But the **rule-27 V4 absolute-field gate FAILS**: n=12 worlds, **mean -559.4**, median +90.5,
favours 8/12, worst **-8,213.5**, boot90 **[-1,934.9, +226.5]** -> CI includes 0, one lineage
negative, worst < -1,000. The remedy pass (drop the carrying lineage) **moved** the negative from
`p15_quadcover` to `p16_land_cadence`, i.e. it is not lineage-specific.
**Attribution.** Exactly **one world carries the whole deficit**: `p16_land_cadence / seed 22003000`
at -8,214; the other 11 worlds average **+136/seat**. On that world step1009 scores 118,162 vs the
opponent's 117,938 - **it wins** - while `cha22_champion` scores an outlier **126,409**. So the loss
is cha22's outlier-good world, not a step1009 collapse. Timing defect **ruled out**:
`actTimeout=1s`, step1009 max call 257-768 ms, `errors=0`, all-PASS turns 3/3 in both worlds
(`out/p23b_timing_probe.txt`).
**Reason for rejection (as a promotion).** Rule 27 V7 fails: the CI includes zero and the worst
world breaches the floor. It is a high-variance near-peer, not a validated upgrade.
**Reopenable** yes with more worlds: the direction on 11/12 worlds is positive (+136/seat), so a
larger panel could resolve whether the one-world -8.2k is a tail or a fixed weakness. Do not promote
on the head-to-head +564 alone - that is the H2H-vs-field divergence the repo already documents
(E222: "+638 mirror while field reads -641").

### H-080 Step1009's edge over cha22 is entirely sell-side (profile)
**Observed result.** Both spines are **identical on production**: quads 3.3 = 3.3, tile-days
30,627 vs 30,601 (+26), plant ops 242.3 = 242.3, builds 19 = 19, herd COW 6.7 = 6.7. The whole
+912/seat gap (3-seed mean) is the sell side: step1009 sells **686 FERTILIZER units vs cha22's 2,359
(-1,673)** and issues **598 market orders vs 628 (-30)**. FERTILIZER's shelf is 493 units, so cha22
runs ~4.8x the shelf per season; step1009 is closer to shelf-appropriate on the item where they
differ most.
**Note.** This *correlates* the difference but does not attribute the +564 to FERT alone (the two
files are different lineages, not one-lever variants). A FERT-sell cap on cha22 would be the causal
test, and rule R-001 ("WHEAT/FERTILIZER fires are round-trip neutralised to exactly $0 by the
opponent's own `BUY_PRODUCT`") plus H-025 already make that a closed axis - do not re-litigate it
without a materially different construction. Provenance: `out/p21_step1009_profile.txt`.

### H-081 RESOLUTION: the E262 panel was spine-contaminated; a clean panel REVERSES H-079
**Construction.** `tools/…` n/a. Two audits + a re-run:
`E251_252_20260929/p24_lineage_audit.py`, `p24b_lineage_audit2.py`, `p25_panel_screen.py`,
`p26_clean_field.py`.
**Observed result.**
1. **Panel audit** (byte-identical prefix vs `cha22_champion` + def-set Jaccard):
   `pixelx_v2.py` prefix **501,563 = cha22_champion's entire length** (J 0.946);
   `p15_quadcover.py` prefix **501,563** (J 0.952); `p16_land_cadence.py` prefix **501,563** (J 0.994);
   `friend_r78ub.py` J **0.760**. Every opponent in E262/E263 shared the control arm's spine, so
   **E262 was not a rule-27 V4 field gate at all** - it was a clone match. (`opponents/*` had also
   been pruned away.)
2. **Clean panel** - 6 lineages audited unrelated to BOTH arms and screened loadable+alive
   (`hesoponyo-pure-rl-agent-bc-ppo`, `pioneers_town`, `ice_and_fire`,
   `goodpjw2008-melon-threshold-squeeze-2749`, `alperen5252525-market-rhythm-sale-policy`,
   `nathanjacob-pipe-8-clean-opening`), 4 unseen seeds x both seats (n=24 worlds):
   **step1009 vs cha22_champion = mean -1,530.7, median -822.5, favours 7/24, worst -11,230,
   boot90 [-2,667.4, -540.1], 5 of 6 lineages negative -> V7 FAIL.**
   Mean absolute bank: step1009 **97,486** vs cha22_champion **99,017**.
**Reason for rejection.** H-079's head-to-head **+564/seat does not survive a valid field panel**;
on unrelated lineages step1009 is **~1.5 k/seat WORSE**. This is the repo's documented
H2H-vs-field divergence reproduced exactly (E222: "+638 mirror while the field reads -641"). It also
shows *why* the head-to-head flattered step1009: cha22 is itself **tetsutani-derived**
(`agents/donor/tetsutani-demand-preserving-turn-sale-timing.py`, 460,005 B, J 0.672 vs cha22), so
step1009-vs-cha22 is a near-family match decided by the sell-timing race that step1009 specialises in,
while its farm is weaker against genuinely different lineages.
**Verdict.** `cha22_champion` stays. **Do not ship step1009.** `submission.py` unchanged
(sha256 `A0031C0DDE7E157D...`).
**Lesson for the ledger.** A byte-prefix + def-Jaccard audit of every panel member against BOTH arms
is now mandatory before any V4 gate is quoted - a clone panel silently converts a field test into a
mirror test and can reverse the sign. Also: `agents/_top_pub/_raw_pilkwang_kaggriculture_structured_economic_policy.py`
does not even load (`SyntaxError`); screen loadability before including an opponent.


## Addendum 2026-09-29 (3) — the tetsutani Godview V2 graft and three farm-side counter arms (H-082…H-085)

### H-082 `agents/tetsutani_godview_v2.py` (submitted as ref 56672630) is a 100 % inert graft

**Construction.** `tools/build_tetsutani_godview_v2.py` appends one wrapper on
`kernels_pull_20260929/tetsutani_step1009_fortyfirst_closure.py`: (a) at `step % 24 == 23` sell the first
non-empty shed item among MILK/WOOL/EGG/TOMATO/CARROT/STRAWBERRY/MELON/WHEAT, and (b) at
`120 <= step <= 480` buy 2 TOMATO/CARROT seeds alternating by day when `money >= 250`.
**Why it is inert.** Both mechanisms are guarded on `isinstance(action, list)`, but the spine returns a
**dict** (`action['farmer']`, `action['hands']`, `action['market']`) - the spine's own telemetry block
reads `action['hands'][0] == ['DROP']`, and every action recorded in a live replay is a dict. Layer (b)
additionally reads money from `observation['private']['farm']['money']`; `observation['private']` has only
`inventories`, `seeds`, `shed`, so money is permanently `0` and the branch is unreachable.
**Evidence.** Gate 0W/0L/32T over 64 games vs its own parent (all ties = never tested, AGENTS.md Rule 2).
Live: 55 episodes 40W/12L/3T at mean margin **+10,267**/episode vs the parent's 135 episodes at +2,093 -
i.e. the file did not regress in dollars; its lower `publicScore` (1568.3 vs 1851.7) is the rating-schedule
artifact documented in `E253–E255` (fresh row starts near a 700 prior, needs ~130 games).
**Law to keep.** A fire counter must count **mutations applied to the returned action**, after the type
guard, never opportunities seen before it. Report `_FIRES` without a `converted`/`applied` companion is
how an inert layer ships as a validated one.

### H-083 Idle-hand herd-throughput layer on the tetsutani spine (E257)

**Construction.** `TETS_COUNTER_20260929/build_e257_fertflow.py` -> `agents/tetsutani_e257_fertflow.py`
(1,198,759 B, sha256 `979522c9…`). For each unit slot whose committed op is exactly `["PASS"]`, read the
tile under it (`farm['tiles'][pos[1]][pos[0]]`) and that unit's own inventory
(`private['inventories'][idx]`, idx 0 = farmer), then convert to `COLLECT_FERTILIZER` (animal tile with
`fertilizer_available`), else `FEED` (animal tile, `fed_today` false, carrying WHEAT), else `FERTILIZE`
(PLANT tile with `fertilized_until_day < day`, carrying FERTILIZER). Engine legality
`kaggriculture.py:475-521`; no market order added, no committed op displaced.
**Liveness.** PROBE PASS: 51-68 conversions/game (`collect` 37-56, `feed` 8-10, `fert` 4), errors 0, no ties.
**Gate.** H2H R1 vs the parent: n=16, **0W/8L/0T**, mean **−366.9**, per-seed deltas −67 … −586. Paired absolute vs
4 out-of-fleet lineages, 4 fresh seeds × both seats (32 rows): mean **−79.1/seat**, median −29.0, 11/32 favour,
worst −458; every lineage negative (−31.8 … −138.9).
**Reason for rejection.** Shed capacity is 100 units (`_drop_inventories_to_shed`, `kaggriculture.py:843`).
Collected fertilizer is inventory, so extra collection displaces produce - the same "shed is not a bank"
law measured on cha22. The winners' higher `COLLECT_FERTILIZER`/`FEED` rates are a **consequence** of a
bigger herd and higher throughput, not an action a wrapper can buy. Do not retry collection- or
feed-forcing on this spine; the reopen condition is an arm that also raises the shed release rate.

### H-084 Paid-fertilizer buy veto on the tetsutani spine (E258)

**Construction.** `TETS_COUNTER_20260929/build_e258_e259.py` -> `agents/tetsutani_e258_fertbuy_veto.py`
(1,197,700 B, sha256 `b5f6a2b2e70e4b31`, `py_compile` PASS, +1,619 B over the parent). Drop every
`["BUY_PRODUCT","FERTILIZER",n]` market order when shed FERTILIZER + carried inventory across units >= n.
Nothing added, cash kept.
**Liveness.** 25–27 fertilizer orders seen per game, 15–19 dropped (42–53 units), errors 0, no ties.
**Gate.** Paired absolute vs 4 out-of-fleet lineages, 4 fresh seeds x both seats (32 rows): mean
**−374.8/seat**, median 0.0, 12/32 favour, worst **−3,075**; lineage means −618 (friend_r78ub), −256 (a13),
−712 (oblate_orderbook), +87 (a15). Probe seeds −255 and −1,718 vs the parent.
**Reason for rejection.** The veto is not a saving: the spine consumes the purchased dose within a few steps,
so blocking the buy starves an application and the yield loss exceeds the price. The 104-vs-17 buy
asymmetry seen in the losing replays is a symptom of a different herd size, not an independent mistake.

### H-085 Idle-hand replant on the tetsutani spine (E259) - positive mean, bimodal, rejected

**Construction.** `agents/tetsutani_e259_idle_replant.py` (1,198,693 B, sha256 `3db88f1d3d701435`). A hand
whose committed op is exactly `["PASS"]` standing on an owned-empty tile (`tiles[y][x] is None`) plants the
first crop with seeds left in `private.seeds`, order TOMATO > CARROT > MELON > STRAWBERRY > WHEAT, counted
locally so the observation is never mutated. Attacks the measured `tile_days_empty` +727 / `op_PASS` +112 /
`td_TOMATO` −1,184 signature of the heavy losses.
**Liveness.** 9 and 17 conversions per probe game, errors 0, no ties (both probe seeds lose: −1,290, −3,288).
**Gate.** Pooled paired absolute mean **+615.5/seat**, but median **−2,101.5**, win share 9/32, worst row
**−31,280**; lineage means +3,551 / +1,322 / +3,547 / **−5,959**. Rule fires three times over (worst row,
negative lineage, win share) - REJECT.
**Reason and the one reopen condition.** Two worlds carry the whole mean (few-worlds law), and a planted tile
spends that worker's water/labor budget, which is why `a15_full_wheat` loses 5,959/seat on the same layer.
Reopen only with a seed-and-day-windowed variant that plants only a crop whose seed would otherwise stay
unspent at episode end, screened on >= 8 seeds with the per-row distribution printed beside the mean.

### H-086 Collect-AND-dump fertilizer on the tetsutani spine (E260) - the control that closes the axis

**Construction.** `TETS_COUNTER_20260929/build_e260_collect_dump.py` -> `agents/tetsutani_e260_collect_dump.py`
(1,198,921 B, sha256 `2792aff95c0616e4`, +2,840 B over the parent, `py_compile` PASS). Leg 1 as H-083 but COLLECT only (idle hand on an animal tile
with `fertilizer_available`). Leg 2, the new part: cadenced surplus release - when shed FERTILIZER > 5 and
`step % 4 == 3`, append `["SELL","FERTILIZER", min(stock-5,12)]` to `action['market']` (legal because
`TOWN_CENTER_PRODUCTS` excludes FERTILIZER, `kaggriculture.py:114`).
**Liveness.** 25 and 70 collects with 7 and 6 sell orders (23 and 13 units), errors 0, probe seeds −58 and −20.
**Gate.** Paired absolute, 4 out-of-fleet lineages × 8 fresh seeds × both seats (128 games, 128 OK): n=64 rows,
mean **−12.7/seat**, median **0.0**, worst −605, best +306, win share 39 %; lineage means +11.2, −15.2, −58.3,
+11.5. REJECT under the fixed bar (needs a positive pooled mean).
**Why this is the useful result.** E260 isolates H-083's loss mechanism: with a release valve the same
collection arm moves from −79.1/seat to ≈0, so all of E257's damage was shed displacement, and what is left of
the fertilizer-throughput idea is worth nothing. The spine does not monetise extra collected fertilizer because
its tape does not schedule the applications that would consume it - and E258 proves the demand it does have is
already met by market purchases (vetoing them costs 375/seat).

**Axis verdict for the tetsutani spine (E257+E258+E259+E260).** The four farm-side mechanisms the replay
anatomy named are all measurable and all wrapper-expressible, and none pays: the deficits are properties of the
tape's herd size, shed release rate and water/labor budget, not free actions a wrapper can add. Do not build a
fifth sell- or hand-side overlay on this spine; the remaining route is tape generation (as on cha22, H-060/H-071).





