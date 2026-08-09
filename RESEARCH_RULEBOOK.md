# Kaggriculture Research Rulebook

> **Status**: live, authoritative. Supersedes any per-session improvisation.
> Companion to `RESEARCH_PLAYBOOK_V23_TO_V26.md` (history + evidence) —
> this file is the **constraint set** for every future improvement cycle.
>
> The goal is not to hardcode a workflow. It is to keep every cycle
> *small, measured, falsifiable, and never blind to what was already
> learned*. Plans that reference this rulebook can execute fast; plans
> that don't are requested to be reconsidered before turning into hours
> of undirected experiments.

---

## 0. The Invariant (reads this rule first)

1. **The champion never changes except by promotion.** All candidate work
   is a *delta wrapper* on top of the frozen champion (`main.py`). A
   candidate is a separate file; the champion stays untouched until a
   gate says promote.
2. **The market is shared; the outcome is H2H.** Winning in this game is
   an asymmetric squeeze on the common price curve, not a farm-plan
   duel. Mirror deltas are contaminated by that shared curve and are
   NEVER evidence of superiority. Only head-to-head (H2H) deltas vs the
   incumbent, on the official engine, decide anything.
3. **Small deltas are real deltas.** The recorded losses were small
   systematic gaps (159–1,914 coin range on the earlier endgame-patch
   runs; V26's own margin reported at +618/100 H2H). At the top, sub-2k
   systematic gaps are the entire game. Never dismiss a persistent H2H
   margin as "noise" because it is small — noise is what repeated
   games measure, not magnitude.

---

## 1. The Experiment Canvas (mandatory per cycle)

Every experiment writes, at minimum, this canvas **before code runs**:

```
Observation   — what instrumented fact motivates this?
Hypothesis    — the ONE mechanism claimed (falsifiable, in one sentence).
Intervention  — EXACTLY ONE mechanism changed; everything else frozen.
Measurement   — what is measured (H2H delta, per-step SELL trace, shed
                dump) and what success looks like (pre-registered).
Gate          — official engine, fixed seed set, N games, pre-registered
                pass/fail rule (mean + CI, not vibes).
Conclusion    — Accept / Reject / Inconclusive; row appended to the
                ledger (§4) the same session, win or lose.
```

**One lever per cycle.** If the plan changes two mechanisms, split it
into two cycles. (V24 was killed by exactly this: three orthogonal
changes in one diff made its regressions unattributable.)

---

## 2. Measurement rules (what counts as evidence)

1. **H2H is the truth.** Mirror sweeps may be run for instrumentation
   only; they are never a gate. A candidate promoted on mirrors is a
   mistake by definition (see: "aggr v26", −972, rejected).
2. **Instrument before hypothesizing.** Every cycle that touches the
   sell side starts with traces: shed/inventories every 60 steps (the
   `dbg4` style) and a **per-step SELL dump** (step, product, qty, price
   available) over the last 10+ days (`dbg5` style). Never build a
   quantity hypothesis on basket-level aggregates — a +2 bump in 3
   products is invisible in a season-total basket and is exactly how we
   "proved" baskets were identical while the mechanism was missing.
3. **Persist everything, in-session, to numbered files.** Console-only
   outputs die at session compaction (playbook §9.5: the reason the
   playbook exists). Every run writes `bank_out*.txt` / `gate_*.txt` /
   trace files. If it's not on disk, it didn't happen.
4. **Facts are tagged.** [F] file-verified, [S] docstring, [G] git,
   [H] hash, [R] prior-session recollection. Anything tagged [R] is a
   hypothesis to verify, not evidence to build on.
5. **Never generalize from an unmeasured number.** When a trace looks
   odd (a suspicious tie, a surprising surplus), rerun the instrument
   before theorizing on top of it.

---

## 3. Gate rules (the only pass/fail authority)

1. **Official engine, official config.** `kaggle-environments` ≥ 1.32.4
   (local is 1.32.5), engine-built `make("kaggriculture")`, 720 steps.
2. **Both regimes count as separate gates.** Legacy (`interval=12`) and
   **rebalance (`interval=24`)**. A candidate adopted on one regime only
   carries an unmeasured risk on the other. V26 has only legacy evidence
   today — that's a known, recorded gap, not a scandal, but it must be
   closed before broad claims.
3. **Pre-register the decision rule.** Before the gate runs, on the
   ledger: N games, the frozen seed family (`1M 9M 3.33M 7.77M 5M 6M 8M
   2M`, playbook §8), and the pass rule: **≥ 6/8 wins with positive mean
   delta** (playbook §12.4; a single 8-seed sweep is a probe, not a
   gate),
   extended confirmation at N = 100 preferred. Win-rate alone never
   decides a close call; mean delta decides.
4. **A gate that fails is a result, not a rerun.** If CI straddles 0 →
   INCONCLUSIVE: extend games, do not theorize. If CI < 0 → REJECT, move
   to the next hypothesis. Do not chase a reject with "one more seed"
   after the boundary is clear.
5. **A promoted candidate becomes the new incumbent only after** hash
   + wire-diff + archive-of-old-champion, and a boundary banner in the
   ledger. The old champion survives as `archive_main_v<promoted>.py`.

---

## 4. The Experiment Ledger — the "never rediscover" rule

1. Every experiment (including dead ends, negative gates, killed
   variants) writes one row in the ledger in the same session:
   `ID | hypothesis | mechanism lever | regime(s) | N | mean Δ | CI |
   verdict | trace files | date`.
2. **Before starting an experiment, consult the ledger.** If the exact
   mechanism-intervention pair appears (e.g. "sellall — killed 2026",
   "aggr fill — −972 rejected"), do not and re-run it: extend, or pick
   the next lever.
3. The playbook's hypotheses ledger (§2/§4) is precedent: H1–H7 with
   verdicts are the first rows already recorded. New rows continue the
   numbering (H8…).
4. Ledger and rulebook live next to the champion file so any future
   session (or agent) starts from the same memory; references are made
   in every improvement plan.

---

## 5. Guardrails (no-go list, each with the reason it exists)

| # | Banned move | Why (what taught it) |
|---|---|---|
| G1 | Promote on mirror deltas | shared-curve confounding; v26b conserved, H2H revealed |
| G2 | Route-swap redesigns ("copy the top agent's route") while no route mechanism is established | the 3 transplant candidates lost outright (A −31k, AF −6.6k, BF −0.4k; `[R]` prior-session figures — reverify at exploration time); the win mechanism was quantity/timing on the SELL side, not the farm route |
| G3 | Multi-lever candidates (scope creep) | v24: 3 changes, regressions unattributable, archived |
| G4 | Harvest-what-you-can fills / overflow-inducing adds | aggressive v26: −972 mirror leak via shed-cap crowding |
| G5 | Unified price-dump ("sellall") / low-value late bumps | price collapse; WHEAT/FERT late tops-up kill EV |
| G6 | Unmeasured theory on quantities | the "baskets are identical" aggregation hid the +2 top-up — aggregates differ from streams |
| G7 | Untested regime claims ("this also works at i=24") | rebalance regime never gated to-date; speculation is not evidence |
| G8 | Console-only results / session-memory as the record | playbook per-seed tables lost to compaction; disk or nothing |
| G9 | "Just one more seed" to bend a clear reject | bounds: CI decided, not desire |
| G10 | Trusting [R] recollection | prior-session numbers are hypotheses (§2.4) |

---

## 6. Budget discipline (against "dwelling into hours")

1. **Plan first, code later.** A cycle that starts with
   canvas-filled (§1) + ledger-check (§4) + gate-registered (§3) has a
   natural end. Any cycle that starts with exploring without a canvas
   is cut within the hour.
2. **One mechanism, N ≤ 3 candidate values** per cycle (e.g. cap 3 vs
   cap 4 in sequential H2H). Empiric sweep in one cycle: gate cap 3
   single; if bordered, cap 4 never.
3. **Timebox per gate**: one frozen 8-seed probe (≥ 6/8 + positive
   mean — playbook §12.4), then the extended N=100 confirmation only
   when the probe is positive; do not empty a session into a single
   borderline hypothesis (rule §3.3).
4. When 3 consecutive cycles on related mechanics are all
   Inconclusive/Reject: stop the programme, reopen the canvas from a
   fresh trace (not from assumption), and record the closure. The rule
   is the guardrail: an unresolved mechanism is not an excuse to pivot
   to geometry (the "route" mistake). It is a reason to go back to the
   trace.

---

## 7. The V27+ / next-cycle quick checklist

Before *any* improvement plan is executed, it must answer: preprint
"address rulebook §0-6" or it isn't ready to run.

- [ ] Champion frozen as `main.py`; candidate is a wrapper of it?
- [ ] Hypothesis states ONE mechanism, falsifiable?
- [ ] The trace/instrument that will *see* the mechanism (SELL stream /
      shed dump) is named?
- [ ] Gate pre-registered: regime(s), seed set, N, CI rule, on official
      engine?
- [ ] Ledger consulted — no duplicate of a killed experiment?
- [ ] Success/cancel written to disk plan?

---

## 8. Sanctioned next experiments (already on the ledger draft)

E8 (cap experiment) — V27-A: cap 3; V27-B: cap 4; all else frozen
(intervention per §1). Measurement: H2H delta + per-step SELL stream
(confirm quantity/value/step delta across caps). Gates: probe 8 seeds
≥6/8 with positive mean (playbook §12.4), extended N=100 confirmation,
pre-registered before running (rule §3.3); *rebalance* variant gated
the same way since champion evidence exists only in legacy.

E9 (regime check) — V26 baseline at `interval=24`: run H2H vs v23
under the rebalance config on the same frozen 8-seed set, plus trace
the top-up behavior in that regime; record whether the +2
late-high-value edge persists, reverses, or never materializes.
This closes G7 directly.

Both are single-lever cycles, pre-registered, small, and either
conclusion is a row in the ledger — exactly the shape this rulebook
wants.

---

*Rulebook version 1 — authored 2026-08-08. Update version + date when
rules change; never edit silently. Changes must be additive / explicit.*