import os
import subprocess
import json
import time

def _run_command(command):
    print(f"Running command: {command}")
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return ""

def get_clients():
    try:
        result = _run_command('hyprctl clients -j')
        return json.loads(result)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

def get_client_info(address: str):
    clients = get_clients()
    for client in clients:
        if client.get("address") == address:
            return client
    print(f"No client found with address: {address}")
    return None

def get_active_window():
    out = _run_command("hyprctl activewindow -j")
    try:
        j = json.loads(out)
        return j.get("address", "")
    except Exception as e:
        print(f"Error getting active window: {e}")
        return ""

def set_active_client(address, max_count=10):
    count = 0
    while get_active_window() != address and count < max_count:
        _run_command(f"hyprctl dispatch focuswindow address:{address}")
        time.sleep(0.05)  # tiny wait
        count += 1
    return count < max_count

def move_window_local(address, target_x, target_y):
    info = get_client_info(address)
    if not info:
        print("Could not get window info.")
        return

    current_pos = info.get("at", [0, 0])
    dx = target_x - current_pos[0]
    dy = target_y - current_pos[1]

    print(f"Moving window by offset dx={dx}, dy={dy}")
    _run_command(f"hyprctl dispatch movewindowpixel {dx} {dy} address:{address}")
    new_info =  get_client_info(address)
    pos = info.get("at", [0, 0])
    print(f"Window position: {pos[0]}:{pos[1]}")

def toggle_floating(address):
    _run_command(f"hyprctl dispatch togglefloating address:{address}")

def set_floating(address):
    window_data = get_client_info(address=address)
    is_floating = window_data['floating']
    if(is_floating == False):
        toggle_floating(address=address)
        window_data = get_client_info(address=address)
        return window_data['floating'] == True
    else:
        return True
def set_tiling(address):
    window_data = get_client_info(address=address)
    is_floating = window_data['floating']
    if(is_floating == True):
        toggle_floating(address=address)
        window_data = get_client_info(address=address)
        return window_data['floating'] == False
    else:
        return True

def set_current_workspace(workspace:int):
    _run_command(f"hyprctl dispatch workspace {workspace}")

def focus_window(address):
    _run_command(f"hyprctl dispatch focuswindow address:{address}")

def move_win_to_workspace(address,workspace):
    _run_command(f"hyprctl dispatch movetoworkspacesilent {workspace}, address:{address}")