"""Summarize V14 tape: per-day market orders + unit action counts."""
import importlib.util, collections

spec = importlib.util.spec_from_file_location('v14mod', r'C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\v14_source.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ACT = mod._ACTIONS

def day_of(step):
    return step // 24

# Per-day market aggregates
mkt_by_day = collections.defaultdict(lambda: collections.defaultdict(int))  # day -> ("SELL", item) -> qty
hire_by_day = collections.defaultdict(int)
buyseed_by_day = collections.defaultdict(lambda: collections.defaultdict(int))
buylan_by_day = collections.defaultdict(int)
buyanimal_by_day = collections.defaultdict(lambda: collections.defaultdict(int))
buyproduct_by_day = collections.defaultdict(lambda: collections.defaultdict(int))
unit_actions = collections.defaultdict(collections.Counter)  # day -> action counter
n_hands_by_day = collections.defaultdict(int)

for step, entry in enumerate(ACT):
    d = day_of(step)
    mkt = entry.get('market') or []
    for order in mkt:
        if not isinstance(order, (list, tuple)) or len(order) < 2:
            continue
        op = order[0]
        if op == 'HIRE':
            hire_by_day[d] += 1
        elif op == 'BUY_SEED' and len(order) >= 3:
            buyseed_by_day[d][order[1]] += order[2]
        elif op == 'BUY_LAND':
            buylan_by_day[d] += 1
        elif op == 'BUY_ANIMAL' and len(order) >= 3:
            buyanimal_by_day[d][order[1]] += order[2]
        elif op == 'BUY_PRODUCT' and len(order) >= 3:
            buyproduct_by_day[d][order[1]] += order[2]
        elif op == 'SELL' and len(order) >= 3:
            mkt_by_day[d][order[1]] += order[2]
    f = entry.get('farmer') or []
    hands = entry.get('hands') or []
    if hands:
        n_hands_by_day[d] = max(n_hands_by_day[d], len(hands))
    for a in [f] + list(hands):
        if a and isinstance(a, list) and a[0] != 'PASS':
            unit_actions[d][a[0]] += 1

print("=== HIRES & HANDS per day ===")
for d in sorted(hire_by_day):
    print(f"  D{d:2d}: hire={hire_by_day[d]} peak_hands={n_hands_by_day[d]}")

print("\n=== BUY_SEED per day ===")
for d in sorted(buyseed_by_day):
    items = ', '.join(f'{k}:{v}' for k, v in sorted(buyseed_by_day[d].items()))
    print(f"  D{d:2d}: {items}")

print("\n=== BUY_LAND per day ===")
for d in sorted(buylan_by_day):
    print(f"  D{d:2d}: x{buylan_by_day[d]}")

print("\n=== BUY_ANIMAL per day ===")
for d in sorted(buyanimal_by_day):
    items = ', '.join(f'{k}:{v}' for k, v in sorted(buyanimal_by_day[d].items()))
    print(f"  D{d:2d}: {items}")

print("\n=== BUY_PRODUCT (arbitrage) per day ===")
for d in sorted(buyproduct_by_day):
    items = ', '.join(f'{k}:{v}' for k, v in sorted(buyproduct_by_day[d].items()))
    print(f"  D{d:2d}: {items}")

print("\n=== SELL per day ===")
total_q = collections.Counter()
for d in sorted(mkt_by_day):
    items = ', '.join(f'{k}:{v}' for k, v in sorted(mkt_by_day[d].items(), key=lambda kv: -kv[1]))
    for k, v in mkt_by_day[d].items():
        total_q[k] += v
    print(f"  D{d:2d}: {items}")
print("  TOTAL SELL QTY:", dict(total_q))

print("\n=== UNIT ACTION COUNTS per day (farmer+hands, non-PASS) ===")
for d in sorted(unit_actions):
    acts = ', '.join(f'{k}:{v}' for k, v in unit_actions[d].most_common(6))
    print(f"  D{d:2d}: {acts}")

# First occurrence of each op type
print("\n=== FIRST OCCURRENCES ===")
firsts = {}
for step, entry in enumerate(ACT):
    mkt = entry.get('market') or []
    for order in mkt:
        if isinstance(order, (list, tuple)) and order:
            op = order[0]
            if op not in firsts:
                firsts[op] = (step, order)
for op in sorted(firsts):
    print(f"  {op}: step {firsts[op][0]} {firsts[op][1]}")
