"""Extract battle-ready agents from the two pulled notebooks."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTEBOOKS = HERE.parent / "notebooks"


def extract_writefile(nb_path, out_path):
    nb = json.load(open(nb_path, encoding="utf-8"))
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if src.strip().startswith("%%writefile"):
            lines = src.splitlines()
            # magic line: %%writefile main.py
            target = lines[0].split(None, 1)[1].strip()
            body = "\n".join(lines[1:]).lstrip("\n")
            (HERE / "boatlee_v16rc2").mkdir(exist_ok=True)
            (HERE / out_path).write_text(body, encoding="utf-8")
            print(f"extracted {target} ({len(body)} chars) -> {out_path}")
            return True
    return False


def dump_cells(nb_path, out_path):
    nb = json.load(open(nb_path, encoding="utf-8"))
    with open(out_path, "w", encoding="utf-8") as f:
        for i, c in enumerate(nb["cells"]):
            src = "".join(c["source"])
            f.write(f"\n{'='*20} cell {i} ({c['cell_type']}, len {len(src)}) {'='*20}\n")
            f.write(src[:6000])
            if len(src) > 6000:
                f.write(f"\n... [truncated, total {len(src)}] ...\n")
    print(f"dumped cells -> {out_path}")


ok = extract_writefile(
    NOTEBOOKS / "v16-rc2-high-score-near-mirror-market-relay.ipynb",
    "boatlee_v16rc2/main.py",
)
print("boatlee writefile cell:", ok)

dump_cells(
    NOTEBOOKS / "25-27-strict-future-v27-midgame-meta-reset.ipynb",
    HERE / "kaitofukami_notebook_dump.txt",
)