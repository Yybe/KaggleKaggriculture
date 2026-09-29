"""E256 p02b - download replays our tetsutani files lost (+ win controls) via the CDN route.

GetEpisodeReplay 404s here (documented in p6_fetch_field.py / AGENTS.md ph2), so the fetch uses
https://www.kaggleusercontent.com/episodes/<id>.json.  Full replay stored zlib-9 in raw/.
"""
import csv
import json
import os
import sys
import time
import zlib

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
RAW = os.path.join(HERE, "raw")
CDN = "https://www.kaggleusercontent.com/episodes/%d.json"
CAP = {"56672630": 12, "56653474": 16, "56644648": 6}
CTRL = 3


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load(ref):
    rows = list(csv.DictReader(open(os.path.join(OUT, "episodes_%s.csv" % ref), encoding="utf-8")))
    keep = []
    for r in rows:
        r["margin"] = num(r["margin"])
        if r["margin"] is None:
            continue
        r["our_reward"] = num(r["our_reward"]) or 0.0
        r["opp_reward"] = num(r["opp_reward"]) or 0.0
        keep.append(r)
    return keep


def main():
    os.makedirs(RAW, exist_ok=True)
    idx = []
    for ref, cap in CAP.items():
        rows = load(ref)
        losses = sorted([r for r in rows if r["outcome"] == "L"], key=lambda r: r["margin"])[:cap]
        wins = sorted([r for r in rows if r["outcome"] == "W"], key=lambda r: -r["margin"])[:CTRL]
        for kind, sel in (("L", losses), ("W", wins)):
            for r in sel:
                ep = int(r["episode"])
                path = os.path.join(RAW, "ep_%d.json.zlib" % ep)
                status = "cached"
                if not (os.path.exists(path) and os.path.getsize(path) > 5000):
                    try:
                        resp = requests.get(CDN % ep, timeout=180)
                        if resp.status_code != 200 or len(resp.content) < 5000:
                            print("MISS", ep, resp.status_code, len(resp.content), flush=True)
                            continue
                        blob = json.dumps(resp.json(), separators=(",", ":")).encode("utf-8")
                        open(path, "wb").write(zlib.compress(blob, 9))
                        status = "fetched"
                        time.sleep(0.6)
                    except Exception as exc:  # noqa: BLE001
                        print("FAIL", ep, repr(exc)[:120], flush=True)
                        continue
                idx.append({
                    "episode": ep, "ref": ref, "label": r["label"], "kind": kind,
                    "margin": r["margin"], "our_reward": r["our_reward"], "opp_reward": r["opp_reward"],
                    "opp_sid": r["opp_sid"], "opp_team": r["opp_team"], "our_seat": r["our_seat"],
                    "create": r["create"], "file": os.path.basename(path),
                    "bytes": os.path.getsize(path), "status": status,
                })
                print("ok", ref, kind, ep, "%.0f" % r["margin"], os.path.getsize(path), flush=True)
    with open(os.path.join(OUT, "replay_index.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(idx[0].keys()))
        w.writeheader()
        w.writerows(idx)
    print("TOTAL", len(idx))
    return 0


if __name__ == "__main__":
    sys.exit(main())
