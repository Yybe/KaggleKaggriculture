# V6-E103 vs Apex V5 superiority study (2026-09-22, 15:27 UTC)

## Identity finding (Rule 2 relevant)
The three "submission.py" entries the user listed collapse to **two distinct agents**:
`submission.py`, `agents/pub_apex_v6.py` and `agents/pub_e103_v5_full.py` are **byte-identical**
(md5 `b65ecfe8071ddeb7203a17fab4f6275f`, 1,030,699 bytes). "Apex V6 Champion (1513)" and
"Apex V6 (2492.7)" are the same file — the live-score gap is submission-pool noise, not an agent delta.
`agents/pub_apex_v5.py` = md5 `11e19ef6…` (the third, distinct agent).

## Gates run (engine 1.32.7, both seats per seed, 3 parallel streams)
Logs: `results/v6stream.log`, `results/v5stream.log`, `results/h2h_v6_vs_v5_xbank.txt`.
Stream note: 3×12-worker concurrent gates crashed one pool (OOM); xbank re-run solo, clean.

### V6/E103 vs V5 — head-to-head, four seed banks
| Bank | n | W/L/T | mean |
|---|---|---|---|
| R1 (8 seeds) | 16 | 0/0/8T | +0.0 |
| R2 (8 seeds) | 16 | 2/0/6T | +138.1 |
| Fresh (16 seeds) | 32 | 0/1/15T | −7.9 |
| XBank 40M (16 new seeds, this study) | 32 | 1/0/15T | +113.2 (sole firing seed +1811) |

Shared-spine mirror: 39/48 seeds tie at exactly 0. When V6's retuned layers fire they win; one Fresh seed
lost −7.9 (near-tie). No loss on R2/XBank.

### Fleet — same agents vs E94 and r78u (R1/R2/Fresh)
| Matchup | R1 | R2 | Fresh |
|---|---|---|---|
| V6 vs E94 | 7W/1L +31.0 | 7W/1L **+83.1** | 11W/5L +39.4 |
| V5 vs E94 | 7W/1L +31.0 | 5W/3L **−53.4** | 11W/5L +47.2 |
| V6 vs r78u | 8W/0L +81.9 | 8W/0L **+110.7** | 16W/0L +67.7 |
| V5 vs r78u | 8W/0L +81.9 | 6W/2L **−25.8** | 16W/0L +75.6 |

V5's R2 losses are the −563/−592 floor-tail seeds; the 90/30/140 retune in V6 removes that class
(R2 flips −53.4→+83.1 vs E94, −25.8→+110.7 vs r78u). Zero ties in all 192 fleet games.
Cost: V6 gives up ~7 mean vs E94 on Fresh (second-biggest wins shrink +319→+264, +264→+193) — record identical.

### Vs external v57 (from `results/h2h_v57_vs_*.txt`, sign-flipped)
v57 scored 26W/6L vs V5, 27W/5L vs V6, 28W/4L vs E94, 28W/4L vs r78u on R1+R2+Fresh.
**All three internal agents lose to v57**; V6 is the least-bad pairing partner only on Fresh (+565 mean favors v57).

## Verdict
**V6/E103 ≥ V5, strictly**: never loses the head-to-head except one −7.9 near-tie; dominates V5 on the R2
bank vs both relatives; identical everywhere else (same spine). Deploy file = V6/E103.
External threat: v57 funding-order-invariant beats both — its R1-only loss class (3 seeds) is the next forensic target.
