import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
scene = bpy.context.scene; O = bpy.data.objects
dg = bpy.context.evaluated_depsgraph_get()

# 1) lamp on the desk top, head reaching over the desk, not into the sign
lamp = O["Lamp"]; lamp.location = (-0.5, 0.05, 0.788); lamp.rotation_euler = (0, 0, math.radians(-150))
O["LampSpot"].location = (-0.3, 0.15, 1.45)
O["NeonSign"].location.z = 1.88

# 2) shelf boards by ray casting, then seat crate and chest on them
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
shelf = O["Shelves"]
def boards(x, y):
    zs = []; z = 3.0
    while z > 0.02:
        hit, loc, nrm, idx, ob, mw = scene.ray_cast(dg, Vector((x, y, z)), Vector((0, 0, -1)))
        if not hit: break
        if nrm.z > 0.7 and (ob.name.startswith("steel_frame") or (ob.parent and ob.parent.name == "Shelves")): zs.append(round(loc.z, 3))
        z = loc.z - 0.01
    return zs
sx, sy = shelf.location.x, shelf.location.y
lv = boards(sx, sy); print("shelf boards", lv)
def seat(objs_root, x, y, level_z):
    # move so the lowest point of the object's meshes sits on level_z
    meshes = [o for o in [objs_root] + list(objs_root.children_recursive) if o.type == 'MESH' and not o.hide_render]
    bpy.context.view_layer.update()
    mn = min((o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box)
    objs_root.location.x = x; objs_root.location.y = y
    objs_root.location.z += level_z - mn
crate = O["plastic_crate_01"]; chest = O["Chest"]
lv_sorted = sorted(lv)
seat(crate, sx - 0.25, sy, lv_sorted[1] if len(lv_sorted) > 1 else lv_sorted[0])
seat(chest, sx + 0.18, sy, lv_sorted[2] if len(lv_sorted) > 2 else lv_sorted[-1])

# 3) Panther a bit further from camera, beside the desk
O["Panther"].location = (1.55, 0.02, 0.1825)

# 4) camera: back off along the view line until key objects fit with margin
cam = O["BannerCam"]; tgt = O["CamTarget"]
keys = ["Shelves", "Desk", "Lamp", "NeonSign", "PLC_Cabinet", "Cart", "PLCStand", "Panther", "PandaBase"]
def corners(name):
    r = O[name]
    ms = [o for o in [r] + list(r.children_recursive) if o.type in ('MESH', 'CURVE') and not o.hide_render]
    return [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
pts = [p for k in keys for p in corners(k)]
d = (cam.location - tgt.location).normalized()
def fits(m=0.025):
    bpy.context.view_layer.update()
    for p in pts:
        v = world_to_camera_view(scene, cam, p)
        if not (m <= v.x <= 1 - m and m <= v.y <= 1 - m): return False
    return True
cam.data.shift_x = 0.0; cam.data.shift_y = 0.0
# centre the target on the bbox of key objects
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
c = (mn + mx) / 2
tgt.location = Vector((c.x, 0.35, c.z))
cam.location = tgt.location + d * 3.0
step = 0.05
while not fits() and (cam.location - tgt.location).length < 14:
    cam.location += d * step
print("cam", tuple(round(v, 2) for v in cam.location), "tgt", tuple(round(v, 2) for v in tgt.location), "dist", round((cam.location - tgt.location).length, 2))
bpy.ops.wm.save_mainfile()
import bpy
from mathutils import Vector
O = bpy.data.objects; scene = bpy.context.scene
for o in O:
    if o.name.startswith("metal_tool_chest"):
        for m in list(o.modifiers):
            if m.type == 'ARMATURE': o.modifiers.remove(m)
O["rig_metal_tool_chest"].hide_render = O["rig_metal_tool_chest"].hide_viewport = True
def seat(root, x, y, level_z):
    meshes = [o for o in [root] + list(root.children_recursive) if o.type == 'MESH' and not o.hide_render]
    bpy.context.view_layer.update()
    mn = min((o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box)
    root.location.x = x; root.location.y = y; root.location.z += level_z - mn
sh = O["Shelves"]; sx, sy = sh.location.x, sh.location.y
seat(O["Chest"], sx - 0.95, sy - 0.15, 0.0)
crate = O["plastic_crate_01"]
seat(crate, sx - 0.25, sy, 0.639)
c2 = O.get("plastic_crate_02b") or crate.copy(); c2.name = "plastic_crate_02b"
if c2.name not in scene.collection.objects: scene.collection.objects.link(c2)
c2["built"] = True; c2.location = crate.location.copy(); c2.location.x = sx + 0.22; c2.location.z = crate.location.z + (1.145 - 0.639)
c3 = O.get("plastic_crate_03b") or crate.copy(); c3.name = "plastic_crate_03b"
if c3.name not in scene.collection.objects: scene.collection.objects.link(c3)
c3["built"] = True; c3.location = crate.location.copy(); c3.location.x = sx - 0.05; c3.location.z = crate.location.z - (0.639 - 0.133)
bpy.context.view_layer.update()
for nm in ("Chest", "plastic_crate_01", "plastic_crate_02b", "plastic_crate_03b"):
    r = O[nm]; ms = [o for o in [r] + list(r.children_recursive) if o.type == 'MESH' and not o.hide_render]
    print(nm, "bottom", round(min((o.matrix_world @ Vector(c)).z for o in ms for c in o.bound_box), 3), "top", round(max((o.matrix_world @ Vector(c)).z for o in ms for c in o.bound_box), 3))
bpy.ops.wm.save_mainfile()
import bpy, math, itertools
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O = bpy.data.objects; scene = bpy.context.scene
for nm, st in (("NeonTeal", 9.0), ("NeonAmber", 8.0)):
    bpy.data.materials[nm].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = st
bpy.data.lights["NeonWash"].energy = 35
def box(name):
    r = O[name]; ms = [o for o in [r] + list(r.children_recursive) if o.type in ('MESH','CURVE') and not o.hide_render]
    pts = [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]), pts
def overlap(a, b, pad=0.06):
    return all(a[0][i] - pad < b[1][i] and b[0][i] - pad < a[1][i] for i in range(2))
O["Cart"].location = (3.2, -0.05, 0); O["Cart"].rotation_euler = (0, 0, math.radians(-18))
pan = O["Panther"]; others = ["Desk", "Cart", "Shelves", "Chest", "PLC_Cabinet", "Lamp"]
best = None
for x, y, yaw in itertools.product([1.82, 1.86, 1.9, 1.94, 1.98], [-0.45, -0.35, -0.25, -0.15, -0.05], [-90, -75, -105, 90]):
    pan.location = (x, y, 0.1825); pan.rotation_euler = (0, 0, math.radians(yaw)); bpy.context.view_layer.update()
    pb = box("Panther")
    if any(overlap(pb, box(o)) for o in others): continue
    s = abs(y + 0.3) + 0.2 * abs(yaw + 90) / 15
    if best is None or s < best[0]: best = (s, x, y, yaw)
print("panther spot", best)
_, x, y, yaw = best
pan.location = (x, y, 0.1825); pan.rotation_euler = (0, 0, math.radians(yaw))
# re-fit camera to every key object
cam = O["BannerCam"]; tgt = O["CamTarget"]
keys = ["Shelves", "Chest", "Desk", "Lamp", "NeonSign", "PLC_Cabinet", "Cart", "PLCStand", "Panther", "PandaBase"]
bpy.context.view_layer.update()
pts = [p for k in keys for p in box(k)[2]]
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
c = (mn + mx) / 2
d = (cam.location - tgt.location).normalized()
tgt.location = Vector((c.x, 0.35, c.z)); cam.location = tgt.location + d * 3.0
def fits(m=0.02):
    bpy.context.view_layer.update()
    return all(m <= v.x <= 1 - m and m <= v.y <= 1 - m for v in (world_to_camera_view(scene, cam, p) for p in pts))
while not fits() and (cam.location - tgt.location).length < 14: cam.location += d * 0.04
print("cam dist", round((cam.location - tgt.location).length, 2))
for o in others:
    print(o, "overlaps rover:", overlap(box("Panther"), box(o), pad=0.0))
scene.render.resolution_x, scene.render.resolution_y = 1920, 600
bpy.ops.wm.save_mainfile()
