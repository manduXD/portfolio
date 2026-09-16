#!/usr/bin/env python3
"""Emit arena_map_builder_v2.lua from arena_v2_gen.B (Blender Z-up -> Roblox Y-up)."""
from pathlib import Path
import arena_v2_gen as G

OUT = Path(__file__).parent / "arena_map_builder_v2.lua"

RMAT = {
 "Grass":"Grass","Stone":"Cobblestone","RockSide":"Sandstone","RockDark":"Rock",
 "Slate":"Slate","Wood":"WoodPlanks","Crate":"Wood","Trunk":"Wood","Leaf":"Grass",
 "Water":"Water","Gold":"Metal","NeonCyan":"Neon","NeonPink":"Neon","NeonOrange":"Neon",
 "RockTop":"Sandstone",
}
RCOL = {k:(int(r*255),int(g*255),int(b*255)) for k,(r,g,b) in G.MAT_COLORS.items()}

lines = []
lines.append("-- Arena v2 Builder (188 boxes, parkour + zones + textures via Materials)")
lines.append("-- USE: Studio > View > Command Bar > paste whole file > Enter. Map -> Workspace > RockyArenaV2")
lines.append('local W = game:GetService("Workspace")')
lines.append('local L = game:GetService("Lighting")')
lines.append('local old = W:FindFirstChild("RockyArenaV2") if old then old:Destroy() end')
lines.append('local map = Instance.new("Folder") map.Name = "RockyArenaV2" map.Parent = W')
lines.append('local function P(n, x,y,z, sx,sy,sz, col, mat, rotY, anchor, collide, transp)')
lines.append(' local p = Instance.new("Part") p.Name=n p.Position=Vector3.new(x,y,z) p.Size=Vector3.new(sx,sy,sz)')
lines.append(' p.Color=col p.Material=mat p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth')
lines.append(' if rotY and rotY~=0 then p.Orientation=Vector3.new(0,rotY,0) end')
lines.append(' p.Anchored = (anchor==nil) and true or anchor')
lines.append(' p.CanCollide = (collide==nil) and true or collide')
lines.append(' if transp then p.Transparency=transp end')
lines.append(' p.Parent=map return p end')
lines.append('local C = function(r,g,b) return Color3.fromRGB(r,g,b) end')

for (n,bx,by,bz,sx,sy,sz,m,rot) in G.B:
    rx, ry, rz = bx, bz, by
    rsx, rsy, rsz = sx, sz, sy
    r,g,b = RCOL[m]
    rmat = RMAT.get(m,"Rock")
    # sanitize name for lua string
    safe = n.replace('"','')
    extra = ""
    if m == "Water":
        extra = ", nil, true, false, 0.25"
    elif m.startswith("Neon"):
        extra = ""
    lines.append(f'P("{safe}", {rx:.2f},{ry:.2f},{rz:.2f}, {rsx:.2f},{rsy:.2f},{rsz:.2f}, C({r},{g},{b}), Enum.Material.{rmat}, {rot}{extra})')

# lights + spawns + lighting
lines.append('-- torches / braziers glow')
lines.append('for _,o in ipairs(map:GetChildren()) do if o.Name:find("TorchFire") or o.Name:find("Brazier") then local l=Instance.new("PointLight") l.Color=Color3.fromRGB(255,170,90) l.Brightness=2 l.Range=25 l.Parent=o end end')
lines.append('for _,o in ipairs(map:GetChildren()) do if o.Name:find("JumpPad") or o.Name:find("FinishPad") or o.Name:find("Check") then local l=Instance.new("PointLight") l.Color=o.Color l.Brightness=1.5 l.Range=15 l.Parent=o end end')
lines.append('local s1=Instance.new("SpawnLocation") s1.Position=Vector3.new(0,3,52) s1.Size=Vector3.new(6,1,6) s1.Anchored=true s1.Neutral=true s1.Duration=0 s1.Parent=map')
lines.append('local s2=Instance.new("SpawnLocation") s2.Position=Vector3.new(42,4,2) s2.Size=Vector3.new(6,1,6) s2.Anchored=true s2.Neutral=true s2.Duration=0 s2.Parent=map')
lines.append('L.ClockTime=17.6 L.Brightness=2.4 L.Ambient=Color3.fromRGB(65,70,100) L.OutdoorAmbient=Color3.fromRGB(85,95,135) L.FogColor=Color3.fromRGB(60,80,135) L.FogStart=90 L.FogEnd=500 L.GlobalShadows=true')
lines.append('local a=L:FindFirstChild("ArenaV2Atmo") if not a then a=Instance.new("Atmosphere") a.Name="ArenaV2Atmo" a.Parent=L end')
lines.append('a.Density=0.32 a.Offset=0.25 a.Color=Color3.fromRGB(150,170,225) a.Decay=Color3.fromRGB(65,75,135) a.Glare=0.25 a.Haze=2')
lines.append('print("RockyArenaV2 built: "..#map:GetChildren().." parts")')

OUT.write_text("\n".join(lines))
print(f"WROTE {OUT.name}: {len(lines)} lines")
