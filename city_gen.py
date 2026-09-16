#!/usr/bin/env python3
"""City v1: 600x600 waterfront blocky city. Run: python city_gen.py
Generates: PNG textures, OBJ+MTL (matte Ns), Roblox Lua, Blender bpy."""
from pathlib import Path
import random, math
random.seed(99)

ROOT = Path(__file__).parent
TEXDIR = ROOT / "city_textures"
OBJ = ROOT / "low_poly_city.obj"
MTL = ROOT / "low_poly_city.mtl"
LUA = ROOT / "city_map_builder.lua"
BPY = ROOT / "low_poly_city_blender.py"

B = []
def box(n,x,y,z,sx,sy,sz,m,rx=0,ry=0,rz=0,uv=None):
    B.append((n,x,y,z,sx,sy,sz,m,rx,ry,rz,uv))

def euler_bake(x,y,z, cx,cy,cz, rx,ry,rz):
    """Rotate point around center by XYZ euler degrees. Single-axis use is exact."""
    px,py,pz = x-cx, y-cy, z-cz
    ax,ay,az = math.radians(rx), math.radians(ry), math.radians(rz)
    # X
    c,s = math.cos(ax), math.sin(ax); py,pz = py*c-pz*s, py*s+pz*c
    # Y
    c,s = math.cos(ay), math.sin(ay); px,pz = px*c+pz*s, -px*s+pz*c
    # Z
    c,s = math.cos(az), math.sin(az); px,py = px*c-py*s, px*s+py*c
    return (px+cx, py+cy, pz+cz)

# ============ GROUND / WATER / BEACH ============
box("Ground", 0,-90,-1, 600,430,2, "Concrete")
box("Water", 0,210, -0.1, 600,190,0.5, "Water")
box("Sand", 0,112,0.1, 600,26,0.3, "Sand")
box("Seawall", 0,124,0.6, 600,2,1.4, "Stone")
box("Boardwalk", 0,102,0.75, 600,14,0.3, "Wood", uv=(150,4))

# ============ ROADS (avenues E-W, streets N-S) ============
AVES = [-200,-120,-40,40]
STS = [-200,-120,-40,40,120,200]
for ay in AVES:
    box(f"Ave_{ay}", 0,ay,0.22, 600,10,0.2, "Asphalt", uv=(150,1))
for sx in STS:
    box(f"St_{sx}", sx,-90,0.26, 10,430,0.2, "Asphalt", uv=(1,108))
# crosswalks near center
for cx,cy in [(-40,-40),(40,-40),(-40,40),(40,40)]:
    for k in range(5):
        box(f"Cross_{cx}_{cy}_{k}", cx-4+k*2,cy,0.40, 1.1,7,0.06, "Cream")

# ============ CITY BLOCKS: towers with setbacks ============
FACS = ["FacadeA","FacadeB","FacadeGlass"]
def tower(p,x,y,w,d,tiers,fac,heli=False):
    z=0.3
    # glass lobby
    box(f"{p}_Lobby", x,y,z+2, w*0.96,d*0.96,4, "Glass")
    box(f"{p}_Canopy", x,y+d/2+1.2,z+3.2, w*0.5,2.6,0.3, "Stone")
    z+=4
    cw,cd=w,d
    for i,h in enumerate(tiers):
        box(f"{p}_T{i}", x,y,z+h/2, cw,cd,h, fac)
        z+=h; cw*=0.84; cd*=0.84
    box(f"{p}_Par", x,y,z+0.4, cw+1.4,cd+1.4,0.9, "RoofGrey")
    if heli:
        box(f"{p}_Heli", x,y,z+1.05, 12,12,0.4, "Asphalt")
        box(f"{p}_H1", x,y,z+1.28, 6,1.0,0.08, "Gold")
        box(f"{p}_H2", x,y-2.4,z+1.28, 1.0,5.8,0.08, "Gold")
        box(f"{p}_H3", x,y+2.4,z+1.28, 1.0,5.8,0.08, "Gold")
    else:
        box(f"{p}_AC", x+cw*0.2,y,z+1.1, 2.4,2.4,1.3, "RoofGrey")
        box(f"{p}_AC2", x-cw*0.22,y+cd*0.15,z+1.0, 1.8,1.8,1.1, "RoofGrey")
        if max(w,d)>=20:
            box(f"{p}_Ant", x,y,z+4, 0.5,0.5,8, "Slate")
            box(f"{p}_Beacon", x,y,z+8.2, 0.9,0.9,0.9, "Beacon")
    return z

# hero supertall + tall cluster (center-north)
tower("Hero", 0,-80, 30,26, [34,30,26,20], "FacadeGlass", heli=True)
tower("Tall2", -75,-75, 24,22, [28,24,20], "FacadeA")
tower("Tall3", 78,-78, 22,24, [26,22,18], "FacadeB")
tower("Tall4", -78,10, 24,20, [24,20,16], "FacadeGlass")
tower("Tall5", 80,8, 20,24, [26,20], "FacadeA")
# mid blocks (seeded variety; (-160,-160) is the park, (0,0) is the retail block)
blocks=[( -80,-160,22,20,2),(0,-160,18,18,2),(80,-160,20,20,3),(160,-160,18,16,2),
        (-160,-80,22,18,3),(160,-80,20,18,2),(160,0,18,20,2),(160,80,20,18,2),
        (-160,0,18,18,2),(-160,80,20,20,2),(-80,80,18,18,2),(0,80,20,18,2),(80,80,18,18,2),
        (-80,0,16,16,2)]
for i,(bx,by,w,d,nt) in enumerate(blocks):
    tiers=[random.randint(12,20) for _ in range(nt)]
    tower(f"B{i}", bx,by, w,d, tiers, FACS[i%3])

# ============ RETAIL ROW (south of center, shops + signs) ============
for i,rx in enumerate([-60,-36,-12,12,36,60]):
    box(f"Shop{i}_Base", rx,-4,2.2, 20,12,4.4, "Plaster")
    box(f"Shop{i}_Trim", rx,-4,4.6, 20.4,12.4,0.4, "Stone")
    box(f"Shop{i}_Glass", rx,2.15,1.9, 16,0.2,2.6, "Glass")
    for k in range(5):
        c="Cream" if (k+i)%2==0 else "Roof"
        box(f"Shop{i}_Aw{k}", rx-4+k*2,3.1,3.6, 2.0,1.6,0.15, c)
    box(f"Shop{i}_Sign", rx,-4,5.6, 8,0.4,1.4, f"Ad{(i%4)+1}", uv="face")

# ============ BILLBOARDS ============
def billboard(p,x,y,z,w,h,ad,along):
    if along=="x":
        box(f"{p}_Pole", x,y,z/2, 1.2,1.2,z, "Slate")
        box(f"{p}_Frame", x,y,z, w+1,h+1,0.6, "Slate")
        box(f"{p}_Face", x,y+0.35,z, w,h,0.2, ad, uv="face")
    else:
        box(f"{p}_Pole", x,y,z/2, 1.2,1.2,z, "Slate")
        box(f"{p}_Frame", x,y,z, 0.6,h+1,w+1, "Slate")
        box(f"{p}_Face", x+0.35,y,z, 0.2,h,w, ad, uv="face")
billboard("BB1", -135,-55,26, 16,9, "Ad1","x")
billboard("BB2", 135,55,30, 18,10, "Ad2","x")
billboard("BB3", -60,-160,24, 16,9, "Ad3","x")
billboard("BB4", -185,65,22, 14,8, "Ad4","y")
billboard("BB5", 185,-100,26, 16,9, "Ad1","y")
billboard("BB6", 60,60,20, 12,7, "Ad2","x")
billboard("BB7", -75,-52,44, 12,7, "Ad3","x")
billboard("BB8", 78,-56,40, 12,7, "Ad4","x")

# ============ PIER + FERRIS WHEEL (x=-40, extends south) ============
box("PierDeck", -40,150,0.9, 26,72,0.5, "Wood")
for px in (-51,-40,-29):
    for py in range(118,186,8):
        box(f"Pile_{px}_{py}", px,py,-0.2, 0.8,0.8,2.6, "Trunk")
box("PierRail1", -52.5,150,2.0, 0.4,72,1.2, "Wood")
box("PierRail2", -27.5,150,2.0, 0.4,72,1.2, "Wood")
box("PierShop", -40,128,3.0, 14,10,4.0, "Plaster")
box("PierRoof1", -40,128,5.4, 15,11,0.8, "Roof")
box("PierRoof2", -40,128,6.2, 10,11,0.8, "Roof")
box("Ticket", -48,140,2.0, 4,4,2.6, "Wood")
box("TicketTop", -48,140,3.5, 4.6,4.6,0.4, "Roof")
# wheel: hub (-40,172,14), R=10, plane XZ (rotate about Y)
HX,HY,HZ,R = -40,172,14,10
box("WheelLeg1", HX-4,HY,7, 1.2,1.2,13, "WheelRed", ry=12)
box("WheelLeg2", HX+4,HY,7, 1.2,1.2,13, "WheelRed", ry=-12)
box("WheelAxle", HX,HY,HZ, 3,3,3, "Slate")
for k in range(8):
    ang = k*22.5
    c = "WheelRed" if k%2==0 else "WheelGreen"
    box(f"Spoke{k}", HX,HY,HZ, 0.5,0.5,2*R, c, ry=ang)
    ex = HX + R*math.sin(math.radians(ang)); ez = HZ + R*math.cos(math.radians(ang))
    box(f"Cabin{k}", ex,HY,ez, 2.2,2.2,2.2, "Cabin", ry=ang)
for k in range(16):
    a0=k*22.5; a1=(k+1)*22.5; mid=(a0+a1)/2
    mx=HX+R*0.98*math.sin(math.radians(mid)); mz=HZ+R*0.98*math.cos(math.radians(mid))
    box(f"Rim{k}", mx,HY,mz, 0.4,0.4,4.0, "Cream", ry=mid)

# ============ MARINA (east): docks + boats ============
for d,dx in enumerate([60,100,140]):
    box(f"Dock{d}", dx,155,0.7, 5,60,0.4, "Wood")
    for py in range(130,182,10):
        box(f"DockP{d}_{py}", dx,py,-0.2, 0.6,0.6,2.2, "Trunk")
def boat(p,x,y,c):
    box(f"{p}_Hull", x,y,0.6, 4,10,1.6, c)
    box(f"{p}_Bow", x,y+6,0.9, 2.6,3,1.2, c)
    box(f"{p}_Cab", x,y-1,2.0, 2.6,4,1.8, "Cream")
    box(f"{p}_Mast", x,y+1,4.2, 0.25,0.25,4.5, "Trunk")
boat("Boat1", 70,160,"Roof"); boat("Boat2", 112,150,"FacadeB"); boat("Boat3", 150,165,"WheelGreen")
# beach umbrellas
for i,(ux,uy,c) in enumerate([(-120,110,"Ad1"),(-100,108,"Ad2"),(180,110,"Ad4"),(200,108,"Ad3")]):
    box(f"UmbP{i}", ux,uy,1.2, 0.25,0.25,2.4, "Trunk")
    box(f"UmbT{i}", ux,uy,2.7, 3.4,3.4,0.5, c)
    box(f"UmbT2_{i}", ux,uy,3.1, 2.0,2.0,0.5, c)

# ============ BRIDGE (far east over water) ============
box("BridgeDeck", 250,215,6, 120,10,1.5, "Concrete")
box("BridgeR1", 250,210.5,7.2, 120,0.5,1.6, "Concrete")
box("BridgeR2", 250,219.5,7.2, 120,0.5,1.6, "Concrete")
for px in (210,290):
    box(f"Pylon{px}", px,215,14, 3,3,26, "Slate")
    for s in (-1,1):
        for k in (1,2):
            box(f"Cable{px}_{s}_{k}", px+s*12*k,215,12-k*2, 0.3,0.3,10, "Cream", ry=s*28)

# ============ PARK BLOCK (x -160..-80? use block at (-120,-120) area) ============
box("ParkGrass", -160,-160,0.1, 56,56,0.25, "Grass")
box("ParkPath1", -160,-160,0.45, 56,4,0.1, "Stone")
box("ParkPath2", -160,-160,0.50, 4,56,0.1, "Stone")
box("ParkFount", -160,-160,0.7, 8,8,1.2, "Stone")
box("ParkWater", -160,-160,1.3, 7,7,0.2, "Water")
box("ParkOb", -160,-160,2.6, 1.2,1.2,1.8, "Stone")

# ============ PARKING LOT + CARS ============
box("ParkLot", 120,-160,0.15, 60,56,0.2, "Concrete")
for k in range(7):
    box(f"LotLine{k}", 95+k*8,-160,0.28, 0.4,40,0.05, "Cream")
def car(p,x,y,rot,c):
    box(f"{p}_Body", x,y,0.9, 4.6,2.2,1.0, c, rz=rot)
    box(f"{p}_Top", x,y,1.85, 2.4,2.0,0.9, "Glass", rz=rot)
    for wx,wy in [(-1.5,-1.0),(1.5,-1.0),(-1.5,1.0),(1.5,1.0)]:
        a=math.radians(rot)
        box(f"{p}_W{wx}_{wy}", x+wx*math.cos(a)-wy*math.sin(a), y+wx*math.sin(a)+wy*math.cos(a), 0.45, 0.9,0.9,0.9, "Slate")
car("Car1", 99,-170,0,"Roof"); car("Car2", 107,-150,0,"FacadeB"); car("Car3", 123,-170,90,"Gold")
car("Car4", 131,-150,90,"WheelRed"); car("Car5", 139,-170,0,"Cream"); car("Car6", 147,-150,0,"Slate")

# ============ STREET LAMPS + TREES/PLANTERS ============
lid=0
for ay in AVES:
    for sx in STS:
        for ox,oy in [(-8,8),(8,-8)]:
            box(f"LampP{lid}", sx+ox,ay+oy,1.8, 0.35,0.35,3.6, "Slate"); box(f"LampH{lid}", sx+ox,ay+oy,3.8, 0.8,0.8,0.8, "LampGlow"); lid+=1
for i in range(12):
    box(f"Bollard{i}", -20+i*4,96,0.9, 0.5,0.5,1.0, "Gold")
tid=0
def street_tree(x,y):
    global tid
    box(f"ST_T{tid}", x,y,1.2, 0.9,0.9,2.4, "Trunk")
    box(f"ST_C{tid}", x,y,3.2, 3.4,3.4,2.0, "Leaf"); tid+=1
for sx in STS:
    street_tree(sx-9,60); street_tree(sx+9,-100)
for ay in AVES:
    street_tree(-60,ay+9); street_tree(60,ay-9)
for i,(x,y,s) in enumerate([(-160,-160,1.2),(-150,-170,1.0),(-170,-150,1.1),(120,120,1.2)]):
    box(f"BigT{i}", x,y,2*s, 1.2*s,1.2*s,4*s, "Trunk")
    box(f"BigC{i}", x,y,5*s, 6*s,6*s,2.4*s, "Leaf")

MAT_COLORS = {
 "Concrete":(0.55,0.56,0.60),"Stone":(0.66,0.61,0.55),"Cream":(0.95,0.91,0.79),
 "Asphalt":(0.16,0.17,0.20),"Slate":(0.23,0.27,0.39),"RoofGrey":(0.42,0.43,0.47),
 "FacadeA":(0.62,0.60,0.58),"FacadeB":(0.52,0.44,0.38),"FacadeGlass":(0.35,0.52,0.68),
 "Glass":(0.55,0.78,0.90),"Plaster":(0.93,0.88,0.76),"Roof":(0.62,0.26,0.18),
 "Trunk":(0.26,0.19,0.12),"Wood":(0.55,0.40,0.24),"Leaf":(0.16,0.42,0.30),
 "Grass":(0.30,0.62,0.28),"Sand":(0.87,0.78,0.58),"Water":(0.15,0.45,0.80),
 "Gold":(0.95,0.75,0.25),"Beacon":(1.0,0.25,0.25),"LampGlow":(1.0,0.80,0.45),
 "WheelRed":(0.80,0.15,0.15),"WheelGreen":(0.12,0.60,0.30),"Cabin":(0.95,0.90,0.70),
 "Ad1":(0.85,0.15,0.20),"Ad2":(0.05,0.65,0.85),"Ad3":(0.55,0.25,0.75),"Ad4":(0.10,0.65,0.35),
}
TEXTURED = {"Concrete":"city_pavers.png","Stone":"city_pavers.png","Cream":"city_plaster.png",
 "Asphalt":"city_asphalt.png","FacadeA":"city_facadeA.png","FacadeB":"city_facadeB.png",
 "FacadeGlass":"city_facadeGlass.png","Glass":"city_facadeGlass.png","Plaster":"city_plaster.png",
 "Roof":"city_roof.png","Wood":"city_wood.png","Leaf":"city_leaf.png","Grass":"city_grass.png",
 "Sand":"city_plaster.png","Water":"city_water.png","RoofGrey":"city_roofgrey.png",
 "Ad1":"city_ad1.png","Ad2":"city_ad2.png","Ad3":"city_ad3.png","Ad4":"city_ad4.png"}

def make_textures():
    from PIL import Image, ImageDraw
    TEXDIR.mkdir(exist_ok=True); S=256
    def grain(base,var=18,dots=700,dot=None):
        img=Image.new("RGB",(S,S),base); px=img.load()
        for yy in range(S):
            for xx in range(S):
                v=random.randint(-var,var); r,g,b=base
                px[xx,yy]=(max(0,min(255,r+v)),max(0,min(255,g+v)),max(0,min(255,b+v)))
        d=ImageDraw.Draw(img)
        for _ in range(dots):
            x,y=random.randrange(S),random.randrange(S)
            c=dot or (max(0,base[0]-36),max(0,base[1]-36),max(0,base[2]-36))
            d.rectangle([x,y,x+2,y+2],fill=c)
        return img
    grain((76,158,72),24,1100,(46,118,50)).save(TEXDIR/"city_grass.png")
    grain((148,150,158),12,400,(120,122,130)).save(TEXDIR/"city_pavers.png")
    grain((120,120,128),14,400,(92,92,100)).save(TEXDIR/"city_roofgrey.png")
    grain((158,66,46),14,350,(120,45,30)).save(TEXDIR/"city_roof.png")
    grain((140,102,62),16,350,(108,74,40)).save(TEXDIR/"city_wood.png")
    grain((236,224,194),10,250,(214,200,170)).save(TEXDIR/"city_plaster.png")
    grain((44,108,78),24,1200,(26,78,56)).save(TEXDIR/"city_leaf.png")
    w=grain((38,110,190),22,700,(25,80,150)); w.save(TEXDIR/"city_water.png")
    # asphalt with center dashes along U
    a=grain((44,46,52),8,300,(30,32,38)); d=ImageDraw.Draw(a)
    d.rectangle([0,8,S,14],fill=(220,220,220)); d.rectangle([0,S-14,S,S-8],fill=(220,220,220))
    for xx in range(10,S,64): d.rectangle([xx,S//2-4,xx+32,S//2+4],fill=(230,190,60))
    a.save(TEXDIR/"city_asphalt.png")
    # facades
    def facade(base,win,lit,floors=8,cols=6):
        img=Image.new("RGB",(S,S),base); d=ImageDraw.Draw(img)
        cw,ch=S//cols,S//floors
        for r in range(floors):
            for c in range(cols):
                x0,y0=c*cw+4,r*ch+4; x1,y1=(c+1)*cw-4,(r+1)*ch-4
                col=lit if random.random()<0.10 else win
                d.rectangle([x0,y0,x1,y1],fill=col)
        return img
    facade((150,150,156),(38,58,88),(255,220,150)).save(TEXDIR/"city_facadeA.png")
    facade((132,112,96),(40,60,92),(255,220,150)).save(TEXDIR/"city_facadeB.png")
    g=facade((70,110,150),(45,80,125),(200,230,255),floors=10,cols=8)
    d=ImageDraw.Draw(g)
    for yy in range(0,S,26): d.line([0,yy,S,yy],fill=(200,225,245),width=2)
    g.save(TEXDIR/"city_facadeGlass.png")
    # billboard ads (bold abstract)
    def ad(bg,fg,style):
        img=Image.new("RGB",(S,S),bg); d=ImageDraw.Draw(img)
        if style==0:
            d.ellipse([S//4,S//5,3*S//4,4*S//5],fill=fg); d.rectangle([0,0,S,30],fill=(255,255,255))
        elif style==1:
            d.polygon([(S//2,20),(S-30,S-30),(30,S-30)],fill=fg); d.rectangle([0,S-50,S,S-20],fill=(255,220,60))
        elif style==2:
            for k in range(4): d.rectangle([20,30+k*55,S-20,60+k*55],fill=fg if k%2==0 else (255,255,255))
        else:
            d.rectangle([0,S//3,S,2*S//3],fill=fg); d.ellipse([S//3,S//4,2*S//3,3*S//4],fill=(255,255,255))
        return img
    ad((200,30,45),(255,255,255),0).save(TEXDIR/"city_ad1.png")
    ad((10,140,200),(255,255,255),1).save(TEXDIR/"city_ad2.png")
    ad((110,50,160),(255,255,255),2).save(TEXDIR/"city_ad3.png")
    ad((20,150,90),(255,255,255),3).save(TEXDIR/"city_ad4.png")
    print("textures:",len(list(TEXDIR.glob("*.png"))))

def write_obj():
    verts=[]; items=[]
    for (n,x,y,z,sx,sy,sz,m,rx,ry,rz,uv) in B:
        hx,hy,hz=sx/2,sy/2,sz/2
        corners=[(x-hx,y-hy,z-hz),(x+hx,y-hy,z-hz),(x+hx,y+hy,z-hz),(x-hx,y+hy,z-hz),
                 (x-hx,y-hy,z+hz),(x+hx,y-hy,z+hz),(x+hx,y+hy,z+hz),(x-hx,y+hy,z+hz)]
        if rx or ry or rz:
            corners=[euler_bake(cx,cy,cz,x,y,z,rx,ry,rz) for cx,cy,cz in corners]
        base=len(verts)+1; verts.extend(corners)
        faces=[((0,1,2,3),(sx,sy)),((4,5,6,7),(sx,sy)),((0,1,5,4),(sx,sz)),
               ((1,2,6,5),(sy,sz)),((2,3,7,6),(sx,sz)),((3,0,4,7),(sy,sz))]
        items.append((n,m,base,faces,uv))
    lines=[f"# City v1 waterfront 600x600, {len(B)} boxes","mtllib low_poly_city.mtl"]
    lines+=[f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}" for v in verts]
    vts=[]
    bymat={}
    for (n,m,base,faces,uv) in items: bymat.setdefault(m,[]).append((n,base,faces,uv))
    for m,lst in bymat.items():
        for (n,base,faces,uv) in lst:
            for (inds,(du,dv)) in faces:
                if uv=="face": tu,tv=1,1
                elif isinstance(uv,tuple): tu,tv=uv
                else: tu,tv=max(1,round(du/4)),max(1,round(dv/4))
                for (uu,vv) in [(0,0),(tu,0),(tu,tv),(0,tv)]: vts.append((uu,vv))
    lines+=[f"vt {u} {v}" for (u,v) in vts]
    vi=1
    for m,lst in bymat.items():
        lines.append(f"o {m}"); lines.append(f"usemtl {m}")
        for (n,base,faces,uv) in lst:
            for (inds,(du,dv)) in faces:
                ids=[f"{base+i}/{vi+k}" for k,i in enumerate(inds)]; vi+=4
                lines.append(f"f {' '.join(ids)} # {n}")
    OBJ.write_text("\n".join(lines)+"\n")
    NSMAT={"Glass":120,"Water":150,"FacadeGlass":80,"Beacon":20,"LampGlow":20,
           "Ad1":20,"Ad2":20,"Ad3":20,"Ad4":20,"Gold":60}
    with open(MTL,"w") as f:
        for m,(r,g,b) in MAT_COLORS.items():
            f.write(f"newmtl {m}\nKd {r:.3f} {g:.3f} {b:.3f}\nKa 0.08 0.08 0.08\nKs 0.05 0.05 0.05\nNs {NSMAT.get(m,12)}\nd {0.7 if m=='Water' else 1.0}\nillum 2\n")
            if m in TEXTURED: f.write(f"map_Kd city_textures/{TEXTURED[m]}\n")
            if m in ("LampGlow","Beacon","Gold","Ad1","Ad2","Ad3","Ad4"): f.write(f"Ke {r:.3f} {g:.3f} {b:.3f}\n")
            f.write("\n")
    print(f"WROTE {OBJ.name}: {len(verts)} verts, {len(B)*6} faces, {len(B)} boxes")

RMAT={"Concrete":"Concrete","Stone":"Cobblestone","Cream":"Limestone","Asphalt":"Asphalt",
 "Slate":"Slate","RoofGrey":"Concrete","FacadeA":"Concrete","FacadeB":"Brick","FacadeGlass":"Glass",
 "Glass":"Glass","Plaster":"Limestone","Roof":"Brick","Trunk":"Wood","Wood":"WoodPlanks",
 "Leaf":"Grass","Grass":"Grass","Sand":"Sand","Water":"Water","Gold":"Metal","Beacon":"Neon",
 "LampGlow":"Neon","WheelRed":"SmoothPlastic","WheelGreen":"SmoothPlastic","Cabin":"SmoothPlastic",
 "Ad1":"Neon","Ad2":"Neon","Ad3":"Neon","Ad4":"Neon"}

def write_lua():
    L=["-- City v1 Builder 600x600 waterfront. Command Bar paste > Enter. Map -> Workspace > CityV1",
     'local W=game:GetService("Workspace") local L=game:GetService("Lighting")',
     'local old=W:FindFirstChild("CityV1") if old then old:Destroy() end',
     'local map=Instance.new("Folder") map.Name="CityV1" map.Parent=W',
     'local function P(n,x,y,z,sx,sy,sz,col,mat,rx,ry,rz,anchor,collide,transp)',
     ' local p=Instance.new("Part") p.Name=n p.Position=Vector3.new(x,y,z) p.Size=Vector3.new(sx,sy,sz)',
     ' p.Color=col p.Material=mat p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth',
     ' if (rx or 0)~=0 or (ry or 0)~=0 or (rz or 0)~=0 then p.Orientation=Vector3.new(rx or 0,ry or 0,rz or 0) end',
     ' p.Anchored=(anchor==nil) and true or anchor p.CanCollide=(collide==nil) and true or collide',
     ' if transp then p.Transparency=transp end p.Parent=map return p end',
     'local C=function(r,g,b) return Color3.fromRGB(r,g,b) end']
    for (n,bx,by,bz,sx,sy,sz,m,rx,ry,rz,uv) in B:
        r,g,b=[int(c*255) for c in MAT_COLORS[m]]
        extra=""
        if m=="Water": extra=",0,0,0, true, false, 0.35"
        elif m=="Glass": extra=",0,0,0, true, true, 0.25"
        elif m=="FacadeGlass": extra=",0,0,0, true, true, 0.1"
        if m=="Water": L.append(f'P("{n}", {bx:.2f},{bz:.2f},{by:.2f}, {sx:.2f},{sz:.2f},{sy:.2f}, C({r},{g},{b}), Enum.Material.{RMAT.get(m,"Rock")}, 0,0,0{extra})')
        else: L.append(f'P("{n}", {bx:.2f},{bz:.2f},{by:.2f}, {sx:.2f},{sz:.2f},{sy:.2f}, C({r},{g},{b}), Enum.Material.{RMAT.get(m,"Rock")}, {rx},{ry},{rz}{extra})')
    L+=['for _,o in ipairs(map:GetChildren()) do local n=o.Name if n:find("LampH") or n:find("Beacon") then local l=Instance.new("PointLight") l.Color=Color3.fromRGB(255,200,120) l.Brightness=2 l.Range=30 l.Parent=o end end',
     'local s1=Instance.new("SpawnLocation") s1.Position=Vector3.new(0,3,60) s1.Size=Vector3.new(6,1,6) s1.Anchored=true s1.Neutral=true s1.Duration=0 s1.Parent=map',
     'L.ClockTime=14.5 L.Brightness=2.6 L.Ambient=Color3.fromRGB(100,105,120) L.OutdoorAmbient=Color3.fromRGB(135,150,180) L.FogColor=Color3.fromRGB(150,185,225) L.FogStart=200 L.FogEnd=1200 L.GlobalShadows=true',
     'local a=L:FindFirstChild("CityAtmo") if not a then a=Instance.new("Atmosphere") a.Name="CityAtmo" a.Parent=L end',
     'a.Density=0.25 a.Offset=0.35 a.Color=Color3.fromRGB(190,210,240) a.Decay=Color3.fromRGB(120,140,190) a.Glare=0.15 a.Haze=1',
     'print("CityV1 built: "..#map:GetChildren().." parts")']
    LUA.write_text("\n".join(L))
    print(f"WROTE {LUA.name}: {len(L)} lines")

def write_bpy():
    H='"""City v1 Blender builder. Scripting > Run. Needs city_textures/ next to it. Z > Material Preview."""\nimport bpy,os,math\n'
    H+='TEXDIR=os.path.join(os.path.dirname(__file__) if "__file__" in globals() else os.getcwd(),"city_textures")\n'
    H+='TEXMAP='+repr({k:v for k,v in TEXTURED.items()})+'\n'
    H+='COLORS='+repr({k:(r,g,b,1) for k,(r,g,b) in MAT_COLORS.items()})+'\n'
    H+='EMISSIVE={"LampGlow":3.0,"Beacon":4.0,"Gold":0.5,"Ad1":1.2,"Ad2":1.2,"Ad3":1.2,"Ad4":1.2}\n'
    H+='''def make_mat(name):
    mat=bpy.data.materials.get("C_"+name)
    if mat is None:
        mat=bpy.data.materials.new("C_"+name); mat.use_nodes=True
        nt=mat.node_tree; nodes=nt.nodes; links=nt.links; nodes.clear()
        out=nodes.new("ShaderNodeOutputMaterial"); out.location=(400,0)
        bsdf=nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location=(100,0)
        r,g,b,a=COLORS[name]; bsdf.inputs["Base Color"].default_value=(r,g,b,a)
        try: bsdf.inputs["Roughness"].default_value=0.85
        except: pass
        links.new(bsdf.outputs[0],out.inputs[0])
        if name=="Water":
            try:
                bsdf.inputs["Alpha"].default_value=0.75
                mat.blend_method="BLEND"
            except: pass
        if name in EMISSIVE:
            try:
                bsdf.inputs["Emission Color"].default_value=(r,g,b,1)
                bsdf.inputs["Emission Strength"].default_value=EMISSIVE[name]
            except: pass
        fn=TEXMAP.get(name)
        if fn:
            import os as _os
            fp=_os.path.join(TEXDIR,fn)
            if _os.path.exists(fp):
                tex=nodes.new("ShaderNodeTexImage"); tex.location=(-300,100)
                try: tex.image=bpy.data.images.load(fp,check_existing=True)
                except: tex.image=None
                if tex.image:
                    tex.image.colorspace_settings.name="sRGB"
                    coord=nodes.new("ShaderNodeTexCoord"); coord.location=(-700,100)
                    mapping=nodes.new("ShaderNodeMapping"); mapping.location=(-500,100)
                    mapping.inputs["Scale"].default_value=(4.0,4.0,4.0)
                    links.new(coord.outputs["UV"],mapping.inputs["Vector"])
                    links.new(mapping.outputs["Vector"],tex.inputs["Vector"])
                    mix=nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.location=(-100,150)
                    mix.inputs["Factor"].default_value=0.55
                    mix.inputs[6].default_value=(r,g,b,a)
                    links.new(tex.outputs["Color"],mix.inputs[7])
                    links.new(mix.outputs[2],bsdf.inputs["Base Color"])
    return mat
def add_box(name,loc,size,mat,eul):
    import math as _m
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=(_m.radians(eul[0]),_m.radians(eul[1]),_m.radians(eul[2])))
    o=bpy.context.active_object; o.name=name; o.scale=size
    bpy.ops.object.transform_apply(scale=True)
    for p in o.data.polygons: p.use_smooth=False
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
BOXES=[
'''
    rows=[H]
    for (n,bx,by,bz,sx,sy,sz,m,rx,ry,rz,uv) in B:
        rows.append(f' ("{n}",({bx:.2f},{by:.2f},{bz:.2f}),({sx:.3f},{sy:.3f},{sz:.3f}),"{m}",({rx},{ry},{rz})),')
    rows.append("]\ndef main():")
    rows.append(' cn="CityV1"; col=bpy.data.collections.get(cn)')
    rows.append(" if col is None:\n  col=bpy.data.collections.new(cn); bpy.context.scene.collection.children.link(col)")
    rows.append(" bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[cn]")
    rows.append(" for o in list(col.objects): bpy.data.objects.remove(o,do_unlink=True)")
    rows.append(" mats={k:make_mat(k) for k in COLORS}")
    rows.append(" for (n,loc,size,m,eu) in BOXES: add_box(n,loc,size,mats[m],eu)")
    rows.append(' print(f"Done: {len(col.objects)} objects")\nif __name__=="__main__": main()')
    BPY.write_text("\n".join(rows))
    print(f"WROTE {BPY.name}: {len(B)} boxes")

if __name__=="__main__":
    make_textures(); write_obj(); write_lua(); write_bpy()
