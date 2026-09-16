"""
Rocky Arena - Blender builder (matches Roblox map reference)
Blender 3.x / 4.x, Z-up, meters.
Usage:
  1. Blender > Scripting tab > Open this file > Run Script (Alt+P)
  2. Collection "RockyArena" appears in Outliner
No addons needed.
"""

import bpy

# (name, loc_x, loc_y, loc_z, size_x, size_y, size_z, material)
# Blender coords: X right, Y forward, Z up. Converted from Roblox version.
BOXES = [
    # ground
    ("Ground", 0, 0, -1, 512, 512, 2, "Ground"),
    # main platform (light top + dark base)
    ("MainBase", 0, 10, 3, 28, 22, 6, "RockSide"),
    ("MainTop", 0, 10, 6.2, 28.4, 22.4, 0.8, "RockTop"),
    # side platforms
    ("Plat_Left", -32, -8, 2, 18, 16, 4, "RockSide"),
    ("Plat_Left_Top", -32, -8, 4.2, 18.4, 16.4, 0.8, "RockTop"),
    ("Plat_Right", 32, 12, 3, 20, 14, 6, "RockSide"),
    ("Plat_Right_Top", 32, 12, 6.2, 20.4, 14.4, 0.8, "RockTop"),
    ("Plat_Back", 0, -32, 2.5, 24, 12, 5, "RockSide"),
    ("Plat_Back_Top", 0, -32, 5.2, 24.4, 12.4, 0.8, "RockTop"),
    ("Plat_FarRight", 38, -18, 1.5, 14, 14, 3, "Cover"),
    # cover walls
    ("Cover1", -12, -12, 1.5, 10, 1.5, 3, "Cover"),
    ("Cover2", 14, -6, 1.5, 10, 1.5, 3, "Cover"),
    ("Cover3", -8, 28, 1.5, 8, 1.5, 3, "Cover"),
    ("Cover4", 20, 30, 1.5, 12, 2, 3, "Cover"),
    ("Cover5", -28, 18, 1, 2, 10, 2, "Cover"),
    ("FloatDebris", 18, -8, 14, 6, 2, 1.2, "Debris"),
    ("Crate", -38, 8, 1, 6, 3, 2, "Crate"),
    # cliffs
    ("CliffBack1", -30, -58, 12, 30, 10, 28, "RockDark"),
    ("CliffBack2", 5, -62, 15, 35, 12, 34, "RockDark"),
    ("CliffBack3", 40, -58, 11, 28, 10, 26, "RockDark"),
    ("CliffLeft", -58, 0, 12, 10, 120, 28, "RockDark"),
    ("CliffRight", 58, 0, 12, 10, 120, 28, "RockDark"),
    ("CliffFrontL", -30, 60, 8, 40, 10, 20, "RockDark"),
    ("CliffFrontR", 30, 60, 8, 40, 10, 20, "RockDark"),
    ("Pillar1", -48, -48, 18, 14, 14, 40, "RockDark"),
    ("Pillar2", 48, -48, 18, 14, 14, 40, "RockDark"),
]

# trees: (x, y, base_z, scale)
TREES = [
    (-30, -60, 26, 1.4),
    (8, -64, 32, 1.6),
    (42, -60, 24, 1.2),
    (-58, -10, 26, 1.0),
    (58, 5, 26, 1.1),
]

COLORS = {
    "Ground": (0.29, 0.63, 0.27, 1),
    "RockDark": (0.20, 0.23, 0.31, 1),
    "RockTop": (0.66, 0.61, 0.55, 1),
    "RockSide": (0.36, 0.31, 0.27, 1),
    "Cover": (0.20, 0.24, 0.36, 1),
    "Crate": (0.23, 0.55, 0.27, 1),
    "Trunk": (0.18, 0.27, 0.24, 1),
    "Leaf": (0.14, 0.35, 0.31, 1),
    "Debris": (0.08, 0.08, 0.11, 1),
}

def make_mat(name, rgba):
    mat = bpy.data.materials.get("Arena_" + name)
    if mat is None:
        mat = bpy.data.materials.new("Arena_" + name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = rgba
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = 0.85
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 0.0
    return mat

def add_box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    for p in o.data.polygons:
        p.use_smooth = False
    if mat:
        if o.data.materials:
            o.data.materials[0] = mat
        else:
            o.data.materials.append(mat)
    return o

def main():
    col_name = "RockyArena"
    col = bpy.data.collections.get(col_name)
    if col is None:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = \
        bpy.context.view_layer.layer_collection.children[col_name]
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    mats = {k: make_mat(k, v) for k, v in COLORS.items()}

    for (n, x, y, z, sx, sy, sz, m) in BOXES:
        add_box(n, (x, y, z), (sx, sy, sz), mats[m])

    for (x, y, bz, s) in TREES:
        add_box(f"Trunk_{x}_{y}", (x, y, bz + 4*s), (2*s, 2*s, 8*s), mats["Trunk"])
        add_box(f"Canopy_{x}_{y}", (x, y, bz + 9*s), (10*s, 10*s, 2.5*s), mats["Leaf"])
        add_box(f"Canopy2_{x}_{y}", (x+1, y, bz + 10.5*s), (7*s, 7*s, 2*s), mats["Leaf"])

    print(f"Done: {len(col.objects)} objects in {col_name}")

if __name__ == "__main__":
    main()
