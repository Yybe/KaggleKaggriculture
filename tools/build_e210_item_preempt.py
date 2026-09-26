"""E210/E211: item-identity preempts — the one untried direction §45 left open.

Mechanism: q8's WHEAT/FERTILIZER pass and every inherited dose stay byte-identical;
a second pass A sells ONE clip of a non-rebuyable crop item at its measured peak
hour (§33/E193 phase table, the same source that put MILK/WOOL at h01 for E206):
  * E210 STRAWBERRY at hour 13
  * E211 CARROT     at hour 00
STRAWBERRY and CARROT have no `BUY_PRODUCT` branch (kaggriculture.py:598-601), so a
clip sold in them cannot be undone by the engine's no-arbitrage round trip (§43),
and the debt ledger clips the parent's next scheduled sale of that same item
(`_e137_repay` is generic over items), keeping total volume conserved (E57c law).

The hour, not a price floor, is the fire condition — exactly as in E206. One item
per turn, slot-guarded, booked into `state["debt"]`.

Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e210_item_preempt.py
"""
import importlib.util
import inspect
import os
import py_compile
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "agents", "cha22_e199_lo96q8.py")

# name, item, hours, qty, min_avail
VARIANTS = [
    ("cha22_e210_straw_h13q6.py", "STRAWBERRY", (13,), 6, 6),
    ("cha22_e211_carrot_h00q6.py", "CARROT", (0,), 6, 6),
]

ANCHORS = ("_E137_T = {", "def _e137_repay(", "def _e137_preempt(", "_E185_FIRES = []",
           "_E185_QTY_WHEAT = 8", "_E185_LO = 96", "_E185_FLOOR_WHEAT = 24")

LAYER = '''

# ===========================================================================
# E210 item-identity preempt: one non-rebuyable crop clip at its measured peak
# hour, appended after the E199 dose and rebinding `_e137_preempt` (call-time
# global, spine untouched).  Pass A is the new mechanism; pass B is q8's
# WHEAT/FERTILIZER preempt re-expressed verbatim against the inherited
# `_E185_*` globals.  Repayment uses the existing generic `_e137_repay`, so the
# clip is booked out of the parent's next scheduled sale of the same item.
# ===========================================================================
_E210_HOURS = __HOURS__
_E210_QTY = __QTY__
_E210_MIN_AVAIL = __MIN_AVAIL__
_E210_ITEM = "__ITEM__"
_E210_FIRES = []


def _e137_preempt(observation, action, state):
    t = _E137_T
    step = int(observation.get("step", 0) or 0)
    if step == 0:
        del _E185_FIRES[:]
        del _E210_FIRES[:]
    if not (_E185_LO <= step <= t["hi"]):
        return action
    shed = (observation.get("private") or {}).get("shed") or {}
    prices = ((observation.get("market") or {}).get("prices")) or {}
    market = list(action.get("market") or [])

    # --- pass A: sell one crop clip at its peak hour, book it against the
    # parent's next sale of that same item.  Hour 13/0 never collides with the
    # phase-23 WHEAT pass, so no cross-pass guard is needed.
    if step % t["mod"] in _E210_HOURS:
        avail = int(shed.get(_E210_ITEM, 0) or 0)
        if avail >= _E210_MIN_AVAIL and state["debt"].get(_E210_ITEM, 0) <= 0:
            if len(market) >= 10:
                _E137_REPORT["e137_slot_blocks"] += 1
            else:
                qty = min(avail, _E210_QTY)
                px = int(prices.get(_E210_ITEM, 0) or 0)
                if qty > 0:
                    market.append(["SELL", _E210_ITEM, qty])
                    state["debt"][_E210_ITEM] = state["debt"].get(_E210_ITEM, 0) + qty
                    _E137_REPORT["e137_preempts"] += 1
                    _E137_REPORT["e137_preempt_units"] += qty
                    _E185_FIRES.append((step, _E210_ITEM, px, qty, int(observation.get("player", 0) or 0), avail))
                    _E210_FIRES.append((step, _E210_ITEM, px, qty, int(observation.get("player", 0) or 0), avail))

    # --- pass B: the inherited E199 dose (identical predicate, identical order).
    if step % t["mod"] != _E185_PHASE:
        return dict(action, market=market[:10])
    for item in _E137_ORDER:
        avail = int(shed.get(item, 0) or 0)
        px = int(prices.get(item, 0) or 0)
        if item == "WHEAT":
            floor = _E185_FLOOR_WHEAT
        else:
            floor = t["floors"].get(item, t["floors"]["other"])
        min_avail = _E185_MIN_AVAIL if item == "WHEAT" else t["min_avail"]
        if avail >= min_avail and px >= floor and state["debt"].get(item, 0) <= 0:
            if len(market) >= 10:
                _E137_REPORT["e137_slot_blocks"] += 1
                break
            qty_cap = _E185_QTY_WHEAT if item == "WHEAT" else t["qty"].get(item, t["qty"]["other"])
            qty = min(avail, qty_cap)
            if qty <= 0:
                break
            market.append(["SELL", item, qty])
            state["debt"][item] = state["debt"].get(item, 0) + qty
            _E137_REPORT["e137_preempts"] += 1
            _E137_REPORT["e137_preempt_units"] += qty
            _E185_FIRES.append((step, item, px, qty, int(observation.get("player", 0) or 0), avail))
            break
    return dict(action, market=market[:10])
'''


def build(dst_name, item, hours, qty, min_avail):
    dst = os.path.join(BASE, "agents", dst_name)
    with open(SRC, encoding="utf-8", newline="") as fh:
        base = fh.read()
    for a in ANCHORS:
        assert a in base, "anchor moved in %s: %s" % (SRC, a)
    blk = (LAYER.replace("__HOURS__", repr(tuple(hours)))
           .replace("__QTY__", str(qty)).replace("__MIN_AVAIL__", str(min_avail))
           .replace("__ITEM__", item)
           .strip().replace("\n", "\r\n"))
    assert "__QTY__" not in blk and "__HOURS__" not in blk and "__MIN_AVAIL__" not in blk and "__ITEM__" not in blk
    out = base.rstrip("\r\n") + "\r\n" + blk + "\r\n"
    with open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    py_compile.compile(dst, doraise=True)

    spec = importlib.util.spec_from_file_location("chk_e210_" + dst_name[7:-3], dst)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    # inherited dose must still be q8's
    assert (mod._E185_LO, mod._E185_FLOOR_WHEAT, mod._E185_QTY_WHEAT, mod._E185_MIN_AVAIL,
            mod._E185_PHASE) == (96, 24, 8, 6, 23), "inherited WHEAT pass mutated"
    assert mod._E137_T["lo"] == 240 and mod._E137_T["hi"] == 671, "shipped table mutated"
    assert mod._E210_HOURS == tuple(hours) and mod._E210_QTY == qty and mod._E210_MIN_AVAIL == min_avail
    assert mod._E210_ITEM == item
    src_txt = inspect.getsource(mod._e137_preempt)
    assert "_E210_FIRES.append" in src_txt and "_E185_FIRES.append" in src_txt, "a pass went missing"
    assert src_txt.count("break") == 3, "first-match-wins shape changed"
    assert mod.agent is not None and callable(mod.agent)
    tele = getattr(mod.agent, "telemetry", {})
    assert "e137_preempts" in dict(tele), "telemetry chain broken"
    print("WROTE agents/%-32s item=%-11s hours=%-4s qty=%-3d min_avail=%d  bytes %+d"
          % (dst_name, item, ",".join(map(str, hours)), qty, min_avail, len(out) - len(base)), flush=True)


def main():
    for v in VARIANTS:
        build(*v)


if __name__ == "__main__":
    main()
