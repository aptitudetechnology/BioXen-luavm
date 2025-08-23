"""
Core Lua process management for individual VM instances.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Union, Dict, Any
from .exceptions import (
    LuaProcessError, 
    LuaNotFoundError, 
    ScriptGenerationError
)
from .interactive_session import InteractiveSession
from .logger import VMLogger


class LuaProcess:
    """
    Manages a single Lua interpreter subprocess.
    
    This class handles the execution of Lua code through subprocess calls,
    supporting both string execution and script file execution.
    """
    
    def __init__(self, name: str = "LuaVM", lua_executable: str = "lua", debug_mode: bool = False):
        """
        Initialize a Lua process manager.
        
        Args:
            name: Human-readable name for this VM instance
            lua_executable: Path to Lua interpreter (default: "lua")
            debug_mode: Enable debug logging output
        """
        self.name = name
        self.lua_executable = lua_executable
        self.debug_mode = debug_mode
        self.logger = VMLogger(debug_mode=debug_mode, component="LuaProcess")
        self._temp_scripts = []  # Track temporary script files for cleanup
        self._interactive_session: Optional[InteractiveSession] = None
        
        self.logger.debug(f"Initializing LuaProcess: name='{name}', executable='{lua_executable}'")
        
        # Verify Lua is available
        self._verify_lua_available()
        
    # --- Interactive Session Methods ---
    def start_interactive_session(self):
        """Start a persistent interactive Lua interpreter session."""
        self.logger.debug("Starting interactive session")
        if self._interactive_session and self._interactive_session.is_running():
            raise LuaProcessError("Interactive session already running")
        self._interactive_session = InteractiveSession(
            lua_executable=self.lua_executable, 
            name=self.name,
            debug_mode=self.debug_mode
        )
        self._interactive_session.start()
        self.logger.debug("Interactive session started successfully")

    def stop_interactive_session(self):
        """Stop the interactive Lua interpreter session."""
        self.logger.debug("Stopping interactive session")
        if self._interactive_session:
            self._interactive_session.stop()
            self._interactive_session = None
            self.logger.debug("Interactive session stopped")

    def send_input(self, input_str: str):
        """Send input to the interactive Lua interpreter session."""
        self.logger.debug(f"Sending input to interactive session: '{input_str[:50]}{'...' if len(input_str) > 50 else ''}'")
        if not self._interactive_session or not self._interactive_session.is_running():
            raise LuaProcessError("Interactive session not running")
        self._interactive_session.send_input(input_str)

    def read_output(self, timeout: float = 0.1) -> Optional[str]:
        """Read output from the interactive Lua interpreter session."""
        self.logger.debug(f"Reading output from interactive session (timeout={timeout})")
        if not self._interactive_session or not self._interactive_session.is_running():
            raise LuaProcessError("Interactive session not running")
        output = self._interactive_session.read_output(timeout=timeout)
        if output:
            self.logger.debug(f"Read output: '{output[:100]}{'...' if len(output) > 100 else ''}'")
        return output

    def is_interactive_running(self) -> bool:
        """Check if the interactive session is running."""
        is_running = self._interactive_session is not None and self._interactive_session.is_running()
        self.logger.debug(f"Interactive session running status: {is_running}")
        return is_running
    
    def _verify_lua_available(self) -> None:
        """Check if Lua interpreter is available in PATH."""
        self.logger.debug(f"Verifying Lua executable availability: '{self.lua_executable}'")
        try:
            result = subprocess.run(
                [self.lua_executable, "-v"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode != 0:
                self.logger.debug(f"Lua verification failed with return code {result.returncode}: {result.stderr}")
                raise LuaNotFoundError(f"Lua interpreter check failed: {result.stderr}")
            self.logger.debug(f"Lua verification successful: {result.stdout.strip()}")
        except FileNotFoundError:
            self.logger.debug(f"Lua executable not found in PATH: '{self.lua_executable}'")
            raise LuaNotFoundError(f"Lua executable '{self.lua_executable}' not found in PATH")
        except subprocess.TimeoutExpired:
            self.logger.debug(f"Lua executable verification timed out: '{self.lua_executable}'")
            raise LuaNotFoundError(f"Lua executable '{self.lua_executable}' did not respond")
    
    def execute_string(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a Lua code string.
        
        Args:
            lua_code: Lua code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        if not lua_code.strip():
            raise ValueError("Lua code cannot be empty")
        
        self.logger.debug(f"Executing Lua string (timeout={timeout}): '{lua_code[:100]}{'...' if len(lua_code) > 100 else ''}'")
        
        command = [self.lua_executable, "-e", lua_code]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            
            execution_result = {
                'stdout': result.stdout.strip() if result.stdout else "",
                'stderr': result.stderr.strip() if result.stderr else "",
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
            
            self.logger.debug(f"String execution completed: success={execution_result['success']}, return_code={result.returncode}")
            if execution_result['stderr']:
                self.logger.debug(f"String execution stderr: {execution_result['stderr']}")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            self.logger.debug(f"String execution timed out after {timeout} seconds")
            raise LuaProcessError(f"Lua execution timed out after {timeout} seconds")
        except Exception as e:
            self.logger.debug(f"String execution failed with exception: {e}")
            raise LuaProcessError(f"Failed to execute Lua code: {e}")
    
    def execute_file(self, script_path: Union[str, Path], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a Lua script file.
        
        Args:
            script_path: Path to Lua script file
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        script_path = Path(script_path)
        
        self.logger.debug(f"Executing Lua file (timeout={timeout}): '{script_path}'")
        
        if not script_path.exists():
            self.logger.debug(f"Script file not found: {script_path}")
            raise FileNotFoundError(f"Lua script not found: {script_path}")
        
        if not script_path.is_file():
            self.logger.debug(f"Path is not a file: {script_path}")
            raise ValueError(f"Path is not a file: {script_path}")
        
        command = [self.lua_executable, str(script_path)]
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            
            execution_result = {
                'stdout': result.stdout.strip() if result.stdout else "",
                'stderr': result.stderr.strip() if result.stderr else "",
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
            
            self.logger.debug(f"File execution completed: success={execution_result['success']}, return_code={result.returncode}")
            if execution_result['stderr']:
                self.logger.debug(f"File execution stderr: {execution_result['stderr']}")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            self.logger.debug(f"File execution timed out after {timeout} seconds")
            raise LuaProcessError(f"Lua script execution timed out after {timeout} seconds")
        except Exception as e:
            self.logger.debug(f"File execution failed with exception: {e}")
            raise LuaProcessError(f"Failed to execute Lua script: {e}")
    
    def execute_temp_script(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a temporary Lua script and execute it.
        
        Useful for complex multi-line Lua code that's easier to manage as a file.
        
        Args:
            lua_code: Lua code to write to temporary script
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        self.logger.debug(f"Creating and executing temporary script (timeout={timeout})")
        
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.lua',
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(lua_code)
                temp_script_path = Path(temp_file.name)
            
            self.logger.debug(f"Created temporary script: {temp_script_path}")
            
            # Track for cleanup
            self._temp_scripts.append(temp_script_path)
            
            # Execute the temporary script
            result = self.execute_file(temp_script_path, timeout=timeout)
            
            # Clean up immediately after execution
            self._cleanup_temp_script(temp_script_path)
            
            self.logger.debug("Temporary script execution completed")
            return result
            
        except Exception as e:
            self.logger.debug(f"Temporary script creation/execution failed: {e}")
            raise ScriptGenerationError(f"Failed to create/execute temporary script: {e}")
    
    def _cleanup_temp_script(self, script_path: Path) -> None:
        """Clean up a specific temporary script file."""
        self.logger.debug(f"Cleaning up temporary script: {script_path}")
        try:
            if script_path.exists():
                script_path.unlink()
                self.logger.debug(f"Successfully removed temporary script: {script_path}")
            if script_path in self._temp_scripts:
                self._temp_scripts.remove(script_path)
        except Exception as e:
            self.logger.debug(f"Warning: Could not remove temporary script {script_path}: {e}")
    
    def cleanup(self) -> None:
        """Clean up all temporary script files."""
        self.logger.debug(f"Cleaning up {len(self._temp_scripts)} temporary scripts and stopping interactive session")
        for script_path in self._temp_scripts[:]:  # Copy list to avoid modification during iteration
            self._cleanup_temp_script(script_path)
        if self._interactive_session:
            self._interactive_session.stop()
            self._interactive_session = None
        self.logger.debug("Cleanup completed")
    
    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()
    
    def __repr__(self):
        return f"LuaProcess(name='{self.name}', lua_executable='{self.lua_executable}', debug_mode={self.debug_mode})"