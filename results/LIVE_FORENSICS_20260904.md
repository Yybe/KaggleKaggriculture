# Live Forensics 2026-09-04 — why UVM-2 stalled at ~2100 / top 600

## Submission ladder (Kaggle live scores)

| submission | date | public score | live record | source |
|---|---|---|---|---|
| ShiV17 | 2026-08-10 (55408688) | 2994.8 | 99W/7L/0T (n=107 incl. draws) | replays pulled 2026-09-04 |
| V18 APEXX | 2026-08-11 (55413866) | 2781.7 | ~79W/27L/1T | likewise |
| lynnsakurai v4 | 2026-09-03 (55979431) | 1638.3 | 70W/? |  |
| UVM-2 | 2026-09-03 (55993544) | **2100.9** | **62W / 54L / 3T (n=119)** | `results/live_uvm2_episodes/` |

(UVM-2's rate 52.1% W is the entire explanation of the rank plateau. The scoring
period around 2026-09-04 pairs you against the live meta — a pool increasingly
dominated by the same v29/boatlee-lineage clones we studied, plus a minority of
structurally different agents (animal-heavy, crop-diverse, etc.). Losing to that
minority at −20 k…−69 k while winning vs clones by +13…+859 creates the ceiling.)

## Replay forensics (n=119, 100% of UVM-2's public episodes, 3.5 GB)

### The stall is NOT: mirror noise, UVM-2 side-effects, or crashes.
- No season-long stalls: max consecutive PASS-only steps is 2–3 for both sides
  in every game (the 3-PASS streaks include legitimate crop waiting time).
- No solver/gym timeouts: every episode is 720 steps, statuses DONE/DONE.
- Tape is intact: all games reach quadrant 3, 11 hands, 0–6 crops.

### The stall IS: a production-capacity gap against the live animal-heavy meta

The deepest 20 losses share three signatures, measured the same way in wins
so it is not cherry-picked:

1. **PLACED-animal gap** — The 20 worst losses final farm:
   `own COW 6–7 / SHEEP 3–4` (mean 6.5/3.4) vs `opp COW 9 / SHEEP 5–8` (mean
   9.0/6.8). The 62 wins average own 9/5 vs opp 8–10/4–5 — the wins are the
   games where the opponent's final herd matches (or undercuts) ours. The
   tape itself is identical for both sides (byte-identical `_ACTIONS`), so
   the gap is not BUY volume — it is BUILD→PLACE fidelity.

2. **Identical BUYs, different BUILD→PLACE fidelity.**
   The v29 tape buys 14 animals (`COW 9 / SHEEP 5`, steps 1/66/88/150/169/176/195/313)
   and issues 20 BUILDs + 14 PLACEs. In the worst losses the live opponent's
   *replay* actions show identical BUY counts but 18–20 BUILDs and 14 effective
   PLACEs, while our side logs the same PLACEs as no-ops because at that wall-clock
   step there is no hired hand to receive the PLACE (tape steps 95/156/200/…)
   and/or no empty PASTURE at the tile (weed-cleared tile fell back to PLANT,
   or hands were reassigned by weed-repair). Net: `final shed COW 2 SHEEP 1
   WHEAT 3…64` on our side, `0/0/0` on theirs. The 2–3 stranded COWs cost
   ~20 k late-production each (MILK every 2 days @ px 40–100).

3. **Revenue follows capacity, not price-play.**
   Endgame money curves diverge steadily from ~step 260 onward (opponent
   +1.0–1.5 k/day), not as a single sell spike the UVM-2 layer could have
   salvaged. The UVM-2's price-state-aware defer/re-inject is irrelevant here:
   both players transact similar total WHEAT/MILK/WOOL, the opponent just has
   more yield_units/day. Wins vs WHEAT/MELON agents (+25–80 k) are the
   complement: they keep animals alive (escapes after day 8 if WHEAT unfed)
   and their farm collapses when the tape's FEED/CARE rhythm falls out.

### Why the local fleet didn't catch this

The local `agents/_top_pub/` and `WybeV2/kernels_pull/_new_top/` fleets are
all dominated by the same lineage (boatlee v21/v29, lynnsakurai v4,
salemali7 2900/3094, tetsutani, pilkwang). In those mirrors the same tape
induces the same stranded-animal pattern on both sides, so the mirror-gated
UVM-2 saw 0W/2L/34T vs v4 at ±84 coin — not because the tape is optimal, but
because the comparison is symmetric noise. Against the live diversity pool
(~108 distinct opponents in 119 games), the asymmetry is exposed. Promotion
gate `UVM2_PROMOTION.md:16-31` measured "≥ champion" vs its own fleet, which
is exactly the contaminated measurement rulebook §2.1 warns against as a
*mirror-like* floor: "A candidate promoted on mirrors is a mistake by
definition."

Rulebook §§0.2/2.1/3.4/5.G1 — gate must be H2H on the incumbent using the
official engine, and A/B on a *fresh* opponent set. `228-0` vs a 1-family
mirror fleet could never justify ±84 mirror neutrality as "H2H on the
incumbent with a diverse fleet." The live ladder is itself the fresh fleet,
and there UVM-2 regressed vs ship's best prior (ShiV17 at 92% WR, V18 at
73% WR).

### Top-player mechanics — what was reverse-engineered correctly and must be kept

From the lynnsakurai v4 diff and the 119 replays, these are file-verified
insights that the fix must preserve (read from `WybeV2/kernels_pull/_new_top/*`):

- The v29-lineage tape (sha `5f0ac2abd6bc5fe1`, 720 steps) is still the correct
  **foundation**: 20 PASTURE/COOP builds, 14 planned PLACEs, 3-quadrant
  expansion (29 boom — 14 PLACEs buys consistency at +0.6 coin of draw variance),
  and the adaptive-market sell ranking (`_adaptive_market` with
  price_gate 0.66, pressure trigger, shop-aware reserve, tranche=4, overflow
  guards). In the replay forensics, every team name that lost to us had strictly
  *fewer* hands or *later* pasture builds; the teams that beat us had the same
  tape's builds but executed PLACE reliably.
- The **WEED repair** is essential and already present: `_WEED_REPLAY_STEPS=8`,
  DIG + `_trace_actor_action(step-1)` + `_intended` on step+1 correctly covers
  the inner shed quadrants where our BUILDs land. Disabling it would lose the
  2–3 coin of draw variance we have. The failure is not the WEED handler but
  the next item.
- The **SHEEP gap** is the observable: 5 planned SHEEP on tape vs 5–8 realized
  by opponents. Live opponents that beat us most consistently bought the third
  SHEEP before step 150 (our tape's third SHEEP arrives step 195) and
  placed it before the CARES/ feeds stabilize — i.e., they front-loaded the
  cheap WOOL pipeline (cost 500, product 3-day, marginal px > 60 by day 19
  in rebalance). WOOL is the only item whose px stays > 100 when MELON
  gluts repeatedly crash to $1 (town demand Melon 88% down in 1.32.6 per
  README §V18). Beating the floor therefore means beating the SHEEP count
  on placement, not on price.

### What the ONE-lever fix must do (canvas §1 template)

- **Observation** — `results/live_uvm2_analysis.json`: deepest losses final
  `own 6/3 vs opp 9/8`, same BUY 14, stranded shed 2/1 (F); `bench_top_vs_v18`
  36W/0L mirrors hide the gap (G); ShiV17 99W/7L proves a non-animal-fix
  path once existed (R → needs local re-verify before trusting).
- **Hypothesis** — The tape's blind BUILD→PLACE binding is not WEED-robust:
  on pastures cleared from WEED at steps 27–28/155–161/254, the FEED/CARE
  rhythm and the 1-day hand cooldown leave the PLACE's target hand on a
  different tile, so PLACE hits the wrong tile and the animal stays in the
  shed until terminal. Opponents' tapes encode a PASTURE-aware PLACE (the
  same 20 builds, but hand routed to the empty PASTURE nearest the shed
  before PICKUP→PLACE).
- **Intervention** — Fix exactly **one** mechanism (rulebook §1): **PASTURE-
  aware PLACE repair**. Before executing a tape PLACE (COW/SHEEP), if the
  tape's target tile is not an empty PASTURE, **retarget the PLACE to the
  hand currently on (or nearest to) an empty PASTURE, and precede PICKUP of
  the same animal from the shed when within shed-adjacency**. Everything else
  frozen — including the UVM-2 market pacing and the WEED repair.
- **Measurement** — H2H vs the *live-derived* opponent tapes (extracted from
  the 119 replays; 108 distinct opponents), plus the `diag_head_vs_all*` fleet
  (mirror fleet), official engine 1.32.6 interval=24, on the 8-seed family
  `1M 9M 3.33M 7.77M 5M 6M 8M 2M` (rulebook §3.3), extended to 100 seeds if
  borderline. Track: final animals/shed/WHEAT, MILK/WOOL cumulative volume,
  and the 54-loss set's mean Δ. Rulebook §2.2 — instrument with per-step
  SELL dumps + shed dumps every 60 steps.
- **Gate** — Pre-registered (rulebook §3.3): ≥ 6/8 seeds with positive mean
  Δ vs the incumbent (UVM-2) on the live-derived opponent set; mirror pair
  vs lynnsakurai v4 / boatlee v29 must stay ≥ −100 (neutrality). Persist
  outputs per §2.3.
- **Conclusion** — Accept iff the worst-20 mean Δ moves positive (or the
  stranded-shed count hits 0 at end-of-season); Reject otherwise — do not
  chase with one more seed (§5.G9).

Ledger rows E8 (cap experiment) + E9 (regime check) remain open and must be
carried into the V27+ checklist (§7), now with a new E10 (pasture-aware PLACE).
