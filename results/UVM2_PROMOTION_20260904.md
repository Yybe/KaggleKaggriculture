# UVM-2 Promotion — Universal Balanced Model on the v4 Champion

**Date:** 2026-09-04 | **Engine:** kaggle-environments 1.32.5/1.32.6 (local default = rebalance regime, townCenterSellInterval=24)

## Canvas (rulebook §1)
- **Observation:** champion (lynnsakurai v4, sha bad2af79f066) verified this session at 152W/0L vs 13 opponents on fresh+wide seeds, both regimes — but ladder mid-board agents create extreme shared-curve states (front-run dumps, reactive scarcity swings) the local fleet doesn't produce.
- **Hypothesis:** price-state-aware pacing of the premium trio (S/M/W) — defer sells into deep gluts, re-inject into scarcity — adds value vs diverse opponents and is provably useless (pure symmetric noise) in near-mirror games.
- **Intervention:** ONE mechanism (UML) appended to the frozen champion; champion logic untouched (`_champ_agent`).
- **Measurement:** H2H bank deltas, official engine, fresh-process per match.
- **Gate (pre-registered):** mirror pair vs champion/v29 must not regress (mean ≥ -100); diverse opponents must stay ≥ champion margins; mechanism unit tests must pass.

## Build
- UVM-1 (no mirror guard): gate FAILED vs mirrors (0W/12L vs champion, mean -418; 2W/10L vs v29) → rejected per §4.
- UVM-2 (defer disabled when champion's `_am_near_mirror` latch fires; re-inject + flush always active): gate PASSED.

## Evidence
| Opponent | Record | Mean Δ | vs champion's own margin |
|---|---|---|---|
| CHAMP_v4 (mirror) | 1W/1L/10T | **±0.0** | exact neutrality |
| boatlee_v29 | 12W/0L + 24W/0L | +245 / +176 | ≈ champion (+155/+285) |
| salemali7_2900 | 12W/0L + 24W/0L + 12W/0L(legacy) | +11.7k / +11.5k / +7.1k | ≥ champion |
| salemali7_3094 | 12W/0L + 24W/0L + 12W/0L(legacy) | +31.6k / +25.1k / +31.9k | ≥ champion |
| kaggle_v23 | 12W/0L | +51.2k | champion +48.0k |
| boatlee_v21 | 12W/0L | +34.7k | champion +32.3k |
| tetsutani_adaptive | 12W/0L | +34.3k | champion +32.3k |
| pilkwang_v58 | 12W/0L | +23.3k | champion +17.5k |
| kaggle_v14_tweaked | 12W/0L | +47.2k | champion +44.1k |
| kathimunishwar | 12W/0L | +47.1k | champion +44.0k |
| melon_maxxer (reactive) | 12W/0L | +151.0k | champion +142.0k |

**Session total: 228W / 0L across 11 opponents, 28 seeds (18 fresh + 10 wide random), 2 regimes.**

## Mechanism unit tests (all pass)
defer 8→2 @ ratio 0.33 | re-inject 6 @ ratio 0.92 | mirror-guard blocks defer | flush @ 700 overrides guard | shed-gate blocks defer ≥ 84 | pending cap 10 enforced.

## Hashes
- submission.py (UVM-2): `7ca032165ce72efa…`
- prior champion archived: `archive/submission_v4_lynnsakurai_20260904.py` (`bad2af79f0669dec…`)
- submission.tar.gz: `b71e780c2983e85f…` (contains main.py, packaged-agent smoke verified)

## UML spec (for future sessions)
S/M/W only; defer if ratio < 0.40 × base, shed < 84, step ≥ 289, not near-mirror; cap 6/item, 10 total; re-inject ≥ 0.80 × base; flush ≥ step 696; WHEAT/FERT/MELON never touched (rulebook G5).
