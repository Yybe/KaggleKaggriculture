"""E94: graft the 'One More Wheat' extra-day-maturity opening layer (Dmitrii Gluzdov,
Apache-2.0, verbatim from agents/pub_e80_omw.py) onto the CLEAN r78u base — i.e. keep
r78u's two newest gates (V219 union) and the d<20 fert-ROI 1.3 line, which the public
OMW file reverted (the confounder that sank E80's gate at -538 mean).

Rationale (live forensics 2026-09-21): loss ep111482825 (-4955, sid 56403425) = the
opponent running this opening family on our spine; their hand1 executes BUILD_PASTURE at
the temp-wheat tile at step ~34 while ours DIGs and only restores the pasture at step 55
-> their 8th cow places 21 steps earlier, ours sleeps in the shed all game (shed_final
COW:1). E80 queued exactly this experiment (then numbered E81): single-lever gate of the
layer alone, zero gate reverts.

Output: agents/pub_e94_omw_clean.py (new file; r78u untouched).
"""
import hashlib
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
CHAMP = BASE / "agents" / "pub_metav4_r78u.py"
OMW = BASE / "agents" / "pub_e80_omw.py"
OUT = BASE / "agents" / "pub_e94_omw_clean.py"

src = CHAMP.read_text(encoding="utf-8")
omw = OMW.read_text(encoding="utf-8")
assert hashlib.md5(str(CHAMP).encode()).hexdigest() or True  # path only; file md5 checked below
md5 = hashlib.md5(pathlib.Path(CHAMP).read_bytes()).hexdigest()
assert md5 == "319aad8c48675c51432ccec8f35264b8", f"champion md5 changed: {md5}"

# 1) mode flip
old_mode = "_ALT_MODE = 'EarlyCycle'"
assert src.count(old_mode) == 1
src = src.replace(old_mode, "_ALT_MODE = 'HybridOpening'")

# 2) restore the HybridOpening mode branch inside _alt_install (verbatim from OMW)
old_hunk = """    if mode=='Original': return
    CT_TABLE={}
    tape[0]['market']=[['BUY_PRODUCT','WHEAT',5],['BUY_SEED','WHEAT',1]]
    tape[1]['market']=[o for o in tape[1]['market'] if not (len(o)>=3 and o[0] in ('BUY_PRODUCT','SELL') and o[1]=='WHEAT')]
"""
new_hunk = """    if mode=='Original': return
    if mode=='HybridOpening':
        tape[0]['market']=list(tape[0]['market'])+[['BUY_SEED','WHEAT',1]]
    else:
        CT_TABLE={}
        tape[0]['market']=[['BUY_PRODUCT','WHEAT',5],['BUY_SEED','WHEAT',1]]
        tape[1]['market']=[o for o in tape[1]['market'] if not (len(o)>=3 and o[0] in ('BUY_PRODUCT','SELL') and o[1]=='WHEAT')]
"""
assert src.count(old_hunk) == 1, "anchor hunk not found in r78u"
src = src.replace(old_hunk, new_hunk)

# 3) append the maturity layer tail verbatim (from its header comment to EOF of OMW)
marker = "# Apache-2.0. Dmitrii Gluzdov: mature the temporary wheat one extra day."
idx = omw.index(marker)
tail = omw[idx:]
assert tail.rstrip().endswith("kaggle_submission_agent = agent")
src = src + "\n\n" + tail

OUT.write_text(src, encoding="utf-8")
print("wrote", OUT, len(src), "chars, md5", hashlib.md5(src.encode()).hexdigest())

# 4) verify the three deltas are the ONLY ones vs champion (line-level)
import difflib
d = list(difflib.unified_diff(pathlib.Path(CHAMP).read_text(encoding="utf-8").splitlines(),
                              src.splitlines(), lineterm=""))
adds = sum(1 for l in d if l.startswith("+") and not l.startswith("+++"))
dels = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
print(f"diff vs champion: +{adds}/-{dels} lines (expect ~4+3 removed / +21+44 added)")
for l in d[:80]:
    print(l)
