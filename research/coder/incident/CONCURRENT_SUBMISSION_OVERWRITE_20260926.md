# INCIDENT — concurrent `submission.py` overwrite by a parallel session (2026-09-26)

## What was found

While committing `tools/p28_tape_divergence.py` (commit `6c23aeb`), `git status` reported
` M submission.py` with the worktree file at **508,860 B** against `HEAD:submission.py` at
**1,086,993 B** (FutureV1, commit `5b80e8c`). Diff: +1370 / −1227 lines, i.e. a wholesale rewrite.

Worktree file header (verbatim first lines):

```
# Kaggriculture submission v9/3: public V39 (Apache-2.0, notices below) plus the v9 layers
# RACEPX gate, RACE (reservation from step 192, horizon 40 / margin 12), COURIER, CARROT and HERD
# appended at the end of this file.
# EXP-173 isolate opening market sequence inspired by yhay81/shop-router-0911-simple (Apache-2.0).
# Kaggriculture EXP-167 candidate. Not submitted automatically.
```

## Verdict: NOT the `agents/_e98f` clobber

| test | cropsense clobber (earlier today) | this event |
|---|---|---|
| size | 9,155 B | 508,860 B |
| stray `main.py` / `submission.tar.gz` | yes, both written | **absent** |
| "Ready to upload submission.tar.gz" printed | yes | no evidence |
| content | unrelated file with no `agent` attribute | a real v9/3 / V39-lineage candidate that says "Not submitted automatically" |

Timestamp `2026-09-26 23:26:03 +0530` = **17:56:03 UTC**, i.e. ~2 min *before* the CODER background
agent for CQ-7 was launched (17:57:42 UTC) and ~8.5 h after the `cropsense` incident was contained.
So the writer is a **second live session working in this same working tree** (the
"parallel-account session" already noted in `git log`), writing its own candidate — consistent with
OpenCode's rows in `research/SUBAGENT_REGISTRY.md`.

## Actions taken

* **Nothing restored.** `git checkout -- submission.py` would have destroyed the other session's
  in-progress work. The file is left exactly as that session wrote it.
* CODER's commit staged 5 explicit paths only; verified `git show --stat HEAD` contains
  `tools/p28_tape_divergence.py`, `results/p28_tape_divergence/REPORT.md`,
  `results/p28_tape_divergence/p28_per_seat_item.csv`, `results/p28_run.log`,
  `research/SUBAGENT_REGISTRY.md` — and **`git cat-file -s HEAD:submission.py` = 1,086,993**, so
  the overwrite was NOT committed and the git-tracked champion is intact.
* Side effect to note: `research/SUBAGENT_REGISTRY.md` committed as 207 insertions rather than the
  ~30 lines CODER appended, because the append-only file also carried the parallel sessions'
  uncommitted rows. Their content is preserved, now under CODER's commit message.

## No submit, no deploy

CODER called no submission mechanism this cycle. §23/§24 and the standing operator constraint hold:
no submits, no deploys, no `submission.py` change without the operator's explicit per-action
permission.

## CORRECTION, issued 2026-09-27 after verifying rather than inferring

**The characterisation above is wrong in its central claim.** Direct comparison:

```
agents/cha22_e199_lo96q8.py  sha1 ec0f0edc2ce2740fc8ee01df792c3a9807b83337  508,860 B
submission.py                sha1 ec0f0edc2ce2740fc8ee01df792c3a9807b83337  508,860 B
BYTE-IDENTICAL: True
```

The worktree `submission.py` is **`cha22_e199_lo96q8`, our own preempt-only line** — the file
`research/CHAMPION.md:27` records as `sha1 EC0F0EDC2CE2, 508,860 B, author: CODER`. The header text I read
as identifying a foreign lineage ("submission v9/3", "RACEPX/RACE/COURIER/CARROT/HERD", "EXP-167
candidate") is present **inside e199's own source** (13 matching lines), inherited from the donor stack. It
identified nothing. **This was a promotion of our best-supported finals candidate into the shipping file,
not a hostile or accidental overwrite by another lineage.** I should have hashed the two files before
writing the incident; the size match was already in front of me.

What is actually true and still needs the operator's decision:

1. `HEAD:submission.py` is **FutureV1** (1,086,993 B, `5b80e8c`) while the worktree file is **e199**
   (508,860 B). **Whatever is submitted from this directory today is e199, not the committed file.** That
   is probably the *right* content — `CHAMPION.md` states e199 is "the best-supported line for a
   win-rate-judged finals", with gate evidence 93.8% / 87.5% bands, +336.9 on 12/12, +559.0 (8W/0L), and
   drain R1 8W/0L/0T +660.8 — but the promotion was not authorised by the operator and the git record and
   the shipping file disagree.
2. **`agents/cha22_e199_lo96q8.py` is UNTRACKED.** It is now, doubly, the file to protect: it is both the
   recommended finals line and the actual shipping content, and a single `git clean -fd` deletes it. Same
   status for `agents/cha22_champion.py`, `agents/cha22_e206_mw_h1q6.py`, `agents/sluice_topup7.py` and
   `research/baselines/`. Only `cha22_e210_straw_h13q6.py` is tracked. The sibling repo has zero tracked
   `cha22` files.
3. Nothing in the original report's *safety* conclusions changes: no upload occurred, no submission
   mechanism was called by CODER, `submission.py` was left untouched by me, and `HEAD` is intact. The
   `agents/_e98f/cropsense` clobber (9,155 B + stray `main.py`/`submission.tar.gz`) remains a separate,
   genuinely hostile event from earlier today; the two must not be conflated.

Method law taken from this mistake: **hash before you narrate.** The incident report was written from a
size/header comparison when a one-line `sha1` comparison against the candidate directory was available and
would have settled it in two seconds.

## Independent corroboration of the unobtainable control

The CQ-6 subagent that had been dispatched to find the us-vs-top-13 episode died at its turn limit, and its
last verified statement supports the blocker rather than contradicting it: **0 top-13 encounters in all 214
of our episodes** (checked against both p17's 13-team list and the live top-13). So the control p17 called
impossible is now measured across a larger sample than my own count, and the relocation of the question to
leader-vs-leader within-market pairs (`tools/p28_tape_divergence.py`) stands as the only available route.
