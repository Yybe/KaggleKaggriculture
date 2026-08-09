"""Generate price-threshold variants of V15.5 from the fixed base file.
Only replaces the threshold constant, version string, and docstring line."""
import re

src = open(r"agents\kaggle_champion_v155.py", encoding="utf-8").read()
assert "_FIRE_THRESHOLD = 180" in src
assert "def _idle_fill" in src, "idle_fill must be present"

for T in (90, 120, 150, 180):
    body = src.replace("_FIRE_THRESHOLD = 180", f"_FIRE_THRESHOLD = {T}")
    body = body.replace('__version__ = "V15_5_Champion"', f'__version__ = "V15_5_T{T}"')
    body = re.sub(
        r'"""Champion Agent V15\.5:.*?winrate-focused refinement\)\.',
        f'"""V15.5-T{T}: V15 + price-threshold capselllate (fire only when item price >= {T}).',
        body,
        count=1,
        flags=re.S,
    )
    out = rf"agents\kaggle_v155_t{T}.py"
    with open(out, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"wrote {out} | idle_fill={'def _idle_fill' in body} | gate={'def _price_gate_ok' in body}")
