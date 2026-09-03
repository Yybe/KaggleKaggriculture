"""Bench top 6 public kernels vs V18 APEXX on FRESH_SEEDS (both seats)."""
import sys, pathlib, json, time
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

FRESH_SEEDS = [314159,2718281,1414213,1732050,2236067,2645751,3162277,3245553,3316624,3464101,3588989,3660254,2426406,2469507,2549509,2641391,2745995,2871778]
CANDIDATES = [
  "agents._top_pub.salemali7_2900",
  "agents._top_pub.boatlee_v29",
  "agents._top_pub.lynnsakurai_v4",
  "agents._top_pub.boatlee_v21",
  "agents._top_pub.tetsutani_adaptive",
  "agents._top_pub.pilkwang_kaitofukami_fork",
]

def play_task(args):
    cand_mod, seed, swap = args
    # isolated imports per worker
    import importlib, importlib.util, sys as _sys
    BASE2 = pathlib.Path(__file__).resolve().parent.parent
    def load(mod):
        if mod == "v18":
            spec = importlib.util.spec_from_file_location(f"_v18_{seed}_{swap}", str(BASE2/"submission.py"))
            m = importlib.util.module_from_spec(spec)
            _sys.modules[spec.name] = m
            spec.loader.exec_module(m)
            return m.agent
        else:
            m = importlib.import_module(mod)
            fn = getattr(m, "agent", None)
            if fn is None:
                for alt in ["kaggle_agent_v58","kaggle_agent"]:
                    fn = getattr(m, alt, None)
                    if fn: break
            return fn
    cand_fn = load(cand_mod)
    champ_fn = load("v18")
    fn0 = champ_fn if swap else cand_fn
    fn1 = cand_fn if swap else champ_fn
    try:
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps":720, "seed":seed}, debug=False)
        env.run([fn0, fn1])
        r0 = float(env.state[0].get("reward",0) or 0)
        r1 = float(env.state[1].get("reward",0) or 0)
        cand_score = r1 if swap else r0
        champ_score = r0 if swap else r1
        return (cand_mod, seed, swap, cand_score, champ_score, None)
    except Exception as e:
        import traceback
        return (cand_mod, seed, swap, 0, 0, traceback.format_exc()[:600])

def main():
    import os
    os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
    import warnings
    warnings.filterwarnings("ignore")
    all_tasks = []
    for cand in CANDIDATES:
        for s in FRESH_SEEDS:
            all_tasks.append((cand, s, False))
            all_tasks.append((cand, s, True))
    print(f"BENCH: {len(CANDIDATES)} public candidates vs V18 APEXX, {len(all_tasks)} matches (2 seats x {len(FRESH_SEEDS)} seeds)")
    t0 = time.time()
    jsonl_path = BASE/"results/bench_top_vs_v18.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    import json
    f = open(jsonl_path,"w",encoding="utf-8")
    counts = {}
    # Use 8 workers - each env is ~1s, keeps OOM low on Win
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(play_task, t): t for t in all_tasks}
        done = 0
        for fut in as_completed(futs):
            cand_mod, seed, swap, sc, so, err = fut.result()
            done += 1
            short = cand_mod.split(".")[-1]
            if err:
                print(f"[{done}/{len(all_tasks)}] ERR {short} seed {seed} swap {swap}: {err[:260]}", flush=True)
                f.write(json.dumps({"cand":short,"seed":seed,"swap":swap,"error":err})+"\n"); f.flush()
                continue
            delta = sc - so
            rec = {"cand":short,"seed":seed,"swap":swap,"cand_score":sc,"champ_score":so,"delta":delta,"outcome":"WIN" if delta>0 else ("LOSS" if delta<0 else "TIE")}
            f.write(json.dumps(rec)+"\n"); f.flush()
            results.setdefault(short,[]).append(delta)
            if done % 18 == 0 or done == len(all_tasks):
                print(f"  progress {done}/{len(all_tasks)} {time.time()-t0:.1f}s", flush=True)
    f.close()
    print("\n"+"="*105)
    print(f"{'Candidate':<30} | {'Games':>5} | {'W-L-T':>11} | {'Win%':>6} | {'Mean d':>10} | {'Min':>8} | {'Max':>8}")
    print("-"*105)
    summary={}
    for cand, deltas in sorted(results.items()):
        n=len(deltas); w=sum(1 for d in deltas if d>0); l=sum(1 for d in deltas if d<0); t=sum(1 for d in deltas if d==0)
        wr=w/n*100 if n else 0; md=sum(deltas)/n if n else 0
        summary[cand]={"games":n,"wins":w,"losses":l,"ties":t,"win_rate":wr,"mean_delta":md,"min":min(deltas) if deltas else 0,"max":max(deltas) if deltas else 0}
        print(f"{cand:<30} | {n:5d} | {w:2d}-{l:2d}-{t:1d}      | {wr:5.1f}% | {md:+10.1f} | {min(deltas):+8.0f} | {max(deltas):+8.0f}")
    print("="*105)
    # Paired
    from collections import defaultdict
    per_seed=defaultdict(list)
    for line in open(jsonl_path,encoding="utf-8"):
        r=json.loads(line)
        if "error" in r: continue
        per_seed[(r["cand"], r["seed"])].append(r["delta"])
    print("\nPaired (both seats same seed, cand vs V18):")
    for cand in sorted(results):
        pairs=[v for (c,s),v in per_seed.items() if c==cand]
        pos=sum(1 for p in pairs if all(d>0 for d in p))
        neg=sum(1 for p in pairs if all(d<0 for d in p))
        mix=len(pairs)-pos-neg
        print(f"  {cand:<30} paired {pos:2d}W / {mix:2d} split / {neg:2d}L over {len(pairs)} seeds")
    with open(BASE/"results/bench_top_vs_v18_summary.json","w",encoding="utf-8") as out:
        json.dump(summary,out,indent=2)
    print(f"\nSaved {jsonl_path} + summary, elapsed {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
