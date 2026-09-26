# P28b ADDENDUM — intra-step commit ordering is REAL, and it is a seat-average NEUTRAL wash

Instrument `tools/p28b_seat_collision.py`, engine 1.32.7, exec fidelity **0 mismatches** (assert re-run).
Question: p28 found the winner sells ~3 days earlier, but never tested the *other* candidate for a
within-market price gap — the engine commits **seat 0 before seat 1** in every unit tick
(`kaggriculture.py:612-620`) and each SELL at `px>1` raises the shared inventory (`:659-660`). So two
seats selling the same item in the same step cannot both get the same price. Is that where the money is?

## Measurement

**32.1% of all FOCUS-item units (109,545 / 341,442) are sold in a step in which the opponent sold the
same item.** The collision is not an edge case; roughly a third of the ladder's premium volume collides.

| item | px collided s0 / s1 | Δ (s0-s1) | px **alone** s0 / s1 | alone Δ | collided units s0/s1 |
|---|---|---:|---|---:|---|
| **WOOL** | 145.5 / 130.6 | **+14.9** | 138.1 / 139.4 | −1.3 | 3699 / 4195 |
| **MILK** | 110.4 / 105.0 | **+5.4** | 106.4 / 107.3 | −0.9 | 5144 / 5426 |
| MELON | 226.6 / 223.5 | +3.1 | 188.0 / 187.6 | +0.4 | 2557 / 2402 |
| STRAWBERRY | 131.7 / 130.7 | **+1.0** | 137.2 / 134.3 | +2.9 | 5815 / 6498 |
| FERTILIZER | 49.8 / 51.2 | −1.4 | 45.5 / 42.5 | +3.0 | 9168 / 9430 |
| WHEAT | 30.3 / 30.8 | −0.5 | 34.0 / 34.4 | −0.4 | 16974 / 19239 |
| CARROT / EGG / TOMATO | Δ ≤ 1.1 in both columns | | | | |

## Three conclusions

1. **The ordering effect exists and is large on WOOL (+14.9/unit, 11%) and real on MILK (+5.4).** Seat 0
   is genuinely first onto the curve.
2. **It is a redistribution, not a creation of value.** WOOL alone prices are 138.1 / 139.4 while
   collided prices are 145.5 / 130.6 — the *pair mean* is 138.05 either way. So avoiding collisions would
   cost us the +14.9 when we are seat 0 and buy it back when we are seat 1. **Seat-averaged, and in
   absolute money, the expected gain is ~0.** A "sell offset from the opponent's step" rule is therefore
   NOT a lever, and it is not win-rate leverage either once both seats are averaged over an episode set.
   This is the same trap as the preemption family, arrived at from the other direction.
3. **The STRAWBERRY target survives the test.** Strawberry's collision Δ is only **+1.0/unit** (and its
   *alone* Δ is +2.9, i.e. noise or schedule, not order). So our refs' 10th/14th-of-15 strawberry
   conversion on the **scarcest pool of all 15 teams** cannot be explained by commit ordering. It is a
   schedule/lead-time property — exactly the thing that lives inside the route and not in the wrapper
   (`AJ_STRUCTURAL_ANSWERS_20260927.md` §J).

## Caveat that must travel with these numbers

MELON and FERTILIZER price *higher* in collided steps than in alone steps (226.6/188.0; 49.8/45.5).
That is a **selection effect, not a collision benefit**: collisions cluster in the terminal window when
the town has already drained the pool, so those steps are scarcer. Do not read it as "sell together".

## Method use

Any future per-seat realised-price comparison inside one market should report the **collided share**,
because ~1/3 of units sit in a component that is coin-flipped by seat assignment. Cohort means over
170 seat-episodes are fine; single-seat price quotes are not, at this resolution.

Files: `tools/p28b_seat_collision.py`, `results/p28_tape_divergence/p28b_seat_collision.txt`,
`results/p28b_run.log`. No engine run, no gate, no agent edit, no submission mechanism called.
