from kaggle_environments import make
import agents_lib

results = []
for g in range(8):
    env = make('kaggriculture', debug=False)
    env.run([agents_lib.baseline_v7, agents_lib.baseline])
    b = env.steps[-1][0]['observation']['farms']
    results.append((round(b[0]['money']), round(b[1]['money'])))

print("game  v7  v6")
for i, (a, c) in enumerate(results):
    print(f"{i:4d}  {a:5.0f} {c:5.0f}")
