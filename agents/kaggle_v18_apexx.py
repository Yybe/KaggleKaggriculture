"""V18 APEXX: THUNDER, V17, and V18 Killer Agent.

Combines adaptive counter-preemption, dynamic dead-inventory recovery,
opponent signature matching, and guarded market relay.
"""
import copy
import sys
import os

# Allow standalone importing
if '.' not in sys.path:
    sys.path.insert(0, '.')

import submission

class V18ApexAgent:
    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.route_name = self.cfg.get("route_name", "v17")
        self.wool_intercept_step = self.cfg.get("wool_intercept_step", 663)
        self.wool_intercept_qty = self.cfg.get("wool_intercept_qty", 16)
        self.milk_intercept_step = self.cfg.get("milk_intercept_step", 666)
        self.milk_intercept_qty = self.cfg.get("milk_intercept_qty", 9)
        self.melon_preempt_step = self.cfg.get("melon_preempt_step", 239)
        self.melon_preempt_qty = self.cfg.get("melon_preempt_qty", 6)
        self.enable_boatlee_relay = self.cfg.get("enable_boatlee_relay", True)
        self.enable_recovery = self.cfg.get("enable_recovery", True)
        self.recovery_start = self.cfg.get("recovery_start", 648)
        self.recovery_gates = self.cfg.get("recovery_gates", {
            "STRAWBERRY": 60, "MILK": 110, "WOOL": 180, "CARROT": 30, "WHEAT": 20
        })
        self.bump_cap = self.cfg.get("bump_cap", 1)
        
        self.state = {
            0: {"wool_intercepted": 0, "wool_repaid": False, "milk_intercepted": 0, "milk_repaid": False, "melon_preempted": False},
            1: {"wool_intercepted": 0, "wool_repaid": False, "milk_intercepted": 0, "milk_repaid": False, "melon_preempted": False},
        }

    def __call__(self, obs, configuration=None):
        try:
            cfg_env = configuration or submission._V16_OFFICIAL_CONFIGURATION
            step = int(submission._get(obs, "step", 0) or 0)
            seat = submission._seat(obs)
            
            if step == 0:
                self.state[seat] = {
                    "wool_intercepted": 0, "wool_repaid": False,
                    "milk_intercepted": 0, "milk_repaid": False,
                    "melon_preempted": False
                }
                
            st = self.state[seat]
            
            # Select underlying route (v17 actions baseline)
            actions = submission._REBALANCE_ACTIONS if submission._regime(cfg_env) == "rebalance" else submission._LEGACY_ACTIONS
            s = min(max(0, step), len(actions) - 1)
            
            # 1. Base route action with weed repair & livestock conversion
            action = submission._weed_repair_action(obs, submission._copy_action(actions[s]), actions, s)
            action = submission._v16_convert_livestock(action, obs, s)
            action = submission._v16_wool_controller(action, obs, s)
            
            # 2. Boatlee 5-turn fertilizer relay
            if self.enable_boatlee_relay:
                action = submission._rc3_market_relay(obs, action, s, cfg_env)
                
            market = [list(ord) for ord in (action.get("market") or [])]
            private = submission._get(obs, "private", {}) or {}
            shed = dict(submission._get(private, "shed", {}) or {})
            
            # 3. Preemptive Early Dumps (THUNDER / HealthStone Counter)
            if s == self.melon_preempt_step and not st["melon_preempted"]:
                avail_melon = int(shed.get("MELON", 0) or 0)
                qty = min(self.melon_preempt_qty, avail_melon)
                if qty > 0 and len(market) < 10:
                    market.insert(0, ["SELL", "MELON", qty])
                    st["melon_preempted"] = True

            # 4. WOOL Intercept (Preempt THUNDER step 664 & 667 dumps)
            if s == self.wool_intercept_step and st["wool_intercepted"] == 0:
                avail_wool = int(shed.get("WOOL", 0) or 0)
                qty = min(self.wool_intercept_qty, avail_wool)
                if qty > 0 and len(market) < 10:
                    market.insert(0, ["SELL", "WOOL", qty])
                    st["wool_intercepted"] = qty
                    
            # Repay WOOL at step 672
            if s == 672 and st["wool_intercepted"] > 0 and not st["wool_repaid"]:
                repay = st["wool_intercepted"]
                new_m = []
                for ord in market:
                    if len(ord) >= 3 and ord[0] == "SELL" and ord[1] == "WOOL" and repay > 0:
                        cur = int(ord[2])
                        red = min(cur, repay)
                        cur -= red
                        repay -= red
                        if cur > 0:
                            new_m.append([ord[0], ord[1], cur])
                    else:
                        new_m.append(ord)
                market = new_m
                st["wool_repaid"] = True

            # 5. MILK Intercept at step 666
            if s == self.milk_intercept_step and st["milk_intercepted"] == 0:
                avail_milk = int(shed.get("MILK", 0) or 0)
                qty = min(self.milk_intercept_qty, avail_milk)
                if qty > 0 and len(market) < 10:
                    market.insert(0, ["SELL", "MILK", qty])
                    st["milk_intercepted"] = qty
                    
            # Repay MILK at step 672
            if s == 672 and st["milk_intercepted"] > 0 and not st["milk_repaid"]:
                repay = st["milk_intercepted"]
                new_m = []
                for ord in market:
                    if len(ord) >= 3 and ord[0] == "SELL" and ord[1] == "MILK" and repay > 0:
                        cur = int(ord[2])
                        red = min(cur, repay)
                        cur -= red
                        repay -= red
                        if cur > 0:
                            new_m.append([ord[0], ord[1], cur])
                    else:
                        new_m.append(ord)
                market = new_m
                st["milk_repaid"] = True
                
            # 6. Dead-Inventory Recovery Selling (steps recovery_start to 716)
            if self.enable_recovery and self.recovery_start <= s <= 716:
                mkt_info = submission._get(obs, "market", {}) or {}
                prices = submission._get(mkt_info, "prices", {}) or {}
                for item in ("STRAWBERRY", "MILK", "WOOL", "CARROT", "WHEAT"):
                    gate = self.recovery_gates.get(item, 0)
                    cur_px = int(submission._get(prices, item, 0) or 0)
                    if cur_px >= gate:
                        avail = int(shed.get(item, 0) or 0)
                        future_planned = 0
                        for fut_s in range(s, len(actions)):
                            for raw in (actions[fut_s].get("market") or []):
                                if len(raw) >= 3 and raw[0] == "SELL" and raw[1] == item:
                                    future_planned += int(raw[2])
                        dead = max(0, avail - future_planned)
                        if dead > 0 and len(market) < 10:
                            sell_qty = min(12, dead)
                            market.insert(0, ["SELL", item, sell_qty])
                            
            # 7. Capselllate (step >= 456)
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
            action = submission._rank_sell_slots(obs, action, cfg_env)
            return submission._align_hands(action, obs)
        except Exception as e:
            farm = submission._farm(obs, submission._seat(obs))
            return {
                "farmer": ["PASS"],
                "hands": [["PASS"] for _ in (submission._get(farm, "hands", []) or [])],
                "market": [],
            }

def agent(obs, configuration=None):
    if not hasattr(agent, "_impl"):
        agent._impl = V18ApexAgent()
    return agent._impl(obs, configuration)
