"""Build E100: E99 + front_run activated with mirror opponent plan.

Class B live loss (ep111662271, alban beat Apex -1,473 by selling 1-3h earlier at
day-28 settlements) used OMW's front_run layer. E94/E99 carry the full _front_run
implementation but disabled: settings front_run=False and factory opponent_plan=None.
Live-viable activation: assume the opponent mirrors our own active route tape
(the live pool is spine clones per E98F forensics), so plan = self.routes[route].

Note: sell_lead (already True) promotes our own next-step lots too, and _front_run
skips items already scheduled this step -> the graft may be redundant; the gate
decides (inert = drop).

Pins E99 md5, exact-match-once anchors, compiles, asserts EOF anchor.
Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e100_front_run.py
"""
import hashlib
import pathlib
import py_compile
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
SRC = BASE / "agents" / "pub_e99_pasture_fix.py"
DST = BASE / "agents" / "pub_e100_frontrun.py"
SRC_MD5 = "92fde71c2aef844847f86d94f6b52c2f"

SUBS = [
    # 1. enable the layer
    ("'front_run': False}", "'front_run': True}"),
    # 2. drop the opponent_plan precondition at the call site
    ('if cfg["front_run"] and self.opponent_plan:', 'if cfg["front_run"]:'),
    # 3. mirror plan: opponent assumed to replay our own active route tape
    ("        plan = self.opponent_plan\n",
     "        plan = self.opponent_plan if self.opponent_plan is not None else self.routes.get(route)\n"
     "        if not plan:\n"
     "            return\n"),
]


def main():
    src_bytes = SRC.read_bytes()
    got = hashlib.md5(src_bytes).hexdigest()
    assert got == SRC_MD5, f"E99 md5 mismatch: {got}"
    text = src_bytes.decode("utf-8")
    crlf = "\r\n" in text
    if crlf:
        text = text.replace("\r\n", "\n")
    for old, new in SUBS:
        assert text.count(old) == 1, f"anchor count {text.count(old)} for {old[:50]!r}"
        text = text.replace(old, new)
    assert "kaggle_submission_agent = agent" in text[-200:], "EOF anchor missing"
    if crlf:
        text = text.replace("\n", "\r\n")
    DST.write_bytes(text.encode("utf-8"))
    py_compile.compile(str(DST), doraise=True)
    print("wrote", DST, "md5", hashlib.md5(DST.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
