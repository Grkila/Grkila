import bpy, math
from mathutils import Vector
scene = bpy.context.scene
w = scene.world
for n in w.node_tree.nodes:
    if n.type == 'BACKGROUND': n.inputs['Strength'].default_value = WORLD
L = {"Key": KEY, "Rim": RIM, "Fill": FILL, "CabGlow": CAB}
for k, v in L.items(): bpy.data.lights[k].energy = v
bpy.data.lights["LampSpot"].energy = LAMP
cam = bpy.data.objects["BannerCam"]; cd = cam.data
cam.location = Vector(CAMLOC); bpy.data.objects["CamTarget"].location = Vector(CAMTGT)
cd.lens = LENS; cd.shift_x = SHIFTX; cd.shift_y = SHIFTY; cd.dof.aperture_fstop = FSTOP
scene.view_settings.exposure = EXPO
# darker, cooler wall so the neon carries the frame
wm = bpy.data.materials["Wall"]
for n in wm.node_tree.nodes:
    if n.type == 'MIX' and n.blend_type == 'MULTIPLY': n.inputs['B'].default_value = (*WALLTINT, 1)
bpy.ops.wm.save_mainfile()
print("look ok")
