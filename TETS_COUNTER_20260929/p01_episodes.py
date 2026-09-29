"""E256 p01 - fresh episode ledger for our tetsutani-era submissions + fresh leaderboard.

Refs (all read live from the API today, nothing cached from previous cycles):
  56672630 tetsutani_godview_v2  (the grafted file under audit)
  56653474 tetsutani_step1009     (its parent, the higher-scoring row)
  56644648 cha22_champion         (bar of record, frozen row)
Writes out/episodes_<ref>.csv + raw list json + leaderboard csv.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from fetch_episodes import list_episodes  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
RAW = os.path.join(HERE, "raw")
REFS = {
    "56672630": "tetsutani_godview_v2",
    "56653474": "tetsutani_step1009",
    "56644648": "cha22_champion",
}
OUR_TEAM = 16669256


def _retry(fn, *a, attempts=6, **kw):
    delay = 5
    for _ in range(attempts):
        try:
            return fn(*a, **kw)
        except Exception as exc:  # noqa: BLE001
            if "429" not in str(exc):
                raise
            print("429 sleeping %ds" % delay, flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 120)
    raise RuntimeError("rate limited")


def pick(node, *names, default=None):
    for n in names:
        if n in node and node[n] is not None:
            return node[n]
    return default


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    for ref, label in REFS.items():
        path = os.path.join(RAW, "list_%s.json" % ref)
        if os.path.exists(path) and os.path.getsize(path) > 200:
            listing = json.load(open(path, encoding="utf-8"))
        else:
            listing = _retry(list_episodes, ref)
            json.dump(listing, open(path, "w", encoding="utf-8"))
        eps = None
        for key in ("episodes", "items", "results"):
            node = listing.get(key) if isinstance(listing, dict) else None
            if isinstance(node, list) and node:
                eps = node
                break
        if eps is None and isinstance(listing, list):
            eps = listing
        if eps is None:
            print("NO_EPISODE_LIST", ref, list(listing)[:8] if isinstance(listing, dict) else "?")
            continue
        rows = []
        for e in eps:
            agents = e.get("agents") or []
            mine, opp = None, None
            for a in agents:
                row = {
                    "sid": pick(a, "submissionId", "id"),
                    "team": pick(a, "teamId"),
                    "idx": pick(a, "index", "submissionIndex"),
                    "reward": pick(a, "reward"),
                    "name": pick(a, "teamName", "teamNamePublic", default=""),
                }
                if row["sid"] == int(ref):
                    mine = row
                else:
                    opp = row
            if mine is None or opp is None:
                continue
            mr, orr = mine["reward"], opp["reward"]
            outcome = "T" if mr == orr else ("W" if (mr or 0) > (orr or 0) else "L")
            rows.append({
                "ref": ref, "label": label, "episode": pick(e, "episodeId", "id"),
                "create": pick(e, "createTime", "creationDate"), "outcome": outcome,
                "our_reward": mr, "opp_reward": orr, "margin": (mr or 0) - (orr or 0),
                "our_seat": mine["idx"], "opp_sid": opp["sid"], "opp_team": opp["team"],
                "opp_name": opp["name"],
            })
        w = csv.DictWriter(open(os.path.join(OUT, "episodes_%s.csv" % ref), "w", newline="", encoding="utf-8"),
                           fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        n_w = sum(r["outcome"] == "W" for r in rows)
        n_l = sum(r["outcome"] == "L" for r in rows)
        n_t = sum(r["outcome"] == "T" for r in rows)
        mean = sum(r["margin"] for r in rows) / max(len(rows), 1)
        print("%s %s n=%d W%d/L%d/T%d mean_margin=%.1f" % (ref, label, len(rows), n_w, n_l, n_t, mean), flush=True)

    # fresh leaderboard (never a saved csv)
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        lp = os.path.join(OUT, "leaderboard_today.csv")
        if not (os.path.exists(lp) and os.path.getsize(lp) > 1000):
            api.competition_leaderboard("kaggriculture", OUT)
            for f in os.listdir(OUT):
                if f.startswith("kaggriculture") and f.endswith(".csv"):
                    os.replace(os.path.join(OUT, f), lp)
        print("leaderboard rows:", sum(1 for _ in open(lp, encoding="utf-8", errors="replace")) if os.path.exists(lp) else "MISSING")
    except Exception as exc:  # noqa: BLE001
        print("leaderboard FAIL", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
