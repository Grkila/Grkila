import bpy
exec(open(os.path.join(os.environ["BANNER_DIR"], "01_build.py"), encoding="utf-8").read().split("# ---------- room ----------")[0].split("# ---------- clean slate")[0])
src = open(os.path.join(os.environ["BANNER_DIR"], "01_build.py"), encoding="utf-8").read()
ns = {}
exec(src[src.index("def proc_mat"):src.index("def img_mat")], globals())
RED = proc_mat("PantherRed", (0.55, 0.04, 0.03), rough=0.4, noise=40, bump=0.04)
BLK = bpy.data.materials["PantherBody"]; SIL = bpy.data.materials["Hub"]; TIRE = bpy.data.materials["Tire"]
for o in bpy.data.objects["Panther"].children_recursive:
    if o.type != 'MESH': continue
    n = o.name.lower(); wheel = any(p.name.startswith("Wheel_") for p in [o.parent, o.parent.parent if o.parent else None] if p)
    for s in o.material_slots:
        if "red" in n: s.material = RED
        elif "silver" in n: s.material = SIL
        else: s.material = TIRE if wheel else BLK
for o in bpy.data.objects:
    if o.name.startswith("cur_") or o.name.startswith("geo_top_wire") or o.name.startswith("geo_middle_wire"):
        o.hide_render = o.hide_viewport = True
for nm, st in (("NeonTeal", 9.0), ("NeonAmber", 8.0)):
    bpy.data.materials[nm].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = st
for m in bpy.data.materials: m.use_fake_user = True
bpy.ops.wm.save_mainfile()
print("fix1 ok", sorted({s.material.name for o in bpy.data.objects["Panther"].children_recursive if o.type=='MESH' for s in o.material_slots}))
import bpy, math
from mathutils import Vector
O = bpy.data.objects
O["Panther"].location = (1.62, -0.55, 0.1825); O["Panther"].rotation_euler = (0, 0, math.radians(200))
O["PLC_Cabinet"].location = (1.95, 1.27, 1.25)
O["Cart"].location = (3.05, 0.55, 0)
O["CabGlow"].location = (1.95, 0.7, 1.25)
bpy.data.lights["NeonWash"].energy = 30
bpy.ops.wm.save_mainfile()
print("moved")
import bpy
bpy.data.objects["NeonSign"].location.z = 1.62
bpy.ops.wm.save_mainfile(); print("ok2")
import bpy, math
O = bpy.data.objects
O["Lamp"].location = (-0.82, 0.05, 0.788); O["Lamp"].rotation_euler = (0, 0, math.radians(95))
O["LampSpot"].location = (-0.6, 0.05, 1.3)
O["Panther"].location = (1.5, -0.15, 0.1825)
bpy.ops.wm.save_mainfile(); print("ok3")
import bpy, math
from mathutils import Vector
O = bpy.data.objects
cart, stand = O["Cart"], O["PLCStand"]
if stand.parent != cart:
    mw = stand.matrix_world.copy(); stand.parent = cart; stand.matrix_world = mw
cart.location = (2.62, -0.25, 0); cart.rotation_euler = (0, 0, math.radians(-24))
bpy.context.view_layer.update()
board = O["PLCBoard"]
l = bpy.data.lights.get("StandSpot") or bpy.data.lights.new("StandSpot", 'SPOT')
l.energy = 70; l.color = (1.0, 0.92, 0.82); l.spot_size = math.radians(45); l.spot_blend = 0.5; l.shadow_soft_size = 0.15
so = O.get("StandSpot") or bpy.data.objects.new("StandSpot", l)
if so.name not in bpy.context.scene.collection.objects: bpy.context.scene.collection.objects.link(so)
so["built"] = True
tgt = board.matrix_world @ Vector((0, 0, 0.35))
so.location = tgt + Vector((-0.5, -1.1, 0.9))
so.rotation_euler = (tgt - so.location).to_track_quat('-Z', 'Y').to_euler()
bpy.data.lights["CabGlow"].energy = 4
bpy.ops.wm.save_mainfile(); print("stand2 ok", tuple(round(v,2) for v in tgt))
import bpy, os
src = open(os.path.join(os.environ["BANNER_DIR"], "build.py"), encoding="utf-8").read()
exec(src[src.index("def tex_mat"):src.index("def proc_mat")], globals())
m = tex_mat("painted_metal_shutter", "StandPanel", scale=2.5, tint=(0.78, 0.8, 0.83), rough=0.55, metal=0.0)
o = bpy.data.objects["BoardPlate"]; o.data.materials.clear(); o.data.materials.append(m)
bpy.data.lights["StandSpot"].energy = 140
bpy.ops.wm.save_mainfile(); print("stand3 ok")
