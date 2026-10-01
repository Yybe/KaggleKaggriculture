# V47 Shadow-price SELL ordering canvas (2026-09-24)

Observation: V11 has 110 multi-SELL cells on seed 1,000,000. Existing
preemption never fires. Active asymmetry exists only inside already-issued SELL
slots.

Hypothesis: sorting existing SELL orders by conservative marginal revenue
improves shared-price capture without changing quantity, funding orders, or
worker actions.

Intervention: reorder only existing SELL entries; preserve every non-SELL slot,
SELL quantities, and total item volume.

Measurement: changed-cell count, volume invariant, H2H R1 against V11 on the
pinned engine/config.

Gate: exploratory; positive mean and zero seed losses required.

Conclusion: pending probe.
