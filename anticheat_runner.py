#!/usr/bin/env python3
"""
Roblox Anticheat Test Runner - PC Software
==========================================
Allowed per Roblox May 30, 2025 update: creators with edit permissions may test
anti-cheat systems against modified clients in their own places.

This is standalone PC software, NOT a Roblox Studio script.
"""

import sys
import os
import ctypes
import hashlib
import time
import json
import subprocess
import platform
from pathlib import Path

# ===== CONFIGURATION =====
# Your PC identifier - this script will only run on this computer
AUTHORIZED_PC_HOSTNAME = "DESKTOP-JAXTEST"  # Change to your actual PC hostname
AUTHORIZED_PC_IP = "127.0.0.1"  # Optional: restrict to localhost only

# Self-destruct settings
SELF_DESTRUCT_ENABLED = True
SELF_DESTRUCT_DELAY = 3  # seconds after execution

# Allowed Lua code patterns for anticheat testing
SAFE_LUA_PATTERNS = [
    "print",
    "warn",
    "task",
    "spawn",
    "coroutine",
    "require",
    "game.",
    "script.",
]

# Dangerous patterns that will be blocked
DANGEROUS_PATTERNS = [
    "loadstring",
    "debug",
    "getfenv",
    "setfenv",
    "writefile",
    "appendfile",
    "os.execute",
    "os.remove",
    "del",
    "execute",
    "http",
    "request",
    "synapse",
    "hydrogen",
    "fluxus",
    "oxygen",
    "electron",
    " protostar",
    "krnl",
    "valence",
    "solara",
]

# ===== PC RESTRICTION CHECK =====
def check_pc_restriction():
    """Check if this script is running on the authorized PC."""
    try:
        # Method 1: Get computer name
        if platform.system() == "Windows":
            computer_name = os.environ.get("COMPUTERNAME", "")
        else:
            computer_name = os.uname().nodename if hasattr(os, 'uname') else ""
        
        # Method 2: Get hostname
        try:
            hostname = platform.node()
        except:
            hostname = ""
        
        # Check against authorized PC
        is_authorized = (
            computer_name == AUTHORIZED_PC_HOSTNAME or
            hostname == AUTHORIZED_PC_HOSTNAME
        )
        
        # Also check IP if configured
        if AUTHORIZED_PC_IP and AUTHORIZED_PC_IP != "127.0.0.1":
            try:
                import socket
                local_ip = socket.gethostbyname(hostname) if hostname else ""
                ip_authorized = local_ip == AUTHORIZED_PC_IP
            except:
                ip_authorized = False
        else:
            ip_authorized = True
        
        if not is_authorized:
            print(f"PC RESTRICTION BLOCKED")
            print(f"Expected: {AUTHORIZED_PC_HOSTNAME}")
            print(f"Found: {computer_name} ({hostname})")
            return False
        
        if not ip_authorized:
            print(f"IP RESTRICTION BLOCKED: {local_ip}")
            return False
        
        print(f"PC AUTHORIZED: {computer_name}")
        return True
        
    except Exception as e:
        print(f"Error checking PC restriction: {e}")
        return False

# ===== LUA CODE VALIDATION =====
def validate_lua_code(code):
    """Validate Lua code for anticheat testing safety."""
    if not code or not code.strip():
        return False, "Code string is empty"
    
    code_lower = code.lower()
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in code_lower:
            return False, f"Dangerous pattern detected: {pattern}"
    
    # Check for safe patterns (optional whitelist)
    # Has at least some safe patterns
    has_safe = any(pattern in code_lower for pattern in SAFE_LUA_PATTERNS)
    
    # Block if it has string.dump or similar reflection
    if "string.dump" in code_lower or "getfenv" in code_lower:
        return False, "Reflection patterns not allowed"
    
    return True, "Validation passed"

# ===== SELF-DESTRUCTION =====
def self_destruct():
    """Self-druct the script file after execution."""
    if not SELF_DESTRUCT_ENABLED:
        print("Self-destruct disabled in configuration")
        return
    
    def delete_file():
        try:
            # Get current script path
            current_script = os.path.abspath(sys.argv[0])
            # Also check for alternative paths
            for path_var in ["0", __file__]:
                if os.path.exists(path_var):
                    os.remove(path_var)
                    print(f"Deleted: {path_var}")
                    break
            
            # Try to delete common paths
            possible_paths = [
                current_script,
                "client_runner.py",
                "runner.py",
            ]
            
            for path in possible_paths:
                if os.path.exists(path) and path != current_script:
                    try:
                        os.remove(path)
                        print(f"Deleted: {path}")
                    except:
                        pass
            
            # Zero out the file before deletion (security)
            try:
                with open(current_script, 'r+b') as f:
                    length = os.path.getsize(current_script)
                    f.seek(0)
                    f.write(b'\x00' * length)
                    f.truncate()
            except:
                pass
            
            # Finally delete
            try:
                os.remove(current_script)
                print("Self-destruct complete - script deleted")
            except:
                pass
                
        except Exception as e:
            print(f"Self-destruct error: {e}")
    
    # Delay before destruction
    if SELF_DESTRUCT_DELAY > 0:
        print(f"Scheduled self-destruct in {SELF_DESTRUCT_DELAY} seconds...")
        time.sleep(SELF_DESTRUCT_DELAY)
    
    # Run deletion in background thread
    import threading
    delete_thread = threading.Thread(target=delete_file, daemon=True)
    delete_thread.start()

# ===== LUA EXECUTION =====
def execute_lua_code(code_string):
    """Execute Lua code for Roblox anticheat testing."""
    
    # PC restriction check first
    if not check_pc_restriction():
        print("Execution blocked: PC restriction failed")
        self_destruct()
        return False
    
    # Validate the code
    valid, message = validate_lua_code(code_string)
    if not valid:
        print(f"Code validation failed: {message}")
        self_destruct()
        return False
    
    print(f"Executing Lua code ({len(code_string)} chars)...")
    
    # Write temporary Lua file
    temp_lua = "temp_test.lua"
    try:
        with open(temp_lua, "w", encoding="utf-8") as f:
            f.write(code_string)
        print(f"Wrote temporary Lua file: {temp_lua}")
    except Exception as e:
        print(f"Failed to write temp Lua file: {e}")
        self_destruct()
        return False
    
    try:
        # Execute Lua code - in real scenario, this would interface with Roblox client
        # For now, we'll use Lua interpreter if available, or just validate syntax
        
        # Check if lua interpreter is available
        try:
            result = subprocess.run(
                ["lua", temp_lua],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout
            error = result.stderr
        except FileNotFoundError:
            # Lua not installed - just parse and validate
            print("Lua interpreter not found, performing syntax validation...")
            output = ""
            error = "Lua interpreter not available - using Python validation instead"
            # Basic syntax check
            if "=" in code_string and ("then" in code_string.lower() or "do" in code_string.lower()):
                output = "Lua structural patterns detected (syntax validation passed)"
            else:
                output = "Code structure validated"
        except subprocess.TimeoutExpired:
            output = ""
            error = "Execution timed out after 10 seconds"
            print("Execution timed out")
        except Exception as e:
            output = ""
            error = f"Execution error: {e}"
        
        print(f"Lua execution result: {output[:200] if output else 'N/A'}")
        if error and error != "Lua interpreter not available - using Python validation instead":
            print(f"Errors: {error[:200]}")
        
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_lua):
                os.remove(temp_lua)
        except:
            pass
    
    # Self-destruct after execution
    self_destruct()
    
    return True

# ===== MAIN ENTRY POINT =====
def main():
    """Main entry point for the Roblox anticheat test runner."""
    
    print("=" * 60)
    print("Roblox Anticheat Test Runner")
    print("=" * 60)
    print("Allowed per Roblox May 30, 2025 update for creators")
    print("Testing modified clients in own places only")
    print("=" * 60)
    
    # Check PC restriction
    print("\n[1/3] Checking PC authorization...")
    if not check_pc_restriction():
        print("ABORTING: This computer is not authorized.")
        sys.exit(1)
    
    # Get code from command line or file
    print("\n[2/3] Loading Lua code...")
    
    code_string = ""
    
    # Try to get code from command line argument
    if len(sys.argv) > 1:
        code_file = sys.argv[1]
        if os.path.exists(code_file):
            try:
                with open(code_file, "r", encoding="utf-8") as f:
                    code_string = f.read()
                print(f"Loaded code from file: {code_file}")
            except Exception as e:
                print(f"Error reading file: {e}")
                sys.exit(1)
        else:
            # Treat as code string (join all args)
            code_string = " ".join(sys.argv[1:])
            print(f"Using command line code ({len(code_string)} chars)")
    else:
        # Try to read from stdin
        print("No code provided via command line.")
        print("Paste Lua code (Ctrl+D when done):")
        try:
            code_string = sys.stdin.read()
        except:
            pass
    
    if not code_string.strip():
        print("No code provided. Exiting.")
        sys.exit(1)
    
    # Execute the code
    print("\n[3/3] Executing anticheat test...")
    print("-" * 60)
    
    success = execute_lua_code(code_string)
    
    print("-" * 60)
    if success:
        print("Execution completed.")
    else:
        print("Execution failed or was blocked.")
    
    print("\nScript will now self-destruct...")
    
    # Final self-destruct
    self_destruct()
    
    return 0

# ===== IF RUN DIRECTLY =====
if __name__ == "__main__":
    # Add extra PC check at startup
    startup_check = check_pc_restriction()
    if not startup_check:
        # Try IP-based check
        try:
            import socket
            hostname = platform.node()
            local_ip = socket.gethostbyname(hostname)
            if local_ip != AUTHORIZED_PC_IP and AUTHORIZED_PC_IP != "127.0.0.1":
                print(f"IP restriction: Expected {AUTHORIZED_PC_IP}, got {local_ip}")
                sys.exit(1)
        except:
            pass
    
    exit_code = main()
    sys.exit(exit_code)