# WybeV2 H9 — H2H Gate vs V16a (pre-registered in PLAN_H8.md conclusion)

Date: 2026-08-09 | Candidate: submission_v8.py | Opponent: submission.py (V16a champion, root)

## Pre-registration (from PLAN_H8.md conclusion, written BEFORE the run)
"H9: H2H vs V16a on frozen 8-seed family (≥6/8 + positive mean), then feed-priority
fix if H2H shows the escape costing more than the feed tax."

## Measurement
- Runner: tools\diag_bench_seeds.py (real kaggle_environments 1.32.6, make("kaggriculture"),
  720 steps, townCenterSellInterval=24 = scoring engine config)
- Seeds: frozen family 1000000, 9000000, 3330000, 7770000, 5000000, 6000000, 8000000, 2000000
  x 2 seats = 16 games
- File: h2h_H9_v8_vs_v16.txt [F]

## Result [F]
- submission_v8.py: 0 W / 16 L / 0 T | seed-level 0W/8L/0T
- Mean Delta: -122,482 | Median: -130,941 | Min: -140,253 | Max: -69,932
- v8 avg: 22,112 | V16a avg: 144,594
- Worst: seed 1000000 -140,253 (v8 23,351 vs 163,604). Best: seed 7770000 -69,932
  (v8 16,804 vs 86,736 — V16a's weakest seed still wins 5x).

## Verdict: REJECTED — decisive (rulebook §3.4: a gate that fails is a result, not a rerun)
- Gate rule was >=6/8 wins + positive mean. 0/8 seeds, mean -122K. No rerun, no extra seeds.
- The H8 sanity pass (28K vs PASS) was a self-consistency check only: v8's absolute output
  (~22K vs ANY opponent; shared-market interference drops it slightly vs a mass seller) is a
  production gap, not a sell-timing gap. Incremental tuning of the v6.3 crop engine CANNOT
  close 6.5x. The v6.3/v8 line is a research artifact; the champion stays submission.py.

## Next (per user directive: implement top-1/top-2 strategy based on these results)
- STRATEGY_TOPS.md (produced by background analysis of cjlcjlcjl live-meta kernel +
  existing HS/SEB reverse engineering) defines the top farms' actual mechanisms.
- New cycles (H10+) implement ONE mechanism each from that map, gated H2H on the frozen
  family, starting with the highest-EV lever per the doc. The champion file never changes
  except by promotion (rulebook §0.1).
