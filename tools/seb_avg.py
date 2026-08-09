import json

with open(r'c:\Users\xxshi\Desktop\farmmasterV2\seb_analysis\seb_data.json','r') as f:
    d = json.load(f)

games = d['games']
N = len(games)
agg = d['aggregated']
print(f'=== SEB AVERAGES (N={N}) ===')

for crop in ['MELON','WHEAT','STRAWBERRY']:
    avg = sum(g['seeds_bought'].get(crop, 0) for g in games) / N
    print(f'Avg seeds/game {crop}: {avg:.1f}')

for a in ['COW','SHEEP']:
    avg = sum(g['animals_bought'].get(a, 0) for g in games) / N
    print(f'Avg animals/game {a}: {avg:.1f}')

for p in ['FERTILIZER','WHEAT','WOOL','MILK','MELON','STRAWBERRY']:
    avg = sum(g['sold'].get(p, 0) for g in games) / N
    print(f'Avg sold/game {p}: {avg:.1f}')

avg_wheat_buy = sum(g['bought'].get('WHEAT', 0) for g in games) / N
print(f'Avg WHEAT BUY_PRODUCT/game: {avg_wheat_buy:.1f}')

hire_total = agg['market_orders']['HIRE']
print(f'Avg HIRE/game: {hire_total / N:.1f}')

u = agg['quadrant_unlock_times']
ne = u[0::3]
sw = u[1::3]
se = u[2::3]
print(f'NE unlock: step {sum(ne)/len(ne):.0f} (day {sum(ne)/len(ne)/24:.1f})')
print(f'SW unlock: step {sum(sw)/len(sw):.0f} (day {sum(sw)/len(sw)/24:.1f})')
print(f'SE unlock: step {sum(se)/len(se):.0f} (day {sum(se)/len(se)/24:.1f})')

banks = agg['final_banks']
margins = agg['margins']
print(f'Avg final bank: {sum(banks)/N:.0f}')
print(f'Avg margin: {sum(margins)/N:.0f}')
print(f'Win rate: {agg["wins"]}/{N} = {agg["wins"]/N*100:.0f}%')
