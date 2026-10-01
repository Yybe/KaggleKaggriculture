# Kernel Sweep — 2026-09-19 (competition: kaggriculture)

Sorted by voteCount / dateRun / hotness / dateCreated / commentCount (`--page-size 200`);
224 unique kernels. 114 have `lastRunTime >= 2026-09-12`. Note: this CLI (kaggle 2.2.4) exposes
`lastRunTime`, not `lastUpdatedDate` — used as the recency proxy. Raw JSON + pulled `.ipynb` +
extracted `.py`/`.md` live in `WybeV2/kernels_pull/_sweep_0919/{raw,src}`.

## Biggest finding: the top ladder is ONE shared lineage, not independent bots

Every high-vote recent agent (thomastschinkel 2945-farm, ahmedberatozer V25–V50 + more-yield-smarter-labor,
guruprasaathas111 master-engine-v3, aurax7 shop-router-reactive v4/v5, prvsiyan frontier series) embeds the
**same `E182 / Shop0909 last-seven-turn physical closure planner`** and the same `LAND_PRICES=(1000,2000,4000)`
tape-budget block. Attribution chain (from the code headers, verbatim intent):
- **yhay81 Shop Router 0908→0909→0911→0913** = 13 action tapes + shop-pair route map ("choose a plan after two shops")
- **aurax7 Reactive Router** = sale timing + shed projection (already forked into our base family)
- **dmitriigluzdov E180/E182** = terminal "physical closure planner" at steps **712–718** (64 deterministic sims, strict positive physical delivery, cargo-recovery on obs divergence)
- **prvsiyan V221B/V224C** = production/timing layer, lossless single-file packaging
- **ahmedberatozer / thomastschinkel** = EXP overlays on top of the above.

So "finding a new bot" is the wrong frame — the meta is a fast-moving **fork-and-layer race on the yhay81/aurax7/E182 spine**. Our 7-turn-rescue shop-router is on the SAME spine but several overlay generations behind.

## New kernels pulled (ref | votes | lastRun | type)

| Ref | Votes | Run | Type | Base strategy | Claimed score |
|---|---|---|---|---|---|
| thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots | 122 | 09-19 | agent+arena | Shop0909 tape + E182 planner + EXP overlays | **live 2944.7** (sub 56269928, 09-16); 96.1% (519-21/270 seeds) vs top-10 public; warns identical code scored 2579–2956 |
| raykkretzschmar/kaggriculture-rank-your-agent | 137 | 09-13 | arena/analysis | Elo/arena harness over episodes | tool, no agent |
| georgymamarin/kaggriculture-what-2600-farms-do-differently | 45 | 09-19 | analysis | measures `first_land_day`, `peak_crew`, crops by score band; lead often "never buys land early" | tool, no agent |
| ahmedberatozer/more-yield-smarter-labor | 107 | 09-12 | agent | Shop0909 tape + planner + v219/v233 land overlays | recorded-replay 3093 / 3826 / 3882 (vs replayed public histories, NOT live) |
| guruprasaathas111/kaggriculture-master-engine-v3 | 83 | 09-19 | agent | router + **EXP241 two-policy selector** + v219/v233 + clamp_sells/sell_lead | n/a |
| aurax7/kaggriculture-shop-router-reactive-v5 | 93 | 09-14 | agent | Shop0909 + reactive sell timing + **EXP257 funded atomic opening** | n/a |
| prvsiyan/kaggriculture-frontier-the-soil-remembers-rain | 103 | 09-14 | agent (repack) | yhay81 13 tapes + aurax7 timing; "PPO" only in prose, agent is rule/tape | n/a |
| tetsutani/demand-preserving-turn-sale-timing | 36 | 09-19 | agent | deterministic production controller + **bounded 3-turn sale advance** + **22-unit opening WHEAT attack** | the "highest public" that 2945-farm beats |

(Also new-but-not-pulled: reyhanksatria/dynamic-route-agent v85, flexonafft/multi-route v93, jaxa623 [2802]/[2780] v70/v40, degnonguidi/cloning-agent v59, alperen5252525 series, nathanjacob pipe-7 v62 — all on the same spine or clones thereof.)

## The 4-quadrant / BUY_LAND truth (directly answers the ask)

Confirmed in source. Top agents run the base tape on **{NW,NE,SW}** and buy the **4th quadrant (SE, $4000)**
as a *conditional, self-funding expansion* — never early/unconditional. Two named overlays:
- **v233 SHEEP/WOOL land grab** fires on **day 12** iff `unlocked_quadrants=={NW,NE,SW}` and `YARN_STORE>=2` and `WOOL price>=220` and `WHEAT<=45`; issues atomic `[['BUY_LAND'],['BUY_ANIMAL','SHEEP',6]] + [['BUY_PRODUCT','WHEAT',6],['HIRE'],['HIRE']]`; confirms only after SE unlocks and 6 sheep funded.
- **v219 TOMATO land grab** fires on **day 18** iff `{NW,NE,SW}`, `money>=12000`, `TOMATO price>=CROP_MIN`, `>=3 of PIZZA_SHOP/FARMERS_MARKET`; atomic `[['BUY_LAND'],['BUY_SEED','TOMATO',10]]` (+fertilizer+hires); refuses if the native tape already buys land/plants tomato on steps 432–718.
- Cost model: `LAND_PRICES=(1000,2000,4000)`, indexed by `quadrants_owned-1` → NE $1000 / SW $2000 / SE $4000 tiered by count — exactly as suspected, but gated.
- This **matches our repo memory** ("Quad SE conditional arb — 4-quadrant works only as gated TOMATO scarcity overlay (v219)"). We already knew v219; the sweep adds v233 (wool) and the hard qualifier sets.

## Sell-timing approach (top vs us)

- aurax7 **Reactive Router** sale timing + shed projection is the shared substrate (in our base too).
- Newer layers we lack: **sell_lead / front_run suppression** (order your SELL ahead of shop-consumption windows and ahead of the opponent's glut), **clamp_sells** (cap qty to avoid driving premium prices to $1 floor), **bounded 3-turn sale advance** (tetsutani), and a **22-unit opening WHEAT round-trip** (buy 22 WHEAT turn 1 / sell turn 2 under a cash guard) to *shape the shared price curve* early — not a farming gain, a market-attack.

## Meta shifts since 2026-09-11 (what 3000+ code does that our 7-turn-rescue shop-router base does NOT)

1. **Shop-composition-conditioned policy selection (EXP241):** a hand-fit lookup table picks expert `V39` (yarn-specialized worlds) vs `EXP240` (other shops) from the **first-two-shop draw's YARN_STORE count** at step 144, with a **rival-state route override** keyed on `(rival money, wheat inventory)` sampled at step 2, and a fixed day-27 endgame route. We route one tape; they route an *ensemble chosen by the revealed shop mix*.
2. **Two gated 4-quadrant capital overlays (v233 wool @day12, v219 tomato @day18)** bundled "funded atomic opening" (EXP257: land + animals/seeds + feed + hires in one turn, budget-guarded, zero-overflow validated). We have the v219 idea but not v233, not the atomic bundling, and our submission shows no BUY_LAND gating.
3. **Market-queue microstructure layers:** sell_lead / front_run suppression / clamp_sells + the 22-unit opening WHEAT price-shape attack. Our base sells on tape schedule, not adversarially.
4. **Hardened terminal planner:** our "7-turn rescue" is now "E182 physical-closure" — 64 candidate re-routes, strict positive physical delivery certificate, and **post-deviation cargo recovery/salvage** when live obs diverges from the plan.
5. **Honest-ladder caveat (methodology shift):** top notebooks now ship live-vs-replay reconciliation and note that byte-identical agents scored 2579–2956 across notebooks, and replay-panel wins (+869 mean margin) do NOT transfer to live. This aligns with our own memory ("Engine 1.32.7 hinge: gates run pre-09-19 on 1.32.6 are stale") — treat any pre-09-19 local gate as unreliable.

## Practical next steps for us (2194 → 3023 cutoff)

- Highest ROI: port **EXP241 shop-composition selector** + **v233 wool overlay** + **sell_lead/clamp_sells** onto our existing Shop0909 spine (they are drop-in layers, not rewrites). Then the hardened E182 closure with cargo recovery.
- Verify everything against the **live 1.32.7 engine** (memo: pre-09-19 gates stale) and against the **destbreso 45k-matchup benchmark** + **georgymamarin episodes dataset** (`first_land_day`,`peak_crew`) before spending a submission slot.
