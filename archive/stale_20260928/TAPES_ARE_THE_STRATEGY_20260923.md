# The tapes are the strategy — measured 2026-09-23

Read-only measurement on the deployed champion `agents/pub_v57_apex_v11_dump.py`. Nothing here is a
candidate; it is the explanation for why fifteen candidates could not beat it by more than a rounding error.

## 1. The Days 28-30 bulk dump is inside the public action tapes

Introspecting `_ROUTES` (41 route ids, tape length 719, 38 distinct byte-signatures):

| Route | bulk `SELL` orders with qty ≥ 100 | of which in steps 648-719 | step range | items |
|---|---|---|---|---|
| 105 | 87 | **87 (100%)** | 670-719 | CARROT 18, WHEAT 18, FERTILIZER 10, MILK 8, EGG 8, WOOL 7, TOMATO 6, MELON 6, STRAWBERRY 5 |
| 9 | 87 | **87 (100%)** | 670-719 | identical block |

Every tape already emits the full end-of-season liquidation. The V11 graft is coverage for the cases
where the tape's fixed order sizes miss the residual shed, not the invention of the dump.

## 2. That puts a hard ceiling on what an overlay can be worth

| Comparison | Record | Mean delta | Typical game money | Relative |
|---|---|---|---|---|
| V11 vs its own parent `pub_v57_funding.py` | 22W/10L/0T | +63.5 | ~100,000 | **+0.06%** |
| V11 vs `pub_apex_v5.py` | 26W/6L | +277.9 | ~100,000 | +0.28% |
| V11 vs `pub_metav4_r78u.py` | 28W/4L | +352.7 | ~100,000 | +0.35% |
| f90 vs V11, T3 holdout (32 fresh seeds) | 15W/15L/2T | +87.7, sign p = 1.00 | ~100,000 | +0.09%, **not significant** |

Fifteen distinct graft constructions (V12-V26) all landed inside that same ±0.35% band, and the two that
looked like wins (f90, V25) collapsed on a never-used seed bank. That is not bad luck — it is the
expected magnitude of a post-hoc overlay on an agent that is already replaying a champion-authored tape.

## 3. Consequence: the lever is tape *selection*, not tape *decoration*

`_router` (spine `:961-980`) maps the day-6 shop draw to one of 41 tapes through lookup tables fitted by
other authors (`_R108_SHOP_ROUTES` n=64, `_R110_OLD_SHOPS` n=64, `_V92_TABLE` n=15, `_V93_ROUTE_BY_RIVAL`
n=1) on their own chassis. Measured coverage over the 8-store shop universe (64 ordered pairs):

- **All 15 YARN-containing pairs collapse onto route 9** (one tape, via `_V92_TABLE`, which overrides
  whatever `_R110_OLD_SHOPS` said).
- **21 of the 49 non-YARN pairs (43%) collapse onto route 105.**
- Only **20 of 41 tapes are selectable at all**; 21 are dead weight: 0-8, 10-12, 100, 109, 114, 115, 119,
  125-128.
- Two tapes carry different mid-game market loads: route 105 has 703 SELL/BUY orders in steps 144-648,
  route 9 has 548, route 103 has 877. So the choice moves mid-game production economics by ~20-40%,
  whereas the overlay band above is ±0.3%.
- The step ≥648 `route = 2` override is **functionally inert**: the unit-task block for steps 648-719 is
  byte-identical across all 41 tapes, and the market block is identical except for route 1 (which the
  table never selects). Any future candidate that "changes the day-27 route" will therefore produce ties,
  and ties must be read as an untested candidate (AGENTS.md Rule 2), not as safety.

**How to apply:** rank experiments by the magnitude of the structure they touch. Route selection moves
20-40% of the mid-game action volume; sell-timing, shed-guard, land-timing and hire overlays move
0.0-0.35%. The fert axis is logistics-bound (45 `carried==0` blocks per episode against 957 idle
unit-turns, see `V13_PRODUCTION_GATE_20260923.md`), so it is a supply-chain question, not a routing one.

Reproduce:
```bash
WybeV2/rank_env/Scripts/python.exe -c "import importlib.util as u; s=u.spec_from_file_location('v','agents/pub_v57_apex_v11_dump.py'); m=u.module_from_spec(s); s.loader.exec_module(m); print(len(m._ROUTES))"
```
