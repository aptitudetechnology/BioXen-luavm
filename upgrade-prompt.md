I'm adding hypervisor-like management to the BioXen-luavm CLI to control persistent Lua VMs with interactive terminal access. The underlying pylua-bioxen-vm library has been updated with interactive capabilities.

REQUIRED FILES TO UPDATE:
1. interactive-bioxen-lua.py - Add new menu options for hypervisor commands (list VMs, start persistent VM, attach/detach terminal, stop VM, VM status)
2. InteractiveBioXen class - Add methods for VM lifecycle management, terminal attachment, and status monitoring
3. Update main menu system - Add hypervisor-style commands alongside existing one-shot execution options
4. Add terminal passthrough functionality - Raw terminal mode when attached to VM console
5. Any configuration files - Add settings for persistent VM management

NEW CLI COMMANDS TO IMPLEMENT:
- List running VMs with status
- Start persistent Lua VM (keeps running in background)
- Attach to VM terminal (interactive console access)
- Detach from VM terminal (return to main menu, VM stays running)
- Stop persistent VM
- Show VM resource usage and status
- Background monitoring of VM states

The goal is to provide Docker-like or hypervisor-like VM management through an enhanced interactive CLI while maintaining existing functionality.

Please help me implement these CLI enhancements for hypervisor-style Lua VM management.