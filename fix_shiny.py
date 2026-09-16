"""
Fix super-reflective / glossy imports: forces matte PBR values on every material.
Run in Blender: Scripting tab > Open this file > Run Script.
- Everything -> Roughness 0.9, Metallic 0, low specular (matte low-poly look)
- Glass stays slightly glossy (0.25), Water 0.15, lamps/emit left alone
Works in Blender 3.x and 4.x, on any imported scene.
"""
import bpy

GLASSY = {"Glass": 0.25, "Water": 0.15, "Window": 0.25}
EMIT = ("Neon", "LampGlow", "LampH", "Brazier", "TorchFire", "FinishPad", "JumpPad", "Check")

def base_name(n):
    for p in ("V_", "A2_", "Arena_", "LP_"):
        if n.startswith(p):
            n = n[len(p):]
    return n.split(".")[0]

fixed = 0
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    base = base_name(mat.name)
    if base.startswith(EMIT) or "Neon" in base:
        continue
    bsdf = next((x for x in mat.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        continue
    try:
        bsdf.inputs["Roughness"].default_value = GLASSY.get(base, 0.9)
        bsdf.inputs["Metallic"].default_value = 0.0
        # Blender 4.x uses "Specular IOR Level", 3.x uses "Specular"
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.35
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.35
        fixed += 1
    except Exception as e:
        print(f"skip {mat.name}: {e}")

print(f"De-shined {fixed} materials. If still glossy, check: Rendered view (not just Material Preview, which adds studio reflections), and any HDRI World strength.")
