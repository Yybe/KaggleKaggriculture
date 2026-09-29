"""E256 p02 - download the replays our tetsutani files LOST (and win controls), zlib cached.

Reads out/episodes_<ref>.csv from p01. Losses sorted by worst margin first.
Cap per ref so the box does not drown (each replay is ~35 MB unpacked).
"""
import csv
import json
import os
import sys
import time
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from fetch_episodes import get_replay  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
RAW = os.path.join(HERE, "raw")
CAP = {"56672630": 14, "56653474": 18, "56644648": 8}
CTRL = 4  # winning controls per ref (same opponent where possible)


def _retry(fn, *a, attempts=6, **kw):
    delay = 5
    for _ in range(attempts):
        try:
            return fn(*a, **kw)
        except Exception as exc:  # noqa: BLE001
            if "429" not in str(exc):
                raise
            print("429 sleep %ds" % delay, flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 120)
    raise RuntimeError("rate limited")


def load(ref):
    p = os.path.join(OUT, "episodes_%s.csv" % ref)
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    for r in rows:
        r["margin"] = float(r["margin"])
        r["our_reward"] = float(r["our_reward"])
        r["opp_reward"] = float(r["opp_reward"])
    return rows


def main():
    os.makedirs(RAW, exist_ok=True)
    index_rows = []
    for ref, cap in CAP.items():
        rows = load(ref)
        losses = sorted([r for r in rows if r["outcome"] == "L"], key=lambda r: r["margin"])[:cap]
        wins = sorted([r for r in rows if r["outcome"] == "W"], key=lambda r: -r["margin"])[:CTRL]
        for kind, sel in (("L", losses), ("W", wins)):
            for r in sel:
                ep = int(r["episode"])
                path = os.path.join(RAW, "ep_%d.json.zlib" % ep)
                if not (os.path.exists(path) and os.path.getsize(path) > 500):
                    try:
                        rep = _retry(get_replay, ep)
                    except Exception as exc:  # noqa: BLE001
                        print("FAIL", ep, exc, flush=True)
                        continue
                    payload = rep.get("replay") if isinstance(rep, dict) and "replay" in rep else rep
                    open(path, "wb").write(zlib.compress(json.dumps(payload).encode("utf-8"), 6))
                    time.sleep(0.5)
                index_rows.append({
                    "episode": ep, "ref": ref, "label": r["label"], "kind": kind,
                    "margin": r["margin"], "our_reward": r["our_reward"], "opp_reward": r["opp_reward"],
                    "opp_sid": r["opp_sid"], "opp_team": r["opp_team"], "opp_name": r["opp_name"],
                    "our_seat": r["our_seat"], "create": r["create"],
                    "file": os.path.basename(path),
                    "bytes": os.path.getsize(path) if os.path.exists(path) else 0,
                })
                print("ok", ref, kind, ep, "%.0f" % r["margin"], r["opp_name"], flush=True)
    with open(os.path.join(OUT, "replay_index.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(index_rows[0].keys()))
        w.writeheader()
        w.writerows(index_rows)
    print("TOTAL", len(index_rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
