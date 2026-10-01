# V57 "funding-order invariant" — external kernel H2H study (2026-09-22)

## Provenance
- Kernel: `ahmedberatozer/kaggriculture-v57-funding-order-invariant` → notebook pulled to repo root.
- Agent extracted from the cell-2 base85+zlib blob (`SOURCE_BLOB`) to `agents/pub_v57_funding.py`,
  1,067,076 bytes, SHA-256 `2ee689fdc58f38b7bf6b80b8d3f48129d19b47201dbee51fdcbd977498a5106f`
  (matches the kernel's own `EXPECTED_MAIN_SHA256`; module imports clean, entry `agent` callable).
- Self-described mechanism: V56 policy + fix that rejects same-turn order permutations which moved
  HIRE/BUY_SEED/BUY_ANIMAL/BUY_LAND earlier than the parent slot before funding cash arrived.
- Engine: `kaggle-environments==1.32.7` (asserted in the `WybeV2/rank_env` interpreter running the gates).

## Gates — `tools/run_h2h.py agents/pub_v57_funding.py OBS all`
R1 = 8 seeds, R2 = 8 seeds, Fresh = 16 seeds, both seats per seed. Logs: `results/h2h_v57_vs_*.txt`.

| Opponent | R1 (n=16) | R2 (n=16) | Fresh (n=32) | Total W/L/T | Mean per game |
|---|---|---|---|---|---|
| `pub_apex_v5.py` | 5W/3L/0T −468.8 | 7W/1L/0T +453.6 | 14W/2L/0T +557.1 | 26W/6L/0T | +247.8 |
| `pub_apex_v6.py` | 5W/3L/0T −468.8 | 7W/1L/0T +400.8 | 15W/1L/0T +565.0 | 27W/5L/0T | +242.5 |
| `pub_e94_omw_clean.py` | 5W/3L/0T −425.4 | 8W/0L/0T +393.3 | 15W/1L/0T +605.6 | 28W/4L/0T | +258.7 |
| `pub_metav4_r78u.py` | 5W/3L/0T −393.9 | 8W/0L/0T +433.0 | 15W/1L/0T +631.2 | 28W/4L/0T | +265.3 |

Zero ties in all 256 games — v57 is a foreign spine, no shared-spine symmetry defect.

## Loss-first reading
- The only loss class is **R1**: v57 goes 5W/3L with mean −394..−469 on the R1 bank against all four
  opponents (same three losing seeds every time — R1 seeds 1000000/2000000-class, deltas −2508/−1735/−869
  worst case vs V5). Outside R1 it is uniformly positive: 14–15W on Fresh, 7–8W on R2.
- Per-seed tails vs V5: R1 `−2508, −1735, −869, +82…+593`; R2 single loss `−514`; Fresh losses `−52, −33`
  (fresh vs V5: two near-ties). vs V6 Fresh: 1 loss. vs E94/r78u: R2 swept 8W/0L.
- v57 beats apex V5 on R2 (+453.6) where E103's floor-retune advantage lives, but loses R1 — its edge is
  market/order-book timing on late banks, not early expansion, and the R1 deficit is systematic (same seeds),
  i.e. a deterministic bad world class, not variance.

## Status
Not adopted. Champion remains `pub_apex_v5.py` (with E103 retune pending). Useful as a sparring opponent:
its R1 loss class targets the same early-game band where our recent candidates regressed.
