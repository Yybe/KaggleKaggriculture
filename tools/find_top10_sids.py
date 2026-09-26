"""BFS the Kaggle episode graph to find current submission ids for top-10 teams.

Usage: py tools/find_top10_sids.py <seed_summary.json> <out.json>
Seed summary = list of episodes (agents[] with submissionId/teamId) from ListEpisodes.
Explores opponents-of-opponents until all target teamIds are seen or budget spent.
"""
import json
import os
import sys
import time
from collections import deque

import requests

BASE = "https://www.kaggle.com/api/i/competitions.EpisodeService"
TOP10 = {
    16732748: "DSM", 16718819: "Majkel1337", 16681125: "M & M & P & Q",
    16730612: "Unknown Mother-Goose", 16640510: "SpaTaro", 16730524: "THIRD FARM CLUB",
    16675778: "Orbital Terraformer", 16817528: "QQ", 16760701: "Yannik Schiffner",
    16760569: "Otter Vibe",
    16915014: "Boey", 16667959: "Fourth Quadrant", 16623559: "DECEM",
    16854176: "吃白饭的大肥鱼",
}


def token():
    tok = os.environ.get("KAGGLE_ACCESS_TOKEN")
    if tok:
        return tok
    with open(os.path.join(os.path.expanduser("~"), ".kaggle", "access_token"), encoding="utf-8") as fh:
        return fh.read().strip()


H = {"Authorization": f"Bearer {token()}", "Content-Type": "application/json", "User-Agent": "kaggle-cli/2.2.4"}


def list_episodes(sid):
    r = requests.post(f"{BASE}/ListEpisodes", json={"submissionId": int(sid)}, headers=H, timeout=60)
    r.raise_for_status()
    return r.json().get("episodes") or []


def main():
    seed_path, out_path = sys.argv[1], sys.argv[2]
    max_calls = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    found = {}  # teamId -> {submissionId, lastSeen, episodes}
    seen_eps = set()

    def absorb(ep):
        if ep.get("id") in seen_eps:
            return
        seen_eps.add(ep["id"])
        for a in ep.get("agents", []):
            t = a.get("teamId")
            if t in TOP10:
                rec = found.setdefault(t, {})
                s = rec.setdefault(str(a["submissionId"]), 0)
                rec[str(a["submissionId"])] = s + 1

    queue = deque()
    calls = 0
    for ep in json.load(open(seed_path, encoding="utf-8")):
        absorb(ep)
        for a in ep.get("agents", []):
            sid = a.get("submissionId")
            if sid:
                queue.append((sid, 1))

    seen_sid = set()
    while queue and calls < max_calls and len(found) < len(TOP10):
        sid, depth = queue.popleft()
        if sid in seen_sid or depth > 3:
            continue
        seen_sid.add(sid)
        try:
            eps = list_episodes(sid)
            calls += 1
            time.sleep(0.25)
        except Exception as exc:
            print(f"call fail {sid}: {exc}")
            continue
        for ep in eps:
            before = len(found)
            absorb(ep)
        if len(found) < len(TOP10) and depth < 3:
            for ep in eps[:20]:
                for a in ep.get("agents", []):
                    if a.get("teamId") in TOP10:
                        queue.appendleft((a["submissionId"], depth + 1))
                    else:
                        queue.append((a["submissionId"], depth + 1))
        print(f"calls={calls} found={ {TOP10[k]: len(v) for k, v in found.items()} }", flush=True)

    result = {TOP10[t]: sids for t, sids in found.items()}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    print("FINAL:", json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
