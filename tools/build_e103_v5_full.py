"""E103 = Apex V5 spine + retuned preemption floors (E102) + the E99 weed-deferred pasture replay.

The E99 patch is a spine fix (in _weed_repair), the retune is a market-layer constant, so they
compose. This builds both onto V5 and checks the anchors match exactly once.

Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e103_v5_full.py
"""
import hashlib
import pathlib
import py_compile
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
SRC = BASE / "agents" / "pub_e102_v5_f90.py"
DST = BASE / "agents" / "pub_e103_v5_full.py"

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
    text = SRC.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert text.count(ANCHOR) == 1, f"anchor count {text.count(ANCHOR)}"
    assert text.count('floor = 90 if item == "FERTILIZER"') == 1, "retuned floors missing"
    out = text.replace(ANCHOR, PATCH)
    assert out.count('act = ["BUILD_PASTURE"]') > text.count('act = ["BUILD_PASTURE"]'), "patch did not land"
    assert "kaggle_submission_agent = agent" in out[-200:], "EOF anchor missing"
    DST.write_text(out.replace("\n", "\r\n") if "\r\n" in SRC.read_text(encoding="utf-8") else out,
                   encoding="utf-8")
    py_compile.compile(str(DST), doraise=True)
    print("wrote", DST.name, len(out), "bytes md5", hashlib.md5(out.encode()).hexdigest()[:8])
    return 0


if __name__ == "__main__":
    sys.exit(main())
