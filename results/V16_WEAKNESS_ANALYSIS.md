# V16 Weakness Analysis: salemali7 (from LIVE episode replays)

Date: 2026-08-09
Source: live episodes of submission `55364555` (salemali7 3000-score agent, scouting submission under team Shivam_2212)

---

## 1. Live Episode Outcomes (4 episodes)

| Episode | Type | Opponent | Seed | Rewards | Result |
|---|---|---|---|---|---|
| 91177983 | VALIDATION | Shivam_2212 (self/mirror) | 0 | 58,552 vs 58,552 | **TIE** |
| 91178526 | PUBLIC | Anthony LOISEAU | 445187720 | 112,589 vs 34,560 | WIN |
| 91179399 | PUBLIC | CompilingCoder | 1308047812 | 98,871 vs 39,444 | WIN |
| 91180265 | PUBLIC | Dean Shalev | 354817812 | 144,109 vs 85,160 | WIN |

Leaderboard score of the salemali7 submission: **842.5** (vs our V15.5 champion: 1628.7).

**Headline**: In LIVE competition salemali7 underperforms our V15.5. Its preemption only fires
against near-clones (`_clone_distance <= 6`); against the diverse live field it plays pure tape
+ ranking + liquidation, which is weaker than our champion's capselllate/dead-inventory/idle-fill runtime.

---

## 2. The Validation Tie = Mirror Self-Play (720/720 identical actions)

The validation episode ran our submission against **itself**: all 720 steps have byte-identical
actions for both agents (farm, hands, market). Final: exact tie at 58,552.

### 2.1 Double-Dump Degeneracy (the mechanism cannibalizes itself)

Because both agents are near-clones, **both** `_preempt_shift` layers fire on the SAME future
sells and shift them into the SAME early windows. The planned supply is doubled at the shift
step and the tape step is emptied:

| Tape step (planned) | Shift step | Volume hitting market | vs planned |
|---|---|---|---|
| 599 (22 STR) | 597 | **44 STR (22+22)** | 2× |
| 601 (4 STR) | 600 | **8 STR (4+4)** | 2× |
| 615 (10 STR) | 613 | **20 STR (10+10)** | 2× |
| 622 (6 STR) | 620 | **12 STR (6+6)** | 2× |
| 624 (18 STR) | 623 | **36 STR (18+18)** | 2× |
| 648 (8 STR) | 646 | **16 STR (8+8)** | 2× |
| 666 (25 STR) | 664 | **50 STR (25+25)** | 2× |
| 670 (4 STR) | 667/668/671 | 2-3+2-3+3+3 | 2× |

Net effect: the "volume-neutral" property holds per-agent but NOT globally. Two preempting
clones put 2× supply into the early window, destroying the pre-crash high both were chasing.
Mirror game total collapses: 58,552 (live) vs ~118-126K in normal salemali7 games.

Local reproduction (kaggle_environments 1.32.5, live config): mirror tie at ~84K vs ~119K vs
our champion — confirms the mechanism-level cost, with the magnitude gap vs live (58K)
attributed to module version (1.32.6 live) / actual validation seed.

### 2.2 Preemption never fired in the WIN episodes

Win episodes show STR sells at tape+1 steps (600/602/616/623/625/649/667/671), i.e. the
unmodified tape schedule — **zero early shifts**. Opponents (LOISEAU / CompilingCoder /
Shalev) were not near-clones, so `clone_distance > 6` disabled `_preempt_shift` entirely.
salemali7 won purely on tape + `_rank_sell_slots` + `_terminal_liquidation`.

---

## 3. Weaknesses Confirmed (ordered by exploitability)

1. **Near-clone collision (self-defeating)**: two agents with the same tape + preemption
   double-dump and BOTH lose money vs. their normal solo performance. This is directly
   exploitable: an agent that mirrors salemali7's tape triggers the collapse.
   - Counter for V16: **preempt the same windows it preempts** (or sell the same future
     volume 2-3 steps earlier) → force 2× supply → destroy its captured value.
2. **clone_distance gate**: preemption is OFF against any non-clone. Our V15.5 already
   outscores it in general live play (1628.7 vs 842.5). Keep our runtime-layer edge and
   salemali7's preemption never engages.
3. **Horizon ≤ 3 + one-at-a-time**: only shifts sells 1-3 steps out, one active shift at a
   time. A deep-horizon preempter (h=6-12) or an agent that shifts MORE future volume can
   out-position it on the same tape.
4. **Lookahead is deterministic on OUR tape**: `_future_sells_at` reads its own `_ACTIONS`,
   which equals our V14 tape byte-for-byte. **Anti-prediction tape** (randomize among
   equivalent sell slots, or shift our premium sells off-tape) makes its lookahead target
   phantom sales → its shifts land at bad prices (it already leaks small negative shifts:
   e.g. -12 MILK @662, -6 STR @670 in local theft maps).
5. **Price-floor blind spot**: never shifts at $1 floor; leaks small negatives when shifting
   into a lower price than the due step (seed 2000: -12, -8, -3; seed 2073: -6, -2, -2).
6. **Needs staged shed inventory**: `target = min(shed_available, ...)` — if we delay/diverge
   production so the item isn't at the shed 3 steps before its sell, the shift is capped.

---

## 4. Recommended V16 Direction

The killer question ("is preemption intrinsically stronger, or just front-running our dumps?")
is now answered **both ways**, with the live tie as the missing proof:

- Intrinsically stronger in 1v1 clone play (it beat us 40/40 locally by front-running OUR dumps).
- BUT it is **globally volume-positive** — it does NOT add supply, it RELOCATES it. The
  moment the opponent relocates the same supply (mirror/counter-preemption), the edge
  inverts into a shared loss.

### Highest-EV V16 experiments (in order)
1. **A. Counter-preemption (mirror-trigger)**: our agent plays the same tape but ALSO
   preempts 2-3 steps before salemali7's shift points (sell the future volume first, at the
   highest price, then repay at due). Forces the double-dump ON SALEMALI7's shifted window —
   we capture the first-mover high; it eats the crash.
2. **C. Anti-prediction tape**: randomize (deterministically, per-seed) among equivalent
   sell slots for premium items ≥4 units in the 120-680 window. Breaks `_future_sells_at`.
3. **B. Deep preemption**: horizon 6-12, multiple queued shifts. Same skeleton, strictly
   more positioning power on the identical tape.
4. Keep V15.5 runtime layer for general play (already beats salemali7 live: 1628 vs 842).

### Files
- Replays: `results/replays/episode-{91177983,91178526,91179399,91180265}-replay.json`
- Theft map (local, 6 games): `results/theft_map_summary.txt`
- Agent source: `agents/salemali7_3000score.py` (lines 199-290 = repay/preempt)
