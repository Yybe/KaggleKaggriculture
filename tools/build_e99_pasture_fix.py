"""Build E99: E94 + immediate replay of weed-deferred BUILD_PASTURE.

Defect (local repro seed 1898931754 seat1, live ep111596738 class A', -5,585):
tape step 33 hand1 = BUILD_PASTURE at (4,2); a WEED spawned there, so _weed_repair
queues (pos, BUILD_PASTURE) and emits DIG. DIG clears the weed, but the replay
branch only fires on no-op tape actions and the tape's next act is a MOVE, so the
unit walks away and the queue is dropped -> pasture lost until step ~88.

Fix: in _weed_repair, when the queued head is BUILD_PASTURE, its tile is now None
and the unit still stands on it, replay the build immediately, overriding the
tape's move (cost: one move delayed; gain: free pasture ~55 steps earlier).

Pins E94 md5, exact-match-once anchor, compiles, asserts EOF anchor.
Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e99_pasture_fix.py
"""
import hashlib
import pathlib
import py_compile
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
SRC = BASE / "agents" / "pub_e94_omw_clean.py"
DST = BASE / "agents" / "pub_e99_pasture_fix.py"
SRC_MD5 = "398eadad5d61d54d6a2c5d6a30f93c18"

ANCHOR = """            if act and act[0] in ("PLANT", "BUILD_COOP", "BUILD_PASTURE") and is_weed:
                pending.setdefault(i, []).append((pos, act))
                act = ["DIG"]
            elif queue and noop:
"""

PATCH = """            if act and act[0] in ("PLANT", "BUILD_COOP", "BUILD_PASTURE") and is_weed:
                pending.setdefault(i, []).append((pos, act))
                act = ["DIG"]
            elif queue and queue[0][1][0] == "BUILD_PASTURE" and tile is None and act and act[0] in MOVES:
                # E99: DIG cleared the weed; build the queued pasture before the tape walks the unit away
                queue.pop(0)
                act = ["BUILD_PASTURE"]
                if not queue:
                    pending.pop(i, None)
            elif queue and noop:
"""


def main():
    src_bytes = SRC.read_bytes()
    got = hashlib.md5(src_bytes).hexdigest()
    assert got == SRC_MD5, f"E94 md5 mismatch: {got}"
    text = src_bytes.decode("utf-8")
    crlf = "\r\n" in text
    if crlf:
        text = text.replace("\r\n", "\n")
    assert text.count(ANCHOR) == 1, f"anchor count {text.count(ANCHOR)}"
    out = text.replace(ANCHOR, PATCH)
    assert "kaggle_submission_agent = agent" in out[-200:], "EOF anchor missing"
    if crlf:
        out = out.replace("\n", "\r\n")
    DST.write_bytes(out.encode("utf-8"))
    py_compile.compile(str(DST), doraise=True)
    print("wrote", DST, "md5", hashlib.md5(DST.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
