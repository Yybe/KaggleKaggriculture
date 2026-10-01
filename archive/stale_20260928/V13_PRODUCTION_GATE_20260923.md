# V13 PRODUCTION-AXIS GATE FINDINGS — 2026-09-23

Engine pin: kaggle-environments 1.32.7, townCenterSellInterval=24, interpreter `WybeV2/rank_env/Scripts/python.exe` (asserted inside probe + gate).
Probe: `tools/probe_v13_layers.py` -> `results/v13_probe.log`. Gate: `tools/gate_v12_family_0923.py agents/pub_v57_apex_v13_labor.py` -> `results/v12/gate_family_0923.log` (run 05:02). Census: `tools/census_v13_fertmax_blocked.py`.

Parent for both grafts: `agents/pub_v57_apex_v11_dump.py` (champion, untouched).

## V13-F  agents/pub_v57_apex_v13_fertmax.py  — VERDICT: DROP (fails probe step B, never gated)

- Liveness A: PASSED — TELE `fert_injected` = 2–6 per episode (30 summed over 8 episodes), `errors`=0. Not inert, but ~4 fires/game vs the 240 episode cap.
- Volume B: FAILED. Emitted FERTILIZE cand 948 vs V11-in-same-world 924 over 8 episodes (+24 total = +3/game, +0.6%). Spine baseline 109–123/game; champion band 135–249. The graft does not move the production axis.
- Per-episode margins vs V11 (same world, both seats): +24 +24 −74 −74 +35 +35 +27 +27, mean +3.0. Would gate as ~all-ties/near-ties.
- ROOT CAUSE (census, seed 1000000, free tier only — travel-pause tier is disabled by design, `_V13F_PAUSE_MAX=0`):
  957 zero-cost (PASS / engine-dropped WATER) unit-turns, 797 standing on a PLANT, 52 fully tile-eligible,
  **45/52 blocked by `carried == 0`**, 3 blocked by ROI gate, only 4 fire.
  The binding constraint is fertilizer LOGISTICS (units don't hold fertilizer on their idle turns), not
  wasted-turn availability. Substituting onto idle turns cannot scale without a pick-up/delivery loop,
  which is a different (multi-action) mechanism and violates this graft's zero-cost invariant.
- The pause tier shows 392 would-fires but was measured (build docstring) to cost 4 real WATERs/seed; kept disabled.

## V13-L  agents/pub_v57_apex_v13_labor.py  — VERDICT: DROP (gated, R1 fail)

- Liveness A: PASSED — TELE `hire_injected` = 6/episode (episode cap hit exactly), `errors`=0.
- Volume B: PASSED — emitted HIRE cand 2214 vs V11 2166 (+48 = 6/game, 266→272 hires).
- Probe margins (both seats × 4 seeds): −720 −720 −1042 −1042 −720 −720 −665 −665, mean −786.8. Uniformly negative on every seed, both seats — hires cost fib wage + hand-feed overhead and the extra late hands do not water enough urgent tiles to pay for themselves. (Matches top-10 DNA note "hires NOT a lever".)
- Gate R1 vs V11 (8 seeds, both seats): **0W/8L/0T mean −815.9** → DROP. Screen aborted before R2/Fresh/fleet per harness rule (mean<=0). Ties: 0 (no Rule 2 defect; the graft moves the world, in the wrong direction).

## Ledger entry (Rule 3)

PRODUCTION axis, both constructions now tested and refuted:
1. fertmax = zero-cost FERTILIZE substitution on idle/dropped-WATER turns, ROI-gated, cap 240 — limited to ~4/game because the fertilizer never leaves the shed into unit inventories on those turns. A future attempt must differ materially: a fertilize *supply chain* (scheduled PICKUP + haul + tour) on the labor budget, not turn substitution.
2. labor = late-window (days 14–26, hours 8–15) +1 hand/day when ≥6 urgent unwatered tiles reachable from shed within 5 steps and zero native idle capacity, self-commanded extra hands water nearest urgent tile, cap 6 hires — deterministic −816/seed. The "watering backlog" premise under-counted wage+opportunity cost; do not re-run this construction.
Market axis remains CLOSED per f90/T3. Production axis per these two constructions: no live lever found on turn-substitution or marginal-hire extensions of V11.
