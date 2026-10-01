# ZERO-TIE STRATEGY — 2026-09-24 (synthesis, no code; needs operator pick)

Pin: 1.32.7, townCenterSellInterval=24, 720 steps, both seats, seed-level W/L/T.
Champion: `agents/futurev1_forecast.py` (6W/0L/26T pooled vs PRED-B — safe, tie-heavy).

## 1. What the two feeds jointly prove

Autopsy (`_scratch_ourlosses/OUR_LIVE_LOSS_AUTOPSY_20260924.md`): in our live −19k/−19k/−7.6k
router losses, production DNA is at FULL parity (hire/fert/plant/water ±2%, mirror 63–76%),
crash losses symmetric, plumbing zero — the leak is the **10-slot/day market ALLOCATION**:
fixed-mix lines (+ empty-shed firings) vs field sweep-alls + high-value-first mix ≈ −12…−13k/game
(~65–70% of margin). Allocation, not count (L2 leaks −19k with only +15 opp lines).
Survey (`DECISIVE_MECHANISMS_SURVEY_20260924.md`): tie-BREAKERS (preempt/sweep/reorder/oracle)
cap at ±0.6% with residual ties; tie-KILLERS change production every seed (v57 chassis swap:
0 ties/256 games; V11 dump: 0 ties/192 fleet games).

## 2. Zero-tie construction (two halves, each singly-gated)

HALF-A — allocation rebuild (converts decisiveness into wins; attacks the −13k leak):
replace fixed-mix SELL lines with per-step shed-aware sweep-alls (SELL actual shed contents,
high-value-first: MILK/WOOL/STRAW over wheat, same-step DROP→sweep capture), within the 10-slot
cap, debt-ledgered against the parent schedule. Base: FutureV1. Gate: R1/R2/Fresh vs FutureV1,
bar = zero seed-losses AND mean > +500 (allocation must move coins, not just reorder them).

HALF-B — production differentiation (kills ties by construction; attacks mirror parity):
fert-scope rebind 114→~221 funded by existing flow (V29 L132-138, zero purchases; re-bind
forecast+path+joint-plans, retune 1.5*cost+50 — V30/V33 naive variant warns −265/−293).
Gate: R1 vs FutureV1, bar = decisive rate (W+L) ≥ 6/8 seeds AND zero seed-losses.
TOMATO-native chassis stays OPTION-C (lineage swap via extract_live_opponents + elimination
matrix) — bigger surgery, only if A+B leave ties.

## 3. Why ties die under this plan (structural argument)

Ties require shared tapes. HALF-B changes plant/fert/hire actions on every seed → tape differs
from parent on every seed → vs-parent ties → 0 by construction (remaining outcomes are W or L,
gated). HALF-A changes SELL mix/velocity daily → even seeds where production converges still
diverge at market. Combined: no seed family left where cand == parent. Residual risk: both halves
could lose (decisive includes L) — the gates (zero-loss + margin bars) are the filter, not hope.

## 4. Order + stop rules

Build A first (attacks the measured −13k leak on the proven-safe champion; market-only, no
production risk), gate R1→R2→Fresh; then B on top of A, same banks. ANTI-LOOP: 2 fix attempts per
half; any red → STOP, ledger, operator decides. No submission.py touch until both halves pass.
Dead axes (do not spend): FRIEND §2 list + ROUND2 a/b + survey §(c) warnings (V28 64-key tables,
herd overlays, tape replays, MW expansion, hold-for-reprice, leaner hiring).
