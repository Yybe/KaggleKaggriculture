#!/bin/bash
# Detached, resumable confirmation sweep for the metav4 incumbent:
#   (1) composite gate: pub_metav4.py (A) vs pub_metav4_early.py (B), 8 seeds x 2 seats
#   (2) fleet gate:     pub_metav4.py (A) vs each of 4 recent-meta opponents, same seeds
# Pattern copied from tools/newmeta_sweep.sh: engine_assert must PASS before any gate,
# every result file gets the ENGINE_ASSERT block prepended, DONE marker at the end.
# Re-running skips gates whose output already contains "Mean Delta".
cd "$(dirname "$0")/.."
SEEDS="1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000"
PY=WybeV2/rank_env/Scripts/python.exe
BASE=agents/pub_metav4.py
LOG=results/metav4_early_sweep.log
EA=results/metav4_early_engine_assert.txt
: > "$LOG"
export PYTHONIOENCODING=utf-8

if ! "$PY" tools/engine_assert.py > "$EA" 2>&1; then
  echo "ENGINE ASSERT FAILED - REFUSING TO GATE $(date +%H:%M:%S)" >> "$LOG"
  cat "$EA" >> "$LOG"
  exit 1
fi
echo "=== engine asserted $(date +%H:%M:%S) ===" >> "$LOG"
grep ENGINE_ASSERT "$EA" | tail -1 >> "$LOG"

run_gate () {          # $1 = B agent path, $2 = out file, $3 = label
  local b="$1" out="$2" label="$3"
  if grep -q "Mean Delta" "$out" 2>/dev/null; then echo "=== $label SKIP(done)" >> "$LOG"; return 0; fi
  if [ ! -f "$b" ]; then echo "=== $label SKIP(missing $b)" >> "$LOG"; return 0; fi
  echo "=== $label START $(date +%H:%M:%S)" >> "$LOG"
  "$PY" tools/diag_bench_seeds.py "$BASE" "$b" "$SEEDS" "$out" --interval 24 >> "${out}.log" 2>&1
  local rc=$?
  if [ $rc -ne 0 ]; then echo "=== $label RUNFAIL rc=$rc $(date +%H:%M:%S)" >> "$LOG"; return 0; fi
  { grep ENGINE_ASSERT "$EA"; cat "$out"; } > "${out}.tmp" && mv "${out}.tmp" "$out"
  rm -f "${out}.log"
  grep -E "Mean Delta|seed-level|Errs:" "$out" >> "$LOG"
  echo "=== $label END $(date +%H:%M:%S)" >> "$LOG"
}

run_gate agents/pub_metav4_early.py results/metav4_early_composite_gate8.txt composite_early

for s in demand_timing salem_2900 moryield v48queue; do
  run_gate "agents/pub_${s}.py" "results/fleetmetav4_${s}_gate8.txt" "fleet_${s}"
done

# final integrity check: incumbent sources must be untouched
md5sum agents/pub_metav4.py agents/pub_2945farm.py >> "$LOG" 2>&1
echo DONE >> "$LOG"
