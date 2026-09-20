"""Load-check + entry-point check for an extracted agent (no games played).

Kaggle runs the LAST callable defined at module level, while the local gate
harness calls `module.agent`.  This script proves the two agree and that the
module imports clean on this machine (native .so bridges raise WinError 193).

Usage: python tools/probe_agent_entry.py <agent.py> [<agent.py> ...]
"""
import importlib.util
import sys


def probe(path):
    spec = importlib.util.spec_from_file_location("probe_mod", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"{path}\n  IMPORT FAIL: {type(e).__name__}: {e}")
        return False
    callables = [v for v in mod.__dict__.values() if callable(v) and getattr(v, "__module__", "") == spec.name]
    last = callables[-1] if callables else None
    agent = getattr(mod, "agent", None)
    ok = callable(agent) and last is not None and (last is agent or last.__name__ == "agent")
    print(f"{path}\n  agent={getattr(agent, '__name__', agent)!r} last_callable="
          f"{getattr(last, '__name__', None)!r} -> {'OK' if ok else 'MISMATCH (gate would use a stale entrypoint)'}")
    return ok


if __name__ == "__main__":
    allok = True
    for p in sys.argv[1:]:
        try:
            allok &= probe(p)
        except Exception as e:
            print(f"{p}\n  PROBE FAIL: {type(e).__name__}: {e}")
            allok = False
    sys.exit(0 if allok else 1)
