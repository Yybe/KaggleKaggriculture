import importlib.util, os, pathlib, sys, json
BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
A = BASE/"agents"/"pub_e94_omw_clean.py"; B = BASE/"agents"/"friend_r78ub.py"
def load(p,n):
    spec=importlib.util.spec_from_file_location(n,str(p)); m=importlib.util.module_from_spec(spec)
    sys.modules[n]=m; spec.loader.exec_module(m); return m
def entry(m):
    for fn in ("agent","kaggle_agent"):
        f=getattr(m,fn,None)
        if callable(f): return f
    raise RuntimeError
sink=[]
def wrap(f,tag):
    def g(obs,cfg=None):
        a=f(obs,cfg)
        if obs.get("step",0) in (0,1,2):
            sink.append((tag,obs["step"],json.dumps(a.get("market"))[:160]))
        return a
    return g
noop=lambda obs,cfg=None:{}
from kaggle_environments import make
mode=sys.argv[1]
fa=entry(load(A,"probe_a"))
fb=entry(load(B,"probe_b"))
pair={"a_only":(wrap(fa,"A"),"A"),"b_only":(wrap(fb,"B"),"B"),"both":(wrap(fa,"A"),"A")}
if mode=="both": pair=pair  # both handled below
cfg={"episodeSteps":5}
env=make("kaggriculture",configuration=cfg,debug=False)
if mode=="a_only": env.run([wrap(fa,"A"),noop])
elif mode=="b_only": env.run([wrap(fb,"B"),noop])
else: env.run([wrap(fa,"A"),wrap(fb,"B")])
for r in sink: print(*r)
