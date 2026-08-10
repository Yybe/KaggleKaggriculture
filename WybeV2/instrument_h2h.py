import importlib.util, sys

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.agent

V16 = load_agent(r'C:\Users\xxshi\Desktop\farmmasterV2\submission.py', 'v16mod')
V14 = load_agent(r'C:\Users\xxshi\Desktop\FARMMASTER\VersionWybe\v14_source.py', 'v14mod')

from kaggle_environments import make
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000000}, debug=False)
env.run([V16, V14])

print("V16 vs V14:", env.state[0].reward, "vs", env.state[1].reward)
for i, (s0, s1) in enumerate(env.steps):
    obs = s0['observation']
    if i in (0, 240, 480, 600, 696, 719):
        print(f"S{i}: prices={dict((obs.get('market') or {}).get('prices', {}))}")
