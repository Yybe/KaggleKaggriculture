"""Extract agent code from a kaggle kernel notebook into a standalone .py file.

Usage: python extract_kernel_agent.py <notebook.ipynb> <out.py>
Dumps all code cells in order, then reports which functions are defined
(def agent / def _kaggle_submission_entrypoint / classes)."""
import json, sys, re, io

def main():
    nb_path, out_path = sys.argv[1], sys.argv[2]
    with io.open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb.get("cells", [])
    code = []
    for c in cells:
        if c.get("cell_type") == "code":
            src = "".join(c.get("source", []))
            code.append(src)
    blob = "\n\n# ==== cell ====\n\n".join(code)
    with io.open(out_path, "w", encoding="utf-8") as f:
        f.write(blob)
    print(f"wrote {out_path}: {len(code)} code cells, {len(blob)} chars")
    # report function defs
    for m in re.finditer(r"^\s*(?:def|class)\s+(\w+)", blob, re.M):
        print("  def/class:", m.group(1))

if __name__ == "__main__":
    main()
