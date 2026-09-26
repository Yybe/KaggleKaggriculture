"""P8 god's view, take 3 — fetch top-vs-top replays via the kaggle CLI.

`kaggle competitions replay <episodeId>` reaches episodes the raw EpisodeService
404s for (those are restricted to episodes involving the calling account).
Reads candidate ids from WybeV2/datasets/p8_godview/cand_eps.json and writes
episode-<id>-replay.json into WybeV2/datasets/p8_godview/replays/.

usage: WybeV2/rank_env/Scripts/python.exe tools/p8_fetch_godview3.py [n_max]
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "WybeV2", "datasets", "p8_godview", "cand_eps.json")
OUT = os.path.join(ROOT, "WybeV2", "datasets", "p8_godview", "replays")
n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 120


def main():
    os.makedirs(OUT, exist_ok=True)
    cands = json.load(open(CAND, encoding="utf-8"))
    done = skip = fail = 0
    for eid in sorted(cands, key=int, reverse=True):
        if done >= n_max:
            break
        out_path = os.path.join(OUT, f"episode-{eid}-replay.json")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            skip += 1
            continue
        r = subprocess.run(["kaggle", "competitions", "replay", str(eid), "-p", OUT, "-q"],
                           capture_output=True, text=True, timeout=600)
        if r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            done += 1
            if done % 10 == 0:
                print(f"done={done} skip={skip} fail={fail}", flush=True)
        else:
            fail += 1
            print(f"FAIL {eid}: {r.stdout[-120:]} {r.stderr[-120:]}", flush=True)
            time.sleep(2)
        time.sleep(0.6)
    print(f"GODVIEW3 COMPLETE done={done} skip={skip} fail={fail}", flush=True)


if __name__ == "__main__":
    main()
