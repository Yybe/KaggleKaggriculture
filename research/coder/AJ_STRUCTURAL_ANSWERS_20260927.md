# A–J STRUCTURAL ANSWERS + §22 TapeForge RE-EVALUATION — CODER/Qoder, 2026-09-27

**Status: §5 answered end-to-end on measured evidence. §5J = NO, the architecture cannot express the
required strategy, so the recommendation is an architecture change, not another patch. §22 answers all
seven questions and names the one cheap census that settles TapeForge — CQ-7 is running it now.**

Evidence base, all read this cycle or produced by it: `results/p17_realisation/REPORT.md`,
`results/p18_curve/REPORT.md`, `results/p19_release_hist/REPORT.md`, `results/p20_opencheck`,
`results/p25_oppmix/REPORT.md`, `results/p27_basket_regimes/REPORT.md`,
`results/p28_tape_divergence/REPORT.md` (mine, exec model asserted 0 mismatches / 85 replays),
`research/coder/RATCHET_FINDING_20260926.md` + `RATCHET_RETRACTION_20260926.md`, E94–E210 gate logs.
Three of my own earlier claims are retracted on this evidence (mix, rate, tomato +16-24%) — see
`research/coder/RATCHET_RETRACTION_20260926.md`.

Restating the objective's question: *what can the ~3093 agents express or execute that our ~1400-1600
`cha22` agents cannot?*

---

## Question A — TAPE. How is the leader's route/tape fundamentally different?

**Not in shape, not in rate, not in hour. In two things: which POOLS the route's marginal plot-days sit
in, and the ORDER in which an item's volume meets the market.**

| candidate difference | measured | verdict |
|---|---|---|
| release **rate** (peak units/item/day) | p19: **0/13** leaders at or below the town's 10-13/day, on 7/7 items, on two series differing by 30%; our peaks sit **inside** the leaders' range (MILK 19.5 vs 18.9-55.9, WOOL 22.3 vs 18.0-39.4, STRAW 29.7 vs 26.6-50.8) | **REFUTED** |
| sell **hour** / `step%24==23` preempt slot | p28, within one market: `hour` perm p=0.24, `mod23` p=0.07, `nsell` p=0.83 — **no separation** across 109 divergent pairs | **REFUTED as the mechanism** (and this contradicts our own `Top-10 DNA levers` note, which was measured across markets) |
| season **shape** (thirds) | p17: 5.2/36.3/58.4% vs 5.4/36.2/58.4%, mid-step@50% 522 vs 523 | **REFUTED** |
| **lead-time against the opponent** | p28: winner sells the same item **~3.06 days earlier** (win-share 6% ⇒ loser side 94%), where the pool is **~25.8 units less glutted** (win-share 1%), with a **~3-unit smaller** largest order (29%), perm p<0.0001 | **THE DIFFERENCE** |
| **which pool the volume goes into** | p27, contested regime: our px/base STRAW 0.75, MILK 0.50, WOOL 0.50 (cliffs 62/76/59) vs CARROT 1.58 (cliff 842), WHEAT 1.57 | **THE DIFFERENCE** |
| production at parity | E118: winners hold **1.47x money at production parity**; tomato tile-days 4.22x, fert 1.34x, **217 extra idle PASS** | consistent — the extra money is realised, not grown |

## Question B — LAND. What is the actual optimal land cadence?

**There is no land cadence that is a mechanism.** `150/220/254` is a *marker* copied from replays:
gating it returned **0W/10L/2T −1,356**, and the engine **refuses the buy** at the cadence we asked for
(`project-land-cadence-rejected`). Land unlock is downstream of cash, and cash is downstream of the
sell-timing pool problem. E104's route census (all 41 routes animal-maxed, 17 place / 9 COW XOR 14
SHEEP) says the plot geometry is already saturated. **Land is closed as a lever; the cost of treating
it as one is two full candidate cycles.**

## Question C — ECONOMY. How is money/resources accumulated and reinvested?

**The real bottleneck is one shared `shed + cash` constraint, not either one alone.** Measured on the
E220 ration arm: capping premium releases throttled **WHEAT by 153 units/seat** — an item the cap never
names — because `shedCapacity=100` end-of-day discard is the *only* storage and the spine's cash is
locked in the same queue. Consequences that are now laws: the shed **is not a bank** (deferral needs
~3.7x the entire shed); `$1` floor sells are **shed relief, not revenue** (engine: `:659-660`, a `$1`
sale is not added to the pool, so the glut self-limits); and turn-level cash neutrality holds (V12-V19
ledger). The leaders' `217 extra idle PASS` (E118) is them **waiting for a pool state, not for cash** —
they are liquid at the moment of sale, we are not.

## Question D — FERTILIZER. Why and when does the strongest strategy use it?

* **Supply side, not turn count.** V13 `fertmax` produced only +3 apps/game with 45 blocked at
  `carried==0` → the ceiling is fert *availability*, and `E123/E124` fert-CARRY was refuted.
* **It accrues on two engine paths** (winner-diff law), and the effective whitelist is the **crop list**
  at `cha22` `:2153` — strawberry tile-days buy +107 apps with **zero extra buys or hires** (V27-V29).
  So "more fert" is really "grow the crops that generate fert".
* **Price discipline:** top-10 DNA buys fert only at ≤25/turn and ≥$40. Champions run 135-249 fert vs our
  85-110, and the 2700-tier loss class is exactly the fert-starved spine.
* Fertilizer's own **pool is the widest cheap one** (cliff 493) and it is the one item the town **never
  removes** (`TOWN_REMOVAL FERTILIZER = 0`), so it behaves as a pure input, never a store of value.

## Question E — CROPS. What crop programs are being executed?

**11 of 13 top teams run tomato at 90-242 tile-days; we ship 0** (`behaviors_p6.csv`, p27). But the
prize is small and I over-claimed it once: `agents/friend_r78ub.py` actually runs tomato, and
**20 PLANT TOMATO → 79 committed units/seat ≈ 8 realised units per plot per season**, not the 56 my
`lane_valuation.py` assumed from a 0.35 yield guess. Re-based: **~+2.4k/seat (~+3%)**, and r78ub's
observed +2,399 over the champion on the same seed is the whole edge (r78ub is not tomato-only-different
— it is E94 with an EarlyCycle flip, [[project-e97-r78ub-tomato]]).
The *real* crop-program finding is **pool tolerance**: our marginal plot-days go into the 59-76-unit
cliffs (WOOL 59, MILK 76, STRAW 62) where a second seller destroys the price, while CARROT (842) and
TOMATO (529, and its scarcity side is `hinge below_target 0.40` so the town *lifts* it) are the pools
that survive contest. p27: carrot is the **only** contested item where our realised price **rises**
(42.0 → 55.2).

## Question F — HERD / PASTURE. What explains the larger herd strategy?

**E104: the top-10 gap IS herd scale.** V11 over-tends a 6/6/5 herd; every one of the 41 routes is
already animal-maxed and COW and SHEEP are **mutually exclusive within a route** (9 vs 14), so the
livestock decision is not a knob — it is baked into the route's plot geometry. The overlay that tried to
exploit it was **rejected at −65,875**. Only path: a **new co-designed livestock + wheat + hire block**,
i.e. route generation, not wrapping. Corollary from the shed math: 10-14 cows × `max_held` 6 = 60-84
milk, so **no team can bank milk** — which is why p19 shows everyone, leaders included, bursting.

## Question G — TIMING. What critical events happen at specific turns?

The market calendar is **common and shared**, which is the key structural fact:
`I0 − inventory` crosses zero on the **same day for essentially every team** — FERTILIZER d1, WOOL d9,
MILK d17 (11/15), STRAWBERRY d21 (13/15); TOMATO never (most scarce pool on the ladder). Town events:
`townCenterSellInterval=24`, shop draws from `random.Random((seed*1_000_003)^day)` **consumed once per
empty unlocked tile** (so a farming route and a noop route see *different* shop sequences — town removal
is not seed-invariant and cannot be added across regimes), `episodeSteps=720`, `maxMarketOrdersPerTurn=10`,
`shedCapacity=100` end-of-day discard. Loss concentration: **E145, 88.2% of live-loss dollars land in
days 15-24** — the window that contains the MILK (d17) and STRAWBERRY (d21) crossings. p28 says the
winning tape is ~3 days *ahead* of the loser in exactly that window.

## Question H — SEQUENCING. Which action sequences matter more than individual actions?

Three sequence laws, each bought with a failed candidate:
1. **Preempt without a debt ledger is a self-inflicted price crash** — the front-run attempts lost until
   volume was conserved by booking executed quantity into `state["debt"][item]` and repaying out of the
   step-24 order.
2. **HARVEST→SELL must be same-day.** The shed cannot hold a deferred premium unit (E220: 130.7 MILK /
   103.7 WOOL / 131.3 STRAW per seat annihilated; step-718 shed = 0 in *both* arms). So any lead-time
   policy has to move the **harvest** forward, not the sale backward.
3. **A round-trip neutralises itself** on WHEAT/FERTILIZER (preempts cancel to exact $0) and the
   `obs[t]`/action pairing is POST-action, so an off-by-one in the sequence reads as a working layer that
   never fired. And per E152, **a tape's crop is not separable from its slot geometry** — sequence is the
   unit that matters, which is precisely what a per-action wrapper cannot address.

## Question I — ADAPTATION. Fixed, conditional, or opponent-dependent?

**The required policy is conditional, and the information is available.** Our tape is fixed
(`tapes are the strategy`; only 20/41 routes are selectable and overlays are capped at ±0.35%). p28 shows
the edge is **relative to one specific opponent in one specific market** — lead-time — so it cannot be a
constant schedule. The observation surface is not the blocker: `observation.private.market` / `farm`
exposes live market inventory (E89 established the price oracle data is present; E89b's gate failed with
**0 flips**, i.e. the *hook* was inert, not the information), and rival flow is invertible to ~92% of
cells but **not persistent** (best-lag Jaccard 14%, E108), so adaptation must key on the *current pool
level*, not on a forecast of the rival. p25 closes the last escape hatch: **both seats read identical
prices at every step**, so a realisation gap is *necessarily* a timing gap of our own — and
吃白饭的大肥鱼's opponents sold **832** animal units vs our opponents' **585** and it still realised
**0.538 vs our 0.271**. Not opponent mix. Ours.

## Question J — REPRESENTATION. Can the current architecture express it? — **NO**

The strategy that the evidence names is: **for each item, own the day its volume meets the market, in a
pool whose cliff can absorb it.** Every clause of that is outside what `cha22` can express:

| required | where it lives | can the spine do it? |
|---|---|---|
| choose the item's pool by cliff width / contest tolerance | the route's crop mix | **NO** — crop-mix overlays are inert (V27-V29), production overlays CLOSED |
| move an item's harvest ~3 days earlier | the route's slot geometry | **NO** — harvest day is inside the generated tape; E152 proves the crop is inseparable from the slot |
| keep season volume conserved while re-timing | wrapper | yes, and it has been done (E210) — but it only moves the **sale**, and the shed forbids moving the sale away from the harvest |
| condition on live `market.inventory[item]` | wrapper | the input is exposed, but the only wrapper that reached it flipped 0 times (E89b) |

⇒ **Change the architecture.** The missing component is a **release/production calendar controller**:
one object that, per item, owns the *day* on which harvest and sell are emitted, as a function of
`market.inventory[item]` versus that item's crossing calendar, with `shedCapacity` as a hard constraint
and season volume conserved by construction. Today those decisions are distributed across a static route
table, a step-24 market wave, and a wrapper that can only delete or duplicate actions the route already
chose. That is why 8 candidate families (drain/sluice/preempt/ration/hold-release/fert-carry/feed-
discipline/land-cadence) all landed within ±0.35% or negative: they were all edits *inside* an
architecture that cannot express the target.

---

# §22 — TAPEFORGE RE-EVALUATION (all seven questions)

Prior verdict was NO-GO. **I do not accept it as stated, and I do not accept the romantic version
either.** The required object is smaller than "a tape generator", and whether it is constructible hinges
on exactly one measurement that does not exist yet.

1. **What exactly must it generate?** Not a full episode plan. A per-item **release/production calendar**:
   for MILK, WOOL, STRAWBERRY, MELON, the day (and within-day step) on which each cycle's harvest and its
   matching sell are emitted, subject to (a) `shedCapacity=100` same-day pass-through, (b) season volume
   conserved, (c) the item's cliff width as the budget for how much may land in one day. The route's plot
   geometry stays as-is; only the *timing* of the ops the route already produces becomes an output.
2. **Can existing public data supply it?** Partially, and the parts are identified. We hold 85 raw replays
   with declared actions and an exec model **proven exact on 1465/1465 cells**; p28/p29 give the winner's
   day / order-size / pool-level distributions; `p18` gives the closed-form inventory→price curves and the
   cliff widths (MILK 76, WOOL 59, STRAW 62, MELON 158, FERT 493, TOMATO 529, CARROT 842). **Missing: the
   harvest-side ground truth** — on-tile maturity per step, which *is* in the replays (`farm.tiles`) but
   has never been extracted. No new Kaggle data is required, so the 429 on `tools/fetch_episodes.py` is not
   a blocker.
3. **Simplified version within the deadline?** Yes as a **re-timing pass over the existing route**, ~2
   functions in the production/market layer, not a new lineage. No as a *generator* — route re-fit has
   already been tried and is capped at ±0.35% because only 20/41 routes are selectable.
4. **Minimum viable structural change:** the **lead-time scheduler** for the four narrow-cliff premium
   items, front-loading ~3 days relative to the opponent with same-day shed pass-through and conserved
   volume. This is the only mechanism that survived every falsifier this cycle.
5. **Highest-value portion only?** Yes: p28's mean $ gap at matched volume is **WHEAT 5,116,
   STRAWBERRY 4,039, MELON 3,573, FERTILIZER 2,429, MILK 2,594, WOOL 2,029**, and p17 independently puts
   the realisation deficit on MILK (`px/base` 0.375 vs 0.831) and STRAWBERRY (we hold the **scarcest pool
   of all 15 teams** and still convert 10th/14th of 15). Target **MILK + STRAWBERRY** first; that is where
   the same-item, same-market edge is largest and where our pool position is already right and only the
   conversion is wrong.
6. **Expected development time:** ~1 day for the scheduler plus liveness probes, ~1 day for symmetric
   arms on ≥4 seeds reporting H2H **and** absolute. The dominant risk is not time, it is that the shed cap
   re-applies: front-loading harvest may simply move the destruction earlier.
7. **Fast falsifier — and it is already running.** CQ-7/`p29` asks, for the 109 divergent pairs: **does
   the winner's HARVEST day lead the loser's, or only the SELL day?**
   * Harvest days differ ⇒ the edge is **production-start, route-resident** ⇒ TapeForge in any form that
     respects the existing route table is **NO-GO CONFIRMED**, the honest §22 answer is "not
     constructible in the remaining time", and the recommendation is to ship `cha22_e199_lo96q8` and stop
     the offensive.
   * Harvest days match and only the sale mass differs ⇒ **GO**, and it is expressible as the scheduler in
     (4) — a wrapper, buildable this week, with p28's numbers as the prize.

**One correction to the framing both IDEs carried:** the falsifier must *not* be "can we match the
leaders' price by copying their sell window" — p28 already killed the sell-window hypothesis (p=0.24).
It is specifically the harvest/lead-time split above.

---

## FILES / CONSTRAINTS

`research/coder/AJ_STRUCTURAL_ANSWERS_20260927.md` (this file). No agent modified, no gate run, **no
submission called, `submission.py` not touched** (§23/§24 hold; the two live baselines
`56578803 cha22_e210_straw_h13q6` and `56578809 sluice_topup7` remain immutable). Open CQ-7:
`tools/p29_leadtime_split.py` → `results/p29_leadtime_split/REPORT.md`.
Incident this cycle, disclosed separately:
`research/coder/incident/CONCURRENT_SUBMISSION_OVERWRITE_20260926.md` — a parallel session overwrote the
worktree `submission.py` (508,860 B, v9/3/V39 lineage) ~2 min before my commit; left unrestored, never
committed, `HEAD:submission.py` still 1,086,993 B.
