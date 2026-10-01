# LEAN_WFLIP_V9 Agent Documentation (2026-09-30)

## Lineage
- Base: `lean_s336.py`
- Promoted Candidate: `agents/lean_wflip_v9_standalone.py` -> `submission.py`

## Architecture Stack Table
| Layer | Description | Mechanism |
|---|---|---|
| Base Spine | `lean_s336.py` | 360-step lean production spine |
| CXTB Graft | `_CXTB_MIN_REVENUE` 9000 -> 8000 | Lowers revenue threshold for earlier tomato lane opening |
| WHEAT-Flip Graft | Step 216, 264, 433 WHEAT buy | Forces 1 WHEAT seed purchase when inventory count is 0 to desynchronize opponent sell curve |

## Benchmark Matrix vs `lean_s336.py`
Engine: `kaggle-environments==1.32.7`, `townCenterSellInterval=24`

| Bank | Games | Record (W/L/T) | Win Rate | Mean Delta |
|---|---|---|---|---|
| R1 | 16 | 8W / 0L / 0T | 100.0% | +444.6 |
| R2 | 16 | 7W / 0L / 1T | 87.5% | +12.1 |
| Fresh | 32 | 14W / 2L / 0T | 87.5% | +121.9 |
| **Total** | **64** | **29W / 2L / 1T** | **90.6%** | **+175.2** |

## Deployment Record
- `submission.py`: Updated with standalone lean_wflip_v9 (SHA-256 `6EC5E6A5AF4267303F2B4BCD972EAF886B8D91311F70F38C4472F36E9087A6EC`).
- `agents/lean_wflip_v9_standalone.py`: Saved as benchmark archive.
- `lean_s336.py`: Untouched, verified byte-exact (SHA-256 `BAD988901CAD5185D7AF87844771533FE1D047FEACE50B708ABDB6AC13CE387A`).
