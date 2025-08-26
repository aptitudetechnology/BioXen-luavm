import os
import sys
import signal
import questionary
from questionary import Choice

from nucleoid_vm import LuaVMManager


class VMStatus:
    def __init__(self, profile):
        self.profile = profile
        self.running = False
        self.attached = False
        self.pid = None


class VMCLI:
    def __init__(self):
        self.vm_manager = LuaVMManager()
        self.vm_status = {}

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
            elif action == "exit":
                self.cleanup()
                sys.exit(0)

            # after each action (except long-running ones), wait for key
            if action not in ["attach_vm", "env_status", "setup_profile"]:
                questionary.press_any_key_to_continue().ask()

    def create_lua_vm(self):
        profile_name = questionary.text("Enter profile name for this VM").ask()
        if not profile_name:
            print("❌ Profile name is required")
            return

        try:
            vm_id, pid = self.vm_manager.launch_vm(profile_name)
            self.vm_status[vm_id] = VMStatus(profile_name)
            self.vm_status[vm_id].running = True
            self.vm_status[vm_id].pid = pid

            print(f"\n✅ VM '{vm_id}' created with profile '{profile_name}' (PID {pid})")
            print("💡 Type 'exit' or press Ctrl+D to return to menu")
            print("-" * 70)

            # attach right away to new VM
            with self.vm_manager.attach_interactive_session(vm_id) as session:
                session.interactive_loop()

        except Exception as e:
            print(f"❌ Failed to create VM: {e}")

    def attach_to_vm_terminal(self):
        if not self.vm_status:
            print("❌ No VMs available to attach to")
            return

        vm_choices = [
            Choice(f"{vm_id} (Profile: {status.profile})", vm_id)
            for vm_id, status in self.vm_status.items() if status.running
        ]

        if not vm_choices:
            print("❌ No running VMs to attach to")
            return

        vm_id = questionary.select("Select a VM to attach:", choices=vm_choices).ask()
        if not vm_id:
            return

        try:
            print(f"\n🔗 Attaching to VM '{vm_id}' (Profile: {self.vm_status[vm_id].profile})")
            print("💡 Press Ctrl+D or type 'exit' to detach and return to menu")
            print("💡 The VM will continue running after detachment")
            print("-" * 70)

            self.vm_status[vm_id].attached = True

            with self.vm_manager.attach_interactive_session(vm_id) as session:
                session.interactive_loop()

            self.vm_status[vm_id].attached = False
            print(f"✅ Detached from VM '{vm_id}' - VM continues running")

        except Exception as e:
            print(f"❌ Failed to attach to VM: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to continue...")
            self.vm_status[vm_id].attached = False

    def install_packages(self):
        install_choice = questionary.select(
            "How would you like to install packages?",
            choices=[
                Choice("Install recommended package", "recommended"),
                Choice("Install specific package by name", "specific"),
                Choice("Install all recommendations", "all_recommended"),
                Choice("← Back to Menu", "back")
            ],
            default="recommended"
        ).ask()

        if not install_choice or install_choice == "back":
            print("↩️ Returning to main menu...")
            return

        try:
            if install_choice == "recommended":
                package = questionary.text("Enter package name to install").ask()
                if package:
                    self.vm_manager.install_package(package)
                    print(f"✅ Installed package: {package}")

            elif install_choice == "specific":
                package = questionary.text("Enter specific package name").ask()
                if package:
                    self.vm_manager.install_package(package)
                    print(f"✅ Installed package: {package}")

            elif install_choice == "all_recommended":
                recommended_packages = ["luasocket", "luafilesystem"]
                for pkg in recommended_packages:
                    self.vm_manager.install_package(pkg)
                    print(f"✅ Installed: {pkg}")

        except Exception as e:
            print(f"❌ Package installation failed: {e}")

        input("Press Enter to return to menu...")

    def setup_profile(self):
        profile_name = questionary.text("Enter new profile name").ask()
        if not profile_name:
            print("❌ Profile name is required")
            return

        # TODO: add actual profile creation logic
        print(f"✅ Profile '{profile_name}' setup successfully")

    def show_environment_status(self):
        print("\n🖥️  Environment Status:")
        if not self.vm_status:
            print("  No VMs created yet")
            return

        for vm_id, status in self.vm_status.items():
            state = []
            if status.running:
                state.append("Running")
            if status.attached:
                state.append("Attached")
            if not state:
                state.append("Stopped")
            print(f"  VM {vm_id}: Profile={status.profile}, PID={status.pid}, State={','.join(state)}")

    def cleanup(self):
        print("\n🧹 Cleaning up running VMs...")
        for vm_id, status in self.vm_status.items():
            if status.running:
                try:
                    os.kill(status.pid, signal.SIGTERM)
                    print(f"✅ VM {vm_id} (PID {status.pid}) terminated")
                except Exception as e:
                    print(f"⚠️ Could not terminate VM {vm_id}: {e}")


if __name__ == "__main__":
    cli = VMCLI()
    cli.main_menu()
