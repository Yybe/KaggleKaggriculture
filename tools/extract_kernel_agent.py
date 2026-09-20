"""Triage + extract agent code from Kaggle kernel notebooks.

For a given .ipynb, reconstructs the submitted agent (main.py) from whichever
materialisation style the author used:
  A. `%%writefile main.py` magic cell
  B. base64 (+optional zlib/gzip, +optional tar.gz wrapper) blob literal in a cell
  C. a cell that writes a literal already present in the notebook

Usage:
  python tools/extract_kernel_agent.py <notebook.ipynb> <out.py> [--dump-list]
  python tools/extract_kernel_agent.py <notebook.ipynb> --blob     # show blob decode report
"""
import ast
import base64
import gzip
import hashlib
import io
import json
import re
import sys
import tarfile
import zlib


def cells(nb):
    return [(i, c) for i, c in enumerate(nb.get("cells", [])) if c.get("cell_type") == "code"]


def src(c):
    s = c.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def try_decompress(blob):
    """Return (text, how) for a bytes blob, trying zlib / gzip / tar.gz / raw."""
    tries = []
    raw = blob
    for name, fn in (("zlib", zlib.decompress), ("gzip", gzip.decompress),
                     ("b85zlib", lambda b: zlib.decompress(base64.b85decode(b))),
                     ("raw", lambda b: b)):
        try:
            data = fn(raw)
        except Exception:
            continue
        tries.append((name, data))
        raw = data
        if isinstance(data, (bytes, bytearray)) and data[:2] == b"\x1f\x8b" or (
                isinstance(data, bytes) and data[:5] == b"\x7fELF"):
            continue
    # tar.gz member extraction
    for name, data in tries:
        try:
            tf = tarfile.open(fileobj=io.BytesIO(data))
            names = tf.getnames()
            pick = [n for n in names if n.endswith(".py")]
            if pick:
                member = "main.py" if "main.py" in pick else pick[0]
                return tf.extractfile(member).read().decode("utf-8"), f"{name}->tar:{member} members={names}"
        except Exception:
            pass
    for name, data in tries:
        if b"def agent" in data[:200000] or data[:3] == b'"""':
            return data.decode("utf-8", errors="replace"), name
    return None, "undecoded"


def _literal_source_cells(nb):
    """Yield (cell_index, name, bytes) for module-level assignments whose value is
    a bytes literal (possibly b''.join([...])) — the V50 embedding style."""
    for i, c in cells(nb):
        s = src(c)
        try:
            tree = ast.parse(s)
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            tgt = node.targets[0]
            if not isinstance(tgt, ast.Name):
                continue
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                val = None
            if val is None:
                # b''.join((b'..', b'..')) -- V50 style
                v = node.value
                if (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute)
                        and v.func.attr == "join" and v.args):
                    base = v.func.value
                    if isinstance(base, ast.Constant) and isinstance(base.value, (bytes, bytearray)):
                        try:
                            parts = ast.literal_eval(v.args[0])
                        except Exception:
                            parts = None
                        if parts is not None:
                            val = base.value.join(bytes(p) for p in parts)
            if isinstance(val, (bytes, bytearray)) and len(val) > 5000:
                yield i, tgt.id, bytes(val)


def extract(path, out=None):
    nb = json.load(open(path, encoding="utf-8"))
    cs = cells(nb)
    # A: %%writefile main.py
    for i, c in cs:
        s = src(c)
        m = re.match(r"^%%writefile\s+(\S+)\s*\n", s)
        if m and m.group(1).endswith(".py") and "def agent" in s:
            body = s[m.end():]
            return body, f"writefile:{m.group(1)} (cell {i})", i
    # B0: module-level bytes literals (b'...' chunks joined) -- V50 style
    for i, name, data in _literal_source_cells(nb):
        text, how = try_decompress(data)
        if text and "def agent" in text:
            return text, f"bytes-literal {name} (cell {i}) via {how}", i
        if data[:4] in (b"# EX", b'"""', b"from", b" imp", b"impo", b"# Ka"):
            t = data.decode("utf-8", errors="replace")
            if "def agent" in t or "def _" in t:
                return t, f"bytes-literal {name} (cell {i}) raw", i
    # B1: str literals that are b85/b64 blobs -- master-engine-v4 / beat-v48 style
    for i, c in cs:
        s = src(c)
        try:
            tree = ast.parse(s)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            tgt = node.targets[0]
            if not isinstance(tgt, ast.Name):
                continue
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                continue
            if not isinstance(val, str) or len(val) < 1500:
                continue
            for dec in (base64.b85decode, base64.b64decode, base64.b32decode):
                try:
                    data = dec(val.encode())
                except Exception:
                    continue
                text, how = try_decompress(data)
                if text and "def agent" in text:
                    return text, f"str-literal {tgt.id} (cell {i}) via {dec.__name__}+{how}", i
                break
    # B2: base64 literal blob embedded in a call
    best = None
    for i, c in cs:
        s = src(c)
        for mm in re.finditer(r"[A-Za-z0-9+/=]{2000,}", s):
            blob = mm.group(0)
            if best is None or len(blob) > best[0]:
                best = (len(blob), i, blob)
    if best:
        try:
            decoded = base64.b64decode(best[2] + "=" * (-len(best[2]) % 4))
        except Exception:
            decoded = None
        if decoded:
            text, how = try_decompress(decoded)
            if text and "def agent" in text:
                return text, f"blob cell {best[1]} via {how}", best[1]
            return None, f"blob cell {best[1]} decoded via {how} (no def agent)", best[1]
    # C: any cell with a top-level def agent that is self-contained
    for i, c in cs:
        s = src(c)
        if re.search(r"^def agent\(", s, re.M):
            return s, f"raw cell {i}", i
    return None, "no agent found", None


def main():
    path = sys.argv[1]
    if "--dump-list" in sys.argv:
        nb = json.load(open(path, encoding="utf-8"))
        for i, c in cells(nb):
            s = src(c)
            print(i, len(s), repr(s.splitlines()[0][:90]) if s.strip() else "")
        return
    text, how, cell = extract(path)
    if text is None:
        print("FAIL:", how)
        return
    if "--blob" in sys.argv:
        print(how)
        lines = text.count("\n")
        print("lines:", lines, "sha256:", hashlib.sha256(text.encode()).hexdigest())
        for kw in ("ctypes", "CDLL", ".so", "def agent", "REQUIRED_ENGINE", "base64"):
            print(f"  {kw}: {text.count(kw)}")
        return
    out = sys.argv[2]
    ast.parse(text)
    open(out, "w", encoding="utf-8", newline="\n").write(text)
    print(f"wrote {out}  ({how})  bytes={len(text)} md5={hashlib.md5(text.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
