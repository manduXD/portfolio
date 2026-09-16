-- Rocky Arena Map Builder (like reference: stone platforms + cliffs + dusk)
-- HOW TO USE IN ROBLOX STUDIO:
-- 1. Open your place in Studio
-- 2. View > Command Bar (or Alt+X)
-- 3. Paste: loadstring(game:GetService("ServerScriptService"):WaitForChild("ArenaBuilder").Source)()  -- OR simply:
--    Copy this whole file into the Command Bar and press Enter
--    Easiest: Put this as a Script in ServerScriptService, press Play, then delete it (it keeps the map)
-- 4. Map appears in Workspace > RockyArena. Re-run to rebuild (deletes old).

local Workspace = game:GetService("Workspace")
local Lighting = game:GetService("Lighting")

-- delete old
local old = Workspace:FindFirstChild("RockyArena")
if old then old:Destroy() end
for _, v in ipairs(Lighting:GetChildren()) do
	if v.Name == "ArenaAtmosphere" or v.Name == "ArenaSky" then v:Destroy() end
end

local map = Instance.new("Folder")
map.Name = "RockyArena"
map.Parent = Workspace

local function part(name, pos, size, color, material, parent)
	local p = Instance.new("Part")
	p.Name = name
	p.Position = pos
	p.Size = size
	p.Color = color
	p.Material = material
	p.Anchored = true
	p.CanCollide = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent or map
	return p
end

-- COLORS (sampled from reference)
local C_GROUND = Color3.fromRGB(74, 160, 70)      -- bright green grass
local C_ROCK_DARK = Color3.fromRGB(52, 58, 78)    -- blue-grey cliffs
local C_ROCK_TOP = Color3.fromRGB(168, 156, 140)  -- warm light platform top
local C_ROCK_SIDE = Color3.fromRGB(92, 78, 70)    -- platform sides
local C_COVER = Color3.fromRGB(52, 60, 92)        -- low cover walls
local C_CRATE = Color3.fromRGB(58, 140, 70)       -- green crate
local C_TRUNK = Color3.fromRGB(45, 70, 60)
local C_LEAF = Color3.fromRGB(35, 90, 80)

-- 1. GROUND
part("Ground", Vector3.new(0, -1, 0), Vector3.new(512, 2, 512), C_GROUND, Enum.Material.Grass)

-- 2. MAIN PLATFORM (foreground in image - light top, dark sides)
-- base + thin top plate for two-tone look
part("MainBase", Vector3.new(0, 3, 10), Vector3.new(28, 6, 22), C_ROCK_SIDE, Enum.Material.Rock)
part("MainTop", Vector3.new(0, 6.2, 10), Vector3.new(28.4, 0.8, 22.4), C_ROCK_TOP, Enum.Material.Concrete)

-- 3. SIDE PLATFORMS (parkour / combat spacing)
part("Plat_Left", Vector3.new(-32, 2, -8), Vector3.new(18, 4, 16), C_ROCK_SIDE, Enum.Material.Rock)
part("Plat_Left_Top", Vector3.new(-32, 4.2, -8), Vector3.new(18.4, 0.8, 16.4), C_ROCK_TOP, Enum.Material.Concrete)

part("Plat_Right", Vector3.new(32, 3, 12), Vector3.new(20, 6, 14), C_ROCK_SIDE, Enum.Material.Rock)
part("Plat_Right_Top", Vector3.new(32, 6.2, 12), Vector3.new(20.4, 0.8, 14.4), C_ROCK_TOP, Enum.Material.Concrete)

part("Plat_Back", Vector3.new(0, 2.5, -32), Vector3.new(24, 5, 12), C_ROCK_SIDE, Enum.Material.Rock)
part("Plat_Back_Top", Vector3.new(0, 5.2, -32), Vector3.new(24.4, 0.8, 12.4), C_ROCK_TOP, Enum.Material.Concrete)

part("Plat_FarRight", Vector3.new(38, 1.5, -18), Vector3.new(14, 3, 14), C_COVER, Enum.Material.Slate)

-- 4. LOW COVER WALLS (scattered dark blocks like in image mid-ground)
local covers = {
	{Vector3.new(-12, 1.5, -12), Vector3.new(10, 3, 1.5)},
	{Vector3.new(14, 1.5, -6), Vector3.new(10, 3, 1.5)},
	{Vector3.new(-8, 1.5, 28), Vector3.new(8, 3, 1.5)},
	{Vector3.new(20, 1.5, 30), Vector3.new(12, 3, 2)},
	{Vector3.new(-28, 1, 18), Vector3.new(2, 2, 10)},
}
for i, c in ipairs(covers) do
	part("Cover"..i, c[1], c[2], C_COVER, Enum.Material.Slate)
end

-- small floating dark block (like debris in reference upper-right)
local float = part("FloatDebris", Vector3.new(18, 14, -8), Vector3.new(6, 1.2, 2), Color3.fromRGB(20,20,28), Enum.Material.Slate)
float.CanCollide = false

-- green crate (left side in image)
part("Crate", Vector3.new(-38, 1, 8), Vector3.new(6, 2, 3), C_CRATE, Enum.Material.Grass)

-- 5. PERIMETER CLIFFS (tall rock walls enclosing arena)
-- back wall segments
part("CliffBack1", Vector3.new(-30, 12, -58), Vector3.new(30, 28, 10), C_ROCK_DARK, Enum.Material.Rock)
part("CliffBack2", Vector3.new(5, 15, -62), Vector3.new(35, 34, 12), C_ROCK_DARK, Enum.Material.Rock)
part("CliffBack3", Vector3.new(40, 11, -58), Vector3.new(28, 26, 10), C_ROCK_DARK, Enum.Material.Rock)
-- left / right walls
part("CliffLeft", Vector3.new(-58, 12, 0), Vector3.new(10, 28, 120), C_ROCK_DARK, Enum.Material.Rock)
part("CliffRight", Vector3.new(58, 12, 0), Vector3.new(10, 28, 120), C_ROCK_DARK, Enum.Material.Rock)
-- front far (low, so sky visible)
part("CliffFrontL", Vector3.new(-30, 8, 60), Vector3.new(40, 20, 10), C_ROCK_DARK, Enum.Material.Rock)
part("CliffFrontR", Vector3.new(30, 8, 60), Vector3.new(40, 20, 10), C_ROCK_DARK, Enum.Material.Rock)
-- corner pillars for silhouette
part("Pillar1", Vector3.new(-48, 18, -48), Vector3.new(14, 40, 14), C_ROCK_DARK, Enum.Material.Rock)
part("Pillar2", Vector3.new(48, 18, -48), Vector3.new(14, 40, 14), C_ROCK_DARK, Enum.Material.Rock)

-- 6. BLOCKY TREES on top of cliffs (like reference background)
local function tree(x, y, z, s)
	s = s or 1
	part("Trunk", Vector3.new(x, y + 4*s, z), Vector3.new(2*s, 8*s, 2*s), C_TRUNK, Enum.Material.Wood)
	part("Canopy", Vector3.new(x, y + 9*s, z), Vector3.new(10*s, 2.5*s, 10*s), C_LEAF, Enum.Material.Grass)
	part("Canopy2", Vector3.new(x+1, y + 10.5*s, z), Vector3.new(7*s, 2*s, 7*s), C_LEAF, Enum.Material.Grass)
end
tree(-30, 26, -60, 1.4)
tree(8, 32, -64, 1.6)
tree(42, 24, -60, 1.2)
tree(-58, 26, -10, 1.0)
tree(58, 26, 5, 1.1)

-- 7. SPAWN + LIGHT
local spawn = Instance.new("SpawnLocation")
spawn.Position = Vector3.new(0, 8, 30)
spawn.Size = Vector3.new(6, 1, 6)
spawn.Anchored = true
spawn.Neutral = true
spawn.AllowTeamChangeOnTouch = false
spawn.Duration = 0
spawn.Parent = map

-- warm glow on main platform like sunset hit in image
local pl = Instance.new("PointLight")
pl.Color = Color3.fromRGB(255, 180, 120)
pl.Brightness = 2
pl.Range = 40
pl.Position = Vector3.new(0, 10, 10)
pl.Parent = map:FindFirstChild("MainTop")

-- 8. LIGHTING / DUSK LOOK
Lighting.ClockTime = 17.85
Lighting.Brightness = 2.2
Lighting.Ambient = Color3.fromRGB(60, 65, 95)
Lighting.OutdoorAmbient = Color3.fromRGB(75, 85, 125)
Lighting.FogColor = Color3.fromRGB(55, 75, 130)
Lighting.FogStart = 80
Lighting.FogEnd = 400
Lighting.GlobalShadows = true

local atm = Instance.new("Atmosphere")
atm.Name = "ArenaAtmosphere"
atm.Density = 0.35
atm.Offset = 0.2
atm.Color = Color3.fromRGB(140, 160, 220)
atm.Decay = Color3.fromRGB(60, 70, 130)
atm.Glare = 0.3
atm.Haze = 2
atm.Parent = Lighting

local sky = Instance.new("Sky")
sky.Name = "ArenaSky"
sky.SkyboxBk = "rbxassetid://701868112"
sky.SkyboxDn = "rbxassetid://701868112"
sky.SkyboxFt = "rbxassetid://701868112"
sky.SkyboxLf = "rbxassetid://701868112"
sky.SkyboxRt = "rbxassetid://701868112"
sky.SkyboxUp = "rbxassetid://701868112"
sky.CelestialBodiesShown = true
sky.Parent = Lighting

print("RockyArena built: "..#map:GetChildren().." instances. Move Spawn as needed.")
