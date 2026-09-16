#!/usr/bin/env python3
"""Generate low_poly_arena.obj + .mtl from box list (no Blender needed)."""
from pathlib import Path

OUT = Path(__file__).parent
OBJ = OUT / "low_poly_arena.obj"
MTL = OUT / "low_poly_arena.mtl"

BOXES = [
    ("Ground", 0, 0, -1, 512, 512, 2, "Ground"),
    ("MainBase", 0, 10, 3, 28, 22, 6, "RockSide"),
    ("MainTop", 0, 10, 6.2, 28.4, 22.4, 0.8, "RockTop"),
    ("Plat_Left", -32, -8, 2, 18, 16, 4, "RockSide"),
    ("Plat_Left_Top", -32, -8, 4.2, 18.4, 16.4, 0.8, "RockTop"),
    ("Plat_Right", 32, 12, 3, 20, 14, 6, "RockSide"),
    ("Plat_Right_Top", 32, 12, 6.2, 20.4, 14.4, 0.8, "RockTop"),
    ("Plat_Back", 0, -32, 2.5, 24, 12, 5, "RockSide"),
    ("Plat_Back_Top", 0, -32, 5.2, 24.4, 12.4, 0.8, "RockTop"),
    ("Plat_FarRight", 38, -18, 1.5, 14, 14, 3, "Cover"),
    ("Cover1", -12, -12, 1.5, 10, 1.5, 3, "Cover"),
    ("Cover2", 14, -6, 1.5, 10, 1.5, 3, "Cover"),
    ("Cover3", -8, 28, 1.5, 8, 1.5, 3, "Cover"),
    ("Cover4", 20, 30, 1.5, 12, 2, 3, "Cover"),
    ("Cover5", -28, 18, 1, 2, 10, 2, "Cover"),
    ("FloatDebris", 18, -8, 14, 6, 2, 1.2, "Debris"),
    ("Crate", -38, 8, 1, 6, 3, 2, "Crate"),
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
TREES = [(-30,-60,26,1.4),(8,-64,32,1.6),(42,-60,24,1.2),(-58,-10,26,1.0),(58,5,26,1.1)]
for (x,y,bz,s) in TREES:
    BOXES.append((f"Trunk_{x}_{y}", x, y, bz+4*s, 2*s, 2*s, 8*s, "Trunk"))
    BOXES.append((f"Canopy_{x}_{y}", x, y, bz+9*s, 10*s, 10*s, 2.5*s, "Leaf"))
    BOXES.append((f"Canopy2_{x}_{y}", x+1, y, bz+10.5*s, 7*s, 7*s, 2*s, "Leaf"))

MAT_COLORS = {
    "Ground": (0.29,0.63,0.27),
    "RockDark": (0.20,0.23,0.31),
    "RockTop": (0.66,0.61,0.55),
    "RockSide": (0.36,0.31,0.27),
    "Cover": (0.20,0.24,0.36),
    "Crate": (0.23,0.55,0.27),
    "Trunk": (0.18,0.27,0.24),
    "Leaf": (0.14,0.35,0.31),
    "Debris": (0.08,0.08,0.11),
}

verts = []  # list of (x,y,z)
faces_by_mat = {}  # mat -> list of (o_name, [idx...])

for (n,x,y,z,sx,sy,sz,m) in BOXES:
    hx, hy, hz = sx/2, sy/2, sz/2
    base = len(verts) + 1  # OBJ 1-indexed
    box_v = [
        (x-hx, y-hy, z-hz),
        (x+hx, y-hy, z-hz),
        (x+hx, y+hy, z-hz),
        (x-hx, y+hy, z-hz),
        (x-hx, y-hy, z+hz),
        (x+hx, y-hy, z+hz),
        (x+hx, y+hy, z+hz),
        (x-hx, y+hy, z+hz),
    ]
    verts.extend(box_v)
    b = base
    quads = [
        (b+0,b+1,b+2,b+3),
        (b+4,b+5,b+6,b+7),
        (b+0,b+1,b+5,b+4),
        (b+1,b+2,b+6,b+5),
        (b+2,b+3,b+7,b+6),
        (b+3,b+0,b+4,b+7),
    ]
    faces_by_mat.setdefault(m, []).extend([(n,q) for q in quads])

with open(OBJ,"w") as f:
    f.write("# Rocky Arena - Blender Z-up, meters\nmtllib low_poly_arena.mtl\n")
    for v in verts:
        f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
    for m, flist in faces_by_mat.items():
        f.write(f"\no {m}\nusemtl {m}\n")
        # merge object names as comments to keep groups readable
        for (oname,q) in flist:
            f.write(f"f {q[0]} {q[1]} {q[2]} {q[3]} # {oname}\n")

with open(MTL,"w") as f:
    for m,(r,g,b) in MAT_COLORS.items():
        f.write(f"newmtl {m}\nKd {r:.3f} {g:.3f} {b:.3f}\nKa 0.1 0.1 0.1\nKs 0.0 0.0 0.0\nNs 12\nd 1.0\nillum 1\n\n")

print(f"WROTE {OBJ.name}: {len(verts)} verts, {sum(len(v) for v in faces_by_mat.values())} faces, {len(BOXES)} boxes")
print(f"WROTE {MTL.name}")
