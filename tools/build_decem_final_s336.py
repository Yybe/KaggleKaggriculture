"""FINAL CANDIDATE: lean_s336.py + guarded phase-desync buys.

Rationale (live-measured, not local-gate-measured):
  agents/lean_s336.py              -> Kaggle publicScore 1833.7  (submission 56687139)
  agents/lean_wflip_v9_standalone.py -> Kaggle publicScore 1708.7 (submission 56712190)
  v3 / v12 (wflip + CXTB7000 + desync) -> 1688.1

The DECEM line was built on the wflip base, which is ~125 live points WORSE
than the s336 spine we already had. Every sell-side lever is closed
(H-067/H-071) and the CXTB dial was measured exhausted on wflip (9k -435.5,
8k 8/8 tie), so the one live, non-refuted, non-sell-side mechanism left is
the phase-desync tie-break: worth exactly +7.2 head-to-head on wflip, proven
by ablation (agents/decem_nodesync.py vs v12 = 0W/8L -7.2).

This restores the better base AND keeps the verified lever. One appended
layer, nothing else touched.
"""
import hashlib
import os

ROOT = r"C:\Users\xxshi\Desktop\farmmasterV2"
SRC = os.path.join(ROOT, "lean_s336.py")
DST = os.path.join(ROOT, "agents", "decem_final_s336_desync.py")

text = open(SRC, encoding="utf-8").read()

# --- invariants on the source -------------------------------------------
assert "LAYER DECEM_SOVEREIGN" not in text, "source already carries a DECEM layer"
assert "step == 192" not in text, "source already desyncs at 192"
assert "step == 312" not in text, "source already desyncs at 312"
assert "_CXTB_MIN_REVENUE" in text
cx = [l for l in text.splitlines() if "_CXTB_MIN_REVENUE =" in l]
print("source CXTB:", cx)
print("source bytes:", len(text))
print("source sha  :", hashlib.sha256(open(SRC, "rb").read()).hexdigest()[:16])

LAYER = '''

# ==== LAYER DECEM_FINAL_S336_DESYNC: guarded phase desync (2026-10-01) ====
# Restores the live-better base spine (lean_s336 = 1833.7 publicScore vs
# lean_wflip_v9_standalone = 1708.7) and adds the one lever measured live on
# this family: two 1-unit WHEAT buys that break seed-level ties. Guarded by
# len(market) < 10 so the order is never silently dropped by
# maxMarketOrdersPerTurn. Verified worth exactly +7.2 head-to-head by
# ablation (agents/decem_nodesync.py vs agents/decem_sovereign_v12.py =
# 0W/8L/0T, mean -7.2). No market/sell overlay: that ceiling is +-0.35-0.6%
# (H-071) and is refuted (H-067).
_DSFDS_PARENT = agent

def decem_final_s336_desync_agent(observation, configuration=None):
    action = _DSFDS_PARENT(observation, configuration)
    step = int(observation.get('step', -1))
    market = action.setdefault('market', [])

    # Guarded: never exceed maxMarketOrdersPerTurn (extras are silently dropped).
    if step == 192 and len(market) < 10:
        market.append(['BUY_PRODUCT', 'WHEAT', 1])
    if step == 312 and len(market) < 10:
        market.append(['BUY_PRODUCT', 'WHEAT', 1])

    return action

agent = decem_final_s336_desync_agent
kaggle_submission_agent = agent
'''

out = text + LAYER
assert out.startswith(text)
assert out.count("step == 192") == 1
assert out.count("step == 312") == 1
assert out.count("_DSFDS_PARENT = agent") == 1

with open(DST, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)

# --- verify the written artefact ----------------------------------------
back = open(DST, encoding="utf-8").read()
assert back == out
assert back.count("_DSFDS_PARENT") == 2
print()
print("built  :", DST)
print("bytes  :", len(back), f"(+{len(back)-len(text)} layer)")
print("sha    :", hashlib.sha256(open(DST, "rb").read()).hexdigest()[:16])
