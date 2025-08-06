import os
import subprocess
import json
def get_clients():
    try:
        # Run hyprctl clients -j and capture output
        result = subprocess.run(['hyprctl', 'clients', '-j'], capture_output=True, text=True, check=True)
        
        # Parse the output as JSON
        clients = json.loads(result.stdout)
        
        return clients
    except subprocess.CalledProcessError as e:
        print(f"Error running hyprctl: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    
    return []
def get_client_info(address:str):
    try:
        # Run hyprctl clients -j
        result = subprocess.run(['hyprctl', 'clients', '-j'], capture_output=True, text=True, check=True)
        clients = json.loads(result.stdout)

        # Search for the client with the given address
        for client in clients:
            if client.get("address") == address:
                return client

        print(f"No client found with address: {address}")
    except subprocess.CalledProcessError as e:
        print(f"Error running hyprctl: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

def get_active_window():
        out, _, _ = os.system("hyprctl activewindow -j")
        try:
            j = json.loads(out)
            return j.get("address", "")
        except Exception:
            return ""

def set_active_client(address,max_count = 10):
    count = 0
    while(get_active_window() != address and count < max_count):
        os.system(f"hyprctl dispatch focuswindow address:{address}")
        count+=1
    if(count >= max_count):
        return False
    return True
