"""Static day-by-day cash-feasibility check for the v23 trajectories.

Simulates our player's cash flow alone (opponent passive at base prices):
  - out: HIRE (fib cost/day), BUY_LAND, BUY_SEED, BUY_ANIMAL, BUY_PRODUCT
  - in : SELL (at base market price; a lower-bound revenue estimate would
         use the glut curve, upper-bound the scarcity curve -- base is the
         middle and the ground truth comes from the engine smoke test)
Prints the per-day cash curve and flags any day where the plan goes negative.
"""
import json

from main_v23 import _LEGACY_ACTIONS, _REBALANCE_ACTIONS

STARTING_MONEY = 3000
LAND_PRICES = [1000, 2000, 4000]
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
BASE_PRICE = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
    "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100,
}


def fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def check(name, actions):
    cash = STARTING_MONEY
    hires_today = 0
    land_bought = 0
    day = 0
    worst = (999999, None)
    print(f"\n=== {name} ({len(actions)} steps) ===")
    print(f"{'day':>3} {'cash':>8} {'buy':>6} {'sell':>6} {'hire':>5} {'land':>5}  buys")
    for step, act in enumerate(actions):
        if step % 24 == 0 and step > 0:
            hires_today = 0
            day += 1
        buy = sell = hire = land = 0
        for order in act.get("market") or []:
            op = order[0]
            if op == "HIRE":
                c = fib(hires_today)
                hires_today += 1
                hire += c
            elif op == "BUY_LAND":
                if land_bought < len(LAND_PRICES):
                    c = LAND_PRICES[land_bought]
                    land_bought += 1
                    land += c
            elif op == "BUY_SEED":
                buy += SEED_COST.get(order[1], 0) * max(0, int(order[2]))
            elif op == "BUY_ANIMAL":
                buy += ANIMAL_COST.get(order[1], 0) * max(0, int(order[2]))
            elif op == "BUY_PRODUCT":
                buy += BASE_PRICE.get(order[1], 0) * max(0, int(order[2]))
            elif op == "SELL":
                sell += BASE_PRICE.get(order[1], 0) * max(0, int(order[2]))
        total_out = buy + hire + land
        cash += sell - total_out
        if cash < worst[0]:
            worst = (cash, day, step, sell, total_out)
        if step % 24 in (0, 12) or total_out or sell:
            print(f"{day:>3} {cash:>8.0f} {buy:>6} {sell:>6} {hire:>5} {land:>5}  "
                  f"{[o for o in act.get('market') or [] if o[0] != 'PASS']}")
    print(f"\nfinal cash: {cash:.0f}   worst: {worst}")
    return worst


if __name__ == "__main__":
    w1 = check("LEGACY (Azelearn)", _LEGACY_ACTIONS)
    w2 = check("REBALANCE (Khanh)", _REBALANCE_ACTIONS)
    for name, w in (("legacy", w1), ("rebalance", w2)):
        ok = w[0] >= 0
        print(f"{name}: {'PASS' if ok else 'FAIL'} (worst cash {w[0]:.0f} on day {w[1]})")
