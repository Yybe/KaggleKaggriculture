"""Decode kaitofukami v27 agent: cell 11 base85+zlib blob -> main.py (SHA-256 verified)."""
import ast
import base64
import hashlib
import json
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
NB = HERE.parent / "notebooks" / "25-27-strict-future-v27-midgame-meta-reset.ipynb"
OUT_DIR = HERE / "kaitofukami_v27"
EXPECTED_SHA = "f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8"
EXPECTED_SIZE = 20813

nb = json.load(open(NB, encoding="utf-8"))
src = "".join(nb["cells"][11]["source"])
tree = ast.parse(src)
parts = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == "_AGENT_B85_PARTS" for t in node.targets
    ):
        parts = ast.literal_eval(node.value)
        break
assert parts is not None, "_AGENT_B85_PARTS assignment not found"

raw = zlib.decompress(base64.b85decode("".join(parts).encode("ascii")))
print(f"decoded: {len(raw)} bytes (expected {EXPECTED_SIZE}), "
      f"sha256: {hashlib.sha256(raw).hexdigest()}")
assert len(raw) == EXPECTED_SIZE
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA

compile(raw, "main.py", "exec")  # syntax check
OUT_DIR.mkdir(exist_ok=True)
(OUT_DIR / "main.py").write_bytes(raw)
print(f"wrote {OUT_DIR / 'main.py'} ({len(raw)} bytes)")