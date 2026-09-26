# E222 / future arms — vetted independent-opponent panel + import-hazard list

`research/coder/opponent_panel_20260927.md` · static scan of 380 loadable non-`cha22`/`sluice`/`pub_`/
`futurev1`/`w3_` agent files under `agents/**` (engine venv untouched, no imports executed, no files
written outside this note). Produced because the brief forbids mirror-only validation and because this
session has already contained one import that rewrote `submission.py`.

## Hazard: these write files at import time — do NOT import them in any probe or arm

| file | import-time write calls |
|---|---:|
| `agents/_top_pub/_raw_pilkwang_kaggriculture_structured_economic_policy.py` | 1 |
| `agents/_top_pub/_raw_boatlee_v17_r1_rc2.py` | 2 |
| `agents/_top_pub/boatlee_v17.py` | 2 |
| `agents/v28_debug.py` | 1 |
| `agents/_e98f/farmpilot_ai.py` | 1 (also dies on `charmap` UnicodeEncodeError on this box) |
| **`agents/_e98f/cropsense_the_adaptive_farm_ai.py`** | 1 — **confirmed to overwrite `submission.py`**, plus `main.py` and `submission.tar.gz`, and prints "Ready to upload submission.tar.gz to Kaggle"; it has **no `agent` attribute** |

Rule to keep: **never import an unvetted pulled agent.** Static `open(..., 'w'|'a')` scanning is two lines
of regex and catches all six; it is cheaper than the incident it prevents. `farmpilot_ai.py` and
`farmcraft_kaggriculture_grandmaster.py` additionally crash at import on this machine (`charmap`), so a
failed import is not always a hostile file — check the encoding error before assuming tampering.

## Clean panel (0 import-writes, no submit calls): 374 of 380 files

Structurally strongest and genuinely *not* our lineage, for the absolute estimator:

- `agents/_pulled_c22/pioneers_town.py` (1,192,093 B)
- `agents/prvsiyan_str_schedule_advance_20260924.py` (1,050,813 B)
- `agents/_top_pub/_raw_ahmedberatozer_v53_opening_signature.py` (1,036,776 B)
- `agents/_pulled_c22/herd_safe_sale.py` (1,034,764 B)
- `agents/oblate_orderbook_full.py` (1,029,726 B) — note the orderbook ablation already found **no
  portable trick** in it; usable as an opponent, not as a donor
- `agents/_top_pub/_raw_romantamrazov_yummers_v55.py` (1,024,462 B)
- `agents/v28_public_herd_parity_20260924.py` / `..._herd_swap_...` (1,074,066 / 1,073,322 B)
- `agents/crop_r51.py` — already used as "a real, unrelated third-party agent" in OpenCode's p27 regime B

## The caveat that must travel with any "independent opponent" number

**Independent ≠ structurally different.** `project-base-monoculture-closed` established that the public
pool is metav4/pipe16 derivatives, and most files above are ~1 MB — i.e. the same spine family with
different wrappers. So a panel of these files:

* **does** satisfy "not the candidate, not a mirror of the candidate" (the requirement that makes the
  absolute estimator meaningful and a tie meaningless), and
* **does not** satisfy "an opponent that plays a strategy our spine cannot express" — no such opponent is
  available locally, and the top-13 band is unreachable in matchmaking (0 top-13 encounters in all 214 of
  our episodes, per CQ-6's final verified statement and my own live-game check).

Therefore: report W/L/T against this panel **and** the absolute-money delta, and do not describe either as
generalisation evidence. The generalisation claim this cycle rests on the within-market replay panel
(578 paired cells, 85 replays, exec model asserted exact), not on these gates.

## Use in the current arm

`cha22_e222_throughput` was instructed to use ≥6 seeds both-seat symmetric plus ≥4 unseen common
opponents. If its own pick came from `agents/_top_pub/` or `agents/_e98f/`, **the run is suspect on
side-effect grounds and must be re-run against the clean list above** — an import that rewrites a file
mid-gate can change what is being evaluated without changing any reward line. This note exists so that can
be checked after the fact instead of discovered later.
