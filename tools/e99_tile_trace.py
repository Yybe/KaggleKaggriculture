"""Dump tile (4,2) state + both seats' farmer/hand actions, steps 28-45, from probe replay.
Usage: Python311 tools/e99_tile_trace.py results/E99_losses/probe_replay_1898931754.json
"""
import json, sys

rep = json.load(open(sys.argv[1], encoding="utf-8"))
steps = rep["steps"]
for si in (0, 1):
    print(f"=== seat {si} ===")
    for t in range(28, 46):
        st = steps[t][si]
        obs = st.get("observation") or {}
        act = st.get("action") or {}
        farms = obs.get("farms") or []
        player = obs.get("player", si)
        tile = pos = None
        if len(farms) >= 2:
            me = farms[player]
            tiles = me.get("tiles") or []
            try:
                tile = tiles[4][2]
            except Exception:
                tile = "?"
            pos = [me.get("farmer")] + list(me.get("hands") or [])
        kind = tile.get("kind") if isinstance(tile, dict) else tile
        if isinstance(tile, dict):
            extra = {k: tile.get(k) for k in ("crop", "planted_day", "yield_units") if k in tile}
        else:
            extra = {}
        print(f"st{t} tile(4,2)={kind!r} {extra} farmer={act.get('farmer')} hands={act.get('hands')} pos={pos}")
