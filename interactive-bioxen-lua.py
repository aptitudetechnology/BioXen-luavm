#!/usr/bin/env python3
"""
Interactive BioXen CLI using questionary for user-friendly VM management.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    sys.exit(1)

try:
    from pylua_vm import VMManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the BioXen root directory")
    sys.exit(1)

class InteractiveBioXen:
    def create_lua_vm(self):
        """
        High-level Lua VM orchestration using VMManager from vm_manager.py.
        """
        from vm_manager import VMManager
        print("\n🌙 Create Lua VM (VMManager)")
        print("💡 This option uses the VMManager library for robust Lua VM orchestration.")
        print("    Make sure 'lua' and 'luasocket' are installed for networking features.")

        vm_manager = VMManager()

        while True:
            lua_action = questionary.select(
                "How would you like to interact with the Lua VM?",
                choices=[
                    Choice("Start Lua Server VM (Socket)", "server_socket"),
                    Choice("Start Lua Client VM (Socket)", "client_socket"),
                    Choice("Start Lua P2P VM (Socket)", "p2p_socket"),
                    Choice("Execute Lua code string", "string"),
                    Choice("Execute Lua script file", "file"),
                    Choice("Back to Main Menu", "back")
                ]
            ).ask()

            if lua_action is None or lua_action == "back":
                print("↩️ Returning to main menu.")
                break

            try:
                if lua_action == "server_socket":
                    port = questionary.text("Enter port for Lua Server (e.g., 8080):", default="8080", validate=lambda x: x.isdigit() and 1024 <= int(x) <= 65535 or "Port must be between 1024 and 65535").ask()
                    if not port:
                        continue
                    process_name = f"Lua Server on Port {port}"
                    print(f"\n--- Starting {process_name} ---")
                    print("💡 This process will block until a client connects and sends a message.")
                    output, error = vm_manager.run_server(port=int(port))
                    if output:
                        print(f"--- {process_name} STDOUT ---\n{output.strip()}")
                    if error:
                        print(f"--- {process_name} STDERR ---\n{error.strip()}", file=sys.stderr)

                elif lua_action == "client_socket":
                    ip = questionary.text("Enter Server IP (default: localhost):", default="localhost").ask()
                    if not ip:
                        continue
                    port = questionary.text("Enter Server Port (e.g., 8080):", default="8080", validate=lambda x: x.isdigit() and 1024 <= int(x) <= 65535 or "Port must be between 1024 and 65535").ask()
                    if not port:
                        continue
                    message = questionary.text("Enter message to send to server:", default="Greetings, Lua Server!").ask()
                    if not message:
                        continue
                    process_name = f"Lua Client to {ip}:{port}"
                    print(f"\n--- Starting {process_name} ---")
                    output, error = vm_manager.run_client(ip=ip, port=int(port), message=message)
                    if output:
                        print(f"--- {process_name} STDOUT ---\n{output.strip()}")
                    if error:
                        print(f"--- {process_name} STDERR ---\n{error.strip()}", file=sys.stderr)

                elif lua_action == "p2p_socket":
                    local_port = questionary.text("Enter local port for P2P VM to listen on (e.g., 8081):", default="8081", validate=lambda x: x.isdigit() and 1024 <= int(x) <= 65535 or "Port must be between 1024 and 65535").ask()
                    if not local_port:
                        continue
                    peer_ip_port_str = questionary.text("Enter peer IP:Port to connect to (e.g., localhost:8080, leave blank for no outgoing connection):").ask()
                    peer_ip, peer_port = None, None
                    if peer_ip_port_str:
                        try:
                            peer_ip, peer_port = peer_ip_port_str.split(":")
                            peer_port = int(peer_port)
                        except ValueError:
                            print("❌ Invalid peer IP:Port format. Use IP:Port (e.g., localhost:8080).")
                            continue
                    process_name = f"Lua P2P VM (Listen:{local_port}"
                    if peer_ip_port_str:
                        process_name += f", Connect:{peer_ip_port_str})"
                    else:
                        process_name += ")"
                    print(f"\n--- Starting {process_name} ---")
                    print(f"💡 This P2P VM will run for 30 seconds, attempting to listen on port {local_port}")
                    if peer_ip_port_str:
                        print(f"    and connect to peer {peer_ip_port_str}.")
                    output, error = vm_manager.run_p2p(local_port=int(local_port), peer_ip=peer_ip, peer_port=peer_port, run_duration=30)
                    if output:
                        print(f"--- {process_name} STDOUT ---\n{output.strip()}")
                    if error:
                        print(f"--- {process_name} STDERR ---\n{error.strip()}", file=sys.stderr)

                elif lua_action == "string":
                    lua_code = questionary.text("Enter Lua code to execute (e.g., print('Hello')):").ask()
                    if not lua_code:
                        print("⚠️ No Lua code entered. Returning to Lua VM menu.")
                        continue
                    process_name = "Lua Code String"
                    output, error = vm_manager.run_code(lua_code)
                    print(f"--- {process_name} STDOUT ---\n{output.strip() if output else ''}")
                    if error:
                        print(f"--- {process_name} STDERR ---\n{error.strip()}", file=sys.stderr)

                elif lua_action == "file":
                    file_path_str = questionary.text("Enter path to Lua script file (e.g., my_script.lua):").ask()
                    if not file_path_str:
                        print("⚠️ No file path entered. Returning to Lua VM menu.")
                        continue
                    lua_file_path = Path(file_path_str)
                    if not lua_file_path.is_file():
                        print(f"❌ Error: File not found at '{lua_file_path}'.")
                        continue
                    process_name = f"Lua Script File: {lua_file_path.name}"
                    output, error = vm_manager.run_script(str(lua_file_path))
                    print(f"--- {process_name} STDOUT ---\n{output.strip() if output else ''}")
                    if error:
                        print(f"--- {process_name} STDERR ---\n{error.strip()}", file=sys.stderr)

            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}", file=sys.stderr)
            questionary.press_any_key_to_continue().ask()

    def main_menu(self):
        """Display and handle the main menu."""
        while True:
            print("\n" + "="*60)
            print("🌙 Lua VM Manager - Interactive Interface")
            print("="*60)
            
            choices = [
                Choice("🌙 Create Lua VM", "create_lua_vm"),
                Choice("❌ Exit", "exit"),
            ]
            
            action = questionary.select(
                "What would you like to do?",
                choices=choices,
                use_shortcuts=True
            ).ask()
            
            if action is None or action == "exit":
                print("👋 Goodbye!")
                break
            
            try:
                if action == "create_lua_vm":
                    self.create_lua_vm()
            except KeyboardInterrupt:
                print("\n\n⚠️ Operation cancelled by user")
                continue
            except Exception as e:
                print(f"\n❌ Error: {e}")
                questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    cli = InteractiveBioXen()
    cli.main_menu()