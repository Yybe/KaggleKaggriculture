# Phase-DNA trace (2026-09-24)

Source: pinned engine 1.32.7, interval 24, seed 1,000,000;
`tools/trace_phase_dna_20260924.py`.

Compared V11 against extracted DSM tape. This is diagnostic only; DSM tape is
not a deployable opponent policy.

| seat | reward | harvest actions | fertilize actions |
|---:|---:|---:|---:|
| V11 | 156,092 | 482 | 95 |
| DSM tape | 27,888 | 552 | 131 |

DSM emits a denser production/input cadence and sells many products every day,
but fixed replay cannot preserve physical state. Therefore copying its tape is
invalid. Useful target: adaptive production timing that verifies live tile,
inventory, and shed state before each extra input or sale.

Artifact: `results/phase_dna_v11_dsm_1m.json`.
