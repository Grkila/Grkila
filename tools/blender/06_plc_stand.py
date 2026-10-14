# PLC training stand on the tool cart: real Siemens CAD exports (S7-1500 wide CPU,
# I/O modules, KTP700-size HMI) on a tilted aluminium board.
import bpy, math, os
from mathutils import Vector, Matrix

SC = os.environ["BANNER_DIR"]
SIE = os.environ["SIEMENS_MODELS"]
scene = bpy.context.scene
src = open(os.path.join(SC, "01_build.py"), encoding="utf-8").read()
exec(src[src.index("def tag(o)"):src.index("# ---------- room ----------")], globals())

for o in list(bpy.data.objects):
    if o.get("plcstand"): bpy.data.objects.remove(o, do_unlink=True)

def mine(o):
    o["plcstand"] = True; o["built"] = True
    return o

# colour -> textured material (noise roughness + bump), keyed by the CAD colour names
def cad_mat(name):
    rgb = name[name.index("(") + 1:name.index(")")].split(",") if "(" in name else ["150", "150", "150"]
    c = tuple((int(v) / 255.0) ** 2.2 for v in rgb)
    lum = 0.3 * c[0] + 0.6 * c[1] + 0.1 * c[2]
    emit = c if (c[1] > 0.3 and c[0] < 0.1 and c[2] < 0.2) or name.endswith("(255,0,0)") else None
    return proc_mat("S7_" + name.replace(" ", ""), c, rough=0.42 if lum < 0.4 else 0.5, noise=180, bump=0.02,
                    emit=emit, emit_strength=6.0 if emit else 0.0)

def import_obj(fname, parent):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=os.path.join(SIE, fname), global_scale=0.001, forward_axis='NEGATIVE_Z', up_axis='Y')
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        mine(o)
        if o.type == 'MESH':
            for s in o.material_slots:
                if s.material: s.material = cad_mat(s.material.name)
            for p in o.data.polygons: p.use_smooth = False
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in new if o.type == 'MESH' for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    holder = mine(empty(fname.split(".")[0].replace(" ", "_") + "_Holder", parent))
    for o in new:
        if o.parent is None:
            o.parent = holder
            o.location -= Vector((mn.x, mx.y, mn.z))   # origin: left, back, bottom
    return holder, mx - mn

cart = bpy.data.objects["Cart"]
stand = mine(empty("PLCStand", loc=cart.matrix_world @ Vector((0.0, -0.05, 0.965)), rot=(0, 0, cart.rotation_euler.z + math.radians(14))))
board = mine(empty("PLCBoard", stand, (0, 0.06, 0.0), (math.radians(-10), 0, 0)))
BW, BH = 0.78, 0.6
M_ALU = tex_mat("metal_plate_02", "Alu", scale=3.0, tint=(0.75, 0.77, 0.8), rough=0.35, metal=1.0)
mine(box("BoardPlate", (BW, 0.012, BH), (0, 0.006, BH / 2 + 0.03), M_ALU, board, bevel=0.003))
for x in (-BW / 2 + 0.06, BW / 2 - 0.06):
    mine(box(f"BoardFoot{x:.2f}", (0.04, 0.22, 0.02), (x, 0.03, 0.01), M_ALU, stand, bevel=0.003))
M_RAILS = bpy.data.materials["Rail"]
RAIL_Z = 0.17
mine(box("BoardRail", (BW - 0.08, 0.008, 0.035), (0, -0.004, RAIL_Z + 0.07), M_RAILS, board))
x = -0.2
cpu, cdim = import_obj("S7 1500 wider.obj", board)
cpu.location = (x, 0.0, RAIL_Z); x += cdim.x + 0.002
for i in range(4):
    io, idim = import_obj("IO_module.obj", board)
    io.location = (x, 0.0, RAIL_Z); x += idim.x + 0.001
hmi, hdim = import_obj("HMI_panel.obj", board)
hmi.location = (-hdim.x / 2, 0.0, 0.38)
# HMI screen overlay sized to the panel's display area
bpy.ops.mesh.primitive_plane_add(size=1)
scr = mine(bpy.context.active_object); scr.name = "StandHMIScreen"
scr.parent = board; scr.rotation_euler = (math.pi / 2, 0, 0)
scr.scale = (hdim.x * 0.72, hdim.z * 0.66, 1)
scr.location = (0.0, -hdim.y - 0.0008, 0.38 + hdim.z * 0.5)
scr.data.materials.append(bpy.data.materials["ScreenHMI"])
# terminal strip and wiring duct under the rail
M_TERM = bpy.data.materials["Terminal"]; M_TB = bpy.data.materials["TerminalBlue"]
for k in range(40):
    mine(box(f"StandTerm{k}", (0.0055, 0.045, 0.05), (-0.22 + k * 0.0062, -0.022, 0.085), M_TB if k % 6 == 5 else M_TERM, board, bevel=0.0008))
mine(box("StandDuct", (BW - 0.08, 0.05, 0.04), (0, -0.025, 0.035 + 0.02), bpy.data.materials["Duct"], board))
# E-stop and pilot lights at the board's right edge
M_RED = bpy.data.materials["SafetyRed"]; M_YEL = bpy.data.materials["SafetyYellow"]
mine(box("StandEstopPlate", (0.08, 0.004, 0.08), (0.31, -0.002, 0.47), M_YEL, board, bevel=0.003))
mine(cyl("StandEstop", 0.028, 0.03, (0.31, -0.02, 0.47), M_RED, board, rot=(math.pi / 2, 0, 0)))
for i, nm in enumerate(["PilotG", "PilotA"]):
    mine(cyl(f"StandPilot{i}", 0.012, 0.012, (0.31, -0.008, 0.36 - i * 0.05), bpy.data.materials[nm], board, rot=(math.pi / 2, 0, 0)))
for m in bpy.data.materials: m.use_fake_user = True
bpy.ops.wm.save_mainfile()
print("stand ok", [round(v, 3) for v in cdim], [round(v, 3) for v in hdim])
