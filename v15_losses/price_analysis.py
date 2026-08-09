"""Price-path analysis of the 5 V15 losses: where did each player's late
high-value sells land on the shared price curve, and what revenue did they get?"""
import json, glob, os, collections

OUT = r"C:\Users\xxshi\Desktop\farmmasterV2\v15_losses"
MY_TEAM = "Shivam_2212"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def analyze(path):
    d = load(path)
    info = d.get("info", {})
    names = info.get("TeamNames", [])
    me = 0 if names[0] == MY_TEAM else 1
    opp = 1 - me
    rewards = d.get("rewards", [])
    steps = d["steps"]

    # per-item price series (shared) from market obs
    prices = collections.defaultdict(list)  # item -> list[(step, price)]
    # per-player sell events: (step, item, qty, price_at_sell)
    sells = [[], []]
    for t, st in enumerate(steps):
        for s in (0, 1):
            obs = st[s].get("observation") or {}
            market = obs.get("market") or {}
            mkt_prices = market.get("prices") or {}
            for item, p in mkt_prices.items():
                prices[item].append((t, p))
            act = st[s].get("action") or {}
            for m in act.get("market") or []:
                if isinstance(m, list) and len(m) >= 3 and m[0] == "SELL":
                    item, qty = m[1], m[2]
                    sells[s].append((t, item, qty, mkt_prices.get(item)))

    return dict(names=names, me=me, rewards=rewards, sells=sells, prices=prices)


def main():
    for fp in sorted(glob.glob(os.path.join(OUT, "*_replay.json"))):
        r = analyze(fp)
        me, opp = r["me"], 1 - r["me"]
        print("=" * 78)
        print(f"{os.path.basename(fp)} | {r['names'][0]} {r['rewards'][0]:.0f} vs "
              f"{r['names'][1]} {r['rewards'][1]:.0f}")
        # late-game high-value sells with prices, step >= 456
        for s, tag in ((me, "V15(ME)"), (opp, "OPP")):
            print(f"--- {tag} late sells (>=456) ---")
            late = [x for x in r["sells"][s] if x[0] >= 456 and x[1] in
                    ("STRAWBERRY", "MILK", "WOOL", "MELON")]
            rev = 0
            for t, item, qty, px in late:
                rev += qty * (px or 0)
                print(f"  step {t:>3} (d{t//24:>2}) {item:<11} x{qty:>3} @ px={px}")
            print(f"  late HV revenue: {rev:,.0f}")
        # final-10-day price paths
        print("--- price path final 10 days (STRAWBERRY / MILK / WOOL) ---")
        for item in ("STRAWBERRY", "MILK", "WOOL"):
            ser = [(t, p) for t, p in r["prices"][item] if t >= 480]
            # sample every 24 steps
            sampled = [p for t, p in ser if t % 24 == 0]
            if sampled:
                print(f"  {item:<11} d20-29: {sampled}")
        print()


if __name__ == "__main__":
    main()
