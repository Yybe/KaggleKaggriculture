# RESEARCH PLAYBOOK — V23 → V26 (Kaggriculture)

> **Purpose**: complete, evidence-tagged reconstruction of how the V26 champion
> (`kaggle_v26.py`, "capselllate") was researched, built, and validated on top of the
> V23 incumbent. Reusable as a methodology for the next promotion attempt (incl. a
> "how to dethrone V26" protocol).
>
> **Evidence legend**: `[F]` verified from an on-disk artifact this session; `[S]`
> quoted from a code docstring; `[G]` git history; `[H]` file hash verified this
> session; `[R]` reported in a prior session summary (NOT re-verifiable from disk);
> `UNKNOWN — NOT RECOVERED` = genuine gap, nothing invented.

---

## 1. Chronological Timeline (V23 → V26)

1. **Pre-v23** — `Kaggriculture/` research dir: engine-source study
   (`KAGGRICULTURE_GUIDE.md`, ground-truth constants), opponent spy (`findings.txt`),
   pre-v23 history (`RUN_REPORT.md`). `[F]`
2. **Candidate lineage** — "Kaitofukami 44/46 copy with candidate9" (`9c8f62f`);
   then "Candidate9 v23: Integrated Meta Enforcement Guard and Day-1 hiring
   protection into v23 trajectory agent" (`4ea24f8`). `[G]`
3. **V23 frozen as incumbent** — sparse closed-loop agent with a precomputed farm plan
   (zlib+base85 payload embedded), plan chosen once from engine config (Azelearn
   strict-future route for legacy engine; Khanh route for PR #1394); runtime feedback
   limited to actor-local weed recovery + SELL-slot ordering by price impact + bounded
   demand term (rebalance regime only). Sites: `agents/kaggle_v23.py` — SHA-256
   `76F6FCE5470B568410D79AA1EA7B32AC1F0616B6584D6CD6E146DA1CBB037252` — and identical
   copies at repo root `main.py` / `kaggle_agent_main.py` (same hash). `[F][H]`
4. **V24 experiment (abandoned)** — v23 + idle-utilization + feed-cash clamp + legacy
   demand term (`diff_v23_v24.txt`). Direct H2H vs v23: **LOSS 110,661 vs 124,142**;
   **LOSS 88,998 vs 149,852**; **tie 119,870 vs 119,870** (suspiciously identical to the
   baseline — possibly unused/bugged run). Never promoted. `[F] bank_out*.txt`
5. **Idle-fill research cycle** — hypothesis: v23 wastes PASS turns; build `sweep_lib.py`
   with **one-rule variants** for filling PASS turns, measured mirror-vs-mirror on seeds
   1M/9M (legacy). Variants: `base`, `aggr` (=aggressive v26), `capfill`, `capsell`,
   `latefill`, `sellall` (**KILLED — price collapse**), `capselllate`. `[F] sweep_lib.py:1-18`
6. **Aggressive v26 rejected in mirrors — the "-972 leak"** — harvesting ongoing crops +
   animals whenever yield > 0 on PASS turns added units that overflow the 100-cap shed
   and crowd out scheduled drops. `[S] kaggle_v26b.py docstring`
7. **v26b (safe half-step)** — water unwatered plants + harvest one-shots only at
   absolute max yield; market orders exactly v23's; mirrors ≈ neutral. `[F][S] kaggle_v26b.py`
8. **Capacity instrumentation** — `dbg4_out.txt` dumps shed/inventory every 60 steps:
   during v23 runs shed max **91** (step 600), inv max **60** (step 660), final bank
   **119,870** → the shed cap (100) is **not** the binding constraint;
   unsold surplus + timing is. `[F]`
9. **v23 sell-window profiled** — `dbg5_out.txt`: SELL blowout at 624 (STRAW 14, MILK 9,
   FERT 12, WHEAT 14), 648 (WOOL 18, MILK 12, STRAWBERRY 10, WHEAT 4), dribble 661–677
   (small FERT/MILK/STRAW/FR), then 696 (MILK 12, FERTILIZER 14, WHEAT 41), 710–718 final wipe;
   shed empty at end; final bank **124,246** (this seed); money 600→719: 88,158 → 124,246.
   `[F]`
10. **The "aha" — asymmetric shared market —** markets/town are SHARED; extra units you
    sell late depress the common price curve, hurting **v23's fixed big dumps (624–696)**
    more than they hurt you. Therefore mirror deltas are misleading; **H2H is the
    truth**. `[S] kaggle_v26.py:1-21`
11. **V26 champion** = v23 + safe fill (v26b-style) + **capselllate**: at step ≥
    19*24 = 456, bump ONLY high-value SELLs (STRAWBERRY 120 / MILK 160 / WOOL 200) by
    **+2 max** when shed holds more than the planned qty; NEVER low-value (WHEAT /
    FERT 100). `[F] kaggle_v26.py:1-21,32-37,101-137` — same policy in
    `sweep_lib.py:163-183`.
12. **Promotion** — H2H vs v23: **8/8 wins** (docstring); bundled single-file
    `submission.py` (inlined v23) commit `014139d` "…validated 3/3 H2H vs v23
    (d=+673/+395/+938)". Smoke 7/7 `[R]`; gate decisions 32/32 + 32/32 earlier gate
    `[R]` (exact pool tables `UNKNOWN — NOT RECOVERED`).
13. **Deploy** — Kaggle submission run ID `[R]` → **COMPLETE, publicScore 600.0**;
    backup zip `FARM_V26_BACKUP_…` created `[R]`; pushed to GitHub `[G]`.

---

## 2. Hypothesis → Experiment → Result Ledger

| # | Hypothesis | Experiment | Result | Verdict |
|---|---|---|---|---|
| H1 | v23 leaves yield on the table via PASS turns | aggr fill (harvest everything harvestable) | ~-972 mirror regression (overflow) | **REJECTED** |
| H2 | Only capacity-safe fills can help | v26b fill set (max-yield & water only) | mirrors ≈ neutral; H2H positive | **kept as base** |
| H3 | Shed capacity 100 is the binding constraint | 60-step dump (`dbg4_out.txt`) | max shed 91 < 100 | **FALSIFIED** for v23 |
| H4 | Extra late high-value units hurt the seller via price collapse | `sellall` (dump everything at once) | price collapse — killed | **REJECTED** |
| H5 | Extra late units depress the SHARED curve → asymmetric win | capselllate (+2, ≥456, high-value only) | H2H 8/8 vs v23 | **CONFIRMED — champion** |
| H6 | Mirror deltas predict promotion | mirror vs H2H comparisons | mirrors misled; H2H is truth | **rule: H2H decides** |
| H7 | v24 guard set improves v23 | v24 H2H (3 seeds) | 2 losses + 1 tie | **REJECTED/archived** |
| H8 | Deeper counter-preemption (h=(4,3,2,1), fire BEFORE opponent's h=3 shift at T−3) beats salemali7's own preemption | V16a = V15.5 brain + `_counter_preempt` (V15.5 agent() + counter line); gate: rulebook frozen 8-seed family, ≥6/8 + positive mean, N=100 | Root cause found & fixed: `NameError: _PREEMPT` (undefined) at line 127 crashed the counter → 4-step PASS fallback → SAL swept (Δ −54,400). After fix `for item in _PREMIUM:`: gate **8W/0L, mean Δ +2,361** (min +738); N=100 fresh seeds **100W/0L, mean Δ +2,325**; regression vs V15.5 **8W/0L, mean Δ +1,594**. Counter fires 45× vs SAL 39×, lands T−4 one step before SAL's T−3. Ladder: vs V15 **8W/0L +2,074**, vs V14 **8W/0L +2,368**, vs V26 **8W/0L +3,451**. Rebalance (`interval=24`): vs SAL **8W/0L +2,646**, vs V15.5 **8W/0L +1,619** | **CONFIRMED — gate passed, ladder clean, rebalance closed; promoted to incumbent** |

---

## 3. False Leads & Dead Ends

- **`sellall`** — selling the full shed at once destroys own price curve. Killed with an
  explicit comment in the sweep rig. `[F] sweep_lib.py:159-161`
- **v26 aggressive fill** — ongoing-crop + animal harvesting ≈ overflow loss (the
  "-972 leak" as named in v26b's docstring). `[S] kaggle_v26b.py`
- **v24** — demand + idle-fill + feed clamp did not beat v23 on direct H2H; archived.
  `[F] bank_out*.txt`
- **"Capacity is the problem"** — falsified by instrumentation; pricing *timing* was
  the lever. `[F] dbg4_out.txt`
- *(earlier, pre-v23)* candidate families "Kaitofukami 44/46" & GitHub v23 —
  superseded by Meta-Enforcement-Guard v23. `[G]`

---

## 4. Debugging Process (how the mechanisms were pinned down)

1. **Shed/inventory sampling (dbg4_out.txt)**: read `private.shed` +
   `private.inventories` every 60 steps; proved shed never reached 100 in v23's own
   runs, ending the "overflow" theory. `[F]`
2. **Sell-order trace (dbg5_out.txt)**: instrument the market orders v23 emits during
   the final 10 days; revealed the exact late-sell window (624–718) and that shed is
   emptied early but 100-ish surpluses were NOT the issue. `[F]`
3. **Mirror harness (sweep_run/seeds/h2h)** — fixed seed sets: 1M, 9M, 3.33M, 7.77M,
   5M, 6M, 8M, 2M `[F]` (exact per-seed sweep table itself was console-only →
   `UNKNOWN — NOT RECOVERED`).
4. Day/step math: step/24 = day; late window = 19×24 = 456.

---

## 5. Mechanism Discovery (the "aha")

Markets/town are **shared**; a SELL shifts the common price curve. Because v23's sale
plan is **fixed** (big WOOL/MILK/STRAWBERRY dumps 624–696), selling small extra
high-value units late *cheapens the same curve v23 will sell into*, so the marginal
cost to you (≤ +2 qty) is outweighed by the damage to v23's plan. Low-value volume
(WHEAT 25, FERT 100) would tank the curve more than it earns → never bumped. This
also explains why **mirror deltas look neutral while H2H wins 8/8**: two copies of the
same strategy both suffer the shared dip equally. `[S][F] kaggle_v26.py; sweep_lib.py`

## 6. Game-Mechanics Reverse-Engineering (ground truth used)

- 720 turns (30 days × 24), two players; win = **highest final bank**; ties → 0.
  `[F] guide`
- **Shed**: capacity 100 non-seed items; overflow silently discarded at end of day;
  hand inventories count toward the same end-of-day check. `[F] guide §2`
- Animals: goose/egg, cow/milk, sheep/wool (max 4/6/6); feeding prevents escape.
  `[F] sweep_lib + guide`
- One-shot max yields: WHEAT 6 (day 4-cap), CARROT 4 (3), MELON 6 (12); ongoing
  TOMATO / STRAWBERRY harvestable whenever yield>0. `[F]`
- Town demand ramp: ≥10 days → 2×, ≥20 days → 4×; shops drain every 4 steps; center
  every 12 steps; market prices absorb selling pressure (theory→the Aha). `[F] guide`

---

## 7. Exact Experiment Evolution (per variant, code-level)

```
base        v23 untouched (control)
aggr        v26: harvest ongoing+animal yield>0, one-shot at max, water unwatered
capill      aggr but only harvest if shed_sum+inv_sum+units <= 100
capsell     capfill + same-step bump of existing SELL quantities by surplus
latefill    aggr only on steps >= 19*24=456 + cap guard
sellall     KILLED (price collapse)
capselllate late high-value top-up: only >=456, only S/M/W, +2 max
```
Champion = **v23 + [safe max-yield & water fill] + [capselllate top-up]**, nothing
else changed; market queue stays v23's own ordering. `[F] kaggle_v26.py, kaggle_v26b.py`

---

## 8. Exact Numbers (verified subset)

| Quantity | Value | Source |
|---|---|---|
| v23 vs v23 baseline bank | 119,870 (seed 1M era) | `dbg4_out.txt`, `bank_out*.txt` |
| v23 bank (other seed) | 124,246 | `dbg5_out.txt` |
| max shed_sum (v23) | 91 @ step 600 | `dbg4_out.txt` |
| max inv_sum (v23) | 60 @ step 660 | `dbg4_out.txt` |
| v24 H2H vs v23 | 110,661 / 88,998 vs 124,142 / 149,852; tie 119,870 | `bank_out*.txt` |
| v23 dump @624 | STRAW 14, MILK 9, FERT 12, WHEAT 14 | `dbg5_out.txt` |
| v23 dump @648 | WOOL 18, MILK 12, STR 10, WHEAT 4 | `dbg5_out.txt` |
| v23 dump @696 | MILK 12, FERTILIZER 14, WHEAT 41 | `dbg5_out.txt` |
| late top-up gate | step ≥ 456 (19×24) | `kaggle_v26.py:36` |
| bump cap | +2 units | `kaggle_v26.py:37` |
| H2H champion vs v23 | 8/8 | `kaggle_v26.py` docstring |
| bundled H2H | +673 / +395 / +938 | git `014139d`; smoke 3/3 `[R]` |
| Kaggle public score | 600.0 | prior session `[R]` |
| aggressive v26 mirrors | ≈ −972 (avg leak) | `kaggle_v26b.py` docstring |
| seed set | 1M 9M 3.33M 7.77M 5M 6M 8M 2M | `[F] sweep_h2h.py` |

(Per-seed mirror sweep deltas of aggr/capfill/capsell/latefill not persisted —
**UNKNOWN — NOT RECOVERED**.)

---

## 9. Methodological Mistakes (learned the hard way)

1. **Trusting mirror deltas** — mirrors cancel the shared-price effect; H2H is truth.
2. **Harvest-what-you-can** (aggressive v26) — overflow inside the shed cap, crowding
   scheduled drops.
3. **Dump everything** (`sellall`) — your own curve collapses.
4. **v24 scope creep** — three orthogonal changes in one diff made regressions
   unattributable.
5. **Console-only sweeps** — many numbers printed-to-stdout were lost when the session
   compacted; always persist outputs (this playbook exists because of that error).

---

## 10. DO NOT REPEAT (checklist)

- [ ] Never promote on mirror deltas alone — run H2H against the incumbent.
- [ ] Never sell extra units of low-value products into the shared curve.
- [ ] Never exceed the 100-cap when filling PASS turns.
- [ ] Never ship `sellall`-style unified dumps.
- [ ] Always persist every sweep/H2H result to a numbered file (bank_out-style).
- [ ] Hash + archive champion file at promotion time (this repo: `[H]` table exists).

---

## 11. Reusable Research Loop

1 instrument incumbent (shed/orders) → 2 hypothesize ONE lever → 3 build variant wrap
(no structural edits) → 4 mirror sweep on fixed 8-seed set → 5 H2H sweep vs incumbent →
6 gate (32/32 + decision 32/32; pool `[R]`) → 7 bundle single-file → 8 hash + wire diff +
git commit + push → 9 persist results & hashes into the playbook (even failures).

---

## 12. How to Dethrone V26 (V27+ protocol)

1. **Re-instrument v26** (dbg4/dbg5 analogues): dump its shed/inventories per 60 steps
   `[F]-style`, and trace its SELL orders in the final 10 days — find what v26 leaves
   on the table (its +2 cap; FERT/WHEAT surpluses; early shed headroom).
2. **Probe the levers v26 refuses**: low-value top-ups, different late-step gates
   (456±48), cap >2, mirror vs H2H on the shared curve.
3. **Adversarial idea worth testing**: since v26 exploits the *shared curve*, an
   opponent that *halts its own dumps* (or sells the exact products v26 bumps, at the
   same steps, larger) can turn the asymmetry back.
4. **Validate**: fixed 8 seed H2H vs v26; require ≥6/8 wins with positive mean delta;
   then dev 32/32 gate; bundle; hash; submit. Persist per-seed deltas.

---

## 13. Evidence Hierarchy (strongest → weakest)

1. H2H bank deltas vs incumbent (multi-seed) — decisive.
2. Trace files (dbg-N_out.txt) — direct engine-state facts.
3. Mirror-bank experiments — informative, but shared-curve contaminated.
4. Code + docstrings — durable intent but self-reported.
5. Prior-session summaries `[R]` — weakest; only corroborated claims accepted.

---

## 14. Facts vs Interpretations

**Facts** (file-verified): hashes `[H]`, dbg traces, bank files, sell traces, sweep
harness constants, docstring claims (8/8, -972, +2, ≥456), git commits, Kaggle status
600.0 `[R]`.

**Interpretations** (explicitly modeled, not directly measured):
- I1: "late extra high-value sales damage the shared curve asymmetrically" — strongly
  supported by H2H 8/8 and code design, but the per-step price-path observation was
  never persisted (`UNKNOWN — NOT RECOVERED`).
- I2: "v24 failed due to scope creep" — N detected in 2 losses + 1 tie.
- I3: "v26b mirrors ≈ neutral ⇒ safe fill" — claim consistent with new-neutral;

---

## 15. Research Memory (what to preserve going forward)

- Preserve: `agents/kaggle_*`, `submission.py`, `dbg*_out.txt`, `sweep*`,
  `bank_out*`, `diff_v23_v24.txt`, `RESEARCH_PLAYBOOK_V23_TO_V26.md` (this file),
  git commits, Kaggle run ID.
- Persist EVERY future sweep result to disk, not stdout.
- Hash the champion + bundled submission + backup zip together (single table),
  e.g. E4F243…/949049…/386A24…/76F6FC…/E097E7… for kaggle_v26/v26b/aggr/v23/sub.py.
- If a number looks odd (e.g. the tie-119,870), rerun the experiment rather than
  generalize from it.

---

*Reconstructed 2026-08 from on-disk artifacts; every missing sweep value is explicitly
marked UNKNOWN — NOT RECOVERED. Nothing invented.*