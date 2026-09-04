"""Fetch episode replays for a kaggriculture submission via the Kaggle episode API.

Usage:
  python tools/fetch_episodes.py <submission_id> <out_dir> [--list-only]

Auth: uses ~/.kaggle/access_token (KGAT_...) or KAGGLE_ACCESS_TOKEN env var.
Writes one JSON per episode into <out_dir>, plus a summary CSV of
episode -> our reward vs opponent reward -> opponent submission id.
"""
import json
import os
import sys
import time

import requests

BASE = "https://www.kaggle.com/api/i/competitions.EpisodeService"


def _token():
    tok = os.environ.get("KAGGLE_ACCESS_TOKEN")
    if tok:
        return tok
    path = os.path.join(os.path.expanduser("~"), ".kaggle", "access_token")
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def _headers():
    tok = _token()
    return {
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "User-Agent": "kaggle-cli/2.2.4",
    }


def list_episodes(submission_id):
    url = f"{BASE}/ListEpisodes"
    resp = requests.post(url, json={"submissionId": int(submission_id)}, headers=_headers(), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data


def get_replay(episode_id):
    url = f"{BASE}/GetEpisodeReplay"
    resp = requests.post(url, json={"episodeId": int(episode_id)}, headers=_headers(), timeout=120)
    resp.raise_for_status()
    return resp.json()


def main():
    submission_id = sys.argv[1]
    out_dir = sys.argv[2]
    list_only = "--list-only" in sys.argv
    os.makedirs(out_dir, exist_ok=True)

    listing = list_episodes(submission_id)
    # The response nests the episode list under various keys depending on API version.
    episodes = None
    for key in ("episodes", "items", "results"):
        node = listing.get(key)
        if isinstance(node, list) and node:
            episodes = node
            break
    if episodes is None:
        # maybe {"episodes": {"episodes": [...]}} or a bare list
        if isinstance(listing, list):
            episodes = listing
        else:
            for value in listing.values():
                if isinstance(value, list) and value and isinstance(value[0], dict) and "episodeId" in json.dumps(value[0]):
                    episodes = value
                    break
    if episodes is None:
        print("Could not locate episode list; raw keys:", list(listing.keys()))
        print(json.dumps(listing)[:2000])
        return 1

    summary = []
    for entry in episodes:
        ep_id = entry.get("episodeId") or entry.get("id")
        agents = entry.get("agents") or []
        ours = None
        opp = None
        for agent in agents:
            sid = agent.get("submissionId")
            reward = agent.get("reward")
            index = agent.get("index")
            if sid == int(submission_id):
                ours = (index, reward)
            else:
                opp = (index, reward, sid)
        summary.append({
            "episodeId": ep_id,
            "createTime": entry.get("createTime"),
            "ours_index_reward": ours,
            "opp_index_reward_sid": opp,
        })
        if list_only:
            continue
        out_path = os.path.join(out_dir, f"episode-{ep_id}-replay.json")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            continue
        try:
            replay = get_replay(ep_id)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {ep_id}: {exc}")
            continue
        payload = replay.get("replay") if isinstance(replay, dict) else None
        if payload is None and isinstance(replay, dict):
            payload = json.dumps(replay)
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                pass
        with open(out_path, "w", encoding="utf-8") as fh:
            if isinstance(payload, (dict, list)):
                json.dump(payload, fh)
            else:
                fh.write(str(payload))
        time.sleep(0.4)

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    wins = losses = ties = 0
    for row in summary:
        if row["ours_index_reward"] and row["opp_index_reward_sid"]:
            ours = row["ours_index_reward"][1]
            opp = row["opp_index_reward_sid"][1]
            if ours is None or opp is None:
                continue
            if ours > opp:
                wins += 1
            elif ours < opp:
                losses += 1
            else:
                ties += 1
    print(f"episodes={len(summary)} wins={wins} losses={losses} ties={ties}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
