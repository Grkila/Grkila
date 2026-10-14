# Neon name sign on the back wall: glyph-outline tubes on an acrylic backer.
import bpy, math
from mathutils import Vector

scene = bpy.context.scene
for o in list(bpy.data.objects):
    if o.get("sign"): bpy.data.objects.remove(o, do_unlink=True)

def mark(o):
    o["sign"] = True; o["built"] = True
    return o

WALL_Y = 1.45
CENTER = Vector((0.0, WALL_Y - 0.06, 1.62))
root = mark(bpy.data.objects.new("NeonSign", None)); scene.collection.objects.link(root)
root.location = CENTER

def neon_mat(name, color, strength):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; m.use_fake_user = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Emission Color'].default_value = (*color, 1)
    b.inputs['Emission Strength'].default_value = strength
    b.inputs['Roughness'].default_value = 0.15
    b.inputs['Coat Weight'].default_value = 1.0
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def tube_text(name, text, size, loc, mat, font, depth):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = text; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    cu.font = font
    ob = mark(bpy.data.objects.new(name, cu)); scene.collection.objects.link(ob)
    ob.parent = root; ob.location = loc; ob.rotation_euler = (math.pi / 2, 0, 0)
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects: o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.convert(target='CURVE')
    ob = bpy.context.active_object
    ob.data.fill_mode = 'NONE'
    ob.data.extrude = 0
    ob.data.bevel_depth = depth
    ob.data.bevel_resolution = 4
    ob.data.materials.clear(); ob.data.materials.append(mat)
    return ob

font = bpy.data.fonts.load(r"C:\Windows\Fonts\segoeuisl.ttf", check_existing=True)
NEON = (0.45, 0.93, 1.0)
AMBER = (1.0, 0.62, 0.22)
name = tube_text("NeonName", "Dušan Grković", 0.38, (0, 0, 0.05), neon_mat("NeonTeal", NEON, 28.0), font, 0.0042)
sub_font = bpy.data.fonts.load(r"C:\Windows\Fonts\segoeui.ttf", check_existing=True)
sub = tube_text("NeonSub", "embedded  ·  robotics  ·  automation  ·  AI", 0.085, (0, 0, -0.2), neon_mat("NeonAmber", AMBER, 22.0), sub_font, 0.0022)

# acrylic backer, standoffs and a wall wash light for the halo
glass = bpy.data.materials.get("Acrylic") or bpy.data.materials.new("Acrylic")
glass.use_nodes = True; glass.use_fake_user = True
gb = glass.node_tree.nodes.get("Principled BSDF")
gb.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 1)
gb.inputs['Roughness'].default_value = 0.08
gb.inputs['Transmission Weight'].default_value = 1.0
gb.inputs['Alpha'].default_value = 0.25
glass.surface_render_method = 'BLENDED' if hasattr(glass, "surface_render_method") else None
bpy.ops.mesh.primitive_cube_add(size=1)
backer = mark(bpy.context.active_object); backer.name = "NeonBacker"
backer.scale = (1.55, 0.008, 0.58); bpy.ops.object.transform_apply(scale=True)
backer.parent = root; backer.location = (0, 0.03, -0.03)
md = backer.modifiers.new("bevel", 'BEVEL'); md.width = 0.01; md.segments = 3
backer.data.materials.append(glass)
steel = bpy.data.materials.get("Steel")
for i, (x, z) in enumerate([(-0.73, 0.22), (0.73, 0.22), (-0.73, -0.29), (0.73, -0.29)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.07, vertices=24)
    s = mark(bpy.context.active_object); s.name = f"NeonStandoff{i}"
    s.rotation_euler = (math.pi / 2, 0, 0); s.parent = root; s.location = (x, 0.035, z)
    if steel: s.data.materials.append(steel)

wash = bpy.data.lights.get("NeonWash") or bpy.data.lights.new("NeonWash", 'AREA')
wash.shape = 'RECTANGLE'; wash.size = 1.5; wash.size_y = 0.45
wash.energy = 55; wash.color = NEON
wo = mark(bpy.data.objects.new("NeonWash", wash)); scene.collection.objects.link(wo)
wo.parent = root; wo.location = (0, 0.0, 0); wo.rotation_euler = (-math.pi / 2, 0, 0)  # faces the wall
spill = bpy.data.lights.get("NeonSpill") or bpy.data.lights.new("NeonSpill", 'AREA')
spill.size = 1.6; spill.energy = 30; spill.color = NEON
so = mark(bpy.data.objects.new("NeonSpill", spill)); scene.collection.objects.link(so)
so.parent = root; so.location = (0, -0.08, 0); so.rotation_euler = (math.pi / 2, 0, 0)    # faces the room

for m in bpy.data.materials: m.use_fake_user = True
bpy.ops.wm.save_mainfile()
print("sign ok", name.dimensions[:], sub.dimensions[:])
