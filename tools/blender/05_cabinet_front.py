import os
import bpy, math
from mathutils import Vector
src = open(os.path.join(os.environ["BANNER_DIR"], "01_build.py"), encoding="utf-8").read()
scene = bpy.context.scene
exec(src[src.index("def tag(o)"):src.index("# ---------- room ----------")], globals())
O = bpy.data.objects
for o in list(O):
    if o.get("cabfront"): bpy.data.objects.remove(o, do_unlink=True)
O["Panther"].location = (1.5, -0.3, 0.1825)
lamp = O["Lamp"]; lamp.location = (-0.62, 0.42, 0.788); lamp.rotation_euler = (0, 0, math.radians(150))
O["LampSpot"].location = (-0.5, 0.3, 1.4)
hinge = O["CabDoorHinge"]; hinge.rotation_euler = (0, 0, 0)
door = O["CabDoor"]
def front(o):
    o["cabfront"] = True; o.parent = door
    return o
# door-local frame: door box centred at its own origin, front face at y = -0.0125
F = -0.013
M_SCREEN = bpy.data.materials["ScreenHMI"]
M_BEZEL = bpy.data.materials["Bezel"]
front(box("HMIFrame", (0.36, 0.02, 0.24), (0.0, F - 0.01, 0.22), M_BEZEL, bevel=0.006))
bpy.ops.mesh.primitive_plane_add(size=1)
s = bpy.context.active_object; s.name = "HMIScreen"; tag(s)
s.scale = (0.32, 0.2, 1); s.rotation_euler = (math.pi / 2, 0, 0); s.location = (0.0, F - 0.0205, 0.225)
s.data.materials.append(M_SCREEN); front(s)
M_YEL = proc_mat("SafetyYellow", (0.95, 0.72, 0.05), rough=0.45, noise=60, bump=0.03)
M_RED = proc_mat("SafetyRed", (0.7, 0.03, 0.02), rough=0.35, noise=60, bump=0.03)
front(box("EstopPlate", (0.09, 0.006, 0.09), (0.25, F - 0.003, -0.12), M_YEL, bevel=0.004))
front(cyl("EstopBase", 0.022, 0.02, (0.25, F - 0.015, -0.12), M_BEZEL, rot=(math.pi / 2, 0, 0)))
front(cyl("EstopHead", 0.032, 0.018, (0.25, F - 0.032, -0.12), M_RED, rot=(math.pi / 2, 0, 0)))
front(box("SwitchPlate", (0.1, 0.006, 0.1), (-0.25, F - 0.003, -0.12), M_YEL, bevel=0.004))
front(box("SwitchHandle", (0.085, 0.03, 0.02), (-0.25, F - 0.02, -0.12), M_RED, rot=(0, math.radians(35), 0), bevel=0.006))
for i, (nm, col) in enumerate([("PilotG", (0.15, 1.0, 0.35)), ("PilotA", (1.0, 0.6, 0.1)), ("PilotR", (1.0, 0.12, 0.08))]):
    m = proc_mat(nm, col, rough=0.15, emit=col, emit_strength=14.0 if i != 2 else 2.0)
    front(cyl(nm + "Ring", 0.018, 0.012, (-0.08 + i * 0.08, F - 0.006, -0.12), bpy.data.materials["Steel"], rot=(math.pi / 2, 0, 0)))
    front(cyl(nm, 0.013, 0.012, (-0.08 + i * 0.08, F - 0.014, -0.12), m, rot=(math.pi / 2, 0, 0)))
M_LABEL = proc_mat("LabelWhite", (0.85, 0.86, 0.87), rough=0.5, noise=80, bump=0.02)
front(box("NamePlate", (0.2, 0.004, 0.035), (0.0, F - 0.002, 0.42), M_LABEL, bevel=0.002))
bpy.data.lights["CabGlow"].energy = 6
for m in bpy.data.materials: m.use_fake_user = True
bpy.ops.wm.save_mainfile()
print("cabfront ok")
