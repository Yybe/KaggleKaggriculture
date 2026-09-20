#!/bin/bash
# Detached new-meta (2026-09-19/20) gate sweep vs our live base.
# Resumable: skips any challenger whose result file already has a summary.
# Every gate: engine_assert first (must PASS, else abort the whole sweep), then
# base-as-A x 8 seeds x 2 seats, interval 24 (hinge config).
cd "$(dirname "$0")/.."
SEEDS="1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000"
PY=WybeV2/rank_env/Scripts/python.exe
BASE=agents/pub_2945farm.py
LOG=results/newmeta_sweep.log
: > "$LOG"
export PYTHONIOENCODING=utf-8

if ! "$PY" tools/engine_assert.py > results/newmeta_engine_assert.txt 2>&1; then
  echo "ENGINE ASSERT FAILED - REFUSING TO GATE" >> "$LOG"
  cat results/newmeta_engine_assert.txt >> "$LOG"
  exit 1
fi
echo "=== engine asserted ===" >> "$LOG"
grep ENGINE_ASSERT results/newmeta_engine_assert.txt >> "$LOG"

for s in 2950peak metav4 guru_v4 v50yarn melon2749 day6herd; do
  out=results/newmeta_${s}_gate8.txt
  if grep -q "Mean Delta" "$out" 2>/dev/null; then echo "=== $s SKIP(done)" >> "$LOG"; continue; fi
  if [ ! -f "agents/pub_${s}.py" ]; then echo "=== $s SKIP(missing)" >> "$LOG"; continue; fi
  echo "=== $s START $(date +%H:%M:%S)" >> "$LOG"
  "$PY" tools/diag_bench_seeds.py "$BASE" "agents/pub_${s}.py" "$SEEDS" "$out" --interval 24 >> "${out}.log" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then echo "=== $s RUNFAIL rc=$rc" >> "$LOG"; continue; fi
  { grep ENGINE_ASSERT results/newmeta_engine_assert.txt; cat "$out"; } > "${out}.tmp" && mv "${out}.tmp" "$out"
  rm -f "${out}.log"
  grep -E "Mean Delta|seed-level" "$out" >> "$LOG"
  echo "=== $s END $(date +%H:%M:%S)" >> "$LOG"
done
echo DONE >> "$LOG"
