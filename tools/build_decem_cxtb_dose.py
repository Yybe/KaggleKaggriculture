"""Build CXTB dose variants of decem_sovereign_v12.py.

H-109 (knowledge/REJECTED_HYPOTHESES.md:2043-2068) measured the
_CXTB_MIN_REVENUE dial on the sibling s336 spine: 7k = +270.4/seat t 1.06
(noise), 9k = shipped optimum, 11k = -77.9/seat. decem_sovereign_v12 ships
7000, i.e. the losing end of a bracketed dial, and that constant is its ONLY
live lever.

This script changes exactly one line and asserts it.
"""
import hashlib
import os
import shutil

ROOT = r"C:\Users\xxshi\Desktop\farmmasterV2"
SRC = os.path.join(ROOT, "agents", "decem_sovereign_v12.py")
NEEDLE = "_CXTB_MIN_REVENUE = 7000"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def build(dst_name, new_line):
    dst = os.path.join(ROOT, "agents", dst_name)
    text = open(SRC, encoding="utf-8").read()

    # hard invariants on the source
    assert text.count(NEEDLE) == 1, f"expected exactly 1 needle, got {text.count(NEEDLE)}"
    assert "_CXTB_THEIR_UNITS = 0.75" in text
    assert "_CXTB_DRAIN_SLACK = 2.4" in text
    assert "_CXTB_OUR_UNITS = 20" in text

    out = text.replace(NEEDLE, new_line)
    assert out != text
    assert out.count(new_line) == 1
    assert NEEDLE not in out

    with open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)

    # verify the written file: only that one line differs from the parent
    a = text.splitlines()
    b = open(dst, encoding="utf-8").read().splitlines()
    assert len(a) == len(b), "line count changed"
    diff = [(i, a[i], b[i]) for i in range(len(a)) if a[i] != b[i]]
    assert len(diff) == 1, f"expected 1 changed line, got {len(diff)}"
    print(f"{dst_name:34s} {sha(dst)}  changed line {diff[0][0]+1}:")
    print(f"{'':34s}   - {diff[0][1]}")
    print(f"{'':34s}   + {diff[0][2]}")
    return dst


if __name__ == "__main__":
    print("source:", SRC, sha(SRC))
    build("decem_cxtb9k.py", "_CXTB_MIN_REVENUE = 9000")
    build("decem_cxtb8k.py", "_CXTB_MIN_REVENUE = 8000")
    print("done")
