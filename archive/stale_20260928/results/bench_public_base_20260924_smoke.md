# bench_public_base_20260924 — usage + smoke report (2026-09-24)

Runner: `tools/bench_public_base_20260924.py` (new file; no existing harness touched).
Engine pin: kaggle_environments==1.32.7, townCenterSellInterval=24 (aborts otherwise).
Semantics: fresh process per game (`max_tasks_per_child=1`) + unique module name
per load; entry = LAST module-level callable (Kaggle semantics, entry name logged
per game); both seats per seed, verdict on seat-averaged delta.

## Usage

```powershell
# single pair, one bank
WybeV2\rank_env\Scripts\python.exe tools/bench_public_base_20260924.py `
  --cand submission.py --opp agents/pub_apex_v5.py --bank r1 `
  --out results/bench_public_base_20260924.jsonl
# banks: r1 | r2 | fresh | t4 | all ; T4 = range(50000000,50016000,1000),
# asserted disjoint from R1/R2/FRESH/T3(range 40000000..)
# explicit seeds override bank: --seeds 1000000,2000000
# multiple files: repeat --cand/--opp or comma-separate; --tie-band N (default 0)
# C++/tar/non-py inputs -> skipped-unloadable rows (never losses);
# missing files -> REJECT exit 2 with reason
```

Output: per-seed JSONL rows (`seed`: cand_avg/opp_avg/delta/verdict/tie_band/error
+ per-seat games) + `summary` rows (W/L/T/mean/min/max/tie_band/errors) + stdout
report; every report prints ENGINE/CONFIG/HASH headers.

## Smoke (2026-09-24, 1 seed x 2 seats, --workers 2)

`--cand submission.py --opp agents/pub_apex_v5.py --seeds 1000000` ->
`results/bench_public_base_20260924_smoke.jsonl`:
submission.py vs pub_apex_v5.py: **1W/0L/0T err=0 mean=+357.0** (81965.0 vs 81608.0, 11.5s).
Reject probe: `--cand agents/no_such_file_xyz.py` -> `REJECT missing candidate ...
-- file does not exist`, exit 2, no games run. Full fleet NOT run; no promotion.
