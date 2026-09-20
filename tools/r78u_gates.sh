#!/bash
# R78U gate battery — resumable (skip on existing output). Run detached:
#   nohup bash tools/r78u_gates.sh > results/r78u_gates.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
PY="WybeV2/rank_env/Scripts/python.exe"
RU=agents/pub_metav4_r78u.py
CM=agents/pub_metav4_early.py
H2=agents/crop_roi30_h20.py
PANEL="1000001,1000041,1000003,1000075,1000004,1000032,1000078,1000088,1000028,1000050,1000014,1000036,1000020,1000065,1000024,1000076"
GATE8="1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000"

run() { # out a b label seeds
  [ -f "results/$1" ] && { echo "SKIP $1"; return; }
  echo "START $1 $4 $(date +%T)"
  "$PY" tools/diag_bench_seeds.py "$2" "$3" "$5" "results/$1" --interval 24 > "results/$1" 2>&1
  echo "DONE $1 $(date +%T)"
}

# isolate the gate: r78u vs its actual base h20
run r78u_vs_h20_gate8.txt   "$RU" "$H2" "gate"  "$GATE8"
run r78u_vs_h20_panel16.txt "$RU" "$H2" "panel" "$PANEL"
# champion-swap decision: r78u vs local champ (also carries the h20 fert-ROI delta)
run r78u_vs_champ_gate8.txt   "$RU" "$CM" "gate"  "$GATE8"
run r78u_vs_champ_panel16.txt "$RU" "$CM" "panel" "$PANEL"
# control for the inherited h20-champ delta
run h20_vs_champ_gate8.txt "$H2" "$CM" "ctrl" "$GATE8"
# fleet (champion fleetctrls already exist as results/t20b_fleetctrl_*.txt)
for F in agents/pub_demand_timing.py agents/pub_metav4.py agents/_top_pub/lynnsakurai_v3.py \
         agents/live_replay/opp_涵哥_29ee77a6.py agents/live_replay/opp_kwa_67f80680.py \
         agents/live_replay/opp_THIRD_FARM_CLUB_f5afac52.py agents/live_replay/opp_tamura_aicon_d45969a0.py \
         agents/live_replay/opp_Yanis_Belami_03d5c442.py; do
  N=$(basename "$F" .py)
  run r78u_fleet_${N}.txt "$RU" "$F" "fleet" "$GATE8"
done
echo "BATTERY COMPLETE $(date +%T)"
