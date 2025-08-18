"""
pylua-bioxen-vm: A Python library for orchestrating networked Lua virtual machines.

This library provides process-isolated Lua VMs managed from Python with built-in
networking capabilities using LuaSocket. Perfect for distributed computing,
microservices, game servers, and sandboxed scripting.
"""

from .lua_process import LuaProcess
from .networking import NetworkedLuaVM, LuaScriptTemplate, validate_port, validate_host
from .vm_manager import VMManager, VMCluster
from .exceptions import (
    LuaVMError,
    LuaProcessError, 
    NetworkingError,
    LuaNotFoundError,
    LuaSocketNotFoundError,
    VMConnectionError,
    VMTimeoutError,
    ScriptGenerationError
)

__version__ = "0.1.0"
__author__ = "pylua-bioxen-vm contributors"
__email__ = ""
__description__ = "Process-isolated networked Lua VMs managed from Python"
__url__ = "https://github.com/yourusername/pylua-bioxen-vm"

# Main exports for easy importing
__all__ = [
    # Core classes
    "LuaProcess",
    "NetworkedLuaVM", 
    "VMManager",
    "VMCluster",
    
    # Utilities
    "LuaScriptTemplate",
    "validate_port",
    "validate_host",
    
    # Exceptions
    "LuaVMError",
    "LuaProcessError",
    "NetworkingError", 
    "LuaNotFoundError",
    "LuaSocketNotFoundError",
    "VMConnectionError",
    "VMTimeoutError",
    "ScriptGenerationError",
    
    # Metadata
    "__version__",
]

# Convenience function for quick VM creation
def create_vm(vm_id: str = "default", networked: bool = False, lua_executable: str = "lua") -> LuaProcess:
    """
    Quick VM creation function.
    
    Args:
        vm_id: Unique identifier for the VM
        networked: Whether to create a networked VM with socket support
        lua_executable: Path to Lua interpreter
        
    Returns:
        The created VM instance
    """
    if networked:
        return NetworkedLuaVM(name=vm_id, lua_executable=lua_executable)
    else:
        return LuaProcess(name=vm_id, lua_executable=lua_executable)


def create_manager(max_workers: int = 10, lua_executable: str = "lua") -> VMManager:
    """
    Quick VMManager creation function.
    
    Args:
        max_workers: Maximum number of concurrent VM executions
        lua_executable: Path to Lua interpreter
        
    Returns:
        A new VMManager instance
    """
    return VMManager(max_workers=max_workers, lua_executable=lua_executable)