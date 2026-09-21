# Ebi WHEAT "bulk round-trip arb" — actual margin, episode 111594513

Ebi = seat 0 (reward 111,857), us = seat 1 (94,460), seed 109727367.
Script: `results/E99_losses/111594513/ebi_arb_margin.py`

## Semantics that decide the answer
`obs[t]` is POST-action: `inventory[t]` already absorbs step t's fills and
`prices[t]` already contains step t's own impact. Money drift on quiet steps
(no market op, no hire) is **exactly 0** in 434/434 samples, so per-step money
deltas are ground truth for realized fills. Reading the tape instead of the money
is what creates the phantom spread.

## What Ebi actually ran
Not a carry. 82 identical flips: `BUY_PRODUCT:WHEAT q` at hours 5/9/13/17/21 and
`SELL:WHEAT q` **one step later, same quantity** (buy→sell gap = 1 step in 83/97
cases). Peak market-bought position 90 u (4.4k notional); nothing held overnight.
Totals reproduce the tape: bought 6,458 / sold 6,620 u.

| phase | buyQ | sellQ | tape px[t] buy/sell | apparent | tape px[t-1] buy/sell | apparent | **realized buy/u** | **realized sell/u** | **margin/u** | gross | /day |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 d12-17 | 2,045 | 2,003 | 41.24 / 38.17 | −3.07 | 38.17 / 41.29 | +3.12 | 39.48 | 39.61 | **+0.129** | 248 | 41 |
| P2 d18-25 | 2,992 | 2,952 | 46.59 / 44.36 | −2.22 | 44.22 / 46.63 | +2.41 | 45.16 | 45.32 | **+0.154** | 389 | 49 |
| P3 d26-29 | 1,421 | 1,665 | 47.14 / 44.73 | −2.42 | 44.96 / 46.70 | +1.73 | 45.84 | 46.02 | **+0.177** | 198 | 50 |

Clean flips cover 5,569 u = 86% of in-phase buys. **Total arb gross 835**
(≈925 extrapolated to all 82 flips) = **~46–51/day**, mean **0.150 px/unit**, max
0.259 px/unit. The per-cycle net is quantised at 8–18 cash regardless of qty
(54–90 u), i.e. an integer-rounding stub, not a price spread. Realized fill ≈
`(px[t-1]+px[t])/2` (predicted 39.71 vs realized 39.48 on P1): the engine gives
average-price execution against your own impact, so buy-then-sell-next-step hands
back your own impact. E57c confirmed on opponent data.

## Attribution of Ebi's +17.4k win
| window | Ebi Δmoney | ours Δmoney | gap | wheat-arb | % |
|---|---|---|---|---|---|
| P1 d12-17 | +30,137 | +25,374 | +4,763 | 248 | 5.2% |
| P2 d18-25 | +38,930 | +22,651 | +16,279 | 389 | 2.4% |
| P3 d26-29 | +34,840 | +27,881 | +6,959 | 198 | 2.8% |
| d12-29 | +103,907 | +75,906 | +28,001 | **835** | **3.0%** |

MILK sells alone: Ebi 288 u / $53,422 vs ours 239 u / $42,230 = **+11,193 (40% of
gap)**. Caveat: non-wheat items lack clean single-op steps, so their cash is an
avg-fill estimate (±few %), and hire/production flows overlap; separation is not
exact. But wheat arb is *directly bounded at ≤1k*, so the residual is
production/mix by construction. Our lead peaked +18,828 (d14 intraday; +13,499 at
d12 close) and ended −17,397.

## Verdict
**Do not graft the price-spread arb scaler.** Ebi's realized wheat margin was
0.13–0.18 px/unit — a rounding stub inside our ≤1px sensing floor (E89 stands),
worth ~50/game-day not >2k/day. It does not scale: hitting 2k/day needs ~13k u/day
flipped, more than the entire 10,000-unit WHEAT book, and would collapse the price
(E57c). Ebi beat us with the MILK/production engine, not the market spread — the
6.5k-unit wheat churn was near-zero-EV noise that inflated their tape volume.
Investigate their milk throughput/timing instead.
