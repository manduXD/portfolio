#!/usr/bin/env python3
"""Village v1: 500x500 low-poly blocky village, town hall center.
Generates: PNG textures, OBJ+MTL, Roblox Lua, Blender bpy. Run: python village_gen.py"""
from pathlib import Path
import random, math
random.seed(21)

ROOT = Path(__file__).parent
TEXDIR = ROOT / "village_textures"
OBJ = ROOT / "low_poly_village.obj"
MTL = ROOT / "low_poly_village.mtl"
LUA = ROOT / "village_map_builder.lua"
BPY = ROOT / "low_poly_village_blender.py"

B = []
def box(n,x,y,z,sx,sy,sz,m,rot=0):
    B.append((n,x,y,z,sx,sy,sz,m,rot))

def rot2(lx,ly,deg):
    a = math.radians(deg)
    return (lx*math.cos(a)-ly*math.sin(a), lx*math.sin(a)+ly*math.cos(a))

# ============ GROUND + ROADS (500x500) ============
box("Ground", 0,0,-1, 500,500,2, "Grass")
box("Plaza", 0,0,0.12, 52,52,0.3, "Stone")
box("PlazaTrim", 0,0,0.30, 46,46,0.12, "StoneTrim")
# roads stop at plaza edge (26)
box("RoadS", 0,138,0.05, 9,224,0.22, "Stone")
box("RoadN", 0,-138,0.05, 9,224,0.22, "Stone")
box("RoadE", 138,0,0.05, 224,9,0.22, "Stone")
box("RoadW", -138,0,0.05, 224,9,0.22, "Stone")
# grass variation patches (thin, no z-fight: 0.02 above ground top z=0)
for i,(x,y,sx,sy) in enumerate([(-80,90,60,40),(90,-80,70,50),(-120,-90,55,45),(110,110,60,55),(0,180,80,40)]):
    box(f"Meadow{i}", x,y,0.02, sx,sy,0.1, "LeafDark")

# ============ TOWN HALL (center, faces south +y) ============
TH = "TH"
box(f"{TH}_Base", 0,-2,2.0, 28,20,4.0, "RockSide")
box(f"{TH}_Upper", 0,-2,6.0, 24,17,4.2, "Plaster")
# timber frame on upper
for cx in (-11.5, 11.5):
    for cy in (-10.2, 6.2):
        box(f"{TH}_Post_{cx}_{cy}", cx,-2+cy+2,6.0, 0.5,0.5,4.2, "Trunk")
box(f"{TH}_BeamF", 0,6.6,7.6, 24.4,0.5,0.6, "Trunk")
box(f"{TH}_BeamB", 0,-10.6,7.6, 24.4,0.5,0.6, "Trunk")
# stepped pyramid roof
box(f"{TH}_Roof1", 0,-2,8.6, 27,20,1.2, "Roof")
box(f"{TH}_Roof2", 0,-2,9.7, 20,14.5,1.2, "Roof")
box(f"{TH}_Roof3", 0,-2,10.8, 13,9,1.2, "Roof")
box(f"{TH}_Cap", 0,-2,11.7, 6,4,0.7, "Trunk")
# tower
box(f"{TH}_Tower", 0,-2,14.5, 6.5,6.5,6.0, "Plaster")
box(f"{TH}_TowerTrim", 0,-2,17.7, 7.2,7.2,0.6, "Stone")
box(f"{TH}_Spire1", 0,-2,18.6, 6.0,6.0,1.2, "Roof")
box(f"{TH}_Spire2", 0,-2,19.6, 3.6,3.6,1.2, "Roof")
box(f"{TH}_FlagPole", 0,-2,21.2, 0.3,0.3,2.4, "Trunk")
box(f"{TH}_Flag", 1.3,-2,22.0, 2.4,0.15,1.2, "Gold")
# clock (gold face + dark hands) on south face
box(f"{TH}_Clock", 0,1.35,15.2, 2.6,0.15,2.6, "Gold")
box(f"{TH}_HandV", 0,1.45,15.2, 0.25,0.1,1.6, "Slate")
box(f"{TH}_HandH", 0.6,1.45,15.2, 1.0,0.1,0.25, "Slate")
# double door + steps + windows
box(f"{TH}_DoorL", -1.1,8.15,1.9, 2.0,0.3,3.4, "Trunk")
box(f"{TH}_DoorR", 1.1,8.15,1.9, 2.0,0.3,3.4, "Trunk")
box(f"{TH}_Steps", 0,9.6,0.5, 7,3.2,0.7, "Stone")
box(f"{TH}_Step2", 0,8.9,1.0, 6,1.6,0.5, "Stone")
for wx in (-8,-4.5,4.5,8):
    box(f"{TH}_WinF_{wx}", wx,6.62,6.0, 1.6,0.15,1.8, "Glass")
for wx in (-8,-4.5,4.5,8):
    box(f"{TH}_WinB_{wx}", wx,-10.62,6.0, 1.6,0.15,1.8, "Glass")
for wy in (-6,2):
    box(f"{TH}_WinL_{wy}", -12.12,wy-2,6.0, 0.15,1.6,1.8, "Glass")
    box(f"{TH}_WinR_{wy}", 12.12,wy-2,6.0, 0.15,1.6,1.8, "Glass")
for bx in (-14.5,14.5):
    box(f"{TH}_Banner_{bx}", bx,8.2,5.5, 1.8,0.15,3.0, "Roof")
    box(f"{TH}_LampP_{bx}", bx,10.5,1.5, 0.35,0.35,3.0, "Trunk")
    box(f"{TH}_LampH_{bx}", bx,10.5,3.2, 0.8,0.8,0.8, "LampGlow")

# ============ FOUNTAIN (north plaza) ============
box("FountainBase", 0,-19,0.8, 7,7,1.0, "Stone")
box("FountainWater", 0,-19,1.35, 6,6,0.2, "Water")
box("FountainPillar", 0,-19,2.2, 1.2,1.2,1.8, "Stone")
box("FountainBowl", 0,-19,3.2, 3.0,3.0,0.4, "Stone")
box("FountainTop", 0,-19,3.9, 0.5,0.5,1.0, "Stone")
for bx,by in [(-5,-19),(5,-19),(0,-14),(0,-24)]:
    box(f"BenchF_{bx}_{by}", bx,by,0.75, 2.4,0.9,0.25, "Wood")
    box(f"BenchB_{bx}_{by}", bx,by-0.65 if by==-14 or by==0 else by,0.75, 2.4,0.9,0.25, "Wood")

# ============ MARKET STALLS (south plaza row) ============
for i,sx in enumerate([-18,-6,6,18]):
    S = f"Stall{i}"
    box(f"{S}_Counter", sx,16,1.0, 4.2,2.2,1.0, "Wood")
    box(f"{S}_Top", sx,16,1.6, 4.4,2.4,0.15, "Wood")
    for px,py in [(sx-1.9,15),(sx+1.9,15),(sx-1.9,17),(sx+1.9,17)]:
        box(f"{S}_Post_{px}_{py}", px,py,2.2, 0.25,0.25,2.4, "Trunk")
    for k in range(5):
        c = "Cream" if k%2==0 else "Roof"
        box(f"{S}_Aw_{k}", sx-1.76+k*0.88,16,3.55, 0.88,3.0,0.12, c)
    box(f"{S}_Crate", sx+3.2,16,0.6, 1.2,1.2,1.2, "Crate")

# ============ HOUSES ============
def house(p, x, y, rot, w, d, wh, wall, roof, shop=False):
    hw, hd = (d, w) if rot in (90,270) else (w, d)
    box(f"{p}_Plinth", x,y,0.35, hw+0.6,hd+0.6,0.7, "RockSide")
    box(f"{p}_Walls", x,y,0.7+wh/2, hw,hd,wh, wall)
    # front dir vector
    fx, fy = rot2(0,1,rot)
    # door on front face
    dx, dy = x+fx*(hd/2+0.1), y+fy*(hd/2+0.1)
    dw = hw if abs(fy)<0.5 else hd  # not used; door width fixed 1.6
    box(f"{p}_Door", dx,dy,1.55, 1.6 if abs(fy)>0.5 else 0.25, 0.25 if abs(fy)>0.5 else 1.6, 2.5, "Trunk")
    box(f"{p}_Step", x+fx*(hd/2+0.9),y+fy*(hd/2+0.9),0.2, 2.4,2.4,0.4, "Stone")
    # windows front (2) + sides
    for s in (-1,1):
        # front windows offset along front tangent
        tx, ty = rot2(s*hw*0.28,0,rot)
        wx, wy = x+tx+fx*(hd/2+0.06), y+ty+fy*(hd/2+0.06)
        box(f"{p}_WinF{s}", wx,wy,0.7+wh*0.55, 1.2 if abs(fy)>0.5 else 0.15, 0.15 if abs(fy)>0.5 else 1.2, 1.3, "Glass")
        # side windows
        sx2, sy2 = rot2(s*(hw/2+0.06),0,rot)
        # place on left/right walls
        lx, ly = rot2(0,0,rot)  # center
        qx, qy = x+sx2, y+sy2
        # orient thin axis along x or y depending on side
        if rot in (0,180):
            box(f"{p}_WinS{s}", qx,qy,0.7+wh*0.55, 0.15,1.2,1.3, "Glass")
        else:
            box(f"{p}_WinS{s}", qx,qy,0.7+wh*0.55, 1.2,0.15,1.3, "Glass")
    # corner timber boards
    for cx in (-1,1):
        for cy in (-1,1):
            ox, oy = rot2(cx*hw/2,cy*hd/2,rot)
            box(f"{p}_Post{cx}{cy}", x+ox,y+oy,0.7+wh/2, 0.4,0.4,wh, "Trunk")
    # roof pyramid steps
    rz = 0.7+wh
    box(f"{p}_R1", x,y,rz+0.35, hw+1.0,hd+1.0,0.7, roof)
    box(f"{p}_R2", x,y,rz+1.05, hw*0.68,hd*0.68,0.7, roof)
    box(f"{p}_R3", x,y,rz+1.7, hw*0.4,hd*0.4,0.6, roof)
    # chimney
    chx, chy = rot2(hw*0.25,-hd*0.15,rot)
    box(f"{p}_Chim", x+chx,y+chy,rz+1.6, 0.9,0.9,2.2, "RockSide")
    if shop:
        ax, ay = x+fx*(hd/2+1.2), y+fy*(hd/2+1.2)
        for k in range(4):
            ox, oy = rot2(-1.5+k*1.0,0,rot)
            c = "Cream" if k%2==0 else roof
            box(f"{p}_Aw{k}", ax+ox,ay+oy,2.9, 1.0 if abs(fy)>0.5 else 0.12, 0.12 if abs(fy)>0.5 else 1.0, 0.12, c)

house("CotA", -42,78,180, 9,7,3.2, "Plaster","Roof")
house("ShopA", 44,80,180, 10,8,3.4, "Plaster","Roof", shop=True)
house("CotB", -44,-78,0, 9,7,3.2, "Plaster","Roof")
house("HouseC", 46,-80,0, 11,8,3.6, "Cream","Roof")
house("FarmH", -85,30,90, 10,8,3.4, "Plaster","Roof")
house("HouseD", 86,-28,-90, 10,8,3.4, "Cream","Roof")
house("CotE", -86,-30,90, 8,7,3.0, "Plaster","Roof")
house("ShopB", 88,34,-90, 10,8,3.4, "Cream","Roof", shop=True)

# ============ CHAPEL (north-east of plaza) ============
box("Ch_Nave", -32,122,2.6, 10,16,5.2, "Plaster")
box("Ch_Roof1", -32,122,5.6, 11,17,1.0, "Roof")
box("Ch_Roof2", -32,122,6.5, 7.5,17,1.0, "Roof")
box("Ch_Roof3", -32,122,7.3, 4,17,0.8, "Roof")
box("Ch_Tower", -32,132,5.0, 5,5,10.0, "Plaster")
box("Ch_Spire1", -32,132,10.6, 5.6,5.6,1.2, "Roof")
box("Ch_Spire2", -32,132,11.6, 3.2,3.2,1.2, "Roof")
box("Ch_CrossV", -32,132,12.9, 0.3,0.3,1.6, "Gold")
box("Ch_CrossH", -32,132,12.9, 1.0,0.3,0.3, "Gold")
box("Ch_Door", -32,114.1,1.6, 2.2,0.25,3.2, "Trunk")
box("Ch_Win1", -32,122,3.4, 2.0,16.2,2.2, "Glass")
box("Ch_Win2", -37.1,122,3.4, 0.15,2.0,2.2, "Glass")
box("Ch_Win3", -26.9,122,3.4, 0.15,2.0,2.2, "Glass")

# ============ BARN + FARM (west) ============
box("BarnBase", -80,112,2.5, 16,12,5.0, "BarnRed")
box("BarnRoof1", -80,112,5.6, 17,13,1.2, "Roof")
box("BarnRoof2", -80,112,6.7, 11,13,1.2, "Trunk")
box("BarnRoof3", -80,112,7.7, 5,13,1.0, "Trunk")
box("BarnDoor", -80,118.15,1.9, 5,0.3,3.8, "Trunk")
box("BarnWin", -80,106.1,3.4, 2.0,0.15,1.4, "Glass")
box("Hay1", -68,112,0.9, 1.8,1.8,1.8, "Hay")
box("Hay2", -68,114.2,0.9, 1.8,1.8,1.8, "Hay")
box("Hay3", -68,113.1,2.6, 1.8,1.8,1.6, "Hay")
# fields with crop rows
for f,(fx,fy) in enumerate([(-112,88),(-112,64)]):
    box(f"Field{f}_Soil", fx,fy,0.15, 22,14,0.3, "Soil")
    box(f"Field{f}_Fence1", fx,fy-7.5,0.6, 23,0.3,1.2, "Wood")
    box(f"Field{f}_Fence2", fx,fy+7.5,0.6, 23,0.3,1.2, "Wood")
    for r in range(3):
        for c in range(5):
            box(f"Crop{f}_{r}_{c}", fx-8+c*4,fy-4+r*4,0.7, 1.0,1.0,0.9, "LeafDark")
# windmill
box("MillBase", -128,104,2.5, 6,6,5.0, "RockSide")
box("MillMid", -128,104,6.0, 4.6,4.6,4.0, "Plaster")
box("MillCap", -128,104,8.4, 5.2,5.2,0.8, "Roof")
box("MillHub", -124.6,104,8.0, 0.8,0.8,0.8, "Trunk")
box("MillBladeV", -124.2,104,8.0, 0.3,0.7,13.0, "Cream")
box("MillBladeH", -124.2,104,8.0, 0.3,13.0,0.7, "Cream")
# orchard rows
for i,(ox,oy) in enumerate([(-58,116),(-50,116),(-42,116),(-58,126),(-50,126),(-42,126)]):
    box(f"OrchT{i}", ox,oy,1.5, 0.8,0.8,3.0, "Trunk")
    box(f"OrchL{i}", ox,oy,3.6, 3.2,3.2,1.8, "Leaf")
    box(f"OrchA{i}", ox+0.8,oy+0.8,3.2, 0.5,0.5,0.5, "Apple")

# ============ PARK + POND (south-east) ============
box("PondSand", 88,-102,0.08, 26,20,0.25, "RockTop")
box("Pond", 88,-102,0.28, 23,17,0.3, "Water")
box("Dock", 76,-102,0.7, 6,2.4,0.3, "Wood")
for px in (73.5,78.5):
    box(f"DockPost{px}", px,-103,0.2, 0.3,0.3,1.4, "Trunk")
    box(f"DockPost2{px}", px,-101,0.2, 0.3,0.3,1.4, "Trunk")
for i,(bx,by,br) in enumerate([(70,-92,0),(106,-92,180),(70,-112,0),(106,-112,180)]):
    box(f"ParkBench{i}", bx,by,0.75, 2.6,1.0,0.25, "Wood")
    box(f"ParkBack{i}", bx,by+(0.6 if br==0 else -0.6),1.2, 2.6,0.2,0.9, "Wood")

# ============ STREET LAMPS along roads ============
for i,(lx,ly) in enumerate([(-8,60),(8,100),(-8,140),(8,180),(-8,-60),(8,-100),(-8,-140),(8,-180),(60,8),(100,-8),(140,8),(180,-8),(-60,-8),(-100,8),(-140,-8),(-180,8)]):
    box(f"LampP{i}", lx,ly,1.5, 0.35,0.35,3.0, "Trunk")
    box(f"LampH{i}", lx,ly,3.2, 0.8,0.8,0.8, "LampGlow")

# ============ GATES + PERIMETER WALL (245) ============
W = 245
# south wall with gate at x=0
box("WallS1", -130,W,1.75, 220,3,3.5, "RockSide")
box("WallS2", 130,W,1.75, 220,3,3.5, "RockSide")
box("WallN1", -130,-W,1.75, 220,3,3.5, "RockSide")
box("WallN2", 130,-W,1.75, 220,3,3.5, "RockSide")
box("WallW1", -W,130,1.75, 3,220,3.5, "RockSide")
box("WallW2", -W,-130,1.75, 3,220,3.5, "RockSide")
box("WallE1", W,130,1.75, 3,220,3.5, "RockSide")
box("WallE2", W,-130,1.75, 3,220,3.5, "RockSide")
for gx,gy,along in [(0,245,"x"),(0,-245,"x"),(245,0,"z"),(-245,0,"z")]:
    if along=="x":
        box(f"GateP1_{gx}_{gy}", gx-7,gy,2.5, 3,3,5, "RockDark")
        box(f"GateP2_{gx}_{gy}", gx+7,gy,2.5, 3,3,5, "RockDark")
        box(f"GateT_{gx}_{gy}", gx,gy,5.4, 17,3.4,1.2, "Trunk")
        box(f"GateLamp_{gx}_{gy}", gx,gy,6.4, 0.9,0.9,0.9, "LampGlow")
    else:
        box(f"GateP1_{gx}_{gy}", gx,gy-7,2.5, 3,3,5, "RockDark")
        box(f"GateP2_{gx}_{gy}", gx,gy+7,2.5, 3,3,5, "RockDark")
        box(f"GateT_{gx}_{gy}", gx,gy,5.4, 3.4,17,1.2, "Trunk")
        box(f"GateLamp_{gx}_{gy}", gx,gy,6.4, 0.9,0.9,0.9, "LampGlow")

# ============ TREES / NATURE ============
def oak(x,y,s,i):
    box(f"OakT{i}", x,y,2.5*s, 1.3*s,1.3*s,5*s, "Trunk")
    box(f"OakC{i}", x,y,5.6*s, 6.5*s,6.5*s,2.2*s, "Leaf")
    box(f"OakC2_{i}", x+1*s,y,6.8*s, 4.5*s,4.5*s,1.6*s, "Leaf")
def pine(x,y,s,i):
    box(f"PineT{i}", x,y,2*s, 1.1*s,1.1*s,4*s, "Trunk")
    box(f"Pine1_{i}", x,y,4.4*s, 5.5*s,5.5*s,2*s, "LeafDark")
    box(f"Pine2_{i}", x,y,5.8*s, 4*s,4*s,1.8*s, "LeafDark")
    box(f"Pine3_{i}", x,y,7.1*s, 2.6*s,2.6*s,1.5*s, "LeafDark")
n=0
for x,y,s in [(-60,60,1.2),(-70,-60,1.3),(70,60,1.1),(60,-60,1.2),(-150,40,1.4),(-150,-40,1.2),(150,60,1.3),(150,-60,1.2),(40,150,1.3),(-40,150,1.1),(40,-150,1.2),(-40,-150,1.3),(120,120,1.2),(-120,-120,1.3),(120,-140,1.1),(-140,140,1.2)]:
    oak(x,y,s,f"o{n}"); n+=1
for x,y,s in [(-180,100,1.2),(-180,-100,1.3),(180,120,1.1),(180,-120,1.2),(100,180,1.3),(-100,180,1.1),(100,-180,1.2),(-100,-180,1.3),(0,210,1.2),(210,0,1.1),(-210,0,1.2),(0,-210,1.3)]:
    pine(x,y,s,f"p{n}"); n+=1
# bushes + flowers + rocks (clean scatter, off roads)
for i,(x,y) in enumerate([(-30,50),(30,52),(-52,-50),(52,-52),(-100,-20),(100,20),(-20,110),(24,-108),(140,140),(-140,-140)]):
    box(f"Bush{i}", x,y,0.6, 2.2,2.2,1.3, "Leaf")
    box(f"Flower{i}", x+0.6,y+0.6,1.35, 0.35,0.35,0.5, "Gold" if i%2 else "Cream")
for i,(x,y,z,s,r) in enumerate([(-90,0,0.4,2.4,15),(90,90,0.4,2.0,-20),(-95,-110,0.5,2.8,30),(130,-60,0.4,2.2,10),(-130,60,0.4,2.4,-10),(30,190,0.5,2.6,0)]):
    box(f"Rock{i}", x,y,z, s,s*0.75,s, "RockDark", r)
# crates + barrels near shops/barn
for i,(x,y) in enumerate([(52,80),(54,80),(-52,-78),(94,34),(96,34),(-74,112)]):
    box(f"Crate{i}", x,y,0.9, 1.8,1.8,1.8, "Crate")
for i,(x,y) in enumerate([(50,82),(-50,-76),(92,36)]):
    box(f"Barrel{i}", x,y,0.9, 1.4,1.4,1.8, "Wood")

MAT_COLORS = {
 "Grass":(0.30,0.62,0.28),"LeafDark":(0.13,0.38,0.26),"Leaf":(0.17,0.45,0.32),
 "Stone":(0.64,0.60,0.54),"StoneTrim":(0.55,0.51,0.46),"RockSide":(0.45,0.40,0.35),
 "RockDark":(0.25,0.28,0.37),"RockTop":(0.60,0.55,0.48),"Slate":(0.23,0.27,0.39),
 "Plaster":(0.93,0.88,0.76),"Cream":(0.96,0.92,0.80),"Roof":(0.62,0.26,0.18),
 "BarnRed":(0.60,0.20,0.15),"Trunk":(0.26,0.19,0.12),"Wood":(0.48,0.34,0.22),
 "Crate":(0.56,0.39,0.23),"Hay":(0.85,0.72,0.35),"Soil":(0.32,0.22,0.14),
 "Glass":(0.55,0.78,0.90),"Water":(0.28,0.56,0.85),"Gold":(0.95,0.75,0.25),
 "LampGlow":(1.0,0.72,0.35),"Apple":(0.85,0.2,0.2),
}
TEXTURED = {"Grass":"village_grass.png","LeafDark":"village_leaf.png","Leaf":"village_leaf.png",
 "Stone":"village_pavers.png","StoneTrim":"village_pavers.png","RockTop":"village_pavers.png",
 "RockSide":"village_rock.png","RockDark":"village_rock_dark.png","Slate":"village_rock_dark.png",
 "Plaster":"village_plaster.png","Cream":"village_plaster.png","Roof":"village_roof.png",
 "BarnRed":"village_roof.png","Trunk":"village_wood.png","Wood":"village_wood.png",
 "Crate":"village_wood.png","Hay":"village_wood.png","Soil":"village_soil.png"}

def make_textures():
    from PIL import Image, ImageDraw
    TEXDIR.mkdir(exist_ok=True)
    S=256
    def grain(base,var=20,dots=800,dot=None):
        img=Image.new("RGB",(S,S),base); px=img.load()
        for yy in range(S):
            for xx in range(S):
                v=random.randint(-var,var); r,g,b=base
                px[xx,yy]=(max(0,min(255,r+v)),max(0,min(255,g+v)),max(0,min(255,b+v)))
        d=ImageDraw.Draw(img)
        for _ in range(dots):
            x,y=random.randrange(S),random.randrange(S)
            c=dot or (max(0,base[0]-38),max(0,base[1]-38),max(0,base[2]-38))
            d.rectangle([x,y,x+2,y+2],fill=c)
        return img
    grain((76,158,72),24,1200,(46,118,50)).save(TEXDIR/"village_grass.png")
    grain((112,104,96),20,900,(70,62,55)).save(TEXDIR/"village_rock.png")
    grain((60,66,90),16,800,(36,42,62)).save(TEXDIR/"village_rock_dark.png")
    w=grain((122,86,54),18,350,(90,60,35))
    d=ImageDraw.Draw(w)
    for yy in range(0,S,42): d.line([0,yy,S,yy],fill=(70,45,25),width=3)
    w.save(TEXDIR/"village_wood.png")
    p=grain((164,154,136),12,450,(136,124,106))
    d=ImageDraw.Draw(p)
    for xx in range(0,S,64): d.line([xx,0,xx,S],fill=(118,106,90),width=4)
    for yy in range(0,S,64): d.line([0,yy,S,yy],fill=(118,106,90),width=4)
    p.save(TEXDIR/"village_pavers.png")
    grain((44,112,82),26,1300,(26,80,58)).save(TEXDIR/"village_leaf.png")
    grain((236,224,194),10,300,(214,200,170)).save(TEXDIR/"village_plaster.png")
    r=grain((158,66,46),16,500,(120,45,30))
    d=ImageDraw.Draw(r)
    for yy in range(0,S,32): d.line([0,yy,S,yy],fill=(100,38,24),width=3)
    for xx in range(0,S,32): d.line([xx,0,xx,S],fill=(100,38,24),width=2)
    r.save(TEXDIR/"village_roof.png")
    s=grain((82,56,36),16,500,(58,38,22))
    d=ImageDraw.Draw(s)
    for yy in range(0,S,26): d.line([0,yy,S,yy],fill=(52,34,20),width=3)
    s.save(TEXDIR/"village_soil.png")
    print("textures:",len(list(TEXDIR.glob("*.png"))))

def write_obj():
    verts=[]; items=[]
    for (n,x,y,z,sx,sy,sz,m,rot) in B:
        hx,hy,hz=sx/2,sy/2,sz/2
        corners=[(x-hx,y-hy,z-hz),(x+hx,y-hy,z-hz),(x+hx,y+hy,z-hz),(x-hx,y+hy,z-hz),
                 (x-hx,y-hy,z+hz),(x+hx,y-hy,z+hz),(x+hx,y+hy,z+hz),(x-hx,y+hy,z+hz)]
        if rot:
            a=math.radians(rot); ca,sa=math.cos(a),math.sin(a)
            corners=[(x+(cx-x)*ca-(cy-y)*sa,y+(cx-x)*sa+(cy-y)*ca,cz) for cx,cy,cz in corners]
        base=len(verts)+1; verts.extend(corners)
        faces=[((0,1,2,3),(sx,sy)),((4,5,6,7),(sx,sy)),((0,1,5,4),(sx,sz)),
               ((1,2,6,5),(sy,sz)),((2,3,7,6),(sx,sz)),((3,0,4,7),(sy,sz))]
        items.append((n,m,base,faces))
    vts=[]
    with open(OBJ,"w") as f:
        f.write("# Village v1 500x500 Z-up\nmtllib low_poly_village.mtl\n")
        for v in verts: f.write(f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}\n")
        for (uu,vv) in []: f.write(f"vt {uu} {vv}\n")
    # second pass with vt (kept simple: rebuild)
    vts=[]; 
    lines=[f"# Village v1 500x500 Z-up, {len(B)} boxes","mtllib low_poly_village.mtl"]
    lines += [f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}" for v in verts]
    bymat={}
    for (n,m,base,faces) in items: bymat.setdefault(m,[]).append((n,base,faces))
    for m,lst in bymat.items():
        for (n,base,faces) in lst:
            for (inds,(du,dv)) in faces:
                tu=max(1,round(du/4)); tv=max(1,round(dv/4))
                for (uu,vv) in [(0,0),(tu,0),(tu,tv),(0,tv)]: vts.append((uu,vv))
    lines += [f"vt {u} {v}" for (u,v) in vts]
    vi=1
    for m,lst in bymat.items():
        lines.append(f"o {m}"); lines.append(f"usemtl {m}")
        for (n,base,faces) in lst:
            for (inds,(du,dv)) in faces:
                ids=[f"{base+i}/{vi+k}" for k,i in enumerate(inds)]; vi+=4
                lines.append(f"f {' '.join(ids)} # {n}")
    OBJ.write_text("\n".join(lines)+"\n")
    with open(MTL,"w") as f:
        for m,(r,g,b) in MAT_COLORS.items():
            ns = 12 if m not in ("LampGlow","Gold","Water","Glass") else (120 if m=="Glass" else 150 if m=="Water" else 60 if m=="Gold" else 20)
            f.write(f"newmtl {m}\nKd {r:.3f} {g:.3f} {b:.3f}\nKa 0.08 0.08 0.08\nKs 0.05 0.05 0.05\nNs {ns}\nd 1.0\nillum 2\n")
            if m in TEXTURED: f.write(f"map_Kd village_textures/{TEXTURED[m]}\n")
            if m in ("LampGlow","Gold","Water"): f.write(f"Ke {r:.3f} {g:.3f} {b:.3f}\n")
            f.write("\n")
    print(f"WROTE {OBJ.name}: {len(verts)} verts, {len(B)*6} faces, {len(B)} boxes")

RMAT={"Grass":"Grass","LeafDark":"Grass","Leaf":"Grass","Stone":"Cobblestone","StoneTrim":"Concrete",
 "RockSide":"Sandstone","RockDark":"Rock","RockTop":"Sandstone","Slate":"Slate","Plaster":"Limestone",
 "Cream":"Limestone","Roof":"Brick","BarnRed":"Brick","Trunk":"Wood","Wood":"WoodPlanks","Crate":"Wood",
 "Hay":"Straw" if False else "Wood","Soil":"Ground","Glass":"Glass","Water":"Water","Gold":"Metal",
 "LampGlow":"Neon","Apple":"SmoothPlastic"}

def write_lua():
    L=["-- Village v1 Builder 500x500 (town hall center). Command Bar paste > Enter. Map -> Workspace > VillageV1",
     'local W=game:GetService("Workspace") local L=game:GetService("Lighting")',
     'local old=W:FindFirstChild("VillageV1") if old then old:Destroy() end',
     'local map=Instance.new("Folder") map.Name="VillageV1" map.Parent=W',
     'local function P(n,x,y,z,sx,sy,sz,col,mat,rotY,anchor,collide,transp)',
     ' local p=Instance.new("Part") p.Name=n p.Position=Vector3.new(x,y,z) p.Size=Vector3.new(sx,sy,sz)',
     ' p.Color=col p.Material=mat p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth',
     ' if rotY and rotY~=0 then p.Orientation=Vector3.new(0,rotY,0) end',
     ' p.Anchored=(anchor==nil) and true or anchor p.CanCollide=(collide==nil) and true or collide',
     ' if transp then p.Transparency=transp end p.Parent=map return p end',
     'local C=function(r,g,b) return Color3.fromRGB(r,g,b) end']
    for (n,bx,by,bz,sx,sy,sz,m,rot) in B:
        r,g,b=[int(c*255) for c in MAT_COLORS[m]]
        rm=RMAT.get(m,"Rock")
        extra=""
        if m=="Water": extra=", nil, true, false, 0.3"
        elif m=="Glass": extra=", nil, true, true, 0.25"
        L.append(f'P("{n}", {bx:.2f},{bz:.2f},{by:.2f}, {sx:.2f},{sz:.2f},{sy:.2f}, C({r},{g},{b}), Enum.Material.{rm}, {rot}{extra})')
    L += ['for _,o in ipairs(map:GetChildren()) do if o.Name:find("LampH") or o.Name:find("LampGlow") or o.Name:find("GateLamp") then local l=Instance.new("PointLight") l.Color=Color3.fromRGB(255,190,110) l.Brightness=2 l.Range=30 l.Parent=o end end',
     'local s1=Instance.new("SpawnLocation") s1.Position=Vector3.new(0,3,40) s1.Size=Vector3.new(6,1,6) s1.Anchored=true s1.Neutral=true s1.Duration=0 s1.Parent=map',
     'L.ClockTime=15.5 L.Brightness=2.4 L.Ambient=Color3.fromRGB(90,90,105) L.OutdoorAmbient=Color3.fromRGB(120,125,150) L.FogColor=Color3.fromRGB(150,175,210) L.FogStart=150 L.FogEnd=900 L.GlobalShadows=true',
     'local a=L:FindFirstChild("VillageAtmo") if not a then a=Instance.new("Atmosphere") a.Name="VillageAtmo" a.Parent=L end',
     'a.Density=0.28 a.Offset=0.3 a.Color=Color3.fromRGB(190,200,230) a.Decay=Color3.fromRGB(110,125,170) a.Glare=0.2 a.Haze=1.5',
     'print("VillageV1 built: "..#map:GetChildren().." parts")']
    LUA.write_text("\n".join(L))
    print(f"WROTE {LUA.name}: {len(L)} lines")

def write_bpy():
    H='"""Village v1 Blender builder. Scripting > Run. Needs village_textures/ next to it. Then Z > Material Preview."""\nimport bpy,os\n'
    H+='TEXDIR=os.path.join(os.path.dirname(__file__) if "__file__" in globals() else os.getcwd(),"village_textures")\n'
    H+='TEXMAP='+repr({k:v for k,v in TEXTURED.items()})+'\n'
    H+='COLORS='+repr({k:(r,g,b,1) for k,(r,g,b) in MAT_COLORS.items()})+'\n'
    H+='EMISSIVE={"LampGlow":3.0,"Gold":0.5,"Water":0.3}\n'
    H+='''def make_mat(name):
    mat=bpy.data.materials.get("V_"+name)
    if mat is None:
        mat=bpy.data.materials.new("V_"+name); mat.use_nodes=True
        nt=mat.node_tree; nodes=nt.nodes; links=nt.links; nodes.clear()
        out=nodes.new("ShaderNodeOutputMaterial"); out.location=(400,0)
        bsdf=nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location=(100,0)
        r,g,b,a=COLORS[name]; bsdf.inputs["Base Color"].default_value=(r,g,b,a)
        try: bsdf.inputs["Roughness"].default_value=0.85
        except: pass
        links.new(bsdf.outputs[0],out.inputs[0])
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
def add_box(name,loc,size,mat,rot_z=0):
    import math
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=(0,0,rot_z))
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
    for (n,bx,by,bz,sx,sy,sz,m,rot) in B:
        rows.append(f' ("{n}",({bx:.2f},{by:.2f},{bz:.2f}),({sx:.3f},{sy:.3f},{sz:.3f}),"{m}",{math.radians(rot):.4f}),')
    rows.append("]\ndef main():")
    rows.append(' cn="VillageV1"; col=bpy.data.collections.get(cn)')
    rows.append(" if col is None:\n  col=bpy.data.collections.new(cn); bpy.context.scene.collection.children.link(col)")
    rows.append(" bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[cn]")
    rows.append(" for o in list(col.objects): bpy.data.objects.remove(o,do_unlink=True)")
    rows.append(" mats={k:make_mat(k) for k in COLORS}")
    rows.append(" for (n,loc,size,m,rz) in BOXES: add_box(n,loc,size,mats[m],rz)")
    rows.append(' print(f"Done: {len(col.objects)} objects")\nif __name__=="__main__": main()')
    BPY.write_text("\n".join(rows))
    print(f"WROTE {BPY.name}: {len(B)} boxes")

if __name__=="__main__":
    make_textures(); write_obj(); write_lua(); write_bpy()
