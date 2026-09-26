#!/bin/bash
# E210: the item-identity preempt cha22_e210_straw_h13q6 (STRAWBERRY at hour 13, qty 6, on top of the
# q8 WHEAT/FERT layer) - official 3-bank gate vs the champion (done, E210_straw_vs_cha22_all.txt),
# then vs its own parent q8 to attribute the increment, then the same 8-opponent ladder E205/E208 ran.
# Sequential by necessity: run_h2h owns a ProcessPoolExecutor, so nothing may overlap.
cd /c/Users/xxshi/Desktop/farmmasterV2 || exit 1
PY=WybeV2/rank_env/Scripts/python.exe
C=agents/cha22_e210_straw_h13q6.py
CHAIN=gates_cha22/E210_chain.txt
: > "$CHAIN"

run() {  # run <opponent> <bank> <tag>
  $PY tools/run_h2h.py "$C" "$1" "$2" > "gates_cha22/E210_${3}_$2.txt" 2>&1
  local rc=$?
  echo "$(date -Is) done $3 $2 exit=$rc" >> "$CHAIN"
}

echo "$(date -Is) E210 ladder start" >> "$CHAIN"
run agents/cha22_e199_lo96q8.py               all    straw_vs_q8parent
run agents/futurev1_forecast.py               r1     vs_futurev1_forecast
run agents/submission_apex_final.py          r1     vs_submission_apex_final
run agents/pub_v57_apex_v35_dumporder.py      r1     vs_pub_v57_apex_v35
run agents/baseline_x1.py                     fresh  vs_baseline_x1
run agents/c22_preempt.py                     fresh  vs_c22_preempt
run agents/crop_r51.py                        fresh  vs_crop_r51
run agents/friend_r78ub.py                    fresh  vs_friend_r78ub
run agents/futurev1_cha22sell_w1.py           fresh  vs_futurev1_cha22sell
echo ALLDONE >> "$CHAIN"
