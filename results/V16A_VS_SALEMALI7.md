# V16a Counter-Preemption vs salemali7 — Gate Report

Date: 2026-08-09
Agents:
- **A (candidate)**: `agents/kaggle_v16a_counterpreempt.py` — V15.5 brain + `_counter_preempt`
  (h=(4,3,2,1) horizon, fires BEFORE opponent's h=3 shift at T−3)
- **B (target)**: `agents/salemali7_3000score.py` — top public agent; preempts own future
  premium sells at T−3
- Regression baseline: `agents/kaggle_champion_v155.py` — current champion (V15.5)

Gate pre-registered per `RESEARCH_RULEBOOK.md` §3: frozen 8-seed family
`1M 9M 3.33M 7.77M 5M 6M 8M 2M`, pass rule **≥ 6/8 wins + positive mean delta**,
extended confirmation at N = 100 preferred.

---

## 0. The Blocker That Was Found & Fixed

V16a's counter crashed at `kaggle_v16a_counterpreempt.py:127` with
`NameError: name '_PREEMPT' is not defined` — the module defines `_PREMIUM`
(line 43) but the loop iterated an undefined `_PREEMPT`. The crash only triggered
when the clone gate passed (cd ≤ 6) **and** a future premium SELL existed within
4 steps. On seed 2000 that first happened at steps 164–167 → `agent()`'s internal
`except` fell back to PASS for 4 steps → farms diverged at step 168 (MELON 9 vs 12,
COOP 4 vs 0, WEED 6 vs 7) → cd = 8+ for the rest of the game → **both** preempts
clone-gated off → SAL swept (Δ −54,400).

**Fix** (one line): `for item in _PREMIUM:` — matches V14 (`kaggle_boat84_v14.py:253`)
and SAL (`salemali7_3000score.py:262`). Traceback captured by `pinpoint_v16_exc3.py`
(agent twin logging `traceback.format_exc()` to a file; stdout-filtered probes were
silent because `agent()` swallows exceptions before outer wrappers see them).

Post-fix seed 2000: V16a **119,971** vs SAL **116,881** (+3,090), farm lockstep
restored (cd = {0: 693, 1: 26}).

---

## 1. Gate: V16a vs salemali7 — frozen 8-seed family (16 games, 2 seats each)

`python tools\diag_bench_seeds.py agents\kaggle_v16a_counterpreempt.py agents\salemali7_3000score.py 1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000 ...`

| Result | Value |
|---|---|
| Games | 16/16 OK, 0 errors |
| Record | **16 W / 0 L / 0 T (100%)** |
| Seed-level | **8 W / 0 L / 0 T** |
| Mean Δ | **+2,361** |
| Median Δ | +2,708 |
| Min / Max Δ | +738 / +3,100 |
| V16a avg / SAL avg | 133,397 / 131,036 |

| seed | swap=0 Δ | swap=1 Δ |
|---|---|---|
| 1000000 | +2,717 | +2,717 |
| 2000000 | +2,586 | +2,586 |
| 3330000 | +3,100 | +3,100 |
| 5000000 | +2,895 | +2,895 |
| 6000000 | +2,700 | +2,700 |
| 7770000 | +738 | +738 |
| 8000000 | +3,057 | +3,057 |
| 9000000 | +1,097 | +1,097 |

**PASS** (≥ 6/8 and positive mean — 8/8, +2,361).

---

## 2. Extended Confirmation: N = 100 (50 fresh seeds × 2 seats, offset 40 — seeds never used in tuning)

`diag_bench_seeds.py` with seeds `2000 + (40+s)*73` for s = 0..49 (4920…8497).

| Result | Value |
|---|---|
| Games | 100/100 OK, 0 errors |
| Record | **100 W / 0 L / 0 T (100%)** |
| Seed-level | **50 W / 0 L / 0 T** |
| Mean Δ | **+2,325** |
| Median Δ | +2,692 |
| Min / Max Δ | +675 / +3,211 |
| V16a avg / SAL avg | 128,490 / 126,165 |

Weakest seeds (still wins): 5504 (+675), 4920 (+810), 5358 (+1,087), 9000000-family 7770000 (+738).

---

## 2.5 Full ladder sweep: V16a vs every predecessor (frozen 8-seed family, legacy interval=12)

| Opponent | Record | Seed-level | Mean Δ | Min / Max |
|---|---|---|---|---|
| **V15.5** (incumbent) | 16W/0L | 8W/0L | **+1,594** | +540 / +2,133 |
| **SAL** (threat) | 16W/0L | 8W/0L | **+2,361** | +738 / +3,100 |
| **V15** | 16W/0L | 8W/0L | **+2,074** | +670 / +2,728 |
| **V14** | 16W/0L | 8W/0L | **+2,368** | +741 / +3,205 |
| **V26** | 16W/0L | 8W/0L | **+3,451** | +2,575 / +5,465 |

The chain holds: V16a retains V15.5's economic strength **and** counters salemali7's
clone-preemption exploit — the clean succession V15 → V15.5 → V16a, with the threat
eliminated and zero regressions anywhere in the ladder.

---

## 2.6 Rebalance regime (`townCenterSellInterval=24`) — frozen 8-seed family

| Opponent | Record | Seed-level | Mean Δ | Min / Max |
|---|---|---|---|---|
| **SAL** (threat) | 16W/0L | 8W/0L | **+2,646** | +1,399 / +3,474 |
| **V15.5** (incumbent) | 16W/0L | 8W/0L | **+1,619** | +868 / +2,371 |

The rebalance gap (rulebook §3.2) is now closed — V16a dominates both the threat and
the incumbent in the rebalance regime as well.

---

## 3. Regression: V16a vs V15.5 (champion) — frozen 8-seed family

`diag_bench_seeds.py agents\kaggle_v16a_counterpreempt.py agents\kaggle_champion_v155.py ...`

| Result | Value |
|---|---|
| Games | 16/16 OK, 0 errors |
| Record | **16 W / 0 L / 0 T (100%)** |
| Seed-level | **8 W / 0 L / 0 T** |
| Mean Δ | **+1,594** |
| Min / Max Δ | +540 / +2,133 |
| V16a avg / V15.5 avg | 132,680 / 131,086 |

**No regression** — V16a beats the incumbent on the same family (counter adds
value; the clone gate keeps non-clone behavior identical to V15.5).

---

## 4. Mechanism Evidence (seed 2000 clean trace, `clean_v16fix_A/B.txt`)

- cd (clone distance) distribution: **{0: 693, 1: 26}** — farm lockstep with SAL,
  clone gate open all game (this is the clone-war regime).
- Fires: **V16a 45×**, SAL **39×**.
- Timing: V16a lands at **T−4** one step before SAL's **T−3** shift, e.g. tape SELL at
  step 241 → V16a sells at 237 (MILK 4), SAL at 238 (MILK 4); same at 333/334,
  428/429, 466/467, 595/596, 611/612, 618/619, 644/645, 658/659.
- Post-fix steps 164–167 execute normal actions (CARE/WATER/SOUTH, BUY_PRODUCT
  WHEAT 1) — no PASS fallback, no crash (`pin2_out.txt`).
- Mirror self-play (V16a vs V16a) was NOT part of this gate — H2H only per rulebook §6.

---

## 5. Promotion Checklist (rulebook §3.5 — COMPLETE, promoted 2026-08-09)

- [x] **Hash** the candidate: sha256 of `agents/kaggle_v16a_counterpreempt.py` =
      `02C3B2301538563DC1F7A7811FA47189103143F6D3385FD3AFD96CE8D929ACA8`
      (old champion V155 = `93CA298E0018FFB708312A8F457F3F6B65475FF2A751F659D241A7539FC466FC`)
- [x] **Wire-diff** vs old champion `kaggle_champion_v155.py`: V16a `agent()` = V15.5
      chain with exactly ONE runtime change — `_preempt_shift` → `_counter_preempt`
      (line 259 vs V155 line 222); all other runtime helpers identical.
- [x] **Archive** old champion as `archive\archive_main_v155.py` (10,691 bytes)
- [x] **Boundary banner** in ledger (H8 row — verdict "CONFIRMED — gate passed, ladder
      clean, rebalance closed; promoted to incumbent")
- [x] **Rebuild submission** (`build_v16_submission.py` → `submission.py`, 28,920 bytes;
      V14 embedded inline, same pattern as V15.5 build)
- [x] **Smoke test** `submission.py` vs V15.5 on frozen 8-seed family: **16W/0L,
      Mean Δ +1,594** (min +540, max +2,133) — reproduces the regression gate exactly
- [x] **Rebalance regime** (`interval=24`): vs SAL **16W/0L +2,646**; vs V15.5
      **16W/0L +1,619** (rulebook §3.2 gap closed)

---

## 6. Artifacts

- Gate results: `%TEMP%\opencode\v16_sal_gate8.txt`, `v16_v155_reg8.txt`, `v16_sal_conf100.txt`
- Traces: `%TEMP%\opencode\clean_v16fix_A.txt`, `clean_v16fix_B.txt`, `pin2_out.txt`
- Runner: `tools/diag_bench_seeds.py` (seed-list variant of `diag_bench.py`)
- Ledger: `RESEARCH_PLAYBOOK_V23_TO_V26.md` §2 — H8 row added

---

## 7. Engine Version Discovery & Re-Verification (2026-08-09, kaggle-environments 1.32.6)

Per `notebooks/dariushafshar-agent-tuned-for-a-dead-game.ipynb`: the scoring engine
is **1.32.6**, which changed the town-demand model mid-competition. We were on
**1.32.5** (one release behind; Kaggle default image ships 1.29.3 — seven behind).

Changes (1.32.5 → 1.32.6): `townCenterSellInterval` default 12→24; town-centre
multiplier schedule (1x→2x→4x) **deleted** (flat 1x); shops sampled **with
replacement** (was without; `MAX_SHOP_INSTANCES = 8`). Net: town centre consumes
1×/day per product all season (was up to 8×/day late); melon demand fell ~88%.
Our earlier `interval=24` tests on 1.32.5 did NOT capture the multiplier/shop
changes — they were re-run on the real engine.

**Re-verification on 1.32.6 (interval=24, engine default), all 16W/0L:**

| Opponent | Games | Mean Δ | Min | Max |
|---|---|---|---|---|
| kathimunishwar (ground truth) — gate | 16 | +2,003 | +484 | +3,238 |
| kathimunishwar — N=100 fresh seeds | 200 | +1,665 | +92 | +3,385 |
| V15.5 (old champion) | 16 | +1,134 | +380 | +2,135 |
| V15 | 16 | +1,754 | +450 | +2,780 |
| V14 | 16 | +1,886 | +438 | +3,263 |
| V26 | 16 | +3,039 | +1,496 | +3,992 |

Verdict: **all gates still PASS on the real scoring engine**; reconstruction
fidelity preserved (16/16 ties vs ground truth on 1.32.6). Absolute scores ~33%
lower (avg ~88-89K vs ~133K) — town centre drains less — but V16a's relative
dominance is unchanged. Evidence files:
`results/v16a_vs_kathimunishwar_engine1326_gate24.txt`,
`results/v16a_vs_kathimunishwar_engine1326_conf100.txt`,
`results/v16a_vs_v155_engine1326_reg24.txt`,
`results/v16a_vs_v15_engine1326.txt`, `results/v16a_vs_v14_engine1326.txt`,
`results/v16a_vs_v26_engine1326.txt`,
`results/recon_vs_groundtruth_engine1326_16ties.txt`.
