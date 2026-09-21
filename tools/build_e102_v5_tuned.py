"""E102 = Apex V5's OWN spine with only the preemption floors retuned (90/30/140).

E101/E101t put the tuned layers on the E99 spine and still lost to Apex V5
(r1 0W/1L/7T -9.2, fresh 0W/3L/13T -11.8): the E99 spine is worth less than V5's
h20/V219/Gluzdov/OW stack, so the retune must be applied on top of V5, not E99.
Same-spine ablation => every delta in the gate is purely the floor change.

Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e102_v5_tuned.py
"""
import hashlib
import pathlib
import py_compile
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
SRC = BASE / "agents" / "pub_apex_v5.py"

OLD = 'floor = 75 if item == "FERTILIZER" else (20 if item == "WHEAT" else 80)'
TUNED = {
    # R2 sweep: ctrl -54.2 (5W/3L), f85 +36.0 (tail -265 survives), f90/f95 +82.2 (7W/1L/0T),
    # f110 +36.1, f130 inert (0W/0L/8T). Plateau = 140..160 on the "other" floor.
    "f90": 'floor = 90 if item == "FERTILIZER" else (30 if item == "WHEAT" else 140)',
    "f95": 'floor = 95 if item == "FERTILIZER" else (32 if item == "WHEAT" else 160)',
}


def main():
    src = SRC.read_text(encoding="utf-8")
    assert src.count(OLD) == 1, f"floor anchor count {src.count(OLD)} != 1"
    for tag, new in TUNED.items():
        out = src.replace(OLD, new)
        assert out.count(new) == 1 and OLD not in out
        dst = BASE / "agents" / f"pub_e102_v5_{tag}.py"
        dst.write_text(out, encoding="utf-8", newline="\r\n" if "\r\n" in src else "\n")
        py_compile.compile(str(dst), doraise=True)
        print(f"wrote {dst.name} {len(out)}B (base {len(src)}B) md5={hashlib.md5(out.encode()).hexdigest()[:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
