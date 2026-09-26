# Why an "inert" control still moves flow — construction rule for every wrapper in this lineage

`research/coder/inert_control_reassignment_20260927.md` · from inspecting `tools/build_e222_throughput.py`
(read-only; the arm's own files were not modified) and the arm's first seed in `results/p31_e222/`.

## The symptom

The `off` preset is designed to be arithmetically inert — `theta=99.0, keep=1.0, cap=0`, and the builder's
own comment says the layer "returns the parent's own object. Must tie the parent byte-exactly". It does not:

| both seats, seed 1000000 | rewards | flow MILK | flow STRAWBERRY |
|---|---|---:|---:|
| parent `agents/cha22_champion.py` | 81,600 / 81,600 | 407 | 391 |
| `cha22_e222_throughput_off.py` | 81,372 / 81,372 (**−228**) | **410** | **395** |

`fires=0 thin_units=0 pull_units=0 blocked_shedcap=0 credit_out=0 errors=0` — i.e. **every mechanism the
preset is supposed to disable reports itself disabled, and the episode still differs.** Committed flow,
measured from `market["inventory"]` increments, moved by +3 MILK and +4 STRAWBERRY.

## The cause to check first

`tools/build_e222_throughput.py:179`:

```python
out["market"] = revised[:_E222_MAXORDERS]
```

The early-out at `:108-109` only covers an *empty* queue. On a non-empty queue the layer **rebuilds and
reassigns the market list unconditionally**, so the action handed back to the engine is a new list whose
elements may differ in type, order-index position, or quantity normalisation even when no thin/pull branch
fired. That matters specifically because of how the engine consumes it:

* `_process_market` walks orders **by index across both seats** and commits per unit, quoting each unit at
  the shared pre-commit inventory (`kaggriculture.py:595-628`). So re-ordering or re-typing an entry shifts
  which seat's unit lands on which inventory step, which changes the price each unit gets, which changes how
  many units clear before the shed empties or the 10-order cap binds.
* A `$1`-priced SELL is **not** added to the pool (`:659-660`), so a small price perturbation can flip units
  between "adds supply" and "doesn't", amplifying an apparently cosmetic change into a flow delta.

This is the same failure family already recorded twice in this project: stateful layers leaking through a
"disabled" switch (producing false ties), and *declared* quantity normalisation changing execution
(E176/E113). The general form: **in a shared-pool, order-index-locked engine, rebuilding the queue is never
a semantic no-op, even when the arithmetic is.**

## The rule to adopt

> An inert preset must return the parent's action object **without touching the keys the engine consumes**.
> Gate the *reassignment*, not just the arithmetic.

Concretely, in any market wrapper:

1. Compute the branch decision first; if nothing would change, `return` the parent's action object
   unmodified — do not rebuild, do not slice, do not re-`dict()` it.
2. If a change is made, mutate only the specific order entry that changed, preserving list identity where
   possible and the order **index positions of every other entry** (never re-sort, never filter-and-append).
3. Assert the control at the level that decides the number: not "rewards are close" but
   **byte-equal rewards AND equal per-item committed flow AND `fires == 0`**. The `off` row above passes
   `fires==0` and fails flow — which is precisely why flow must be in the inertness assert.
4. Report the flow columns alongside every delta, as this arm already does (`flow_*` per item), so a leak
   like this is visible in the same row rather than two reports away.

## Status of the numbers this note was written against

Nothing in `results/p31_e222/` should be used as a verdict yet: with the control leaking, the mirror
candidate delta (−578/seat) and the H2H delta (+638) are both measured against a *moving* baseline. After
the control is fixed, re-run before drawing any conclusion, and expect the H2H-vs-absolute split to persist
— P34 independently predicted it (packing every premium unit as early as its own availability allows is
**−913/seat net** once our own supply is priced endogenously, so the +11,233 gross headroom is positional,
i.e. it requires beating an opponent who is not doing the same thing).

One seed, engine pin 1.32.7 asserted in the builder. No engine run performed for this note, no file outside
this one written, no agent edited, **no submission mechanism called.**
