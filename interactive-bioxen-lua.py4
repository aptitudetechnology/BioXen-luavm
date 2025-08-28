#!/usr/bin/env python3
"""
Fixed VMCLI with proper pylua_bioxen_vm_lib integration
"""

import os
import sys
import signal
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    sys.exit(1)

try:
    # Correct pylua_bioxen_vm_lib imports
    from pylua_bioxen_vm_lib import VMManager, InteractiveSession
    from pylua_bioxen_vm_lib.exceptions import (
        InteractiveSessionError, AttachError, DetachError, 
        SessionNotFoundError, SessionAlreadyExistsError, 
        VMManagerError, LuaVMError
    )
    # Curator system imports for package management
    from pylua_bioxen_vm_lib.utils.curator import (
        Curator, get_curator, bootstrap_lua_environment, Package
    )
    from pylua_bioxen_vm_lib.env import EnvironmentManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure pylua_bioxen_vm_lib>=0.1.6 is installed:")
    print("  pip install --upgrade pylua_bioxen_vm_lib")
    sys.exit(1)


class VMStatus:
    def __init__(self, profile):
        self.profile = profile
        self.running = False
        self.attached = False
        self.pid = None
        self.created_at = datetime.now()
        self.packages_installed = 0

    def get_uptime(self) -> str:
        delta = datetime.now() - self.created_at
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{delta.days}d {hours}h {minutes}m"


class VMCLI:
    def __init__(self):
        self.vm_manager = VMManager()
        self.vm_status = {}
        
        # Initialize curator system
        self.curator = get_curator()
        self.env_manager = EnvironmentManager()

    def main_menu(self):
        while True:
            action = questionary.select(
                "⚡ ModularNucleoid CLI - VM Control",
                choices=[
                    Choice("🚀 Create new Lua VM", "create_vm"),
                    Choice("🔗 Attach to existing VM", "attach_vm"),
                    Choice("📦 Install Packages", "install_packages"),
                    Choice("👤 Manage Profiles", "setup_profile"),
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
            elif action == "env_status":
                self.show_environment_status()
            elif action == "list_vms":
                self.list_vms()
            elif action == "stop_vm":
                self.stop_vm()
            elif action == "exit":
                self.cleanup()
                sys.exit(0)

            # after each action (except long-running ones), wait for key
            if action not in ["attach_vm", "env_status", "setup_profile"]:
                questionary.press_any_key_to_continue().ask()

    def create_lua_vm(self):
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

        try:
            print(f"🔄 Creating VM '{vm_id}' with profile '{profile_name}'...")
            
            # Create interactive session
            session = self.vm_manager.create_interactive_vm(vm_id)
            
            # Track VM status
            self.vm_status[vm_id] = VMStatus(profile_name)
            self.vm_status[vm_id].running = True

            print(f"✅ VM '{vm_id}' created with profile '{profile_name}'")
            print("💡 Type 'exit' or press Ctrl+D to return to menu")
            print("-" * 70)

            # Mark as attached and enter interactive mode
            self.vm_status[vm_id].attached = True
            
            # Send welcome message
            welcome_msg = f"""
-- VM '{vm_id}' started with {profile_name} profile
print('🌙 VM ready! Type Lua commands or exit to return to menu')
"""
            self.vm_manager.send_input(vm_id, welcome_msg)
            time.sleep(0.2)
            
            print("Entering interactive session...")
            self._interactive_loop(vm_id)
            
            self.vm_status[vm_id].attached = False

        except Exception as e:
            print(f"❌ Failed to create VM: {e}")
            if vm_id in self.vm_status:
                del self.vm_status[vm_id]

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
            Choice(f"{vm_id} (Profile: {status.profile}, Uptime: {status.get_uptime()})", vm_id)
            for vm_id, status in running_vms.items()
        ]
        vm_choices.append(Choice("← Back to Menu", "back"))

        vm_id = questionary.select("Select a VM to attach:", choices=vm_choices).ask()
        if not vm_id or vm_id == "back":
            return

        try:
            print(f"🔗 Attaching to VM '{vm_id}' (Profile: {self.vm_status[vm_id].profile})")
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
        install_choice = questionary.select(
            "How would you like to install packages?",
            choices=[
                Choice("Install specific package by name", "specific"),
                Choice("Install recommended packages", "recommended"),
                Choice("Show available packages", "show_available"),
                Choice("← Back to Menu", "back")
            ],
            default="specific"
        ).ask()

        if not install_choice or install_choice == "back":
            print("↩️ Returning to main menu...")
            return

        try:
            if install_choice == "specific":
                package = questionary.text("Enter package name to install:").ask()
                if package:
                    print(f"🔄 Installing package: {package}")
                    success = self.curator.install_package(package)
                    if success:
                        print(f"✅ Successfully installed: {package}")
                    else:
                        print(f"❌ Failed to install: {package}")

            elif install_choice == "recommended":
                recommended = ["luasocket", "luafilesystem", "lua-cjson"]
                confirm = questionary.confirm(
                    f"Install recommended packages: {', '.join(recommended)}?"
                ).ask()
                
                if confirm:
                    success_count = 0
                    for pkg in recommended:
                        print(f"🔄 Installing {pkg}...")
                        if self.curator.install_package(pkg):
                            print(f"✅ {pkg} installed")
                            success_count += 1
                        else:
                            print(f"❌ {pkg} failed")
                    
                    print(f"📦 Installation complete: {success_count}/{len(recommended)} successful")

            elif install_choice == "show_available":
                try:
                    installed = self.curator.list_installed_packages()
                    print("\n📦 Currently Installed Packages:")
                    if installed:
                        for pkg in installed:
                            print(f"  • {pkg.get('name', 'unknown')} v{pkg.get('version', 'unknown')}")
                    else:
                        print("  No packages installed")
                    
                    # Show health check
                    health = self.curator.health_check()
                    print(f"\n🏥 System Health:")
                    print(f"  Lua Version: {health.get('lua_version', 'unknown')}")
                    print(f"  LuaRocks: {'Available' if health.get('luarocks_available') else 'Unavailable'}")
                    print(f"  Total Packages: {health.get('installed_packages', 0)}")
                    
                except Exception as e:
                    print(f"❌ Error showing packages: {e}")

        except Exception as e:
            print(f"❌ Package operation failed: {e}")

        input("Press Enter to return to menu...")

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