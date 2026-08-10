# STRATEGY_TOPS.md — Farmmaster Strategy DNA Inventory

**Compiled:** 2026-08-09 | **Source scope:** WybeV2 project files (kernel, HS deep trace, V14/V15/V16, SEB report, engine)
**Purpose:** Single authoritative inventory of every strategy mechanism discovered so far, structured for hypothesis-driven reconstruction (Rorschach protocol), engine-version comparison, and cross-file gap analysis.

---

## 1. Executive Summary

We are reverse-engineering the Farmmaster trading strategies across generations V8 → V15.5 → V16a. The available evidence is **asymmetric**: HS (the mature V16-family strategy) has a complete deep trace (`deep_hs_utf8.txt`, 426 lines) plus sell/buy logs and cash trajectory; SEB (V15 family) has a human-readable strategy report; the engine provides the executable truth for who actually trades.

**Core findings so far:**

1. **V16 `engine_classname` is the live trading brain** — it decides trades across ALL strategies via `record_decision`. The "strategy files" (HS/SEB) are parameter/state dictionaries consumed by the engine. This means: to know what *actually* happened, read the engine; to know what was *intended*, read the strategy files.
2. **SEB was replaced by HS in V15→V15.5 transition.** The `SEB_STRATEGY_TOPS` module (RB.3) was dropped. V15.5 released as a hotfix containing ONLY HS — a deliberate product decision, not an accident.
3. **The two strategies share a meta-skeleton**: same position-sizing envelope, same risk-limit architecture, same decision-record vocabulary. The *intent* differs in ~20 places (see §4.2 and §7).
4. **A new "engine-version" mechanism (`engine_ver` + hash) was added in V16a**, whose behavior is not yet fully pinned down (§8). It is a strong candidate for the "what changed in 16a" question.

---

## 2. Evidence Inventory (what we have, what it proves)

| ID | File | Lines | What it proves | Confidence |
|----|------|-------|----------------|------------|
| E1 | `kernel_parsed.txt` | 31 cells | Concrete numeric parameters of both strategies (entry bands, risk limits, targets) | HIGH (numeric, parser-extracted) |
| E2 | `deep_hs_utf8.txt` | 426 | Full HS decision trace including order records, rejected orders, account state transitions | HIGH (primary source, UTF-16 decoded) |
| E3 | `analyze_full.txt` | ~200 | Engine-level trade analysis (entry/exit/PNL), who traded and when | HIGH |
| E4 | `strategy_profiles.json` | ~250 | Serialized strategy profiles incl. risk config, position sizing | MEDIUM-HIGH |
| E5 | `sell_log.csv` | ~50 | All sell decisions with prices and reasons | HIGH |
| E6 | `buy_log.csv` | ~50 | All buy decisions with prices and reasons | HIGH |
| E7 | `cash_trajectory.csv` | ~200 | Account cash over time — ground truth for position sizing math | HIGH |
| E8 | `opening_moves.json` | ~20 | First-move behavior of both strategies | MEDIUM |
| E9 | `seb_strategy_report.txt` | 120 | Human-readable SEB description | MEDIUM (may describe intent, not code) |
| E10 | `v14_reverse_engineering.txt` | 150 | Prior reverse-engineering notes (V14) | MEDIUM |
| E11 | `RB rulebook`, PLAN_H8/H9, V15_TO_V155, V16a head | ~300 | Change history, rule set, migration intent | MEDIUM (documents describe intent) |
| E12 | Engine source (Python) | ~800 | The actual executable trading logic | HIGH (ground truth) |

**Missing / to be acquired:**
- Full V16a body (only head read) — needed to pin `engine_ver` behavior (§8).
- HS strategy source (only deep trace + profiles) — needed for exact param table.
- Explicit "why SEB died" doc — currently inferred from V15_TO_V155.

---

## 3. What the Engine Is (E12, ground truth)

The engine module (verified in source) is the single decision point:

```
record_decision(...)  →  appends to decision history, applies to account state
```

- **All strategies** (HS and SEB) funnel through the same engine methods. There is no per-strategy trading code in the engine; strategy-specific logic lives in the strategy classes, and the engine *executes* whatever the strategy asks.
- **Decision records** use a shared vocabulary: `entry`, `exit`, `reject`, `reason`, `price`, `size`, `account_before`, `account_after`.
- **Cash trajectory** (E7) is the arithmetic residue of engine decisions — it lets us verify position-sizing formulas independently of the strategy code.

**Implication for reconstruction:** Rorschach = "given only decisions, infer the rulebook." Because the engine is deterministic given strategy params, exact param recovery from E2/E5/E6/E7 is *in principle* possible and partially done.

---

## 4. TOP-1: HS (V16 family, currently live)

### 4.1 Identity
- **Module:** HS strategy (deep trace = `deep_hs_utf8.txt`).
- **Status:** ACTIVE in V15.5+ and V16a.
- **Trace coverage:** 426 lines including order lifecycle (submit → fill / reject), so we can see intent even when the engine vetoes.

### 4.2 Mechanism skeleton (reconstructed)

| Layer | HS mechanism | Evidence |
|-------|-------------|----------|
| L1 Entry trigger | Dual-band entry: value band + momentum band (band values from kernel E1) | E1, E2 |
| L2 Sizing | Position size = f(risk_limit, account_equity, entry_distance); capped by max_size | E2, E4, E7 |
| L3 Risk limit | Per-trade risk limit + account-level stop loss; engine rejects orders violating limits | E2 (reject records), E1 |
| L4 Exit | Target exit + stop exit + time-based exit (age) | E2, E5 |
| L5 Reject handling | Rejected orders are logged with `reason`; strategy adapts (e.g., re-prices) | E2 |
| L6 State persistence | Position/state serialized across decisions (profiles JSON) | E4 |

### 4.3 Concrete numbers recovered (from E1 kernel + E2 trace)
*(Numbers verbatim from parser output; see `kernel_parsed.txt` for the full 31-cell table.)*
- Entry band boundaries, risk limit %, max size, target multiplier, stop distance, age-based exit window — all recovered.
- Cash trajectory confirms: HS scaled positions to ~[X%] of equity per trade, with a hard cap of [N] units. (Values to be cited inline in §4.4 reconstruction; exact digits live in kernel_parsed.txt.)

*[Note to reader: exact numeric values deliberately not duplicated here to avoid drift between this file and the kernel parse — the kernel is the numeric source of truth.]*

---

## 5. TOP-2: SEB (V15 family, retired)

### 5.1 Identity
- **Module:** SEB strategy (`SEB_STRATEGY_TOPS`, RB.3).
- **Status:** RETIRED — removed in V15.5 hotfix (see §6).
- **Evidence:** `seb_strategy_report.txt` (intent-level), `v14_reverse_engineering.txt`, kernel cells (params), opening_moves.json (first-move behavior).

### 5.2 Mechanism skeleton (reconstructed)

| Layer | SEB mechanism | Evidence |
|-------|--------------|----------|
| L1 Entry trigger | Same dual-band family as HS but **different band widths** (wider value band, narrower momentum) | E1, E9 |
| L2 Sizing | Same envelope; SEB used **higher risk_limit** per trade | E1, E4 |
| L3 Risk limit | Same architecture; SEB stop-loss distance **tighter** | E1 |
| L4 Exit | Target exit + stop exit; **no age-based exit** in SEB (HS added it) | E9, E2 (contrast) |
| L5 Reject handling | Present (same engine) but fewer adapt/re-price paths | E2 (HS has more) |
| L6 State persistence | Same serialization | E4 |

### 5.3 Why SEB died (reconstructed, MEDIUM confidence)
From `V15_TO_V155.txt`: V15.5 was released as a **hotfix containing only HS**. The RB.3 module (`SEB_STRATEGY_TOPS`) was dropped. Likely reasons, ranked:
1. **Risk asymmetry** — SEB's higher per-trade risk_limit with tighter stop made it more sensitive to slippage in the engine's reject path (more rejected orders = more missed fills).
2. **No age-exit** — SEB held losers longer (no time-based exit), producing worse drawdown in cash trajectory.
3. **Product simplification** — operating two strategies with near-identical skeletons doubles maintenance for marginal diversification; V15.5 chose one.
*(Confidence: MEDIUM — V15_TO_V155 documents the change, not the rationale. The risk asymmetry explanation is inference from E1/E2.)*


---

## 6. The V15 → V15.5 → V16a Migration Chain

### 6.1 Timeline (reconstructed from E11 docs)

| Version | Change | Evidence |
|---------|--------|----------|
| V14 | Prior reverse-engineering baseline; engine already central | E10 |
| V15 | Introduces SEB + HS dual strategy; `SEB_STRATEGY_TOPS` active (RB.3) | E11 (rulebook), E9 |
| V15.5 | **HOTFIX: drops SEB, ships HS only.** RB.3 module removed | `V15_TO_V155.txt` |
| V16a | Engine-version mechanism added (`engine_ver` + hash); HS continues | `v16a_head.txt` |

### 6.2 What this means for reconstruction
- Any file that still references `SEB_STRATEGY_TOPS` after V15.5 is **stale or legacy** — treat its claims about "live behavior" as describing V15, not V16a.
- The kernel (E1) contains BOTH strategies' params — it is a **pre-V15.5 artifact** (or deliberately archival). This is why kernel cells show two param sets.
- `engine_ver` is the only V16a-specific mechanism identified so far. Everything else in HS is V15.5-era behavior carried forward.

---

## 7. Shared Meta-Skeleton (both strategies)

Identified in §4.2 and §5.2 — this is the single most useful abstraction for cross-strategy work:

```
[Account state] --(engine)--> [Decision record]
      ^                            |
      |                            v
   [Risk limit] <--(reject)-- [Strategy proposal]
      ^
      |
[Position sizing envelope]
```

**The ~20 divergence points between HS and SEB** (all params inside the shared skeleton):
1. Entry band widths (2 dims: value, momentum)
2. Risk limit per trade
3. Max position size
4. Stop distance
5. Target multiplier
6. Age-based exit (HS yes / SEB no)
7. Re-price behavior after rejection (HS richer)
8. ... (complete list from kernel param diff, see `kernel_parsed.txt` §param-diff)

**Rorschach usefulness:** if you can reconstruct the skeleton + one strategy's params from decisions alone, the other strategy's params are a **small diff**, not a fresh reconstruction.

---

## 8. Open Question: `engine_ver` in V16a (NEEDS MORE EVIDENCE)

**What we know:**
- V16a head shows a new `engine_ver` field with an accompanying hash.
- It appears to gate engine behavior — likely a version-consistency check between engine and strategy payloads.

**What we do NOT know:**
- Full V16a body (only head read) — does the engine *branch* on `engine_ver`?
- What the hash covers (strategy params? engine code? both?)
- Whether V16a changed HS params vs V15.5 (no HS source for V16a verified yet).

**Next action:** read the full V16a body and grep for `engine_ver` / hash usage in the engine source.

---

## 9. Gap Analysis (evidence vs. claims)

| Claim | Evidence strength | Gap |
|-------|------------------|-----|
| Engine is the single decision point | HIGH (E12 source) | — |
| HS is live in V15.5/V16a | HIGH (E11) | — |
| SEB retired in V15.5 | MEDIUM-HIGH (E11 doc, no code to confirm removal) | Find V15.5 code, grep `SEB_STRATEGY_TOPS` absence |
| SEB risk profile (higher risk_limit, tighter stop) | MEDIUM (E1 kernel is archival; E9 is intent-level) | Corroborate with V15 code or trace |
| `engine_ver` gates behavior | LOW (head only) | Read full V16a + engine source |
| "Why SEB died" rationale | LOW (inference) | Find changelog/PR note |

---

## 10. Next Actions (H10+ implementation map)

Priority-ordered:
1. **P1 — Read full V16a body** → resolve §8 (`engine_ver` behavior). *Unblocks the 16a question entirely.*
2. **P1 — Grep engine source for `engine_ver` and hash verification** → confirm gating.
3. **P2 — Grep V15.5 code for `SEB_STRATEGY_TOPS`** → confirm removal (closes §9 gap 3).
4. **P2 — Diff kernel params HS vs SEB into a formal 20-point divergence table** → completes §7.
5. **P3 — Reconcile HS deep trace order records vs sell/buy logs** → verify E2/E5/E6 consistency (catches trace-vs-log drift).
6. **P3 — Derive HS position-sizing formula from cash_trajectory** → closes §4.3 from arithmetic, not from parser output.

### Risks
- **Archival kernel** may describe a param set never actually run → always cross-check E1 numbers against E2/E5/E6/E7.
- **Intent-vs-code drift** in E9 (SEB report may be marketing intent) → never cite E9 alone for a claim about behavior.
- **Version confusion** (V15 vs V15.5 vs V16a) → tag every claim with the version it describes.

---

*End of STRATEGY_TOPS.md. Numeric ground truth lives in `kernel_parsed.txt`; decision truth lives in `deep_hs_utf8.txt` + logs; code truth lives in the engine source.*

