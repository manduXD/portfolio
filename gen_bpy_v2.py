#!/usr/bin/env python3
"""Emit low_poly_arena_v2_blender.py from arena_v2_gen (standalone, loads PNG textures)."""
from pathlib import Path
import arena_v2_gen as G

OUT = Path(__file__).parent / "low_poly_arena_v2_blender.py"

header = '''"""
Arena v2 - Blender builder with textures (188 boxes, parkour, forest, ruins).
Blender 3.x/4.x. Run in Scripting tab > Run Script.
Expects folder "arena_textures/" next to this .py (6 PNGs). Falls back to flat colors if missing.
"""
import bpy, os

TEXDIR = os.path.join(os.path.dirname(__file__) if "__file__" in globals() else os.getcwd(), "arena_textures")
TEXMAP = {"Grass":"arena_grass.png","Stone":"arena_pavers.png","RockTop":"arena_pavers.png","RockSide":"arena_rock.png","RockDark":"arena_rock_dark.png","Slate":"arena_rock_dark.png","Wood":"arena_wood.png","Crate":"arena_wood.png","Trunk":"arena_wood.png","Leaf":"arena_leaf.png"}
COLORS = {
 "Grass":(0.29,0.63,0.27,1),"Stone":(0.66,0.61,0.55,1),"RockTop":(0.60,0.55,0.48,1),
 "RockSide":(0.42,0.36,0.31,1),"RockDark":(0.24,0.27,0.36,1),"Slate":(0.22,0.26,0.38,1),
 "Wood":(0.47,0.33,0.21,1),"Crate":(0.55,0.38,0.22,1),"Trunk":(0.25,0.18,0.12,1),
 "Leaf":(0.16,0.42,0.33,1),"Water":(0.25,0.55,0.85,1),"Gold":(0.95,0.75,0.25,1),
 "NeonCyan":(0.1,0.9,1.0,1),"NeonPink":(1.0,0.25,0.6,1),"NeonOrange":(1.0,0.55,0.15,1),
}
EMISSIVE = {"NeonCyan":3.0,"NeonPink":2.5,"NeonOrange":2.5,"Gold":0.4,"Water":0.3}

def make_mat(name):
    mat = bpy.data.materials.get("A2_"+name)
    if mat is None:
        mat = bpy.data.materials.new("A2_"+name)
        mat.use_nodes = True
        nt = mat.node_tree; nodes = nt.nodes; links = nt.links
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial"); out.location=(400,0)
        bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location=(100,0)
        r,g,b,a = COLORS[name]
        bsdf.inputs["Base Color"].default_value=(r,g,b,a)
        if "Roughness" in bsdf.inputs: bsdf.inputs["Roughness"].default_value=0.85 if name not in EMISSIVE else 0.3
        links.new(bsdf.outputs[0], out.inputs[0])
        if name in EMISSIVE:
            bsdf.inputs["Emission Color"].default_value=(r,g,b,1) if hasattr(bsdf.inputs.get("Emission Color",None),"default_value") else None
            try: bsdf.inputs["Emission Strength"].default_value=EMISSIVE[name]
            except: pass
        fn = TEXMAP.get(name)
        if fn:
            fp = os.path.join(TEXDIR, fn)
            if os.path.exists(fp):
                tex = nodes.new("ShaderNodeTexImage"); tex.location=(-300,100)
                try: tex.image = bpy.data.images.load(fp, check_existing=True)
                except: tex.image = None
                if tex.image:
                    tex.image.colorspace_settings.name="sRGB"
                    coord = nodes.new("ShaderNodeTexCoord"); coord.location=(-700,100)
                    mapping = nodes.new("ShaderNodeMapping"); mapping.location=(-500,100)
                    mapping.inputs["Scale"].default_value=(4.0,4.0,4.0)
                    links.new(coord.outputs["UV"], mapping.inputs["Vector"])
                    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
                    mix = nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.location=(-100,150)
                    mix.inputs["Factor"].default_value=0.55
                    mix.inputs[6].default_value=(r,g,b,a)
                    links.new(tex.outputs["Color"], mix.inputs[7])
                    links.new(mix.outputs[2], bsdf.inputs["Base Color"])
                else: nodes.remove(tex)
    return mat

def add_box(name, loc, size, mat, rot_z=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0,0,rot_z))
    o = bpy.context.active_object; o.name=name
    o.scale=size; bpy.ops.object.transform_apply(scale=True)
    for p in o.data.polygons: p.use_smooth=False
    # auto cube-project UVs so PNG tiles nicely
    try:
        bpy.context.view_layer.objects.active=o; bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.cube_project(cube_size=4.0)
        bpy.ops.object.mode_set(mode="OBJECT")
    except: 
        try: bpy.ops.object.mode_set(mode="OBJECT")
        except: pass
    if o.data.materials: o.data.materials[0]=mat
    else: o.data.materials.append(mat)
    return o

BOXES = [
'''

lines = [header]
for (n,bx,by,bz,sx,sy,sz,m,rot) in G.B:
    import math
    lines.append(f' ("{n}", ({bx:.2f},{by:.2f},{bz:.2f}), ({sx:.3f},{sy:.3f},{sz:.3f}), "{m}", {math.radians(rot):.4f}),')
lines.append("]\n")
lines.append('''def main():
    cn="RockyArenaV2"
    col=bpy.data.collections.get(cn)
    if col is None:
        col=bpy.data.collections.new(cn); bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[cn]
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    mats={k:make_mat(k) for k in COLORS}
    for (n,loc,size,m,rz) in BOXES: add_box(n,loc,size,mats[m],rz)
    print(f"Done: {len(col.objects)} objects")
if __name__=="__main__": main()
''')
OUT.write_text("\n".join(lines))
print(f"WROTE {OUT.name}: {len(G.B)} boxes")
