import sys, os, numpy as np, trimesh
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
Y_UP = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]], float)  # z-up -> y-up for glTF
for root, _, files in os.walk(src):
    for f in files:
        if not f.endswith('.dae'): continue
        sc = trimesh.load(os.path.join(root, f), force='scene')
        b = sc.bounds
        sc.apply_transform(Y_UP)
        out = os.path.join(dst, os.path.relpath(root, src), f.replace('.dae', '.glb'))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sc.export(out)
        print(os.path.relpath(out, dst), 'z-up bounds', np.round(b, 3).tolist(), len(sc.geometry), 'geoms')
