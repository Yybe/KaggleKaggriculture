# LEANTOMATO13 V1 — VERDICT

**Variant-1 on the LEAN spine. One DECEM-derived lever. Loss-first.**

```
===================================================================================================
LEANTOMATO13 V1 -- MEASURED NEGATIVE.  The layer is LIVE and it LOSES to its own parent.
===================================================================================================
  ESTIMATOR: mirror (SELF-FIGHT -- candidate and parent share a spine, H-081)
  pin       kaggle_environments 1.32.7 | townCenterSellInterval 24 | episodeSteps 720
  band      B5 = 61250000 + 441*i ... 61250000 + 4441*i, i=0..19  span [61250000, 61334379]
            unseen by both arms; repo-wide literal scan 7,576 files / 5,444.7 MB, 0 hits
  arms      CAND   agents/lean_tomato13_v1.py  sha256 e9986953f4b537da907c2da870771b4b7f19bbc865da4d0f80a968e96543e5b2
            PARENT lean_s336.py                sha256 bad988901cad5185d7af87844771533fe1d047feace50b708abdb6ac13ce387a
  games     40 = 20 fresh worlds x 2 seat orders, 5 chunks of 8
===================================================================================================
```

## 1. The verdict, number-first

| | value |
|---|---|
| **pooled mean paired delta** | **−133.2** |
| median | −47.0 |
| worst world | **−562** (seed 61276646) |
| best world | +2 (seed 61303292) |
| W / L / T | **1 / 11 / 8** |
| favours | **1 / 20** |
| exact two-sided sign test | **p = 0.00684** (on the 12 non-tied worlds) |
| bootstrap 90% CI on the pooled mean | **[−199.8, −73.8]** — entirely below zero |
| worlds where the layer committed | **12 of 20** (13 commits, 179 CARROT units re-timed) |
| worlds where the two banks differ | **12 of 20** |
| worlds where the two seats returned the same bank | **20 of 20** (mirror collapse) |
| candidate mean bank / parent mean bank | 102,634 / 102,768 (reported only, never the selector) |

**Pre-registered decision rule (the tightened bar):**

| clause | result |
|---|---|
| D1 pooled mean paired delta > 0 | **FALSE** (−133.2) |
| D2 no world worse than −2,500 | TRUE (worst −562) |
| D3 no negative lineage | **VACUOUS** — one lineage, the candidate's own parent |
| D4 commits>0 and actions_changed>0 and banks differ | TRUE (13 / 13 / 12) |
| attribution: every delta traces to a commit | TRUE (8 of 8 abstaining worlds are exact ties) |

**TIGHTENED BAR: NOT MET (D1 fails).** This is *not* a NO-OP and *not* a tie. The graft is provably
live, and it is provably, significantly **worse** than the parent it wraps.

Per `Kaggriculture.md:1240-1241` the only permitted phrasing: **the candidate breaks the tie with
its parent by −133.2** (i.e. it loses the tie it was built to break). Nothing is promoted. No V4
field gate was run. Nothing was submitted.

## 2. What the lever was, and why it was the right one to build

**MECHANISM (one, as pre-registered).** In DECEM's terminal CARROT window — days 28–29, steps
648–719 — whenever the shared shed holds CARROT that the parent's own market orders for that same
step would not liquidate in full, prepend exactly one `['SELL','CARROT', n]` at **market-queue
position 0**, `n` = the un-liquidated remainder.

Source: DECEM `21ff37be` (`agents/live_replay/opp_DECEM_21ff37be.py`, episode-112931179) drips its
terminal CARROT across **21 orders / 86 units at s675–s719**. LEAN block-dumps it. The layer moves
the un-liquidated remainder to the front of the shared queue.

**Why this candidate and not the other two — killed by measurement, not by assertion:**

| candidate | verdict | the number that killed it |
|---|---|---|
| **WOOL day-7 burst discipline** | **REJECTED — measured inert** | On lean's tape, over t=144…167 the shed holds **WOOL = 0** for 7 steps, **2** at t=151, **0** for 16 steps. The parent already issues SELL WOOL 6/4/2 at t=149/150/151. Admissible burst headroom = **2 units, once, already covered**. Max shed WOOL over the whole 720-step game = 11. Independently confirmed dead on the cha22 spine: `E262_TOMATO13_20260929.md:165-171` — "shed['WOOL'] == 0 across both DECEM windows … its counter reads **0 on all 40 rows**", because DECEM's 18 units are the delivery of 3 SHEEP placed at s3 — a *herd* event, not a sell event. Rebuilding a sheep opening on lean would be a second mechanism. |
| **pre-carrot goose/coop batch** | **REJECTED — no surface, forbidden class** | DECEM builds COOP at s227/232/237/257/258/278 and picks up geese s225–274. On lean, over t=224…278 (220 observed steps) **`n_owned_empty = 0` for t=224…~274** — the board is full and the herd is already built (COOP+GOOSE present at t=224, e.g. `(5,3,'COOP','GOOSE')`). **108 of 220 steps have no hand standing on any owned-empty tile**, so the only remaining sites need a MOVE — exactly the walk commandeering this task forbids, and which the closed cha22 axis established as refuted. |
| **carrot-terminal overlap** | **SELECTED** | The only candidate with a non-zero admissible firing surface that is expressible with **zero unit actions** (so it cannot walk-commandeer at all). Shed CARROT appears at exactly 3 steps of t=648…719 (30 / 22 / 35) and the parent's next-step order liquidates 100% of it, so the un-liquidated remainder is real, small, and measurable. |

## 3. The two decisive pieces of mechanism evidence

**3a. The CARROT price is FLAT across the shift, so the re-timing buys nothing.** (`_mech.txt`)

```
seed 61276646   arm=CAND                          arm=PARENT
  step   px  shed  our CARROT SELL orders           step   px  shed  our CARROT SELL orders
  672  54.0    18  []                               672  54.0    18  []
  673  54.0    18  [[SELL CARROT 16],[SELL CARROT 2]] 673  54.0    18  [[SELL CARROT 2]]
  681  52.0     0  [[SELL CARROT 3]]                674  54.0    16  [[SELL CARROT 16]]
  696  52.0    33  []                               683  52.0     0  [[SELL CARROT 3]]
  697  52.0    33  [[SELL CARROT 33]]               696  52.0    33  []
```

The parent sells **2 at t=673 then 16 at t=674**; the layer collapses both into t=673. The price is
**54.0 at 672, 54.0 at 673, 54.0 at 674** — identical. There is no price window to capture. Same on
seed 61316615 (42.0 / 42.0 / 42.0).

**3b. The cost is real and it is the shared curve.** On a shared market the units are a common
resource. LEAN's own block dump is already at the front of a **declining** segment (52 → 52 → …, and
64 → 59 → 53 by t=717 on the S1 world). Collapsing a 2-then-16 sequence into one 18-unit step taps
the curve harder for every remaining CARROT on the board — ours and the opponent's. That is
`H-067` re-confirmed on a new construction: *a sell-side break must conserve total volume, and
re-timing volume in a shared market transfers value to the opponent.*

**3c. Constraint C3 held at the order level but NOT at the realised-volume level — and it still lost.**
The layer only inserts at index 0 and never edits a parent order (AST-verified). But because the shed
is capped at 100 and the shed ran at 91–92/100 on the day boundaries, selling 16 units a step early
**frees 16 slots**, so 3 more CARROT and 1 more FERTILIZER got delivered instead of being discarded:

```
seed 61276646   item        cand  parent  delta
                CARROT        119     116   +3   <-- realised volume CHANGED
                FERTILIZER    349     348   +1   <-- realised volume CHANGED
                MELON/MILK/STRAWBERRY/WHEAT/WOOL  identical
```

The candidate sold **4 more units** and still banked **less** (−297 in this diagnostic pairing). The
shed-capacity side-effect is an accidental second mechanism; it does not rescue the sign.

## 4. V0 / V1 / V2 / V3 evidence

| stage | file | result |
|---|---|---|
| **V0 pin** | `identity.json` → `v0` | **PASS** — `kaggle_environments 1.32.7`, hinge shapes `CARROT/TOMATO/EGG`, T = 450/200/332, `townCenterSellInterval 24`, `episodeSteps 720`. Re-asserted in-log before every chunk (`_c0…_c4.txt`, `PIN_ASSERT V3/chunkN` × 3 lines each). `tools/engine_assert.py` → `RESULT=PASS`. |
| **V1 smoke** | `smoke.json` | **PASS** — 720 turns executed (step indices 0…719), final status `['DONE','DONE']`, **0 errors**, candidate active 715/719 steps, control game (parent vs PASS on the same world) also 720 turns `DONE`. |
| **V2 identity** | `identity.json` | **PASS** — candidate `e9986953…`, 1,201,858 B = parent `1,196,079 B` **+5,779 B**; **parent prefix byte-identical**; parent `bad9889…`; `^def` diff: parent 331 top-level defs → candidate 334, **ADDED `_lt13_key`, `_lt13_drip`, `lean_tomato13_v1_agent`**, **REMOVED none**; rebound `agent`, `kaggle_submission_agent`; `load_agent(path).__name__ == kaggle_submission_agent.__name__ == lean_tomato13_v1_agent` (H-081 entry trap checked and clear). |
| **V3 census** | `games_chunk00…04.jsonl`, `score_v3.json` | 40/40 rows `OK`, 5 distinct chunks, seeds == pre-registered band, both seats every world, both sha256 constant on every row, all 720 turns, all `DONE`, `errors_total = 0`. |

**Constraint proofs (AST over the appended layer only, V2):**

| constraint | proof |
|---|---|
| C1 no land buys | `BUY_LAND` literal in layer: **NONE**; order verbs constructed: **`['SELL']` only** |
| C2 no walk commandeering | `NORTH/SOUTH/EAST/WEST` literals: **NONE**; `dict()` keys written: **`['market']`**; unit-action writes (`farmer`/`hands`): **NONE** |
| C3 no parent-quantity edits | insertion at index 0 only; realised volume **+3 CARROT / +1 FERT** via shed-capacity side-effect (§3c) |
| C4 drip at position 0 | the inserted order is always `new_orders = [[SELL, CARROT, n]] + parent_orders` |
| C5 crew top-up | `HIRE` literal in layer: **NONE** — the "≥ 10 unplanted owned-empty targets" rule is vacuously satisfied |

**Mutation counters** (`lean_tomato13_v1_agent.telemetry` → `_LT13_REPORT`): `commits`,
`units_dripped`, `actions_changed`, `errors`, plus the abstention ledger
`abstain_no_stock` / `abstain_parent_covers` / `abstain_queue_full` and a 64-entry `commit_log`.
V3 totals: **commits 13, units_dripped 179, actions_changed 13, errors 0** — all **> 0**, so the
NO-OP rule did not fire and the measured-negative path applies.

**Attribution is clean.** 0 worlds where `(commits>0)` disagrees with `(delta != 0)`; **8 of 8**
abstaining worlds are **exact** bank ties. So the layer is behaviourally inert when it abstains and
every one of the 12 bank differences is caused by the layer and by nothing else. The layer is not
inert, and it is not a measurement artefact.

### Instrument validity (checked against the repo's own known counter failure mode)

`knowledge/REJECTED_HYPOTHESES.md` H-106 carries a live instrument warning from another session:
*"the first probe read `agent.telemetry` and reported zero fires on 16/16 worlds because a later
appended layer rebinds that attribute — the counters must be read from the module-level dict
(`mod._V219_REPORT`). 'Telemetry all zero' is an unverified measurement until a money difference
confirms it."* That trap does not apply here, and it was checked explicitly rather than assumed:

```
caller telemetry IS the module-level _LT13_REPORT dict : True
parent chain _LT13_PARENT.__name__                     : step1009_step1008_fortyfirst_final_fixedsell_closure_agent
parent IS the step1009 EOF def of lean_s336            : True
no later layer rebinds .telemetry after mine            : True
same telemetry object survives a step-0 reset          : True   (reset mutates in place)
```

And the second half of the warning's own test is satisfied: the counters are corroborated by
**money** — the 12 worlds with bank differences are exactly the 12 worlds with `commits > 0`, and the
8 worlds with `commits == 0` are exact ties. The census reads the counters from the callable the
worker itself loaded (`max_tasks_per_child=1`, one load per game), so there is no cross-game bleed.

## 5. Decider sanity (reproduced before the build)

`BASE_GATE_20260930/VERDICT.md` established `lean_s336 > cha22_champion` at **+1,433.6 mean, 8W/0L**
over 8 unseen worlds. Re-run first, on a fresh band `S1 = 61550000, 61553217`, paired and
seat-collapsed (`sanity_verdict.json`):

```
world 61550000  lean=[74142, 74142]  cha22=[74626, 74626]  paired delta  -484   L
world 61553217  lean=[101394,101514] cha22=[100934,100812] paired delta  +581   W
pooled mean +48.5     W/L 1/1     worlds where the 2 seats disagreed: 1 of 2
```

**PASS under the operator's tightened bar** (pooled mean > 0 = +48.5 > 0; worst world −484 > −2,500).
**Disclosed honestly: a strict "positive on both worlds" reading FAILS** — world 61550000 is −484.
The reproduction is also far weaker than the original (pooled +48.5, 1W/1L, vs +1,433.6, 8W/0L): two
worlds is an underpowered replication, and the effect on this pair is at the edge of resolution.
The *ordering* (lean above cha22) reproduces; the *magnitude* does not.

## 6. Corrections to the brief's DECEM DNA (measured from the tape, not quoted)

Three of the figures in the task brief do not match the `21ff37be` tape. Recorded so they are not
re-imported:

| brief said | tape actually says |
|---|---|
| goose `s224-273` | **s225–274** (PICKUP GOOSE at 225, 229, 233, 252, 255, 274). The literals `s224`/`s273` appear nowhere. |
| crew **13** from d12 | tape `max_hands = 12`, 311 total hires, 11/day from d12. **13 is our own E224 design target, not DECEM's number.** |
| **94.87%** active | tape measures **98.47%** (11 idle steps of 720). `94.87` appears in no DECEM artifact. |

Confirmed as stated: WOOL 18-unit day-6 burst (s148/150/151 × 6; sq 200 → 181, floors at +59 glut);
COOP **s227–278** exact; CARROT first plant **s260** (last s662, n=77); d28–29 terminal dump present
in the tape (86 units, 21 orders) but the *field* data says it is not DECEM's signature — DECEM's
peak days are mid-season, 34 of 98 episodes peak in d27–29
(`results/p19_release_hist/REPORT.md:261-266`).

## 7. What this closes, and what it does not

**Closed for this construction:** DECEM's d28–29 CARROT terminal-overlap discipline does **not**
transfer to the LEAN spine. The reason is structural and is now measured, not guessed: on LEAN's
tape the terminal CARROT is (a) already block-dumped by the parent at the first step it exists, and
(b) already sitting on a **flat** price across the only step the layer can reach, inside a
**declining** segment. There is no front-run to win. Any re-timing inside a shared, declining,
already-front-loaded dump is a pure transfer to the opponent.

**Not closed, not claimed:** nothing about CARROT volume, capacity or price on LEAN. The one
accidental finding worth carrying forward is §3c — **the shed runs at 91–92/100 on the day-28/29
boundaries, so a single early sell frees real capacity and lets 3–4 otherwise-discarded units
through.** That is a capacity mechanism, not a sell-timing mechanism, and it is a *different* lever;
it is recorded here, not built.

**Still open on this spine** (not attempted, would each be a separate one-lever cycle with its own
pre-registration): the shed-capacity headroom above; the DECEM land cadence (BUY_LAND s150/218/254 —
**explicitly out of scope here**, the task forbids land buys); DECEM's crew-13 target (lean already
runs 9–13 hands and reaches 13 by d27); DECEM's tomato window (lean's tape carries **zero** TOMATO
plants in the S1 census — a production lever, therefore a walk-commandeering lever, therefore out of
scope here).

## 8. Compliance

- `lean_s336.py`, every `cha22*` file, `submission.py`, every ledger, `experiments/seeds.json` and the
  panel: **not edited**. The build appends a new file and asserts the parent prefix is byte-identical.
- Built on the **LEAN** spine as instructed. The cha22-tomato axis stays **CLOSED** (E262 −49,194 /
  E263 −10,710 / E267 −2,052, three consecutive ≤ 0) and was not re-opened.
- **No V4 gate. Nothing submitted. No live score used as evidence.**
- **40 games / 20 distinct worlds**, at the ≤ 40 budget. Both seat orders every world.
- **Exactly one lever.** One window, one stock test, one remainder, one insertion site.
- No `knowledge/REJECTED_HYPOTHESES.md` entry was written — editing ledgers was forbidden. **A ledger
  entry recording this construction and its mechanism is owed** (§3a/§3b above) and should be filed by
  whoever owns that file, so the DECEM CARROT terminal-overlap idea is not re-imported next session.
- **Observed, not caused by this work:** `knowledge/REJECTED_HYPOTHESES.md` grew 148,911 → 154,114 B
  (368 added lines) at 06:19 during this session. The added entries are **H-105 / H-106**, a tomato-lane
  price-floor construction from a *different* session, and contain no reference to LEANTOMATO13. This
  session issued no write to that path; the diff is recorded here only so it is not misattributed.
  Integrity of the protected set is otherwise confirmed by hash and mtime:
  `lean_s336.py` = `bad9889…` (unchanged, and untracked in git so the hash is the proof),
  `submission.py` = `787244ef…` (mtime 2026-09-29 16:17), `experiments/seeds.json` = `ee90c036…`
  (mtime 02:25), `agents/cha22_champion.py` = `a0031c0d…` (mtime 2026-09-27) — all pre-date this
  session's first write. The only new paths this session created are
  `agents/lean_tomato13_v1.py`, `LEAN_TOMATO13_V1_REPORT.md` and `LEAN_TOMATO13_V1_20260930/`
  (all three show as `??` untracked in `git status`).

### Artefacts

```
agents/lean_tomato13_v1.py                     candidate, 1,201,858 B, sha256 e9986953…
LEAN_TOMATO13_V1_20260930/
  PRE_REGISTRATION.md        written BEFORE the build and before any census-band game
  bands.json                 S1 = 61550000 + 3217i (2) · B5 = 61250000 + 4441i (20)
  band_check.py  /  _bandcheck output       collision proof: 7,576 files / 5,444.7 MB, 0 hits
  sanity.jsonl / sanity_verdict.json         decider sanity, 4 games
  tape_census_seed*.jsonl / _probe.txt       lever-selection census (4 games, band S1)
  identity.json                              V0 pin + V2 identity + AST proofs
  smoke.json                                 V1 smoke + replay-fidelity control
  games_chunk00..04.jsonl                    V3 raw, 40 rows, both sha256 per row
  score_v3.json                              V3 scored, pre-registered estimator
  mechanism.json / _mech.txt                 C3 volume check + price-flat mechanism
  _c0.._c4.txt                               per-chunk in-log PIN_ASSERT + PROGRESS lines
```
