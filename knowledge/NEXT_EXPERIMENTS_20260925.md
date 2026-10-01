# Next-step selection after the current-field audit — 2026-09-25

Inputs: `knowledge/CURRENT_STATE.md`, `results/P6_CURRENT_FIELD_DNA_20260925.md`,
`results/P7_OUR_LOSS_ANATOMY_20260925.md`, `knowledge/PUBLIC_AGENT_REGISTRY.md`,
`knowledge/RESEARCH_MEMORY.md` (R-0xx), `knowledge/REJECTED_HYPOTHESES.md` (H-0xx).
Contest facts that constrain everything here: **final submission deadline 2026-09-30**, judging is a single
Bradley-Terry fit on post-deadline episodes against the **frozen field**, margins do not count — only
**win-rate**, and a tie contributes nothing. Two finals submissions per account.

## 12. Verdict on the previously proposed next step

**STRAWBERRY at h13 / CARROT at h00 — DISCARD. Three independent grounds, all measured today:**

1. Already run. It is the item-identity variant of the peak-hour sell retarget: `E194 mwsc`
   (MILK/WOOL + STRAWBERRY h13 + CARROT h0) = **0W/16L/0T, −$66,596.8/seed**, 10,028/74,097 units deferred,
   3.7 % realised, 6,278 forced releases, 44 `no_room` seats, 44 slot drops
   (`results/LEDGER_20260925.md:1143-1187`, `H-010`, `H-011`).
2. The mechanism is the wrong shape. Any sell-retiming must *withhold* volume to work, and the shed is not a
   bank (R-009): deferral is unbounded, release is clock-rate-limited (1 turn per 24 + forced h23). That is
   why every dose of this axis loses.
3. The current field does not behave that way. `behaviors_p6.csv` shows the winners' realisation edge is
   **not** item selection: 11/13 teams sell consolidated (≤600 orders/ep, like us), all 13 hit the 10-order cap
   every step, and their distinguishing market act is **dose at `step%24==23`** (7–17 % of units, 7/13 teams)
   on a *worse* hour (h23 is MILK/WOOL/STRAWBERRY's measured trough, R-010) — i.e. they sell earlier, not
   cleverer. Meanwhile P7's loss classes measured **TIMING = $0 and INVENTORY = $0** across 41 anatomised
   losses: not one loss we suffer is a sell-timing loss.

**q8 vs h1q6 evaluated against the CURRENT field rather than historical local opponents:** in the 70 newly
ingested live episodes, our `e206_mw_h1q6` games carry **+$3,870/episode** in final money and
**+$3,230** in `price_realisation` over the parent `cha22_champion`'s own live games, against a comparable
opponent band (`gap_decomp_p6.txt:36`, `matchup_control_p6.txt`). Two consequences. (a) On current-field
evidence h1q6 is **not worse** than q8 — the earlier "Fresh bank says −86…−104/seed vs pulled kernels" tension
in §46 was an artefact of the local pool being cha22-family-shaped. (b) The local gate's +$219.7/seed
under-estimates the live difference by ~17×, which is the same asymmetry P7 measured from the other side
(live detection limit ±$19,163/game). Neither candidate is the problem; **the axis is small**.

## 13. Top three experiments

### E1 — Dose the proven volume-conserving preemption to the field's measured share

* **Hypothesis.** Raising our hour-23 preemption from 2.9 % to 10–17 % of sold units closes part of the
  $28.7k realisation gap without touching production, and converts near-losses into BT wins.
* **Evidence.** `behaviors_p6.csv` rows "preempts at step%24==23 ≥10 %": 7/13 teams, 51 % of episodes;
  DSM 17.1 %/$14,737, UMG 16.7 %/$13,972, DECEM 14.6 %/$12,210 vs our 2.9 %/$4,315. Our price_realisation
  −$34,682 is the worst column in `gap_decomp_p6.txt`. The layer already exists and already fires live
  (18 preempts / 129 units, `LEDGER` §47).
* **Mechanism.** Selling one turn before the synchronised step-24 wave takes a quote that has not yet been
  crashed by everyone else's supply. Debt-ledger repayment keeps total volume constant, so this is *not* the
  refuted withhold-and-hope retiming (R-002). Restricted to non-rebuyable items
  (MILK, WOOL, STRAWBERRY, CARROT, TOMATO, MELON, EGG) because WHEAT/FERTILIZER fires are round-trip
  neutralised to exactly $0 by the opponent's own `BUY_PRODUCT` (R-001).
* **Control (parent).** `agents/cha22_e199_lo96q8.py` (already-layered q8 spine) so the dose is the only delta.
* **Intervention.** `qty 8 → 24`, `min_avail 6 → 4`, allow up to 2 items/turn, item order
  `MILK, WOOL, STRAWBERRY, CARROT, TOMATO, MELON, EGG`, floors from the measured per-item curve (R-010) rather
  than 90/24/140. Builder `tools/build_e199_preempt_dose2.py` extended; telemetry census asserts
  `units@mod23 % ∈ [10, 17]` before any gate is run.
* **Gate.** Census on 8 R1 seeds first (15 min). Then official 3-bank `tools/run_h2h.py E1 agents/cha22_champion.py all`
  (R1 8 seeds × 2 seats, R2 holdout, Fresh 16) **plus** the field-calibrated pool from E3. Engine pin
  `kaggle-environments==1.32.7` asserted in the log, and `tools/e209_live_entry_probe.py` before any submit.
* **Success.** Zero ties on all banks (bar for this cycle), ≥ 55 % per-seed win rate pooled,
  and **≥ +$2,000/seat-episode** mean margin — an order of magnitude above the +$219.7 the previous cycle
  argued over, and the size P7 says the live board can actually see.
* **Failure.** 0W/xL or mean < +$500/seed closes *dose* permanently (R-019: the champion is a local optimum
  under single-mechanism perturbation) and moves the market axis to `H-0xx` with this construction recorded.
* **Information value if it wins.** The realisation gap is reachable without touching the tapes → the
  remaining 6–10k is market-interaction, and finals should ship this line.
* **Information value if it loses.** Proves the field's h23 share is a *consequence* of selling more total
  volume (their `own_units` +68 %), not an independent lever → all market work stops, capacity becomes the only
  programme, and we spend the remaining 5 days on E2/E3.

### E2 — Buy the capacity the field buys: 3rd-quadrant unlock at the field step, fertilizer supply at field intensity

* **Hypothesis.** Our deficit is production volume; a runtime capacity decision (not a tape edit) that reaches
  4.00 quads, ≥1,400 tile-days and ≥180 `FERTILIZE` ops converts the +$13–20 k `production_volume_at_base`
  term.
* **Evidence.** `quads_end` us 3.14 vs 4.00 in 9/13; 3rd unlock step us 290 vs field 250–265; land spend
  us 3,571 vs 7,000 (`DNA table` rows 9/10/24/25). `FERTILIZE` ops us 115 vs 150–247 in 11/13, `fert-days`
  244 vs 397/385/357. `tile-days total` us 1,246 vs 1,502–1,566. P7 §2.1: **PRODUCTION is 57 % of our
  cha22-era loss deficit (−$25,473 of −$44,622)** and CAPACITY a further 16 %.
* **Mechanism.** Fertile tiles × tile-days is the only source of `own_units`; the leaders' realisation is
  better partly because they sell *more, earlier* out of a bigger shed flow.
* **Control (parent).** `agents/cha22_champion.py`.
* **Intervention.** One append-only layer **outside** `ig_agent` (R-008 wrap-the-spine), two clauses only:
  (a) emit `BUY_LAND` for the 3rd quadrant as soon as `cash ≥ 4,000 + 2 days of wages` and step ≤ 265;
  (b) fert *supply side*: when `shed.FERTILIZER < 1 × tiles_in_cultivation` and price ≤ the measured
  day-13-type trough, buy the shortfall (apps are supply-limited, R-015 — the refuted V13 lever changed
  *turns*, not supply). Land clause is gated on the SE-conditional-arb conditions already recorded
  (money ≥ 8,000, shops ≥ 2), so it is not the naked SE buy that went 0W/16L.
* **Gate.** **Screen before gating (15 min):** replay census that the layer actually moves `quads_end` to 4.0
  and `tile-days` ≥ 1,400 on ≥ 6/8 R1 seeds — if the choreography cannot service the new tiles, stop there
  (E130/E131 showed static-tape injections lose −$4k…−$45k exactly this way). Only then `run_h2h.py` R1.
* **Success.** tile-days ≥ 1,400 **and** mean ≥ +$3,000/seed **and** zero ties on R1; then R2 + Fresh.
* **Failure.** Any construction where `quads_end` rises while money falls closes the runtime-capacity
  channel for this spine and makes the E3/ship-the-best-line decision the finals plan.
* **Information value if it wins.** It is the first lever big enough to matter under BT judging: +13–20 k/game
  is 60× the effect size we have been chasing.
* **Information value if it loses.** Confirms on the cha22 spine what E130/E131 showed on FutureV1: capacity is
  tape-resident, unreachable by wrappers → the only remaining route is engine-in-loop tape *generation*, which
  needs >5 days and is therefore **out of scope before the deadline**. Record that so no one re-opens it in
  October.

### E3 — Rebuild the gate around the current field (measurement experiment, run in parallel)

* **Hypothesis.** Our 3-bank gate cannot see effects of the size that decides the leaderboard; a
  field-calibrated pool makes W/L/T mean something for the BT fit we are actually judged on.
* **Evidence.** P7 §1.5: live detection limit ±$19,163/game at n=19 vs the gate's +$219.7/seed (87×);
  6 of 6 recent old champions beat our candidates by +$1,392…+$1,685 while the field leader is +$13–24 k
  above us; 54 of 95 cha22-era losses are un-anatomised because our local opponents are not the pool.
* **Mechanism.** Turn the 70 ingested rank-1-13 episodes into replay-tape agents with the existing
  `tools/extract_live_opponents.py` (base85+zlib tapes + `_weed_repair_action` fallback) → a "field pool" gate
  whose per-seed margin distribution is centred on today's leaders rather than on last month's champions.
* **Control.** The existing 3-bank harness `tools/test_candidate_breakthrough.py` / `tools/run_h2h.py`, unchanged.
* **Intervention.** `tools/p9_field_pool.py`: build ≤12 tape agents (ranks 1–13, deduplicated by action-tape
  sha), emit a bank manifest in the existing `e98f_epidx` format, and a `--pool field` mode in `run_h2h.py`.
* **Gate for itself.** Each tape agent must reproduce its source episode's reward within 1 coin on its own seed
  (the check `extract_live_opponents.py` already supports); a tape that fails to reproduce is dropped, not
  approximated.
* **Success.** A candidate that beats `cha22_champion` by ≥$2,000/seed on the field pool *and* has ≥ the same
  win rate as on R1 — i.e. an effect that survives the pool that actually plays us.
* **Failure.** If field-pool results are statistically indistinguishable from R1 results, the existing gate is
  already field-calibrated and the noise explanation (P7) is the whole story: ship the best zero-tie line and
  stop engineering.
* **Information value if it wins.** Every remaining day is spent measuring things that transfer.
* **Information value if it loses.** Proves the local harness cannot rank candidates at the 3000 tier, which is
  the honest reason to treat finals as a BT lottery rather than an optimisation target (FRIEND §6).

## 14. Compute allocation (5 remaining days, deadline 2026-09-30)

| Window | Work | Learns |
|---|---|---|
| **15 min** | E1 census of `units@mod23 %` and dose grid on 8 R1 seeds; E2 census of `quads_end`/`tile-days`; E3 tape-reproduction check | Whether each candidate fires at all — inert grafts are the failure mode that fakes a clean tie (R-003) |
| **1 hour** | E1 full 3-bank gate + E3 field-pool build for ranks 1–6 | Whether the dose survives a holdout bank; whether the field pool is usable |
| **3 hours** | E2 layer build + R1 + R2 with the tile-days precondition; E1 dose-2 variant if E1 lands between +$500 and +$2,000 | Whether capacity is reachable on this spine at all |
| **6 hours** | **Justified only if** E2's 15-min census shows `quads_end → 4.0` **and** money does not fall. Then it is one paired programme: engine-in-loop capacity planning over the existing executor, gated per hour on the field pool. Otherwise **not justified** — E130/E131 already spent six hours proving static-tape capacity injection loses $4k–$45k |
Not funded: any further sell-timing/dose/floor study, any tomato-cadence tape rewrite, any public-kernel port, any replay of `REJECTED_HYPOTHESES.md` entries.

## 15. Deployment integrity (standing rule, unchanged)

Before **any** submit: engine pin asserted inside the log (`kaggle-environments==1.32.7`,
`townCenterSellInterval=24`, `episodeSteps=720`) → candidate sha1 recorded → `tools/e209_live_entry_probe.py`
reports the *live* callable and that it **is** the gated object → telemetry fire counts non-zero →
live-path single-seed delta reproduces the gate's delta → only then `kaggle competitions submit`. If the live
entry is not the gated object, the gate is void, not the candidate. `submission.py` and the Finals
active-selection remain operator/browser actions; this session changed neither.

## 16. Cleanup (nothing deleted, retrieval already excludes)

* Move-under-archive candidates: `gates_futurev1/` (146 MB, 97 logs of a closed FutureV1 study), the six
  single-question gate dirs (`gates_p5`, `gates_contestplant`, `gates_fertscope`, `gates_horizonb`,
  `gates_sweepalloc`, `gates_lineage`), `kernels_pulled/scan_20260925/*__wrapper` duplicates (wrapper `.py`
  + decoded `__BLOB.py` are the same agent at two sizes), `scratch/p8_*`, `p9_*` decoders.
* Keep-evidence: `WybeV2/datasets/p6_field_20260925/` (47 MB Parquet + manifest + hashes — the current-field
  record), `results/p6_field_20260925/`, `WybeV2/datasets/p7_live_20260925/`.
* Duplicate note worth recording so nobody re-derives it: `agents/cha22_byte_identical.py` and
  `agents/cha22_champion.py` differ by 18 bytes — only the entry binding — yet they are *different live
  agents* (the donor's own trailing alias is the platform's entry, §47). Do not treat them as interchangeable.
* `submission.py` (1,094,498 B) is the 1917.8 FutureV1 lineage while our best live file is the cha22 donor at
  2376.2 and the child at 2199.1 and climbing. Flagged, not changed.
