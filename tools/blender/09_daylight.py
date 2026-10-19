# Daytime variant of the banner scene for GitHub light mode.
import bpy, os, sys
s = bpy.context.scene
OUT = sys.argv[sys.argv.index("--") + 1]
for n in s.world.node_tree.nodes:
    if n.type == 'BACKGROUND': n.inputs['Strength'].default_value = 0.9
L = bpy.data.lights
L["Key"].energy = 420; L["Fill"].energy = 120; L["Rim"].energy = 140; L["LampSpot"].energy = 30
for n in bpy.data.materials["Wall"].node_tree.nodes:
    if n.type == 'MIX' and n.blend_type == 'MULTIPLY': n.inputs['B'].default_value = (0.46, 0.48, 0.5, 1)
s.view_settings.exposure = 0.3
# saturated neon so the name stays readable against a daylit wall
for nm, col, st in (("NeonTeal", (0.0, 0.55, 0.75), 14.0), ("NeonAmber", (1.0, 0.42, 0.05), 12.0)):
    b = bpy.data.materials[nm].node_tree.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Emission Color'].default_value = (*col, 1)
    b.inputs['Emission Strength'].default_value = st
bpy.data.lights["NeonWash"].energy = 12
s.render.filepath = os.path.join(OUT, "f")
s.frame_start = int(os.environ.get("FS", s.frame_start)); s.frame_end = int(os.environ.get("FE", s.frame_end))
if os.environ.get("ONE"):
    s.frame_set(70); s.render.filepath = os.path.join(OUT, "day_test.png")
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
