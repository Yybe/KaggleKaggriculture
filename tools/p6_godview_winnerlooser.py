"""P6 god's-view winner-vs-loser anatomy with CORRECT attribution.

atlas_0921 attributes seat 0 as "ours" when no team name matches the shivam hint,
so in top-vs-top games the sign of every div_class gap is flipped on half the rows.
Real winner-minus-loser = +gap when seat0 lost, -gap when seat0 won.
Reads results/atlas_p6_godview/atlas_games.csv, rewrites the loss-feature table,
writes results/p6_godview_winner_anatomy_20260926.md.

usage: WybeV2/rank_env/Scripts/python.exe tools/p6_godview_winnerlooser.py
"""
import csv
import os
import re
import statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "results", "atlas_p6_godview", "atlas_games.csv")
OUT = os.path.join(ROOT, "results", "p6_godview_winner_anatomy_20260926.md")


def tokens(div_class):
    out = []
    for t in (div_class or "").split(","):
        t = t.strip()
        m = re.match(r"([A-Za-z_]+):([+-]?\d+)", t)
        if m:
            out.append((m.group(1), int(m.group(2))))
    return out


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    feat_w = defaultdict(list)  # winner-minus-loser per feature, over ALL games
    n_win = 0
    for r in rows:
        seat0_won = r["ours_w"] == "True"
        if seat0_won:
            n_win += 1
            gaps = {k: -v for k, v in tokens(r["div_class"])}
        else:
            gaps = dict(tokens(r["div_class"]))
        for k, v in gaps.items():
            feat_w[k].append(v)
    lines = [f"# P6 top-vs-top winner anatomy (sign-corrected) — {len(rows)} games, seat0 won {n_win}\n",
             "| feature | n | median gap (winner-loser) | mean gap | #games winner>loser |",
             "|---|---:|---:|---:|---:|"]
    for k, vs in sorted(feat_w.items(), key=lambda kv: -abs(st.median(kv[1]) if kv[1] else 0)):
        med = st.median(vs)
        lines.append(f"| {k} | {len(vs)} | {med:+.0f} | {sum(vs)/len(vs):+.1f} | {sum(1 for v in vs if v > 0)} |")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
