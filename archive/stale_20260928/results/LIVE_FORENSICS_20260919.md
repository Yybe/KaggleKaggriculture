# Live Forensics 2026-09-19 — why our live scores sit at ~2200, not ~3000

Scope: read-only. Kaggle live (simulathon) replays, competition `kaggriculture`, engine `1.32.7`.
Four submissions examined. Per-submission episode lists + rewards pulled via
`competitions.EpisodeService/ListEpisodes`; 12 replays (3 per submission: biggest win,
biggest loss, median margin) downloaded to `results/live_forensics_0919/` and parsed with stdlib `json`.

**One framing correction up front:** the Kaggle "publicScore" (2194.2, 2994.8, ...) is a
*leaderboard rating*, not the in-game bank. Real final banks run ~50k–177k. So "score" and
"bank" are different quantities and only the *rating-vs-bank* comparison can test the
inflation hypothesis (done in §1).

---

## 1. Pool-inflation test (our own bank distribution across eras)

| submission | date | rating | episodes W/L/T | win-rate | OUR mean bank | OUR median bank | OPP mean bank | OPP mean bank when we LOSE |
|---|---|---|---|---|---|---|---|---|
| ShiV17 (55408688) | Aug-11 | **2994.8** | 99/7/0 | 93.4% | 92,372 | 91,375 | 80,516 | 90,686 |
| v28 herdswap (56017040) | Sep-04 | 2289.2 | 49/33/25 | 59.8%* | 85,235 | 82,563 | 75,570 | 84,319 |
| v34 quad (56149972) | Sep-10 | 1618.0 | 24/13/0 | 64.9% | 90,951 | 89,528 | 80,189 | 81,822 |
| **shop-router (56151628)** | Sep-10/11 | **2194.2** | 42/10/1 | 80.8% | **98,453** | **97,698** | **88,749** | **112,733** |

\*v28's 25 "ties" are byte-identical **mirror matches vs clones** (verified: ep 105557472 ends 64,246 = 64,246 with identical tape). Win-rate adj for ties ≈ 57%.

**Reading:**
- shop-router has the **highest own bank of any era** (mean 98.5k, median 97.7k) yet a **lower rating (2194) than ShiV17 (2994) which banked less (92.4k)**. Same-or-better economics → *lower* score. That is the inflation signature.
- The rating does not track bank: v34 banks 91k → rating 1618; ShiV17 banks 92k → rating 2994. Rating tracks **win-rate against the pool**, and the pool moved.
- Opponent strength rose: average live opponent bank 80.5k (Aug) → 88.7k (Sep). The bank needed to *win* rose from ~91k (ShiV17 median win) to shop-router losing games at 98k bank because its losing opponents banked 105k median / 112.7k mean.
- shop-router's 19% loss rate vs ShiV17's 6.6% is *not* explained by worse play (shop-router banks more); it is explained by facing a richer pool.

**Verdict on hypothesis: SUPPORTED.** The 2994 is a stale-weak-pool artifact. ShiV17 is *not* ~800 points of economics better than shop-router — shop-router is arguably the stronger agent and still rates lower because the same bank no longer clears the pool. (Caveat: not 100% inflation — shop-router's raw win-rate is genuinely below ShiV17's, but that gap is itself attributable to pool strength, since shop-router banks more per game.)

---

## 2. Are we crashing live? — NO.

Signal from all 12 replays (our agent):

| episode | our final status | min `remainingOverageTime` | longest do-nothing run (farmer PASS + no mkt + idle hands) | market orders in last 120 steps | INVALID / ERROR / TIMEOUT |
|---|---|---|---|---|---|
| all 12 (every era) | DONE | 60.0 (never dips) | 1–3 (ShiV17 up to 13, legit crop-wait) | 119–306 | **0** |

- We finish every game `DONE`, at 720 steps, with the **full 60s overage bank untouched** → zero timeout pressure.
- No long PASS runs; no late-game market blackout (we keep issuing orders through day 30). `late_empty_market` only when there is genuinely nothing to sell.
- Conclusion: **live losses are out-economics, not crashes/timeouts.**

---

## 3. Loss anatomy: the herd-assembly (PLACE-fidelity) failure

Our tape is essentially fixed across eras (buy ~17–18 animals, ~260–290 hires, 239+ seed buys, 2 BUY_LANDs → 3 quadrants). The wins and losses differ in **whether that tape's animals actually get seated on pasture.** Herd on-board vs step (bought always 17–18):

| game | outcome | PLACE cmds | CARE / FEED | herd ramp 0→end: @120 / @240 / @360 / @600 / final | animals SOLD |
|---|---|---|---|---|---|
| shop-router MED (win) | WIN 120k | 97 | 417 / 367 | 6 / 13 / 17 / 17 / **17** | none |
| shop-router LOSS (51.9k) | LOSS | 96 | 416 / 367 | 2 / 5 / 5 / 5 / **5** | none |
| v34 MED (win) | WIN 104k | 97 | — | → **17** | none |
| v34 LOSS (54.2k) | LOSS | 109 | 384 / 361 | 3 / 4 / 6 / 6 / **6** | none |
| ShiV17 LOSS (67.6k) | LOSS | 13 | 285 / 290 | 5 / 12 / 12 / 13 / **13** | none |

Same agent, ~identical PLACE/CARE/FEED counts, **but in losses the herd never assembles** — it plateaus at 5–6 animals instead of 17. Animals are not sold (SELL-animal = 0) and the curve is monotone (no mass escape die-off); the PLACE commands are firing as **no-ops** (no valid empty PASTURE/COOP at the standing tile / no hand to receive them at that step). Result: ~12 stalled animals ⇒ ~20k+/game of lost MILK/WOOL late production ⇒ the 4× money-curve gap at step 600 (e.g. shop-LOSS 27,870 vs opp 111,299). ShiV17's loss is the *mild* version (herd 13 vs opponent 19); shop-router/v34 losses are the *severe* version (herd 5–6 vs 17).

This is the same BUILD→PLACE fidelity defect flagged in `LIVE_FORENSICS_20260904.md`; it is live-reproducible and is a placement/hand-scheduling bug, **not** a market/price or timeout problem.

---

## 4. What a live winner looks like (quadrants, herd, sell timing)

Winners among the 12 episodes: the non-us winners are **Naru041104, xxxxyt, yang zhang, HealthStone**. All four are one archetype:

| winner team | final bank | quadrants | herd (placed) | hires | BUY_LAND | sell-timing |
|---|---|---|---|---|---|---|
| Naru041104 | 158,610 | **3** (NW,NE,SW) | 17 (8 COW / 6 SHEEP / 3 GOOSE) | 266 | 2 | ~70% of income by step 600, rest back-loaded |
| xxxxyt | 132,419 | **3** | 17 (8 COW / 9 SHEEP) | 283 | 2 | back-loaded (68% by 600) |
| yang zhang | 110,557 | **3** | 16 (6 COW / 10 SHEEP) | 287 | 2 | back-loaded (67% by 600) |
| HealthStone | 79,151 | **3** | 19 (12 COW / 7 SHEEP) | 274 | 2 | back-loaded (77% by 600) |

- **Distinct winning strategies across these episodes = 1.** They are the same 3-quadrant COW+SHEEP animal-economy we ourselves run; we lose when our own herd fails to assemble, not to a novel counter-strategy. The meta has converged.
- **Nobody plays 4 quadrants.** Every winner *and* every game we win tops out at **3 unlocked quadrants (NW+NE+SW)**; SE ($4k) is never bought. Corroborates the "quad-SE is not a blanket win / gated overlay only" project note.
- **Herd is the engine:** winners carry 16–19 placed COW+SHEEP (19 in the strongest, HealthStone). Pasture count is not the limiter — both sides build 12–19 pastures; winners *fill* them, losers leave 7–12 empty.
- **Sell timing is universally back-loaded** (50–82% of income by step 600, i.e. ~day 25 of 30) for winners AND losers alike — timing is **not** a discriminator. The `raw SELL unit` fields are unreliable here (agents emit "sell-all" sentinel quantities like 7,000,000), so timing was measured off the money curve instead.
- **Bank scale:** a live winner banks ~80k–160k (median ~110k on our losses). The "400k+ bank / 3000-class economy" framing doesn't apply — ~130–160k with a full 17–19 head is what beats us.

The opponents we *crush* (Romain Bomba 22.8k, masayoshi 7.5k, Georgy Mamarin 4, SNAEHATH P 16.3k) are stale/crippled agents: 1–2 quadrants, herd of 0–1 despite 8–18 pastures, long PASS runs (max_pass 8–15), 18–27 animals bought but never seated. These are leftovers that inflate win-rates in a thin pool.

---

## 5. Conclusions

1. **Not crashing.** Zero timeouts/errors; full time bank retained; no PASS blackouts; late market orders present in every game. Live losses are purely economic.
2. **Out-economics, specifically herd assembly.** Our fixed tape buys the right herd but PLACE/CARE/FEED silently no-op in ~10–20% of live games, leaving 5–6 of 17 animals on the board. That, not selling or prices, is where we lose. Fix the BUILD→PLACE→FEED fidelity (ensure a hand is co-located with an empty matching structure before issuing PLACE; verify animal actually seats, else re-place) and shop-router's ~19% live loss rate is largely recoverable.
3. **Pool inflation is real and is the main reason 2194 ≠ 2994.** Our banks did *not* drop from Aug to Sep — they rose (92k→98k) — while the rating fell 800 pts. The same bank that won the Aug pool now loses to a Sep pool whose opponents bank 105–113k. ShiV17's 2994 reflects a weaker/stale field, not 800 points of superior economics.
4. **Live winner template to match:** 3 quadrants (NW/NE/SW), fill 16–19 pastures with COW+SHEEP, ~260–290 hires, income back-loaded after day 12. We already match this template in our wins — the gap is execution fidelity, not strategy, and not buying SE.

Artifacts: `results/live_forensics_0919/_select.py` (era bank distributions), `_analyze.py` + `_analysis.json` (per-episode replay parse), and the 12 `episode-*-replay.json` files.
