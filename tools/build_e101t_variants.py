"""E101t = E99 spine + the Apex V5 market layers with the preemption knobs exposed.

Same two mechanisms as pub_e101_apex_layers.py (cloned from tools/build_apex_v5.py), but the
preemption thresholds live in one `_T` dict so floors / window / phase / clip size can be swept
without editing the 1 MB spine.

Usage: WybeV2/rank_env/Scripts/python.exe tools/build_e101t_variants.py [TAG ...]
"""
import hashlib
import pathlib
import py_compile
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
SRC = BASE / "agents" / "pub_e99_pasture_fix.py"

# knobs: lo/hi window, phase (step % mod == phase), min shed units, price floors, clip sizes
VARIANTS = {
    # control: exact Apex V5 / E101 defaults
    "ctrl":   dict(lo=240, hi=671, mod=24, phase=23, avail=6, f_fert=75, f_wheat=20, f_other=80, q_fert=10, q_other=6),
    # higher price bar -> fewer, better preempts
    "f90":    dict(lo=240, hi=671, mod=24, phase=23, avail=6, f_fert=90, f_wheat=30, f_other=140, q_fert=10, q_other=6),
    "f110":   dict(lo=240, hi=671, mod=24, phase=23, avail=6, f_fert=110, f_wheat=40, f_other=180, q_fert=10, q_other=6),
    "f130":   dict(lo=240, hi=671, mod=24, phase=23, avail=6, f_fert=130, f_wheat=50, f_other=220, q_fert=10, q_other=6),
    # window: preemption is a mid-season lever, late-season dumps are the noisy d30 coin-flip band
    "w527":   dict(lo=240, hi=527, mod=24, phase=23, avail=6, f_fert=75, f_wheat=20, f_other=80, q_fert=10, q_other=6),
    "w575":   dict(lo=288, hi=575, mod=24, phase=23, avail=6, f_fert=75, f_wheat=20, f_other=80, q_fert=10, q_other=6),
    # clip size / trigger geometry
    "q4":     dict(lo=240, hi=671, mod=24, phase=23, avail=8, f_fert=75, f_wheat=20, f_other=80, q_fert=4, q_other=4),
    "ph22":   dict(lo=240, hi=671, mod=24, phase=22, avail=6, f_fert=75, f_wheat=20, f_other=80, q_fert=10, q_other=6),
    # combo: selective floors inside a mid-season window
    "c1":     dict(lo=240, hi=575, mod=24, phase=23, avail=6, f_fert=90, f_wheat=30, f_other=140, q_fert=8, q_other=5),
    # round 2: locate the floor cliff between f_other=80 (ctrl, -54.2) and 140 (f90, +82.2)
    "f85":    dict(lo=240, hi=671, mod=24, phase=23, avail=6, f_fert=85, f_wheat=25, f_other=110, q_fert=10, q_other=6),
    "f95":    dict(lo=240, hi=671, mod=24, phase=23, avail=6, f_fert=95, f_wheat=32, f_other=160, q_fert=10, q_other=6),
    # f90 clipped to the pre-528 window (w527 also removed the -592 tail)
    "f90w":   dict(lo=240, hi=527, mod=24, phase=23, avail=6, f_fert=90, f_wheat=30, f_other=140, q_fert=10, q_other=6),
    # f90 with a bigger clip: is the gain from selectivity or from volume?
    "f90q12": dict(lo=240, hi=671, mod=24, phase=23, avail=6, f_fert=90, f_wheat=30, f_other=140, q_fert=14, q_other=10),
    # f90 on the two-turn-ahead trigger
    "f90p22": dict(lo=240, hi=671, mod=24, phase=22, avail=6, f_fert=90, f_wheat=30, f_other=140, q_fert=10, q_other=6),
}

LAYER = '''

# ===========================================================================
# E101t: APEX V5 MARKET LAYERS (tunable preemption) grafted onto the E99 spine
# knobs: window @LO@..@HI@, trigger step%@MOD@==@PHASE@, floors @F_FERT@/@F_WHEAT@/@F_OTHER@
# ===========================================================================

_V5_ITEMS = ("WOOL", "MILK", "STRAWBERRY", "TOMATO", "MELON", "CARROT", "EGG", "FERTILIZER", "WHEAT")
_V5_STATE = {}

_T = {
    "lo": @LO@, "hi": @HI@, "mod": @MOD@, "phase": @PHASE@, "min_avail": @AVAIL@,
    "floors": {"FERTILIZER": @F_FERT@, "WHEAT": @F_WHEAT@, "other": @F_OTHER@},
    "qty": {"FERTILIZER": @Q_FERT@, "other": @Q_OTHER@},
}


def _apex_precision_terminal_sweep(observation, action):
    """At steps 716..719 (end of season), liquidate 100% of remaining shed inventory."""
    if not isinstance(action, dict):
        return action
    step = int(observation.get("step", 0))
    if step < 716:
        return action

    private = observation.get("private") or {}
    shed = private.get("shed") or {}
    market = list(action.get("market") or [])

    committed = {}
    for order in market:
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
            committed[order[1]] = committed.get(order[1], 0) + int(order[2])

    for item in _V5_ITEMS:
        if len(market) >= 10:
            break
        available = int(shed.get(item, 0) or 0) - committed.get(item, 0)
        if available > 0:
            market.append(["SELL", item, available])
            committed[item] = committed.get(item, 0) + available

    return dict(action, market=market[:10])


def _apex_tuned_clone_preemption(observation, action):
    """One turn ahead of the 24-turn clone sell wave, sell a clip at price >= floor and
    book it into per-seat debt so the scheduled step-24 order repays it (volume conserved)."""
    if not isinstance(action, dict):
        return action
    step = int(observation.get("step", 0))
    seat = int(observation.get("player", 0))
    state = _V5_STATE.setdefault(seat, {"step": -1, "debt": {}})
    if step <= state["step"]:
        state.clear()
        state.update(step=-1, debt={})
    state["step"] = step

    private = observation.get("private") or {}
    shed = private.get("shed") or {}
    market = list(action.get("market") or [])

    if state["debt"]:
        revised = []
        for order in market:
            if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                item = order[1]
                qty = int(order[2])
                debt = state["debt"].get(item, 0)
                if debt > 0:
                    repay = min(qty, debt)
                    state["debt"][item] -= repay
                    qty -= repay
                if qty > 0:
                    revised.append(["SELL", item, qty])
            else:
                revised.append(order)
        market = revised

    if _T["lo"] <= step <= _T["hi"] and (step % _T["mod"] == _T["phase"]) and len(market) < 10:
        obs_mkt = observation.get("market") or {}
        prices = obs_mkt.get("prices") or {}
        for item in ("FERTILIZER", "WHEAT", "MILK", "WOOL", "STRAWBERRY"):
            if len(market) >= 10:
                break
            avail = int(shed.get(item, 0) or 0)
            px = int(prices.get(item, 0) or 0)
            floor = _T["floors"].get(item, _T["floors"]["other"])
            if avail >= _T["min_avail"] and px >= floor and state["debt"].get(item, 0) <= 0:
                sell_qty = min(avail, _T["qty"].get(item, _T["qty"]["other"]))
                market.append(["SELL", item, sell_qty])
                state["debt"][item] = state["debt"].get(item, 0) + sell_qty
                break

    return dict(action, market=market[:10])


_V5_PARENT = agent
del agent


def agent(observation, configuration=None):
    action = _V5_PARENT(observation, configuration)
    try:
        action = _apex_tuned_clone_preemption(observation, action)
        action = _apex_precision_terminal_sweep(observation, action)
    except Exception:
        pass
    return action

agent.telemetry = getattr(_V5_PARENT, "telemetry", {})
'''


def build(tag):
    k = VARIANTS[tag]
    text = LAYER
    for name, val in (("LO", k["lo"]), ("HI", k["hi"]), ("MOD", k["mod"]), ("PHASE", k["phase"]),
                      ("AVAIL", k["avail"]), ("F_FERT", k["f_fert"]), ("F_WHEAT", k["f_wheat"]),
                      ("F_OTHER", k["f_other"]), ("Q_FERT", k["q_fert"]), ("Q_OTHER", k["q_other"])):
        text = text.replace("@%s@" % name, str(val))
    assert "@" not in text, "unsubstituted token in layer"

    src = SRC.read_text(encoding="utf-8")
    assert src.count("kaggle_submission_agent = agent") == 1, "E99 EOF marker not unique"
    body, tail = src.rsplit("kaggle_submission_agent = agent", 1)
    out = body + text + "\nkaggle_submission_agent = agent" + tail
    for sym in ("_apex_tuned_clone_preemption", "_apex_precision_terminal_sweep"):
        assert out.count(sym) == 2, f"{sym} not wired into variant {tag}"
    assert len(out) > len(src) + 1000, "layer too small vs base"

    dst = BASE / "agents" / f"pub_e101t_{tag}.py"
    dst.write_text(out, encoding="utf-8", newline="\r\n" if "\r\n" in src else "\n")
    py_compile.compile(str(dst), doraise=True)
    spec = __import__("importlib.util", fromlist=["util"]).spec_from_file_location(f"t_{tag}", str(dst))
    mod = __import__("importlib.util", fromlist=["util"]).module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.agent) and hasattr(mod, "_T"), f"{dst.name} missing symbols"
    print(f"built {dst.name} {len(out)}B md5={hashlib.md5(out.encode()).hexdigest()[:8]} _T={mod._T}")
    return dst


if __name__ == "__main__":
    tags = sys.argv[1:] or list(VARIANTS)
    for t in tags:
        build(t)
