"""P8 — god's-view replay pull for current top-team submissions (2026-09-26).

Lists episodes for each top-team sid (from p8_live_20260926/top_sids.json),
takes the most recent N=12 episodes, fetches each replay via EpisodeService,
and writes episode-<id>-replay.json into WybeV2/datasets/p8_godview/replays/.
Skips files already on disk. Paced 1.0 s between calls.

usage: WybeV2/rank_env/Scripts/python.exe tools/p8_fetch_godview.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_episodes import list_episodes, get_replay  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIDS = json.load(open(os.path.join(ROOT, "WybeV2", "datasets", "p8_live_20260926", "top_sids.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "WybeV2", "datasets", "p8_godview", "replays")
N_PER_TEAM = 12


def main():
    os.makedirs(OUT, exist_ok=True)
    done = 0
    for team, sids in SIDS.items():
        sid = max(sids.items(), key=lambda kv: kv[1])[0]
        eps = None
        for attempt in range(5):
            try:
                eps = list_episodes(sid)
                break
            except Exception as exc:  # noqa: BLE001
                wait = 30 * (attempt + 1)
                print(f"LIST RETRY {team} {sid} in {wait}s: {exc}", flush=True)
                time.sleep(wait)
        if eps is None:
            print(f"LIST FAIL {team} {sid}", flush=True)
            continue
        time.sleep(2.0)
        eps.sort(key=lambda e: e.get("createTime") or "", reverse=True)
        got = 0
        for ep in eps:
            if got >= N_PER_TEAM:
                break
            ep_id = ep.get("episodeId") or ep.get("id")
            if not ep_id:
                continue
            out_path = os.path.join(OUT, f"episode-{ep_id}-replay.json")
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                got += 1
                continue
            try:
                replay = get_replay(ep_id)
                payload = replay.get("replay") if isinstance(replay, dict) else None
                if isinstance(payload, str):
                    payload = json.loads(payload)
                if not isinstance(payload, dict):
                    print(f"BAD PAYLOAD {team} {ep_id}", flush=True)
                    continue
                if len(payload.get("steps") or []) < 720:
                    got += 1  # short/aborted game, counts toward budget but not useful
                    continue
                with open(out_path, "w", encoding="utf-8") as fh:
                    json.dump(payload, fh)
                got += 1
                done += 1
                print(f"OK {team} {ep_id} done={done}", flush=True)
                time.sleep(1.0)
            except Exception as exc:  # noqa: BLE001
                print(f"FETCH FAIL {team} {ep_id}: {exc}", flush=True)
                time.sleep(2.0)
    print(f"GODVIEW COMPLETE total_new={done}", flush=True)


if __name__ == "__main__":
    main()
