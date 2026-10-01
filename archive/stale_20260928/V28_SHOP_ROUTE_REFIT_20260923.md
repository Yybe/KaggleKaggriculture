# V28 — Is the shop-composition → route table still fitted to the chassis that runs it?

Date: 2026-09-23 · Experiment: V28 T1–T4 · Owner: this file's author only
Parent/champion under test: `agents/pub_v57_apex_v11_dump.py` (Apex **V11**, 7,041 lines, 1,076,248 B)
Engine: `kaggle-environments 1.32.7`, `episodeSteps=720`, `townCenterSellInterval=24`, 2 players, score = final money.
Interpreter: `WybeV2/rank_env/Scripts/python.exe`.

**Question.** The champion's map choice is a lookup table keyed on the two shops that unlock at
day 6 (`state['route'] = _R108_SHOP_ROUTES.get(shops, 100)`, then `_V92_TABLE`, then a forced
route 2 at day 27). That table was fitted on an older chassis. Nobody has re-measured it on the
spine that actually runs it. This experiment re-derives the whole space from scratch on the
**current** V11 spine and ships a re-fit only if it pays.

**Verdict:** _pending T2/T3 — see §3._

---

## 0. Mechanism under test (read from the spine, verbatim anchors)

`agents/pub_v57_apex_v11_dump.py`:

| symbol | line | what it is |
|---|---|---|
| `make_agent(routes, router, **settings)` | :910 | tape replayer; stores `self.router` at :418, calls it every step at :469 |
| `_ROUTES` | :948 | **41** route tapes (ids 0–12 and 100–128 except 102), 719 steps each |
| `_R108_SHOP_ROUTES` | :949 | 64 **ordered** shop-pair keys → route |
| `_R110_OLD_SHOPS` | :956 | 64 keys, only consulted when `YARN_STORE` is in the pair |
| `_V92_TABLE` | :958 | 15 keys, every ordered YARN pair → route 9 |
| `_V93_ROUTE_BY_RIVAL` | :960 | `{(229.0, 9989): 128}` — rival-state override |
| `_router` | :961–980 | step 2 samples rival `(money, WHEAT)`; step ≥144 latches shops and picks the route; step ≥648 forces route 2 |
| `_IMPL=make_agent(...)` | :986 | the live chassis the rest of the file layers on top of |

Route selection only affects steps 144–647 (**504 steps**, verified: `steps_forced=504` in every
graft game and `forced2_at=648` in 128/128 census seats), so this axis is one map choice per game.

## 1. T1 — the space as it actually occurs (64 worlds, no forcing)

`tools/probe_v28_router.py` wraps the **shipped** router (`chassis.router = wrapper`, behaviour
identical) and logs the day-6 latch on 64 self-play worlds: `SEEDS_R1` (8) + `SEEDS_R2` (8) +
`SEEDS_FRESH` (16) + `SEEDS_T5` (32). Raw: `results/v28/t1_router_census.jsonl`, summary
`results/v28/t1_summary.json`, table analysis `results/v28/shipped_table_analysis.json`.

Exactly two shops are ever unlocked at step 144 (`town_shops_all` length 2 in 128/128 seats), so
the key space is the ordered pair, and the draw is a world property (identical for both seats).

| measure | value |
|---|---|
| worlds | 64 |
| distinct **ordered** pairs observed | **42** |
| distinct **unordered** pairs observed | **28** |
| unordered pairs that occur in **both** orders | **14** (covering **43/64 = 67%** of worlds) |
| YARN worlds | 17 (R1 2, R2 2, FRESH 3, T5 10) = 27% |
| route the shipped table picks | 105 ×21, 9 ×17, 121 ×4, 107 ×4, 108 ×3, 104 ×3, 117 ×2, 101 ×2, 103 ×2, then 116/112/106/113/123/120 ×1 |
| routes reachable from the table | **20 of 41**: 9, 101, 103–108, 110–113, 116–118, 120–124 |
| routes the table can **never** pick | 19: 1, 3–8, 10–12, 100, 109, 114, 115, 119, 125–128 |

### 1.1 The hypothesised YARN fall-through bug is NOT real — no defect to report first

`_V92_TABLE` carries **all 15** ordered YARN keys and maps every one of them to route 9, so a
leading `YARN_STORE` cannot fall through to route 0. Empirically 17/17 YARN worlds latched
route 9. `state['route']` is never left at its 0 default by the YARN branch. **Closed.**

Dead code found instead (three branches that can never fire, worth knowing before a re-fit):
`_R110_OLD_SHOPS` (64 keys) is only consulted for YARN pairs, and every YARN pair is then
overwritten by `_V92_TABLE` → the whole 64-key dict is unreachable; the `100` default is
unreachable for non-YARN pairs *in observed worlds*; `_V93_ROUTE_BY_RIVAL` never matched once in
64 worlds (`rival_hit` false in 64/64, the rival `(money=229.0, WHEAT=9989)` state it wants
requires the opponent to be a different agent).

### 1.2 A real *design* defect: the table keys on an order that carries no signal

`_R108_SHOP_ROUTES` is order-**sensitive**: 15 of the 36 unordered pairs in the tables resolve to
two different routes depending on which shop the engine lists first, e.g.

```
BAKERY|BRUNCH_SPOT -> 103     BRUNCH_SPOT|BAKERY -> 105
BAKERY|PIZZA_SHOP -> 107      PIZZA_SHOP|BAKERY  -> 120
BRUNCH_SPOT|SMOOTHIE_SHOP -> 105   SMOOTHIE_SHOP|BRUNCH_SPOT -> 121
```

and 9 of those 15 classes **occur in both orders across only 64 worlds**
(`order_sensitive_AND_seen_both_ways` in `results/v28/t1_summary.json`). Two worlds with the same
*economics* (same two shops unlocked) therefore get two different maps, chosen by a list ordering
that is not part of the game state the agent reasons about. That is textbook noise-fitting: the
table's 64 keys describe ~28–36 real classes at best, and per-class sample sizes in the wild are
1–3 worlds. A re-fit must therefore be **hierarchical** (ordered pair → unordered pair → YARN/other
regime → keep shipped) rather than another 64-key dict.

## 2. T2 — oracle upper bound on the current chassis

Method (`tools/sweep_v28_routes.py`): candidate = the shipped champion with **one attribute
rebound** (`_IMPL.chassis.router`), so what plays is byte-for-byte V11 except the day-6 route
choice; opponent = unmodified V11. Forced skeleton keeps the shipped timing exactly:
step <144 → 0, 144–647 → forced rid, ≥648 → 2. Every one of the 41 tapes is forced on every one
of the 16 fit-bank worlds (`SEEDS_R1`+`SEEDS_R2`), **both seats**, = 1,344 games + controls.

Cell = candidate bank − opponent bank in the same game, so a forced route the table already picks
reads as an **exact 0.0 tie** and the `CTRL` cell (V11 vs V11) reads as 0.0 mean delta; a null
therefore reports as a null.

### 2.1 Three protocol facts the first run had to be restarted for

* **An instrumented router must wrap the shipped one, not replace it.** The first version of
  `make_forced_router` returned the forced id and kept only the `day6`/`day27` flags it needed.
  Spine `:1046` (`_shadow_terminal`) gates a terminal planner layer on
  `state.get('route')==2` at step 711, and `_router` also maintains `state['rkey']` (step 2) and
  `state['expert']`. A router that merely *returns* 2 without assigning `state['route']=2`
  silently switches that layer off, so the cell would measure two changes at once. Every sweep and
  graft router now calls the shipped router first and overrides only
  `state['route']` for steps 144–647. 458 games measured with the old instrument were deleted and
  are being re-run.
* **Inertness is now proven, not assumed.** `results/v28/t2_fidelity_check.jsonl`: forcing the
  route the table already picks (route 9 on the four YARN worlds) reproduces the control's two
  banks **exactly in 8/8 cells**, e.g. seed 5550000 → (87,014 / 87,303) for both the forced-9 cell
  and the V11-vs-V11 control. The instrument adds no measurement noise.
* **Self-play is not symmetric between seats.** Seed 5550000 pays seat 0 = 87,014 and seat 1 =
  87,303 (seed 1111111: 110,079 / 110,145), so a per-game delta can be ±289 while the agent is
  literally the same code. Both seats are therefore kept and **averaged per world** before any
  W/L/T or sign test — that average is exactly 0.0 for the control, which cancels the first-mover
  asymmetry instead of pretending it away. This is also the convention of the house gate
  `tools/test_candidate_breakthrough.eval_h2h:43-46` (mean over seats per seed), so the numbers
  here stay comparable with earlier verdicts.
* **Crash resilience was required.** The first sweep run died at 25/672 with
  `BrokenProcessPool` (shared box, ~3.5 GB free while another agent held 4 GB). The driver now
  runs one fresh pool per route, requeues what a broken pool lost, and steps down workers
  automatically; the 25 lost games were recovered from disk.

### 2.2 Scale reference (needed to read any gap)

Mean V11 bank on this bank ≈ 89–99 k/game; the measured overlay ceiling on this spine is
±0.35% ≈ **±350/game**. So the resolution floor of this experiment is ~350 and any claimed win
must clear it.

T1's independent measurements reproduce the two structural facts previously recorded for this
chassis (`TAPES_ARE_THE_STRATEGY_20260923.md`): 20 selectable routes (there: "21 of 41 never
selectable", counting route 0 and route 2, which the day-6 branch cannot reach either), and route
105 as the modal pick (21/64 worlds). That agreement is a useful cross-check on the probe, not new
evidence.

### 2.3 The 41 tapes are 38 strategies (multiple-comparison inflation is real but bounded)

`results/v28/tape_clusters.json` — MD5 of each tape's steps 144–647 (the only window this axis
controls): 38 distinct signatures over 41 tapes; exact duplicates 101≡119, 105≡125, 109≡127.
Behaviourally the collapse is bigger than the bytes suggest: routes 0 and 2 are distinct tapes but
their 16-world forced deltas correlate at **+0.99** (per-world difference never exceeds 768), and
1 and 3 correlate at +0.95. So a max-over-41 oracle is roughly a max-over-38 draw — inflated, which
is why the honest number in §2.4 is the LOSO fit and not the per-world oracle.

_T2 oracle arithmetic: pending the 1,344-game sweep._

### 2.4 Relationship to the E96 refutation (why this is not a re-run of a dead test)

Memory `e96-router-portfolio-optimal` refuted route **forcing** on the older E94 spine: g8 (force
101 in non-YARN worlds) = 3 seed-level losses against 3 wins; g9 (force 100 in YARN worlds) =
−35,436/−25,645. That test differed in three ways that matter: it changed the route for an entire
regime on **one** hand-picked target route, on a chassis that no longer exists, and it had no
no-change control. Here every one of the 41 tapes is forced on every world on the **current V11
chassis**, the candidate's own table is the control (delta 0.0 by construction), and the ship
decision is made by an out-of-sample sign test, not by a pooled mean.

## 3. T3 — out-of-sample gate for the frozen fit

_pre-registered before any test world was played: fit on `SEEDS_R1+SEEDS_R2` (16 worlds) only;
report on `SEEDS_FRESH` (16) and `SEEDS_T5` (32, `range(60000000, 60032000, 1000)`, asserted
disjoint from the fit bank inside `write_fitted_table()`); one record per world with both seats
averaged; exact two-sided sign test over the non-tie worlds; a candidate whose sign test is not
informative is **PARITY**, not a win._

**Structural limit found while the sweep ran.** With 16 fit worlds the class support is tiny: the
16 worlds realise 15 distinct ordered pairs and ~12 unordered pairs, i.e. **no** ordered or
unordered pair class reaches the pre-registered minimum support of 3 except by luck — the only
classes with n≥3 are the two regimes (YARN ≈ 4 worlds, other ≈ 12). So a 16-world bank can only
ever answer the coarse question "is there one better tape for YARN worlds / for non-YARN worlds";
it cannot re-fit the 64-key table the champion ships. The per-world support census is printed by
`--analyze` under "class support".

_T3 numbers: pending._

## 4. T4 — production graft

`tools/build_v57_apex_v28_fitted.py` produces `agents/pub_v57_apex_v28_fitted.py`: the spine copied
byte-identical plus one appended layer that rebinds `_IMPL.chassis.router` to a wrapper of the
shipped router (`_V28_SHIPPED_ROUTER`), resolving the day-6 tape through the frozen rule chain
`P → U → R → shipped pick`, with TELE counters `_V28_FIRE` (`latches`, `steps_forced`,
`differs_from_table`, `rule_P/U/R/none`) and `_V28_SHOP_LATCHES`.

Rule 5 proofs implemented and (with a synthetic table, to prove the harness before the real fit
lands) all passing:

| proof | mechanism | selftest result |
|---|---|---|
| (a) parent intact | 5 anchor symbols (`def make_agent(`, `def _router(observation,step,state):`, `_IMPL=make_agent(...)`, `\nagent = v57_apex_v11_dump_agent`, `\nkaggle_submission_agent = ...`) each count 1 in base and in output; base is a byte prefix | PASS |
| (b) layer symbols new | 12 layer symbols (`_V28_PARENT`, `_V28_SHIPPED_ROUTER`, `_V28_TABLE`, `_V28_FIRE`, `_V28_SHOP_LATCHES`, `_V28_META`, `_v28_fit_pick`, `_v28_router`, `_IMPL.chassis.router = _v28_router`, `v57_apex_v28_fitted_agent`, layer marker) each appear 0× in the parent and exactly `layer.count()`× in the output | PASS |
| (c) byte delta | `len(out) == len(base) + len(layer)` | base 1,076,244 B + layer 3,265 B = 1,079,509 B |
| (d) import + rebind | module loads, `_V28_TABLE` round-trips the frozen JSON, `_IMPL.chassis.router is _v28_router`, `kaggle_submission_agent is agent`, `agent is not _V28_PARENT`, `len(_ROUTES)==41` | PASS |
| (e) not inert | play the seed and read `_V28_FIRE['differs_from_table']` + the latch tuple | PASS 1/1 (`('YARN_STORE','PET_CAFE') → 105 instead of shipped 9`, `steps_forced=504`, `rule_P=1`); a world with no learned rule reports `rule='none'`, `differs_from_table=0`, i.e. it demonstrably keeps the shipped pick |

_Note: the synthetic table used for this selftest was deleted; the shipped candidate (if any) is
rebuilt from `results/v28/v28_table.json` only._

## 5. Verdict

## 4. Reproduction

```
WybeV2/rank_env/Scripts/python.exe tools/probe_v28_router.py                 # T1 census (64 worlds)
WybeV2/rank_env/Scripts/python.exe tools/sweep_v28_routes.py --bank r1r2 --all --swaps both --workers 5 \
    --out results/v28/t2_sweep.jsonl                                        # T2/T3 sweep, resumable
WybeV2/rank_env/Scripts/python.exe tools/sweep_v28_routes.py --analyze results/v28/t2_sweep.jsonl
WybeV2/rank_env/Scripts/python.exe tools/sweep_v28_routes.py --fitfrom results/v28/t2_sweep.jsonl \
    --bank r1r2 --outtable results/v28/v28_table.json                       # freeze the fit
WybeV2/rank_env/Scripts/python.exe tools/sweep_v28_routes.py --fit --seeds <fresh+t5> \
    --table results/v28/v28_table.json --out results/v28/t3_eval.jsonl      # out-of-sample gate
WybeV2/rank_env/Scripts/python.exe tools/build_v57_apex_v28_fitted.py \
    --table results/v28/v28_table.json --verify <seeds>                     # T4 graft + proofs
```

Pre-registered fit rule (fixed before any test bank was read): a class gets a rule only if it has
**≥3 training worlds** and its argmax route beats the shipped table by **≥+500/game** in training.
The shipped pick's own training delta is 0.0 by construction (forcing the route the table picks is
inert), so this is a pure improvement test. Resolution chain: ordered pair → unordered pair →
YARN/other regime → **no change**. Fit bank `SEEDS_R1+SEEDS_R2`; test banks `SEEDS_FRESH` (16) and
`SEEDS_T5 = range(60000000, 60032000, 1000)` (32), disjointness asserted in
`write_fitted_table()`.

Files touched: `tools/probe_v28_router.py`, `tools/sweep_v28_routes.py`,
`tools/build_v57_apex_v28_routes.py`, `tools/build_v57_apex_v28_fitted.py`,
`agents/pub_v57_apex_v28_*.py`, `results/v28/*`. The spine, `submission.py`, `processing.md` and
every other agent's directories are untouched.
