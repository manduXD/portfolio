#!/usr/bin/env python3
"""Arena v2 generator: PNG textures + OBJ/MTL with UVs. Run: python arena_v2_gen.py"""
from pathlib import Path
import random, math
random.seed(7)

ROOT = Path(__file__).parent
TEXDIR = ROOT / "arena_textures"
OBJ = ROOT / "low_poly_arena_v2.obj"
MTL = ROOT / "low_poly_arena_v2.mtl"

# (name, x,y,z, sx,sy,sz, mat, rot_z_deg)
B = []
def box(n,x,y,z,sx,sy,sz,m,rot=0):
    B.append((n,x,y,z,sx,sy,sz,m,rot))

# --- ground + paths ---
box("Ground", 0,0,-1, 400,400,2, "Grass")
box("Path_NS", 0,22,0.05, 8,70,0.25, "Stone")
box("Path_E", 32,2,0.05, 56,8,0.25, "Stone")
box("Path_W", -32,4,0.05, 56,8,0.25, "Stone")
box("Path_N", 0,-32,0.05, 8,50,0.25, "Stone")

# --- spawn plaza (south y=50) ---
box("PlazaBase", 0,52,0.5, 32,32,1.0, "RockSide")
box("PlazaTop", 0,52,1.1, 32.4,32.4,0.35, "Stone")
box("Obelisk", 0,52,4.5, 2.4,2.4,6.0, "Slate")
box("ObeliskTop", 0,52,7.8, 3.0,3.0,0.7, "Gold")
box("PlazaFountain", 0,52,1.6, 6,6,0.6, "Slate")
box("PlazaWater", 0,52,1.95, 5,5,0.2, "Water")
for sx, sy in [(-13,39),(13,39),(-13,65),(13,65)]:
    box(f"TorchPole_{sx}_{sy}", sx,sy,2.0, 0.4,0.4,3.0, "Wood")
    box(f"TorchFire_{sx}_{sy}", sx,sy,3.8, 0.7,0.7,0.9, "NeonOrange")
for sx in (-8, 8):
    box(f"BannerPole_{sx}", sx,64,2.5, 0.35,0.35,5.0, "Wood")
    box(f"Banner_{sx}", sx,63.4,4.2, 1.8,0.15,2.2, "NeonPink" if sx<0 else "NeonCyan")

# --- central arena ---
box("MainBase", 0,0,3, 36,28,6, "RockSide")
box("MainTop", 0,0,6.2, 36.4,28.4,0.8, "Stone")
for cx, cy in [(-15,-11),(15,-11),(-15,11),(15,11)]:
    box(f"Tower_{cx}_{cy}", cx,cy,8, 4.5,4.5,10, "RockDark")
    box(f"TowerTop_{cx}_{cy}", cx,cy,13.3, 5.2,5.2,0.7, "Stone")
    box(f"Brazier_{cx}_{cy}", cx,cy,14.1, 1.2,1.2,0.8, "NeonOrange")
box("CoverA1", -8,0,7.3, 8,1.2,2.0, "Slate")
box("CoverA2", 8,0,7.3, 8,1.2,2.0, "Slate")
box("CoverA3", 0,-8,7.3, 1.2,8,2.0, "Slate")
box("JumpPadMid", 0,6,6.95, 3.2,3.2,0.35, "NeonCyan")

# --- east parkour ridge ---
box("ParkStart", 42,2,1, 12,12,2, "RockSide")
box("ParkStartTop", 42,2,2.15, 12.4,12.4,0.3, "Stone")
steps = [(52,6,2.5,7,7,5),(60,-1,4,6,6,8),(68,5,5.5,5.5,5.5,11),(76,-2,7,4.5,4.5,14),(84,4,8.5,4,4,17)]
for i,(x,y,z,sx,sy,sz) in enumerate(steps):
    box(f"ParkStep{i}", x,y,z, sx,sy,sz, "RockSide")
    box(f"ParkStepTop{i}", x,y,z+sz/2+0.15, sx+0.4,sy+0.4,0.3, "Stone")
    box(f"Check{i}", x,y,z+sz/2+0.35, 2,2,0.15, "NeonPink")
box("Beam1", 64,2,6.5, 10,0.7,0.7, "Wood")
box("Beam2", 72,1,8.0, 9,0.7,0.7, "Wood")
box("Pole1", 56,2.5,5.5, 0.7,0.7,6, "Wood")
box("Pole2", 80,1,8.5, 0.7,0.7,7, "Wood")
box("FinishTower", 92,5,6, 9,9,12, "RockDark")
box("FinishTop", 92,5,12.3, 9.6,9.6,0.7, "Stone")
box("FinishFlagPole", 92,5,15, 0.35,0.35,5, "Wood")
box("FinishFlag", 93.1,5,16.5, 2.2,0.15,1.4, "Gold")
box("FinishPad", 92,5,12.8, 3,3,0.3, "NeonCyan")

# --- west canyon ---
box("CanyonWallS", -60,-12,5, 65,3.5,10, "RockDark")
box("CanyonWallN", -60,16,5, 65,3.5,10, "RockDark")
box("CanyonMossS", -60,-10.1,8.5, 65,0.3,1.2, "Grass")
for ax in (-48,-70):
    box(f"ArchP1_{ax}", ax,-8,4, 2.5,2.5,8, "RockDark")
    box(f"ArchP2_{ax}", ax,12,4, 2.5,2.5,8, "RockDark")
    box(f"ArchTop_{ax}", ax,2,8.4, 3,23,1.6, "RockDark")
box("Ledge1", -58,-10,3.5, 4,1.5,1.0, "Stone")
box("Ledge2", -64,14,5.0, 4,1.5,1.0, "Stone")
box("Ledge3", -55,-10,6.0, 3.5,1.5,1.0, "Stone")

# --- north ruins ---
ruins = [(-14,-52,2.5,10,2,5),(-2,-54,3.5,10,2,7),(10,-52,2,10,2,4),(22,-56,3,8,2,6)]
for i,(x,y,z,sx,sy,sz) in enumerate(ruins):
    box(f"Ruin{i}", x,y,z, sx,sy,sz, "RockSide")
    box(f"RuinTop{i}", x,y,z+sz/2+0.12, sx+0.3,sy+0.3,0.25, "Stone")
for i,(x,y) in enumerate([(-18,-62),(-6,-62),(6,-62),(18,-62)]):
    box(f"Column{i}", x,y,4, 2.2,2.2,8, "Stone")
box("ColumnFallen", 0,-66,1.1, 8,2.2,2.2, "Stone")
box("RuinLintel", 0,-62,8.6, 30,2.6,1.4, "Stone")
box("Overlook", 0,-72,2, 24,10,4, "RockSide")
box("OverlookTop", 0,-72,4.15, 24.4,10.4,0.3, "Stone")
box("RailN", 0,-76.8,5.2, 24,0.4,1.6, "Wood")

# --- bridges ---
box("BridgeS_Deck", 0,32,1.2, 6,12,0.5, "Wood")
box("BridgeS_R1", -2.8,32,2.1, 0.4,12,1.4, "Wood")
box("BridgeS_R2", 2.8,32,2.1, 0.4,12,1.4, "Wood")
box("BridgeE_Deck", 26,2,1.2, 10,5,0.5, "Wood")

# --- forest grove (NW) + pond ---
box("PondSand", -46,-34,0.08, 15,13,0.25, "RockTop")
box("Pond", -46,-34,0.25, 13,11,0.25, "Water")
TREES = [(-52,-28,0,1.3,"oak"),(-40,-26,0,1.1,"pine"),(-58,-38,0,1.5,"oak"),
         (-36,-40,0,1.2,"oak"),(-50,-46,0,1.0,"pine"),(-62,-26,0,0.9,"dead"),
         (-30,-30,0,1.4,"pine"),(-56,-48,0,1.1,"oak"),(20,-40,0,1.2,"oak"),
         (-20,-44,0,1.0,"pine"),(60,-30,0,1.3,"oak"),(-80,30,0,1.2,"pine")]
for i,(x,y,bz,s,kind) in enumerate(TREES):
    if kind == "pine":
        box(f"TrunkF{i}", x,y,bz+2*s, 1.2*s,1.2*s,4*s, "Trunk")
        box(f"Pine1_{i}", x,y,bz+4.5*s, 6*s,6*s,2*s, "Leaf")
        box(f"Pine2_{i}", x,y,bz+6*s, 4.5*s,4.5*s,1.8*s, "Leaf")
        box(f"Pine3_{i}", x,y,bz+7.4*s, 3*s,3*s,1.6*s, "Leaf")
    elif kind == "dead":
        box(f"DeadTrunk{i}", x,y,bz+2.5*s, 1.4*s,1.4*s,5*s, "Trunk")
        box(f"Branch{i}", x+1.5*s,y,bz+4*s, 3*s,0.7*s,0.7*s, "Trunk")
    else:
        box(f"TrunkF{i}", x,y,bz+2.5*s, 1.4*s,1.4*s,5*s, "Trunk")
        box(f"CanF{i}", x,y,bz+5.8*s, 7*s,7*s,2.2*s, "Leaf")
        box(f"Can2F{i}", x+1*s,y,bz+7*s, 5*s,5*s,1.8*s, "Leaf")

# --- scatter rocks/bushes/crates/barrels ---
scat = [(-24,20,0.4,2.2,"RockDark",20),(18,24,0.3,1.8,"RockDark",-15),(30,-14,0.5,2.6,"RockSide",35),
        (-16,-24,0.4,2.0,"RockDark",10),(48,-12,0.4,2.4,"RockDark",-30),(8,40,0.3,1.6,"RockSide",0),
        (-70,2,0.5,2.8,"RockDark",15),(24,-30,0.4,2.2,"RockSide",-20)]
for i,(x,y,z,s,m,r) in enumerate(scat):
    box(f"Rock{i}", x,y,z, s,s*0.8,s, m, r)
bush = [(-24,-14),(12,18),(36,20),(-34,-20),(-48,-22),(14,-38),(70,10),(-90,-10)]
for i,(x,y) in enumerate(bush):
    box(f"Bush{i}", x,y,0.6, 2.2,2.2,1.4, "Leaf")
    box(f"Flower{i}", x+0.5,y+0.5,1.4, 0.35,0.35,0.5, "NeonPink" if i%2==0 else "Gold")
crates = [(-6,40),( -4.5,40),(6,58),(44,10),(-52,4),(-56,4),(12,-46)]
for i,(x,y) in enumerate(crates):
    s = 1.8 if i%3 else 2.4
    box(f"Crate{i}", x,y,s/2, s,s,s, "Crate")
for i,(x,y) in enumerate([(-7,41),(45,11),(-53,5.5)]):
    box(f"Barrel{i}", x,y,0.9, 1.4,1.4,1.8, "Wood")

# --- perimeter cliffs (bigger ring) ---
box("CliffB1", -40,-95,13, 60,14,30, "RockDark")
box("CliffB2", 25,-98,16, 70,16,36, "RockDark")
box("CliffL", -100,0,13, 14,220,30, "RockDark")
box("CliffR", 100,0,13, 14,220,30, "RockDark")
box("CliffF1", -45,100,10, 70,14,24, "RockDark")
box("CliffF2", 40,100,10, 70,14,24, "RockDark")
box("PillarN1", -70,-80,20, 16,16,44, "RockDark")
box("PillarN2", 70,-80,20, 16,16,44, "RockDark")
box("FloatIsl", 30,-60,28, 10,10,3, "RockSide")
box("FloatTop", 30,-60,29.6, 10.2,10.2,0.4, "Grass")
box("FloatTree", 30,-60,32, 1.2,1.2,4, "Trunk")
box("FloatLeaf", 30,-60,34.5, 6,6,2, "Leaf")

MAT_COLORS = {
    "Grass": (0.29,0.63,0.27), "Stone": (0.66,0.61,0.55), "RockTop": (0.60,0.55,0.48),
    "RockSide": (0.42,0.36,0.31), "RockDark": (0.24,0.27,0.36),
    "Slate": (0.22,0.26,0.38), "Wood": (0.47,0.33,0.21),
    "Crate": (0.55,0.38,0.22), "Trunk": (0.25,0.18,0.12),
    "Leaf": (0.16,0.42,0.33), "Water": (0.25,0.55,0.85),
    "Gold": (0.95,0.75,0.25), "NeonCyan": (0.1,0.9,1.0),
    "NeonPink": (1.0,0.25,0.6), "NeonOrange": (1.0,0.55,0.15),
}
TEXTURED = {"Grass":"arena_grass.png","Stone":"arena_pavers.png","RockTop":"arena_pavers.png","RockSide":"arena_rock.png",
            "RockDark":"arena_rock_dark.png","Slate":"arena_rock_dark.png","Wood":"arena_wood.png",
            "Leaf":"arena_leaf.png","Crate":"arena_wood.png","Trunk":"arena_wood.png"}

def make_textures():
    from PIL import Image, ImageDraw
    TEXDIR.mkdir(exist_ok=True)
    S = 256
    def grain(base, var=22, dots=900, dotcolor=None):
        img = Image.new("RGB",(S,S),base)
        px = img.load()
        for y in range(S):
            for x in range(S):
                v = random.randint(-var,var)
                r,g,b = base
                px[x,y] = (max(0,min(255,r+v)), max(0,min(255,g+v)), max(0,min(255,b+v)))
        d = ImageDraw.Draw(img)
        for _ in range(dots):
            x,y = random.randrange(S), random.randrange(S)
            c = dotcolor or (max(0,base[0]-40),max(0,base[1]-40),max(0,base[2]-40))
            d.rectangle([x,y,x+2,y+2], fill=c)
        return img
    g = grain((74,160,70), 24, 1200, (45,120,50)); g.save(TEXDIR/"arena_grass.png")
    r = grain((112,104,96), 20, 1000, (70,62,55)); r.save(TEXDIR/"arena_rock.png")
    rd = grain((58,64,88), 16, 900, (35,40,60)); rd.save(TEXDIR/"arena_rock_dark.png")
    w = grain((122,86,54), 18, 400, (90,60,35))
    d = ImageDraw.Draw(w)
    for yy in range(0,S,42): d.line([0,yy,S,yy], fill=(70,45,25), width=3)
    w.save(TEXDIR/"arena_wood.png")
    p = grain((170,158,140), 12, 500, (140,128,110))
    d = ImageDraw.Draw(p)
    for xx in range(0,S,64): d.line([xx,0,xx,S], fill=(120,108,92), width=4)
    for yy in range(0,S,64): d.line([0,yy,S,yy], fill=(120,108,92), width=4)
    p.save(TEXDIR/"arena_pavers.png")
    lf = grain((42,110,84), 26, 1400, (25,80,60)); lf.save(TEXDIR/"arena_leaf.png")
    print("textures:", len(list(TEXDIR.glob('*.png'))))

def write_obj():
    verts, vts, out = [], [], []
    for (n,x,y,z,sx,sy,sz,m,rot) in B:
        hx,hy,hz = sx/2, sy/2, sz/2
        corners = [(x-hx,y-hy,z-hz),(x+hx,y-hy,z-hz),(x+hx,y+hy,z-hz),(x-hx,y+hy,z-hz),
                   (x-hx,y-hy,z+hz),(x+hx,y-hy,z+hz),(x+hx,y+hy,z+hz),(x-hx,y+hy,z+hz)]
        if rot:
            a = math.radians(rot); ca,sa = math.cos(a), math.sin(a)
            corners = [(x+(cx-x)*ca-(cy-y)*sa, y+(cx-x)*sa+(cy-y)*ca, cz) for cx,cy,cz in corners]
        base = len(verts)+1
        verts.extend(corners)
        # faces: (indices, (u_size, v_size))
        faces = [((0,1,2,3),(sx,sy)),((4,5,6,7),(sx,sy)),
                 ((0,1,5,4),(sx,sz)),((1,2,6,5),(sy,sz)),
                 ((2,3,7,6),(sx,sz)),((3,0,4,7),(sy,sz))]
        out.append((n,m,base,faces))
    with open(OBJ,"w") as f:
        f.write("# Arena v2 - Z-up meters, UV tiled every ~4m\nmtllib low_poly_arena_v2.mtl\n")
        for v in verts: f.write(f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}\n")
        vt_idx = 1
        f.write("\n")
        # group by material
        bymat = {}
        for (n,m,base,faces) in out: bymat.setdefault(m,[]).append((n,base,faces))
        for m, items in bymat.items():
            f.write(f"o {m}\nusemtl {m}\n")
            for (n,base,faces) in items:
                for (inds,(du,dv)) in faces:
                    tu = max(1, round(du/4)); tv = max(1, round(dv/4))
                    vts4 = [(0,0),(tu,0),(tu,tv),(0,tv)]
                    ids = []
                    for (vi,(uu,vv)) in zip(inds,vts4):
                        vts.append((uu,vv)); ids.append(f"{base+vi}/{vt_idx}"); vt_idx+=1
                    f.write(f"f {' '.join(ids)} # {n}\n")
        # write vt block at end? NO - must be before faces for strict parsers.
        # Re-read + inject: simpler to prepend vt after verts by rewriting.
    # inject vt lines after verts (rebuild file properly)
    lines = open(OBJ).read().splitlines()
    verts_lines = [l for l in lines if l.startswith("v ")]
    rest = [l for l in lines if not l.startswith("v ") and not l.startswith("#") or l.startswith("mtllib")]
    # vts were collected in order of faces
    header = ["# Arena v2 - Z-up meters, UV tiled every ~4m","mtllib low_poly_arena_v2.mtl"]
    with open(OBJ,"w") as f:
        f.write("\n".join(header)+"\n")
        f.write("\n".join(verts_lines)+"\n")
        for (uu,vv) in vts: f.write(f"vt {uu} {vv}\n")
        # re-emit faces with correct vt indices (they were sequential already)
        bymat = {}
        for (n,m,base,faces) in out: bymat.setdefault(m,[]).append((n,base,faces))
        vi = 1
        for m, items in bymat.items():
            f.write(f"\no {m}\nusemtl {m}\n")
            for (n,base,faces) in items:
                for (inds,(du,dv)) in faces:
                    ids = [f"{base+i}/{vi+k}" for k,i in enumerate(inds)]; vi+=4
                    f.write(f"f {' '.join(ids)} # {n}\n")
    with open(MTL,"w") as f:
        for m,(r,g,b) in MAT_COLORS.items():
            ns = 12 if not (m.startswith("Neon") or m in ("Gold","Water","Glass")) else (120 if m=="Glass" else 150 if m=="Water" else 60 if m=="Gold" else 20)
            f.write(f"newmtl {m}\nKd {r:.3f} {g:.3f} {b:.3f}\nKa 0.08 0.08 0.08\nKs 0.05 0.05 0.05\nNs {ns}\nd 1.0\nillum 2\n")
            if m in TEXTURED: f.write(f"map_Kd arena_textures/{TEXTURED[m]}\n")
            if m.startswith("Neon") or m in ("Gold","Water"):
                f.write(f"Ke {r:.3f} {g:.3f} {b:.3f}\n")
            f.write("\n")
    print(f"WROTE {OBJ.name}: {len(verts)} verts, {len(B)*6} faces, {len(B)} boxes")

if __name__ == "__main__":
    make_textures()
    write_obj()
