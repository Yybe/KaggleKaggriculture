"""Diagnostic: does V16a's _recovery_sell still fire on engine 1.32.6 (interval=24)?

Usage: python diag_recovery_trace.py <seed> [seed ...] [outfile]

Loads submission.py (V16a bundle), wraps _recovery_sell and _terminal_liquidation,
plays vs the ground-truth kathimunishwar agent (both seats), and reports per game:
  - recovery fires          (step, item, qty sold, price)  — gate met, dead>0
  - blocked opportunities   (step, item, dead, price vs gate) — dead>0 but price<gate
  - window price peak/item  (steps 700-716) vs its gate
  - terminal dump           (step 717: qty per item, price) — what happened instead
  - rough unrealized uplift (peak_price - dump_price) * dead_units, per item

Output is written to <outfile> (default results/diag_recovery_1326.txt) AND stdout.
"""
import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath("agents"))

_ITEMS = ("STRAWBERRY", "MILK", "WOOL")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sell_map(orders):
    q = {}
    for order in (orders or []):
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
            item = str(order[1])
            q[item] = q.get(item, 0) + max(0, int(order[2]))
    return q


def _future_tape(v16, step):
    """Same formula as _recovery_sell: SELL qty of each item in tape AFTER this step."""
    out = {i: 0 for i in _ITEMS}
    for t in range(step + 1, len(v16._ACTIONS)):
        entry = v16._ACTIONS[t]
        if not isinstance(entry, dict):
            continue
        for order in (entry.get("market") or []):
            if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                item = str(order[1])
                if item in out:
                    out[item] += max(0, int(order[2]))
    return out


def run_seed(seed, out, seat_label):
    import kaggle_environments
    from kaggle_environments import make

    v16 = _load(os.path.abspath("submission.py"), "sub_v16")
    opp = _load(os.path.abspath("agents/kathimunishwar_replay_agent.py"), "kath")

    rec_log, term_log = [], []

    orig_rec = v16._recovery_sell
    orig_term = v16._terminal_liquidation

    def rec_wrap(obs, action, step):
        if 700 <= step < 717:
            prices = (obs.get("market") or {}).get("prices") or {}
            shed = (obs.get("private") or {}).get("shed") or {}
            before = list(action.get("market") or [])
            res = orig_rec(obs, action, step)
            rec_log.append({
                "step": step,
                "prices": {i: int(prices.get(i, 0) or 0) for i in _ITEMS},
                "shed": {i: int(shed.get(i, 0) or 0) for i in _ITEMS},
                "before": before,
                "after": list(res.get("market") or []),
            })
            return res
        return orig_rec(obs, action, step)

    def term_wrap(obs, action, step):
        if step >= 700:
            prices = (obs.get("market") or {}).get("prices") or {}
            shed = (obs.get("private") or {}).get("shed") or {}
            before = list(action.get("market") or [])
            res = orig_term(obs, action, step)
            term_log.append({
                "step": step,
                "prices": {i: int(prices.get(i, 0) or 0) for i in _ITEMS},
                "shed": {i: int(shed.get(i, 0) or 0) for i in _ITEMS},
                "before": before,
                "after": list(res.get("market") or []),
            })
            return res
        return orig_term(obs, action, step)

    v16._recovery_sell = rec_wrap
    v16._terminal_liquidation = term_wrap

    agents = [v16.agent, opp.agent] if seat_label == "seat0" else [opp.agent, v16.agent]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run(agents)

    steps = env.steps
    r0 = float(steps[-1][0].reward)
    r1 = float(steps[-1][1].reward)
    v16_reward = r0 if seat_label == "seat0" else r1
    opp_reward = r1 if seat_label == "seat0" else r0

    gates = dict(v16._RECOVERY_GATES)

    # ---- analysis ----
    fires = []
    blocked = []
    peaks = {i: 0 for i in _ITEMS}
    for e in rec_log:
        for i in _ITEMS:
            peaks[i] = max(peaks[i], e["prices"][i])
            shed = e["shed"][i]
            planned_now = _sell_map(e["before"]).get(i, 0)
            future = _future_tape(v16, e["step"]).get(i, 0)
            dead = shed - planned_now - future
            price = e["prices"][i]
            gate = gates.get(i, 0)
            fired_qty = _sell_map(e["after"]).get(i, 0) - planned_now
            if fired_qty > 0:
                fires.append((e["step"], i, fired_qty, price))
            elif dead >= 1 and price < gate:
                blocked.append((e["step"], i, dead, price, gate))

    # Terminal dump: the entry where SELL qty actually increased (usually step 717),
    # not the last logged step (719) where nothing is added anymore.
    dump = {i: 0 for i in _ITEMS}
    dump_price = {i: 0 for i in _ITEMS}
    dump_step = None
    for e in term_log:
        before_map = _sell_map(e["before"])
        after_map = _sell_map(e["after"])
        for i in _ITEMS:
            added = max(0, after_map.get(i, 0) - before_map.get(i, 0))
            if added > dump[i]:
                dump[i] = added
                dump_price[i] = e["prices"][i]
                dump_step = e["step"]
    # End-of-game shed leftover (what never got sold at all)
    end_shed = {i: 0 for i in _ITEMS}
    if rec_log:
        end_shed = rec_log[-1]["shed"]
    term = bool(term_log)

    def _w(line=""):
        out.write(line + "\n")
        print(line)

    _w(f"--- seed {seed} {seat_label}: V16a={v16_reward:,.0f}  opp={opp_reward:,.0f}  delta={v16_reward - opp_reward:+,.0f} ---")
    _w(f"    engine kaggle-environments {kaggle_environments.__version__}")
    if not fires and not blocked:
        _w("    recovery window 705-716: no dead inventory at all (nothing to sell)")
    for step, i, qty, price in fires:
        _w(f"    FIRE    step {step:3d} {i:<11} qty {qty:2d} @ px {price:3d}  (gate {gates[i]})")
    for step, i, dead, price, gate in blocked:
        _w(f"    BLOCKED step {step:3d} {i:<11} dead {dead:2d} @ px {price:3d} < gate {gate}")
    _w("    window price peaks (steps 700-716): " + "  ".join(
        f"{i[:3]}={peaks[i]}" + ("  OK" if peaks[i] >= gates[i] else f"  <gate {gates[i]}") for i in _ITEMS))
    if term:
        _w(f"    terminal dump @{dump_step}: " + "  ".join(
            f"{i[:3]} x{dump[i]} @ px {dump_price[i]}" for i in _ITEMS if dump[i]) or "nothing")
        _w("    end-of-game shed leftover: " + "  ".join(
            f"{i[:3]}={end_shed[i]}" for i in _ITEMS if end_shed[i]) or "empty")
        for i in _ITEMS:
            uplift = (peaks[i] - dump_price[i]) * dump[i]
            if dump[i] and uplift > 0:
                _w(f"    potential recovery uplift {i}: (peak {peaks[i]} - dump px {dump_price[i]}) x {dump[i]} = +{uplift:,.0f}")
    _w("")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    seeds = [int(s) for s in args if s.isdigit()] or [2000]
    outfile = next((a for a in args if not a.isdigit() and a.endswith(".txt")), None) or \
        os.path.abspath("results/diag_recovery_1326.txt")
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, "w", encoding="utf-8") as out:
        for seed in seeds:
            for seat in ("seat0", "seat1"):
                run_seed(seed, out, seat)
    print(f"\n[written] {outfile}")


if __name__ == "__main__":
    main()
