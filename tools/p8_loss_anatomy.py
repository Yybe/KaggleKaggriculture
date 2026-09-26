"""P8 loss anatomy — winner-vs-ours feature gaps across the 63 fresh live losses.

Reads results/atlas_20260926/atlas_features.json (per-seat features from atlas_0921),
pairs seats by episode, keeps games we lost, and reports winner-minus-ours feature
gaps (median/mean), plus the same for wins as control. Writes
results/p8_loss_anatomy_20260926.md and prints the table.

usage: WybeV2/rank_env/Scripts/python.exe tools/p8_loss_anatomy.py
"""
import json
import os
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATS = json.load(open(os.path.join(ROOT, "results", "atlas_20260926", "atlas_features.json"), encoding="utf-8"))

FLAT_KEYS = ["fert", "hire", "land", "water", "feed", "sell_units", "sell_ops"]
NESTED = ["plant", "buy_seed", "animals", "sell_by"]


def flat(seat):
    row = {k: seat.get(k, 0) for k in FLAT_KEYS}
    for n in NESTED:
        for k, v in (seat.get(n) or {}).items():
            row[f"{n}.{k}"] = v
    return row


def main():
    eps = {}
    for f in FEATS:
        eps.setdefault(f["ep"], {})[f["seat"]] = f
    losses, wins = [], []
    for ep, seats in eps.items():
        if len(seats) != 2:
            continue
        ours = next((s for s in seats.values() if "shivam" in str(s["name"]).lower()), None)
        if ours is None:
            continue
        opp = seats[1 - ours["seat"]]
        our_f, opp_f = flat(ours), flat(opp)
        gap = {k: opp_f.get(k, 0) - our_f.get(k, 0) for k in set(our_f) | set(opp_f)}
        (losses if not ours["win"] else wins).append((ep, gap))

    def table(rows):
        keys = sorted({k for _, g in rows for k in g})
        out = []
        for k in keys:
            vals = [g.get(k, 0) for _, g in rows]
            if not any(vals):
                continue
            n_pos = sum(1 for v in vals if v > 0)
            out.append((k, len(vals), st.median(vals), sum(vals) / len(vals), n_pos))
        out.sort(key=lambda t: -abs(t[2]))
        return out

    lines = ["# P8 live loss anatomy — 2026-09-26 field (144 h1q6 episodes)\n"]
    for title, rows in (("LOSSES (winner-minus-ours, positive = winner did more)", losses),
                        ("WINS (winner-minus-ours, control)", wins)):
        lines.append(f"## {title}  n={len(rows)}\n")
        lines.append("| feature | n | median gap | mean gap | #games winner>ours |")
        lines.append("|---|---:|---:|---:|---:|")
        for k, n, med, mean, npos in table(rows):
            lines.append(f"| {k} | {n} | {med:+.0f} | {mean:+.1f} | {npos} |")
        lines.append("")

    lines.append("## Lever check (loss-gap median vs win-gap median)\n")
    for k in ["fert", "water", "sell_units", "sell_ops", "animals.COW", "animals.SHEEP",
              "animals.GOOSE", "land", "hire", "plant.WHEAT", "plant.CARROT", "plant.STRAWBERRY",
              "plant.TOMATO", "plant.MELON", "sell_by.FERTILIZER", "sell_by.WHEAT"]:
        lmed = st.median([g.get(k, 0) for _, g in losses])
        wmed = st.median([g.get(k, 0) for _, g in wins])
        lines.append(f"- {k}: loss-gap {lmed:+.0f}, win-gap {wmed:+.0f}")

    out_path = os.path.join(ROOT, "results", "p8_loss_anatomy_20260926.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
