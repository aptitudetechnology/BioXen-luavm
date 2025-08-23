#!/usr/bin/env python3
"""
Enhanced Interactive BioXen CLI with hypervisor-like VM management capabilities.
UPGRADED for pylua_bioxen_vm_lib v0.1.6 with curator package management system.
Maintains existing functionality while adding intelligent package curation.
"""

class EnhancedInteractiveBioXen:
    """Enhanced Interactive BioXen with hypervisor-like VM management, persistent VM control, and curator integration"""

    def __init__(self):
        self.vm_manager = VMManager()
        self.vm_status: Dict[str, VMStatus] = {}
        self.console = Console() if RICH_AVAILABLE else None
        self.terminal_manager = TerminalManager()
        self.monitoring_active = False
        self.monitor_thread = None

        # Curator system
        self.curator = get_curator()
        self.env_manager = EnvironmentManager()
        self.curator.catalog.update(BIOXEN_PACKAGES)
        if "profiles" not in self.curator.manifest:
            self.curator.manifest["profiles"] = {}
        for profile_name, profile_info in BIOXEN_PROFILES.items():
            self.curator.manifest["profiles"][profile_name] = profile_info["packages"]
        self.curator._save_manifest()
        self._validate_environment()

    def _validate_environment(self):
        print("🔍 Validating BioXen environment...")
        try:
            errors = self.env_manager.validate_environment()
            if errors:
                print(f"⚠️ Environment issues detected: {len(errors)} problems")
                for error in errors[:3]:
                    print(f"   • {error}")
                if len(errors) > 3:
                    print(f"   • ... and {len(errors) - 3} more issues")
            else:
                print("✅ Environment validation passed")
            health = self.curator.health_check()
            if health.get("luarocks_available"):
                print("✅ LuaRocks package manager available")
            else:
                print("⚠️ LuaRocks not available - package management limited")
            print(f"📦 {health.get('installed_packages', 0)} packages currently installed")
            print(f"🐍 Lua version: {health.get('lua_version', 'unknown')}")
        except Exception as e:
            print(f"⚠️ Environment validation error: {e}")
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️ 'rich' library not available. Install with: pip install rich for enhanced display")


# BioXen-specific package collections
BIOXEN_PACKAGES = {
    "bio-utils": Package("bio-utils", category="biology", priority=9,
                        description="Essential biological data processing utilities"),
    "sequence-parser": Package("sequence-parser", category="biology", priority=8,
                              description="DNA/RNA/protein sequence parsing and analysis"),
    "phylo-tree": Package("phylo-tree", category="biology", priority=7,
                         description="Phylogenetic tree construction and analysis"),
    "blast-parser": Package("blast-parser", category="biology", priority=6,
                           description="BLAST output parsing and analysis"),
    "genome-tools": Package("genome-tools", category="biology", priority=7,
                           description="Genome assembly and annotation tools"),
    "protein-fold": Package("protein-fold", category="biology", priority=5,
                           description="Protein structure prediction utilities"),
}

# BioXen environment profiles
BIOXEN_PROFILES = {
    "bioxen-minimal": {
        "packages": ["lua-cjson", "luafilesystem", "bio-utils"],
        "description": "Minimal BioXen environment with core biological tools"
    },

    # Proper import block
    import sys
    import os
    import time
    import threading
    import signal
    import termios
    import tty
    import select
    from pathlib import Path
    from datetime import datetime
    from typing import Dict, List, Optional, Any
    from dataclasses import dataclass

    # Add src to path for imports
    sys.path.insert(0, str(Path(__file__).parent / 'src'))

    try:
        import questionary
        from questionary import Choice
    except ImportError:
        print("❌ questionary not installed. Install with: pip install questionary")

        # Proper import block
        import sys
        import os
        import time
        import threading
        import signal
        import termios
        import tty
        import select
        from pathlib import Path
        from datetime import datetime
        from typing import Dict, List, Optional, Any
        from dataclasses import dataclass

        # Add src to path for imports
        sys.path.insert(0, str(Path(__file__).parent / 'src'))

        try:
            import questionary
            from questionary import Choice
        except ImportError:
            print("❌ questionary not installed. Install with: pip install questionary")

            # Proper import block
            import sys
            import os
            import time
            import threading
            import signal
            import termios
            import tty
            import select
            from pathlib import Path
            from datetime import datetime
            from typing import Dict, List, Optional, Any
            from dataclasses import dataclass

            # Add src to path for imports
            sys.path.insert(0, str(Path(__file__).parent / 'src'))

            try:
                import questionary
                from questionary import Choice
            except ImportError:
                print("❌ questionary not installed. Install with: pip install questionary")
                sys.exit(1)

            try:
                # New v0.1.6 imports with curator system
                from pylua_bioxen_vm_lib import VMManager, InteractiveSession, SessionManager
                from pylua_bioxen_vm_lib.vm_manager import VMCluster
                from pylua_bioxen_vm_lib.networking import NetworkedLuaVM, validate_host, validate_port
                from pylua_bioxen_vm_lib.lua_process import LuaProcess
                from pylua_bioxen_vm_lib.exceptions import (
                    InteractiveSessionError, AttachError, DetachError, 
                    SessionNotFoundError, SessionAlreadyExistsError, 
                    VMManagerError, ProcessRegistryError, LuaProcessError,
                    NetworkingError, LuaVMError
                )
                # Curator system imports
                from pylua_bioxen_vm_lib.utils.curator import (
                    Curator, get_curator, bootstrap_lua_environment, Package
                )
                from pylua_bioxen_vm_lib.env import EnvironmentManager
            except ImportError as e:
                print(f"❌ Import error: {e}")
                print("Make sure pylua_bioxen_vm_lib>=0.1.6 is installed:")
                print("  pip install --upgrade pylua_bioxen_vm_lib")
                sys.exit(1)

            try:
                from rich.console import Console
                from rich.table import Table
                from rich.live import Live
                from rich.panel import Panel
                from rich.text import Text
                from rich.progress import Progress, SpinnerColumn, TextColumn
                RICH_AVAILABLE = True
            except ImportError:
                RICH_AVAILABLE = False
                print("⚠️ 'rich' library not available. Install with: pip install rich for enhanced display")

            # ...existing code...
            def main_menu(self):
                """Enhanced main menu with hypervisor and package management commands"""
                try:
                    while True:
                        print("\n" + "="*70)
                        print("🌙 BioXen Lua VM Manager - Enhanced Hypervisor & Package Management Interface")
                        print("="*70)

                        # Show quick status
                        if self.vm_status:
                            running_count = len(self.vm_status)
                            attached_count = sum(1 for status in self.vm_status.values() if status.attached)
                            print(f"📊 Status: {running_count} VMs running, {attached_count} attached")
                            print("-" * 70)

                        choices = [
                            # Hypervisor commands
                            Choice("🖥️  List Persistent VMs", "list_vms"),
                            Choice("🚀 Start Persistent VM", "start_vm"),
                            Choice("🔗 Attach to VM Terminal", "attach_vm"),
                            Choice("↩️  Detach from VM", "detach_vm"),
                            Choice("🛑 Stop Persistent VM", "stop_vm"),
                            Choice("📊 VM Detailed Status", "vm_status"),
                            Choice("────────────────────", "separator"),
                            # Package management commands
                            Choice("🌱 Show Environment & Package Status", "env_status"),
                            Choice("🎯 Setup Environment Profile", "setup_profile"),
                            Choice("📦 Install Packages", "install_packages"),
                            Choice("────────────────────", "separator2"),
                            # Original functionality
                            Choice("🌙 One-shot Lua VM (Original)", "create_lua_vm"),
                            Choice("────────────────────", "separator3"),
                            Choice("❌ Exit", "exit"),
                        ]

                        action = questionary.select(
                            "Select an action:",
                            choices=choices,
                            use_shortcuts=True
                        ).ask()

                        if action is None or action == "exit":
                            print("🛑 Stopping all persistent VMs...")
                            self.cleanup_all_vms()
                            print("👋 Goodbye!")
                            break

                        # Handle separator selections
                        if action in ["separator", "separator2", "separator3"]:
                            continue

                        try:
                            if action == "list_vms":
                                self.list_persistent_vms()
                            elif action == "start_vm":
                                self.start_persistent_vm()
                            elif action == "attach_vm":
                                self.attach_to_vm_terminal()
                            elif action == "detach_vm":
                                self.detach_from_vm()
                            elif action == "stop_vm":
                                self.stop_persistent_vm()
                            elif action == "vm_status":
                                self.show_vm_detailed_status()
                            elif action == "env_status":
                                self.show_environment_status()
                            elif action == "setup_profile":
                                self.setup_environment_profile()
                            elif action == "install_packages":
                                self.install_packages()
                            elif action == "create_lua_vm":
                                self.create_lua_vm()

                        except KeyboardInterrupt:
                            print("\n\n⚠️ Operation cancelled by user")
                            continue
                        except Exception as e:
                            print(f"\n❌ Error: {e}")
                            import traceback
                            traceback.print_exc()

                        if action not in ["attach_vm", "env_status", "setup_profile", "install_packages"]:
                            questionary.press_any_key_to_continue().ask()

                except KeyboardInterrupt:
                    print("\n\n🛑 Shutting down...")
                    self.cleanup_all_vms()
                except Exception as e:
                    print(f"\n❌ Fatal error: {e}")
                    self.cleanup_all_vms()
            
        except Exception as e:
            print(f"⚠️ Environment validation error: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_all_vms()
    
    def cleanup_all_vms(self):
        """Clean up all managed VMs on exit"""
        for vm_id in list(self.vm_status.keys()):
            try:
                self.vm_manager.terminate_vm_session(vm_id)
            except:
                pass
        self.vm_status.clear()
    
    # ============ NEW CURATOR COMMANDS ============
    
    def show_environment_status(self):
        """Show comprehensive environment and package status"""
        print("\n" + "="*70)
        print("🌱 BioXen Environment & Package Status")
        print("="*70)
        
        # Environment health
        try:
            health = self.curator.health_check()
            errors = self.env_manager.validate_environment()
            
            print(f"🐍 Lua Version: {health.get('lua_version', 'unknown')}")
            print(f"📦 LuaRocks Available: {'✅ Yes' if health.get('luarocks_available') else '❌ No'}")
            print(f"📊 Installed Packages: {health.get('installed_packages', 0)}")
            print(f"🔧 Environment Issues: {len(errors) if errors else 0}")
            
            if errors:
                print("\n⚠️ Environment Issues:")
                for error in errors[:5]:
                    print(f"   • {error}")
                if len(errors) > 5:
                    print(f"   • ... and {len(errors) - 5} more")
            
        except Exception as e:
            print(f"❌ Error getting environment status: {e}")
        
        # Available profiles
        print(f"\n🎯 Available BioXen Profiles:")
        for profile_name, profile_info in BIOXEN_PROFILES.items():
            package_count = len(profile_info["packages"])
            print(f"   • {profile_name}: {package_count} packages - {profile_info['description']}")
        
        # Installed packages
        try:
            installed = self.curator.list_installed_packages()
            if installed:
                print(f"\n📦 Currently Installed Packages ({len(installed)}):")
                # Group by category
                by_category = {}
                for pkg in installed:
                    category = pkg.get("category", "unknown")
                    if category not in by_category:
                        by_category[category] = []
                    by_category[category].append(pkg)
                
                for category, pkgs in sorted(by_category.items()):
                    print(f"   {category.title()}:")
                    for pkg in pkgs[:3]:  # Show first 3 in each category
                        print(f"     • {pkg['name']} v{pkg['version']}")
                    if len(pkgs) > 3:
                        print(f"     • ... and {len(pkgs) - 3} more")
            else:
                print("\n📦 No packages currently installed")
                
        except Exception as e:
            print(f"❌ Error listing packages: {e}")
    
    def setup_environment_profile(self):
        """Setup or switch to a different environment profile"""
        print("\n🎯 Environment Profile Setup")
        
        # Show current profile if available
        current_profile = getattr(self.env_manager, 'profile', 'unknown')
        print(f"Current profile: {current_profile}")
        
        # Profile selection
        profile_choices = []
        for profile_name, profile_info in BIOXEN_PROFILES.items():
            package_count = len(profile_info["packages"])
            choice_text = f"{profile_name} ({package_count} packages) - {profile_info['description']}"
            profile_choices.append(Choice(choice_text, profile_name))
        
        profile_choices.append(Choice("← Back to Menu", "back"))
        
        selected_profile = questionary.select(
            "Select BioXen environment profile:",
            choices=profile_choices
        ).ask()
        
        if not selected_profile or selected_profile == "back":
            return
        
        try:
            print(f"\n🔄 Setting up {selected_profile} environment...")
            
            # Use curator to setup the profile
            success = self.curator.curate_environment(selected_profile)
            
            if success:
                print(f"✅ {selected_profile} environment setup complete!")
                
                # Show what was installed
                packages = BIOXEN_PROFILES[selected_profile]["packages"]
                print(f"📦 Installed {len(packages)} packages:")
                for pkg in packages:
                    print(f"   • {pkg}")
                
                # Update environment manager profile
                self.env_manager.profile = selected_profile
                
                # Get recommendations for additional packages
                recommendations = self.curator.get_recommendations()
                if recommendations:
                    print(f"\n💡 Recommended additional packages:")
                    for rec in recommendations[:3]:
                        print(f"   • {rec.name}: {rec.description}")
                
            else:
                print(f"❌ Failed to setup {selected_profile} environment")
                print("Check environment status for details")
                
        except Exception as e:
            print(f"❌ Error setting up environment: {e}")
    
    def install_packages(self):
        """Install additional packages"""
        print("\n📦 Package Installation")
        
        try:
            # Show package recommendations first
            recommendations = self.curator.get_recommendations()
            installed = self.curator.list_installed_packages()
            installed_names = {pkg["name"] for pkg in installed}
            
            if recommendations:
                print("💡 Recommended packages:")
                for i, rec in enumerate(recommendations[:5], 1):
                    status = "✅ Installed" if rec.name in installed_names else "⬜ Available"
                    print(f"   {i}. {rec.name} - {rec.description} ({status})")
            
            # Installation options
            install_choice = questionary.select(
                "How would you like to install packages?",
                choices=[
                    Choice("Install recommended package", "recommended"),
                    Choice("Install specific package by name", "specific"),
                    Choice("Install all recommendations", "all_recommended"),
                    Choice("← Back to Menu", "back")
                ]
            ).ask()
            
            if not install_choice or install_choice == "back":
                return
            
            if install_choice == "recommended" and recommendations:
                # Select from recommendations
                rec_choices = []
                for rec in recommendations:
                    if rec.name not in installed_names:
                        rec_choices.append(Choice(f"{rec.name} - {rec.description}", rec.name))
                
                if not rec_choices:
                    print("✅ All recommended packages already installed!")
                    return
                
                package_name = questionary.select(
                    "Select package to install:",
                    choices=rec_choices
                ).ask()
                
                if package_name:
                    success = self.curator.install_package(package_name)
                    if success:
                        print(f"✅ Successfully installed {package_name}")
                    else:
                        print(f"❌ Failed to install {package_name}")
            
            elif install_choice == "specific":
                package_name = questionary.text("Enter package name to install:").ask()
                if package_name:
                    version = questionary.text(
                        "Enter version constraint (or 'latest'):", 
                        default="latest"
                    ).ask()
                    
                    success = self.curator.install_package(package_name, version or "latest")
                    if success:
                        print(f"✅ Successfully installed {package_name}")
                    else:
                        print(f"❌ Failed to install {package_name}")
            
            elif install_choice == "all_recommended":
                if not recommendations:
                    print("📭 No recommendations available")
                    return
                
                confirm = questionary.confirm(
                    f"Install all {len(recommendations)} recommended packages?"
                ).ask()
                
                if confirm:
                    print(f"🔄 Installing {len(recommendations)} packages...")
                    success_count = 0
                    
                    for rec in recommendations:
                        if rec.name not in installed_names:
                            print(f"Installing {rec.name}...")
                            if self.curator.install_package(rec.name):
                                success_count += 1
                                print(f"   ✅ {rec.name} installed")
                            else:
                                print(f"   ❌ {rec.name} failed")
                    
                    print(f"📦 Installation complete: {success_count}/{len(recommendations)} successful")
                
        except Exception as e:
            print(f"❌ Package installation error: {e}")
    
    # ============ ENHANCED HYPERVISOR COMMANDS ============
    
    def list_persistent_vms(self):
        """List all running persistent VMs with enhanced status including curator info"""
        print("\n" + "="*80)
        print("🖥️  Persistent Lua VM Status (with Package Information)")
        print("="*80)
        
        if not self.vm_status:
            print("📭 No persistent VMs running")
            return
        
        if RICH_AVAILABLE and self.console:
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("VM ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Profile", style="magenta")
            table.add_column("Packages", style="blue")
            table.add_column("Uptime", style="dim")
            table.add_column("Attached", style="red")
            
            for vm_id, status in self.vm_status.items():
                try:
                    # Check if VM is actually alive
                    sessions = self.vm_manager.session_manager.list_sessions()
                    vm_alive = vm_id in sessions
                    status_text = "🟢 Running" if vm_alive else "🔴 Dead"
                    
                    attached_text = "🔗 Yes" if status.attached else "➖ No"
                    
                    table.add_row(
                        vm_id,
                        status.name,
                        status_text,
                        status.profile,
                        str(status.packages_installed),
                        status.get_uptime(),
                        attached_text
                    )
                except Exception as e:
                    table.add_row(vm_id, status.name, f"🔴 Error: {e}", "N/A", "N/A", "N/A", "N/A")
            
            self.console.print(table)
        else:
            # Fallback text display
            for vm_id, status in self.vm_status.items():
                try:
                    sessions = self.vm_manager.session_manager.list_sessions()
                    vm_alive = vm_id in sessions
                    status_text = "Running" if vm_alive else "Dead"
                    
                    print(f"VM ID: {vm_id}")
                    print(f"  Name: {status.name}")
                    print(f"  Status: {status_text}")
                    print(f"  Profile: {status.profile}")
                    print(f"  Packages: {status.packages_installed}")
                    print(f"  Uptime: {status.get_uptime()}")
                    print(f"  Attached: {'Yes' if status.attached else 'No'}")
                    print()
                except Exception as e:
                    print(f"VM ID: {vm_id} - Error: {e}")
    
    def start_persistent_vm(self):
        """Start a new persistent Lua VM with curator-managed environment"""
        print("\n🚀 Start Persistent Lua VM (with Curator Integration)")
        
        vm_id = questionary.text(
            "Enter VM ID (unique identifier):", 
            validate=lambda x: x and x not in self.vm_status or "VM ID already exists or empty"
        ).ask()
        if not vm_id:
            return
        
        vm_name = questionary.text(
            f"Enter VM name (display name):", 
            default=f"BioXen-{vm_id}"
        ).ask()
        if not vm_name:
            vm_name = f"BioXen-{vm_id}"
        
        # Profile selection
        profile_choices = []
        for profile_name, profile_info in BIOXEN_PROFILES.items():
            package_count = len(profile_info["packages"])
            choice_text = f"{profile_name} ({package_count} packages)"
            profile_choices.append(Choice(choice_text, profile_name))
        
        # Add standard profiles too
        standard_profiles = ["minimal", "standard", "full"]
        for profile in standard_profiles:
            if profile in self.curator.manifest.get("profiles", {}):
                package_count = len(self.curator.manifest["profiles"][profile])
                profile_choices.append(Choice(f"{profile} ({package_count} packages)", profile))
        
        selected_profile = questionary.select(
            "Select environment profile:",
            choices=profile_choices
        ).ask()
        
        if not selected_profile:
            return
        
        networked = questionary.confirm("Enable networking capabilities?", default=False).ask()
        
        auto_setup = questionary.confirm(
            f"Automatically setup {selected_profile} environment?", 
            default=True
        ).ask()
        
        try:
            print(f"🔄 Creating persistent VM '{vm_id}' with {selected_profile} profile...")
            
            # Setup environment first if requested
            packages_installed = 0
            if auto_setup:
                print(f"📦 Setting up {selected_profile} environment...")
                success = self.curator.curate_environment(selected_profile)
                if success:
                    print("✅ Environment setup complete")
                    if selected_profile in BIOXEN_PROFILES:
                        packages_installed = len(BIOXEN_PROFILES[selected_profile]["packages"])
                    elif selected_profile in self.curator.manifest.get("profiles", {}):
                        packages_installed = len(self.curator.manifest["profiles"][selected_profile])
                else:
                    print("⚠️ Environment setup had issues, continuing with VM creation")
            
            # Create the VM
            if networked:
                # Create networked VM
                net_vm = NetworkedLuaVM(name=f"{vm_id}_net")
                session = self.vm_manager.create_interactive_vm(f"{vm_id}_interactive")
                actual_vm_id = f"{vm_id}_interactive"
            else:
                # Create interactive VM directly
                session = self.vm_manager.create_interactive_vm(vm_id)
                actual_vm_id = vm_id
            
            # Get curator health for VM status
            curator_health = self.curator.health_check()
            
            # Register VM status with curator information
            self.vm_status[actual_vm_id] = VMStatus(
                vm_id=actual_vm_id,
                name=vm_name,
                created_at=datetime.now(),
                profile=selected_profile,
                packages_installed=packages_installed,
                curator_health=curator_health
            )
            
            # Send initial setup commands
            welcome_msg = f"""
-- BioXen VM '{actual_vm_id}' started with {selected_profile} profile
-- {packages_installed} packages available
-- Type 'help()' for BioXen commands or regular Lua code
print('🌙 BioXen VM ready! Profile: {selected_profile}')
"""
            self.vm_manager.send_input(actual_vm_id, welcome_msg)
            time.sleep(0.2)
            
            print(f"✅ Persistent VM '{actual_vm_id}' started successfully!")
            print(f"📦 Profile: {selected_profile} ({packages_installed} packages)")
            print(f"🌐 Networking: {'Enabled' if networked else 'Disabled'}")
            print(f"💡 Use 'Attach to VM Terminal' to interact with it")
            
        except Exception as e:
            print(f"❌ Failed to start persistent VM: {e}")
            import traceback
            traceback.print_exc()
    
    def show_vm_detailed_status(self):
        """Show detailed status for a specific VM including curator information"""
        if not self.vm_status:
            print("📭 No persistent VMs available")
            return
        
        choices = [Choice(f"{vm_id} ({status.name})", vm_id) for vm_id, status in self.vm_status.items()]
        choices.append(Choice("← Back to Menu", "back"))
        
        vm_id = questionary.select("Select VM for detailed status:", choices=choices).ask()
        
        if not vm_id or vm_id == "back":
            return
        
        status = self.vm_status[vm_id]
        
        print("\n" + "="*80)
        print(f"📊 Detailed Status for VM '{vm_id}'")
        print("="*80)
        
        try:
            sessions = self.vm_manager.session_manager.list_sessions()
            vm_alive = vm_id in sessions
            
            # Basic VM info
            print(f"🆔 VM ID: {vm_id}")
            print(f"📛 Name: {status.name}")
            print(f"🟢 Status: {'Running' if vm_alive else '🔴 Dead'}")
            print(f"🎯 Profile: {status.profile}")
            print(f"⏰ Created: {status.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  Uptime: {status.get_uptime()}")
            print(f"🔗 Currently Attached: {'Yes' if status.attached else 'No'}")
            
            # Package information
            print(f"\n📦 Package Information:")
            print(f"   Packages in Profile: {status.packages_installed}")
            
            if status.profile in BIOXEN_PROFILES:
                profile_packages = BIOXEN_PROFILES[status.profile]["packages"]
                print(f"   Profile Packages: {', '.join(profile_packages[:5])}")
                if len(profile_packages) > 5:
                    print(f"   ... and {len(profile_packages) - 5} more")
            
            # Curator health at VM creation time
            if status.curator_health:
                print(f"\n🏥 Environment Health (at creation):")
                print(f"   Lua Version: {status.curator_health.get('lua_version', 'unknown')}")
                print(f"   LuaRocks: {'Available' if status.curator_health.get('luarocks_available') else 'Unavailable'}")
                print(f"   Total Packages: {status.curator_health.get('installed_packages', 0)}")
            
            # Current health check
            try:
                current_health = self.curator.health_check()
                print(f"\n🔍 Current System Health:")
                print(f"   Packages Now: {current_health.get('installed_packages', 0)}")
                print(f"   Critical Packages: {current_health.get('critical_packages_ratio', 'unknown')}")
            except Exception as e:
                print(f"   Health Check Error: {e}")
            
            if vm_alive:
                # Try to get some runtime info
                try:
                    self.vm_manager.send_input(vm_id, "print('Health check:', os.date(), 'Packages available')\n")
                    time.sleep(0.2)
                    output = self.vm_manager.read_output(vm_id)
                    if output:
                        print(f"🔊 Last Response: {output.strip()}")
                except:
                    print("🔊 Last Response: Unable to query")
            
        except Exception as e:
            print(f"❌ Error getting VM status: {e}")
    
    # ============ PRESERVED ORIGINAL FUNCTIONALITY ============
    
    def attach_to_vm_terminal(self):
        """Attach to a persistent VM's terminal (preserved original functionality)"""
        if not self.vm_status:
            print("📭 No persistent VMs available")
            return
        
        choices = [Choice(f"{vm_id} ({status.name}) - {status.profile}", vm_id) for vm_id, status in self.vm_status.items()]
        choices.append(Choice("← Back to Menu", "back"))
        
        vm_id = questionary.select("Select VM to attach to:", choices=choices).ask()
        
        if not vm_id or vm_id == "back":
            return
        
        try:
            print(f"\n🔗 Attaching to VM '{vm_id}' (Profile: {self.vm_status[vm_id].profile})")
            print("💡 Press Ctrl+D or type 'exit' to detach and return to menu")
            print("💡 The VM will continue running after detachment")
            print("💡 BioXen packages are available for use")
            print("-" * 70)
            
            # Mark as attached
            self.vm_status[vm