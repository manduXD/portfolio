"""
Fix missing arena textures on already-imported OBJ.
Run in Blender: Scripting tab > Open this file > Run Script.
It relinks all arena materials to C:\\Users\\khush\\Documents\\Default Project\\arena_textures.
Then press Z > Material Preview to SEE textures (Solid mode hides them).
"""
import bpy, os

TEXDIR = r"C:\Users\khush\Documents\Default Project\arena_textures"
MAP = {
    "Grass": "arena_grass.png", "Stone": "arena_pavers.png",
    "RockTop": "arena_pavers.png", "RockSide": "arena_rock.png",
    "RockDark": "arena_rock_dark.png", "Slate": "arena_rock_dark.png",
    "Wood": "arena_wood.png", "Crate": "arena_wood.png",
    "Trunk": "arena_wood.png", "Leaf": "arena_leaf.png",
}

def base_name(mat_name):
    n = mat_name
    for prefix in ("A2_", "Material_", "low_poly_arena_v2_"):
        if n.startswith(prefix):
            n = n[len(prefix):]
    return n.split(".")[0]  # strip .001 duplicates

fixed, missing = [], []
for mat in bpy.data.materials:
    base = base_name(mat.name)
    if base not in MAP:
        continue
    fp = os.path.join(TEXDIR, MAP[base])
    if not os.path.exists(fp):
        missing.append(f"{mat.name} -> {fp} NOT FOUND")
        continue
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = next((x for x in nodes if x.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (100, 0)
        out = next((x for x in nodes if x.type == "OUTPUT_MATERIAL"), None) or nodes.new("ShaderNodeOutputMaterial")
        links.new(bsdf.outputs[0], out.inputs[0])
    # reuse or create image node
    tex = next((x for x in nodes if x.type == "TEX_IMAGE"), None)
    if tex is None:
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (-300, 100)
    try:
        tex.image = bpy.data.images.load(fp, check_existing=True)
    except Exception as e:
        missing.append(f"{mat.name}: load failed {e}")
        continue
    tex.image.colorspace_settings.name = "sRGB"
    # ensure UV -> mapping -> image chain
    if not tex.inputs["Vector"].is_linked:
        coord = next((x for x in nodes if x.type == "TEX_COORD"), None) or nodes.new("ShaderNodeTexCoord")
        mapping = next((x for x in nodes if x.type == "MAPPING"), None) or nodes.new("ShaderNodeMapping")
        try:
            links.new(coord.outputs["UV"], mapping.inputs["Vector"])
            links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        except: pass
    # link image color into base color (via mix to keep tint)
    try:
        if not any(l.from_node == tex for l in bsdf.inputs["Base Color"].links):
            mix = nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"; mix.location = (-100, 150)
            mix.inputs["Factor"].default_value = 0.55
            old = bsdf.inputs["Base Color"].default_value[:]
            mix.inputs[6].default_value = old
            links.new(tex.outputs["Color"], mix.inputs[7])
            links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    except Exception as e:
        missing.append(f"{mat.name}: link failed {e}")
        continue
    fixed.append(mat.name)

print(f"FIXED {len(fixed)}: {fixed}")
if missing:
    print(f"MISSING {len(missing)}:")
    for m in missing: print(" -", m)
else:
    print("All arena textures relinked. Press Z > Material Preview to see them.")
