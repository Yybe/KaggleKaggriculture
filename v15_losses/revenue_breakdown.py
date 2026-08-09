"""Full-game revenue breakdown per item for the 5 losses.
Question: where exactly did V15 lose money vs the mirror opponent?"""
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
    rev = [collections.defaultdict(int), collections.defaultdict(int)]
    qty = [collections.defaultdict(int), collections.defaultdict(int)]
    early = [collections.defaultdict(int), collections.defaultdict(int)]  # step < 456
    late = [collections.defaultdict(int), collections.defaultdict(int)]   # step >= 456
    for st in steps:
        for s in (0, 1):
            obs = st[s].get("observation") or {}
            mkt = (obs.get("market") or {}).get("prices") or {}
            act = st[s].get("action") or {}
            for m in act.get("market") or []:
                if isinstance(m, list) and len(m) >= 3 and m[0] == "SELL":
                    item, q = m[1], m[2]
                    px = mkt.get(item) or 0
                    rev[s][item] += q * px
                    qty[s][item] += q
                    (early if st is None else late)[s][item] += q * px
    return names, me, opp, rewards, rev, qty


def main():
    for fp in sorted(glob.glob(os.path.join(OUT, "*_replay.json"))):
        names, me, opp, rewards, rev, qty = analyze(fp)
        print("=" * 70)
        print(f"{os.path.basename(fp)}")
        print(f"  {names[0]}: {rewards[0]:,.0f}   vs   {names[1]}: {rewards[1]:,.0f}   (diff {rewards[me]-rewards[opp]:+,.0f} for V15)")
        items = sorted(set(rev[0]) | set(rev[1]), key=lambda i: -max(rev[0].get(i, 0), rev[1].get(i, 0)))
        for item in items:
            r0, r1 = rev[me].get(item, 0), rev[opp].get(item, 0)
            q0, q1 = qty[me].get(item, 0), qty[opp].get(item, 0)
            print(f"  {item:<11} V15: {q0:>4}u {r0:>9,.0f}   OPP: {q1:>4}u {r1:>9,.0f}   delta {r0-r1:+,.0f}")
        print()


if __name__ == "__main__":
    main()
