"""Per-step money delta reconciliation: find where V15's money differs from OPP
beyond SELL/BUY market actions. Hypothesis: wage differences (hands hired/terminated)."""
import json, glob, os

OUT = r"C:\Users\xxshi\Desktop\farmmasterV2\v15_losses"
MY_TEAM = "Shivam_2212"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def analyze(path):
    d = load(path)
    names = d["info"]["TeamNames"]
    me = 0 if names[0] == MY_TEAM else 1
    steps = d["steps"]

    # money series from farms[0].money
    money = [[], []]
    hands = [[], []]
    for st in steps:
        for s in (0, 1):
            obs = st[s].get("observation") or {}
            farms = obs.get("farms") or []
            m = farms[0].get("money") if farms else None
            money[s].append(m)
            act = st[s].get("action") or {}
            hands[s].append(len(act.get("hands") or []))

    # step deltas
    print(f"=== {os.path.basename(fp)} ===")
    for s, tag in ((me, "V15"), (1 - me, "OPP")):
        # deltas where money changed by more than ±5 and no market action
        n = len(money[s])
        print(f"--- {tag} money@0={money[s][0]} final={money[s][-1]} "
              f"sum_delta={sum(money[s][i+1]-money[s][i] for i in range(n-1) if money[s][i] is not None)}")
        # hands hire/terminate steps
        chg = [i for i in range(1, n) if hands[s][i] != hands[s][i-1]]
        if chg:
            print(f"  hand changes at: {chg[:30]}{'...' if len(chg) > 30 else ''}")

    # find divergence steps: money delta differs between players
    div = []
    for i in range(len(steps) - 1):
        m0, m1 = money[0][i], money[1][i]
        n0, n1 = money[0][i+1], money[1][i+1]
        if None in (m0, m1, n0, n1):
            continue
        d0, d1 = n0 - m0, n1 - m1
        if abs(d0 - d1) >= 50:
            div.append((i, d0, d1, d0 - d1))
    print(f"  steps with |delta diff|>=50: {len(div)}")
    for i, d0, d1, dd in div[:40]:
        print(f"    step {i} (d{i//24}): V15 delta {d0:+,.0f}  OPP delta {d1:+,.0f}  diff {dd:+,.0f}")
    print()


for fp in sorted(glob.glob(os.path.join(OUT, "*_replay.json"))):
    analyze(fp)
