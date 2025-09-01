#!/usr/bin/env python3
"""
BioXen Interactive CLI v0.1.19 with pylua_bioxen_vm_lib multi-VM support
Supports Basic VMs and XCP-ng VMs (Phase 1 placeholder) using factory pattern
"""

import os
import sys
import signal
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    sys.exit(1)

try:
    # Updated imports for pylua_bioxen_vm_lib version 0.1.19
    from pylua_bioxen_vm_lib import VMManager, InteractiveSession, SessionManager, create_vm
    from pylua_bioxen_vm_lib.exceptions import (
        InteractiveSessionError, AttachError, DetachError, 
        SessionNotFoundError, SessionAlreadyExistsError, 
        VMManagerError, LuaVMError
    )
    # Updated package management imports for 0.1.19 curator system
    from pylua_bioxen_vm_lib.utils.curator import (
        Curator, get_curator, quick_install, Package
    )
    from pylua_bioxen_vm_lib.env import EnvironmentManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure pylua_bioxen_vm_lib>=0.1.19 is installed:")
    print("  pip install --upgrade pylua_bioxen_vm_lib")
    sys.exit(1)


class ConfigManager:
    """Manages configuration settings including XCP-ng credentials"""
    
    def __init__(self, config_file="bioxen_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
                return self.default_config()
        return self.default_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def default_config(self):
        """Return default configuration"""
        return {
            "xcpng": {
                "host": "192.168.1.100",
                "username": "root",
                "password": "",
                "template": "lua-bio-template",
                "save_credentials": False
            },
            "vm_defaults": {
                "profile": "standard",
                "networked": False,
                "persistent": True,
                "debug_mode": False
            }
        }
    
    def get_xcpng_config(self):
        """Get XCP-ng configuration"""
        return self.config.get("xcpng", {})
    
    def save_xcpng_config(self, host, username, password, template, save_credentials=True):
        """Save XCP-ng configuration"""
        self.config["xcpng"] = {
            "host": host,
            "username": username,
            "password": password if save_credentials else "",
            "template": template,
            "save_credentials": save_credentials
        }
        return self.save_config()
    
    def get_vm_defaults(self):
        """Get VM default settings"""
        return self.config.get("vm_defaults", {})


class VMStatus:
    def __init__(self, profile, vm_type="basic"):
        self.profile = profile
        self.vm_type = vm_type  # "basic" or "xcpng" (0.1.19 multi-VM types)
        self.running = False
        self.attached = False
        self.pid = None
        self.created_at = datetime.now()
        self.packages_installed = 0
        # XCP-ng specific fields (Phase 1 placeholder support)
        self.xcpng_config = {} if vm_type == "xcpng" else None

    def get_uptime(self) -> str:
        delta = datetime.now() - self.created_at
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{delta.days}d {hours}h {minutes}m"


class VMCLI:
    def __init__(self):
        self.vm_manager = VMManager()
        self.vm_status = {}
        self.config_manager = ConfigManager()
        
        # Initialize 0.1.19 curator system 
        self.curator = get_curator()
        self.env_manager = EnvironmentManager()

    def main_menu(self):
        print("\n[INFO] BioXen Interactive CLI started. If you do not see the menu below, check your terminal and Python environment.")
        while True:
            action = questionary.select(
                "⚡ ModularNucleoid CLI v0.1.19 - VM Control",
                choices=[
                    Choice("🚀 Create new Lua VM", "create_vm"),
                    Choice("🔗 Attach to existing VM", "attach_vm"),
                    Choice("📦 Install Packages", "install_packages"),
                    Choice("👤 Manage Profiles", "setup_profile"),
                    Choice("⚙️  Configuration Settings", "config_settings"),
                    Choice("🔧 Convert VM to Physical", "convert_vm"),
                    Choice("🖥️  Environment Status", "env_status"),
                    Choice("📋 List VMs", "list_vms"),
                    Choice("🛑 Stop VM", "stop_vm"),
                    Choice("❌ Exit", "exit")
                ]
            ).ask()

            if action == "create_vm":
                self.create_lua_vm()
            elif action == "attach_vm":
                self.attach_to_vm_terminal()
            elif action == "install_packages":
                self.install_packages()
            elif action == "setup_profile":
                self.setup_profile()
            elif action == "config_settings":
                self.manage_configuration()
            elif action == "convert_vm":
                self.convert_vm_to_physical()
            elif action == "env_status":
                self.show_environment_status()
            elif action == "list_vms":
                self.list_vms()
            elif action == "stop_vm":
                self.stop_vm()
            elif action == "exit":
                self.cleanup()
                sys.exit(0)

    def create_lua_vm(self):
        # Step 1: Choose VM type using 0.1.19 multi-VM factory pattern
        vm_type = questionary.select(
            "Select VM type:",
            choices=[
                Choice("🐍 Basic VM (subprocess-based, default)", "basic"),
                Choice("🌐 XCP-ng VM (hypervisor, Phase 1 placeholder)", "xcpng"),
                Choice("← Back to Menu", "back")
            ]
        ).ask()
        
        if not vm_type or vm_type == "back":
            return

        # Additional configuration options for 0.1.19
        networked = questionary.confirm("Enable networking capabilities?", default=False).ask()
        persistent = questionary.confirm("Enable persistent sessions?", default=True).ask()
        debug_mode = questionary.confirm("Enable debug mode?", default=False).ask()

        vm_id = questionary.text(
            "Enter VM ID (unique identifier):",
            validate=lambda x: x and x not in self.vm_status or "VM ID already exists or empty"
        ).ask()
        if not vm_id:
            return

        profile_name = questionary.text(
            "Enter profile name for this VM:",
            default="standard"
        ).ask()
        if not profile_name:
            profile_name = "standard"

        config = None
        if vm_type == "xcpng":
            # Get saved XCP-ng configuration
            saved_config = self.config_manager.get_xcpng_config()
            
            use_saved = False
            if saved_config.get("save_credentials") and saved_config.get("password"):
                use_saved = questionary.confirm(
                    f"Use saved XCP-ng credentials for {saved_config.get('host')}?", 
                    default=True
                ).ask()
            
            if use_saved:
                config = {
                    "xcpng_host": saved_config.get("host"),
                    "username": saved_config.get("username"),
                    "password": saved_config.get("password"),
                    "template": saved_config.get("template")
                }
                print(f"✅ Using saved credentials for {config['xcpng_host']}")
            else:
                # Collect XCP-ng configuration with defaults from saved config
                host = questionary.text(
                    "XCP-ng host IP:", 
                    default=saved_config.get("host", "192.168.1.100")
                ).ask()
                username = questionary.text(
                    "Username:", 
                    default=saved_config.get("username", "root")
                ).ask()
                password = questionary.password("Password:").ask()
                template = questionary.text(
                    "Template name:", 
                    default=saved_config.get("template", "lua-bio-template")
                ).ask()
                
                # Ask if user wants to save credentials
                save_creds = questionary.confirm(
                    "Save these credentials for future use?", 
                    default=False
                ).ask()
                
                config = {
                    "xcpng_host": host,
                    "username": username,
                    "password": password,
                    "template": template
                }
                
                # Save configuration if requested
                if save_creds:
                    success = self.config_manager.save_xcpng_config(
                        host, username, password, template, True
                    )
                    if success:
                        print("✅ Credentials saved to config file")
                    else:
                        print("❌ Failed to save credentials")

        if vm_type == "basic":
            self._create_basic_vm(vm_id, profile_name, networked, persistent, debug_mode)
        elif vm_type == "xcpng":
            self._create_xcpng_vm(vm_id, profile_name, config, networked, persistent, debug_mode)

    def _create_basic_vm(self, vm_id, profile_name, networked=False, persistent=True, debug_mode=False):
        """Create basic VM using 0.1.19 factory pattern"""
        try:
            print(f"🔄 Creating Basic VM '{vm_id}' with profile '{profile_name}'...")
            
            # Use 0.1.19 create_vm factory function
            vm_instance = create_vm(
                vm_id=vm_id, 
                vm_type="basic", 
                networked=networked, 
                persistent=persistent, 
                debug_mode=debug_mode
            )
            
            # Create interactive session
            session = self.vm_manager.create_interactive_vm(vm_id)
            
            # Track VM status
            self.vm_status[vm_id] = VMStatus(profile_name, "basic")
            self.vm_status[vm_id].running = True

            print(f"✅ Basic VM '{vm_id}' created with profile '{profile_name}'")
            print("💡 Use 'Attach to existing VM' to interact with this VM")
            print("-" * 70)

            # Mark as attached and enter interactive mode if requested
            attach_now = questionary.confirm("Attach to VM now?", default=True).ask()
            if attach_now:
                self.vm_status[vm_id].attached = True
                
                # Send welcome message
                welcome_msg = f"""
-- Basic VM '{vm_id}' started with {profile_name} profile
print('🌙 VM ready! Type Lua commands or exit to return to menu')
"""
                self.vm_manager.send_input(vm_id, welcome_msg)
                time.sleep(0.2)
                
                print("Entering interactive session...")
                self._interactive_loop(vm_id)
                
                self.vm_status[vm_id].attached = False

        except Exception as e:
            print(f"❌ Failed to create basic VM: {e}")
            if vm_id in self.vm_status:
                del self.vm_status[vm_id]

    def _create_xcpng_vm(self, vm_id, profile_name, config, networked=False, persistent=True, debug_mode=False):
        """Create XCP-ng VM using 0.1.19 Phase 1 placeholder"""
        try:
            print(f"🔄 Creating XCP-ng VM '{vm_id}' with profile '{profile_name}'...")
            
            # Use 0.1.19 create_vm factory function with XCP-ng type
            vm_instance = create_vm(
                vm_id=vm_id, 
                vm_type="xcpng", 
                networked=networked, 
                persistent=persistent, 
                debug_mode=debug_mode,
                config=config
            )
            
            # Track VM status with XCP-ng config
            self.vm_status[vm_id] = VMStatus(profile_name, "xcpng")
            self.vm_status[vm_id].xcpng_config = config
            
            print(f"✅ XCP-ng VM '{vm_id}' configuration saved (Phase 1 placeholder)")
            print(f"🔧 Host: {config['xcpng_host']}, Template: {config['template']}")
            print("⚠️  Note: Actual XCP-ng VM creation will be implemented in Phase 2")
            
        except NotImplementedError as e:
            print(f"⚠️  XCP-ng VM Phase 1 placeholder: {e}")
            # Still track the VM for demonstration
            self.vm_status[vm_id] = VMStatus(profile_name, "xcpng")
            self.vm_status[vm_id].xcpng_config = config
        except Exception as e:
            print(f"❌ Failed to create XCP-ng VM: {e}")
            if vm_id in self.vm_status:
                del self.vm_status[vm_id]
            # self.vm_manager.create_xen_vm(vm_id, xen_config)
            
            print(f"✅ Xen VM '{vm_id}' configuration saved")
            print(f"🔧 Memory: {xen_config['memory']}MB, vCPUs: {xen_config['vcpus']}")
            print(f"💽 Disk: {xen_config['disk_size']}GB, OS: {xen_config['os_template']}")
            print("⚠️  Note: Actual Xen VM creation to be implemented in pylua_bioxen_vm_lib")
            
        except Exception as e:
            print(f"❌ Failed to create Xen VM: {e}")
            if vm_id in self.vm_status:
                del self.vm_status[vm_id]

    def _collect_xen_config(self):
        """Collect Xen VM configuration from user"""
        print("🔧 Configuring Xen VM parameters...")
        
        # Memory configuration
        memory_choices = [
            Choice("512 MB", 512),
            Choice("1 GB", 1024), 
            Choice("2 GB", 2048),
            Choice("4 GB", 4096),
            Choice("Custom amount", "custom")
        ]
        
        memory = questionary.select(
            "Select memory allocation:",
            choices=memory_choices
        ).ask()
        
        if memory == "custom":
            memory = questionary.text(
                "Enter memory in MB:",
                validate=lambda x: x.isdigit() and int(x) > 0 or "Must be positive number"
            ).ask()
            if not memory:
                return None
            memory = int(memory)
        
        # vCPU configuration
        vcpu_choices = [
            Choice("1 vCPU", 1),
            Choice("2 vCPUs", 2),
            Choice("4 vCPUs", 4),
            Choice("Custom count", "custom")
        ]
        
        vcpus = questionary.select(
            "Select vCPU count:",
            choices=vcpu_choices
        ).ask()
        
        if vcpus == "custom":
            vcpus = questionary.text(
                "Enter vCPU count:",
                validate=lambda x: x.isdigit() and int(x) > 0 or "Must be positive number"
            ).ask()
            if not vcpus:
                return None
            vcpus = int(vcpus)
        
        # Disk configuration
        disk_choices = [
            Choice("8 GB", 8),
            Choice("16 GB", 16),
            Choice("32 GB", 32),
            Choice("64 GB", 64),
            Choice("Custom size", "custom")
        ]
        
        disk_size = questionary.select(
            "Select disk size:",
            choices=disk_choices
        ).ask()
        
        if disk_size == "custom":
            disk_size = questionary.text(
                "Enter disk size in GB:",
                validate=lambda x: x.isdigit() and int(x) > 0 or "Must be positive number"
            ).ask()
            if not disk_size:
                return None
            disk_size = int(disk_size)
        
        # OS Template
        os_choices = [
            Choice("Alpine Linux", "alpine"),
            Choice("Custom ISO", "custom")
        ]
        
        os_template = questionary.select(
            "Select OS template:",
            choices=os_choices
        ).ask()
        
        if os_template == "custom":
            iso_path = questionary.text(
                "Enter path to custom ISO:"
            ).ask()
            if not iso_path:
                return None
            os_template = f"custom:{iso_path}"
        
        # Network configuration
        network_type = questionary.select(
            "Select network configuration:",
            choices=[
                Choice("NAT (default)", "nat"),
                Choice("Bridged", "bridge"),
                Choice("Host-only", "hostonly"),
                Choice("No network", "none")
            ]
        ).ask()
        
        # Advanced options
        advanced = questionary.confirm("Configure advanced options?").ask()
        
        xen_config = {
            'memory': memory,
            'vcpus': vcpus,
            'disk_size': disk_size,
            'os_template': os_template,
            'network_type': network_type
        }
        
        if advanced:
            # Boot options
            boot_order = questionary.select(
                "Boot order:",
                choices=[
                    Choice("CD-ROM first (virtual CD-ROM, ISO file installation)", "cd")
                ]
            ).ask()
            xen_config['boot_order'] = boot_order
            
            # Console access
            console = questionary.confirm("Enable serial console access?").ask()
            xen_config['console'] = console
            
            # For headless environments, SSH is recommended for remote access.
            print("[INFO] VNC access is not available (no GUI). Use SSH for remote management.")
        
        # Summary
        print("\n📋 Xen VM Configuration Summary:")
        print(f"  Memory: {memory} MB")
        print(f"  vCPUs: {vcpus}")
        print(f"  Disk: {disk_size} GB")
        print(f"  OS: {os_template}")
        print(f"  Network: {network_type}")
        
        if advanced:
            print(f"  Boot order: {xen_config.get('boot_order', 'default')}")
            print(f"  Console: {'enabled' if xen_config.get('console') else 'disabled'}")
            print(f"  VNC: {'enabled' if xen_config.get('vnc') else 'disabled'}")
        
        confirm = questionary.confirm("Create VM with this configuration?").ask()
        if not confirm:
            return None
            
        return xen_config

    def attach_to_vm_terminal(self):
        if not self.vm_status:
            print("❌ No VMs available to attach to")
            return

        running_vms = {vm_id: status for vm_id, status in self.vm_status.items() 
                      if status.running and not status.attached}

        if not running_vms:
            print("❌ No running VMs available to attach to")
            return

        vm_choices = [
            Choice(f"{vm_id} ({status.vm_type.title()}, Profile: {status.profile}, Uptime: {status.get_uptime()})", vm_id)
            for vm_id, status in running_vms.items()
        ]
        vm_choices.append(Choice("← Back to Menu", "back"))

        vm_id = questionary.select("Select a VM to attach:", choices=vm_choices).ask()
        if not vm_id or vm_id == "back":
            return

        vm_status = self.vm_status[vm_id]
        
        if vm_status.vm_type == "xen":
            self._attach_to_xen_vm(vm_id)
        else:
            self._attach_to_subprocess_vm(vm_id)

    def _attach_to_subprocess_vm(self, vm_id):
        """Attach to subprocess-based VM"""
        try:
            print(f"🔗 Attaching to Subprocess VM '{vm_id}' (Profile: {self.vm_status[vm_id].profile})")
            print("💡 Press Ctrl+D or type 'exit' to detach and return to menu")
            print("💡 The VM will continue running after detachment")
            print("-" * 70)

            self.vm_status[vm_id].attached = True
            
            # Attach to existing session
            session = self.vm_manager.attach_to_vm(vm_id)
            
            self._interactive_loop(vm_id)
            
            self.vm_status[vm_id].attached = False
            print(f"✅ Detached from VM '{vm_id}' - VM continues running")

        except Exception as e:
            print(f"❌ Failed to attach to VM: {e}")
            self.vm_status[vm_id].attached = False

    def _attach_to_xen_vm(self, vm_id):
        """Attach to Xen-based VM (placeholder)"""
        print(f"🌐 Attaching to Xen VM '{vm_id}'...")
        print("⚠️  Xen VM attachment is a placeholder - actual implementation pending")
        
        # Show Xen VM info
        xen_config = self.vm_status[vm_id].xen_config
        print(f"🔧 VM Configuration:")
        print(f"  Memory: {xen_config.get('memory', 'unknown')} MB")
        print(f"  vCPUs: {xen_config.get('vcpus', 'unknown')}")
        print(f"  Network: {xen_config.get('network_type', 'unknown')}")
        
        # Placeholder console options
        console_choice = questionary.select(
            "Select connection method:",
            choices=[
                Choice("🖥️  Console (xl console)", "console"),
                Choice("📺 VNC Viewer", "vnc"),
                Choice("🌐 SSH Connection", "ssh"),
                Choice("← Back", "back")
            ]
        ).ask()
        
        if console_choice == "back":
            return
            
        print(f"⚠️  {console_choice.upper()} connection placeholder")
        print("Actual Xen VM interaction to be implemented")
        
        questionary.press_any_key_to_continue().ask()

    def _interactive_loop(self, vm_id):
        """Interactive loop for VM session"""
        try:
            while True:
                try:
                    user_input = input(f"lua[{vm_id}]> ")
                    
                    if user_input.strip() in ['exit', 'quit']:
                        break
                    
                    if user_input.strip():
                        self.vm_manager.send_input(vm_id, user_input + "\n")
                        time.sleep(0.1)
                        
                        # Read and display output
                        output = self.vm_manager.read_output(vm_id)
                        if output:
                            print(output.strip())
                            
                except KeyboardInterrupt:
                    print("\nUse 'exit' to detach from VM")
                except EOFError:
                    break
                    
        except Exception as e:
            print(f"Error in interactive loop: {e}")

    def install_packages(self):
        """Enhanced package installation with VM targeting"""
        # First, check available targets
        running_vms = {vm_id: status for vm_id, status in self.vm_status.items() 
                       if status.running}
        # Build target selection
        target_choices = []
        if running_vms:
            target_choices.extend([
                Choice(f"VM: {vm_id} ({status.vm_type.title()}, {status.profile} profile)", f"vm:{vm_id}")
                for vm_id, status in running_vms.items()
            ])
        target_choices.append(Choice("Global system installation", "global"))
        target_choices.append(Choice("← Back to Menu", "back"))
        # Select installation target
        target = questionary.select(
            "Where would you like to install packages?",
            choices=target_choices
        ).ask()
        if not target or target == "back":
            return
        # Parse target selection
        is_vm_install = target.startswith("vm:")
        target_vm_id = target.split(":", 1)[1] if is_vm_install else None
        
        # Check if target is Xen VM
        if is_vm_install and self.vm_status[target_vm_id].vm_type == "xen":
            print("⚠️  Package installation to Xen VMs is a placeholder")
            print("Actual Xen VM package management to be implemented")
            questionary.press_any_key_to_continue().ask()
            return
        
        # Select installation type
        install_choice = questionary.select(
            f"How would you like to install packages {'to ' + target_vm_id if is_vm_install else 'globally'}?",
            choices=[
                Choice("Install specific package by name", "specific"),
                Choice("Install recommended packages", "recommended"), 
                Choice("Show available packages", "show_available"),
                Choice("← Back", "back_to_target")
            ],
            default="specific"
        ).ask()
        if not install_choice or install_choice in ["back_to_target", "back"]:
            if install_choice == "back_to_target":
                self.install_packages()  # Restart from target selection
            return

        try:
            if install_choice == "specific":
                package = questionary.text("Enter package name to install:").ask()
                if package:
                    self._install_single_package(package, is_vm_install, target_vm_id)
            elif install_choice == "recommended":
                recommended = ["luasocket", "luafilesystem", "lua-cjson"]
                confirm = questionary.confirm(
                    f"Install recommended packages: {', '.join(recommended)}?"
                ).ask()
                if confirm:
                    self._install_multiple_packages(recommended, is_vm_install, target_vm_id)
            elif install_choice == "show_available":
                self._show_package_status(is_vm_install, target_vm_id)
        except Exception as e:
            print(f"Package operation failed: {e}")
        questionary.press_any_key_to_continue().ask()

    def _install_single_package(self, package_name, is_vm_install, target_vm_id):
        """Install a single package to VM or global using 0.1.19 quick_install"""
        if is_vm_install:
            print(f"Installing {package_name} to VM '{target_vm_id}'...")
            success = self._install_package_to_vm(package_name, target_vm_id)
            if success:
                print(f"Successfully installed {package_name} to VM '{target_vm_id}'")
                self._verify_package_in_vm(package_name, target_vm_id)
            else:
                print(f"Failed to install {package_name} to VM '{target_vm_id}'")
        else:
            print(f"Installing {package_name} globally using 0.1.19 quick_install...")
            try:
                success = quick_install(package_name)
                if success:
                    print(f"Successfully installed {package_name} globally")
                else:
                    print(f"Failed to install {package_name} globally")
            except Exception as e:
                print(f"Error installing {package_name}: {e}")

    def _install_multiple_packages(self, packages, is_vm_install, target_vm_id):
        """Install multiple packages with progress tracking using 0.1.19 APIs"""
        success_count = 0
        target_desc = f"VM '{target_vm_id}'" if is_vm_install else "globally"
        for pkg in packages:
            print(f"Installing {pkg} {target_desc}...")
            if is_vm_install:
                success = self._install_package_to_vm(pkg, target_vm_id)
            else:
                try:
                    success = quick_install(pkg)
                except Exception as e:
                    print(f"Error installing {pkg}: {e}")
                    success = False
            if success:
                print(f"{pkg} installed")
                success_count += 1
                if is_vm_install:
                    self._verify_package_in_vm(pkg, target_vm_id)
            else:
                print(f"{pkg} failed")
        print(f"Installation complete: {success_count}/{len(packages)} successful")

    def _install_package_to_vm(self, package_name, vm_id):
        """Install package directly to a specific VM"""
        try:
            # Send LuaRocks install command to VM
            install_cmd = f'os.execute("luarocks install {package_name}")\n'
            self.vm_manager.send_input(vm_id, install_cmd)
            # Wait for command to complete
            time.sleep(2.0)
            # Read output to check for success
            output = self.vm_manager.read_output(vm_id)
            # Parse output for success indicators
            if output:
                output_lower = output.lower()
                if "successfully installed" in output_lower or "is now installed" in output_lower:
                    return True
                elif "error" in output_lower or "failed" in output_lower:
                    print(f"LuaRocks error: {output.strip()}")
                    return False
            # If no clear indication, assume success (LuaRocks can be quiet on success)
            return True
        except Exception as e:
            print(f"Error installing {package_name} to VM {vm_id}: {e}")
            return False

    def _verify_package_in_vm(self, package_name, vm_id):
        """Verify package can be loaded in VM"""
        try:
            # Try to require the package
            verify_cmd = f'local ok, result = pcall(require, "{package_name}"); print("VERIFY:", ok and "SUCCESS" or "FAILED")\n'
            self.vm_manager.send_input(vm_id, verify_cmd)
            time.sleep(0.5)
            output = self.vm_manager.read_output(vm_id)
            if output and "VERIFY: SUCCESS" in output:
                print(f"Verification: {package_name} loads successfully in VM '{vm_id}'")
            elif output and "VERIFY: FAILED" in output:
                print(f"Warning: {package_name} installed but cannot be loaded in VM '{vm_id}'")
        except Exception as e:
            print(f"Could not verify {package_name} in VM {vm_id}: {e}")

    def _show_package_status(self, is_vm_install, target_vm_id):
        """Show package status for VM or global using 0.1.19 APIs"""
        try:
            if is_vm_install:
                print(f"\nChecking packages in VM '{target_vm_id}'...")
                # Send command to list installed packages in VM
                list_cmd = 'os.execute("luarocks list")\n'
                self.vm_manager.send_input(target_vm_id, list_cmd)
                time.sleep(1.5)
                output = self.vm_manager.read_output(target_vm_id)
                if output:
                    print("Installed packages in VM:")
                    print(output.strip())
                else:
                    print("No package information available")
            else:
                # Show installed packages using curator
                try:
                    installed = self.curator.list_installed_packages()
                    print("\nCurrently Installed Packages (Global):")
                    if installed:
                        for pkg in installed:
                            print(f"  • {pkg.get('name', 'unknown')} v{pkg.get('version', 'unknown')}")
                    else:
                        print("  No packages installed globally")
                except Exception as e:
                    print(f"  Error listing installed packages: {e}")
                
                # Show health check
                try:
                    health = self.curator.health_check()
                    print(f"\nSystem Health:")
                    print(f"  Lua Version: {health.get('lua_version', 'unknown')}")
                    print(f"  LuaRocks: {'Available' if health.get('luarocks_available') else 'Unavailable'}")
                    print(f"  Total Packages: {health.get('installed_packages', 0)}")
                except Exception as e:
                    print(f"  Error checking system health: {e}")
        except Exception as e:
            print(f"Error showing packages: {e}")

    def setup_profile(self):
        profile_choice = questionary.select(
            "Profile management:",
            choices=[
                Choice("Create new profile", "create"),
                Choice("Setup environment profile", "setup_env"),
                Choice("Show current profiles", "show"),
                Choice("← Back to Menu", "back")
            ]
        ).ask()

        if not profile_choice or profile_choice == "back":
            return

        if profile_choice == "create":
            profile_name = questionary.text("Enter new profile name:").ask()
            if not profile_name:
                print("❌ Profile name is required")
                return
            print(f"✅ Profile '{profile_name}' created (functionality to be implemented)")

        elif profile_choice == "setup_env":
            try:
                print("🔄 Setting up standard environment...")
                success = self.curator.curate_environment("standard")
                if success:
                    print("✅ Standard environment setup complete")
                else:
                    print("❌ Environment setup failed")
            except Exception as e:
                print(f"❌ Environment setup error: {e}")

        elif profile_choice == "show":
            print("\n👤 Available Profiles:")
            print("  • standard - Standard Lua environment")
            print("  • minimal - Minimal Lua setup")
            print("  • bioxen - Biological computation focus")
        
        questionary.press_any_key_to_continue().ask()

    def convert_vm_to_physical(self):
        """Convert a virtual Lua VM to physical hardware - UI only, calls library methods"""
        if not self.vm_status:
            print("❌ No VMs available for conversion")
            return

        # Select VM to convert
        vm_choices = [
            Choice(f"{vm_id} ({status.vm_type.title()}, Profile: {status.profile}, Status: {'Running' if status.running else 'Stopped'})", vm_id)
            for vm_id, status in self.vm_status.items()
        ]
        vm_choices.append(Choice("← Back to Menu", "back"))

        vm_id = questionary.select("Select VM to convert to physical hardware:", choices=vm_choices).ask()
        if not vm_id or vm_id == "back":
            return

        # Check if Xen VM
        vm_status = self.vm_status[vm_id]
        if vm_status.vm_type == "xen":
            print("⚠️  Xen VM to physical conversion requires different approach")
            print("Xen VMs already run on physical hardware via hypervisor")
            questionary.press_any_key_to_continue().ask()
            return

        # Select target platform
        platform_choice = questionary.select(
            "Select target platform:",
            choices=[
                Choice("eLua (Embedded Lua)", "elua"),
                Choice("Lumorphix", "lumorphix"),
                Choice("← Back", "back")
            ]
        ).ask()

        if not platform_choice or platform_choice == "back":
            return

        if platform_choice == "elua":
            self._convert_to_elua(vm_id)
        elif platform_choice == "lumorphix":
            self._convert_to_lumorphix(vm_id)

    def _convert_to_elua(self, vm_id):
        """Handle eLua conversion flow"""
        # Select target hardware
        hardware_choice = questionary.select(
            "Select eLua target hardware:",
            choices=[
                Choice("ESP32 (WiFi, Bluetooth)", "esp32"),
                Choice("ESP8266 (WiFi)", "esp8266"), 
                Choice("STM32F4 (ARM Cortex-M4)", "stm32f4"),
                Choice("STM32F1 (ARM Cortex-M3)", "stm32f1"),
                Choice("Custom target", "custom"),
                Choice("← Back", "back")
            ]
        ).ask()

        if not hardware_choice or hardware_choice == "back":
            return

        try:
            print(f"🔧 Converting VM '{vm_id}' to eLua for {hardware_choice.upper()}...")
            
            # These would be actual library calls once implemented:
            # converter = self.vm_manager.get_elua_converter()
            # result = converter.convert_vm_to_elua(vm_id, target=hardware_choice)
            
            # For now, just placeholder
            print(f"✅ eLua conversion initiated (placeholder)")
            print(f"📁 Would generate: elua_firmware_{vm_id}_{hardware_choice}.bin")
            print(f"🎯 Target: eLua on {hardware_choice.upper()}")
            print(f"⚠️  Note: Actual conversion logic to be implemented in pylua_bioxen_vm_lib")
            
        except Exception as e:
            print(f"❌ eLua conversion failed: {e}")

        questionary.press_any_key_to_continue().ask()

    def _convert_to_lumorphix(self, vm_id):
        """Handle Lumorphix conversion flow"""
        # Select target hardware
        hardware_choice = questionary.select(
            "Select Lumorphix target hardware:",
            choices=[
                Choice("Tang Nano 9k FPGA", "tang_nano_9k"),
                Choice("ELM11", "elm11"),
                Choice("← Back", "back")
            ]
        ).ask()

        if not hardware_choice or hardware_choice == "back":
            return

        try:
            print(f"🔧 Converting VM '{vm_id}' to Lumorphix for {hardware_choice.replace('_', ' ').title()}...")
            
            # These would be actual library calls once implemented:
            # converter = self.vm_manager.get_lumorphix_converter()
            # result = converter.convert_vm_to_lumorphix(vm_id, target=hardware_choice)
            
            # For now, just placeholder
            print(f"✅ Lumorphix conversion initiated (placeholder)")
            
            if hardware_choice == "tang_nano_9k":
                print(f"📁 Would generate: lumorphix_bitstream_{vm_id}_tang_nano_9k.bit")
                print(f"🎯 Target: Lumorphix on Tang Nano 9k FPGA")
                print(f"🔌 FPGA Configuration: Bitstream ready for Tang Nano 9k")
            elif hardware_choice == "elm11":
                print(f"📁 Would generate: lumorphix_firmware_{vm_id}_elm11.bin")
                print(f"🎯 Target: Lumorphix on ELM11")
                print(f"💾 Firmware: Ready for ELM11 flash")
            
            print(f"⚠️  Note: Actual conversion logic to be implemented in pylua_bioxen_vm_lib")
            
        except Exception as e:
            print(f"❌ Lumorphix conversion failed: {e}")

        questionary.press_any_key_to_continue().ask()

    def show_environment_status(self):
        print("\n🖥️  Environment Status:")
        
        # VM status
        if not self.vm_status:
            print("  📭 No VMs created yet")
        else:
            print(f"  🖥️  Active VMs: {len(self.vm_status)}")
            for vm_id, status in self.vm_status.items():
                states = []
                if status.running:
                    states.append("Running")
                if status.attached:
                    states.append("Attached")
                if not states:
                    states.append("Stopped")
                
                print(f"    • {vm_id}: Profile={status.profile}, "
                      f"Uptime={status.get_uptime()}, State={','.join(states)}")

        # Environment health
        try:
            health = self.curator.health_check()
            print(f"\n🏥 System Health:")
            print(f"  🐍 Lua Version: {health.get('lua_version', 'unknown')}")
            print(f"  📦 LuaRocks: {'Available' if health.get('luarocks_available') else 'Unavailable'}")
            print(f"  📊 Packages: {health.get('installed_packages', 0)}")
            
            errors = self.env_manager.validate_environment()
            if errors:
                print(f"  ⚠️  Issues: {len(errors)} problems detected")
            else:
                print(f"  ✅ Environment: OK")
                
        except Exception as e:
            print(f"  ❌ Health check error: {e}")
        
        questionary.press_any_key_to_continue().ask()


    def list_vms(self):
        if not self.vm_status:
            print("📭 No VMs created")
            return

        print("\n🖥️  VM List:")
        print("-" * 80)
        
        for vm_id, status in self.vm_status.items():
            state_indicators = []
            if status.running:
                state_indicators.append("🟢 Running")
            else:
                state_indicators.append("🔴 Stopped")
            
            if status.attached:
                state_indicators.append("🔗 Attached")
            
            print(f"VM ID: {vm_id}")
            print(f"  Profile: {status.profile}")
            print(f"  Status: {' '.join(state_indicators)}")
            print(f"  Created: {status.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Uptime: {status.get_uptime()}")
            print()

        questionary.press_any_key_to_continue().ask()

    def stop_vm(self):
        if not self.vm_status:
            print("📭 No VMs to stop")
            return

        running_vms = {vm_id: status for vm_id, status in self.vm_status.items() 
                      if status.running}

        if not running_vms:
            print("📭 No running VMs to stop")
            return

        vm_choices = [
            Choice(f"{vm_id} (Profile: {status.profile})", vm_id)
            for vm_id, status in running_vms.items()
        ]
        vm_choices.append(Choice("← Back to Menu", "back"))

        vm_id = questionary.select("Select VM to stop:", choices=vm_choices).ask()
        if not vm_id or vm_id == "back":
            return

        confirm = questionary.confirm(
            f"Stop VM '{vm_id}'? This will terminate the session."
        ).ask()

        if not confirm:
            return

        try:
            self.vm_manager.terminate_vm_session(vm_id)
            del self.vm_status[vm_id]
            print(f"✅ VM '{vm_id}' stopped and removed")
        except Exception as e:
            print(f"❌ Failed to stop VM: {e}")
            
        questionary.press_any_key_to_continue().ask()

    def manage_configuration(self):
        """Manage application configuration settings"""
        while True:
            config_action = questionary.select(
                "⚙️  Configuration Settings",
                choices=[
                    Choice("🌐 XCP-ng Credentials", "xcpng_creds"),
                    Choice("🎯 VM Default Settings", "vm_defaults"),
                    Choice("📄 View Current Config", "view_config"),
                    Choice("🗑️  Clear Saved Credentials", "clear_creds"),
                    Choice("← Back to Main Menu", "back")
                ]
            ).ask()

            if not config_action or config_action == "back":
                break

            if config_action == "xcpng_creds":
                self._manage_xcpng_credentials()
            elif config_action == "vm_defaults":
                self._manage_vm_defaults()
            elif config_action == "view_config":
                self._view_configuration()
            elif config_action == "clear_creds":
                self._clear_credentials()

    def _manage_xcpng_credentials(self):
        """Manage XCP-ng credentials"""
        saved_config = self.config_manager.get_xcpng_config()
        
        print("\n🌐 XCP-ng Credentials Management")
        print("-" * 40)
        
        if saved_config.get("save_credentials"):
            print(f"Current Host: {saved_config.get('host', 'Not set')}")
            print(f"Username: {saved_config.get('username', 'Not set')}")
            print(f"Template: {saved_config.get('template', 'Not set')}")
            print(f"Password: {'Saved' if saved_config.get('password') else 'Not saved'}")
        else:
            print("No credentials currently saved")
        
        # Allow editing
        edit = questionary.confirm("Edit XCP-ng credentials?", default=True).ask()
        if not edit:
            return
        
        host = questionary.text(
            "XCP-ng host IP:", 
            default=saved_config.get("host", "192.168.1.100")
        ).ask()
        username = questionary.text(
            "Username:", 
            default=saved_config.get("username", "root")
        ).ask()
        password = questionary.password("Password:").ask()
        template = questionary.text(
            "Template name:", 
            default=saved_config.get("template", "lua-bio-template")
        ).ask()
        
        save_creds = questionary.confirm(
            "Save these credentials?", 
            default=True
        ).ask()
        
        if save_creds:
            success = self.config_manager.save_xcpng_config(
                host, username, password, template, True
            )
            if success:
                print("✅ XCP-ng credentials saved successfully")
            else:
                print("❌ Failed to save credentials")
        
        questionary.press_any_key_to_continue().ask()

    def _manage_vm_defaults(self):
        """Manage VM default settings"""
        defaults = self.config_manager.get_vm_defaults()
        
        print("\n🎯 VM Default Settings")
        print("-" * 30)
        
        profile = questionary.text(
            "Default profile:", 
            default=defaults.get("profile", "standard")
        ).ask()
        
        networked = questionary.confirm(
            "Enable networking by default?", 
            default=defaults.get("networked", False)
        ).ask()
        
        persistent = questionary.confirm(
            "Enable persistent sessions by default?", 
            default=defaults.get("persistent", True)
        ).ask()
        
        debug_mode = questionary.confirm(
            "Enable debug mode by default?", 
            default=defaults.get("debug_mode", False)
        ).ask()
        
        # Update config
        self.config_manager.config["vm_defaults"] = {
            "profile": profile,
            "networked": networked,
            "persistent": persistent,
            "debug_mode": debug_mode
        }
        
        if self.config_manager.save_config():
            print("✅ VM defaults saved successfully")
        else:
            print("❌ Failed to save VM defaults")
        
        questionary.press_any_key_to_continue().ask()

    def _view_configuration(self):
        """View current configuration"""
        print("\n📄 Current Configuration")
        print("=" * 50)
        print(json.dumps(self.config_manager.config, indent=2))
        questionary.press_any_key_to_continue().ask()

    def _clear_credentials(self):
        """Clear saved credentials"""
        confirm = questionary.confirm(
            "Clear all saved credentials? This cannot be undone.", 
            default=False
        ).ask()
        
        if confirm:
            self.config_manager.config = self.config_manager.default_config()
            if self.config_manager.save_config():
                print("✅ All credentials cleared")
            else:
                print("❌ Failed to clear credentials")
        
        questionary.press_any_key_to_continue().ask()

    def cleanup(self):
        print("\n🧹 Cleaning up running VMs...")
        for vm_id in list(self.vm_status.keys()):
            if self.vm_status[vm_id].running:
                try:
                    self.vm_manager.terminate_vm_session(vm_id)
                    print(f"✅ VM {vm_id} terminated")
                except Exception as e:
                    print(f"⚠️  Could not terminate VM {vm_id}: {e}")
        self.vm_status.clear()


if __name__ == "__main__":
    try:
        cli = VMCLI()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()