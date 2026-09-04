def _shield_tile_at(farm, pos):
    if not pos or len(pos) < 2:
        return None
    x, y = int(pos[0]), int(pos[1])
    tiles = _get(farm, "tiles", []) or []
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        return tiles[y][x]
    return None


def _shield_weed(action, observation, seat, state, step):
    # Weed auto-dig: unit about to PLANT/BUILD on a weeded tile digs first,
    # intended op replays next step (avioon shield 1).
    farms = _get(observation, "farms", []) or []
    farm = farms[seat] if seat < len(farms) else {}
    unit_actions = [
        list(action.get("farmer", ["PASS"]) or ["PASS"]),
        *[list(h or ["PASS"]) for h in (action.get("hands") or [])],
    ]
    positions = [_get(farm, "farmer", None), *list(_get(farm, "hands", []) or [])]
    game = state.setdefault("weed", {})
    if step == 0:
        game.clear()
    active = game.setdefault("active", {})
    for actor, trans in list(active.items()):
        idx = 0 if actor == "farmer" else int(actor) + 1
        if idx < len(unit_actions) and step - trans.get("start", -1) == 1:
            unit_actions[idx] = list(trans.get("intended", ["PASS"]))
        else:
            active.pop(actor, None)
    for idx, (pos, intended) in enumerate(zip(positions, unit_actions)):
        actor = "farmer" if idx == 0 else idx - 1
        if actor in active or not isinstance(intended, list) or not intended:
            continue
        if intended[0] in ("PLANT", "BUILD_PASTURE", "BUILD_COOP"):
            tile = _shield_tile_at(farm, pos)
            if tile is not None and _get(tile, "kind") == "WEED":
                active[actor] = {"start": step, "intended": list(intended)}
                unit_actions[idx] = ["DIG"]
    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    return action


def _shield_market(action, observation, seat, step):
    # Market shield stack (avioon 2A-2H): fert monetization, early-cash
    # buffer, sunset overflow guard, shop-synced drip sells, predator
    # ambush, end-game front-run ladder.
    try:
        market = list(action.get("market") or [])
        if len(market) >= 10:
            return action
        private = _get(observation, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        prices = _prices(observation)
        farms = _get(observation, "farms", []) or []
        farm = farms[seat] if seat < len(farms) else {}
        my_money = float(_get(farm, "money", 0) or 0)
        fert = int(shed.get("FERTILIZER", 0) or 0)
        wheat = int(shed.get("WHEAT", 0) or 0)
        fert_price = float(_get(prices, "FERTILIZER", 0) or 0)
        wool = int(shed.get("WOOL", 0) or 0)
        milk = int(shed.get("MILK", 0) or 0)
        strawberry = int(shed.get("STRAWBERRY", 0) or 0)
        melon = int(shed.get("MELON", 0) or 0)
        carrot = int(shed.get("CARROT", 0) or 0)

        def _has(item_op):
            return any(isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == item_op
                       for o in market)

        # 2A protected fertilizer monetization
        if step < 718 and fert_price >= 18.0 and len(market) < 10 and not _has("FERTILIZER"):
            if step < 350 or step >= 524:
                if fert >= 3:
                    market.append(["SELL", "FERTILIZER", min(fert, 2)])
            elif fert >= 20:
                market.append(["SELL", "FERTILIZER", min(fert - 16, 2)])
        # 2B early cash emergency buffer
        if step <= 300 and my_money < 180.0 and len(market) < 10:
            if fert >= 4 and not _has("FERTILIZER"):
                market.append(["SELL", "FERTILIZER", 2])
            elif wheat > 18 and not _has("WHEAT"):
                market.append(["SELL", "WHEAT", min(wheat - 18, 2)])
        # 2C sunset shed overflow shield
        if step % 24 == 22 and len(market) < 10:
            shed_total = sum(int(shed.get(p, 0) or 0) for p in
                             ("FERTILIZER", "WHEAT", "MILK", "WOOL", "STRAWBERRY",
                              "MELON", "TOMATO", "EGG", "CARROT"))
            if shed_total >= 65:
                excess = min(shed_total - 65, 8)
                if fert >= 4 and not _has("FERTILIZER"):
                    market.append(["SELL", "FERTILIZER", min(fert, excess)])
                elif wheat > 18 and not _has("WHEAT"):
                    market.append(["SELL", "WHEAT", min(wheat - 18, excess)])
        # 2D shop-synced high-margin monetization
        town = _get(observation, "town", {}) or {}
        shops = [str(s) for s in (_get(town, "unlocked_shops", []) or [])]
        has_yarn = any("YARN" in s for s in shops)
        has_dairy = any(("SMOOTHIE" in s or "PIZZA" in s or "ICE_CREAM" in s) for s in shops)
        has_berry = any(("SMOOTHIE" in s or "BRUNCH" in s or "ICE_CREAM" in s or "FARMERS" in s) for s in shops)
        has_pet = any("PET_CAFE" in s for s in shops)
        wool_price = float(_get(prices, "WOOL", 0) or 0)
        milk_price = float(_get(prices, "MILK", 0) or 0)
        straw_price = float(_get(prices, "STRAWBERRY", 0) or 0)
        carrot_price = float(_get(prices, "CARROT", 0) or 0)
        if has_yarn and step % 4 == 1 and wool >= 2 and wool_price >= 180.0 and len(market) < 10 and not _has("WOOL"):
            market.append(["SELL", "WOOL", min(wool, 4)])
        if has_dairy and step >= 250 and milk >= 4 and milk_price >= 85.0 and len(market) < 10 and not _has("MILK"):
            market.append(["SELL", "MILK", min(milk, 4)])
        if has_berry and step % 4 == 1 and strawberry >= 3 and straw_price >= 120.0 and len(market) < 10 and not _has("STRAWBERRY"):
            market.append(["SELL", "STRAWBERRY", min(strawberry, 4)])
        if has_pet and step % 4 == 1 and carrot >= 2 and carrot_price >= 35.0 and len(market) < 10 and not _has("CARROT"):
            market.append(["SELL", "CARROT", min(carrot, 2)])
        # 2E predator market ambush
        opp_farm = farms[1 - seat] if len(farms) > (1 - seat) else {}
        opp_tiles = _get(opp_farm, "tiles", []) or []
        day = int(_get(observation, "day", 0) or 0)
        opp_straw = 0
        opp_melon = 0
        for row in opp_tiles:
            for t in (row if isinstance(row, list) else []):
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    p_day = int(t.get("planted_day", 0) or 0)
                    if t.get("crop") == "STRAWBERRY" and (day - p_day) >= 8:
                        opp_straw += 1
                    elif t.get("crop") == "MELON" and (day - p_day) >= 9:
                        opp_melon += 1
        if opp_straw >= 4 and strawberry >= 2 and straw_price >= 110.0 and len(market) < 10 and not _has("STRAWBERRY"):
            market.append(["SELL", "STRAWBERRY", min(strawberry, 4)])
        melon_price = float(_get(prices, "MELON", 0) or 0)
        if opp_melon >= 2 and melon >= 2 and melon_price >= 120.0 and len(market) < 10 and not _has("MELON"):
            market.append(["SELL", "MELON", 2])
        # 2F/2G/2H end-game front-run ladder
        if step == 716:
            for item in ("STRAWBERRY", "MELON"):
                count = int(shed.get(item, 0) or 0)
                if count >= 2 and len(market) < 10 and not _has(item):
                    market.append(["SELL", item, 2])
        if step == 717:
            for item in ("STRAWBERRY", "MELON", "EGG", "CARROT", "TOMATO"):
                count = int(shed.get(item, 0) or 0)
                if count > 0 and len(market) < 10 and not _has(item):
                    market.append(["SELL", item, count])
        if step == 718:
            for item in ("MILK", "WOOL", "STRAWBERRY", "MELON", "TOMATO", "EGG", "CARROT", "FERTILIZER", "WHEAT"):
                count = int(shed.get(item, 0) or 0)
                if count > 0 and len(market) < 10 and not _has(item):
                    market.append(["SELL", item, count])
        if step == 719:
            for item in ("FERTILIZER", "WHEAT", "MILK", "WOOL", "STRAWBERRY", "MELON", "TOMATO", "EGG", "CARROT"):
                count = int(shed.get(item, 0) or 0)
                if count > 0 and len(market) < 10 and not _has(item):
                    market.append(["SELL", item, count])
        action["market"] = market[:10]
    except Exception:
        pass
    return action
