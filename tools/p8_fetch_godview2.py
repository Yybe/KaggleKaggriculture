"""P8 god's view, take 2 — fetch top-vs-top replays via GetEpisodeReplay.

Seed = WybeV2/datasets/p8_live_20260926/seed_raw.json (740 episode entries from
successful ListEpisodes calls). Joined with the 2026-09-25 leaderboard CSV to keep
games where BOTH seats belong to top-T teams. Fetches each replay with pacing and
429 backoff, writing episode-<id>-replay.json into WybeV2/datasets/p8_godview/replays/.

usage: WybeV2/rank_env/Scripts/python.exe tools/p8_fetch_godview2.py [top_t=60] [n_per_team=8]
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_episodes import get_replay  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "WybeV2", "datasets", "p8_live_20260926", "seed_raw.json")
BOARD = os.path.join(ROOT, "scan_20260925", "kaggriculture-publicleaderboard-2026-09-25T16_42_11.csv")
OUT = os.path.join(ROOT, "WybeV2", "datasets", "p8_godview", "replays")

top_t = int(sys.argv[1]) if len(sys.argv) > 1 else 60
per_team = int(sys.argv[2]) if len(sys.argv) > 2 else 8


def main():
    rank = {}
    with open(BOARD, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            rank[int(row["TeamId"])] = (int(row["Rank"]), row["TeamName"])

    seen = {}
    for ep in json.load(open(SEED, encoding="utf-8")):
        eid = ep.get("episodeId") or ep.get("id")
        agents = ep.get("agents") or []
        if len(agents) < 2:
            continue
        tids = [a.get("teamId") for a in agents]
        if any(t not in rank for t in tids):
            continue
        ranks = [rank[t][0] for t in tids]
        if max(ranks) > top_t:
            continue
        seen[eid] = (tids, ranks, [rank[t][1] for t in tids])

    print(f"candidate top-vs-top episodes: {len(seen)}")
    by_team = {}
    for eid, (tids, ranks, names) in seen.items():
        key = tuple(sorted(tids))
        by_team.setdefault(key, []).append(eid)

    os.makedirs(OUT, exist_ok=True)
    done = 0
    for key, eids in sorted(by_team.items()):
        got = 0
        for eid in sorted(eids, reverse=True):
            if got >= per_team:
                break
            out_path = os.path.join(OUT, f"episode-{eid}-replay.json")
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                got += 1
                continue
            for attempt in range(4):
                try:
                    replay = get_replay(eid)
                    payload = replay.get("replay") if isinstance(replay, dict) else None
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    if isinstance(payload, dict) and len(payload.get("steps") or []) >= 720:
                        with open(out_path, "w", encoding="utf-8") as fh:
                            json.dump(payload, fh)
                        done += 1
                        got += 1
                        print(f"OK {eid} {[rank[t][1] for t in key]} done={done}", flush=True)
                    else:
                        got += 1
                    time.sleep(1.2)
                    break
                except Exception as exc:  # noqa: BLE001
                    if "404" in str(exc) or "403" in str(exc):
                        print(f"SKIP {eid}: {exc}", flush=True)
                        break
                    wait = 45 * (attempt + 1)
                    print(f"RETRY {eid} in {wait}s: {exc}", flush=True)
                    time.sleep(wait)
    print(f"GODVIEW2 COMPLETE total={done}", flush=True)


if __name__ == "__main__":
    main()
