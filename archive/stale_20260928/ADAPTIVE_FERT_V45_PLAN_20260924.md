# V45 Adaptive marginal fertilizer canvas (2026-09-24)

Observation: DSM trace uses 131 fertilizer actions versus V11's 95, but fixed
DSM replay loses. Existing high-value fertilizer graft adds workers and loses
small margins. Extra work must be live-state and zero-labor.

Hypothesis: fertilizing an already-idle worker on a live high-value crop only
when reachable production value exceeds fertilizer cost improves H2H score.

Intervention: replace only PASS with FERTILIZE for TOMATO/STRAWBERRY/MELON
tiles; no hires, route changes, sales, or movement changes.

Measurement: fire count, crop/deadline counters, import proof, then H2H R1
against V11 on engine 1.32.7 / interval 24.

Gate: exploratory probe; require positive mean and no seed loss before any
holdout run. Otherwise reject.

Conclusion: Reject. Candidate fired zero times on both probes and tied V11
exactly. PASS replacement cannot reach live high-value crop state.
