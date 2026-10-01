"""Ablation: decem_sovereign_v12 WITHOUT the step-192/312 desync buys.

v12 = lean_wflip_v9_standalone + CXTB=7000 + two guarded 1-unit WHEAT buys.
The desync buys have never been ablated on this spine. Removing the whole
DS12 layer from v12 is exactly equivalent to rebuilding the parent with
CXTB=7000, so we build from the parent to keep the diff auditable.
"""
import hashlib
import os

ROOT = r"C:\Users\xxshi\Desktop\farmmasterV2"
SRC = os.path.join(ROOT, "agents", "lean_wflip_v9_standalone.py")
DST = os.path.join(ROOT, "agents", "decem_nodesync.py")
NEEDLE = "_CXTB_MIN_REVENUE = 8000"
REPL = "_CXTB_MIN_REVENUE = 7000"

text = open(SRC, encoding="utf-8").read()
assert text.count(NEEDLE) == 1, text.count(NEEDLE)
assert "LAYER DECEM_SOVEREIGN" not in text
out = text.replace(NEEDLE, REPL)
assert out.count(REPL) == 1 and NEEDLE not in out

with open(DST, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)

a, b = text.splitlines(), out.splitlines()
diff = [i for i in range(len(a)) if a[i] != b[i]]
print("built", DST)
print("sha", hashlib.sha256(open(DST, "rb").read()).hexdigest()[:16])
print("lines changed:", len(diff), "->", [(i + 1, a[i].strip(), b[i].strip()) for i in diff])
