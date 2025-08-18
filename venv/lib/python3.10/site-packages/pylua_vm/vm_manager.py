"""
High-level VM manager for orchestrating multiple Lua VMs.

This module provides the main interface for creating, managing, and coordinating
multiple networked Lua VMs.
"""

import threading
import time
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future

from .lua_process import LuaProcess
from .networking import NetworkedLuaVM
from .exceptions import LuaVMError, VMConnectionError


class VMManager:
    """
    High-level manager for multiple Lua VMs.
    
    Handles creation, lifecycle management, and coordination of Lua VMs
    with support for both basic and networked VMs.
    """
    
    def __init__(self, max_workers: int = 10, lua_executable: str = "lua"):
        """
        Initialize the VM manager.
        
        Args:
            max_workers: Maximum number of concurrent VM executions
            lua_executable: Path to Lua interpreter
        """
        self.max_workers = max_workers
        self.lua_executable = lua_executable
        self.vms: Dict[str, LuaProcess] = {}
        self.futures: Dict[str, Future] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
    
    def create_vm(self, vm_id: str, networked: bool = False) -> LuaProcess:
        """
        Create a new Lua VM.
        
        Args:
            vm_id: Unique identifier for the VM
            networked: Whether to create a networked VM with socket support
            
        Returns:
            The created VM instance
        """
        if vm_id in self.vms:
            raise ValueError(f"VM with ID '{vm_id}' already exists")
        
        with self._lock:
            if networked:
                vm = NetworkedLuaVM(name=vm_id, lua_executable=self.lua_executable)
            else:
                vm = LuaProcess(name=vm_id, lua_executable=self.lua_executable)
            
            self.vms[vm_id] = vm
            return vm
    
    def get_vm(self, vm_id: str) -> Optional[LuaProcess]:
        """Get a VM by ID."""
        return self.vms.get(vm_id)
    
    def list_vms(self) -> List[str]:
        """Get list of all VM IDs."""
        return list(self.vms.keys())
    
    def remove_vm(self, vm_id: str) -> bool:
        """
        Remove a VM and clean up its resources.
        
        Args:
            vm_id: ID of VM to remove
            
        Returns:
            True if VM was removed, False if VM didn't exist
        """
        with self._lock:
            vm = self.vms.pop(vm_id, None)
            if vm:
                vm.cleanup()
                
                # Cancel any running futures for this VM
                future = self.futures.pop(vm_id, None)
                if future and not future.done():
                    future.cancel()
                
                return True
            return False
    
    def execute_vm_async(self, vm_id: str, lua_code: str, 
                        timeout: Optional[float] = None) -> Future:
        """
        Execute Lua code on a VM asynchronously.
        
        Args:
            vm_id: ID of VM to execute on
            lua_code: Lua code to execute
            timeout: Maximum execution time
            
        Returns:
            Future object representing the execution
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise ValueError(f"VM '{vm_id}' not found")
        
        def execute():
            return vm.execute_string(lua_code, timeout=timeout)
        
        future = self.executor.submit(execute)
        self.futures[vm_id] = future
        return future
    
    def execute_vm_sync(self, vm_id: str, lua_code: str, 
                       timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute Lua code on a VM synchronously.
        
        Args:
            vm_id: ID of VM to execute on
            lua_code: Lua code to execute  
            timeout: Maximum execution time
            
        Returns:
            Execution result dictionary
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise ValueError(f"VM '{vm_id}' not found")
        
        return vm.execute_string(lua_code, timeout=timeout)
    
    def start_server_vm(self, vm_id: str, port: int, 
                       timeout: Optional[float] = None) -> Future:
        """
        Start a VM as a socket server asynchronously.
        
        Args:
            vm_id: ID of VM to use as server
            port: Port to bind to
            timeout: Maximum execution time
            
        Returns:
            Future object representing the server execution
        """
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        
        def start_server():
            return vm.start_server(port, timeout=timeout)
        
        future = self.executor.submit(start_server)
        self.futures[vm_id] = future
        return future
    
    def start_client_vm(self, vm_id: str, host: str, port: int, 
                       message: str = "Hello from client!", 
                       timeout: Optional[float] = None) -> Future:
        """
        Start a VM as a socket client asynchronously.
        
        Args:
            vm_id: ID of VM to use as client
            host: Server host to connect to
            port: Server port to connect to
            message: Message to send to server
            timeout: Maximum execution time
            
        Returns:
            Future object representing the client execution
        """
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        
        def start_client():
            return vm.start_client(host, port, message, timeout=timeout)
        
        future = self.executor.submit(start_client)
        self.futures[vm_id] = future
        return future
    
    def start_p2p_vm(self, vm_id: str, local_port: int,
                     peer_host: Optional[str] = None, peer_port: Optional[int] = None,
                     run_duration: int = 30, timeout: Optional[float] = None) -> Future:
        """
        Start a VM in P2P mode asynchronously.
        
        Args:
            vm_id: ID of VM to use for P2P
            local_port: Port to listen on
            peer_host: Optional peer host to connect to
            peer_port: Optional peer port to connect to  
            run_duration: How long to run P2P mode
            timeout: Maximum execution time
            
        Returns:
            Future object representing the P2P execution
        """
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        
        def start_p2p():
            return vm.start_p2p(local_port, peer_host, peer_port, run_duration, timeout=timeout)
        
        future = self.executor.submit(start_p2p)
        self.futures[vm_id] = future
        return future
    
    def wait_for_vm(self, vm_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Wait for an asynchronous VM operation to complete.
        
        Args:
            vm_id: ID of VM to wait for
            timeout: Maximum time to wait
            
        Returns:
            Result of the VM execution
        """
        future = self.futures.get(vm_id)
        if not future:
            raise ValueError(f"No running operation found for VM '{vm_id}'")
        
        return future.result(timeout=timeout)
    
    def cancel_vm(self, vm_id: str) -> bool:
        """
        Cancel a running VM operation.
        
        Args:
            vm_id: ID of VM to cancel
            
        Returns:
            True if operation was cancelled, False otherwise
        """
        future = self.futures.get(vm_id)
        if future and not future.done():
            return future.cancel()
        return False
    
    def get_vm_status(self, vm_id: str) -> Optional[str]:
        """
        Get the status of a VM's current operation.
        
        Args:
            vm_id: ID of VM to check
            
        Returns:
            Status string: 'running', 'done', 'cancelled', or None if no operation
        """
        future = self.futures.get(vm_id)
        if not future:
            return None
        
        if future.cancelled():
            return 'cancelled'
        elif future.done():
            return 'done'
        else:
            return 'running'
    
    def create_vm_cluster(self, cluster_id: str, vm_count: int, 
                         networked: bool = True) -> List[str]:
        """
        Create a cluster of VMs with consistent naming.
        
        Args:
            cluster_id: Base name for the cluster
            vm_count: Number of VMs to create
            networked: Whether to create networked VMs
            
        Returns:
            List of VM IDs created
        """
        vm_ids = []
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            self.create_vm(vm_id, networked=networked)
            vm_ids.append(vm_id)
        return vm_ids
    
    def setup_p2p_cluster(self, cluster_id: str, vm_count: int, 
                         base_port: int = 8080, run_duration: int = 60) -> List[Future]:
        """
        Set up a P2P cluster where each VM connects to the next one in a ring.
        
        Args:
            cluster_id: Base name for the cluster
            vm_count: Number of VMs in the cluster
            base_port: Starting port number
            run_duration: How long to run each P2P VM
            
        Returns:
            List of Future objects for each P2P VM
        """
        if vm_count < 2:
            raise ValueError("P2P cluster requires at least 2 VMs")
        
        # Create VMs if they don't exist
        vm_ids = []
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            if vm_id not in self.vms:
                self.create_vm(vm_id, networked=True)
            vm_ids.append(vm_id)
        
        # Start P2P VMs in a ring topology
        futures = []
        for i, vm_id in enumerate(vm_ids):
            local_port = base_port + i
            
            # Connect to the next VM in the ring
            next_i = (i + 1) % vm_count
            peer_port = base_port + next_i
            
            future = self.start_p2p_vm(
                vm_id, 
                local_port, 
                peer_host="localhost", 
                peer_port=peer_port,
                run_duration=run_duration
            )
            futures.append(future)
        
        return futures
    
    def broadcast_to_cluster(self, cluster_pattern: str, lua_code: str,
                           timeout: Optional[float] = None) -> Dict[str, Future]:
        """
        Broadcast Lua code execution to all VMs matching a pattern.
        
        Args:
            cluster_pattern: Pattern to match VM IDs (supports wildcards)
            lua_code: Lua code to execute on all matching VMs
            timeout: Maximum execution time per VM
            
        Returns:
            Dictionary mapping VM IDs to their Future objects
        """
        import fnmatch
        
        matching_vms = [vm_id for vm_id in self.vms.keys() 
                       if fnmatch.fnmatch(vm_id, cluster_pattern)]
        
        if not matching_vms:
            raise ValueError(f"No VMs found matching pattern: {cluster_pattern}")
        
        futures = {}
        for vm_id in matching_vms:
            future = self.execute_vm_async(vm_id, lua_code, timeout=timeout)
            futures[vm_id] = future
        
        return futures
    
    def wait_for_cluster(self, futures: Dict[str, Future], 
                        timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """
        Wait for multiple VM operations to complete.
        
        Args:
            futures: Dictionary mapping VM IDs to Future objects
            timeout: Maximum time to wait for all operations
            
        Returns:
            Dictionary mapping VM IDs to their execution results
        """
        results = {}
        for vm_id, future in futures.items():
            try:
                results[vm_id] = future.result(timeout=timeout)
            except Exception as e:
                results[vm_id] = {
                    'error': str(e),
                    'success': False,
                    'stdout': '',
                    'stderr': str(e),
                    'return_code': -1
                }
        return results
    
    def get_cluster_status(self, cluster_pattern: str) -> Dict[str, str]:
        """
        Get status of all VMs matching a pattern.
        
        Args:
            cluster_pattern: Pattern to match VM IDs
            
        Returns:
            Dictionary mapping VM IDs to their status
        """
        import fnmatch
        
        status = {}
        for vm_id in self.vms.keys():
            if fnmatch.fnmatch(vm_id, cluster_pattern):
                status[vm_id] = self.get_vm_status(vm_id) or 'idle'
        
        return status
    
    def cleanup_cluster(self, cluster_pattern: str) -> int:
        """
        Remove all VMs matching a pattern.
        
        Args:
            cluster_pattern: Pattern to match VM IDs
            
        Returns:
            Number of VMs removed
        """
        import fnmatch
        
        matching_vms = [vm_id for vm_id in self.vms.keys() 
                       if fnmatch.fnmatch(vm_id, cluster_pattern)]
        
        removed_count = 0
        for vm_id in matching_vms:
            if self.remove_vm(vm_id):
                removed_count += 1
        
        return removed_count
    
    def shutdown_all(self) -> None:
        """
        Shutdown all VMs and clean up resources.
        """
        # Cancel all running futures
        for future in self.futures.values():
            if not future.done():
                future.cancel()
        
        # Clean up all VMs
        for vm in self.vms.values():
            vm.cleanup()
        
        # Clear collections
        self.vms.clear()
        self.futures.clear()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the VM manager state.
        
        Returns:
            Dictionary with manager statistics
        """
        running_count = sum(1 for status in [self.get_vm_status(vm_id) for vm_id in self.vms.keys()]
                          if status == 'running')
        
        networked_count = sum(1 for vm in self.vms.values() 
                            if isinstance(vm, NetworkedLuaVM))
        
        return {
            'total_vms': len(self.vms),
            'networked_vms': networked_count,
            'basic_vms': len(self.vms) - networked_count,
            'running_operations': running_count,
            'completed_operations': len([f for f in self.futures.values() if f.done()]),
            'max_workers': self.max_workers,
            'lua_executable': self.lua_executable
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.shutdown_all()
    
    def __repr__(self):
        return (f"VMManager(vms={len(self.vms)}, "
                f"max_workers={self.max_workers}, "
                f"lua_executable='{self.lua_executable}')")


class VMCluster:
    """
    Helper class for managing a group of related VMs.
    
    Provides a higher-level interface for common cluster operations.
    """
    
    def __init__(self, manager: VMManager, cluster_id: str, vm_ids: List[str]):
        """
        Initialize a VM cluster.
        
        Args:
            manager: VMManager instance
            cluster_id: Identifier for this cluster
            vm_ids: List of VM IDs in this cluster
        """
        self.manager = manager
        self.cluster_id = cluster_id
        self.vm_ids = vm_ids
    
    def broadcast(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Future]:
        """Broadcast code execution to all VMs in cluster."""
        futures = {}
        for vm_id in self.vm_ids:
            future = self.manager.execute_vm_async(vm_id, lua_code, timeout=timeout)
            futures[vm_id] = future
        return futures
    
    def wait_all(self, futures: Dict[str, Future], 
                timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Wait for all cluster operations to complete."""
        return self.manager.wait_for_cluster(futures, timeout=timeout)
    
    def get_status(self) -> Dict[str, str]:
        """Get status of all VMs in cluster."""
        return {vm_id: self.manager.get_vm_status(vm_id) or 'idle' 
                for vm_id in self.vm_ids}
    
    def cleanup(self) -> int:
        """Remove all VMs in this cluster."""
        removed = 0
        for vm_id in self.vm_ids:
            if self.manager.remove_vm(vm_id):
                removed += 1
        return removed
    
    def __len__(self):
        return len(self.vm_ids)
    
    def __repr__(self):
        return f"VMCluster(id='{self.cluster_id}', vms={len(self.vm_ids)})"