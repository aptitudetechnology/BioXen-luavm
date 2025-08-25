# BioXen Lua VM Manager

BioXen Lua VM Manager is an advanced interactive CLI tool for launching, managing, and monitoring process-isolated Lua virtual machines (VMs) from Python. It is designed for bioinformatics and computational biology workflows, supporting robust VM lifecycle management, package curation, and environment profiles via the `pylua_bioxen_vm_lib` library.

## Features
- **Persistent Lua VM Management:** Start, stop, attach, detach, and monitor multiple Lua VMs with hypervisor-like control.
- **Interactive Terminal Access:** Attach to running Lua VMs for real-time code execution and session management.
- **Package Curation:** Use the built-in curator system to manage Lua packages and environment profiles for specialized workflows.
- **Rich CLI UI:** Enhanced display and status reporting using the `rich` library (optional).
- **Networked VM Support:** Launch networked Lua VMs for distributed or socket-based communication.
- **Environment Validation:** Automatic checks for Lua, LuaRocks, and package health on startup.

## Requirements
- Python 3.8+
- `pylua_bioxen_vm_lib` >= 0.1.6
- `questionary` (for CLI prompts)
- `rich` (optional, for enhanced UI)
- A working Lua installation (with LuaRocks recommended)

## Installation
```bash
pip install --upgrade pylua_bioxen_vm_lib questionary rich
```

## Usage
Run the main CLI:
```bash
python3 interactive-bioxen-lua.py
```

You will be presented with a menu to:
- List running VMs
- Start new persistent VMs
- Attach/detach to VM terminals
- Stop VMs
- View detailed VM status
- Manage environment profiles and packages
- Run one-shot Lua code/scripts

## Screenshots
Below are example screenshots of the CLI in action:

### Main Menu
![Main Menu](screenshots/Screenshot%20from%202025-08-25%2013-51-32.png)

### VM Status Table
![VM Status Table](screenshots/Screenshot%20from%202025-08-25%2013-55-40.png)

### Interactive Terminal Session
![Interactive Terminal](screenshots/Screenshot%20from%202025-08-25%2013-56-10.png)

## Project Structure
- `interactive-bioxen-lua.py` — Main CLI program
- `screenshots/` — Example screenshots
- `requirements.txt` — Python dependencies

## Troubleshooting
- Ensure `pylua_bioxen_vm_lib` is installed and up to date.
- If you see import errors, check your Python environment and package installation.
- For Lua package management, ensure LuaRocks is available and configured.

## License
See LICENSE file for details.

## Author
BioXen Project Team
