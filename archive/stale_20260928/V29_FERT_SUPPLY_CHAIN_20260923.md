# V29 — FERTILIZER SUPPLY CHAIN on APEX V11: the axis is CLOSED (2026-09-23)

Engine pin `kaggle-environments 1.32.7`, `townCenterSellInterval=24`, `episodeSteps=720`,
interpreter `WybeV2/rank_env/Scripts/python.exe` (asserted and echoed in every log below).
Parent `agents/pub_v57_apex_v11_dump.py` (champion) — **read-only, never edited**.
Regime for all measurements: mirror V11-vs-V11 (the gate regime), R1 seeds
`1000000, 2000000, 3330000, 5000000`, both seats.

Logs / data: `results/v29/s2_census.log`, `results/v29/s2_fert_supply.json`,
`results/v29/s2b_cap_ablation.log`, `results/v29/s2c_crop_headroom.json`.
Probes: `tools/v29_fert_supply_census.py`, `tools/v29_tour_cap_ablation.py`,
`tools/v29_crop_headroom_census.py`.

**VERDICT: CLOSED. No `pub_v57_apex_v29_fertsupply.py` was built, because neither S3
precondition holds.** Fertilizer per game: **114.0 applications before = 114.0 after**
(nothing was changed — the intervention was proven inert before construction).

---

## S1 — the call chain, and what actually caps season fert volume

Fertilizer **enters a unit's hand by exactly one route**: `PICKUP FERTILIZER n`, legal only
while the unit stands on a shed-access tile `(4,4),(5,4),(4,5),(5,5)`. `FERTILIZE` then takes
1 unit from that unit's inventory (`kaggriculture.py:475-481` → `_inv_take(inv,"FERTILIZER",1)`),
so an empty hand is a silent no-op. That is the `carried==0` blocker the V13 census found.

Fert **acquisition** has three sources, all spine-internal:

1. `COLLECT_FERTILIZER` off fed animals (engine `:515-521`, 1 unit/animal/day), placed into the
   shed by the sheep/wheat workers via `PLACE`/`DROP` (`agents/pub_v57_apex_v11_dump.py:4285-4297`).
2. `BUY_PRODUCT FERTILIZER` — emitted at only **two** sites:
   * `_r51_input_control` (EXP182 tour layer) → `:2284`
     `changed['market'] += [['BUY_PRODUCT','FERTILIZER', total_q+topup]] + [['HIRE'] for _ in plans]`,
     with `topup = max(0, native_pickups - available)` at `:2277` — i.e. it buys *only* the
     shortfall against shed stock, just-in-time;
   * `_v219` day-24/27 tomato tour → `:1331`, quantity from `_r70_parent_fert_qty` (`:2455-2474`,
     `max(10, 10+native_need-shed_fert)`, shed-space capped).
3. Nothing else. `_cxd_candidates` / `_cxd_reorder` (`:6786`, `:6798`) order existing orders and
   never originate a fert buy — untouched here.

Fert **leaves as revenue** at `_r85_fertilizer` (`:2602-2614`): every turn of days 6–28 it sells
`held - already_sold - _r85_reserve(...)`, and `_r85_reserve` (`:2575-2601`) floors the retained
stock at `max(14, native_reserve + dedicated)`.

The cap stack on applications, in order of severity as measured:

| # | Locus | Term | Kind |
|---|---|---|---|
| 1 | `:2153` | `_R51_INPUT_CROPS = {'WHEAT':(2,4,6),'CARROT':(2,3,4)}` | **crop whitelist** — the tour's price dict at `:2194` is hard-coded `for p in ('WHEAT','CARROT')`, so the tour can *only* ever fertilize the two cheapest crops ($25/$35 base) |
| 2 | `:2441` | `if value < 1.5*cost + 50 or farm['money'] < total_cost+cost+3000: break` | **ROI threshold** against those cheap crop prices |
| 3 | `:2437` | `if q<3 or len(market)+2+i>10 or sum(stock)+purchases+total_q+q+topup > 95: break` | min-3-tiles per tour + market slot + shed space |
| 4 | `:2256-2262` | `hour not in (1,2,3)` / `not 12<=day<=28` / `day in (12,18)` / headcount purity (`owned != set(range(1,len(hands)+1))`) | tour **window** gates |
| 5 | `:2152` | `_R51_INPUT_MAX_WORKERS = 2` | worker-slot cap — **proven slack, see S2b** |

**Answer to "cash budget, per-day limit, ROI threshold, or queue-slot limit?"** — none of the
first three as posed: it is an **ROI threshold (`:2441`) evaluated against a crop whitelist
(`:2153`) that excludes every crop expensive enough to clear it.** It is *not* a cash budget and
*not* a purchase-volume cap.

## S2 — the supply side measured: there is no shortfall

Per-episode means, 4 seeds × 2 seats (8 episodes), `results/v29/s2_census.log`:

| quantity | mean | range |
|---|---|---|
| fert units **bought** (`BUY_PRODUCT FERTILIZER` emitted) | **83.0** | 60–96 |
| fert units **collected from animals** (`COLLECT_FERTILIZER` ops) | **373.5** | 368–376 |
| fert units **applied** (confirmed `fertilized_until_day` transitions) | **114.0** | 107–122 |
| fert **stranded at step 719** (shed + in-hand) | **0.1** | 0–1 |
| peak shed fert held all season | 19.8 | 17–26 |
| turns with fert present in the shed | 34.8 % of the season | 172–371 / 719 |
| market fert price at season end | **$1.5** | 1–3 (market inv 10484 > I0 10000) |
| idle-turn `carried==0` blocks (V13 funnel reproduced) | 31.2/ep | of which only 19 tile-eligible, **2–3 would-fire** |

Mass balance per episode: supply = 83 bought + 373 collected = **456 units**; sinks = 114 applied
+ **~343 exported for cash** + ~0 stranded. **The chassis is a net fertilizer EXPORTER with ~4×
more fert flowing through the farm than it applies.**

The spine's own telemetry agrees, independently of my balance arithmetic
(`_R51_INPUT_REPORT`, one player per episode, `results/v29/s2b_cap_ablation.log`):

```
input_loaded_units        29.8/ep      input_stock_shortfalls   0.0/ep   <-- never starves
input_purchase_requests   29.8/ep      input_hire_errors        0.0/ep
input_application_requests 28.2/ep     input_errors             0.0/ep
```

`input_stock_shortfalls == 0` while 29.8 units load per episode is the direct refutation: the tours
are **never** denied fertilizer. The mission's premise ("we are under-supplied, not under-timed")
is an artifact of counting `BUY_PRODUCT` alone (83 vs the champions' 170–270) and ignoring
`COLLECT_FERTILIZER` (373 free units/episode). Per S2's own decision rule, the supply axis is
**CLOSED**.

## S2b — the named cap does not bind (with positive control)

`_R51_INPUT_MAX_WORKERS` (`:2152`) raised 2 → 3 → 4 → 6 over 4 R1 seeds:

```
MAX_WORKERS=2   FERTILIZE/ep 115.0  fert bought/ep 83.0  money 77410  deltas: hires 4.5 purch 29.8 appl 28.2
MAX_WORKERS=3   FERTILIZE/ep 115.0  fert bought/ep 83.0  money 77410  identical to the last digit
MAX_WORKERS=4   FERTILIZE/ep 115.0  fert bought/ep 83.0  money 77410  identical
MAX_WORKERS=6   FERTILIZE/ep 115.0  fert bought/ep 83.0  money 77410  identical
```

Byte-identical, so per Rule 5 I proved the knob was live rather than accepting a null:

| control | FERTILIZE/ep(seat0) | fert bought | r51 hires | r51 appl_req | money seed 1e6 | money 2e6 |
|---|---|---|---|---|---|---|
| `MAX_WORKERS=0` | **94 / 71** | 64 / 21 | **0** | **0** | 80291 | 74033 |
| `MAX_WORKERS=2` | 123 / 107 | 96 / 60 | 10 | 62 | 81232 | 75186 |

The patch reaches `_r68_joint_plans` (it is a plain module global, resolved per call), zeroing it
collapses applications by 29–36 and costs **+$941 / +$1,153**. So (a) the tour is *profitable per
application* — its ROI gate is not falsely rejecting; (b) it forms only **4.5 plans per season**,
far below the 2/day the cap allows, so the cap is never reached. The binding term is upstream:
tile eligibility inside the whitelist + the `q<3`/ROI break, not the slot count.

## S2c — where the 271 uncovered tile-days actually are

Day-deduplicated, `tools/v29_crop_headroom_census.py`, 4 episodes (seed 0 seat), coverage = share
of fertilizer-useful tile-days inside an active fert window:

| crop | in tour whitelist? | base $ | useful tile-days | covered | cover % | uncovered |
|---|---|---|---|---|---|---|
| WHEAT | yes | 25 | 1351 | 266 | 19.7 % | 1085 |
| CARROT | yes | 35 | 315 | 115 | 36.5 % | 200 |
| STRAWBERRY | **no** | 120 | 912 | 482 | **52.9 %** | 430 |
| MELON | **no** | 250 | 48 | 0 | 0.0 % | 48 |
| TOMATO | **no** | 60 | 0 | 0 | — | 0 (we plant none) |
| **total** | | | **2626** | **863** | **32.9 %** | **1763** |

`FERTILIZE` ops by the crop the acting unit stood on (mean 115.0/ep): **STRAWBERRY 61.8 (53.7 %)**,
WHEAT 37.5 (32.6 %), CARROT 15.8 (13.7 %), TOMATO 0, MELON 0.

So the majority of applications already go to the $120 crop — and they are delivered by the
**native route tape**, not by the tour layer, which cannot legally touch it. Covering the 107
uncovered strawberry tile-days/episode alone would take applications from 114 → ~221, inside the
champions' 135–249 band, with **zero additional purchases**.

*(Instrumentation caveat: the `win useful` / `win cover%` columns of that probe read 0 because the
tile-day dedupe key fires on the first sighting of a day (hour 0), which is outside the tour's
hour-1..3 window. The crop decomposition above is day-level and unaffected; the window split was
not measured and is not claimed.)*

## S3/S4/S5 — not executed, and why that is the correct outcome

S3 was conditional on S2 showing a real shortfall **or** a loosened cap paying. Both branches are
now closed by direct measurement:

* shortfall: none — 456 units supplied against 114 applied, `input_stock_shortfalls = 0`,
  stranded 0.1 units;
* loosened purchase volume: **guaranteed inert or harmful.** `_r85_reserve` floors retained stock
  at 14 and `_r85_fertilizer` sells everything above it every turn of days 6–28, so bought units
  are exported, not applied; and we already *sell ~343 units/episode*, which is what pushes the
  market fert price to $1.5 — buying 170–270 units into our own glut raises our cost without
  adding one application.
* loosened slot cap: `MAX_WORKERS` provably slack (S2b).

Building and gating `agents/pub_v57_apex_v29_fertsupply.py` against this evidence would produce
exactly the V13-fertmax failure signature — an ~inert graft that gates as a clean tie and reads as
"zero regression" (Rule 2/Rule 5). Stopped before construction, as the mission instructs.
No seeds were consumed on gates; `SEEDS_T6` (`70000000..70031000`) remains **unused and available**.

## Ledger entry (Rule 3)

**Axis: fertilizer SUPPLY / purchase volume, on `pub_v57_apex_v11_dump.py`. CLOSED.**
Construction excluded: runtime `_R51_INPUT_MAX_WORKERS` sweep {0,2,3,4,6} + fert unit-flow census
{bought 83, collected 373, applied 114, exported ~343, stranded 0.1} + crop coverage table,
4 R1 seeds × both seats, mirror regime, engine 1.32.7.

What a *materially different* next attempt must be (not a repeat of anything defeated):

1. **Not** turn substitution (V13-fertmax, +3/game, refuted), **not** hires (V13-labor, 0W/8L −816,
   closed), **not** purchase volume (this note).
2. The live lever is the **tour's crop scope**: `_R51_INPUT_CROPS` (`:2153`) plus the hard-coded
   `prices={p: ... for p in ('WHEAT','CARROT')}` dict at `:2194` and `all_units={'WHEAT':0,'CARROT':0}`
   at `:2432/:2445` exclude STRAWBERRY/MELON, which are the only crops whose price clears the
   `:2441` ROI gate with room to spare. A naive runtime patch of `:2153` **crashes** the layer
   (`KeyError` on `prices['MELON']`), and `_r51_input_control`'s `except` then returns
   `{'farmer':['PASS'],'hands':[],'market':[]}` — a total-action wipe. Any attempt must therefore
   re-bind `_r51_input_forecast` + `_r51_input_path` + `_r68_joint_plans` together in one
   append-only layer, keep the number of `HIRE` orders identical (labor is closed), and re-tune
   the `1.5*cost+50` constant, which becomes *less* binding at $120/$250 crop prices.
   Funding already exists: 343 fert units/episode are sold at $1.5 that could instead be applied.
3. Corollary for the sell side: our own fert dumping is what sets the fert price we buy at. That is
   a market-axis statement and the market axis stays CLOSED per f90/T3 — do not act on it alone.
