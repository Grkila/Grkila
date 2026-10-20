# Airlock HIL card scene: a rover passes through a three-zone airlock with two gates.
# blender -b --factory-startup --python airlock.py -- <out_dir> [test]
import bpy, math, os, sys
from mathutils import Vector

SC = os.environ["BANNER_DIR"]
PH = os.path.join(SC, "dl-polyhaven")
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT, TEST = ARGS[0], len(ARGS) > 1
scene = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
FPS, SECS = 12, 12
scene.render.fps = FPS; scene.frame_start, scene.frame_end = 1, FPS * SECS

# ---------- world ----------
w = bpy.data.worlds.new("Quarry"); scene.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]
env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(PH, "drackenstein_quarry_2k.hdr"))
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord')
nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
mp.inputs['Rotation'].default_value[2] = math.radians(120)
nt.links.new(env.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 0.9

# ---------- materials ----------
def pbr(name, folder, scale, tint=None, metal=0.0, rough_mul=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; t = m.node_tree; b = t.nodes["Principled BSDF"]
    tc = t.nodes.new('ShaderNodeTexCoord'); mp = t.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3
    t.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    def tex(fn, non_color=False):
        n = t.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(PH, folder, fn))
        n.projection = 'BOX'; n.projection_blend = 0.3
        if non_color: n.image.colorspace_settings.name = 'Non-Color'
        t.links.new(mp.outputs['Vector'], n.inputs['Vector']); return n
    d = tex(f"{folder}_diff.jpg")
    if tint:
        mx = t.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
        mx.inputs['B'].default_value = (*tint, 1); t.links.new(d.outputs['Color'], mx.inputs['A']); t.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    else:
        t.links.new(d.outputs['Color'], b.inputs['Base Color'])
    r = tex(f"{folder}_rough.jpg", True); rm = t.nodes.new('ShaderNodeMath'); rm.operation = 'MULTIPLY'; rm.inputs[1].default_value = rough_mul
    t.links.new(r.outputs['Color'], rm.inputs[0]); t.links.new(rm.outputs['Value'], b.inputs['Roughness'])
    n = tex(f"{folder}_nor.jpg", True); nm = t.nodes.new('ShaderNodeNormalMap'); t.links.new(n.outputs['Color'], nm.inputs['Color'])
    t.links.new(nm.outputs['Normal'], b.inputs['Normal']); b.inputs['Metallic'].default_value = metal
    return m

def flat(name, color, rough=0.45, metal=0.0, emit=None, strength=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; t = m.node_tree; b = t.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = strength
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        if hasattr(m, "surface_render_method"): m.surface_render_method = 'BLENDED'
    tc = t.nodes.new('ShaderNodeTexCoord'); nz = t.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 80
    bp = t.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.05
    t.links.new(tc.outputs['Object'], nz.inputs['Vector']); t.links.new(nz.outputs['Fac'], bp.inputs['Height']); t.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m

M_SAND = pbr("Regolith", "aerial_sand", 0.6, tint=(1.0, 0.62, 0.42))
M_SHEET = pbr("Sheet", "box_profile_metal_sheet", 1.6, tint=(0.82, 0.84, 0.88), metal=0.6, rough_mul=0.8)
M_ALU = flat("Alu", (0.78, 0.8, 0.83), rough=0.3, metal=1.0)
M_DARK = flat("Dark", (0.05, 0.055, 0.06), rough=0.5)
M_PC = flat("Polycarbonate", (0.75, 0.88, 1.0), rough=0.05, alpha=0.18)
haz = bpy.data.materials.new("Hazard"); haz.use_nodes = True
hb = haz.node_tree.nodes["Principled BSDF"]; hi = haz.node_tree.nodes.new('ShaderNodeTexImage')
hi.image = bpy.data.images.load(os.path.join(SC, "hazard.png")); haz.node_tree.links.new(hi.outputs['Color'], hb.inputs['Base Color'])
hb.inputs['Roughness'].default_value = 0.45

def box(name, size, loc, m, parent=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.active_object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True); o.location = loc; o.parent = parent
    if bevel: md = o.modifiers.new("b", 'BEVEL'); md.width = bevel; md.segments = 3
    o.data.materials.append(m); return o

def cyl(name, r, h, loc, m, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=24); o = bpy.context.active_object
    o.name = name; o.location = loc; o.rotation_euler = rot; o.parent = parent; o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o

def import_gltf(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]

# ---------- ground and rocks ----------
bpy.ops.mesh.primitive_plane_add(size=40); g = bpy.context.active_object; g.name = "Ground"; g.data.materials.append(M_SAND)
rocks = import_gltf(os.path.join(PH, "boulder_01", "boulder_01_1k.gltf"))
rock = next(o for o in rocks if o.type == 'MESH')
for i, (x, y, s, rz) in enumerate([(-2.6, 1.6, 0.35, 20), (2.9, 1.9, 0.5, 80), (3.4, -1.4, 0.22, 140), (-3.2, -1.8, 0.28, 200), (0.4, 2.6, 0.3, 300)]):
    r = rock if i == 0 else rock.copy()
    if i: scene.collection.objects.link(r)
    r.location = (x, y, 0); r.scale = (s, s, s); r.rotation_euler = (0, 0, math.radians(rz))
    for mm in r.data.materials:
        b = mm.node_tree.nodes.get("Principled BSDF")
        if b and not b.inputs['Base Color'].links: b.inputs['Base Color'].default_value = (0.7, 0.45, 0.32, 1)

# ---------- airlock: three zones along x ----------
L, Wd, Hh = 3.6, 1.3, 1.05
zones = [-1.2, 0.0, 1.2]; gates = [-0.6, 0.6]
for x in (-1.8, -0.6, 0.6, 1.8):
    for y in (-Wd / 2, Wd / 2):
        box(f"Post{x}{y}", (0.06, 0.06, Hh), (x, y, Hh / 2), M_ALU, bevel=0.004)
    box(f"Cross{x}", (0.06, Wd + 0.06, 0.06), (x, 0, Hh), M_ALU, bevel=0.004)
for y in (-Wd / 2, Wd / 2):
    box(f"Beam{y}", (L, 0.06, 0.06), (0, y, Hh), M_ALU, bevel=0.004)
    box(f"Sill{y}", (L, 0.08, 0.04), (0, y, 0.02), M_ALU)
box("WallBack", (L, 0.02, Hh - 0.08), (0, Wd / 2 + 0.01, Hh / 2), M_SHEET)        # corrugated back wall
gate_objs = []
for i, x in enumerate(gates):
    for y in (-Wd / 2 + 0.06, Wd / 2 - 0.06):
        box(f"Guide{i}{y}", (0.08, 0.04, Hh * 2), (x, y, Hh), M_DARK)
    gte = box(f"Gate{i}", (0.035, Wd - 0.16, Hh - 0.08), (x, 0, (Hh - 0.08) / 2 + 0.01), haz, bevel=0.005)
    gate_objs.append(gte)
    # status tower outside the clear wall
    box(f"TowerPost{i}", (0.03, 0.03, 1.15), (x + 0.12, Wd / 2 + 0.12, 0.58), M_DARK)
gate_led = []
for i, x in enumerate(gates):
    reds, greens = [], []
    r = cyl(f"TowerRed{i}", 0.045, 0.07, (x + 0.12, Wd / 2 + 0.12, 1.18), flat(f"TR{i}", (1, 0.1, 0.05), emit=(1, 0.08, 0.04), strength=0))
    a = cyl(f"TowerAmber{i}", 0.045, 0.07, (x + 0.12, Wd / 2 + 0.12, 1.26), flat(f"TA{i}", (1, 0.6, 0.1), emit=(1, 0.55, 0.05), strength=0))
    gg = cyl(f"TowerGreen{i}", 0.045, 0.07, (x + 0.12, Wd / 2 + 0.12, 1.34), flat(f"TG{i}", (0.1, 1, 0.3), emit=(0.1, 1, 0.3), strength=0))
    gate_led.append((r, a, gg))
# zone sensors: IR beam across each zone at wheel height, and a floor status strip
beams, strips = [], []
for k, x in enumerate(zones):
    for y in (-Wd / 2 + 0.03, Wd / 2 - 0.03):
        box(f"Sensor{k}{y}", (0.05, 0.04, 0.05), (x, y, 0.22), M_DARK)
    beams.append(cyl(f"Beam{k}", 0.004, Wd - 0.08, (x, 0, 0.22), flat(f"IR{k}", (1, 0.1, 0.1), emit=(1, 0.05, 0.05), strength=4), rot=(math.pi / 2, 0, 0)))
    strips.append(box(f"Strip{k}", (1.0, 0.03, 0.006), (x, Wd / 2 - 0.12, 0.003), flat(f"ST{k}", (0.5, 0.5, 0.5), emit=(0.1, 1, 0.35), strength=0)))

# controller box with Poly Haven circuit board (ESP32 HIL controller)
box("CtrlBox", (0.42, 0.18, 0.34), (2.25, -0.25, 0.62), flat("CtrlGrey", (0.62, 0.64, 0.66), rough=0.5), bevel=0.01)
box("CtrlStand", (0.05, 0.05, 0.45), (2.25, -0.25, 0.22), M_DARK)
board = import_gltf(os.path.join(PH, "circuit_board", "circuit_board_1k.gltf"))
broot = [o for o in board if o.parent is None][0]
broot.scale = (0.85, 0.85, 0.85); broot.rotation_euler = (math.radians(90), 0, 0)
broot.location = (2.25, -0.35, 0.62)
ctrl_led = cyl("CtrlLed", 0.008, 0.01, (2.4, -0.35, 0.74), flat("CL", (0.2, 0.5, 1), emit=(0.2, 0.55, 1), strength=0), rot=(math.pi / 2, 0, 0))

# ---------- rover (Husarion Panther from the banner meshes) ----------
GLB = os.path.join(SC, "glb", "panther")
rover = bpy.data.objects.new("Rover", None); scene.collection.objects.link(rover)
M_BODY = flat("PantherBody", (0.09, 0.095, 0.1), rough=0.5); M_RED = flat("PantherRed", (0.55, 0.04, 0.03), rough=0.4)
M_HUB = flat("Hub", (0.6, 0.62, 0.65), rough=0.3, metal=1.0); M_TIRE = flat("Tire", (0.02, 0.02, 0.02), rough=0.85)
def skin(objs, wheel):
    for o in objs:
        if o.type != 'MESH': continue
        n = o.name.lower()
        for s in o.material_slots:
            s.material = M_RED if "red" in n else M_HUB if "silver" in n else (M_TIRE if wheel else M_BODY)
        for p in o.data.polygons: p.use_smooth = True
base = import_gltf(os.path.join(GLB, "base.glb")); skin(base, False)
for o in base:
    if o.parent is None: o.parent = rover
wheels = []
for wn, (x, y) in {"fl": (0.22, 0.3485), "fr": (0.22, -0.3485), "rl": (-0.22, 0.3485), "rr": (-0.22, -0.3485)}.items():
    we = bpy.data.objects.new(f"W_{wn}", None); scene.collection.objects.link(we); we.parent = rover; we.location = (x, y, 0)
    ws = import_gltf(os.path.join(GLB, f"{wn}_wheel.glb")); skin(ws, True)
    for o in ws:
        if o.parent is None: o.parent = we
    wheels.append(we)

# ---------- lights and camera ----------
def area(name, loc, rot, energy, color, size):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.color = color; l.size = size
    o = bpy.data.objects.new(name, l); scene.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
sun = bpy.data.lights.new("Sun", 'SUN'); sun.energy = 3.2; sun.color = (1.0, 0.9, 0.78); sun.angle = math.radians(4)
so = bpy.data.objects.new("Sun", sun); scene.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
area("Fill", (0, -4, 2.5), (math.radians(65), 0, 0), 120, (0.7, 0.8, 1.0), 4)
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); scene.collection.objects.link(cam); scene.camera = cam
cam_d.lens = 36; cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 5.6; cam_d.dof.focus_distance = 5.1
cam.location = (-0.9, -4.9, 2.3)
tgt = bpy.data.objects.new("Tgt", None); scene.collection.objects.link(tgt); tgt.location = (0.3, 0, 0.62)
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

# ---------- timeline (seconds) ----------
ease = lambda t: t * t * (3 - 2 * t)
def seg(t, a, b, va, vb):
    if t <= a: return va
    if t >= b: return vb
    return va + (vb - va) * ease((t - a) / (b - a))
def rover_x(t):
    if t < 2.0: return seg(t, 0, 2.0, -3.6, -1.2)
    if t < 3.0: return -1.2
    if t < 5.0: return seg(t, 3.0, 5.0, -1.2, 0.0)
    if t < 7.0: return 0.0
    return seg(t, 7.0, 10.5, 0.0, 3.6)
def gate_open(i, t):
    if i == 0: return seg(t, 2.0, 3.0, 0, 1) if t < 5.0 else seg(t, 5.0, 6.0, 1, 0)
    return seg(t, 6.0, 7.0, 0, 1) if t < 9.0 else seg(t, 9.0, 10.0, 1, 0)

def em(o, v):
    o.data.materials[0].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = v
    o.data.materials[0].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].keyframe_insert("default_value", frame=f)

for f in range(1, FPS * SECS + 1):
    t = (f - 1) / FPS
    x = rover_x(t)
    rover.location = (x, 0, 0.1825); rover.keyframe_insert("location", frame=f)
    for we in wheels:
        we.rotation_euler = (0, (x + 3.6) / 0.1825, 0); we.keyframe_insert("rotation_euler", frame=f)
    for i, gte in enumerate(gate_objs):
        op = gate_open(i, t)
        gte.location.z = (Hh - 0.08) / 2 + 0.01 + op * (Hh - 0.06); gte.keyframe_insert("location", frame=f)
        r, a, gg = gate_led[i]
        moving = 0.02 < op < 0.98
        em(r, 0 if op > 0.02 else 12); em(a, 12 if moving and (f // 3) % 2 == 0 else 0); em(gg, 12 if op >= 0.98 else 0)
    for k, zx in enumerate(zones):
        inside = abs(x - zx) < 0.5
        em(strips[k], 8 if inside else 0)
        em(beams[k], 1 if inside else 5)
    em(ctrl_led, 10 if (f // 4) % 2 == 0 else 1)

for m in bpy.data.materials:
    if m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action:
        for layer in m.node_tree.animation_data.action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ---------- render ----------
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 24
if hasattr(scene.eevee, "use_raytracing"): scene.eevee.use_raytracing = True
scene.render.resolution_x, scene.render.resolution_y = 960, 540
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = 'AgX - Medium High Contrast'
except TypeError: pass
scene.render.image_settings.file_format = 'PNG'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SC, "blend", "airlock.blend"))
if TEST:
    for fr in (20, 50, 100):
        scene.frame_set(fr); scene.render.filepath = os.path.join(OUT, f"air_{fr}.png"); bpy.ops.render.render(write_still=True)
else:
    scene.render.filepath = os.path.join(OUT, "a"); bpy.ops.render.render(animation=True)
print("airlock done")
