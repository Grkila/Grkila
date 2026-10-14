# Lighting, camera, render settings and the baked pick-and-place loop.
import bpy, json, math, os, random
from mathutils import Vector, Matrix

SC = os.environ["BANNER_DIR"]
scene = bpy.context.scene
FPS = 15
scene.render.fps = FPS

def tagged(o):
    o["built"] = True
    return o

# ---------- world + lights ----------
w = bpy.data.worlds.get("PolyHaven university_workshop")
scene.world = w
for n in w.node_tree.nodes:
    if n.type == 'BACKGROUND':
        n.inputs['Strength'].default_value = 0.22

def area(name, loc, rot, energy, color, size):
    l = bpy.data.lights.get(name) or bpy.data.lights.new(name, 'AREA')
    l.energy = energy; l.color = color; l.size = size
    o = bpy.data.objects.get(name) or tagged(bpy.data.objects.new(name, l))
    if o.name not in scene.collection.objects: scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    return o

area("Key", (-0.6, -1.6, 2.8), (math.radians(38), 0, math.radians(-25)), 260, (1.0, 0.86, 0.72), 1.6)
area("Rim", (2.8, 0.6, 2.4), (math.radians(55), 0, math.radians(110)), 220, (0.55, 0.7, 1.0), 1.2)
area("CabGlow", (2.35, 0.6, 1.35), (math.radians(90), 0, 0), 25, (0.85, 0.9, 1.0), 0.6)
area("Fill", (1.2, -3.0, 0.8), (math.radians(85), 0, 0), 40, (0.6, 0.7, 0.9), 3.0)
spot = bpy.data.lights.get("LampSpot") or bpy.data.lights.new("LampSpot", 'SPOT')
spot.energy = 40; spot.color = (1.0, 0.78, 0.5); spot.spot_size = math.radians(70); spot.spot_blend = 0.6
so = bpy.data.objects.get("LampSpot") or tagged(bpy.data.objects.new("LampSpot", spot))
if so.name not in scene.collection.objects: scene.collection.objects.link(so)
so.location = (-0.55, 0.35, 1.45); so.rotation_euler = (math.radians(20), 0, 0)

# ---------- camera ----------
cam_data = bpy.data.cameras.get("BannerCam") or bpy.data.cameras.new("BannerCam")
cam = bpy.data.objects.get("BannerCam") or tagged(bpy.data.objects.new("BannerCam", cam_data))
if cam.name not in scene.collection.objects: scene.collection.objects.link(cam)
scene.camera = cam
P = json.load(open(os.path.join(SC, "cam.json"))) if os.path.exists(os.path.join(SC, "cam.json")) else {}
cam_data.lens = P.get("lens", 30)
cam_data.sensor_fit = 'HORIZONTAL'
cam_data.shift_x = P.get("shift_x", -0.12)
cam_data.shift_y = P.get("shift_y", 0.0)
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = P.get("fstop", 4.0)
target = Vector(P.get("target", (1.05, 0.35, 0.95)))
cam.location = Vector(P.get("loc", (0.9, -3.3, 1.55)))
tgt = bpy.data.objects.get("CamTarget") or tagged(bpy.data.objects.new("CamTarget", None))
if tgt.name not in scene.collection.objects: scene.collection.objects.link(tgt)
tgt.location = target
con = cam.constraints.get("Track") or cam.constraints.new('TRACK_TO')
con.name = "Track"; con.target = tgt; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
cam_data.dof.focus_object = bpy.data.objects["PandaBase"]

# ---------- render ----------
scene.render.engine = 'BLENDER_EEVEE'
ee = scene.eevee
for attr, val in [("taa_render_samples", P.get("samples", 48)), ("use_raytracing", True),
                  ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)]:
    if hasattr(ee, attr): setattr(ee, attr, val)
if hasattr(ee, "ray_tracing_options"):
    ee.ray_tracing_options.resolution_scale = '2'
scene.render.resolution_x = P.get("w", 1920)
scene.render.resolution_y = P.get("h", 600)
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except TypeError:
    pass
scene.view_settings.exposure = P.get("exposure", 0.0)

# ---------- animation ----------
data = json.load(open(os.path.join(SC, "poses.json")))
poses = {p["name"]: p for p in data["poses"]}
order = ["home", "aboveA", "atA", "gripA", "liftA", "aboveB", "atB", "relB", "liftB", "home"]
secs = [1.1, 0.7, 0.35, 0.6, 1.2, 0.7, 0.35, 0.6, 1.1]          # A -> B
back = ["home", "aboveB", "atB", "gripA", "liftB", "aboveA", "atA", "relB", "liftA", "home"]  # B -> A (mirror)
mirror = lambda q: [-q[0], q[1], -q[2], q[3], -q[4], q[5], q[6]]

segments = []
def add_leg(names, sides):
    for i in range(len(names) - 1):
        a, b = names[i], names[i + 1]
        qa, qb = poses[a]["q"], poses[b]["q"]
        if sides:
            qa, qb = (mirror(qa) if a not in ("home",) else qa), (mirror(qb) if b not in ("home",) else qb)
        segments.append((qa, qb, secs[i], poses[b]["grip"], poses[b]["carry"], poses[a]["grip"]))
add_leg(order, False)
add_leg(order, True)   # the mirrored leg carries the sponge back from B to A

total = sum(s[2] for s in segments)
N = round(total * FPS)
scene.frame_start, scene.frame_end = 1, N
joints = [bpy.data.objects[f"J{i+1}"] for i in range(7)]
fl, fr = bpy.data.objects["FingerL"], bpy.data.objects["FingerR"]
tcp = bpy.data.objects["TCP"]; sponge = bpy.data.objects["Sponge"]
for o in joints + [fl, fr, sponge]:
    o.animation_data_clear()
ease = lambda t: t * t * (3 - 2 * t)
SP_W = 0.065
OPEN, CLOSED = 0.04, SP_W / 2 - 0.004

base = bpy.data.objects["PandaBase"].matrix_world.copy()
A = base @ Vector((data["A"][0], data["A"][1], 0)); B = base @ Vector((data["B"][0], data["B"][1], 0))
rest_z = 0.788 + 0.025 + 0.0005
held_at = None
for j, v in zip(joints, poses["atA"]["q"]):
    j.rotation_euler = (0, 0, v)
bpy.context.view_layer.update()
m0 = tcp.matrix_world
spot_pos = Vector((m0.translation.x, m0.translation.y, rest_z))
spot_yaw = math.atan2(m0[1][1], m0[0][1]) - math.pi / 2

for f in range(1, N + 1):
    t = (f - 1) / FPS
    acc = 0
    for qa, qb, d, g, carry, g0 in segments:
        if t <= acc + d or (qa, qb) == (segments[-1][0], segments[-1][1]):
            k = ease(min(1, max(0, (t - acc) / d)))
            q = [x + (y - x) * k for x, y in zip(qa, qb)]
            grip = g0 + (g - g0) * k
            break
        acc += d
    for j, v in zip(joints, q):
        j.rotation_euler = (0, 0, v); j.keyframe_insert("rotation_euler", frame=f)
    gap = OPEN + (CLOSED - OPEN) * grip
    fl.location = (0, gap, 0.0584); fr.location = (0, -gap, 0.0584)
    fl.keyframe_insert("location", frame=f); fr.keyframe_insert("location", frame=f)
    bpy.context.view_layer.update()
    m = tcp.matrix_world
    if carry:
        loc = m.translation.copy(); loc.z -= 0.005
        sponge.location = loc
        hand_yaw = math.atan2(m[1][1], m[0][1]) - math.pi / 2
        sponge.rotation_euler = (0, 0, hand_yaw)
        spot_pos = Vector((loc.x, loc.y, rest_z)); spot_yaw = hand_yaw
        sponge.scale = (1.0, 0.9, 1.0)
    else:
        near_b = (Vector((m.translation.x, m.translation.y, 0)) - Vector((B.x, B.y, 0))).length < 0.05
        sponge.location = spot_pos
        sponge.rotation_euler = (0, 0, spot_yaw)
        sponge.scale = (1.0, 1.0 - 0.1 * grip, 1.0)
    sponge.keyframe_insert("location", frame=f); sponge.keyframe_insert("rotation_euler", frame=f); sponge.keyframe_insert("scale", frame=f)

# blinking LEDs (constant interpolation, period divides the loop)
meta = json.load(open(os.path.join(SC, "scene_meta.json")))
random.seed(5)
for name in meta["leds"]:
    o = bpy.data.objects[name]
    mat = o.data.materials[0].copy(); o.data.materials[0] = mat
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs['Emission Strength'].default_value = 0
    per = random.choice([N // 2, N // 3, N // 6, N // 10])
    on = random.random() < 0.7
    for f in range(1, N + 2, max(2, per // 2)):
        b.inputs['Emission Strength'].default_value = 18.0 if (on or (f // max(1, per // 2)) % 2 == 0) else 0.6
        b.inputs['Emission Strength'].keyframe_insert("default_value", frame=f)
        on = not on if random.random() < 0.35 else on
    act = mat.node_tree.animation_data.action
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

for m in bpy.data.materials: m.use_fake_user = True
bpy.ops.wm.save_mainfile()
print("frames", N, "seconds", round(total, 2))
