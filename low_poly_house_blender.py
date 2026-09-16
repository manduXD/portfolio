"""
Low-poly house builder for Blender 3.x / 4.x
Usage in Blender:
  1. Open Blender > Scripting tab
  2. Open this file (low_poly_house_blender.py)
  3. Press Run Script (Alt+P)
  4. Find collection "LowPolyHouse" in the Outliner

No addons required. All quads/tris, flat shaded, real-world scale in meters.
Z-up to match Blender. Edit DIMS below to tweak proportions.
"""

import bpy
import bmesh

# ---------------- settings ----------------
DIMS = {
    "body_w": 4.0,      # X
    "body_d": 3.0,      # Y
    "body_h": 3.0,      # Z
    "roof_overhang": 0.4,
    "roof_h": 1.5,
    "door_w": 1.0,
    "door_h": 1.8,
    "window_s": 0.7,
}

COLORS = {
    "Wall": (0.92, 0.85, 0.70, 1.0),     # warm beige
    "Roof": (0.65, 0.25, 0.18, 1.0),     # brick red
    "Door": (0.35, 0.22, 0.12, 1.0),     # dark wood
    "Window": (0.55, 0.80, 0.92, 1.0),   # light blue
    "Chimney": (0.55, 0.55, 0.58, 1.0),  # grey
    "Trim": (1.0, 1.0, 1.0, 1.0),
}


def make_mat(name, rgba):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = rgba
            # low-poly stylized: high roughness, no metallic
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = 0.8
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def assign_mat(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def flat_shade(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = False


def add_cube(name, location, scale, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    flat_shade(obj)
    if mat:
        assign_mat(obj, mat)
    return obj


def add_roof(name, w, d, base_z, height, overhang, mat):
    """Gable roof, ridge along X axis. Returns object."""
    hw = w / 2.0 + overhang
    hd = d / 2.0 + overhang
    # 6 verts: 4 eaves + 2 ridge
    verts = [
        (-hw, -hd, base_z),  # 0 front-left eave
        (hw, -hd, base_z),   # 1 front-right eave
        (hw, hd, base_z),    # 2 back-right eave
        (-hw, hd, base_z),   # 3 back-left eave
        (-hw, 0, base_z + height),  # 4 left ridge
        (hw, 0, base_z + height),   # 5 right ridge
    ]
    faces = [
        (0, 1, 5, 4),  # front slope
        (2, 3, 4, 5),  # back slope
        (0, 4, 3),     # left gable triangle
        (1, 2, 5),     # right gable triangle
        (0, 3, 2, 1),  # underside (closes solid, hidden)
    ]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    flat_shade(obj)
    if mat:
        assign_mat(obj, mat)
    return obj


def main():
    # collection
    col_name = "LowPolyHouse"
    col = bpy.data.collections.get(col_name)
    if col is None:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = \
        bpy.context.view_layer.layer_collection.children[col_name]

    # clear previous in collection (re-runnable)
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    mats = {k: make_mat("LP_" + k, v) for k, v in COLORS.items()}

    w = DIMS["body_w"]
    d = DIMS["body_d"]
    h = DIMS["body_h"]

    # body
    body = add_cube("Body", (0, 0, h / 2), (w, d, h), mats["Wall"])
    # move to our collection if created elsewhere
    if body.name not in col.objects:
        bpy.context.scene.collection.objects.unlink(body)
        col.objects.link(body)

    # roof
    roof = add_roof("Roof", w, d, h, DIMS["roof_h"], DIMS["roof_overhang"], mats["Roof"])
    # add_roof already links to active collection (LowPolyHouse)

    # door (front face, +Y)
    door = add_cube(
        "Door",
        (0, d / 2 + 0.05, DIMS["door_h"] / 2),
        (DIMS["door_w"], 0.1, DIMS["door_h"]),
        mats["Door"],
    )

    # door step
    step = add_cube("Step", (0, d / 2 + 0.25, 0.1), (1.4, 0.5, 0.2), mats["Trim"])

    # windows front
    ws = DIMS["window_s"]
    wz = 1.9
    for wx in (-1.2, 1.2):
        add_cube(f"Window_Front_{wx}", (wx, d / 2 + 0.03, wz), (ws, 0.06, ws), mats["Window"])

    # windows back
    for wx in (-1.2, 1.2):
        add_cube(f"Window_Back_{wx}", (wx, -d / 2 - 0.03, wz), (ws, 0.06, ws), mats["Window"])

    # windows sides
    for wy in (0,):
        add_cube("Window_Left", (-w / 2 - 0.03, wy, wz), (0.06, ws, ws), mats["Window"])
        add_cube("Window_Right", (w / 2 + 0.03, wy, wz), (0.06, ws, ws), mats["Window"])

    # chimney (sits on back slope)
    add_cube("Chimney", (1.2, 0.5, h + 1.0), (0.5, 0.5, 1.6), mats["Chimney"])

    print(f"Done: {len(col.objects)} objects in '{col_name}'")
    print("Tip: Select all in collection > File > Export > FBX/OBJ for game engines.")


if __name__ == "__main__":
    main()
