# DECISIVE_MECHANISMS_SURVEY_20260924 — zero-tie strategy feed (survey only, no code)
Pin: `kaggle-environments==1.32.7`, `townCenterSellInterval=24`, 720 steps, both seats/seed, seed-level W/L/T.
Standing champion `agents/futurev1_forecast.py`: pooled 6W/0L/26T vs PRED-B (FUTUREV1_ROUND2_LEDGER_20260924.md L4) — safe, tiny edge, tie-heavy. Rule: tie-BREAKERS win the mirror (small edge, residual ties); tie-KILLERS change production every seed (decisive by construction). Killers rank above breakers in §(c).

## (a) Every mechanism with a decisive (non-tie) result
| mechanism | where | result W/L/T + margin (quoted) | decisive? | why it broke mirrors |
|---|---|---|---|---|
| Days 28–30 bulk shed dump (steps 672–719) | Master Guide L124; V11 doc L26: 22W/10L/0T +63.5 vs funding; fleet 153W/39L/0T 79.7% | W, +63.5 / +225.8 fleet | YES | empties shed into open slots 48 steps; tape-fixed sizes no longer strand residual |
| v57 funding-order-invariant chassis swap | V57_FUNDING L17-20: 26–28W vs V5/V6/E94/r78u, +242..+265, 0 ties/256 games | W, +242..+265 | YES (killer) | foreign spine: no shared tape → zero ties by construction |
| Debt-ledger %23 preempt, floors F90 (90/30/140) | V12_F90_CANDIDATE L23-27: R1 7W/1L +130.2, R2 5W/3L +262.8, Fresh 9W/7L +99.7 | W then refuted | NO (breaker) | T3 holdout 15W/15L/2T +87.7 p=1.00 (T3_HOLDOUT L21) — bank luck, WHEAT-only fires |
| Un-debted step-23 preempt (V8) | Master Guide L120: 0W/32L −165k | L, −165k | YES | collided with v57 `_cxd_candidates` funding queue, broke hires — no debt ledger |
| Tomato gate + preempt (V9) | Master Guide L121: 13W/19L −102.9 | L | YES | preempt still thrashed funding slots; gate alone insufficient |
| F90-floor retune (V6 vs V5) | V6_V5_STUDY L28-31: R2 −53.4→+83.1 vs E94, −25.8→+110.7 vs r78u | W on R2 bank | WEAK-YES | removed −563/−592 floor-tail loss class; head-to-head mostly ties (39/48) |
| Mature-wheat CL tail (+28) | FRIEND_INSIGHTS L25-26: 16W/0L +27/+28 every game | W, +28 | YES (micro-breaker) | extra maturation day + deterministic late harvest; uniform additive |
| V35 STR-front dump reorder | V12 doc L21-25: pooled 43W/0L/21T vs V11; fleet 145W/46L/1T | W vs parent, 21T | BREAKER | 1 reordered turn/ep; +71..+659 (≤0.6%, VERIFY_V35 L37-38) |
| PRED-B shop-oracle (25/35/30) | FINAL_REPORT L26-29: pooled 23W/0L/9T vs V11 | W, 9T/64 | BREAKER | d30 STR-front + oracle gate; near-clone mirrors tie on neutral seeds (L47) |
| FutureV1 forecast preempt (backed-only) | ROUND2_LEDGER L4: 6W/0L/26T, +0.6..+1.0 | W, 26T/32 | BREAKER | safe ceiling of preempt family; 26 ties = still mirror-bound |
| Horizon-B unbacked %23 window | ROUND2_LEDGER L6-13: 3W/1L/4T +2.8, loss 6M −3 | refuted | NO | parent wheat sells phase-locked %24∈{2,3,4}; repays land outside N=3 window |
| Contest-plant redirect (wheat→tomato/carrot) | ROUND2_LEDGER L15-23: 0W/8L/0T −7546 (min −8954) | L, −7546 | YES | redirected tomato never harvested on wheat-locked routing; carrot liquidates at floor |
| Marginal late hires (V13-L) | V13_GATE L25-26: 0W/8L/0T −815.9 | L | YES | fib wage + feed overhead; extra hands never amortize |
| Hold-percent sell timing (V16) | V12_F90_CANDIDATE L58: 0W/8L −4211.5 | L | YES | held produce hits 100-item cap, discarded |
| Tomato takeover + early SW (V17) | same L59: 0W/8L −16,923.4 | L | YES | converted wheat tiles (wheat 25→7, weeds 7→14) |
| Clip clamp 1000-unit sells (V18) | same L60: 0W/8L −106,821 | L, catastrophic | YES | withheld supply raised shared curve opponent sold into |
| V28 shop-route refit | V28 doc: R1 8W/0L +1452.1; then E28 R2 4W/2L/2T, Fresh 8W/5/3T +169; T3 pooled −312 p=1.0 (V12 doc L43) | overfit → refuted | NO | 64-key table on ~12-class support; regime-only rule reverses OOS |
| Sheep→cow mix swap (E30) | ROUTE_HUNT L40: 4 probes −2761,−8282,−4092,−7259 | L | YES | tape economics + care schedule coupled; species not free |
| Majkel tape replay (E31) | ROUTE_HUNT L48: 0W/8L −159,289 | L | YES | live tape is seed/world-specific, not portable |
| Livestock transplant (E32) | ROUTE_HUNT L56: −162k..−197k | L | YES | unit positions world-specific; needs new planner |
| DSM tape replay (E36) | ROUTE_HUNT L99-100: 27,888 vs 156,092 | L | YES | fixed replay cannot preserve physical state |
| Herd-buy overlay (E104b) | E104 L100-104: −65,875 (−43%) | L, decisive | YES | tape-locked 6-cow herd; extra buys crowd ≤10 market slots, starve wheat engine |
| Fert-scope rebind (V30/V33) | V12 doc L41: R1 2W/6L −265.8 / 1W/6L/1T −293.5 | L | YES | extra $120 units crash shared curve |
| Carrot drip on PASS (V34) | V12 doc L42: 1W/7L −694 | L | YES | idle tiles not free; 2–4 drips/game |
| MW/MILK-WOOL expansion (PRED-FINAL) | FINAL_REPORT L9-14: R1 5W/2L/1T (−54/−26) where V35 wins +71 | refuted | NO | expansion EV-negative; mw never fires on probe |
| Shadow-price SELL reorder (E47) | ROUTE_HUNT L239-240: R1 4W/4L +11.4 (±463) | parity | NO | ordering active but unstable; trace inconclusive (E48) |
| V13 fertmax turn-substitution | V13_GATE L11: +3/game; 45/52 tile-eligible blocked `carried==0` | tie-grade | NO | logistics-bound, not turn-bound |

## (b) Top-field DNA vs our spine — every axis the field plays DIFFERENTLY on every seed
Counts: my replay parse of `_scratch_dsm_top/episode-*.json` (DSM=p1; rewards [116140/119530], [87191/89379], [99927/112517]); spine refs processing.md Ph3, Master Guide Ph2, V11 forensics, V29 census, PHASE_DNA_TRACE.
| axis | top-field (every seed) | our spine | tie-killer? |
|---|---|---|---|
| Fert intensity | 224 / 244 / 261 FERTILIZE (also flaw-report 224/244/261, band top/above 135–249) | 85–110 (processing L60); V11 95 (DNA_TRACE L11), 106 (forensics L76), 114 (V29 L16) | YES — 2× gap on all 3 seeds |
| TOMATO program | 19 / 24 / 35 plants, ≥2 every game (flaw L43-46) | 0 (Master L60; V11 forensics L80) | YES — exclusive lane, shelf-stable px 62–69 (flaw L29) |
| CARROT program | 42 / 42 / 66 plants | 34–46 block-plant d24–28 only (forensics L80-81) | YES — field drips 1–2/day from d8 |
| Goose/egg line | 7–12 goose buys, EGG 293–388 qty sold | ~5–6 cows / 5–6 sheep plateau, egg line thin (E104 L27, L45) | YES — always-on presence 30/30 (DSM_BATCH L25) |
| Hire curve | 312 / 316 / 335 HIRE orders, early +6..+13/block (flaw L48-49); batch 295–349 (DSM_BATCH L28) | 265–280; V29/V13 ~266–272 | YES — early-heavy, never below field |
| %23 discipline | SELL %23 share 0.108–0.15; TOMATO 10/23, CARROT 7/24 at %23 (flaw L52-56) | rigid %24 waves (Master L61); V11 trough hours 0–3 = 41% of sells (F90_CAND L130) | YES — contested MILK/STRAW scattered, exclusive items disciplined |
| Endgame dumps | 70 / 76 / 80 orders d28–29 (flaw L58-63); trickle-to-close, shed ≈0 | V11 dumps inside tapes + graft (TAPES L10-16); E94-clone coin-flip losses at d30 (forensics L68) | PARTIAL — dump exists; discipline/granularity differs |
| Cash floor | 4–7 days starting <$100, redeploy-to-zero (DSM_BATCH L31) | ~1 day <$100 (DSM_BATCH L91) | YES — enabling fuel for programs above |
| Land script | quad2 exactly d6 + quad3 exactly d9, 30/30 (DSM_BATCH L27) | NE@d7, SW@d12, SE never (FRIEND L91-92); V11 buys @151/266 (forensics L82) | YES — deterministic schedule, never later than d9 |
| Herd scale | 19–25 pastures, 14–16 cows (E104 L45-47); winners median 8 cows day-6/9 burst (E104 L209-212) | 12 pastures / ~6 cows plateau d14+ (E104 L44); pool max 9 COW xor 14 SHEEP (E104 L139-140) | YES — tens-of-thousands axis, pool content missing |
| Sell granularity | 426 orders/clip-2 (DSM_BATCH L30); my parse 433–480 SELLs | 246 orders/clip-5.5 (DSM_BATCH L91); my parse opp 373–639 mixed | adjudicated-dead (sell-splitting) — NOT a killer |

## (c) Ranked top-5 tie-killer candidates (singly-gatable, one production change each)
1. TOMATO-native production chassis (new lineage/tape, not overlay). Behavioral change: 19–35 tomato plants + shelf-stable TOMATO sells every seed; field's uncontested lane (+11k TOMATO rev, flaw L79-80). Decisiveness: highest — exclusivity decided ep443 (+2188) and vanished vs DECEM mirror (flaw L46). Risk: contest-plant overlay warns 0W/8L −7546 (ROUND2 b) — wheat-locked routing cannot host tomato; must be chassis/lineage swap via `tools/extract_live_opponents.py` + elimination matrix. Avoid: anti-glut crop mixing (FRIEND §2 L81, value ≈$0); PASS-only tomato (V20 inert, F90_CAND L60).
2. Fert crop-scope rebind (tour whitelist → STRAWBERRY/MELON, funded by existing flow). Change: 114→~221 applications with zero purchases (V29 L132-138; 343 u/ep currently exported at $1.5, L75-76). Decisive: closes half the 2× intensity gap every seed. Risk: V30/V33 warn R1 2W/6L −265.8/−293.5 (V12 doc L41); naive `:2153` patch wipes actions to all-PASS (V29 L178-180) — must re-bind forecast+path+joint-plans + retune `1.5*cost+50`. Avoid: purchase-volume axis (V29 CLOSED L14-16); MAX_WORKERS (slack, V29 L98-103); V13 fertmax turn-substitution (+3/game).
3. Herd-scale expansion (cows 6→10–14, 19–25 pastures, day-6/9 coordinated burst + wheat/hire co-design). Change: daily MILK stream doubles from d14 on; V11 plateaus while field keeps buying d6–16 (E104 L45-47). Decisive: tens-of-thousands axis (E104 L49-51). Risk: E104b overlay warns −65,875 (E104 L100-104); E30/E33 species swaps warn −2.7k..−8.3k — isolated buys starve; pasture+feed+care must be one packet (E105 port spec L222-228). Avoid: price-only swaps (E33); route re-select (pool animal-maxed, E104 L139-140).
4. Shop-system re-fit done hierarchically + new tape content. Change: different mid-game production (20–40% action volume) per shop draw every seed (TAPES L42-43). Decisive: only axis above the ±0.35% overlay ceiling (TAPES L20-29). Risk: V28 warns OOS reversal −312 p=1.0 (V12 doc L43); E28/E29/E40 warn regime-only, mid-game switch, price-only scoring all reject. Avoid: 64-key ordered-pair tables (order noise, V28 L72-87); post-commit swaps (E37 ties); day-27 route change (inert, TAPES L45-48).
5. Hire-curve + cash-floor aggression co-designed with throughput (early-heavy 295–349, redeploy-to-zero, d6/d9 land). Change: labor + land timing differ every seed; fuel for killers 1–3. Decisive: medium — enabling, not isolable (DSM_BATCH L107). Risk: V13-L warns 0W/8L −815.9 for late marginal hires; FRIEND §2 L84 refutes "leaner hiring" inversion (winners hire MORE). Avoid: late-window +1hire overlays; any hire change without wheat-supply co-design (E52/E59 collapse).

Dead axes — do not spend (FRIEND_INSIGHTS §2 L74-86 + ROUND2 refuted a/b): hold-for-reprice; pull-forward bulk liquidation; late-dump avoidance; sheep/wool V233 gates; fert-intensity-as-ROI-bug; land denial / anti-glut mixing; MAX_ORDERS fixes; HybridOpening; leaner hiring; 3-tier/cut-24/cut-16 gates; god-mode store-RNG; Horizon-B phase-locked repays (ROUND2 a); contest-plant redirect (ROUND2 b); MW-expansion (FINAL −54/−26); clone-preempt unsized (PRED-C 6M −3); V8/V9 un-debted preempts.
Tie-breakers (rank below killers — keep as finish, not strategy): %23 debt preempt (f90 parity p=1.00), terminal sweep 716–719 (dormant when shed drained, FINAL L9), V35 STR-front reorder (≤0.6%), PRED-B oracle, FutureV1 forecast.
