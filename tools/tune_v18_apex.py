"""Clean parallel optimization script that writes structured results to disk."""
import os
import sys
import json
import glob
import copy
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

# Suppress OpenSpiel spam
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '.')
import submission
from kaggle_environments import make

# 1. Load THUNDER consensus routes
tape_dir = r'replays_new/tape_library'
sub1_files = [fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55373222_' in fp]
sub2_files = [fp for fp in glob.glob(os.path.join(tape_dir, '*.json')) if '_55381094_' in fp]

def get_consensus(files):
    eps = [json.load(open(fp, 'r', encoding='utf-8'))['route'][1:] for fp in files]
    cons = []
    for s in range(719):
        c = Counter(json.dumps(ep[s], sort_keys=True, separators=(',', ':')) for ep in eps)
        cons.append(json.loads(c.most_common(1)[0][0]))
    return cons

_TH1_ROUTE = get_consensus(sub1_files)
_TH2_ROUTE = get_consensus(sub2_files)
_V17_ROUTE = submission._REBALANCE_ACTIONS

ROUTES = {
    "v17": _V17_ROUTE,
    "th1": _TH1_ROUTE,
    "th2": _TH2_ROUTE,
}

class RouteReplayAgent:
    def __init__(self, route_name):
        self.route_name = route_name
        
    def __call__(self, obs, configuration=None):
        route = ROUTES[self.route_name]
        step = int(obs.get("step", 0) or 0)
        s = min(max(0, step), len(route) - 1)
        action = copy.deepcopy(route[s])
        action = submission._weed_repair_action(obs, action, route, s)
        return submission._align_hands(action, obs)

class CandidateV18Agent:
    def __init__(self, cfg):
        self.cfg = cfg
        self.route_name = cfg.get("route_name", "v17")
        self.wool_intercept_step = cfg.get("wool_intercept_step", 663)
        self.wool_intercept_qty = cfg.get("wool_intercept_qty", 8)
        self.milk_intercept_step = cfg.get("milk_intercept_step", 666)
        self.milk_intercept_qty = cfg.get("milk_intercept_qty", 9)
        self.enable_boatlee_relay = cfg.get("enable_boatlee_relay", True)
        self.enable_recovery = cfg.get("enable_recovery", True)
        self.recovery_gates = cfg.get("recovery_gates", {"STRAWBERRY": 60, "MILK": 110, "WOOL": 200})
        self.bump_cap = cfg.get("bump_cap", 1)
        
        self.state = {
            0: {"wool_intercepted": 0, "wool_due_step": 672, "milk_intercepted": 0, "milk_due_step": 672},
            1: {"wool_intercepted": 0, "wool_due_step": 672, "milk_intercepted": 0, "milk_due_step": 672},
        }

    def __call__(self, obs, configuration=None):
        try:
            step = int(obs.get("step", 0) or 0)
            seat = int(obs.get("player", 0) or 0)
            route = ROUTES[self.route_name]
            s = min(max(0, step), len(route) - 1)
            
            if step == 0:
                self.state[seat] = {"wool_intercepted": 0, "wool_due_step": 672, "milk_intercepted": 0, "milk_due_step": 672}
                
            st = self.state[seat]
            action = copy.deepcopy(route[s])
            action = submission._weed_repair_action(obs, action, route, s)
            action = submission._v16_convert_livestock(action, obs, s)
            action = submission._v16_wool_controller(action, obs, s)
            
            if self.enable_boatlee_relay:
                action = submission._rc3_market_relay(obs, action, s, submission._V16_OFFICIAL_CONFIGURATION)
                
            market = list(action.get("market") or [])
            private = obs.get("private", {}) or {}
            shed = dict(private.get("shed", {}) or {})
            
            # WOOL Intercept
            if s == self.wool_intercept_step and st["wool_intercepted"] == 0:
                avail_wool = int(shed.get("WOOL", 0) or 0)
                qty = min(self.wool_intercept_qty, avail_wool)
                if qty > 0 and len(market) < 10:
                    market.insert(0, ["SELL", "WOOL", qty])
                    st["wool_intercepted"] = qty
                    
            # Repay WOOL at due step
            if s == st["wool_due_step"] and st["wool_intercepted"] > 0:
                repay_wool = st["wool_intercepted"]
                new_market = []
                for ord in market:
                    if len(ord) >= 3 and ord[0] == "SELL" and ord[1] == "WOOL" and repay_wool > 0:
                        cur_qty = int(ord[2])
                        red = min(cur_qty, repay_wool)
                        cur_qty -= red
                        repay_wool -= red
                        if cur_qty > 0:
                            new_market.append([ord[0], ord[1], cur_qty])
                    else:
                        new_market.append(ord)
                market = new_market
                st["wool_intercepted"] = 0

            # MILK Intercept
            if s == self.milk_intercept_step and st["milk_intercepted"] == 0:
                avail_milk = int(shed.get("MILK", 0) or 0)
                qty = min(self.milk_intercept_qty, avail_milk)
                if qty > 0 and len(market) < 10:
                    market.insert(0, ["SELL", "MILK", qty])
                    st["milk_intercepted"] = qty
                    
            # Dead-Inventory Recovery Selling
            if self.enable_recovery and 705 <= s <= 716:
                mkt_info = obs.get("market", {})
                prices = mkt_info.get("prices", {}) if isinstance(mkt_info, dict) else {}
                for item in ("STRAWBERRY", "MILK", "WOOL"):
                    gate = self.recovery_gates.get(item, 0)
                    cur_px = prices.get(item, 0) or 0
                    if cur_px >= gate:
                        avail = int(shed.get(item, 0) or 0)
                        future_planned = 0
                        for fut_s in range(s, len(route)):
                            for raw in (route[fut_s].get("market") or []):
                                if len(raw) >= 3 and raw[0] == "SELL" and raw[1] == item:
                                    future_planned += int(raw[2])
                        dead = max(0, avail - future_planned)
                        if dead > 0 and len(market) < 10:
                            sell_qty = min(12, dead)
                            market.insert(0, ["SELL", item, sell_qty])
                            
            # Capselllate
            if s >= 456:
                new_m = []
                for ord in market:
                    if len(ord) >= 3 and ord[0] == "SELL" and ord[1] in ("STRAWBERRY", "MILK", "WOOL"):
                        item = ord[1]
                        qty = int(ord[2])
                        avail = int(shed.get(item, 0) or 0)
                        if avail > qty:
                            ord = [ord[0], ord[1], qty + min(self.bump_cap, avail - qty)]
                    new_m.append(ord)
                market = new_m

            action["market"] = market[:10]
            action = submission._rank_sell_slots(obs, action, submission._V16_OFFICIAL_CONFIGURATION)
            return submission._align_hands(action, obs)
        except Exception:
            farm = submission._farm(obs, submission._seat(obs))
            return {
                "farmer": ["PASS"],
                "hands": [["PASS"] for _ in (submission._get(farm, "hands", []) or [])],
                "market": [],
            }

GATE_SEEDS = [1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000, 9000000]
LOSING_SEEDS = [1176492926, 449229689]

def play_match_worker(args):
    agent_a_cfg, opp_type, seed, swap = args
    if agent_a_cfg == "v17_baseline":
        agent_a = RouteReplayAgent("v17")
    else:
        agent_a = CandidateV18Agent(agent_a_cfg)
        
    agent_b = RouteReplayAgent(opp_type)
    fn0 = agent_b if swap else agent_a
    fn1 = agent_a if swap else agent_b
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([fn0, fn1])
        st = env.state
        r0 = float(st[0].get("reward", 0) or 0)
        r1 = float(st[1].get("reward", 0) or 0)
        score_a = r1 if swap else r0
        score_b = r0 if swap else r1
        return score_a, score_b, None
    except Exception as e:
        return 0, 0, str(e)

def evaluate_batch(cfgs, opp_types, seeds, max_workers=10):
    tasks = []
    task_keys = []
    for cfg_idx, cfg in enumerate(cfgs):
        for opp in opp_types:
            for s in seeds:
                for swap in (False, True):
                    tasks.append((cfg, opp, s, swap))
                    task_keys.append((cfg_idx, opp, s, swap))
                    
    print(f"Running {len(tasks)} parallel matches across {max_workers} workers...")
    t0 = time.time()
    
    results_by_cfg = {}
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        raw_results = list(ex.map(play_match_worker, tasks))
        
    for (cfg_idx, opp, s, swap), (score_a, score_b, err) in zip(task_keys, raw_results):
        if cfg_idx not in results_by_cfg:
            results_by_cfg[cfg_idx] = {}
        if opp not in results_by_cfg[cfg_idx]:
            results_by_cfg[cfg_idx][opp] = []
        results_by_cfg[cfg_idx][opp].append((score_a, score_b, score_a - score_b))
        
    print(f"Completed in {time.time() - t0:.1f} seconds.")
    return results_by_cfg

if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    
    candidate_cfgs = [
        "v17_baseline",
    ]
    
    # Generate candidate grid
    grid_cfgs = []
    for route_name in ["v17", "th1", "th2"]:
        for wool_step in [662, 663, 664]:
            for wool_qty in [8, 16]:
                for milk_step in [666, 667]:
                    cfg = {
                        "route_name": route_name,
                        "wool_intercept_step": wool_step,
                        "wool_intercept_qty": wool_qty,
                        "milk_intercept_step": milk_step,
                        "milk_intercept_qty": 9,
                        "enable_boatlee_relay": True,
                        "enable_recovery": True,
                        "bump_cap": 1,
                    }
                    grid_cfgs.append(cfg)
                    
    all_cfgs = candidate_cfgs + grid_cfgs
    print(f"Total candidate configurations: {len(all_cfgs)}")
    
    # Evaluate across 8-seed gate vs both TH1 and TH2
    results = evaluate_batch(all_cfgs, ["th1", "th2"], GATE_SEEDS, max_workers=12)
    
    summary_rows = []
    for idx, cfg in enumerate(all_cfgs):
        res_th1 = results[idx]["th1"]
        res_th2 = results[idx]["th2"]
        
        d1 = [x[2] for x in res_th1]
        d2 = [x[2] for x in res_th2]
        
        w1 = sum(1 for d in d1 if d > 0)
        w2 = sum(1 for d in d2 if d > 0)
        
        md1 = sum(d1) / len(d1)
        md2 = sum(d2) / len(d2)
        total_md = (md1 + md2) / 2
        total_wr = (w1 + w2) / (len(d1) + len(d2)) * 100
        
        summary_rows.append({
            "idx": idx,
            "cfg": cfg,
            "wr_th1": f"{w1}/{len(d1)}",
            "md_th1": md1,
            "wr_th2": f"{w2}/{len(d2)}",
            "md_th2": md2,
            "total_wr": total_wr,
            "total_md": total_md,
        })
        
    summary_rows.sort(key=lambda r: -r["total_md"])
    
    with open('results/tune_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary_rows, f, indent=2)
        
    print("\n" + "="*80)
    print(f"{'Idx':>3} | {'Route':>5} | {'WoolStp':>7} | {'WoolQty':>7} | {'MilkStp':>7} | {'vs TH1 Δ':>10} | {'vs TH2 Δ':>10} | {'Total Δ':>10} | {'WinRate':>7}")
    print("="*80)
    for r in summary_rows[:15]:
        cfg = r["cfg"]
        if cfg == "v17_baseline":
            print(f"{r['idx']:3d} | {'v17':>5} | {'base':>7} | {'base':>7} | {'base':>7} | {r['md_th1']:+10.1f} | {r['md_th2']:+10.1f} | {r['total_md']:+10.1f} | {r['total_wr']:6.1f}%")
        else:
            print(f"{r['idx']:3d} | {cfg['route_name']:>5} | {cfg['wool_intercept_step']:7d} | {cfg['wool_intercept_qty']:7d} | {cfg['milk_intercept_step']:7d} | {r['md_th1']:+10.1f} | {r['md_th2']:+10.1f} | {r['total_md']:+10.1f} | {r['total_wr']:6.1f}%")
