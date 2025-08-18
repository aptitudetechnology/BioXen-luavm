"""
Custom exceptions for pylua-bioxen-vm library.
"""

class LuaVMError(Exception):
    """Base exception for all Lua VM related errors."""
    pass

class LuaProcessError(LuaVMError):
    """Raised when there's an error with Lua subprocess execution."""
    def __init__(self, message, return_code=None, stderr=None):
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr

class NetworkingError(LuaVMError):
    """Raised when there's an error with socket communication."""
    pass

class LuaNotFoundError(LuaVMError):
    """Raised when the Lua interpreter is not found in PATH."""
    pass

class LuaSocketNotFoundError(LuaVMError):
    """Raised when LuaSocket library is not available."""
    pass

class VMConnectionError(NetworkingError):
    """Raised when VM-to-VM connection fails."""
    def __init__(self, message, host=None, port=None):
        super().__init__(message)
        self.host = host
        self.port = port

class VMTimeoutError(NetworkingError):
    """Raised when VM operations timeout."""
    pass

class ScriptGenerationError(LuaVMError):
    """Raised when there's an error generating dynamic Lua scripts."""
    pass