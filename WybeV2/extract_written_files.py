"""Extract %%writefile cell bodies from a notebook (real agent code).

Usage: python extract_written_files.py <notebook.ipynb> <out_dir>
Writes each %%writefile target to <out_dir>/<basename>."""
import json, sys, io, os, re

nb_path, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
with io.open(nb_path, encoding="utf-8") as f:
    nb = json.load(f)

for i, c in enumerate(nb.get("cells", [])):
    if c.get("cell_type") != "code":
        continue
    src = "".join(c.get("source", []))
    m = re.match(r"%%writefile\s+(\S+)", src)
    if m:
        target = os.path.basename(m.group(1))
        body = src[m.end():]
        out = os.path.join(out_dir, target)
        with io.open(out, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"cell {i}: {m.group(1)} -> {out} ({len(body)} chars)")
