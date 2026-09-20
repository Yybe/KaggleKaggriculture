"""Dump notebook cells (source + optional outputs) for extraction triage.

Usage:
  python tools/nb_dump.py <notebook.ipynb> [--full] [--grep PATTERN]

Prints per-cell: index, cell_type, exec_count, size, and the source (first 40
lines by default, all with --full). With --grep only prints cells whose source
matches the pattern.
"""
import json
import re
import sys


def main():
    path = sys.argv[1]
    full = "--full" in sys.argv
    grep = None
    if "--grep" in sys.argv:
        grep = re.compile(sys.argv[sys.argv.index("--grep") + 1], re.I)
    nb = json.load(open(path, encoding="utf-8"))
    for i, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        if grep and not grep.search(src):
            continue
        lines = src.splitlines()
        print(f"--- cell {i} [{cell.get('cell_type')}] chars={len(src)} lines={len(lines)} ---")
        show = lines if full else lines[:40]
        for ln in show:
            print("   |", ln)
        if not full and len(lines) > 40:
            print(f"   | ... ({len(lines)-40} more lines)")


if __name__ == "__main__":
    main()
