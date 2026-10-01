# ENGINE SHIFT 1.32.6 -> 1.32.7 — found 2026-09-19 21:40 (local)

Evidence [F]: 4 newest top public kernels (`_fresh_top/_clean/*`) hard-assert
`REQUIRED_ENGINE = "1.32.7"`. Local rank_env upgraded to 1.32.7. Full diff vs
1.32.6 copy (results/_pkg/1326/...) = 29 changed lines, ONE mechanism:
**new price shape "hinge"** in MARKET_PARAMS below-side for CARROT, TOMATO, EGG.

- `_shape("hinge", x, T)`: `u=x/T; u + 8.0*max(0,u-1)^2` — calm linear until
  scarcity gap exceeds T, then quadratic spike (HINGE_GAIN=8).
- CARROT below: `log,0.20` -> `hinge,1.00` (T=450, base 35)
- TOMATO below: `linear,0.40` -> `hinge,0.40` (T=200, base 60)
- EGG below: `linear,0.40` -> `hinge,0.40` (T=332, base 50)
- MILK/WOOL/STR/MELON/WHEAT/FERT unchanged.

Consequences:
1. All gates run on 1.32.6 since the 1.32.7 rollout are stale — explains
   "local H2H wins do not transfer live" (H17) and live collapse of v33/v34
   (1582/1618) vs Aug-era 2994 class scores.
2. Carrot/tomato/egg SCARCITY now pays huge (px explodes past the knee);
   volume-glut strategies are punished less asymmetrically. Matches live loss
   signature: "carrot px 326→695 in scarcity games, opp carrot season 88-93
   vs ours 14" (V35_V36_LEDGER).
3. guruprasaathas v219 4-quadrant overlay (BUY SE + 10 tomato at px>=70 when
   rich) is EXACTLY built for the hinge — public proof-of-concept.

Re-runs on 1.32.7:
- results/e1327_7turn_vs_v34_gate8.txt (sanity, incumbent ordering)
- results/e1327_7turn_vs_guruV2_gate8.txt (public 4Q overlay vs our base)
