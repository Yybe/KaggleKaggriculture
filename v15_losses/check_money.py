import json

with open(r'C:\Users\xxshi\Desktop\farmmasterV2\v15_losses\91071101_tetsu2131_replay.json', encoding='utf-8') as f:
    d = json.load(f)
steps = d['steps']

for i in (0, 1, 100, 456, 480, 600, 718, 719):
    st = steps[i]
    for s in (0, 1):
        obs = st[s].get('observation') or {}
        farms = obs.get('farms') or []
        money = farms[0].get('money') if farms else None
        print(f'step {i} p{s}: farms[0].money={money}')
print('rewards:', d['rewards'])
print('step 718 reward fields:', steps[718][0].get('reward'), steps[718][1].get('reward'))
print('step 719 reward fields:', steps[719][0].get('reward'), steps[719][1].get('reward'))
print('statuses:', d.get('statuses'))
