# LIVE FORENSICS 2026-09-20 (B) — scout 56387781 (`pub_metav4_early`) loss anatomy, fresh data

Data sources: `ListEpisodes(56387781)` (1 call, raw saved to
`results/live_replays_0920b/_listing_raw.json`, parsed to `_episodes_parsed.json`);
8 fresh replays in `results/live_replays_0920b/` + 8 already-local loss replays
(`results/bigloss_0920/`, `results/scout_metav4_0920/`) reused, not refetched.
Step-level extraction by `tools/live_loss_anatomy_0920b.py` (no engine runs); full text in
`results/live_replays_0920b/_anatomy_all.txt`, machine-readable in `_anatomy.json`.

**API notes.** (1) `ListEpisodes` returns only the ~90 most recent episodes: our entire visible
history is 89 games inside one UTC day (2026-09-20 08:53:49Z → 16:09:46Z) plus 1 self-play
VALIDATION episode (111159927, excluded). Nothing older than 08:53Z is retrievable, so a true
"last 2 days" sweep is impossible; the pre-09-20 history only survives in
`results/scout_0920/summary.json` (59 eps to 09-19T19:41Z, 43W/10L/5T).
(2) `POST /api/i/competitions.EpisodeService/GetEpisodeReplay` now returns **404 (HTML)** for every
episode including ones fetched successfully hours earlier; `.../requests/EpisodeService/GetEpisodeReplay`
returns 400. Replays must currently be pulled with the CLI (`kaggle competitions replay <ep> -p <dir> -q`),
i.e. via `tools/batch_fetch_replays.py`. `ListEpisodes` on `api/i/...` still works.

## 1. Live state vs the E51 morning snapshot

| metric | E51 snapshot (57 eps, to 111215674 @ 12:09Z) | now (89 eps, to 111281893 @ 16:09Z) |
|---|---|---|
| W/L/T | 48 / 8 / 0 (84.2%) | 69 / 19 / 1 (77.5%) |
| score | 2784.3 | **2827.8** (in-window peak 2853.1 @ 13:17Z → −25 in last 3h) |
| marginal slice | — | **33 new games: 21W / 11L / 1T = 63.6%** |

Rating is *up* 43 pts since the morning snapshot (pool drift, as E54 predicted), but the marginal
win rate collapsed 85.7% → 63.6% and **11 new losses** were added (vs 8 in the submission's first 8.5h).
Loss rate by hour (UTC): 10h 3L · 11h 4L · 12h 2L · 13h 4L · 14h 2L · 15h 3L · 16h 1L — the last four
hours are 9W/10L/1T (45% win rate).
Mean opponent rating: **losses 2823 vs wins 2790**; **all 11** new losses came against opponents rated
2754–2865, and **68 of the 86 opponent submissions in the listing were (re)submitted on/after
2026-09-19** — the tier we now match into is refreshed code, not the pool that produced our 48W run.

### Last 15 games (newest first)

| ep | UTC | res | ours | opp | margin | opponent | opp score | our score after |
|---|---|---|---|---|---|---|---|---|
| 111281893 | 16:09:46Z | L | 84,773 | 92,184 | −7,411 | THIRD FARM CLUB | 2849 | 2828 |
| 111281294 | 16:05:47Z | W | 95,358 | 95,308 | +50 | yefenfei | 2783 | 2832 |
| 111278982 | 15:57:47Z | T | 88,806 | 88,806 | 0 | FinalSunFlower | 2816 | 2828 |
| 111271440 | 15:29:47Z | L | 120,839 | 120,988 | −149 | JamesJJJJJ | 2762 | 2829 |
| 111269794 | 15:25:46Z | L | 108,119 | 108,352 | −233 | kuro0315 | 2853 | 2834 |
| 111268157 | 15:17:47Z | L | 66,657 | 67,134 | −477 | tamura_aicon | 2869 | 2839 |
| 111262046 | 14:57:45Z | L | 101,448 | 101,689 | −241 | HadBoumoussa's Farm 🌾 | 2855 | 2843 |
| 111256614 | 14:37:46Z | W | 110,431 | 110,381 | +50 | neuro168 | 2784 | 2847 |
| 111255937 | 14:33:47Z | W | 116,728 | 115,319 | +1,409 | Ueddy | 2781 | 2844 |
| 111249185 | 14:09:47Z | W | 120,411 | 119,501 | +910 | Shadowell888 | 2725 | 2846 |
| 111248647 | 14:09:46Z | L | 120,071 | 122,602 | −2,531 | kwa | 2768 | 2840 |
| 111242519 | 13:45:50Z | L | 105,568 | 107,823 | −2,255 | Yanis Belami | 2852 | 2843 |
| 111242244 | 13:45:50Z | W | 95,853 | 95,231 | +622 | julien gaza | 2825 | 2848 |
| 111235668 | 13:21:46Z | L | 93,244 | 93,263 | −19 | Black Mamba Farm | 2836 | 2844 |
| 111234566 | 13:17:46Z | L | 79,988 | 80,002 | −14 | Zhang Feifan | 2857 | 2848 |

Note two of the wins (yefenfei, neuro168) are worth **exactly +50** each, and the losses in the same band
are −14/−19/−149: at this tier roughly a third of our games are decided by a single settlement tick, so
the observed W/L is dominated by coinflip variance (win-side replays not fetched, budget kept for losses).

## 2. New-loss table (episodes after the E51 snapshot, newest first)

margin % = margin / opponent bank. Class: (a) close tape mirror <10%, (b) fert-intensity /
structural production gap, (c) our collapse, (d) new pattern.

| ep | UTC | opponent (sid, sub date) | ours | opp | margin | class | replay |
|---|---|---|---|---|---|---|---|
| 111281893 | 16:09 | THIRD FARM CLUB (56395336, **09-20 13:18Z**) | 84,773 | 92,184 | −7,411 (−8.0%) | **(b)** | yes |
| 111271440 | 15:29 | JamesJJJJJ (56387092, 09-20 08:32Z) | 120,839 | 120,988 | −149 (−0.1%) | (a) 91.1% identical | yes |
| 111269794 | 15:25 | kuro0315 (56393050, 09-20 12:00Z) | 108,119 | 108,352 | −233 (−0.2%) | (a) 83.1% | yes |
| 111268157 | 15:17 | tamura_aicon (56375556, 09-20 01:10Z) | 66,657 | 67,134 | −477 (−0.7%) | (a) 80.7% + dump-family | yes |
| 111262046 | 14:57 | HadBoumoussa's Farm 🌾 (56392291, 09-20 11:26Z) | 101,448 | 101,689 | −241 (−0.2%) | (a) 93.6% | yes |
| 111248647 | 14:09 | kwa (56392117, 09-20 11:20Z) | 120,071 | 122,602 | −2,531 (−2.1%) | **(b)** 0.1% identical | yes |
| 111242519 | 13:45 | Yanis Belami (56372360, 09-19 22:10Z) | 105,568 | 107,823 | −2,255 (−2.1%) | (a) 83.1% + dump-family | yes |
| 111235668 | 13:21 | Black Mamba Farm (56379608) | 93,244 | 93,263 | −19 (−0.02%) | (a) by threshold | not fetched |
| 111234566 | 13:17 | Zhang Feifan (56370245) | 79,988 | 80,002 | −14 (−0.02%) | (a) by threshold | not fetched |
| 111231254 | 13:05 | 涵哥 (56375637, 09-20 01:15Z) | 121,217 | 145,810 | **−24,593 (−16.9%)** | **(b)+(d)** | yes |
| 111227916 | 12:53 | SJY321 (56362313) | 79,883 | 80,703 | −820 (−1.0%) | (a) by threshold | not fetched |

New-loss point damage totals −38,743; the three structural losses (TFC, kwa, 涵哥) are −34,535 = **89%**.
Whole-submission tally: 19 losses = 13 tape-mirror coinflips + 6 structural (old: keiz −6,227 /
あかつき −8,465 / KawattaTaido −12,045; new: kwa, TFC, 涵哥) + 0 collapse.

## 3. Per-loss evidence (ours vs opp, from replay steps only)

**111281893 THIRD FARM CLUB, −7,411, class (b) — fert-intensity top-tier board at the 2850 tier.**
Mirror similarity 0.14% (nothing alike). FERTILIZE ops **126 vs 183** (the E53 top-10 fingerprint band
is 135–215; keiz was 182), COLLECT_FERT 373 vs 436, fert bought 100u vs 17u, fert sold 317u vs 270u.
Market-order slots consumed (all order types) **998 vs 1,738**; revenue mix ours 8 lines led by MILK 36.5k,
theirs **9 products** all
between 9.6k and 22.8k (MILK/MELON/STRAWBERRY/TOMATO/WOOL/EGG/FERT/WHEAT/CARROT). Plants: STRB 33 vs 29
but CARROT 39 vs 66, TOMATO 0 vs 22, COOP builds 5 vs 10, GOOSE 3 vs 6 (final herd ours 6S/8C/3G, theirs
9C + liquidated sheep). We led every checkpoint d12–d27 (d18 37.3k vs 29.2k; d26 61.3k vs 56.9k), they
passed at d28 (70.4k) and d30 (82.9k vs 77.5k) on bulk ongoing-product sells (MILK 30 @ d27h0 +7,455;
MILK16+TOM31 @ d28 +4,459; MILK24+TOM30 @ d30 +4,177). Shops in world: PET_CAFE×2, SMOOTHIE×2, PIZZA,
BAKERY, YARN, ICE_CREAM — i.e. their 9-product mix was built to the shop draw, ours was not.

**111231254 涵哥, −24,593, class (b) with a new (d) sub-signature — our own twin + a bigger ongoing-crop/crew endgame.**
Mirror similarity 63.75% and the boards are indistinguishable through day 18 (money within a few hundred
every checkpoint; identical herd 9C/5S/3G, identical land BUY_LAND=3 incl. SE, identical wheat 160 /
strawberry 33 / carrot 34 / melon 12). The gap is created by four deltas on day 19+ :
`BUY_SEED TOMATO **20** vs our 10` (step 434, both ongoing-regrow crops), FERTILIZE **155 vs 136**,
fert bought **126u vs 107u**, cumulative HIRE **300 vs 284** (final hands **15 vs 13**).
Realization is the endgame dump: they ran 84 bulk `SELL <item> 1000` (sell-all) orders, 3 on day 28,
24 on day 29, 57 on day 30, capturing the tomato price spike (TOMATO 552→**611** d28): SELL TOMATO 32 =
+19,812 in one step, 28 = +14,376, 28 = +8,539. Day 27→final inflow: **theirs +83.8k, ours +55.0k**.
We liquidated the same product dribbled out at d27–d29 (6/6/14/20 units) and had nothing left for the peak.

**111248647 kwa, −2,531, class (b) — fert CONSUMER, not fert merchant.**
Mirror 0.14%. FERTILIZE **161 vs our 109**, fertilizer bought **0u** (all self-collected, COLLECT_FERT 351),
fertilizer sold **172u vs our 299u** — they spend their fert on yield instead of selling it (E53 "we are a
fertilizer merchant" law, inverted). Extreme land-burn profile: **18 BUY_LAND orders** (only 3 quadrants
exist, so 15 are no-ops) and 296 hires vs our 265. They trailed us days 12–25 (d12 10.4k vs 16.5k), then
out-earned us in the last 48 steps (d29 103,353 vs 101,831; final 122,602 vs 120,071) with fewer
market-order slots (865 vs 992) — i.e. higher unit value, not more churn.

**111271440 JamesJJJJJ (−149) / 111262046 HadBoumoussa (−241) / 111269794 kuro0315 (−233) /
111242519 Yanis Belami (−2,255) / 111268157 tamura_aicon (−477), class (a) — exact tape-mirror coinflips.**
Action-tape identity to us 91.1 / 93.6 / 83.1 / 83.1 / 80.7%. In all five the censuses are *identical*:
James 127 FERTILIZE both, 268 hires both, 2 land, 482/481 harvests, revenue STRB 47.3k vs 44.0k;
HadBoumoussa 133/133 fert ops, 507/506 harvests, STRB 50.3k vs 48.7k; kuro0315 (the wool-heavy 15-sheep
board) 117/117 fert ops, WOOL 66.9k vs 68.5k — the entire −233 is the wool price race. Yanis and tamura
are the same mirror plus the 84-order endgame dump, which is where their +2.1% edge came from.
Per E42–E47 these are unfixable by plan changes; only sell-timing on identical boards.

**Class (c) collapse: ruled out.** Across all 8 analyzed losses our seat has **0** steps with empty/None
action lists (longest idle run = none), and 10 "non-operative" steps — the mirror twins show the same 10,
so it is structural end-of-day idle, not starvation. Herds never break up (ours stays 6S/8C/3G or
15S/6C/2G from day 14 to 30). The E53g plumbing-collapse signature did not occur live.
Nit found: a stray no-op market slot — in **4 of the 8** losses our seat issues exactly one
`SELL FERTILIZER 997`-style bulk order while holding 0 fertilizer (e.g. ep 111281893 step 671, day 28 h23;
our SELL op count is otherwise 300–388/game). Harmless, but it is the same sentinel shape the dump-family
uses deliberately — and they use it 84×.
*Methodology caveat:* per-product "revenue~" is estimated as n × price-at-order-step with n capped by that
seat's actual shed+carry holdings; for the three dump-family tapes the residual estimate is still inflated,
so those games are classified on money trajectory and op censuses, not on revenue lines.

## 4. Opponent frequency: is a NEW opponent class beating us?

* By account/team name: **no repeats** — 19 losses against 19 distinct team names. JamesJJJJJ is the only
  new-loss opponent we met more than once (3 games: L,W,W).
* By code lineage: **yes, one.** `tamura_aicon` (56375556), `Yanis Belami` (56372360) and `涵哥` (56375637)
  are one policy family: each tape contains **exactly 84 `SELL <item> 1000` bulk-dump orders with the
  identical day schedule {28:×3, 29:×24, 30:×57}** and the same sentinel product set
  {FERTILIZER, MILK, CARROT, WHEAT, STRAWBERRY, TOMATO, MELON, EGG}. Their early tapes are ours
  (48–73% identical to our twin's steps; 0 such orders in James/kuro/kwa; ours = 1 stray).
  That single family produced **3 of the 11 new losses and −27,325 of the −38,743 new-loss damage (70%)**.
* Second new-class evidence: THIRD FARM CLUB — a live top-10 team — fielded a **fresh submission
  (56395336) at 09-20 13:18Z** and beat us 45 minutes later with a 183-FERTILIZE / 9-product board
  (the E51/E53 top-10 fingerprint) at the 2850 tier, not the 3000+ tier. That is meta drift arriving
  inside our matchmaking band, and it also explains kuro0315/HadBoumoussa/James being 80–94% tape
  mirrors of us: the ~2800 pool is now largely our own spine (or theirs) re-baked.

## 5. Artifacts written this pass

* `results/live_replays_0920b/`: 8 loss replays (episode-111231254/-111242519/-111248647/-111262046/
  -111268157/-111269794/-111271440/-111281893-replay.json), `_listing_raw.json`,
  `_episodes_parsed.json`, `_anatomy.json`, `_anatomy_all.txt`, `_fetch_set.json`.
* `tools/live_loss_anatomy_0920b.py` (new, reusable step-level anatomy; holdings-capped SELL estimate,
  collapse-run detection, action-tape mirror %, herd/tiles/money day sampling).
* `agents/live_replay/`: 7 new tape donors extracted with `tools/extract_live_opponents.py` —
  `opp_JamesJJJJJ_2802d824.py`, `opp_kuro0315_fdd5eeb0.py`, `opp_tamura_aicon_d45969a0.py`,
  `opp_HadBoumoussa_s_Farm___f9f446ec.py`, `opp_kwa_67f80680.py`, `opp_Yanis_Belami_03d5c442.py`,
  `opp_涵哥_29ee77a6.py`. **Skipped as already-present by name: THIRD FARM CLUB** (3 donors exist, but
  they are the older top-10 submission 56354460; the 56395336 board that beat us is NOT in the donor dir —
  pull it with `py tools/extract_live_opponents.py results/live_replays_0920b/episode-111281893-replay.json agents/live_replay`
  if a 3000-tier rematch gate is ever built). No agent under `agents/` was modified. Nothing submitted.

## 6. Conclusion — what is most likely driving the slump

* **Not decay, and not a new bug class: 8 of 11 new losses are ≤1% margins against boards that are
  80–94% action-identical to ours, and there is zero collapse signature (0 empty/None action runs).**
  The rating is still net-up (2784 → 2828) — the visible "losing more games" is the expected E42–E47
  coinflip tax, now paid ~3× more often because winning pushed matchmaking into the 2750–2870 band where
  68/86 opponent submissions are <36h old.
* **The damage is concentrated in one addressable signature: endgame production + liquidation, not
  sell-timing constants.** 89% of new-loss points come from 3 non-mirror boards, and 70% from a single
  code family that runs *our own opening* and then (i) doubles the ongoing-crop program (TOMATO 20 vs our
  10 on day 19), (ii) spends the fertilizer we sell (155–183 FERTILIZE ops vs our 109–136, 0–17u bought),
  (iii) adds ~2 late hands, and (iv) dumps every shed in 84 bulk orders on days 28–30 into the price
  peak. The 涵哥 game is effectively a controlled experiment: identical board through d18 → −24,593.
* **This is the E53c/E53g class, now proven live against our own spine — so it is reachable, but not by
  the routes already refuted.** E53b (ROI-constant retune), E53g (berry fert via extra R51 hires) and
  E54 (router-table forcing) all stay refuted; the surviving shape is a *policy* layer the opponents
  demonstrably run: hold-and-dump endgame liquidation on days 28–30 plus an ongoing-crop (tomato/strawberry)
  density step that respects the E53e/E53f labor-reuse and feed-census laws (no new hires mid-day-13 window).
  Suggested next step: probe a sell-schedule/retention overlay (no spine surgery) gated against the 3 new
  dump-family donors + the kwa/TFC donors, and re-pull episode lists after ~12h to see whether the
  63.6% marginal rate mean-reverts as the pool settles.
