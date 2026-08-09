# V15 Real-Match Loss Forensics (5 losses on Kaggle)

## Summary
V15 (submission 55353220, 2630.5 public) went 70W-5L-0T in its 76 live episodes.
All 5 losses were analyzed from downloaded replays (v15_losses/). Every opponent
plays a near-identical V14-lineage tape — this is a clone-war, not a strategy gap.

## The 5 Losses
| episode | opponent | reward V15 vs OPP | delta |
|---|---|---|---|
| 91041844 | wenjinyang | 53,504 vs 53,522 | -18 |
| 91071101 | tetsu2131 | 116,259 vs 117,228 | -969 |
| 91074602 | kevin park | 121,362 vs 123,238 | -1,876 |
| 91085994 | tianwen zhang1 | 98,781 vs 99,488 | -707 |
| 91110282 | Malcolm Durosaye | 72,870 vs 72,880 | -10 |

## Opponent Identity (identical across all 5)
- 2 land buys @ steps 169/265 (day 7/11), max 14 hands
- Seeds WHEAT18/MELON2/STRAWBERRY2 (orders), animals COW5/SHEEP3
- BUY_PRODUCT WHEAT165; farmer PASS 172/720 (23.9%)
- Total sells: WHEAT 305, FERTILIZER 212, WOOL 148, MELON 144 — EXACTLY V14 tape numbers
- MILK 214, STRAWBERRY 320 — i.e., V14 tape + ~25 extra STRAWBERRY, +0 MILK
- Compare V15: MILK 221 (+7), STRAWBERRY 328 (+8) — from _capselllate_topup +1 bumps

## Mechanism: the +1 topup is a blunt instrument
- kevin park (worst loss): V15 sold 8 MORE strawberries but earned **2,223 LESS**
  (30,708 vs 32,931). V15's extra units hit at px 1-24; opponent's held units sold at px 47-85.
- tetsu2131: V15 sold 7 more MILK, earned **324 less** (11,041 vs 11,365) — bumped at px 1-38.
- tianwen: MILK -344 with +7 units. wenjinyang/malcolm: tiny deltas, decided by 1-step timing.
- Across all 5: total SELL revenue of V15 is HIGHER in 4/5 games (wenjinyang +444, tetsu +342,
  tianwen +1,067, malcolm +150) yet V15 LOSES all — extra units depress the shared price curve
  against V15's own larger inventory, and land 1 step AFTER the opponent's dump (post-impact price).

## What winners do instead
- Hold surplus STRAWBERRY/MILK for the day-29 price recovery (d29 prices: STR 36-239, MILK 28-40
  across the 5 seeds) instead of dumping at day 23-27 prices of px 1-24.
- Their extra units land BEFORE the crash / at the recovery window, catching px 47-85.

## Design implication for V15.5
1. PRICE-GATE the capselllate topup: only bump +1 when current market price of the item is
   healthy (STR >= 50, MILK >= 30, WOOL >= 150). Never dump surplus into a crashed market.
2. EARLY RECOVERY LIQUIDATION: at steps ~700-714, if shed has surplus high-value inventory and
   the item price has recovered, sell it BEFORE the tape's step-717 dump craters the price
   (opponents' 25-STR d29 sells at px 85/62 vs V15's at px 24).
3. Keep everything else (idle_fill, weed repair, repay_shift, preempt, rank) identical.

## Tooling
- v15_losses/analyze_losses.py — per-player strategic profile
- v15_losses/price_analysis.py — per-step sells + price path
- v15_losses/revenue_breakdown.py — full-game revenue per item
- v15_losses/money_flow.py — buy/sell/hand flow reconciliation
- Replays: v15_losses/{ep}_*_replay.json (via kagglesdk competition_api_client)
