# V11 LIVE-LOSS FORENSICS — 2026-09-23 (data through 2026-09-22 23:39 UTC)

Subject: Apex V11 (`agents/pub_v57_apex_v11_dump.py`, Kaggle ref **56473970**, publicScore 2043.1, submitted 2026-09-22 20:57:13 UTC).
All numbers below are measured from our own live replays in `results/V11_live_eps/` (god's-eye: the replay JSON exposes `observation.private` for BOTH seats, so opponent shed/seeds are ground truth, not inferred).

Freshness: newest episode 2026-09-22T23:25:04Z = **14 min old** at pull time (23:39Z); oldest 21:00:30Z = 2.65 h. This is V11's first live cohort; the earlier `results/APEX_live_eps/` (09-21T15:xx) belongs to V5-era submissions.

## 1. Episode record (V11, from submission onward)

42 completed episodes for ref 56473970; 41 scored (112161376 has no reward pair — the seed episode). **37W / 4L / 0T**, mean Δ +12,693 (blowout-skewed), median Δ ≈ +3,463, min Δ −1,670, max +110,885. All four losses are ≤ −1,670; every loss is a near-tie.

| ep_id | create UTC | ours | opp | opp_sid | Δ | W/L |
|---|---|---|---|---|---|---|
| 112206933 | 23:25:04 | 83,201 | 81,596 | 56367122 | +1,605 | W |
| 112205595 | 23:21:08 | 64,523 | 62,492 | 56407573 | +2,031 | W |
| 112204253 | 23:17:10 | 71,504 | 73,174 | **56462140** | **−1,670** | **L** |
| 112203471 | 23:13:04 | 113,630 | 104,100 | 56339415 | +9,530 | W |
| 112201477 | 23:09:07 | 107,999 | 108,058 | **56473840** | **−59** | **L** |
| 112200039 | 23:05:05 | 85,151 | 82,441 | 56321145 | +2,710 | W |
| 112198623 | 23:01:11 | 111,038 | 109,842 | 56328567 | +1,196 | W |
| 112197170 | 22:57:07 | 121,655 | 121,437 | 56440134 | +218 | W |
| 112196232 | 22:53:04 | 131,788 | 129,923 | 56325366 | +1,865 | W |
| 112195771 | 22:53:03 | 87,278 | 85,728 | 56263138 | +1,550 | W |
| 112195022 | 22:49:07 | 107,777 | 107,543 | 56325431 | +234 | W |
| 112194384 | 22:49:06 | 98,628 | 94,915 | 56341779 | +3,713 | W |
| 112192816 | 22:45:06 | 79,987 | 76,963 | 56319768 | +3,024 | W |
| 112191447 | 22:41:09 | 135,452 | 127,258 | 56342466 | +8,194 | W |
| 112191395 | 22:41:09 | 86,144 | 86,100 | 56474161 | +44 | W |
| 112189897 | 22:37:06 | 141,832 | 133,281 | 56323492 | +8,551 | W |
| 112188430 | 22:33:07 | 101,873 | 88,625 | 56314365 | +13,248 | W |
| 112186942 | 22:29:05 | 77,743 | 73,058 | 56461645 | +4,685 | W |
| 112185445 | 22:25:10 | 94,865 | 92,268 | 56253496 | +2,597 | W |
| 112184040 | 22:21:21 | 115,450 | 116,075 | **56474117** | **−625** | **L** |
| 112182730 | 22:12:55 | 97,487 | 86,995 | 56283537 | +10,492 | W |
| 112182181 | 22:08:52 | 124,768 | 116,365 | 56275519 | +8,403 | W |
| 112181458 | 22:08:51 | 76,695 | 74,399 | 56309529 | +2,296 | W |
| 112180293 | 22:04:52 | 101,499 | 90,229 | 56312038 | +11,270 | W |
| 112179085 | 22:00:49 | 77,980 | 74,074 | 56254456 | +3,906 | W |
| 112177840 | 21:56:48 | 67,740 | 62,637 | 56208407 | +5,103 | W |
| 112176686 | 21:52:49 | 110,054 | 107,481 | 56445342 | +2,573 | W |
| 112175508 | 21:48:47 | 57,613 | 52,134 | 56257139 | +5,479 | W |
| 112174335 | 21:44:47 | 69,346 | 61,548 | 56339570 | +7,798 | W |
| 112173155 | 21:40:49 | 169,851 | 125,026 | 56112320 | +44,825 | W |
| 112171972 | 21:36:48 | 95,627 | 81,469 | 56193280 | +14,158 | W |
| 112170829 | 21:32:46 | 75,277 | 64,246 | 56299117 | +11,031 | W |
| 112170825 | 21:32:46 | 74,291 | 74,518 | **56473840** | **−227** | **L** |
| 112169716 | 21:28:49 | 103,655 | 83,273 | 56100097 | +20,382 | W |
| 112168596 | 21:24:44 | 131,496 | 113,797 | 56297587 | +17,699 | W |
| 112167426 | 21:20:47 | 118,789 | 82,931 | 56213690 | +35,858 | W |
| 112166210 | 21:16:45 | 119,088 | 104,168 | 56278863 | +14,920 | W |
| 112165056 | 21:12:55 | 105,948 | 68,746 | 55441986 | +37,202 | W |
| 112163864 | 21:08:31 | 124,605 | 87,605 | 55849254 | +37,000 | W |
| 112162727 | 21:04:31 | 162,848 | 51,963 | 56280322 | +110,885 | W |
| 112161549 | 21:00:30 | 79,204 | 22,504 | 56074539 | +56,700 | W |
| 112161376 | 20:57:13 | — | — | — | seed episode, no pair | — |

## 2. Loss isolation (ordered by opponent final reward desc) + mirror classification

Anatomy: `results/V11_live_eps/_anatomy.json`, `_anatomy_render.txt` (tools/live_loss_anatomy_0920b.py), `_flows.txt`, `_almond_mechanics.txt`.

| rank | ep | opponent (sid) | opp reward | Δ | mirror-identical action steps | class |
|---|---|---|---|---|---|---|
| 1 | 112184040 | Utkarsh #2 (56474117) | 116,075 | −625 | **91.4%** | V11-lineage clone coin-flip |
| 2 | 112201477 | Andrey Akifev (56473840) | 108,058 | −59 | **89.4%** | V11-lineage clone coin-flip |
| 3 | 112170825 | Andrey Akifev (56473840) | 74,518 | −227 | **80.6%** | V11-lineage clone coin-flip |
| 4 | 112204253 | アルモンド (56462140) | 73,174 | −1,670 | **27.4%** | genuine strategy divergence |

**Three of four live losses are against tapes that are 80–91% byte-identical to our own** (identical herd curve, identical tile census, identical hires 267/267 and 280/280, identical BUY_LAND steps 151+266). Their per-day money diff never leaves the ±900 band (loss margins −59/−227/−625 = town-cycle + dump-order noise; e.g. 112201477 was +973 for us entering day 29 and the d30 dump decided it, opp d30 inflow 8,830 vs our 7,923). These are the Rule-2 seed-level-tie defect, **not** a new mechanism — already-explained class, do not re-report.

**Only アルモンド (ep 112204253) is a true strategy loss.** Same chassis skeleton (identical hire curve shape, identical land steps 151/266, identical day-1 melon×12 + wheat opening — i.e. an E94/metav4-family route) but a different planner overlay. Anatomy, both seats, god's-eye:

| axis | OURS (V11) | アルモンド | gap |
|---|---|---|---|
| final reward | 71,504 | 73,174 | −1,670 |
| HIRE total | 265 | 276 | −11 (parity; labor not a lever — matches memory) |
| FERTILIZE ops | 106 | 148 | **+42 (+40%)** |
| fertilizer bought (units) | 78 | 98 (incl. 8u @ step 290, 3u @ 315 = d13 trough buys) | +20 |
| COLLECT_FERTILIZER ops | 370 | 367 | ≈0 |
| fertilizer declared SELL | 2,365 | 10,357 (sentinel qty) | opp monetizes fert surplus harder |
| PLANT census | WHEAT 148 / STRB 33 / CARROT 46 / MELON 12 | WHEAT 129 / STRB 27 / **CARROT 72** / **MELON 18** | carrot-drip + melon +6 |
| carrot planting pattern | block-plant only d24–28 (6/5/14/12/9) | **1–2/day steady state from d8**, then d25–28 bulk (13/14/11/10) | continuous high-px crop |
| quad unlocks | BUY_LAND @ steps 151, 266 (NW,NE,SW) | identical 151, 266 | 0 |
| WATER ops | 1,100 | 1,077 | −23 (opp slightly leaner) |
| market-linked inflow (steps carrying SELL orders) | 42,353 | **54,475** | **+12,122 to opp** |
| town/auto inflow (positive delta, no sell order) | **43,508** | 36,119 | −7,389 (opp routes goods AWAY from town auto-sale) |
| gross inflow total d1–30 | 85,861 | 90,594 | +4,733 to opp |
| residual shed @ step 719 | {} (dump works) | {} | 0 |
| money-diff trajectory (ours−opp) | +3,102 at d19 start → +1,124 d24 → **−145 d25** → −1,138 d27 → −2,012 d30 → −1,670 final | | **bleed window = days 19–27 (steps 432–671); crossover at steps ~576–600** |

Phantom-axis warning: the opp's tape shows 6× SELL TOMATO 1000 at steps 713–718 — never planted, never held (`private.seeds`/`shed` TOMATO = 0 all game). These are inert sentinel orders; a naive anatomy pass books them as +38k tomato revenue. Disregard.

## 3. Ranked mechanisms by measured money gap (live losses only)

1. **Sell routing / price timing (town→market shift)** — +$12.1k gross market-inflow edge, net +$4.7k inflow edge after they *gave up* $7.4k of town auto-sale; gap opens d13, compounds d19–27 at +$400–900/day. Matches the Top-10-DNA lever (their sells land at px percentile 60–89, ours 26–31) — first live-loss confirmation against a non-clone.
2. **Fertilizer intensity, supply-side** — +42 FERTILIZE ops funded by buying fert into the d13 price trough (steps 290/315), not by more COLLECT. Drives most of the d19–27 production delta (+$3,709 net inflow swing over the bleed window ≈ $412/day). Exactly the fix direction recorded in memory: "next fert attempt must change the supply side."
3. **Crop mix: carrot drip + melon surplus** — CARROT 72 vs 46 (1–2/day from d8, sold at px 59–67 late-season), MELON 18 vs 12, funded by −19 wheat / −6 strawberry. Coupled to #2 (the drip tiles are the fertilized ones). Per-crop dollar split is not separable from sentinel SELL quantities; direction is unambiguous.
4. **Labor** — 276 vs 265 hires; parity, gap ≈ $0 (consistent with "hires NOT a lever").
5. **Land timing** — identical steps 151/266; gap $0. (Note: their SW buy at 266 equals ours, contradicting the 199–228 top-10 DNA claim — this opponent doesn't pay it.)
6. **Water / endgame dump / shed residual** — all zero-gap; V11's days 28–30 dump executed clean (final shed {} both seats, both sold into steps 672–719). Class-(d) remains fixed.

## 4. Top gap → concrete overlay, and its reachability

**Is the top gap overlay-reachable?** Largely NO for gap #1 in its pure form: sell-step/sell-item selection in our lineage lives inside the route tapes (memory: "tapes are the strategy; overlays capped ±0.35%; dump is already IN the tapes"), and both seats here already run the same tape family — the almond edge is a *re-fitted route*, not an attachable wrapper. But gaps #2+#3 have one genuinely **market-order-reachable** component that the tape proved live and that our spine does NOT do:

**Overlay spec — "d13 fert-trough restock" (supply-side fertilizer arbitrage feeding mid-season FERTILIZE):**
- Trigger window: steps 280–340 (days 12–15), the post-SW-unlock cash trough where our spine buys wheat-feed.
- State query: `obs["market"]["prices"]["FERTILIZER"]` (live) and `obs["private"]["shed"]["FERTILIZER"]`; the correct capacity check is against `private["shed"]` totals (cap 100), never `farm["inventory"]`.
- Action shape: prepend to the market list — `["BUY_PRODUCT", "FERTILIZER", n]` with `n ≤ 8` per order, at most 2 orders/turn, while `prices["FERTILIZER"] <= 25` and shed total ≤ 85, spending cap ~1,700 (= almond's actual d13 spend: 8u@~$25 + 3u@~$27 ≈ $270 plus their d8–11 buys; total fert-buy 98u vs our 78u).
- Companion requirement (the honest part): the purchased units only pay off if planner tasks actually emit the extra `FERTILIZE` ops on d13–27 tiles (+42 in the almond tape). If graft-side `carried==0` blocks recur (V13 fertmax failure mode, 45 blocked for lack of carried fert), this overlay is the *supply* half of the fix, but the *demand* half (which tile gets fertilized) is route-internal — expect partial realization unless the plan task picks it up.
- Expected magnitude ceiling from this loss: ≈ +$400/game on the d19–27 window if half of almond's fert intensity is reproduced; full +$3.7k requires the carrot-drip mix (#3), which is planner-internal / route-refit territory.

**Second, cheaper symmetry note:** 3 of 4 losses are clone near-ties at −59/−227/−625 — per Rule 2 the debt-accounted `step % 24 == 23` preemption is the designed breaker for exactly this class; this cohort adds 3 more tie-grade data points but no new information about it.

## 5. Artifacts
- `results/V11_live_eps/summary.json` — episode list (rewards, opp sids) via `tools/fetch_episodes.py 56473970 ... --list-only`
- `results/V11_live_eps/episodes_raw.txt` — `kaggle competitions episodes 56473970`
- `results/V11_live_eps/episode-{112184040,112201477,112170825,112204253}-replay.json` — via `kaggle competitions replay` (CLI at `C:/Users/xxshi/AppData/Local/Programs/Python/Python311/Scripts/kaggle.exe`)
- `results/V11_live_eps/_anatomy.json`, `_anatomy_render.txt`, `_flows.txt`, `_almond_mechanics.txt`, `_episodetable.txt`
