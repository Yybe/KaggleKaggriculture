# APEX V11 AGENT DOCUMENTATION (2026-09-23)

## Lineage & Provenance
- Champion File: [`agents/pub_v57_apex_v11_dump.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/agents/pub_v57_apex_v11_dump.py) (1,076,248 bytes)
- Submission Target: [`submission.py`](file:///c:/Users/xxshi/Desktop/farmmasterV2/submission.py)
- Base Lineage: `pub_v57_funding.py` (cell-2 base85+zlib extraction, funding-order invariant overlay)
- New Mechanism: Days 28-30 Bulk Shed Inventory Liquidation & Cargo Sweep (`_v57_apex_v11_dump_agent`)

## Architecture Stack
```
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Days 28..30 Endgame Bulk Cargo Dump (Steps 672..719)                │
│    Liquidates 100% of remaining shed inventory on every turn.         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Funding-Order Invariant Overlay (_cxd_candidates filter)            │
│    Prevents permutation of HIRE/BUY_SEED/BUY_LAND before cash arrival.│
├────────────────────────────────────────────────────────────────────────┤
│ 0. MetaV4 Core Chassis (Routes, Task Planner, Unit Model)              │
└────────────────────────────────────────────────────────────────────────┘
```

## Fleet Benchmark Matrix (Pinned Environment `kaggle-environments==1.32.7`, `townCenterSellInterval=24`)

| Opponent Lineage | R1 Bank (n=16) | R2 Bank (n=16) | Fresh Bank (n=32) | Total W/L/T | Mean Delta per Game | Win Rate % |
|---|---|---|---|---|---|---|
| `pub_v57_funding.py` | 7W / 1L / 0T | 6W / 2L / 0T | 9W / 7L / 0T | **22W / 10L / 0T** | **+63.5** | **68.8%** |
| `pub_apex_v5.py` | 5W / 3L / 0T | 7W / 1L / 0T | 14W / 2L / 0T | **26W / 6L / 0T** | **+277.9** | **81.3%** |
| `pub_v56_smarter.py` | 7W / 1L / 0T | 7W / 1L / 0T | 14W / 2L / 0T | **28W / 4L / 0T** | **+201.0** | **87.5%** |
| `pub_shiiin9_orderbook.py` | 6W / 2L / 0T | 6W / 2L / 0T | 10W / 6L / 0T | **22W / 10L / 0T** | **+146.6** | **68.8%** |
| `pub_e94_omw_clean.py` | 5W / 3L / 0T | 7W / 1L / 0T | 15W / 1L / 0T | **27W / 5L / 0T** | **+313.0** | **84.4%** |
| `pub_metav4_r78u.py` | 6W / 2L / 0T | 7W / 1L / 0T | 15W / 1L / 0T | **28W / 4L / 0T** | **+352.7** | **87.5%** |
| **GRAND TOTAL FLEET** | | | | **153W / 39L / 0T** | **+225.8** | **79.7%** |

## Deployment Command
```bash
kaggle competitions submit -c kaggriculture -f submission.py -m "Apex V11: v57 funding-order invariant base + Days 28-30 bulk cargo dump & terminal sweep (79.7% fleet win rate, 153W/39L)"
```
