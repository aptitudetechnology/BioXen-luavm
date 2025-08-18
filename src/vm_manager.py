
"""
High-level VM manager for orchestrating multiple Lua VMs.

This module provides the main interface for creating, managing, and coordinating
multiple networked Lua VMs.
"""

import subprocess
import sys
from pathlib import Path

class VMManager:
    def __init__(self):
        self.vms = []  # Track running VMs if needed

    def run_server(self, port=8080):
        """Start a Lua server VM on the given port."""
        lua_code = f'''
local socket = require("socket")
local server = socket.bind("*", {port})
if not server then
    io.stderr:write("Lua Server: Failed to bind to port {port}\\n")
    os.exit(1)
end
print("Lua Server: Listening on port {port}...")
local client = server:accept()
print("Lua Server: Client connected from " .. client:getpeername())
client:send("Hello from Lua Server! What\\'s your message?\\n")
local data, err = client:receive()
if data then
    print("Lua Server: Received from client: " .. data)
else
    io.stderr:write("Lua Server: Error receiving data or client disconnected: " .. tostring(err) .. "\\n")
end
client:close()
server:close()
print("Lua Server: Connection closed.")
'''
        return self._run_lua_code(lua_code)

    def run_client(self, ip="localhost", port=8080, message="Greetings, Lua Server!"):
        """Start a Lua client VM to connect to a server."""
        # Escape any quotes in the message
        escaped_message = message.replace('"', '\\"').replace("'", "\\'")
        
        lua_code = f'''
local socket = require("socket")
local client, err = socket.connect("{ip}", {port})
if not client then
    io.stderr:write("Lua Client: Failed to connect to {ip}:{port}: " .. tostring(err) .. "\\n")
    os.exit(1)
end
print("Lua Client: Connected to server at {ip}:{port}")
local response, err_recv = client:receive()
if response then
    print("Lua Client: Received from server: " .. response)
else
    io.stderr:write("Lua Client: Error receiving initial message from server: " .. tostring(err_recv) .. "\\n")
end
client:send("{escaped_message}\\n")
print("Lua Client: Sent message: \\"{escaped_message}\\"")
client:close()
print("Lua Client: Connection closed.")
'''
        return self._run_lua_code(lua_code)

    def run_p2p(self, local_port=8081, peer_ip=None, peer_port=None, run_duration=30):
        """Start a Lua P2P VM that can listen and optionally connect to a peer."""
        peer_connect_code = ""
        if peer_ip and peer_port:
            peer_connect_code = f'''
local peer_client, peer_err = socket.connect("{peer_ip}", {peer_port})
if peer_client then
    peer_client:settimeout(0.1)
    print("P2P VM: Connected to peer at {peer_ip}:{peer_port}")
    table.insert(sockets_to_monitor, peer_client)
    peer_client:send("Hello from P2P VM on port {local_port}!\\n")
else
    io.stderr:write("P2P VM: Failed to connect to peer {peer_ip}:{peer_port}: " .. tostring(peer_err) .. "\\n")
end
'''
        lua_code = f'''
local socket = require("socket")
local local_port = {local_port}
local server_socket = socket.bind("*", local_port)
if not server_socket then
    io.stderr:write("P2P VM: Failed to bind to local port " .. local_port .. "\\n")
    os.exit(1)
end
server_socket:settimeout(0.1)
print("P2P VM: Listening on local port " .. local_port .. "...")
local sockets_to_monitor = {{server_socket}}
local connected_peers = {{}}
{peer_connect_code}
local last_send_time = os.clock()
local send_interval = 5
local run_duration = {run_duration}
local start_time = os.clock()
while os.clock() - start_time < run_duration do
    local readable_sockets, _, err = socket.select(sockets_to_monitor, nil, 0.1)
    if err then
        io.stderr:write("P2P VM: socket.select error: " .. tostring(err) .. "\\n")
        break
    end
    for i, sock in ipairs(readable_sockets) do
        if sock == server_socket then
            local new_client = server_socket:accept()
            if new_client then
                new_client:settimeout(0.1)
                local peer_ip, peer_port = new_client:getpeername()
                print("P2P VM: Accepted connection from " .. peer_ip .. ":" .. peer_port)
                table.insert(sockets_to_monitor, new_client)
                connected_peers[new_client] = true
                new_client:send("Welcome to P2P VM on port " .. local_port .. "!\\n")
            else
                io.stderr:write("P2P VM: Error accepting new client: " .. tostring(new_client) .. "\\n")
            end
        else
            local data, recv_err, partial = sock:receive()
            if data then
                print("P2P VM: Received from " .. sock:getpeername() .. ": " .. data)
            elseif recv_err == "timeout" then
            else
                print("P2P VM: Connection from " .. sock:getpeername() .. " closed or error: " .. tostring(recv_err))
                sock:close()
                for k, v in ipairs(sockets_to_monitor) do
                    if v == sock then
                        table.remove(sockets_to_monitor, k)
                        break
                    end
                end
                connected_peers[sock] = nil
            end
        end
    end
    if os.clock() - last_send_time > send_interval then
        for sock in pairs(connected_peers) do
            local success, send_err = sock:send("P2P VM " .. local_port .. ": Heartbeat at " .. os.clock() .. "\\n")
            if not success then
                io.stderr:write("P2P VM: Error sending to " .. sock:getpeername() .. ": " .. tostring(send_err) .. "\\n")
            end
        end
        last_send_time = os.clock()
    end
end
print("P2P VM: Shutting down after " .. run_duration .. " seconds.")
for sock in pairs(connected_peers) do
    sock:close()
end
server_socket:close()
'''
        return self._run_lua_code(lua_code)

    def run_code(self, lua_code):
        """Execute a Lua code string."""
        return self._run_lua_code(lua_code)

    def run_script(self, script_path):
        """Execute a Lua script file."""
        command = ["lua", script_path]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            return result.stdout, result.stderr
        except Exception as e:
            return "", str(e)

    def _run_lua_code(self, lua_code):
        command = ["lua", "-e", lua_code]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            return result.stdout, result.stderr
        except Exception as e:
            return "", str(e)