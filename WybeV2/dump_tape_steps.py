import importlib.util, json
spec = importlib.util.spec_from_file_location('v14mod', r'C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\v14_source.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ACT = mod._ACTIONS
steps = list(range(0, 50)) + list(range(166, 192))
for s in steps:
    e = ACT[s]
    f = e.get("farmer")
    hands = e.get("hands") or []
    mkt = e.get("market") or []
    print(f'S{s:3d} F={f} H{len(hands)}={hands} M={mkt}')
