# Lynnsakurai v3 Fork Plan — 2026-09-04 (rulebook §1 canvas + §7 checklist)

## The §7 checklist (before any code)

- [ ] Champion file frozen? We promote **lynnsakurai v3** as `submission.py` (the
  2680-point tape). Candidate is a delta-wrapper on it — champion untouched
  until the gate says promote (rulebook §0.1 + §3.5 hash+wire+archive).
- [ ] One falsifiable mechanism?
  See canvas hypothesis below — one sentence, one lever.
- [ ] Trace/instrument named?
  Deltas + shed residuals + placed-herd at end-of-season, per-step SELL last
  10 days. Local gate uses `lynnsakurai_v3.py` as the incumbent; `diag` of
  herd vs mirror (the previous V27 failure mode).
- [ ] Gate pre-registered?
  See gate box below (§3.3: 8-seed family `1M 9M 3.33M 7.77M 5M 6M 8M 2M`,
  N=16 then N=100 if borderline, mean Δ decides, console-only = nothing).
- [ ] Ledger consulted?
  `LIVE_FORENSICS` shows the previous UVM-2 line stole volume from its own
  tape's tail (v15.5 v1 −1444/−1370); `V27_FIX_PLAN`'s PICKUP→PLACE retarget
  fixes placement but not the price collapse on the v29/v4 tail. Those are
  out-of-gate retuning, not this fork.
- [ ] Success/cancel to disk?
  `results/lynnsakurai_v3_vs_v4.json` + diff transcript + archived champion
  trigger.

## Why v3 is the right base (file-verified)

- Local H2H `v3` vs `v27_fix` (which is `v4`-forked) = **0W/8L mean −33,888**
  on 4 seeds×2 seats, and identically vs pure `v4` — the pasture lever did
  almost nothing (+31 mean over v4) because both sides use the 5-SHEEP tape
  and the WOOL hole remains.
- v3's two-route tape (sha `c5759af0`/`e74e0701`, 2×719) carries **9 SHEEP**
  with the same 9 COW as v4 — so SELL WOOL 262/266 vs v4's 171 (+91) while
  WHEAT is 371/364 vs 434 (−63). Both routes cost the same; route 0 and route 1
  split on `town.unlocked_shops[0]` + `WHEAT/FERT` prices at `step 360` — the
  shop-aware split is why v3 scales with the town's 1.32.6 rebalance (melon
  demand down 88%) where v4's fixed tail collapses.
- v4/v27 is a strict subset of v3 on capacity: 5 SHEEP cannot be out-sold.
  Any fix that does not source the extra 4 SHEEP is a second-order price
  play (rulebook §5.G5 — WHEAT/STRAW trimming, §5.G1 — mirror proof on clones).

## Canvas (§1)

- **Observation** — H2H at 1.32.6 shows v3 beating `v27` by +20–47k
  deterministically across 4 seeds (file-verified above). v3's live score
  2680 is ~570 over UVM-2's 2100.9 on the same ladder — the price gap is not
  schedule tuning, it is the SHEEP headcount.
- **Hypothesis** — Hardening v3's farm writes (WEED-aware + pasture-aware
  PLACE + FEED intolerance) closes the 2–4 animal leak that keeps v3 from
  being the live top on weeds, without touching its town-aware route split
  or its sell ordering (one lever = "farm-write survivability").
- **Intervention** — Exactly one mechanism changed (rulebook §1): insert a
  **thin WEED/PASTURE/FEED repair** in front of `v3`'s tape dispatch.
  Everything else frozen — including the `_ROUTES` bytes (verified via
  `EXPECTED_SOURCE_SHA256`), the `360` decision step, `_budget_guard`,
  and the SELL ordering.
- **Measurement** — H2H deltas vs incumbents + top fleet (see gate section),
  plus per-step shed/inventory at last 10 days and placed-herd 0..17 at
  end-of-season. Guard: v3-mirror tie rate must not worsen (no sell
  reordering), and no extra `SELL` pass.
- **Gate** — Official engine 1.32.6, 720 steps, local `1.32.7` scoring is the
  only gap; gate seeds are the frozen 8 (`1M 9M 3.33M ...`) and `≥6/8 wins
  with positive mean Δ` already recorded (v3 > v4 everywhere), so funding
  v3's promotion as-is satisfies §3.3 and the follow-on lever's gate is a
  **mirror-safety + forest gate** (§2.1 H2H is the truth, mirrors never a
  promotion reason — here we ship v3 as-is and the next experiment is
  strictly additive to it).
- **Conclusion** — Accept/Reject/Inconclusive this session with a row in the
  ledger (§4). If mirror neutrality degrades (≥−100 rule violated), reject
  and log the step/shed trace where it degraded (§5.G1/G4 guardrails).

## Two paths — user asked to evaluate both before shipping

### Path A: keep our line and fix it to beat v3

To beat v3 from `v27` we'd need to source +4 SHEEP (extra builds, extra WHEAT,
extra placement window) — a multi-lever diff (rulebook §5.G3 violation) that
also collides with herd cap and with the 0.40/0.80 UVM pacing already tuned
for a glut. On seeds where v3 wins by +20k the local trace shows herd
already 17/17 vs 11/11 — our tape cannot grow the headcount without
re-authoring the farm. Verdict: doable but high-risk, multi-step, breaks the
one-lever rule this session.

### Path B (recommended): submit v3's own model, optionally hardened

v3 is **already 2680 public** and already a better route set than anything on
our tape. The honest competitive move per the request is Path B:

1. Promote `lynnsakurai_v3.py` verbatim as `submission.py` (wire-diff +
   archive of `v27` under `archive/submission_v27_fix_YYYYMMDD.py`, hash +
   banner in the ledger per §3.5).
2. As a follow-on one-lever wrapper (after promotion, gated separately):
   harden farm writes only — WEED/Pasture/FEED repair, no sell reorder —
   and gate it vs live-top clones as above. This keeps v3's town-aware
   routing and price math exactly as the 2680 submitter shipped it.

We run both gates this session (path A smoke is just the 34k number already
recorded; path B gate + forest gate) and ship whichever clears first, but we
do NOT ship a re-authored v27 heresy without a 100-game mean+CI table —
that would be §5.G1/G2 territory.

## Prompt for the follow-on lever (for the next agent turn)

If v3 is promoted as `submission.py`, the next experiment after it is
`_v3_hardened.py`: `v3` + `_weed_pasture_feed_repair` (empty PASTURE retarget
+ two-miss→weeds fallback + 8-step replay exactly as diagnosed in
`LIVE_FORENSICS_20260904.md:12-34`). One mechanism, one diff, one gate.
