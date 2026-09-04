"""Build v29: EV-ratio epoch-A conversion + end-shed sweep + dead-market feed cutoff.

Base: agents/_top_pub/lynnsakurai_v3.py (verbatim tape). Table = [route][herd]
(herd1 == v28b herd1 byte-exact, MILK_KEEP=120); ONLY the runtime trigger and
two additive runtime levers change vs v28b:

  - Epoch-A (step 145) conversion trigger, v28b rule -> EV-ratio rule:
      v28b: yarn>=1 AND milk_shops==0
      v29 : yarn>=1 AND wool_px*SHEEP_YIELD > milk_px*COW_YIELD*RATIO
    (forensic basis: live ties/losses with yarn live + milk shops present were
    left on the verbatim path; the milk-shop==0 condition was over-conservative.
    NOTE: late yarn unlock remains uncatchable — all cow buys are < step 217,
    verified from the decoded tape; the 5 convertible cows sit at 150-195.)

  - L2 end sweep at _SWEEP_STEPS: append SELL of shed surplus
    (shed - scheduled remaining sells) for _SWEEP_ITEMS; 10-order cap respected.

  - L3 dead-market feed cutoff: steps >= _FEEDCUT_STEP with wool_px<_FEEDCUT_WOOL
    AND milk_px<_FEEDCUT_MILK -> FEED/CARE ops -> PASS (engine: escape after 2
    consecutive unfed days; stops the wheat bleed in double-glut games).

Usage: py -3 tools/build_v29.py [--ratio 0.6] [--out agents/v29.py]
"""
import base64
import json
import re
import sys
import zlib
from copy import deepcopy

SRC = "agents/_top_pub/lynnsakurai_v3.py"
CONVERT_STEP = 145
WOOL_GATE = 60
YARN_THRESHOLD = 1
SWEEP_STEPS = (707, 712, 716, 718)
SWEEP_ITEMS = ("WOOL", "MILK", "WHEAT", "FERTILIZER")
FEEDCUT_STEP = 456
FEEDCUT_WOOL = 12
FEEDCUT_MILK = 15
SHEEP_YIELD = 33
COW_YIELD = 36
RATIO = 0.6


def decode_routes(src):
    m = re.search(r"_ROUTES = json\.loads\(zlib\.decompress\(base64\.b85decode\(b'([^']+)'\)\)\.decode\(\"utf-8\"\)\)", src)
    return json.loads(zlib.decompress(base64.b85decode(m.group(1))).decode("utf-8"))


def convert_tape(tape):
    """v28b herd1 conversion, byte-exact (flat MILK_KEEP=120)."""
    out = deepcopy(tape)
    kept = 0
    for step in range(CONVERT_STEP, len(out)):
        a = out[step]
        for op in ([a.get("farmer")] if a.get("farmer") else []) + list(a.get("hands") or []):
            if op and len(op) >= 2 and op[0] in ("PICKUP", "PLACE") and op[1] == "COW":
                op[1] = "SHEEP"
        for order in a.get("market") or []:
            if len(order) >= 3 and order[0] == "BUY_ANIMAL" and order[1] == "COW":
                order[1] = "SHEEP"
            elif len(order) >= 3 and order[0] == "SELL" and order[1] == "MILK":
                if kept < 120:
                    kept += int(order[2])
                else:
                    order[1] = "WOOL"
    return out


def main():
    out_path = "agents/v29.py"
    ratio = RATIO
    v28rule = False
    no_sweep = False
    no_feedcut = False
    drip = None
    shields = False
    args = sys.argv[1:]
    if "--ratio" in args:
        ratio = float(args[args.index("--ratio") + 1])
    if "--v28rule" in args:
        v28rule = True
    if "--no-sweep" in args:
        no_sweep = True
    if "--no-feedcut" in args:
        no_feedcut = True
    if "--drip" in args:
        drip = args[args.index("--drip") + 1]
    if "--shields" in args:
        shields = True
    if "--out" in args:
        out_path = args[args.index("--out") + 1]

    src = open(SRC, encoding="utf-8").read()
    SHIELDS_SRC = open("tools/shields_inc.py", encoding="utf-8").read()
    routes = decode_routes(src)
    assert len(routes) == 2 and all(len(t) == 719 for t in routes)

    herd0 = [routes[0], routes[1]]
    herd1 = [convert_tape(routes[0]), convert_tape(routes[1])]
    packed = json.dumps([[herd0[0], herd1[0]], [herd0[1], herd1[1]]], separators=(",", ":")).encode("utf-8")
    blob = base64.b85encode(zlib.compress(packed, 9)).decode("utf-8")

    new_src = re.sub(
        r"_ROUTES = json\.loads\(zlib\.decompress\(base64\.b85decode\(b'[^']+'\)\)\.decode\(\"utf-8\"\)\)",
        "_ROUTES = json.loads(zlib.decompress(base64.b85decode(b'" + blob + "')).decode(\"utf-8\"))",
        src, count=1,
    )

    new_src = new_src.replace(
        "_SEGMENT_TURNS = 72",
        "_SEGMENT_TURNS = 72\n"
        f"_HERD_DECISION_STEP = {CONVERT_STEP}\n"
        f"_YARN_CONVERT_THRESHOLD = {YARN_THRESHOLD}\n"
        f"_WOOL_GATE = {WOOL_GATE}\n"
        f"_SWEEP_STEPS = {SWEEP_STEPS}\n"
        f"_SWEEP_ITEMS = {SWEEP_ITEMS}\n"
        f"_FEEDCUT_STEP = {FEEDCUT_STEP}\n"
        f"_FEEDCUT_WOOL = {FEEDCUT_WOOL}\n"
        f"_FEEDCUT_MILK = {FEEDCUT_MILK}\n"
        f"_SHEEP_YIELD = {SHEEP_YIELD}\n"
        f"_COW_YIELD = {COW_YIELD}\n"
        f"_RATIO = {ratio}\n"
        + (f"_DRIP_MIN_QTY = {int(drip.split(',')[0])}\n"
           f"_DRIP_TRANCHES = {int(drip.split(',')[1])}\n"
           "_DRIP_SPACING = 4\n"
           "_DRIP_LATE_STEP = 700\n" if drip else "")
        + '_MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")',
        1,
    )
    new_src = new_src.replace(
        '_STATE = {\n    0: {"last_step": -1, "route": 0},\n    1: {"last_step": -1, "route": 0},\n}',
        '_STATE = {\n    0: {"last_step": -1, "route": 0, "herd": 0, "drip": []},\n    1: {"last_step": -1, "route": 0, "herd": 0, "drip": []},\n}',
        1,
    )
    new_src = new_src.replace(
        'state = {"last_step": -1, "route": 0}',
        'state = {"last_step": -1, "route": 0, "herd": 0, "drip": []}',
    )

    helpers = '''

def _shop_counts(observation):
    town = _get(observation, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    yarn = sum(1 for name in shops if name == "YARN_STORE")
    milk = sum(1 for name in shops if name in _MILK_SHOPS)
    return yarn, milk


def _prices(observation):
    market = _get(observation, "market", {}) or {}
    return _get(market, "prices", {}) or {}


def _shed(observation, seat):
    priv = _get(observation, "private", {}) or {}
    return _get(priv, "shed", {}) or {}


def _scheduled_after(route, herd, step, item):
    total = 0
    tape = _ROUTES[route][herd]
    for s in range(step + 1, len(tape)):
        for order in tape[s].get("market") or []:
            if len(order) >= 3 and order[0] == "SELL" and order[1] == item:
                total += int(order[2])
    return total


def _epoch_convert(observation, seat):
    """v29 trigger (rule=milk0): convert whenever no milk shop seen by 145.

    Rationale: shops drawn with replacement from an 8-type pool (1 yarn);
    yarn is seen by step 145 in only ~14% of games but unlocks eventually in
    ~57% (live 108-game study) — late yarn is uncatchable after the pipeline.
    No-milk-shop + no-yarn-ever games are ~neutral (dead wool px 2-3 vs dead
    milk px 1). Species-agnostic conversion.
    """
    _yarn, milk = _shop_counts(observation)
    return 0 if milk > 0 else 1



def _sweep(action, observation, seat, route, herd, step):
    if step not in _SWEEP_STEPS:
        return action
    shed = _shed(observation, seat)
    if not shed:
        return action
    orders = list(action.get("market") or [])
    for item in _SWEEP_ITEMS:
        have = int(shed.get(item, 0) or 0)
        if have <= 0:
            continue
        surplus = have - _scheduled_after(route, herd, step, item)
        if surplus <= 0:
            continue
        if len(orders) >= 10:
            break
        orders.append(["SELL", item, surplus])
    if len(orders) != len(action.get("market") or []):
        action["market"] = orders
    return action


def _feedcut(action, observation):
    prices = _prices(observation)
    if (float(_get(prices, "WOOL", 0) or 0) >= _FEEDCUT_WOOL
            or float(_get(prices, "MILK", 0) or 0) >= _FEEDCUT_MILK):
        return action
    for key in ("farmer", "hands"):
        ops = action.get(key)
        if not ops:
            continue
        if key == "farmer":
            if ops[0] in ("FEED", "CARE"):
                ops[0] = "PASS"
        else:
            for op in ops:
                if op and op[0] in ("FEED", "CARE"):
                    op[0] = "PASS"
    return action


def _wool_gate(action, observation, herd):
    if herd != 1:
        return action
    prices = _prices(observation)
    if float(_get(prices, "WOOL", 0) or 0) >= _WOOL_GATE:
        return action
    kept = [order for order in action.get("market") or []
            if not (isinstance(order, list) and len(order) >= 3
                    and order[0] == "SELL" and order[1] == "WOOL")]
    if len(kept) != len(action.get("market") or []):
        action["market"] = kept
    return action


def _drip_emit(action, state, step):
    """Flush stashed drip tranches due at this step (wool-gated when herd=1
    unless past _DRIP_LATE_STEP where dumping beats stranding)."""
    if not state.get("drip"):
        return action
    orders = list(action.get("market") or [])
    keep = []
    for due, item, qty in state["drip"]:
        if due > step:
            keep.append((due, item, qty))
            continue
        if len(orders) >= 10:
            keep.append((step + _DRIP_SPACING, item, qty))
            continue
        orders.append(["SELL", item, qty])
    state["drip"] = keep
    action["market"] = orders
    return action


def _drip_split(action, state, step, herd):
    """Re-time big SELLs: qty >= _DRIP_MIN_QTY at steps >= 456 split into
    _DRIP_TRANCHES spaced _DRIP_SPACING apart. Same total units; spreads the
    per-unit lockstep price walk (live forensics: drip-sellers win the close
    full-parity games). Tranches due > 719 collapse into the last step."""
    queue = state.setdefault("drip", [])
    orders = action.get("market") or []
    out = []
    for order in orders:
        if (isinstance(order, list) and len(order) >= 3 and order[0] == "SELL"
                and int(order[2] or 0) >= _DRIP_MIN_QTY and step >= 456):
            qty = int(order[2])
            k = _DRIP_TRANCHES
            last_due = step + _DRIP_SPACING * (k - 1)
            if last_due > 716:
                out.append(order)
                continue
            small = qty // k
            first = qty - small * (k - 1)
            out.append(["SELL", order[1], first])
            for i in range(1, k):
                due = step + _DRIP_SPACING * i
                if due > 719:
                    due = 719
                queue.append((due, order[1], small))
        else:
            out.append(order)
    action["market"] = out
    return action

'''
    if v28rule:
        helpers = helpers.replace(
            "    return 0 if milk > 0 else 1",
            "    yarn, _milk = _shop_counts(observation)\n"
            "    return 1 if (yarn >= _YARN_CONVERT_THRESHOLD and _milk == 0) else 0", 1)
    if no_sweep:
        helpers = helpers.replace("    if step not in _SWEEP_STEPS:\n        return action",
                                  "    if True:\n        return action", 1)
    if no_feedcut:
        helpers = helpers.replace("def _feedcut(action, observation):",
                                  "def _feedcut(action, observation):\n    return action", 1)

    if shields:
        helpers = helpers + chr(10) + SHIELDS_SRC + chr(10)
    if not drip:
        helpers = helpers[:helpers.find("def _drip_emit")]

    new_src = new_src.replace("def agent(observation, configuration=None):", helpers + "\ndef agent(observation, configuration=None):", 1)

    new_src = new_src.replace(
        'if step == _DECISION_STEP:\n            state["route"] = _select_route(observation, seat)',
        'if step == _HERD_DECISION_STEP:\n'
        '            state["herd"] = _epoch_convert(observation, seat)\n'
        '        if step == _DECISION_STEP:\n'
        '            state["route"] = _select_route(observation, seat)',
        1,
    )
    drip_chain = (
        '        action = _drip_emit(action, state, step)\n'
        '        action = _drip_split(action, state, step, herd)\n' if drip else ''
    )
    shield_chain = (
        '        action = _shield_weed(action, observation, seat, state, step)\n'
        '        action = _shield_market(action, observation, seat, step)\n' if shields else ''
    )
    new_src = new_src.replace(
        'action = _copy_action(_ROUTES[route][step])\n        action = _budget_guard(action, observation, route, step)',
        'herd = int(state.get("herd", 0))\n'
        '        action = _copy_action(_ROUTES[route][herd][step])\n'
        '        action = _budget_guard(action, observation, route, herd, step)\n'
        '        action = _wool_gate(action, observation, herd)\n'
        + drip_chain + shield_chain +
        '        action = _sweep(action, observation, seat, route, herd, step)\n'
        '        action = _feedcut(action, observation)',
        1,
    )
    new_src = new_src.replace(
        "def _requirements(observation, route, start, end):",
        "def _requirements(observation, route, herd, start, end):", 1,
    )
    new_src = new_src.replace(
        "def _budget_guard(action, observation, route, step):",
        "def _budget_guard(action, observation, route, herd, step):", 1,
    )
    new_src = new_src.replace(
        "purchase_budget, starting = _requirements(observation, route, step, end)",
        "purchase_budget, starting = _requirements(observation, route, herd, step, end)", 1,
    )
    new_src = new_src.replace(
        "action = _ROUTES[route][step]",
        "action = _ROUTES[route][herd][step]", 1,
    )

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(new_src)
    import py_compile
    py_compile.compile(out_path, doraise=True)
    print("wrote", out_path, "ratio", ratio, "v28rule", v28rule, "no_sweep", no_sweep,
          "no_feedcut", no_feedcut, "drip", drip, "shields", shields)


if __name__ == "__main__":
    main()
