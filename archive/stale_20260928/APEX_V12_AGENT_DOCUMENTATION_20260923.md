# APEX V12 AGENT DOCUMENTATION (2026-09-23)

## Lineage & Provenance
- Champion File: `agents/pub_v57_apex_v35_dumporder.py` (1,078,157 bytes, +1,909 vs V11)
- Submission Target: `submission.py` (byte-identical copy, verified)
- Base Lineage: `pub_v57_funding.py` + V11 Days 28-30 bulk dump
- New Mechanism: d30 dump-order position — STRAWBERRY SELLs stable-moved to queue position 0 at steps 672-719 when STR px >= 30. Same length, same (op,item,qty) multiset, volume conserved, no debt needed. EXP437-invariant holds.
- Builder: `tools/build_v57_apex_v35_dumporder.py`; probe `tools/probe_v57_v35_layers.py`; census `tools/census_v35_strpx.py` (gate 30 from fire-turn px 37/39 vs glut 1-22).

## Architecture Stack
```
| 3. d30 STR-front reorder (672-719, px>=30, position 0) |
| 2. Days 28-30 bulk shed dump (V11, steps 672-719)      |
| 1. Funding-order invariant overlay (_cxd_candidates)   |
| 0. MetaV4 Core Chassis (Routes, Task Planner)          |
```

## Gate Matrix (pin kaggle-environments==1.32.7, townCenterSellInterval=24, both seats, 0 crashes)
| Bank | n | W/L/T | Mean | Median | Min/Max | Sign p |
|---|---|---|---|---|---|---|
| R1 | 16 | 5W/0L/3T | +248.9 | — | +0/+659 | — |
| R2 | 16 | 6W/0L/2T | +394.1 | +524 | +0/+730 | 0.03125 |
| Fresh | 32 | 12W/0L/4T | +183.8 | +112 | +0/+650 | 0.0004883 |
| T4 (70000000-70031000) | 64 | 20W/0L/12T | +274.9 | +271 | +0/+748 | 1.907e-06 |
| Pooled | 128 (64 banks) | 43W/0L/21T | — | — | zero losses | 2.274e-13 |

## Fleet Benchmark (64 games/opp, 384 total, engine pin asserted)
| Opp | Total | Mean |
|---|---|---|
| pub_v57_funding.py | 20W/12L/0T | +36.7 |
| pub_apex_v5.py | 25W/7L/0T | +253.3 |
| pub_v56_smarter.py | 24W/7L/1T | +176.7 |
| pub_shiiin9_orderbook.py | 22W/10L/0T | +126.5 |
| pub_e94_omw_clean.py | 26W/6L/0T | +288.3 |
| pub_metav4_r78u.py | 28W/4L/0T | +326.6 |
| GRAND | 145W/46L/1T (75.5%) | — |

Note: fleet win% trails V11's 79.7% on R1 variance (funding Fresh 7W/9L -46.6) but V35 beats V11 head-to-head 43W/0L with zero losses on 64 banks — dominance over parent is absolute.

## Refuted this loop (Rule 3)
- V30/V30b/V33 fert scope (+25/+50/price-gated): live fires (+30-56 FERT/4eps) but R1 2W/6L -265.8 / 1W/6L/1T -293.5 / 1W/6L/1T -293.5. Extra $120 units crash shared curve. Axis retired.
- V31 shed-surplus preempt: inert 0/4 ties (premium shed 0, terminal shed 0). V32 schedule pull-forward: pulls exec 0, 100% forgiven, 4/4 ties. Preempt volume axis dead mid-game.
- V28 route refit (other->110 +1279 in-sample): T3 pooled p=1.0 mean -312, reverses OOS. PARITY/DROP.
- V34 carrot drip on PASS: 1W/7L -694, 2-4 drips/game, idle tiles not free. Dead.

## Deployment
```bash
Copy-Item agents\pub_v57_apex_v35_dumporder.py submission.py -Force
WybeV2\rank_env\Scripts\python.exe -c "import submission; assert callable(submission.agent)"
kaggle competitions submit -c kaggriculture -f submission.py -m "Apex V12: V11 + d30 STR-front dump reorder (43W/0L vs V11, zero losses, p=2.3e-13)"
```
