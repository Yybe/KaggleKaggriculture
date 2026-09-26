"""E213: v9-fert day-gate doses — the E212 probe's mechanism.

E212 (fert stock probe, results/e212_fert_stock_probe.txt) showed the spine
COLLECTS fert continuously from day 1 but applies ZERO until day 13-14 while
13-18 units sit idle in the shed — and the p6 top-vs-top anatomy plus the p8
loss classes both fingerprint winners as fert-heavier (+55 median, 20/25 games
at the top; +38 median in 8 clone-tier losses). The applying layer is the v9
FERT block: it converts WATER commands on age-1 WHEAT/CARROT into FERTILIZE,
gated by `V9_FERT_FIRST_DAY = 14` and `V9_FERT_AGES = (1,)`.

Doses (one mechanism: widen the application window; built on the E210 stack so
the composed candidate is testable as-is):
  * cha22_e213_f11.py  FIRST_DAY 14 -> 11  (the idle-stock days the probe saw)
  * cha22_e213_f12.py  FIRST_DAY 14 -> 12
  * cha22_e213_a12.py  AGES (1,) -> (1, 2) (last-chance fert inside the 2-day window)

Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e213_fert_doses.py
"""
import importlib.util
import os
import py_compile
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "agents", "cha22_e210_straw_h13q6.py")

ANCHORS = ('V9_FERT_FIRST_DAY = 14', 'V9_FERT_AGES = (1,)',
           'V9_FERT_CROPS = ("WHEAT", "CARROT")')

VARIANTS = [
    ("cha22_e213_f11.py", {("V9_FERT_FIRST_DAY = 14", "V9_FERT_FIRST_DAY = 11")}),
    ("cha22_e213_f12.py", {("V9_FERT_FIRST_DAY = 14", "V9_FERT_FIRST_DAY = 12")}),
    ("cha22_e213_a12.py", {("V9_FERT_AGES = (1,)", "V9_FERT_AGES = (1, 2)")}),
]


def build(dst_name, swaps):
    dst = os.path.join(BASE, "agents", dst_name)
    with open(SRC, encoding="utf-8", newline="") as fh:
        base = fh.read()
    for a in ANCHORS:
        assert base.count(a) == 1, "anchor not unique (%d) in %s: %s" % (base.count(a), SRC, a)
    out = base
    for old, new in swaps:
        assert out.count(old) == 1
        out = out.replace(old, new)
    with open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    py_compile.compile(dst, doraise=True)
    spec = importlib.util.spec_from_file_location("chk_" + dst_name[7:-3], dst)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    assert mod.V9_FERT_CROPS == ("WHEAT", "CARROT"), "crops mutated"
    assert mod.agent is not None and callable(mod.agent)
    print("WROTE agents/%-22s swaps=%s  bytes %+d" % (dst_name, sorted(swaps), len(out) - len(base)), flush=True)


def main():
    for v in VARIANTS:
        build(*v)


if __name__ == "__main__":
    main()
