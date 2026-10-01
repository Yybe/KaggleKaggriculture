# V44 Phase Planner Canvas (2026-09-24)

Observation: V28-V43 route, animal, idle-worker, and price wrappers either lose,
tie, or stay dormant. Static route identity is not enough. A route must fit the
actual cash, shed, seed, and market state at its commit point.

Hypothesis: an executable cash-feasibility planner at the native day-6 router
beats shop-only route selection by rejecting routes whose complete market queue
cannot remain funded through step 671.

Intervention: one mechanism only — score each candidate route with a bounded
cash/stock simulation at the native router; preserve selected route tape and all
downstream layers.

Measurement: import/liveness proof; telemetry for route scores and selected route;
H2H probes against V11 on seeds 1,000,000 and 2,000,000, engine 1.32.7,
`townCenterSellInterval=24`.

Gate: probe is exploratory. Promote only if both seats show positive mean and no
seed loss on R1; otherwise reject and append exact deltas to the route ledger.

Conclusion: Reject. V44 selected route 103 on both probes and lost R1 `2W/6L`,
mean `-1,781.1`. Cash feasibility is not sufficient; next cycle must measure
production timing plus per-step market interaction before any policy commit.
