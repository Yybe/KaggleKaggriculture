"""Full money-flow reconciliation per player for the 5 losses.
Track: sell revenue, buy spend, hand count over time, wages, final money.
Goal: find where V15's +sell-revenue advantage leaks away."""
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
    steps = d["steps"]
    P = [{}, {}]
    for s in (0, 1):
        sells = buys = 0
        hand_steps = 0
        hands_seen = None
        buy_spend = collections.defaultdict(int)
        sell_item = collections.defaultdict(int)
        for t, st in enumerate(steps):
            obs = st[s].get("observation") or {}
            mkt = (obs.get("market") or {}).get("prices") or {}
            act = st[s].get("action") or {}
            for m in act.get("market") or []:
                if isinstance(m, list) and len(m) >= 3:
                    op, item, q = m[0], m[1], m[2]
                    px = mkt.get(item) or 0
                    if op == "SELL":
                        sells += q * px
                        sell_item[item] += q * px
                    elif op == "BUY_SEED" or op == "BUY_PRODUCT" or op == "BUY_ANIMAL" or op == "BUY_LAND":
                        buys += q * px
                        buy_spend[op] += q * px
            hands = len(act.get("hands") or [])
            if hands_seen is not None:
                hand_steps += hands
            else:
                hands_seen = hands
        P[s] = dict(sells=sells, buys=buys, hand_steps=hand_steps,
                    buy_spend=dict(buy_spend), sell_item=dict(sell_item))
    return names, me, P, d.get("rewards", [])


def main():
    for fp in sorted(glob.glob(os.path.join(OUT, "*_replay.json"))):
        names, me, P, rewards = analyze(fp)
        o = 1 - me
        print("=" * 78)
        print(f"{os.path.basename(fp)}")
        print(f"  {names[0]}: {rewards[0]:,.0f}   vs   {names[1]}: {rewards[1]:,.0f}")
        for s, tag in ((me, "V15(ME)"), (o, "OPP")):
            p = P[s]
            print(f"  {tag}: sells={p['sells']:,.0f}  buys={p['buys']:,.0f}  "
                  f"hand-turns={p['hand_steps']:,}  buys_detail={p['buy_spend']}")
        print()


if __name__ == "__main__":
    main()
