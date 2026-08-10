import base64, zlib, re
src = open(r'C:\Users\xxshi\Desktop\farmmasterV2\submission.py', encoding='utf-8').read()
m = re.search(r'_V14_EMBEDDED_B85 = """(.*?)"""', src, re.S)
print('found b85:', bool(m))
if m:
    data = base64.b85decode(m.group(1))
    out = zlib.decompress(data).decode('utf-8')
    open(r'C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\v14_source.py', 'w', encoding='utf-8').write(out)
    print('written', len(out), 'chars')
    # dump the tape structure summary
    import importlib.util
    spec = importlib.util.spec_from_file_location('v14mod', r'C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\v14_source.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print('has _ACTIONS:', hasattr(mod, '_ACTIONS'), 'len:', len(getattr(mod, '_ACTIONS', [])))
    print('has _MARKET_PARAMS:', hasattr(mod, '_MARKET_PARAMS'), getattr(mod, '_MARKET_PARAMS', None))
