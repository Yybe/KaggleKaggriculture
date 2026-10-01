# E89 — Market-price oracle brief (post-mission audit)

Date: 2026-09-21. Status: RESEARCH, no agent edits.

## Audit result: the 31-section reverse-engineering mission is ~90% already executed in this repo

Mission section -> state here:
- §1 map repo, §2 best base, §3 mechanics: done. Base = r78u (commit e9b3b4d), engine_assert PASS 1.32.7, full engine source readable locally at `WybeV2/rank_env/.../kaggriculture.py`.
- §4 cluster == equilibrium: done and CONFIRMED. Ties are byte-identical mirror games (E71 determinism; live exact ties logged in ledger ~line 370). Loss class = near-ties: E63, 13/24 losses <=518 pts.
- §5 CLI data-mining, §6-§7 top-agent forensics: done. leoprovorov god-mode kernel fully decoded; tetsutani .so and avioon C++ verified; E61: r78u >= +17k vs all 9 gatable public champions -> public-code gates no longer discriminate.
- §8 God's Eye, §9 causal divergence, §11 loss taxonomy: done (E55, E57c, E66 laws; fire census).
- §12 draw->win mining: CLOSED (ledger line 367; v30 last-mover spread already tried and retired).
- §13 non-local effects: partially done — own price impact measured (E57c) as a COST only.
- RNG/shop-prediction overlay (mission's implicit "planning" hope): CLOSED twice. E62: live obs has no seed; 31-bit uncrackable. God-mode memory: their own particle filter fails closed (10-18% coverage). Do not re-open.
- Production overlay / mix / sell-timing classes: CLOSED (E74 both directions, E57c, sell-timing refuted).

## What nobody has looked at yet (found this session, CONFIRMED from engine source)

1. **The entire price model is a public, deterministic oracle in the engine source.**
   `price(inv) = base ± amp*f(|inv-10000|)`; TOMATO base=60, T=200, below-hinge (target .40, HINGE_GAIN 8), above-sqrt (target .60). No decay: market inventory changes ONLY via commits (sell +1, buy -1, shop buy -mult).
2. **Prices are exposed in obs; the function is strictly monotone => invertible.** From quoted prices alone, an agent can compute exact market inventory of every product, hence the opponent's cumulative net-flow (telemetry with ~1-step lag). No seed required — this is NOT the closed RNG overlay.
3. **Shop-day schedule is seed-free predictable:** spawns iff `(day+1)%3==0` (choice among shops needs the seed; the DAY does not). Expected inventory drain per shop-day is computable from the 8-shop menus. Scarcity spikes are therefore foreseeable in kind, not in item.
4. **Gate margins are razor-thin.** Fire census: cluster ADDON gates buy at price 79 and 82 vs threshold 78. Exact probe (engine `market_price`, this session): breaking the 78 gate needs +17u tomato inventory from a 79-world, +42u from an 82-world.

## Hypotheses ranked

- **H1 (defense, cheapest): invert-then-gate.** Replace r78u's raw `price>=78/70` gate checks with inventory-aware decisions: read tape -> compute inv -> predict own-impact-adjusted price at commit -> buy/sell on true scarcity EV. Attacks the E63 near-tie loss class (13/24 losses <=518) without new info. Zero new dependency, ~30 lines. Gate8 + fleet + panel16.
- **H2 (offense): gate denial (price war).** Dump tomato to push price under the cluster's 78 gate at their commit step. Refuted-default: market has NO decay and denial means they never absorb the dump — the dump permanently poisons our own remaining tomato pipeline (E57c's own-impact law, amplified). Only sane case: final-sale-then-dump in 79-worlds (17u). Low volume, thin EV; compute offline on tagged replay worlds before writing any code.
- **H3 (forensics): inventory-tape forensics (E89a).** One replay run per fire world dumping per-step market inv + prices (bench has God's-eye access). Measure what actually drains inventory (shop buys vs opp sells), build the empirical price-trajectory model H1 predicts with. Prerequisite for H1/H2, pure read-only.

## Experiment order (protect the 5/day submissions)

1. E89a read-only tape forensics, no agent change.
2. E89b invert+gate overlay on r78u: gate8 vs pub_metav4 clone (same gates = measurable), fleet, panel16. Submit only if fleet 16W/0L preserved AND near-tie band flips.
3. E89c denial EV study offline only unless E89a says inventory recovers in-game.

## E89a RESULT (2026-09-21, tools/e89a_tape.py, results/e89a_tape_{3330000,1000000}.csv)

**PREMISE UPGRADED — no inversion needed: `market["inventory"]` is inside agent obs, LOCALLY AND LIVE.** Verified in real Kaggle replay `replays_new/healthstone/episode-90941017-replay.json` (obs.market = {inventory, prices}; TOMATO inv=9983 at step 400). The full market ledger is public to every agent; the whole 2700 cluster reads only `prices` (V219 gate family). The forensics:

- TOMATO inventory ratchets DOWN all game (starts 10000; end 9708/9744 in fire worlds): shop-day drains dominate player sells. Price = monotone rising scarcity curve: 60 -> 79/82 at commit (t=433) -> 106/136 at season end. Crossing the hinge knee (inv < 9800) is visible in obs as the late-game price run.
- Gate margin at commit: worlds sit at inv 9820-9838; 78-gate breaks at inv>=9855 — i.e. **17-42 units of tomato supply from flipping the cluster's buy decision**, live-measurable, not extrapolated.
- r78u commit fires t=433 (dInv -3), the census "432" is the obs-step lag. Both seats swap-invariant.
- End-of-game inv 9687-9744 means late hinge prices (136+) are NORMAL — agents selling before the run leave money on the table; agents buying after it overpay. Current gates read one price number where the obs hands the whole state vector.

**Consequence for H1:** the overlay does not need price inversion — read `obs["market"]["inventory"]` directly, mirror the engine's `market_price()` to compute commit-time price, and gate on predicted scarcity trajectory instead of the instantaneous quote. Defense and denial both recompute EV against real numbers; denial still poisoned-default (no decay), but the drain curve says the dump is re-absorbed by shop days — re-check absorber math before final kill.

## Standing constraints

- Local clones are non-adaptive but share V219-line gates — denial/gate effects ARE measurable locally (unlike adaptive-class behavior, which only shows live).
- Live 2700 population = adaptive spine-clones (E55/E61); no local gate can certify a 3000+ claim. Treat H1 as a near-tie conversion mechanism, not a new spine.
- Do not re-open: runtime RNG overlay, naive block doubling, mix/schedule/timing heuristics, tie->win last-mover spread.
- Finals re-select (user, by 2026-09-23): only refs 56405541/56412435 are real; h20 ref 56402663 does not exist on Kaggle.

## E89b RESULT (2026-09-21): inventory-aware gate is provably INERT — verdict: do NOT submit

Build: `agents/e89b_invgate.py` = r78u (md5-anchored 319aad8c…) + exactly 3 patches — (1) helper block:
exact price-model mirror `_e89b_price(inv)` (0 mismatches vs engine `market_price` over inv 9000–11000),
6-step drain sensor `_e89b_delta` (ring of 7 observed TOMATO inventories per player, <7 samples → delta 0),
gate price `_e89b_gate_price = price(inv + delta)` with quote-fallback; (2) gate line in
`_v219_qualifies` uses `_gatepx` instead of the quoted price, and logs every call to `$E89B_TAPE`;
(3) behaviorally-inventory sensor in the wrapper (records inv each call). No trajectory (variant C not
built), no denial, no other changes.

Bench evidence (all interval=24, fresh-module loader):
- Fire worlds (3330000, 1000000) e89b vs r78u: 4 games, all exact ties (79090/83980). Tape: 4 gate
  calls, 0 flips; deltas −2, gate_px 79→80 / 82→82; both paths buy (thr 78).
- Fleet 8 seeds vs pub_metav4: 16W/0L/0T, mean +621, min +50 (gate condition 1 met).
- Mirror fleet e89b vs r78u: 16/16 exact ties, swap-consistent score pairs (condition 2 met).
- E63 near-tie live-loss worlds (16 seeds / 21 eps, margin ≤518): 32 games, 5W/5L/22T with
  swap-ANTI-symmetric deltas (±76…±990) → pure seat asymmetry, zero overlay effect. Tape: 30 gate
  calls, 0 flips. Only 2 calls were control-BUYs and both had margin 25 (inv 9766, px 94/95 vs thr 70);
  the other 28 were rejects, closest margin 3 (px 75 vs thr 78).

Why it cannot flip: observed 6-step market drift at commit time is 1–3 inv units → ≤1 price point
(integer-rounded model), while every near-threshold decision sits ≥3 points (≈17–40 inventory units)
from the boundary, and the commit-firing worlds clear the threshold by 25. The gate margin is not the
binding decision in these worlds — the loss class is not convertible via commit-time price gating.

Submit-gate verdict: 1 PASS, 2 PASS, 3 FAIL (zero flips in ≤518-band worlds), 4/5 vacuous.
→ E89b is NOT submittable; do not build variant C (precondition "B works" failed). H1 surface CLOSED
as a tie→win lever. Offline value remains: exact price mirror + inventory exposure facts.
