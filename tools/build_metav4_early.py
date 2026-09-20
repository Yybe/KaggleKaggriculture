"""Build agents/pub_metav4_early.py = pub_metav4.py + the EarlyCycle opening layer.

The EarlyCycle layer is grafted verbatim from the tail of agents/pub_2950peak.py
(the additive diff pub_2945farm.py -> pub_2950peak.py: a self-contained block that
starts at the "# Bounded alternative productive openings." banner and runs to EOF).

Pre-flight checks (all must hold, else we abort without writing):
  * source files are the expected unmodified builds (md5 pin);
  * no symbol collisions between the grafted block and pub_metav4.py;
  * pub_metav4 exposes the graft anchors the block needs: `agent` as last
    executable statement's global, `_IMPL.chassis.routes[0]`, module-global
    `CT_TABLE`, `copy`;
  * route-0 opening tape in pub_metav4 is byte-identical to pub_2945farm's over
    the 96 steps the surgery touches, so every `assert` inside _alt_install holds.

Usage: python tools/build_metav4_early.py [--force]
"""
import hashlib
import importlib.util
import os
import re
import sys

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BASE = os.path.join(ROOT, "agents", "pub_metav4.py")
SPINE = os.path.join(ROOT, "agents", "pub_2945farm.py")
DONOR = os.path.join(ROOT, "agents", "pub_2950peak.py")
OUT = os.path.join(ROOT, "agents", "pub_metav4_early.py")
BANNER = "# Bounded alternative productive openings."

PINS = {
    "agents/pub_metav4.py": "3023521175bf598965eed5759f756802",
    "agents/pub_2945farm.py": "ca0132cad977506a39a1a850f26e53fe",
    "agents/pub_2950peak.py": "428016ee35c2a8009577338f7c01bc81",
}


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load(path, name):
    sys.path.insert(0, os.path.join(ROOT, "agents"))
    sys.path.insert(0, os.path.join(ROOT, "Kaggriculture"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fail(msg):
    print("GRAFT_ABORT: " + msg)
    return 1


def main():
    os.chdir(ROOT)
    if os.path.exists(OUT) and "--force" not in sys.argv:
        return fail(f"{OUT} already exists (use --force to rebuild)")

    print("BUILD pins checked: " + " ".join(f"{os.path.basename(v)}={md5(v)}" for v in PINS))
    for rel, want in PINS.items():
        got = md5(rel)
        if got != want:
            return fail(f"md5 drift on {rel}: {got} != pinned {want}")

    donor = open(DONOR, encoding="utf-8").read().splitlines(keepends=True)
    start = next((i for i, ln in enumerate(donor) if ln.startswith(BANNER)), None)
    if start is None:
        return fail("EarlyCycle banner not found in pub_2950peak.py")
    block = "".join(donor[start:])
    print(f"BUILD extracted EarlyCycle block: {len(donor) - start} lines "
          f"({donor[start].rstrip()!r} .. EOF)")

    base_src = open(BASE, encoding="utf-8").read()
    if base_src.endswith("\n") is False:
        base_src += "\n"

    # symbol collision check
    names = set(re.findall(r"\b(_ALT_[A-Z_]+|_alt_[a-z_]+)\b", block))
    hits = sorted(n for n in names if re.search(r"\b%s\b" % re.escape(n), base_src))
    if hits:
        return fail(f"symbol collision with pub_metav4.py: {hits}")
    print(f"BUILD graft symbols (collision-free): {sorted(names)}")

    # last statement of pub_metav4 must hand back a plain `agent` global
    tail = base_src.rstrip().splitlines()[-1]
    if not re.fullmatch(r"agent\s*=\s*globals\(\)\.pop\(['\"]agent['\"]\)", tail.strip()):
        return fail(f"unexpected pub_metav4 tail: {tail!r}")

    # runtime anchor / tape-identity checks
    mods = {"meta": load(BASE, "_graft_meta"), "spine": load(SPINE, "_graft_spine")}
    for k, m in mods.items():
        if not hasattr(m, "_IMPL") or not hasattr(m, "CT_TABLE") or not hasattr(m, "copy"):
            return fail(f"{k}: missing graft anchor (_IMPL/CT_TABLE/copy)")
    tape_m = mods["meta"]._IMPL.chassis.routes[0]
    tape_s = mods["spine"]._IMPL.chassis.routes[0]
    if tape_m[:96] != tape_s[:96]:
        return fail("route-0 tape[0:96] differs between metav4 and 2945 spine: "
                    "opening surgery context is NOT clean")
    if mods["meta"].CT_TABLE != mods["spine"].CT_TABLE:
        return fail("CT_TABLE differs between metav4 and 2945 spine")
    print("BUILD anchors OK: _IMPL.chassis.routes[0], CT_TABLE, copy;"
          " tape[0:96] identical to 2945 spine (%d steps)" % len(tape_m[:96]))

    header = (
        "\n# ---------------------------------------------------------------------------\n"
        "# Composite: pub_metav4.py (local incumbent, md5 %s) + the EarlyCycle opening-\n"
        "# surgery layer grafted verbatim from pub_2950peak.py (md5 %s), i.e. the exact\n"
        "# additive diff pub_2945farm.py -> pub_2950peak.py (+50/game vs base, 16W/0L).\n"
        "# Built by tools/build_metav4_early.py; no existing agent file was modified.\n"
        "# ---------------------------------------------------------------------------\n"
        % (PINS["agents/pub_metav4.py"], PINS["agents/pub_2950peak.py"])
    )
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(base_src + header + block)
    compile(open(OUT, encoding="utf-8").read(), OUT, "exec")
    print(f"BUILD wrote {OUT} md5={md5(OUT)} lines={sum(1 for _ in open(OUT, encoding='utf-8'))}")

    # post-build pin re-check: sources untouched
    for rel, want in PINS.items():
        if md5(rel) != want:
            return fail(f"source modified during build: {rel}")
    print("BUILD sources unchanged (md5 pins still hold)")
    print("BUILD RESULT=OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
