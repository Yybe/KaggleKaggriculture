# FINDINGS_DSM_BATCH — DNA of 30 winning games of DSM (LB rank 1, sub 56427917, 88W-0L-0T)

Date: 2026-09-22. Pure offline JSON analysis (`tools/dsm_batch_agg.py` → `results/dsm_batch/agg_stats.json`). No arena benches run (ARENA.lock held elsewhere).

Sources:
- 30 per-episode profiles `results/dsm_batch/profiles/prof_<ep>.json` + `results/dsm_batch/manifest.json` (20 tightest-margin top-10 peer fights + 8 mid + 2 blowouts, all DSM wins).
- OLD DSM fossil (ep 111471044, the −21,579 game vs our h20/r78ub pair): `results/dna_profile_live144.json` seat '1'.
- Our current best r78ub in the SAME world as the fossil: `results/dna_runs/g1_live_seed_prof.json` seat '0' (88,408 vs DSM_tape 109,949).
- Prior verdict context: `results/FINDINGS_DNA_TOP10.md` §(d) ("old DSM was tempo-only vs field medians") — re-tested here.

Every stat below = season sum/median over the 30 day-dicts of the seat. "vs opp" = median over the 30 top-10 opponents DSM beat in these very games.

---

## (A) ALWAYS-ON vs WORLD-GATED

### A.1 Core invariant engine (30/30 or ~100% fire-rate — copyable, world-independent)

| Behavior | Batch range | Median | Opp median | Read |
|---|---|---|---|---|
| Wheat cycle: plant d0, replant ~23/30 days | plantings 94–187, days 21–23 | 144 / 23d | 153 / 23d | field-generic, always-on |
| Melon: 10–11 seeds at d0, never later | plantings 10–11, first day 0 | 10 / d0 | 12 / d0 | ALWAYS-ON, razor-tight (range width 1!) |
| Strawberry: FIRST PLANTING EXACTLY d2 in 30/30; trickle-plant 6–14 days | plants 19–41 | 31.5 / 8.5d | 33 / 7d | field-generic but the d2 invariant is a schedule, not a reaction |
| Tomato trickle: ≥2 plants every game, first day d9–18, 1–11 planting days | 2–25 | 10 / 5.5d | 4 / 2d | ALWAYS-ON presence; volume is world-gated |
| Geese line: geese bought, buy-days, first buy, alive at end, eggs sold every game | 2–10 geese / d6–10 first buy / eggs 2.6–15.0k | 7.5 / 5 end / 10,798 egg$ | 3 geese / 10,236 egg$ | ALWAYS-ON presence (100%); scale is world-gated |
| Fertilizer = PRODUCT, never INPUT: fert_applied counter 0 in 30/30 (and in old DSM, and in r78ub — field note: the per-day fert_applied/collected counters are dead weight; the live signal is hands ops: FERTILIZE 168–223, COLLECT_FERTILIZER 346–475) while selling fert every game | 10.9–16.8k fert$ | 12,552 | 16,022 | always-on monetization; free-collect loop |
| Land script: quad2 **exactly d6** and quad3 **exactly d9** in 30/30, 2–3 BUY_LAND orders, quad4 NEVER reached (0/30) | 3 quads end | 2 BUY_LAND orders | opp quad3 median d8 | deterministic schedule; NOT land denial |
| Workforce: total hires | 295–349 | 308 | 287 | always at/above field |
| Tempo: hand_idle (cmd-weighted) never above 2.6% | 1.15–2.52% | 1.98% | 6.01% | THE DSM signature; even its worst game beats the field median by 3.5x |
| Sell granularity: SELL orders / median clip units | 372–467 / 2–3 | 426 / 2 | 368 / 4 | always-on |
| Cash discipline: days START under $1,000 / under $100 (cash floor ~$0–2 redeployed same day, never defaults) | 8–10 / 4–7 | 9 / 6 | 9 / 4 | always-on aggression |
| Endgame: sell value released d28–29 (share); terminal shed value | 8–15% / 0–631 | 12% / 2.5 | 15% | trickle-to-close, no cliff; terminal leftovers ≈ 0 |
| Price-floor discipline: WOOL/STRAWBERRY/MILK sold at price<$20 as share of those goods' value | 0–2% in 29/30 games | ~0% | ~1% | near-invariant |
| Outcome: margin per game | +3,220…+105,283 | +10,322 | opp reward med 103,708 | 30/30 wins; beats top-10 field by ~10% score |

### A.2 World-dependent (gates — do NOT hard-copy, must stay conditional)

| Behavior | Evidence of gating |
|---|---|
| Carrot program depth | 0–177 plants (median 35.5); the 0-carrot game ep 111687896 still won +8,395; the 177-carrot game (ep 111689760) was DSM's LOWEST score (84,680) — carrot is opportunistic fill, not core |
| Tomato volume/timing | 2 plants @d18 (ep 111660430, $1,062 egg-thin tomato) vs 25 @d9 (ep 111675172, $16,789); first-day tracks own cash/land pressure d9–18 |
| Geese scale | 2 geese (eps 111671713, 111665909, 111652465 → egg rev 2.6–2.9k) vs 10 (eps 111691231, 111663794, 111613202, 111689760 → 12.3–15.0k); never below 2 |
| Terminal FEED/CARE ops | 0–38 (median 4.5): zero in the fossil world 144, 38 in ep 111615401, 11 in eps 111730163/111632018/111671713. The "starve the flock at d28" story from §(a) of FINDINGS_DNA_TOP10 is WORLD-SPECIFIC, not core |
| Milk deep-dump | only outlier ep 111689760 (10.6% of milk value at <$20, ep 111615401 4.7%) — in the 84.7k low-score world DSM dumped slightly; elsewhere ~0 |
| Blowout margins | +90k/+105k (eps 111615401, 111613202) are vs 52k-score opponents; vs true top-10 peers the margin is +3.2–11.4k. Don't read blowouts as mechanism |

**Bottom line (A):** the always-on list IS the strategy: d0 wheat+melon, d2 strawberry, d6→d9 land script, free-collect fert → sell fert, goose/egg line always present, tomato always present, 2% idle, clip-2 sells, run cash to ~$0, trickle-sell to d29 with ~0 leftovers and no sub-$20 dumps. Everything else (carrot depth, geese count, tomato volume, feed wind-down) is a gate that flexes with world prices/cash.

---

## (B) OLD DSM (fossil, world seed 1437108706) vs NEW unbeatable submission

**Result: no material change detectable at any statistic.** The fossil seat-1 profile sits INSIDE the batch [min,max] on **all 57 computed stats** (0 outside). "Outside its range?" column below answers: *is the old single-world value outside the new 30-game distribution?*

| stat | batch_med | batch range | old_DSM | old outside range? | r78ub | r78 outside range? |
|---|--:|---|--:|:--:|--:|:--:|
| reward | 113,329 | 84,680–153,083 | 109,974 | no | 88,408 | no (bottom of band) |
| margin | 10,322 | 3,220–105,283 | 21,579 | no | −21,541 | **YES** |
| total_hires | 308 | 295–349 | 296 | no | 279 | **YES** |
| TOMATO_plantings | 10 | 2–25 | 15 | no | 0 | **YES** |
| TOMATO_sell_val | 6,138 | 1,062–16,789 | 8,935 | no | 0 | **YES** |
| GOOSE_buy_count | 7.5 | 2–10 | 4 | no | 0 | **YES** |
| EGG_sell_val | 10,798 | 2,648–15,001 | 7,418 | no | 0 | **YES** |
| quad2_day / quad3_day | 6 / 9 | 6–6 / 9–9 | 6 / 9 | no / no | 6 / 11 | no / **YES** |
| hand_idle_pct_w | 1.98 | 1.15–2.52 | 1.82 | no | 9.82 | **YES** |
| sell_order_count | 426 | 372–467 | 455 | no | 246 | **YES** |
| sell_clip_qty_med | 2 | 2–3 | 2 | no | 5.5 | **YES** |
| ops_FERTILIZE / COLLECT_FERT | 204 / 411 | 168–223 / 346–475 | 209 / 399 | no | 71 / 318 | **YES** / **YES** |
| ops_HARVEST | 516 | 458–553 | 505 | no | 415 | **YES** |
| days money_start<$100 | 6 | 4–7 | 5 | no | 1 | **YES** |
| late_FEED_CARE_ops | 4.5 | 0–38 | 0 | no | 28 | no |
| CARROT_plantings | 35.5 | 0–177 | 42 | no | 28 | no |
| STRAWBERRY_sell_val | 38,694 | 12,254–69,200 | 28,065 | no | 29,963 | no |
| shed_final_val | 2.5 | 0–631 | 3 | no | 0 | no |
| WOOL_deepdump_share | 0.00 | 0.00–0.02 | 0.01 | no | 0.04 | **YES** |
| (all other stats) | — | — | — | **all "no"** | — | 11 more "no" |

Full 57-row table in `agg_stats.json["old_vs_batch_diff"]`.

Interpretation:
1. **The new 88-0 submission is the SAME DNA we dissected** — tomato trickle present in both, geese 4 vs batch-median 7.5 (inside range, so the fossil's smaller goose buy is a world-gate not a version difference), quad3 still exactly d9, idle still ~1.8%, clips still 2, cash still floor-dives 5 days <$100. Zero behavioral "what changed" signal; the unbeatability is variance-selected dominance of the same core, not an update we missed.
2. **§(d) verdict SURVIVES**: vs the 30 top-10 opponents in these same games, DSM's unique edges are still tempo (idle 1.98 vs 6.01) and granularity (426 orders/clip-2 vs 368/clip-4) plus double the field's tomato(10 vs 4)/geese(7.5 vs 3) lines — all on axes already adjudicated or already-present in our plan layer. The field median even buys quad3 FASTER (d8 vs DSM's locked d9) — there is no hidden land genius.
3. Where the fossil genuinely differs from batch *center* (not range): lower hires (296 vs 308), thinner eggs (7.4k vs 10.8k), zero late feed — all inside distribution. Honest reading: **nothing to chase in the update; chase the gaps vs r78ub instead (next section).**

Caveat (mandated): the old profile is ONE world; a "no" in the range column cannot prove version-equality, only fail to disprove it.

---

## (C) Where is r78ub? (same-world anchor: fossil world 144, seed 1437108706)

r78ub sits OUTSIDE the 30-game DSM distribution on 26 of 57 stats (column above), i.e. it is behaviorally distinguishable from DSM in ways DSM itself never varies game-to-game. The always-on rows where r78ub violates DSM's invariant band: idle 9.82% (band ≤2.52), clip 5.5 (band 2–3), orders 246 (band 372–467), hires 279 (band 295–349), quad3 d11 (band d9), 1 day <$100 (band 4–7), tomato 0 (band ≥2), geese 0 (band ≥2), wool dump 4% (band ≤2%), harvest/fertilize ops below band. It MATCHES the band on reward level, wheat volume/sales, strawberry total volume, carrot, fert-sales, endgame-liquidity and animals lines — our plan layer is fine; the misses are the tempo invariants + the two always-on small programs (tomato, geese) whose gates declined to fire (plus trivial edge overshoots: r78 plants 12 melon vs the 10–11 band, 24 wheat days vs 21–23).

---

## Actionable deltas for a hybrid build

Ranked by median $ edge in these 30 games (DSM batch median minus r78ub single-world value; gross, mirror play will realize a fraction). Tag against the adjudicated-dead list {sheep/wool V233, fert-intensity fert_u45, hire-gate hg1, pipe16 idle workers, sell-order splitting, terminal leftovers, land denial, cow-build h20d}.

| # | Delta | Median $ edge | Tag | Note |
|--:|---|--:|---|---|
| 1 | **Geese→eggs always-on**: buy ≥2 (median 7.5) geese d6–10, hold flock alive, sell eggs all season | +10,798 | **NEW** (not on dead list) | Mechanism exists (HD2/_Y window) but fire-rate must be 100%-like; DSM never skipped it in 30 games. Re-tune the gate, not the build |
| 2 | **Strawberry d2 first plant + 8.5-day trickle** (r78ub: d5, 5 days) | +8,731 | **NEW** | Same field (opp median 41,533 > DSM) — this is meta we under-run, not DSM magic; planting-day d2 is the cheapest invariant to copy |
| 3 | **Tomato trickle always-on**: ≥2 plants even at ~$0 cash, window d9–18 | +6,138 | **NEW** (gate exists — V219 — but never fired for r78ub; absent from dead list) | DSM's min = 2 plants (ep 111660430); a minimum-floor rule suffices; volume stays world-gated |
| 4 | **Wheat cycle throughput** (17,826 vs 13,838 realized) | +3,988 | ALREADY-ADJUDICATED | downstream of fert_u45/pipe16 axes; do not re-litigate |
| 5 | **Carrot ramp depth** 35.5 plants / 7.5 days vs 28/3 | +3,174 | **NEW** (C1 from prior report survives: fire-rate 96.7%, but 0–177 range ⇒ keep the floor, not a fixed count; zero-carrot game still won +8.4k) |
| 6 | **Own-land timing: quad3 exactly d9** via thin-buffer buy (2 days earlier than r78ub) | +1–2k est (prior C2) | **NEW** — distinct from DEAD "land denial" | 30/30 invariant d6/d9; the field median is d8, so the claim is "never later than d9", not denial |
| 7 | **Cash-floor aggression**: start ≥4 days <$100 (r78ub: 1 day) | enabling, not isolable | **NEW** (no dead-list item covers redeploy-to-zero) | the fuel for #1/#3/#6; DSM proves it's safe at 30/30 win rate |
| 8 | **Price-floor on wool/straw/milk** (dump share ≤2% vs r78ub wool 4%) | +0.5–2k | **NEW** (= prior C3, hold-cadence; NOT the dead "terminal leftovers" axis, overlap-flagged with sell-splitting) | batch confirms: DSM never dumps; worst MILK 10.6% in its lowest-scoring world (ep 111689760) |
| 9 | Idle ≤2.5% cmd-weighted (r78 9.8%) | ~1–4k | ALREADY-ADJUDICATED (pipe16) | DSM's hardest invariant (max 2.52/30) — already rejected as a port; leave closed |
| 10 | Clip-2 sells, 372–467 orders | ~+2.8k | ALREADY-ADJUDICATED (sell-order splitting) | |
| 11 | Hires 295–349 | ~+2.1k | ALREADY-ADJUDICATED (hg1) | |
| 12 | FERTILIZE 168–223 / COLLECT_FERT 346–475 ops | ~+5–6.5k | ALREADY-ADJUDICATED (fert_u45) | incl. overlap with #4 |

Explicitly confirmed NON-actions: never buys quad4 (0/30) → land-denial dead ✓; terminal shed ≈ 0 → leftovers dead ✓; fed flock through d27+, wind-down 0–38 ops is world-noise → h20d dead ✓; sheep/wool program sizes vary game-to-game → V233 dead ✓.

---

## Raw data
Per-episode DSM + opponent stats (all 57 keys × 60 seats), aggregates, fire-rates, diff table: `results/dsm_batch/agg_stats.json`. Regenerate: `PYTHONIOENCODING=utf-8 python tools/dsm_batch_agg.py`.

Key per-episode anchors (sorted by margin, all 30 in agg_stats.json): tightest wins ep 111684059 (+3,220 vs Vadim Vasilenko), 111692008 (+4,546), 111660430 (+4,586 — the 2-tomato, d18-tomato stress case); blowouts ep 111613202 (+105,283, 153,083 score, 10 geese, 11 tomatoes) and 111615401 (+90,522, the 38-late-FEED outlier); DSM's own lowest score ep 111689760 (84,680 — the 177-carrot / 10.6%-milk-dump world).

## Top 5 findings (≤200 words)

1. **New submission ≠ upgrade, same animal.** The Sep-21 fossil DSM lies inside the 30-game batch range on all 57 stats (tomato trickle, 7.5-median geese, quad3@d9, 1.8% idle, clip-2, 5 cash-floor days — all present then). No behavioral delta to chase.
2. **True core is a schedule, not a strategy:** quad2 exactly d6 + quad3 exactly d9, 30/30; strawberry first plant exactly d2, 30/30; melon d0 10–11 seeds; idle never >2.6%; ≥2 geese and ≥2 tomatoes every game. Those invariants are copyable verbatim.
3. **Fertilizer is a product line for DSM:** applied-counter zero in all 30 games yet 10.9–16.8k fert revenue per game via free-collect ops — always sell, never buy.
4. **World-gates confirmed:** carrot 0–177, tomato 2–25, geese 2–10, terminal FEED 0–38 (the fossil's "starve the flock" was world noise, not policy).
5. **Actionable for hybrid, ranked by $-vs-r78ub:** goose/egg always-on (+10.8k), strawberry d2 (+8.7k), tomato floor (+6.1k), carrot floor (+3.2k), d9 land timing (+1–2k), cash-floor aggression, no-dump price floor — all NEW per the dead list; everything else lands on already-adjudicated axes.
