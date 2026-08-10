import importlib.util, sys, json

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.agent

V16 = load_agent(r'C:\Users\xxshi\Desktop\farmmasterV2\submission.py', 'v16mod')

log = []
def wrapped(obs, cfg=None):
    act = V16(obs, cfg)
    log.append((obs.get('step', 0), obs.get('day', 0), obs.get('hour', 0), list(act.get('market') or [])))
    return act

from kaggle_environments import make
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000000}, debug=False)
env.run([wrapped, lambda obs: {"farmer": ["PASS"], "hands": [], "market": []}])

price_by_step = {}
cash_by_step = {}
for i, (s0, s1) in enumerate(env.steps):
    obs = s0['observation']
    price_by_step[i] = dict((obs.get('market') or {}).get('prices', {}))
    cash_by_step[i] = obs['farms'][0].get('money')

sold = {}
revenue = {}
sold_by_day = {}
for step, day, hour, mkt in log:
    for order in mkt:
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == 'SELL':
            item, qty = order[1], int(order[2])
            px = price_by_step.get(step, {}).get(item, 0) or 0
            sold[item] = sold.get(item, 0) + qty
            revenue[item] = revenue.get(item, 0) + qty * px
            d = sold_by_day.setdefault(day, {})
            d[item] = d.get(item, 0) + qty

print("=== V16 SELLS (solo vs PASS) seed=1M ===")
for item in sorted(sold, key=lambda k: -revenue.get(k, 0)):
    print(f"  {item:12s} qty={sold[item]:5d}  revenue={revenue[item]:10,.0f}")
print("  TOTAL revenue(approx):", sum(revenue.values()))
print("  FINAL cash:", env.state[0].reward)
print("\n=== BY DAY ===")
for day in sorted(sold_by_day):
    items = ', '.join(f'{k}:{v}' for k, v in sorted(sold_by_day[day].items(), key=lambda kv: -kv[1]))
    print(f"  D{day:2d}: {items}")
print("\n=== PRICE SNAPSHOTS (S240=day10 S480=day20 S600=day25 S696=day29 S719) ===")
for step in [0, 240, 480, 600, 696, 719]:
    if step in price_by_step:
        print(f"  S{step:3d} cash={cash_by_step[step]:>10,.0f} prices={price_by_step[step]}")
