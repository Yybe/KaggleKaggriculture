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

## For the operator

Two IDEs are editing `submission.py` in one working tree. It is the file that actually ships, and
right now the worktree copy and the committed copy disagree, so **whatever is submitted from this
directory is the v9/3 file, not `5b80e8c`'s FutureV1.** Recommend either (a) one IDE owns
`submission.py` and the other writes candidates to `agents/` only, or (b) separate worktrees. CODER
is not going to resolve it unilaterally.
