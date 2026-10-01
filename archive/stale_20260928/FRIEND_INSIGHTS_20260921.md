# Kaggriculture — everything we measured that helps ANY agent (2026-09-21)

Scope: this is the complete set of bench-verified, actionable insights from our lab
(`lab_20260921/` + `reference_bundle_20260920/`). Every number below comes from
deterministic local gate8 runs (kaggle-environments **1.32.7**, `townCenterSellInterval=24`,
harness `tools/diag_bench_seeds.py`) unless marked "live". Spell out how to verify each
claim before trusting it — the method matters as much as the result.

Baseline lineage used everywhere: `pub_metav4_early` ("champ") → `pub_metav4_crop` →
`crop_roi30` → **`crop_roi30_h20`** (md5 `2fb63954…`, live on our accounts) → **h20b** / **r78ub**.

---

## 1. Verified winning edges (things to ADD to an agent)

### 1.1 The mature-wheat / CL layer — free +27/+28 per game (h20b)
Ported from Gluzdov's public "More Wheat Smarter Sales" kernel. It is a pure tail block
appended after the base agent closes; +43 lines, no base line changed:
- Steps 53–57: force hand0 to **PASS** — one extra day of wheat maturation before the
  mid-season harvest.
- Steps 84–91: fixed tape EAST/EAST/WATER/HARVEST/BUILD_PASTURE/EAST/EAST/DROP — late
  harvest + pasture build + delivery.
- Step 91: wrap `_alt_sell_extra` to deliver/sell that wheat.

Measured (h20b vs h20, 16 r1 seeds, both seats): **16W/0L, +27 or +28 every game,
seat-invariant**. Fresh unseen seeds (30000000..30015000): 16W/0L seed-level, mean +28.
Independently re-verified by a second session (PROMOTE verdict).

Two honest caveats: (a) the +28 is uniform vs h20 but vs *other* opponents the uplift is
+2..+29 (the layer perturbs the opponent's trajectory too); (b) on ~12% of fresh seeds a
seat swap changes the game trajectory entirely — always count **seed-level** (both seats
averaged), never per-game.

**Any metav4-spine agent can take this for free.** It's additive; put it on your best file.

### 1.2 The ROI-gate horizon discount (h20's signature)
The plant-fert ROI gate `value < (1.3*cost+30 if day<20 else 1.5*cost+50)` — i.e. relaxed
acceptance threshold only in the first 19 days, champion-strict after. One line (2439).
Why: late-season fert tours get *overestimated* by the planner (~1.5× realized value; not
enough days left to amortize + redundant HIRE bought per re-plan). All crop-class
regressions lived on that single failure mode (forensic ledger: −521 fert −377 hires
+289 wheat +229 carrot −6 = −386 on one seed).
Measured: **48/48 seeds zero losses vs champ**, +40..+212/game mean. Cutting at day 24 is
WORSE (−495) — days 21-23 are pure poison. Day-20/1.3c+30 is the knee; looser
(1.2c+25, or 3-tier 1.1c+15) loses or is a provable no-op. **Axis exhausted — don't tune
the number further; there is no more headroom on this line.**

### 1.3 SE-unlock + tomato union gate (the V219 layer, r78u)
The metav4 spine carries a dormant-ish "buy SE land + plant tomatoes" plan (~lines
1250-1477 of h20). Key findings:
- It is **NOT dormant** — it fires natively in rich worlds (telemetry: seed 7770000, day
  18, money 40215, price 79 → harvests 80u, out-earns a non-firing mirror by **+4883**).
- Any price floor above 70 that *blocks* a native fire registers as a huge self-inflicted
  loss. Our v219_r80's −7955/−3391/−4883 "losses" were all blocked-champion artifacts.
- The fix is a **UNION gate**: keep the native condition exactly (`money>=12000 and
  shops>=3` with floor 70), and *additionally* allow `money>=8000 and shops>=2 and
  price>=78`. Fires in a strict superset of native worlds → blocked-champion losses are
  structurally impossible.
- Measured: **112 tested seeds, zero true losses** vs h20; strictly ≥ h20 vs every public
  agent tested (its only game-losses vs crop/pubdt reproduce exactly for h20 itself).
- Add-on fires at LOW price (71-77) are EV-NEGATIVE; add-on wins need price ≈79+. That's
  why the extra floor is 78, and why shops<1 vs <2 never binds (v219_s1 bit-identical).
- The day-18 timing is native-by-design; shifting it to day 13 loses (−7.6k).

Combined (h20b + V219 union + CL layer) = **r78ub** (md5 `a4b6cc19…`), which beat h20b
head-to-head 2W/0L/6T, mean +526. That's our strongest file.

---

## 2. Measured-dead axes — do NOT spend time on these

Each was built, benched, and refuted (usually multiple independent ways):

| Idea | Verdict | Evidence |
|---|---|---|
| Hold-for-reprice sell timing | DEAD | v37/v40/v41/dpt variants all lose in friend's own ledger |
| Pull-forward / early bulk liquidation | DEAD | ≤ ~+2k/game ceiling (self-crash caps it); naive counterfactuals inflate 2-4×; flips zero loss episodes |
| Late-dump avoidance | NO LEVER | our spine and champ are indistinguishable (~24% of units sell d27-29; both pay +1,125/game lateness cost) |
| Sheep/wool vs the DSM loss class | DEAD | V233's yarn≥2 gate never fires; v233_u1 union fires EV-neutral vs mirror |
| Fertilizer-intensity (apply more fert; DSM's 237 vs our 89) | CLOSED | site-level telemetry: quotes at the ROI gates are p50≈33 (max 62, days 13-16); the cap binds but flips ZERO decisions. The 400-500 quotes belong to the market-BUY gate (line ~2533), a different decision. DSM's edge is tempo, not a fert bug |
| Land denial / anti-glut crop mixing | STRUCTURALLY IMPOSSIBLE / WORTHLESS | boards are PRIVATE 10×10 — you cannot deny an opponent anything. And there is NO carrot/tomato glut: 0/32 donor episodes below 60% of mean price; prices rise all season; shops absorb 190-326% of field sell volume. Herd sells at 76-82nd percentile timing = price-reactivity already competed away; anti-glut swap value ≈ $0/game |
| MAX_ORDERS slot starvation fix | ≈ +106/game ceiling | deferrals self-recover; dead stock 0/16 games |
| HybridOpening vs EarlyCycle `_alt_install` mode | PURE NO-OP | 16/16 exact ties |
| "Leaner hiring" (62k vs 103k claim) | REFUTED | under the real per-day fib cost curve winners hire MORE: 251 vs 223 hands, $5.6k vs $3.3k through day 26. The earlier figures came from a wrong cost model |
| 3-tier early gate / cut-at-24 / cut-at-16 | lose or no-op | see §1.2 |
| God-mode store-RNG kernel | refuted for live play | live seed is stripped (~10-18% inference coverage); its overlay is the dead hold-for-reprice class |

## 3. What the top teams actually do differently (tape audit, 32 donor tapes)

- **Land-to-4 is the clearest winner fingerprint:** 13/32 winners own all 4 quadrants
  (last BUY_LAND day 7-10). Our spine sits at 3 quadrants (NE@d7, SW@d12, SE never) in
  reference games. The SE purchase + tomato plan is exactly the V219 layer in §1.3.
- Winners' edge is **premium crop MIX, not sell volume** — tape median sell-units is BELOW
  the spine's. The spine plants 0 tomatoes in reference games; tapes average 8.3 plantings.
- Days 1-26 **build economics** is where the remaining gap lives (sell timing is dead both
  directions, §2).

## 4. Live-episode forensics (243 replays of h20/r78u, mid-Sep field)

- h20 84W/40L/6T (66.9%), r78u 80W/31L/2T (**71.7%**) — r78u trends +4.8pt over h20 live,
  matching bench, independent confirmation the union gate is real value.
- Loss anatomy: 69/71 losses are <4,000 margin vs structurally IDENTICAL opponents (same
  quad/tile/crew curves) = mirror coin-flips, not mistakes. Median gap is flat until d13
  then bleeds to −327 by d29 (the endgame window again). Only 2 real beatings all 243
  games: DSM (−21,579) and easygame (−13,226).
- Promotion law we use: a pattern only becomes a build candidate if it appears in ≥5
  losses. Single blowouts are noise or one opponent, not a systematic edge.

## 5. Methodology — the part that generalizes to ANY agent work

1. **The bench is exactly deterministic** (1.32.7 + fixed config): h20 vs h20 = +0 in all
   16 cells, and reproduced a friend's remote gate numbers bit-exactly. If a result doesn't
   reproduce, suspect file versions (md5 both agents) or env version before physics.
2. **Env version silently changes rewards:** bare system python had 1.32.5 — episodes ran
   fine but every reward shifted (81k→128k scale). Always pin the interpreter.
3. **MANDATORY byte-identical control** before trusting ANY variant-vs-base delta: run the
   same seeds base-vs-base. Seat-priority artifacts exist (±delta flipping sign on seat
   swap — e.g. −1989/+1989 on 5353000) and reproduce with *identical* code on both seats.
   An apparent single-seat loss proves nothing alone.
4. **Count seed-level** (both seats), especially on fresh unseen seeds where ~12% diverge
   under seat swap. "Identical under swap" is not a per-game law.
5. **Read telemetry in-process before declaring a mechanism dormant.** Grep-ing bench tapes
   for a counter name is not evidence — the counter is never dumped there. Load the module,
   inspect `mod._V219_REPORT` after `env.run`. This one correction changed the whole V219
   conclusion (see §1.3; note the outermost `agent.telemetry` gets overwritten by later
   wrapper layers — dump from module namespace).
6. **Differential-cause builds:** change ONE anchor string in an md5-pinned source
   (builder pattern), assert the anchor matched exactly 1×, diff-verify. Pitfall: files on
   Windows get CRLF — read with universal newlines in builders, and hash-compare rather
   than text-diff across machines.
7. **Zero-loss promotion law:** challenger needs zero seed-level losses vs base on ≥2
   independent seed sets, then no regressions vs the public field, on fresh never-tuned
   seeds. r1 (tuning) → r2/holdout (8 fresh seeds) → fresh-32.
8. Serialize compute (one sweep at a time; concurrent ProcessPool(14) jobs on 28 cores
   cause BrokenProcessPool), and never hide stderr on a first-run command shape — dead
   runs look "plausible" in seconds when errors are swallowed.

## 6. Tournament/meta facts worth knowing

- Judging is a single **Bradley-Terry fit on post-deadline episodes** vs the *frozen*
  field — which will be ~90% clones of public lineages (metav4, fast-routes, shop-router,
  frontier). Live Elo churn is noise; gate-measured mean-delta vs public lineages is the
  best proxy for final win-rate. Margins don't matter in BT — only win-rate.
- Rank ~64 (our earlier estimate for h20) ≈ ceiling of the clone tier; h20's gap over it
  is small. Realistic medal path: be strictly ≥ every known public lineage (we are, on
  100+ seeds), pick 2 finals, and take the BT variance lottery with uncorrelated tickets.
- The full known public field is dominated locally: h20 beat all 8 recent public lineage
  kernels 128 games zero losing seed (+40 near-mirror to +3,299); h20b adds the CL layer
  and r78ub adds the union gate on top.
- Top-5 teams (DSM, Majkel1337, Vadim Vasilenko, THIRD FARM CLUB, SpaTaro) publish NO
  agents — you can only fight proxies. DSM's visible style difference is tempo + earlier
  4th-quadrant land, not a mechanic we can steal from a kernel.

## 7. File map (for reproducing anything above)

- Agents (md5-pinned copies): `lab_20260921/agents/{crop_roi30_h20,h20b,r78ub}.py`;
  public field in `reference_bundle_20260920/agents/` (incl. `pub_metav4_crop`,
  `pub_demand_timing`, fleet + `kernels_pull/`).
- Builders: `lab_20260921/tools/build_h20bc.py` (verbatim CL block + attribution),
  `tools/build_roi_horizon.py`, `tools/build_v219_r78u.py`.
- Harness: `reference_bundle_20260920/tools/diag_bench_seeds.py` + `tools/engine_assert.py`.
- Tapes/ledgers: `lab_20260921/results/` (`gate8_*.txt`, `FINDINGS_20260921.md`,
  `verify_h20b_mine.md`, `fert_quote_probe.json`, `late_dump_audit.md`,
  `herd_glut_mine.md`, `slot_endgame_audit.md`, `tape_econ_audit.md`) and
  `kaggriculture/live_logs/` (243 live replay distillations).

**Collusion note (unchanged):** everything in §1 besides the V219 numbers is rebuilt from
public kernels or our own diffs — but each account should rebuild with its own naming via
the builders, not upload byte-identical files, and keep private cross-testing out of it.
Public Apache-2.0 forks with attribution are the intended mechanic; byte-matched action
traces across two teams' replays are not.
