# Builds the profile banner scene. Run inside Blender (via the MCP add-on).
import bpy, bmesh, math, json, os, mathutils
from mathutils import Vector, Euler, Matrix

SC = os.environ["BANNER_DIR"]
GLB = os.path.join(SC, "glb")
scene = bpy.context.scene
log = []

# ---------- clean slate (keep downloaded assets) ----------
for n in ["Cube", "Light", "Camera"]:
    o = bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o, do_unlink=True)
for o in list(bpy.data.objects):
    if o.get("built"): bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    if o.name.startswith("wdg_"): o.hide_render = o.hide_viewport = True

def tag(o):
    o["built"] = True
    return o

def empty(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    scene.collection.objects.link(e)
    e.parent = parent; e.location = loc; e.rotation_euler = rot
    e.empty_display_size = 0.05
    return tag(e)

def group(name, prefixes, loc, rotz=0.0):
    g = empty(name, loc=loc, rot=(0, 0, rotz))
    for o in bpy.data.objects:
        if o.parent is None and o is not g and any(o.name.startswith(p) for p in prefixes):
            o.parent = g
    return g

# ---------- textured materials ----------
def tex_mat(src, name, scale=1.0, tint=None, rough=None, metal=None):
    base = bpy.data.materials[src]
    m = bpy.data.materials.get(name) or base.copy()
    m.name = name; m.use_fake_user = True
    nt = m.node_tree
    tc = next(n for n in nt.nodes if n.type == 'TEX_COORD')
    mp = next(n for n in nt.nodes if n.type == 'MAPPING')
    for l in list(mp.inputs['Vector'].links): nt.links.remove(l)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    for n in nt.nodes:
        if n.type == 'TEX_IMAGE':
            n.projection = 'BOX'; n.projection_blend = 0.25
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    for l in list(out.inputs['Displacement'].links): nt.links.remove(l)
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    if tint is not None:
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1.0
        mix.inputs['B'].default_value = (*tint, 1)
        src_link = bsdf.inputs['Base Color'].links[0].from_socket if bsdf.inputs['Base Color'].links else None
        if src_link: nt.links.new(src_link, mix.inputs['A'])
        nt.links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    if rough is not None:
        for l in list(bsdf.inputs['Roughness'].links): nt.links.remove(l)
        bsdf.inputs['Roughness'].default_value = rough
    if metal is not None:
        for l in list(bsdf.inputs['Metallic'].links): nt.links.remove(l)
        bsdf.inputs['Metallic'].default_value = metal
    return m

def proc_mat(name, color, rough=0.45, metal=0.0, noise=12.0, bump=0.08, emit=None, emit_strength=0.0):
    """Principled material with procedural noise texture driving roughness and bump."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; m.use_fake_user = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = metal
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = noise; nz.inputs['Detail'].default_value = 8
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = rough * 0.75; mr.inputs['To Max'].default_value = min(1, rough * 1.25)
    nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.002
    nt.links.new(nz.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_strength
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def img_mat(name, path, emit=1.0, rough=0.3):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; m.use_fake_user = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path, check_existing=True)
    t.image.use_fake_user = True
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = emit
    b.inputs['Roughness'].default_value = rough
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def box(name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = size; o.location = loc; o.rotation_euler = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        md = o.modifiers.new("bevel", 'BEVEL'); md.width = bevel; md.segments = 3
    o.data.materials.append(mat)
    o.parent = parent
    return tag(o)

def cyl(name, r, h, loc, mat, parent=None, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts)
    o = bpy.context.active_object; o.name = name; o.location = loc; o.rotation_euler = rot
    o.data.materials.append(mat); o.parent = parent
    bpy.ops.object.shade_smooth()
    return tag(o)

def import_glb(path, parent, mat_fix=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        tag(o)
        if o.parent is None:
            o.parent = parent
        if o.type == 'MESH' and mat_fix:
            mat_fix(o)
    return new

# ---------- room ----------
M_FLOOR = tex_mat("concrete_floor_worn_02", "Floor", scale=0.35)
M_WALL = tex_mat("concrete_wall_004", "Wall", scale=0.3, tint=(0.42, 0.45, 0.5))
M_CAB = tex_mat("painted_metal_shutter", "Cabinet", scale=1.4, tint=(0.55, 0.58, 0.62))
M_PLATE = tex_mat("metal_plate_02", "Backplate", scale=2.0, tint=(0.85, 0.87, 0.9))
M_FOAM = tex_mat("polystyrene", "Sponge", scale=6.0, tint=(1.0, 0.78, 0.18), rough=0.85)
M_STEEL = tex_mat("metal_plate", "Steel", scale=3.0, rough=0.35, metal=1.0)

bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
floor = tag(bpy.context.active_object); floor.name = "Floor"; floor.data.materials.append(M_FLOOR)
wall = box("BackWall", (14, 0.2, 5), (0.5, 1.55, 2.5), M_WALL)

# ---------- furniture from Poly Haven ----------
desk = group("Desk", ["metal_office_desk"], (0.35, 0.25, 0))
group("Shelves", ["steel_frame_shelves_01"], (-1.55, 1.15, 0))
crate = bpy.data.objects["plastic_crate_01"]; crate.location = (-1.75, 1.12, 0.885)
chest = group("Chest", ["metal_tool_chest", "rig_metal_tool_chest"], (-1.3, 1.12, 1.29))
group("Cart", ["tool_cart"], (3.35, 0.6, 0), rotz=math.radians(-12))
lamp = group("Lamp", ["geo_", "cur_", "hlp_", "rig_lamp", "wdg_"], (-0.45, 0.55, 0.788), rotz=math.radians(200))
DESK_TOP = 0.788

# ---------- Panda arm (URDF chain from kinematics.yaml) ----------
H = math.pi / 2
JOINTS = [((0, 0, 0.333), (0, 0, 0)), ((0, 0, 0), (-H, 0, 0)), ((0, -0.316, 0), (H, 0, 0)),
          ((0.0825, 0, 0), (H, 0, 0)), ((-0.0825, 0.384, 0), (-H, 0, 0)), ((0, 0, 0), (H, 0, 0)),
          ((0.088, 0, 0), (H, 0, 0))]
M_WHITE = proc_mat("PandaWhite", (0.86, 0.87, 0.88), rough=0.32, noise=40, bump=0.03)
M_DARK = proc_mat("PandaDark", (0.035, 0.037, 0.04), rough=0.4, noise=40, bump=0.03)

def panda_fix(o):
    # keep the original white/black split, but use textured materials
    for i, slot in enumerate(o.material_slots):
        c = slot.material.diffuse_color if slot.material else (1, 1, 1, 1)
        try:
            bs = slot.material.node_tree.nodes.get("Principled BSDF").inputs['Base Color'].default_value
            c = bs
        except Exception:
            pass
        lum = 0.3 * c[0] + 0.6 * c[1] + 0.1 * c[2]
        slot.material = M_WHITE if lum > 0.35 else M_DARK
    for p in o.data.polygons: p.use_smooth = True

ROBOT_BASE = Vector((0.55, 0.25, DESK_TOP))
robot = empty("PandaBase", loc=ROBOT_BASE)
import_glb(os.path.join(GLB, "panda", "link0.glb"), robot, panda_fix)
parent = robot; joints = []
for i, (xyz, r) in enumerate(JOINTS):
    fixed = empty(f"J{i+1}_fixed", parent, xyz, r)
    j = empty(f"J{i+1}", fixed)
    import_glb(os.path.join(GLB, "panda", f"link{i+1}.glb"), j, panda_fix)
    joints.append(j); parent = j
flange = empty("Flange", parent, (0, 0, 0.107))
hand = empty("Hand", flange, (0, 0, 0), (0, 0, -math.pi / 4))
import_glb(os.path.join(GLB, "panda", "hand.glb"), hand, panda_fix)
fl = empty("FingerL", hand, (0, 0, 0.0584)); import_glb(os.path.join(GLB, "panda", "finger.glb"), fl, panda_fix)
fr = empty("FingerR", hand, (0, 0, 0.0584), (0, 0, math.pi)); import_glb(os.path.join(GLB, "panda", "finger.glb"), fr, panda_fix)
tcp = empty("TCP", hand, (0, 0, 0.1034))
# mounting plate
box("RobotPlate", (0.26, 0.26, 0.012), ROBOT_BASE + Vector((0, 0, -0.006)), M_STEEL, bevel=0.004)

# ---------- Panther UGV ----------
M_PANTHER = proc_mat("PantherBody", (0.09, 0.095, 0.1), rough=0.5, noise=30, bump=0.05)
M_TIRE = proc_mat("Tire", (0.02, 0.02, 0.02), rough=0.85, noise=120, bump=0.25)
M_HUB = proc_mat("Hub", (0.6, 0.62, 0.65), rough=0.3, metal=1.0, noise=60, bump=0.03)

def panther_fix(o):
    for slot in o.material_slots:
        name = (slot.material.name if slot.material else "").lower()
        c = (0.5, 0.5, 0.5)
        try:
            c = slot.material.node_tree.nodes.get("Principled BSDF").inputs['Base Color'].default_value[:3]
        except Exception:
            pass
        lum = 0.3 * c[0] + 0.6 * c[1] + 0.1 * c[2]
        if lum > 0.6:
            slot.material = proc_mat("PantherLight", (0.9, 0.9, 0.9), rough=0.2, emit=(0.95, 0.97, 1.0), emit_strength=6.0)
        elif lum > 0.25:
            slot.material = M_HUB
        else:
            slot.material = M_PANTHER if "wheel" not in o.name.lower() else M_TIRE
    for p in o.data.polygons: p.use_smooth = True

panther = empty("Panther", loc=(1.95, -0.75, 0.1825), rot=(0, 0, math.radians(205)))
import_glb(os.path.join(GLB, "panther", "base.glb"), panther, panther_fix)
for w, (x, y) in {"fl": (0.22, 0.3485), "fr": (0.22, -0.3485), "rl": (-0.22, 0.3485), "rr": (-0.22, -0.3485)}.items():
    we = empty(f"Wheel_{w}", panther, (x, y, 0))
    import_glb(os.path.join(GLB, "panther", f"{w}_wheel.glb"), we, panther_fix)

# ---------- PLC control cabinet on the back wall ----------
cab = empty("PLC_Cabinet", loc=(2.35, 1.27, 1.35))
CW, CH, CD = 0.9, 1.1, 0.32
box("CabBack", (CW, 0.02, CH), (0, CD / 2 - 0.01, 0), M_CAB, cab)
box("CabTop", (CW, CD, 0.02), (0, 0, CH / 2), M_CAB, cab)
box("CabBot", (CW, CD, 0.02), (0, 0, -CH / 2), M_CAB, cab)
box("CabL", (0.02, CD, CH), (-CW / 2, 0, 0), M_CAB, cab)
box("CabR", (0.02, CD, CH), (CW / 2, 0, 0), M_CAB, cab)
box("CabPlate", (CW - 0.06, 0.006, CH - 0.06), (0, CD / 2 - 0.025, 0), M_PLATE, cab)
door = empty("CabDoorHinge", cab, (CW / 2, -CD / 2, 0), (0, 0, math.radians(-112)))
box("CabDoor", (CW, 0.025, CH), (-CW / 2, -0.012, 0), M_CAB, door, bevel=0.004)
M_DUCT = proc_mat("Duct", (0.55, 0.57, 0.58), rough=0.6, noise=60, bump=0.04)
M_RAIL = tex_mat("metal_plate", "Rail", scale=8.0, rough=0.25, metal=1.0)
M_MOD = proc_mat("ModuleBody", (0.12, 0.125, 0.13), rough=0.45, noise=80, bump=0.03)
M_MODF = proc_mat("ModuleFront", (0.2, 0.21, 0.22), rough=0.35, noise=80, bump=0.02)
M_TERM = proc_mat("Terminal", (0.62, 0.64, 0.66), rough=0.5, noise=90, bump=0.03)
M_TERMB = proc_mat("TerminalBlue", (0.08, 0.22, 0.6), rough=0.5, noise=90, bump=0.03)
yb = CD / 2 - 0.03
for z in (0.42, -0.04, -0.45):
    box(f"DuctH{z}", (CW - 0.1, 0.06, 0.06), (0, yb - 0.03, z + 0.15 if z < 0.4 else z), M_DUCT, cab)
for x in (-CW / 2 + 0.07, CW / 2 - 0.07):
    box(f"DuctV{x}", (0.06, 0.06, CH - 0.2), (x, yb - 0.03, 0), M_DUCT, cab)
box("Rail1", (CW - 0.2, 0.012, 0.035), (0, yb - 0.006, 0.2), M_RAIL, cab)
box("Rail2", (CW - 0.2, 0.012, 0.035), (0, yb - 0.006, -0.25), M_RAIL, cab)
# S7-1500 style rack: PSU, CPU, I/O modules
leds = []
M_LED_G = proc_mat("LedG", (0.1, 1.0, 0.3), emit=(0.15, 1.0, 0.35), emit_strength=0.0, rough=0.2)
M_LED_O = proc_mat("LedO", (1.0, 0.6, 0.1), emit=(1.0, 0.55, 0.1), emit_strength=0.0, rough=0.2)
M_LED_B = proc_mat("LedB", (0.2, 0.5, 1.0), emit=(0.25, 0.55, 1.0), emit_strength=0.0, rough=0.2)
x = -CW / 2 + 0.14
for k, w in enumerate([0.07, 0.07, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035]):
    h = 0.15
    m = box(f"Mod{k}", (w - 0.003, 0.13, h), (x + w / 2, yb - 0.075, 0.2), M_MOD, cab, bevel=0.002)
    box(f"ModF{k}", (w - 0.006, 0.004, h * 0.62), (x + w / 2, yb - 0.142, 0.18), M_MODF, cab)
    for j in range(2 if k > 1 else 3):
        led = box(f"Led{k}_{j}", (0.008, 0.004, 0.006), (x + w / 2 - 0.008 + j * 0.008, yb - 0.143, 0.255), [M_LED_G, M_LED_O, M_LED_B][(k + j) % 3] if k != 1 else M_LED_G, cab)
        leds.append(led)
    x += w
# terminal blocks on the lower rail
x = -CW / 2 + 0.14
for k in range(26):
    box(f"Term{k}", (0.0055, 0.05, 0.06), (x, yb - 0.04, -0.25), M_TERMB if k % 5 == 4 else M_TERM, cab, bevel=0.0008)
    x += 0.0062
# ---------- desk props: monitors, controller PCB, sponge ----------
M_BEZEL = proc_mat("Bezel", (0.03, 0.032, 0.035), rough=0.5, noise=90, bump=0.04)
M_HMI = img_mat("ScreenHMI", os.path.join(SC, "screen_hmi.png"), emit=1.4)
M_LLM = img_mat("ScreenLLM", os.path.join(SC, "screen_llm.png"), emit=1.4)

def monitor(name, loc, rotz, mat):
    g = empty(name, loc=loc, rot=(0, 0, rotz))
    box(name + "Foot", (0.22, 0.16, 0.012), (0, 0.03, 0.006), M_BEZEL, g, bevel=0.004)
    box(name + "Neck", (0.04, 0.02, 0.2), (0, 0.06, 0.11), M_BEZEL, g)
    box(name + "Body", (0.6, 0.03, 0.36), (0, 0.04, 0.33), M_BEZEL, g, bevel=0.006)
    bpy.ops.mesh.primitive_plane_add(size=1)
    s = bpy.context.active_object; s.name = name + "Screen"
    s.scale = (0.58, 0.34, 1); s.rotation_euler = (math.pi / 2, 0, 0); s.location = (0, 0.024, 0.33)
    s.data.materials.append(mat); s.parent = g; tag(s)
    return g

monitor("MonHMI", (-0.42, 0.5, DESK_TOP), math.radians(14), M_HMI)
monitor("MonLLM", (0.12, 0.56, DESK_TOP), math.radians(-6), M_LLM)

# gripper controller PCB with a generated board texture
M_PCB = img_mat("PCB", os.path.join(SC, "pcb.png"), emit=0.0, rough=0.35)
pcb = box("PCB", (0.14, 0.09, 0.0016), (0.02, -0.02, DESK_TOP + 0.012), M_PCB, rot=(0, 0, math.radians(18)))
for i, (dx, dy) in enumerate([(-0.064, -0.04), (0.064, -0.04), (-0.064, 0.04), (0.064, 0.04)]):
    cyl(f"Standoff{i}", 0.003, 0.01, Vector((0.02, -0.02, DESK_TOP + 0.005)) + Matrix.Rotation(math.radians(18), 3, 'Z') @ Vector((dx, dy, 0)), M_STEEL)
M_CAN = tex_mat("metal_plate", "Shield", scale=20.0, rough=0.25, metal=1.0)
box("ESP32Shield", (0.025, 0.018, 0.003), Vector((0.0, -0.025, DESK_TOP + 0.0145)), M_CAN, rot=(0, 0, math.radians(18)))
pcb_led = box("PCBLed", (0.004, 0.003, 0.002), Vector((0.06, -0.005, DESK_TOP + 0.014)), M_LED_B, rot=(0, 0, math.radians(18)))
leds.append(pcb_led)

# sponge payload (thesis slip tests used sponges)
sponge = box("Sponge", (0.075, 0.065, 0.05), (0, 0, 0), M_FOAM, bevel=0.006)

# cable from PCB toward the robot base
curve = bpy.data.curves.new("Cable", 'CURVE'); curve.dimensions = '3D'; curve.bevel_depth = 0.0035
sp = curve.splines.new('BEZIER'); sp.bezier_points.add(2)
for p, co in zip(sp.bezier_points, [(0.08, 0.0, DESK_TOP + 0.013), (0.3, 0.12, DESK_TOP + 0.004), (0.48, 0.2, DESK_TOP + 0.02)]):
    p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
cable = tag(bpy.data.objects.new("Cable", curve)); scene.collection.objects.link(cable)
curve.materials.append(proc_mat("CableMat", (0.02, 0.02, 0.022), rough=0.55, noise=200, bump=0.1))

json.dump({"leds": [l.name for l in leds]}, open(os.path.join(SC, "scene_meta.json"), "w"))
for m in bpy.data.materials: m.use_fake_user = True
bpy.ops.wm.save_mainfile()
print("built", len([o for o in bpy.data.objects if o.get('built')]), "objects")
