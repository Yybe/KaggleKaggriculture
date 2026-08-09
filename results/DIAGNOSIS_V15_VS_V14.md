# DIAGNOSIS: Why V15 can't completely beat V14 (78W/22L)

Date: 2026-08-08 | Method: RESEARCH_RULEBOOK.md discipline | Evidence tags: [F]=file, [G]=game data, [H]=h2h, [S]=static, [R]=replay/trace

## Verdict (TL;DR)

V15's *entire* effect — every win AND every loss vs V14 — comes from ONE lever: `_capselllate_topup`.
`_idle_fill` is a **dead lever** (100/100 exact ties when capselllate is removed). The 22 losses are
all razor-thin (−4…−59) and are the price-timing cases where the +1 top-up sold units cheap while
V14 held them for a later, higher price. Wins are large (+451 max) because late-game prices often
crash, so selling the surplus early is a windfall. capselllate is a *blind* bet: it fires on surplus
alone, never checking price direction.

## Evidence

### 1. Engine is deterministic — every delta is a real mechanism [G]
V14 vs V14 mirror, 8 seeds × 2 seats = **16/16 exact ties (delta 0)**.
No noise floor. V15's 22 losses are not coin flips; they are deterministic seed outcomes.

### 2. `_idle_fill` contributes ZERO [G]
`agents/kaggle_v15_no_capselllate.py` (V14 + idle-fill only) vs V14:
**0W / 0L / 100T, Mean +0, every delta exactly 0.**
V14's schedule leaves no profitable PASS slack for idle-fill to exploit in these seeds.
(Note: V15's docstring claims both levers contribute — this is FALSE. Ablation proves otherwise.)

### 3. `_capselllate_topup` = 100% of V15's effect [G]
`agents/kaggle_v15_no_idlefill.py` (V14 + capselllate only) vs V14:
**78W / 22L / 0T, Mean +196, Median +184, Min −59, Max +451** — statistically identical to full V15.

### 4. Loss profile [G]
All 22 losses: seeds {3241, 3533, 3971, 3168, 2292, 3898, 4774, 3387, 4482, 4044, 2511} × 2 seats.
Deltas −4…−59. Wins reach +451. Asymmetry: crashes are steep, recoveries are gradual.

## Mechanism (traced with trace_loss.py) [R]

capselllate fires when step ≥ 480 AND shed[good] > planned qty for STRAWBERRY/MILK/WOOL: sells +1
extra unit immediately instead of letting the schedule sell it at the later terminal dump (~step 666/716).

- **Loss seed 3241 (−59)**: STR price low early, recovers late (7 → 28 → 68 → 114 by 714).
  V15 sells +1 STR at 622 (px≈7) and +1 at 648 (px≈28); V14 holds and sells 25 STR at 666 (px≈68).
  The +1 units were sold at ~7–28, forfeiting the ~68–114 late price. Loss ≈ 2 units × ~30 = −59. ✓
- **Win seed 2584 (+451)**: STR price high early, crashes late (204 → 114 → 47 → 39 by 666).
  V15 sells +1 STR at 566 (px≈204) and +1 at 622 (px≈114); V14's 25-unit dump at 666 fetches ≈39–47.
  Early sale captures ~160/unit more. Wins are large because the pre-crash price gap is big. ✓
- Base demand (PASS-agent price_trend.py) is RISING in ALL seeds — not the discriminator. The
  discriminator is the *realized* price path under both agents' supply schedules.

## Why wins >> losses (asymmetry)
Terminal liquidation @716 floods the market late → steep downward price moves when demand is
already saturated. capselllate sells BEFORE that glut → large gains. Losses happen when prices
recover in the final stretch; only 1–2 surplus units are mispriced → losses capped small (−59 max).

## V16 candidates (pre-registered, one lever per cycle)

1. **Price-gated capselllate [candidate]**: fire +1 ONLY when current market price is high
   relative to recent history (e.g., px ≥ trailing-N mean) or when price trend is falling —
   i.e., sell surplus now only if selling later would fetch less. Kills the 22 blind-bet losses.
   Gate test: 11 loss seeds must flip to win/tie ≥ 8; win seeds must NOT regress.
2. **Expected-liquidation gate [alternative]**: compare current price to the price at the step
   the surplus would otherwise be sold (terminal dump step) using the demand curve / trend.
3. **Remove `_idle_fill`** (harmless, dead — shrinks diff surface, no behavior change).
4. Nested test on the 8-seed family (1M 9M 3.33M 7.77M 5M 6M 8M 2M), ≥6/8 + positive mean → N=100.

## Files
- `results/diag_v14_vs_v14_mirror.txt` — 16/16 ties
- `results/diag_v15_vs_v14_100.txt` — 78W/22L per-seed table
- `results/diag_v15_no_capsell_vs_v14_100.txt` — 0/0/100 (idle-fill dead)
- `results/diag_v15_no_idlefill_vs_v14_100.txt` — 78W/22L (capselllate = everything)
- `trace_loss.py`, `price_trend.py`, `diag_bench.py` — tooling
