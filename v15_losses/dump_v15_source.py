"""Dump the exact source of kaggle_champion_v15.py to a log file for reliable reading."""
import io
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agents", "kaggle_champion_v15.py")
with io.open(path, "r", encoding="utf-8") as f:
    src = f.read()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v15_source_dump.log")
with io.open(out, "w", encoding="utf-8") as f:
    f.write("LINES: %d\n" % src.count("\n"))
    f.write("BYTES: %d\n" % len(src.encode("utf-8")))
    f.write("=" * 60 + "\n")
    f.write(src)
print("done")
