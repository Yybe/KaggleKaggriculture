# Roadmap

Ordered roughly by expected impact per unit of effort, based on what
testing actually surfaced rather than a generic wishlist.

## Near-term (clear, well-understood next steps)

### Status (2026-08-07): all near-term items resolved via A/B gating

Each change was gated with `tools/tournament.py` / `tools/tournament_fast.py`
(20 seeded games per matchup, alternating seats, mean_margin + min_margin
guardrails) before promotion; the current `main.py` ships only the promoted
ones. Latest promotion: **candidate9b (day-0 hand army + opening herd +
marginal-priced animals + capacity-gated SE land) — SHIPPED**, see item #9
below.

9. **Top-meta capacity ladder (day-0 hires + herd, marginal animal
   pricing, capacity-gated SE land).** ✅ SHIPPED (candidate9b.py).
   Replay mining (`tools/mine_matches.py`, `tools/_top_opening.py`, 9
   leaderboard replays in "kaggriculture top replays/") showed the winning
   opening is HIRE x5-7 + 2 COW + 2 SHEEP on day 0, q4 by day 9-13,
   peaking at 60-64 crops + 14-23 animals ($79-148k finals) — a *capacity*
   game, not a crop-choice game (see FINDINGS section 9). Changes shipped:
   (a) `plan_hiring` day-0/1 opening override (5 hands, fib cost ~12
   coins) + `MAX_HIRES_PER_DAY` 6->8; (b) `plan_expansion` drops the
   tile-pressure gate for NE/SW (cash-only, 1.05x/1.5x buffers) but gates
   the expensive SE ($4,000) on capacity demand (<=8 empty tiles) so it
   can't strand capital (that was candidate9's regression); (c)
   `plan_animal_investment` prices the daily FEED action at the MARGINAL
   crop's per-action (WHEAT-anchored, candidate7's pricing — now legit
   once surplus hand capacity exists) + `MAX_PER_ANIMAL_TYPE` 4->8; (d)
   `strategy._build_market_orders` buys animals BEFORE seeds and
   day<=1 top-ups the herd toward 2 COW + 2 SHEEP with a relaxed
   in-flight cap (2/type instead of 1). A/B journey: candidate9 (ladder
   without the budget reorder) FAILED h2h 2-18-0 mean -7,496 (q4 land
   stranded + herd starved); candidate9b (with animal-first budget +
   herd bundle + SE gate) PASSED: vs starter +56,698 vs +56,348, vs
   random +61,711 vs +61,397, vs pass +57,476 vs +55,987 (all 20-0-0),
   h2h 8-12-0 mean +114 min -24,923 vs baseline mirror 7-11-2 mean
   -3,354 min -58,073 — mean and floor both clear the mirror noise, and
   normalized W/L (8 vs 7) favors candidate9b. Promoted: fresh build ==
   baseline.py == main.py (MD5 CBB06E46FE35772FD18D38529C1A0330, 1691
   lines / 78,791 B), 720-step smoke P0=63,894 DONE. Footprint now q=2
   day 1 / q=4 day 12 (SE only when tiles fill), day-0 herd (2 COW + 2
   SHEEP), 4-6 animals by endgame, ~$60-65k vs openers. NOTE: the herd
   still caps at ~4-6 vs the top's 14-23 — the remaining gap is likely
   scheduling/feeding throughput on the grown herd, not pricing. See
   FINDINGS section 10.
   **Harness (shipped alongside):** `tools/tournament_fast.py` runs games
   in parallel across cores (agents loaded once per worker, timing
   benchmarks, `--check` determinism guard). Measured: 160 games in 151s
   wall vs ~1,136s estimated serial = **7.5x speedup** on 16 cores;
   same-seed games bit-identical across process counts.

8. **Early land purchase (quadrant racing).** ✅ SHIPPED
   (candidate8_early_land.py). Replay mining (`tools/mine_expansion.py`)
   confirmed the user's report: opponents buy NE day 1-10 / SW day 12
   while our shipped agent stayed one-quadrant until the day-12 harvest —
   the uniform `money >= cost * 1.5` buffer in `plan_expansion` blocked
   the $1,000 NE purchase while the bank sat at $300-1,100. Fix: relax
   the buffer to `1.05x` for the first (cheap) land only; keep 1.5x for
   SW/SE. Gate on 20 fresh seeds: vs starter +57,006 vs +48,338,
   vs random +53,835 vs +51,343, vs pass +56,567 vs +49,375, h2h
   12-8-0 mean +1,055 vs self-mirror +129 — beats baseline on every
   external matchup and wins the mirror; single-seat h2h min -3,132
   (seed 3001 seat 0) is noise, not a systematic regression. Promoted:
   fresh build == baseline.py == main.py (MD5 879DBE86..., 1660 lines /
   77,395 B), 720-step smoke P0=65,357 DONE. Footprint now q=2 day 1 /
   q=3 day 14, but animals remain 0 (section 7 verdict unchanged; land is
   a separate lever from animal *pricing*). Next: confirm the +2.5-8.7k
   edge on a larger corpus vs real leaderboard opponents; consider
   smoothing the tight days 1-11 cash window (staggered land, or crop
   mix during the NE buildout).

1. **Price animal FEED/CARE action-cost properly.** ✅ TESTED, GATED OUT.
   `evaluate_animal` now explicitly prices the daily FEED action at
   `best_crop_per_action`. Adding the CARE turn (2.0x, then 1.5x the best
   crop $/action) was tried and A/B-regressed head-to-head vs the baseline
   (pooled 12-seed mirror margin -577.. -722 with -3.3k tails) while only
   matching random-opponent gains, so FEED-only 1.0x was kept. Keep the
   code comment + docs note; re-verify with a fresh ablation if the live
   market stays quiet.
   **2026-08-07 follow-up (candidate7_animal_marginal.py, REJECTED):** an
   alternative "fix" priced the daily FEED turn at the *marginal* crop's
   $/action (~$10, TOMATO) instead of the best crop's ($94.7, MELON),
   which made animals look profitable on paper (COW +425, SHEEP +215
   whole-season total at day 1; GOOSE stays -31 -- cheap eggs correctly
   out). Gate on 20 fresh seeds: h2h **5-15-0, mean -1,966, min -5,963**
   vs baseline mirror +129 / -1,371 -- blows the min-margin guardrail;
   vs random and vs pass also slightly negative; only vs starter
   +1,482 (noise). A cow's whole-season profit (~+425) is *less than one
   MELON tile* (~+1,420) on the same tile/actions/capital, so in fair
   h2h the animal spend loses to the compounding crop engine (diagnostic
   seed 1117: candidate built 1 COW, ended $29,802 vs baseline $30,863).
   **Conclusion: 0-animal live play is the correct local optimum; the
   replay opponents' animal wins come from their superior route corpus,
   not from animals beating crops in a fair matchup.** Reverted; see
   docs/FINDINGS_2026-08-07.md section 7.
2. **Batch-aware animal market pricing.** — **SHIPPED.** `evaluate_animal`
   now takes `n_existing` and prices the marginal animal against the
   whole type's committed output ((n+1) x per-animal output), mirroring
   `plan_tiles` for crops; `rank_animals` threads `n_existing_by_animal`
   from `plan_animal_investment`. Flat `MAX_PER_ANIMAL_TYPE=4` remains as
   a cheap backstop. A/B: head-to-head +457 vs baseline mirror +198 over
   6 seeds — promoted.
3. **Config-driven `MARKET_PARAMS`.** — **SHIPPED.** `GameState.market_params`
   reads `obs.market.params` (the engine only exposes it when non-default
   `marketParams` are configured), threaded into every price/ROI call via
   `decide_actions(gs, gs.market_params)`; `opponent_model` no longer
   hard-codes `rules.MARKET_PARAMS` for T. Verified end-to-end with
   `marketParams={'WHEAT':{'base':50},'STRAWBERRY':{'I0':500}}` (obs shows
   the override; agent plays clean). Default-config games are byte-identical
   to the pre-change build (obs lacks `params` -> None -> fallbacks).
4. **Town-demand-directed crop selection.** — **TESTED, GATED OUT.**
   Subtracting raw town absorption from the plan_tiles batch size
   over-weighted the most-recently-unlocked shop's crops for BOTH players,
   herding them onto the same crowded queue; pooled 12-seed head-to-head
   regressed (2 seeds with -4,665/-5,711 tails, mean -461 vs baseline's
   own ~+198/-267). Reverted; town demand still reaches the planner
   indirectly via live market prices.

## Medium-term (would need real design work + testing budget)

### Status (2026-08-07): item #5 (cross-call opponent state) SHIPPED

5. **Deeper opponent modeling.** ✅ SHIPPED (first layer). `opponent_model`
   is no longer stateless: `observe(gs)` runs once per turn and records the
   opponent's public money/quadrants/hires per day into module state keyed
   by the OBSERVING player and cleared on step 0 (safe under runpy's
   one-namespace-per-process + self-mirror reuse). `sell_urgency_multiplier`
   now compounds the visible-incoming-supply boost (1.15) to 1.20 when the
   opponent's bank is falling (spending into production => they dump soon).
   A/B gate (10 seeds, alternating seats): vs starter byte-identical
   (+48,163), vs random +51,396 vs +51,044 (better, within noise), h2h
   exactly equal to baseline mirror (+96) -> promoted, no regression. The
   money-trajectory/expansion-race layer above this (quadrant racing) is
   the natural next increment and will need the live-replay corpus to
   validate against real opponents, per item #7.
6. **Larger, more statistically confident test matrix.** ✅ STATUS. First
   expanded pass done (2026-08-07): 20 fresh seeds (1117..3111, never used
   in any gate) for the current baseline. Results: vs starter 20-0-0
   (mean +49,387, min +44,629); vs random 20-0-0 (mean +52,233..+52,418,
   min +46,578..+49,580); self-mirror 7-12-1 (mean -148, min -2,798) --
   the tightened noise floor. Methodology note: two *separate* env.run
   invocations with the same seed are NOT guaranteed bit-identical (dict/
   set iteration order leaks), so single-game deltas are meaningless;
   means over 10-20 seeds are the stable metric (this is why the gate
   always uses mean_margin + min_margin guardrails). Same-file mirrors
   reproduce exactly within one tournament run, confirming determinism
   WITHIN a process. To go beyond 20 seeds per matchup the harness needs
   parallelism (item #7's corpus can reuse the replay machinery).
7. **Replay mining.** `tools/ablation.py` and `tools/run_match.py`
   report aggregate stats, not the turn-by-turn behavioral traces the
   brief's Phase 14 describes (opening sequences, idle-time percentage,
   travel efficiency, etc. mined automatically from many games). Worth
   building once there's a large enough replay corpus (real opponents'
   replays, once available from the live leaderboard, would be far more
   informative than more self-play against the three built-ins).

## Explicitly out of scope for now, with reasoning

- **Tree search / MCTS over raw actions.** Reasoned through in
  `docs/ARCHITECTURE.md`, "Why greedy assignment, not search" -- the
  game's reward structure is smooth and mostly closed-form, so search
  depth buys little, and the compute would be better spent (as it
  currently is) on more accurate economics.
- **A from-scratch parallel simulator.** Deliberately not built; the real
  environment is used directly for all testing (`RESEARCH_SUMMARY.md`).
  Building one would only be worth it if per-turn *lookahead simulation*
  during play (not just offline testing) turned out to be valuable --
  which the architecture argument above suggests it mostly wouldn't be,
  given how directly computable the reward structure already is.

## candidate9e (2026-08-07) -- the herd-stall root-caused and its #1 lever

CLOSED the section-9/10 "herd caps at 2-4" investigation. The stall was
NOT feed-cost on a grown herd; a live trace (tools/trace_animal_planner.py,
seed 202) proved the herd never grows past 2 regardless of how positive the
economics look: `plan_animal_investment` proposed COW@empty-pasture every
single day, yet `carried` stayed zero and the day-12 task dump had ZERO
PLACE tasks -- 2 COW + 2 SHEEP dead in the shed all 720 steps.

Two tasks.py bugs fixed (item #9's plausible cause):
  (1) PICKUP/PLACE valued at 20/25 on tier-3 lost the greedy scheduler to
      nearby PLANT*s (6-3*dist) because the 3/tile distance penalty made a
      8-13 tile shed round trip score negative. Now valued at the animal
      cost (400/500) so a shed->pasture trip outranks routine planting.
  (2) _structure_wants_animal returned dict-first -> PASTURE always "COW",
      so SHEEP was structurally un-placeable. Now prefers an animal of a
      compatible kind we actually own.

Effect (seed 202): placed COW 2 -> 7; final vs starter 57,323 -> 68,161.
Gate (20 seeds, parallel harness): candidate9e h2h vs baseline 18-2-0 mean
+9,318 min -9,242 (self-mirror noise floor mean +247, min +/-17,500);
all openers 20-0-0 with mean_cand up to +$69k. PROMOTED to main.py (MD5
7E3B867A02C2101E010C31B8A531A82DE, 1705 lines / 79,682 B). Prior build
archived as candidate9b.py/baseline.py (unchanged). See FINDINGS section 12.

NEXT LEVER: the planner's pricing gate still turns COW/SHEEP total_profit
NEGATIVE ~day 10-14 (market gluts / WHEAT feed anchor), capping endgame
at ~7-8 animals vs the top's 14-23. candidate9e un-frozen placement, so
the remaining gap is timing (accept a modest negative marginal late-season)
and structure-vs-herd release cadence -- a candidate planner-timing pass.
