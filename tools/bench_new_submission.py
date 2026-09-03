"""H2H the NEW submission.py (v4) vs the old V18 + vs the live fleet on FRESH_SEEDS."""
import sys, pathlib, json, time
from concurrent.futures import ProcessPoolExecutor, as_completed
BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
FRESH_SEEDS = [314159,2718281,1414213,1732050,2236067,2645751,3162277,3245553,3316624,3464101,3588989,3660254,2426406,2469507,2549509,2641391,2745995,2871778]

def play_task(args):
    a_mod, b_mod, seed, swap = args
    import importlib, importlib.util, sys as _sys
    BASE2 = pathlib.Path(__file__).resolve().parent.parent
    def load(mod):
        if mod == "new_sub":
            spec = importlib.util.spec_from_file_location(f"_new_{seed}_{swap}", str(BASE2/"submission.py"))
            m = importlib.util.module_from_spec(spec)
            _sys.modules[spec.name]=m
            spec.loader.exec_module(m)
            return m.agent
        elif mod == "old_v18":
            # archived V18
            spec = importlib.util.spec_from_file_location(f"_old_{seed}_{swap}", str(BASE2/"archive/submission_v18_apexx_backup_20260903.py"))
            m = importlib.util.module_from_spec(spec)
            _sys.modules[spec.name]=m
            spec.loader.exec_module(m)
            return m.agent
        else:
            m = importlib.import_module(mod)
            fn = getattr(m,"agent",None)
            if fn is None:
                for alt in ["kaggle_agent_v58","kaggle_agent"]:
                    fn=getattr(m,alt,None)
                    if fn: break
            return fn
    fn_a = load(a_mod); fn_b = load(b_mod)
    fn0 = fn_b if swap else fn_a
    fn1 = fn_a if swap else fn_b
    try:
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps":720,"seed":seed}, debug=False)
        env.run([fn0, fn1])
        r0=float(env.state[0].get("reward",0)or 0); r1=float(env.state[1].get("reward",0)or 0)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return (a_mod,b_mod,seed,swap,score_a,score_b,None)
    except Exception as e:
        import traceback
        return (a_mod,b_mod,seed,swap,0,0,traceback.format_exc()[:500])

# We test new_sub vs old_v18 + vs the 3 other strong public (boatlee_v29 is now same as new_sub, so skip self)
PAIRS = [
 ("new_sub","old_v18","NEW (v4) vs OLD V18"),
 ("new_sub","agents._top_pub.salemali7_2900","NEW vs salemali 2900"),
 ("new_sub","agents._top_pub.pilkwang_kaitofukami_fork","NEW vs pilkwang v58"),
 ("new_sub","agents._top_pub.tetsutani_adaptive","NEW vs tetsutani"),
 ("new_sub","agents._top_pub.boatlee_v21","NEW vs boatlee v21"),
]
all_tasks=[]
for a,b,_ in PAIRS:
    for s in FRESH_SEEDS:
        all_tasks.append((a,b,s,False)); all_tasks.append((a,b,s,True))
def _run_bench():
    import os
    os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
    import warnings; warnings.filterwarnings("ignore")
    t0=time.time()
    jsonl_path=BASE/"results/bench_new_submission.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    f=open(jsonl_path,"w",encoding="utf-8")
    results={}
    with ProcessPoolExecutor(max_workers=6) as ex:
        futs={ex.submit(play_task,t):t for t in all_tasks}
        done=0
        import json
        for fut in as_completed(futs):
            a_mod,b_mod,seed,swap,sa,sb,err=fut.result()
            done+=1
            tag=f"{a_mod.split('.')[-1]} vs {b_mod.split('.')[-1]}"
            if err:
                print(f"[{done}/{len(all_tasks)}] ERR {tag} seed {seed}: {err[:200]}")
                f.write(json.dumps({"a":a_mod,"b":b_mod,"seed":seed,"swap":swap,"error":err})+"\n"); continue
            delta=sa-sb
            f.write(json.dumps({"a":a_mod,"b":b_mod,"seed":seed,"swap":swap,"score_a":sa,"score_b":sb,"delta":delta,"outcome":"WIN" if delta>0 else ("LOSS" if delta<0 else "TIE")})+"\n"); f.flush()
            results.setdefault((a_mod,b_mod),[]).append(delta)
            if done%18==0:
                print(f"  progress {done}/{len(all_tasks)} {time.time()-t0:.1f}s")
    f.close()
    print("\n"+"="*105)
    print(f"{'Pairing':<45} | {'Games':>5} | {'W-L-T':>11} | {'Win%':>6} | {'Mean':>10} | {'Min':>8} | {'Max':>8}")
    print("-"*105)
    summary={}
    for (a,b),deltas in sorted(results.items()):
        label=dict(PAIRS).get((a,b), f"{a} vs {b}")
        n=len(deltas); w=sum(1 for d in deltas if d>0); l=sum(1 for d in deltas if d<0); t=sum(1 for d in deltas if d==0)
        wr=w/n*100; md=sum(deltas)/n
        summary[label]={"games":n,"wins":w,"losses":l,"ties":t,"win_rate":wr,"mean":md,"min":min(deltas),"max":max(deltas)}
        print(f"{label:<45} | {n:5d} | {w:2d}-{l:2d}-{t:1d}      | {wr:5.1f}% | {md:+10.1f} | {min(deltas):+8.0f} | {max(deltas):+8.0f}")
    print("="*105)
    with open(BASE/"results/bench_new_submission_summary.json","w",encoding="utf-8") as out:
        json.dump(summary,out,indent=2)
    print(f"Saved {jsonl_path}, elapsed {time.time()-t0:.1f}s")

if __name__ == "__main__":
    _run_bench()
