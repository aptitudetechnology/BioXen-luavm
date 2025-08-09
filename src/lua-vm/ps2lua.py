import subprocess
import sys

# --- Helper function to run Lua via subprocess ---
def run_lua_subprocess(lua_code, is_file=False):
    """
    Executes Lua code or a Lua script file using a subprocess.
    """
    print(f"\n--- Running Lua via Subprocess ---")
    try:
        if is_file:
            # Assume 'lua_script.lua' exists for this example
            # For a real scenario, you'd create this file or ensure it exists
            print(f"Executing Lua file: {lua_code}")
            command = ["lua", lua_code]
        else:
            print(f"Executing Lua command:\n{lua_code}")
            # Use -e to execute a string as a Lua chunk
            command = ["lua", "-e", lua_code]

        # Run the command, capture output and errors
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,  # Decode stdout/stderr as text
            check=False # Do not raise an exception for non-zero exit codes
        )

        if result.stdout:
            print("--- Lua STDOUT ---")
            print(result.stdout.strip())
        if result.stderr:
            print("--- Lua STDERR ---")
            print(result.stderr.strip(), file=sys.stderr)

        if result.returncode != 0:
            print(f"--- Lua Process Exited with Error Code: {result.returncode} ---", file=sys.stderr)
        else:
            print("--- Lua Process Completed Successfully ---")

    except FileNotFoundError:
        print("Error: 'lua' executable not found. Make sure Lua is installed and in your PATH.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# --- Example 1: Executing a simple Lua command string ---
run_lua_subprocess("print('Hello from Lua via subprocess!')")
run_lua_subprocess("local a = 5; local b = 3; print('Product:', a * b)")

# --- Example 2: Simulating a Lua script file execution ---
# First, create a dummy Lua script file for demonstration
lua_file_content = """
-- my_subprocess_script.lua
print("This script was run by Python's subprocess!")
function get_message()
    return "Message from Lua file."
end
print(get_message())
"""
with open("my_subprocess_script.lua", "w") as f:
    f.write(lua_file_content)

run_lua_subprocess("my_subprocess_script.lua", is_file=True)

# Clean up the dummy file
import os
os.remove("my_subprocess_script.lua")

# --- Example 3: Demonstrating a Lua error via subprocess ---
run_lua_subprocess("error('This is an intentional Lua error!')")

print("\nPython: Subprocess interactions complete.")
