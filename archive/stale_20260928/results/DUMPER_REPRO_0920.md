# DUMPER REPRO 2026-09-20 — does `pub_metav4_early` lose locally to the 3 live dump-sell losers?

Question: the live scout `pub_metav4_early` (sid 56387781) lost three games whose margin was made
by **endgame dump-sells** — 涵哥 ep111231254 (−24,593), kwa ep111248647 (−2,531), THIRD FARM CLUB
ep111281893 (−7,411). Can the local bench reproduce that loss class, so an overlay has an A/B target?

## 0. Harness correction

`tools/gate_eval.py` is **not** the gate — it is a legacy V15 sell-threshold analyser (hard-wired to
`agents/kaggle_champion_v15.py`, no challenger/opponent arguments). The real gate runner is
`tools/diag_bench_seeds.py <agent_a> <agent_b> <seed_csv> <out.txt> --interval 24`: 8 seeds × both
seats = 16 games, and every number below is `a − b` with `a` = the champion always (seat swap only
permutes physical seats, so `Mean Delta` is champ-relative). Interpreter is the pinned
`WybeV2/rank_env/Scripts/python.exe` → `kaggle_environments 1.32.7` (verified; matches the env
`crop_gate8.sh` / `dumper_bench_0920.sh` use). Nothing was installed, upgraded, or submitted.

## 1. Tape provenance (step 1)

| needed opponent | episode | tape in `agents/live_replay/` | status |
|---|---|---|---|
| 涵哥 | 111231254 | `opp_涵哥_29ee77a6.py` | present, header `Source: episode-111231254-replay.json`, rewards `[121217, 145810]` ✓ |
| kwa | 111248647 | `opp_kwa_67f80680.py` | present, `Source: episode-111248647-replay.json`, rewards `[120071, 122602]` ✓ |
| THIRD FARM CLUB | 111281893 | **`opp_THIRD_FARM_CLUB_f5afac52.py`** | **was missing — extracted this pass** |

The three pre-existing TFC tapes were all the *old* 56354460 board (`ed81ab50`←ep110773945,
`67d48464`←ep110772841, `21154212`←ep110771570, the last of which is a TFC-vs-TFC game), exactly as
`LIVE_FORENSICS_20260920B.md` §5 warned. Fresh extraction (the only file added under `agents/`):

```
WybeV2/rank_env/Scripts/python.exe tools/extract_live_opponents.py \
  results/live_replays_0920b/episode-111281893-replay.json agents/live_replay
-> agents/live_replay/opp_THIRD_FARM_CLUB_f5afac52.py steps=720
   teams=['Shivam_2212', 'THIRD FARM CLUB'] rewards=[84773.0, 92184.0] our_seat=0
```

Rewards reproduce the live −7,411 margin, so the tape is the right board (56395336, 13:18Z submission).

## 2. Gate table — champ vs each tape, standard 8 gate seeds, interval 24

Seeds: `1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000`. W-L-T is out of 16 games
(8 seeds × 2 seats); seed-level in brackets. Mean margin is champion-relative (positive = champ ahead).

| opponent tape | episode | live margin | W-L-T vs champ (seed-level) | mean margin px | tape avg | tape's LIVE score | verdict |
|---|---|---|---|---|---|---|---|
| `opp_涵哥_29ee77a6` | 111231254 | −24,593 | **16W-0L-0T** (8W-0L-0T) | **+111,887** | 32,630 | 145,810 | champ wins locally — **no repro** |
| `opp_kwa_67f80680` | 111248647 | −2,531 | **16W-0L-0T** (8W-0L-0T) | **+102,544** | 47,896 | 122,602 | champ wins locally — **no repro** |
| `opp_THIRD_FARM_CLUB_f5afac52` (new) | 111281893 | −7,411 | **16W-0L-0T** (8W-0L-0T) | **+97,264** | 43,080 | 92,184 | champ wins locally — **no repro** |
| CONTROL `opp_DECEM_d73a2886` (old board) | 106429931 | won live | **16W-0L-0T** (8W-0L-0T) | +77,212 | 50,970 | 106,345 | control behaves as documented (16W/0L) ✓ |
| extra: `opp_TFC_ed81ab50` (old board) | 110773945 | n/a | 16W-0L-0T | +71,642 | 56,299 | 184,265 | no repro |
| extra: `opp_tamura_aicon_d45969a0` (dump family) | 111268157 | −477 | 16W-0L-0T | +107,704 | 36,487 | 67,134 | no repro |
| extra: `opp_Yanis_Belami_03d5c442` (dump family) | 111242519 | −2,255 | 16W-0L-0T | +106,894 | 29,581 | 107,823 | no repro |
| extra: `opp_JamesJJJJJ_2802d824` | 111271440 | −149 | 16W-0L-0T | +104,938 | 37,535 | 120,988 | no repro |

The control confirms the harness is healthy and its prior behaviour is intact: DECEM is the tape
`V35_V36_LEDGER_20260911.md` already flagged as "extracted but replays **state-divergent**". All
three live killers land in the same place as that control and as every other tape — champ 16/0.
Raw outputs: `results/dumper_repro_0920/gate8_vs_*.txt`, log `results/dumper_repro_0920/repro_sweep.log`.

## 3. Per-seed margins (champ − tape)

| seed | 涵哥 | kwa | TFC (new) | DECEM (ctrl) |
|---|---|---|---|---|
| 1000000 | +107,480 | +143,301 / +142,271 | +109,083 | +72,004 |
| 2000000 | +104,323 | +84,338 | +100,125 | +90,114 |
| 3330000 | +99,266 | +70,841 | +71,824 | +78,855 |
| 5000000 | +98,206 | +81,867 | +90,689 | +56,796 |
| 6000000 | +124,978 | +127,426 | +70,473 | +83,458 |
| 7770000 | +131,134 | +105,644 | +119,379 | +76,623 |
| 8000000 | +115,975 | +105,773 | +106,080 | +81,064 |
| 9000000 | +113,736 | +101,681 | +110,458 | +78,782 |

(One row, kwa seed 1000000, differs by seat: +143,301 on seat 0 vs +142,271 on seat 1. Every other
cell is identical across both seats — the tape and the champ barely interact, see §4.)

## 4. Why it does not reproduce — the collision channel exists but is un-inventoried

Single-game probe at seed 1000000, same config:

| opponent | champ score | tape score | champ's loss vs a zero-pressure opponent |
|---|---|---|---|
| `opp_涵哥_29ee77a6` | 149,413 | 41,933 | −4,993 (final px WHEAT 45, CARROT 37, FERT 28, WOOL 1) |
| `pass` (does nothing) | 154,406 | 3,000 | 0 (final px WHEAT 46, CARROT 26, FERT 47, WOOL 238) |

* The tape's dump **schedule fires verbatim**: it still *requests* 84,401 sell units on days 28–30
  (live: 84,435), and that is enough to move the price board — the champion gives up ~5.0k, and
  WOOL collapses 238→1 while FERTILIZER drops 47→28. So the mechanism is real and detectable.
* But requests are capped by holdings, and on a fresh board the frozen tape never builds the stock:
  it ends at 32.6k–47.9k against a live 92k–146k. Its days 1–27 choreography is schedule-driven, so
  it mis-hires, mis-plants and arrives at d28 with an empty shed. Nothing to dump → no −24.6k swing.
* Net: bench delivers **+111,887** where live delivered **−24,593** — a ~136k error, i.e. two orders
  of magnitude past the margin being chased. Seat-swap invariance (§3) is the fingerprint: a real
  dump collision would shift the champion's score when seats swap, and it does not.

## 5. Verdict

**No — the endgame dump-collision loss class is NOT reproducible on the local bench via frozen-tape
replay, so a raw opp tape cannot serve as the overlay's A/B target.** All three live killers lose
16/0 to the champion by +97k to +112k, indistinguishable from the historically-safe DECEM control,
because the schedule-only tape reaches days 28–30 with ~33k–48k of bank instead of its live
92k–146k and therefore dumps an empty shed. The dump **channel** itself is present and measurable
(~5.0k of price pressure on the champion, WOOL 238→1), so the overlay should be gated against an
**inventory-faithful** opponent rather than a tape: either fork the live episode at day ~24 and
re-run only days 25–30 (real board, real stock, both agents live), or use a scripted
"hold-and-dump" adversary that is *forced* to carry the live endgame inventory into d28–30.

## 6. Reusable command lines

```bash
# gate8: champ vs one tape (a = champ always; Mean Delta is champ-relative)
WybeV2/rank_env/Scripts/python.exe tools/diag_bench_seeds.py \
  agents/pub_metav4_early.py agents/live_replay/opp_THIRD_FARM_CLUB_f5afac52.py \
  "1000000,9000000,3330000,7770000,5000000,6000000,8000000,2000000" \
  results/dumper_repro_0920/gate8_vs_opp_THIRD_FARM_CLUB_f5afac52.txt --interval 24

# batch driver used for the whole table
bash tools/dumper_repro_final_0920.sh

# re-extract a live episode into a tape (only writes into agents/live_replay/)
WybeV2/rank_env/Scripts/python.exe tools/extract_live_opponents.py \
  results/live_replays_0920b/episode-<EP>-replay.json agents/live_replay
```
