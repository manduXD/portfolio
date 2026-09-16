-- Roblox Client Script Runner for Anticheat Testing
-- Allowed for creators with edit permissions (Roblox May 30, 2025 update)
-- Runs in actual game place, NOT within Studio editor
-- Self-destructs after execution, restricted to specific PC

--[[
  HOW TO USE:
  1. Place this Script (not LocalScript) in ServerScriptService or a Folder in your game
  2. Run from Command Bar: game:GetService("Players").LocalPlayer:GetDescendants() -- or use specific trigger
  3. Or inject via your testing executor with: loadstring(game:HttpGet("PLACEHOLDER"))()
  
  This is allowed per Roblox update: creators with edit permissions may test anti-cheat
  using modified clients in their own places.
--]]

-- Services
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")

-- ===== PC RESTRICTION CHECK =====
-- Check if running on authorized PC (hostname check)
-- Replace with your actual PC hostname/identifier
local AUTHORIZED_PC_HOSTNAME = "DESKTOP-JAXTEST"

local function checkPCRestriction()
	-- Method 1: Get computer name via environment
	local computerName = ""
	local success, result = pcall(function()
		return game:GetService("ScriptContext").ComputerName or ""
	end)
	if success then
		computerName = tostring(result)
	end
	
	-- Method 2: Check if running in Studio (block non-studio, allow only authorized PC)
	local isStudio = RunService:IsStudio()
	if isStudio then
		-- In studio, still enforce PC check
		if computerName ~= AUTHORIZED_PC_HOSTNAME then
			error("PC restriction: This computer is not authorized to run anticheat tests.")
			return false
		end
	else
		-- Not in studio: enforce strict PC check
		if computerName ~= AUTHORIZED_PC_HOSTNAME then
			warn("PC restriction: Execution blocked. This computer is not authorized.")
			return false
		end
	end
	
	return true
end

-- ===== SELF-DESTRUCTION =====
local function selfDestruct()
	-- Destroy this script and all its children
	local script = script
	if script and script.Parent then
		-- Schedule destruction to ensure code completes
		task.delay(0, function()
			script:Destroy()
		end)
	end
	
	-- Also destroy any module scripts or related scripts
	for _, child in pairs(script:GetDescendants()) do
		if child:IsA("Script") or child:IsA("LocalScript") then
			child:Destroy()
		end
	end
end

-- ===== CODE EXECUTION =====
local function executeCode(codeString)
	-- PC restriction check
	if not checkPCRestriction() then
		selfDestruct()
		return false
	end
	
	-- Validate code string
	if not codeString or type(codeString) ~= "string" or codeString:gsub("%s", "") == "" then
		warn("Invalid code string provided.")
		selfDestruct()
		return false
	end
	
	-- Strip dangerous patterns (basic safeguarding)
	local dangerousPatterns = {"loadstring", "debug", "getfenv", "setfenv", 
		"game.HttpGet", "game.GetService", "getsenv", "getupvalue"}
	
	for _, pattern in ipairs(dangerousPatterns) do
		if codeString:lower():find(pattern:lower(), 1, true) then
			warn("Dangerous pattern detected in code. Blocking execution.")
			selfDestruct()
			return false
		end
	end
	
	-- Execute the code safely
	local success, errorMessage = pcall(function()
		-- Create and run the function
		local func, loadError = loadstring(codeString)
		if loadError then
			error("Failed to load code: " .. tostring(loadError))
		end
		func()
	end)
	
	if success then
		print("Code executed successfully.")
	else
		warn("Error executing code: " .. tostring(errorMessage))
	end
	
	-- Self-destruct after execution (whether success or error)
	selfDestruct()
	return success
end

-- ===== PUBLIC INTERFACE =====
-- Expose execution function globally for command bar or executor injection
-- Usage: _G.RunAnticheatTest([=[your lua code here]=])
_G.RunAnticheatTest = executeCode

-- Also expose self-destruct command
_G.SelfDestruct = selfDestruct

-- Initialization message (only in non-studio or authorized studio)
if not RunService:IsStudio() then
	print("Client Script Runner active. PC restriction enforced.")
else
	print("Studio mode detected. PC restriction: " .. AUTHORIZED_PC_HOSTNAME)
end

-- Auto-execute if code is passed as argument (for testing workflows)
-- This script expects to be loaded/code passed externally
-- For command bar: execute directly with _G.RunAnticheatTest(code)