"""E99 graft-#3 screen: realized per-unit margin of Ebi's wheat round-trip arb.

Parses results/E99_losses/episode-111594513-replay.json (Ebi live loss, seat0).
FIFO-pairs BUY_PRODUCT WHEAT -> SELL (town-center) fills using the market price
in the same step's observation, and writes results/E99_losses/EBI_ARB_MARGIN.md.
Note engine pairing law: obs[t] is post-action, so a BUY's recorded obs price is
the price AFTER Ebi's own demand hit (sell-side obs is post-supply too) -
margins computed this way are UPPER bounds on Ebi's own fill-to-fill spread.
"""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
REPLAY = BASE / "results" / "E99_losses" / "episode-111594513-replay.json"
OUT = BASE / "results" / "E99_losses" / "EBI_ARB_MARGIN.md"
SEAT = 0  # Ebi, final reward 111,857


def main():
    data = json.loads(REPLAY.read_text(encoding="utf-8"))
    steps = data["steps"]
    fifo = []  # (qty_remaining, buy_px, buy_step)
    pairs = []  # (sell_qty, buy_px, sell_px)
    buys, sells = [], []
    for t in range(1, len(steps)):
        entry = steps[t][SEAT]
        act = entry.get("action") or {}
        if not isinstance(act, dict):
            continue
        obs = entry.get("observation") or {}
        px = (obs.get("market") or {}).get("prices") or {}
        for o in act.get("market") or []:
            if not (isinstance(o, list) and len(o) >= 3):
                continue
            op, item, qty = o[0], o[1], int(o[2] or 0)
            if item != "WHEAT" or qty <= 0:
                continue
            p = px.get("WHEAT", 0)
            if op == "BUY_PRODUCT":
                fifo.append([qty, p, t])
                buys.append((t, qty, p))
            elif op == "SELL":
                sells.append((t, qty, p))
                rem = qty
                while rem > 0 and fifo:
                    lot = fifo[0]
                    take = min(rem, lot[0])
                    pairs.append((take, lot[1], p, lot[2], t))
                    lot[0] -= take
                    rem -= take
                    if lot[0] == 0:
                        fifo.pop(0)
                # unmatched sell qty (from own production) just drops
    total_q = sum(p[0] for p in pairs)
    net = sum(p[0] * (p[2] - p[1]) for p in pairs)
    wavg = (net / total_q) if total_q else 0.0
    pos = sum(1 for p in pairs if p[2] > p[1])
    # per-6-day-window margins
    windows = {}
    for q, bpx, spx, bs, ss in pairs:
        w = bs // 144
        a = windows.setdefault(w, [0, 0.0])
        a[0] += q
        a[1] += q * (spx - bpx)
    px_path = sorted({steps[t][SEAT]["observation"]["market"]["prices"]["WHEAT"]
                      for t in range(1, len(steps))
                      if ((steps[t][SEAT].get("observation") or {}).get("market") or {}).get("prices")})
    lines = [
        "# Ebi wheat-arb margin screen (episode 111594513, seat0)",
        "",
        f"- Arbitraged (FIFO-matched buy->sell) units: {total_q}",
        f"- Net round-trip cash: {net:,.0f} | weighted margin: {wavg:.2f} px/unit",
        f"- Matched lots profitable: {pos}/{len(pairs)}",
        f"- Obs WHEAT price path min..max: {px_path[0]}..{px_path[-1]}",
        "",
        "| buy-window (6d) | units | net px |",
        "|---|---|---|",
    ]
    for w in sorted(windows):
        q, npx = windows[w]
        lines.append(f"| d{w*6+1}-{w*6+6} | {q} | {npx:,.0f} |")
    lines += [
        "",
        "Caveat: obs[t] is post-action, so buy px already includes Ebi's own demand",
        "impact and sell px includes his supply impact -> computed spread UNDERSTATES",
        "impact-free opportunity for buys, OVERSTATES nothing; a same-scale copycat",
        "would move the price at least as much (self-impact law, E57c).",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
