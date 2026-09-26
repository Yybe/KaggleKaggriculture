# P28c VERDICT — the tape-side price mechanisms are worth ~12% of the gap, not the gap

`tools/p28c_leadtime_price.py` · `results/p28_tape_divergence/p28c_leadtime_price.txt` · engine pin
1.32.7 · 578 paired `(ep,item)` cells over **69** leader-vs-leader episodes, weighted by units at risk,
4,000-draw **cluster bootstrap over episodes** (seed 20260926). Reads only the p28 CSV. No engine run,
no gate, no agent edit, **no submission mechanism called**.

**This supersedes two of my own claims from earlier today** — the "surviving target: STRAWBERRY
conversion" framing in `research/coder/RATCHET_RETRACTION_20260926.md` and the prize-free §J/§22 text in
`AJ_STRUCTURAL_ANSWERS_20260927.md`. Both are corrected below with numbers.

## Lead-time, priced

`d_px` is ≥0 by construction (winner − loser) and the winner's `d_day` is negative (it sells earlier), so
**a negative beta means selling earlier earns**: prize = `-beta × days_earlier × units`. (A first draft
of this file printed the prize negative by mishandling exactly that sign; the convention is stated in the
output so it cannot be re-mistaken.)

| specification | beta coins/unit/day | R² | 95% CI |
|---|---:|---:|---|
| pooled `d_day` | −1.303 (se 0.014) | 0.075 | [−1.94, −0.78] |
| `d_inv` (**mediator**) | −0.025 | 0.007 | [−0.06, −0.01] |
| `d_maxrun` | 0.001 | 0.000 | [−0.02, 0.02] |
| `d_hour` | 0.216 | 0.009 | [0.02, 0.43] |
| `d_mod23` | 0.029 | 0.002 | [−0.02, 0.09] |

Pooled beta is an average over items whose slopes differ 14× and whose leads differ 15×, so the
defensible number is per-item, on **our own** committed premium units per seat-episode
(MILK 538, STRAWBERRY 492, WOOL 334, MELON 148 = 1,513/seat):

| item | beta | median lead | prize at 100% capture | at 50% |
|---|---:|---:|---:|---:|
| MELON | −7.558 | 1.54 d | **+1,721** | +861 |
| WOOL | −3.860 | 0.87 d | **+1,121** | +561 |
| MILK | −2.211 | 0.40 d | **+470** | +235 |
| **STRAWBERRY** | −0.552 | **0.10 d** | **+28** | +14 |
| **TOTAL** | | | **+3,341/seat/season** | **+1,671** |

Pooled upper bound at a 3.06-day lead would be +6,033, but no item actually carries a 3-day lead — the
3.06 days is the median over the *divergent* set pooled across items, and the per-item decomposition says
the real leads are 0.10–1.54 days.

## What this settles

1. **Lead-time is real but it is a fraction of the gap: +3,341/seat against a 26,813 matched-volume
   `own_revenue` deficit = 12.5%.** It clears the ±900 live-noise band (so it is worth **one candidate**),
   and it fails the brief's bar for an architecture rewrite (P0 structural gap, "a materially different
   strategy", "closing a substantial portion").
2. **STRAWBERRY is refuted as the target — by my own number.** β=−0.552 with a 0.10-day median lead buys
   **+28 coins/seat**. So the "scarcest pool of all 15 teams yet 10th/14th-of-15 conversion" anomaly is
   **not** a day-ordering effect, and p28b already showed it is not commit ordering (+1.0/unit). Two
   independent within-market mechanisms now measured and both ≈0 on the item I nominated. The residual on
   strawberry is unexplained by anything a sell schedule does.
3. **MELON and WOOL carry the mechanism, not MILK.** 86% of the prize sits in WOOL+MELON, which are the
   two narrowest cliffs (59 and 158) and, per p27, the pools where a second seller hurts most. That is the
   *opposite* of where p17 located the dollars (MILK px/base 0.375 vs 0.831, MILK alone −17,713). So the
   item where we lose the most money is **not** the item where the tape can win it back.
4. **`d_maxrun` beta ≈ 0 (R² 0.000)** under units weighting, so p28's "smaller largest order" (win-share
   29%) is a *consequence* of spreading volume, not an independent price lever. Do not build an
   order-size cap.
5. **`d_hour` is marginal and contradicted** — p28's permutation test on hour gave p=0.24 while the weighted
   regression shows R²=0.009 with CI barely excluding zero. Treat hour as null; do not build a time-of-day
   rule on it.
6. **`d_mod23` beta 0.029, CI [−0.02, 0.09]** — third independent confirmation that the step-24 preempt slot
   carries no price. The `cha22` E210 preempt's measured +223 is a *tie-breaker against a clone*, not a
   price mechanism (consistent with [[project-ladder-means-are-few-worlds]]).

## Revised §22 / §J answer (value branch)

`AJ_STRUCTURAL_ANSWERS_20260927.md` asked whether the architecture must change. The evidence now says:

* **The mechanism the architecture cannot express (lead-time) is worth +3.3k/seat, not +26.8k.** So a
  rewrite is **not** justified by this axis. Recommendation narrows to: build the release/production
  calendar scheduler as a **bounded candidate** for WOOL and MELON only (86% of the prize), 1–2 days of
  work, symmetric arms, H2H *and* absolute — and treat anything larger as out of scope.
* **The remaining ~87% of the gap is not attributable to any sell-side mechanism measured this cycle**
  (rate ✗ p19 · mix 6.5% ✗ p17 · season shape ✗ p17 · opponent animal-mix ✗ p25 · hour ✗ · mod23 ✗ ·
  commit order seat-average-neutral ✗ p28b · lead-time only 12% ✗ p28c). What is left standing is
  **production** — herd scale (E104, route-locked, COW XOR SHEEP) and route geometry (E152) — which is
  exactly where every constructive attempt this project has made has failed.
* **The harvest-vs-sell-day census (CQ-7/p29) still decides whether even the +3.3k is reachable**: if the
  winner's edge is a genuinely earlier *harvest*, it is route-resident and unreachable by a wrapper.

## For the operator, plainly

Nine candidate families plus this cycle's nine measurements now converge on one sentence: **the leaders
do not do anything with the market that our spine cannot already do; they produce differently, and the
sell-side correction that is measurably available is worth roughly +3.3k/seat (~4% of a season), not the
~2× money gap to the top of the ladder.** Per §20 the honest answer to "are we optimizing the wrong
abstraction?" is now **yes — the market/price abstraction has been mined to within ~12% of its own
budget and cannot close the gap**, and the abstraction that holds the remaining ~87% (herd + route
co-design) is the one E104 priced at −65,875 as an overlay and E152 blocked as tape surgery.
