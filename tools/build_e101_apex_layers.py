"""E101 = E99 pasture-fix spine + Apex V5 market-interaction layers (append-only graft).

Ports the two mechanisms that removed Apex V5's mirror ties, verified independently on
the Apex gate banks: E99 vs pub_apex_v5 = 1W/7L/0T (R1, -31.0), 3W/5L/0T (R2, +53.4),
5W/11L/0T (Fresh, -47.2). Zero ties on all 3 banks; E99 produced 8/8 ties vs its own mirrors.

Layers added (unchanged from tools/build_apex_v5.py):
  _apex_tuned_clone_preemption  step%24==23 sell ahead of the clone wave, debt-accounted
  _apex_precision_terminal_sweep steps 716-719 full shed liquidation into open slots

Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e101_apex_layers.py
"""
import hashlib
import pathlib
import py_compile
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
SRC = BASE / "agents" / "pub_e99_pasture_fix.py"
DST = BASE / "agents" / "pub_e101_apex_layers.py"
LAYER_SRC = BASE / "agents" / "pub_apex_v5.py"

LAYER = '''

# ===========================================================================
# E101: APEX V5 MARKET-INTERACTION LAYERS grafted onto the E99 spine
# ===========================================================================
'''


def main():
    src = SRC.read_text(encoding="utf-8")
    v5 = LAYER_SRC.read_text(encoding="utf-8")
    start = v5.index("_V5_ITEMS =")
    end = v5.rindex("kaggle_submission_agent = agent")
    assert end > start, "marker order wrong in pub_apex_v5.py"
    layer = v5[start:end].rstrip()
    for sym in ("_apex_tuned_clone_preemption", "_apex_precision_terminal_sweep",
                "_V5_PARENT = agent", "del agent", "def agent(observation, configuration=None)"):
        assert sym in layer, f"layer missing {sym!r}"
    assert src.count("kaggle_submission_agent = agent") == 1, "E99 EOF marker not unique"
    body, tail = src.rsplit("kaggle_submission_agent = agent", 1)
    out = body + LAYER + "\n\n" + layer + "\n" + "kaggle_submission_agent = agent" + tail
    for sym in ("_apex_tuned_clone_preemption", "_apex_precision_terminal_sweep"):
        assert out.count(sym) == 2, f"{sym} not wired into {DST.name}"
    DST.write_text(out, encoding="utf-8", newline="\r\n" if "\r\n" in src else "\n")
    py_compile.compile(str(DST), doraise=True)
    print("wrote", DST.name, "md5", hashlib.md5(DST.read_bytes()).hexdigest(), len(out), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
