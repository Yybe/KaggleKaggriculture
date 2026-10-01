# V28 current-line forensic deployment — 2026-09-24

## Evidence

- Kaggle replay pull: `results/V28_live_eps/summary.json` — 103 episodes, 69 wins, 33 losses, 0 ties.
- Loss anatomy: `results/V28_live_loss_forensics_20260924.txt` and `results/V28_live_anatomy_20260924.txt`.
- Mean live loss delta: -2115.9. Largest observed loss: episode 112547461, -18972.
- The dominant loss signature is production capacity: opponents commonly carry 8 COW / 6 SHEEP while V28 carries 5 COW / 5 SHEEP; MILK/WOOL/STRAWBERRY revenue gaps follow.

## Candidate tests

`tools/build_v28_public_herd_parity_20260924.py` and `tools/build_v28_public_herd_swap_20260924.py` are append-only grafts from the current `submission.py` SHA-256 `6dc54cb69a8c1b41e35b1b18f10a030afd0a7310266af339d498445f15a66043`.

- Herd-parity graft: fixed live tile schema (dict or string), but full-game telemetry remained `buys=0`; R1 was 0W/0L/8T. Rejected as inert.
- Herd-swap graft: replacement of a seed order under a severe visible deficit; full-game telemetry remained `swaps=0`. Rejected as inert.

## Deployment decision

Keep the current V28 spine. It is the strongest tested local lineage: versus V11, 8W/0L/0T, mean +1452.1; E94 versus V28 is 1W/7L, mean -1151.6. Historical Kaggle scores were treated as stale and not used as selection evidence.

The submitted artifact is the verified current `submission.py`; rejected grafts remain only as forensic artifacts.
