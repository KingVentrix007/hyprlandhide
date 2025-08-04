#!/usr/bin/env python3

import os
import json
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio


HIDE_DIR = os.path.expanduser("~/.local/share/hypr-hide")

import subprocess
import time

class HiddenWindowItem(Gtk.Box):
    def __init__(self, address, title, app_class, x, y, workspace):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.address = address
        self.x = x
        self.y = y
        self.workspace = workspace
        self.title = title

        label = Gtk.Label(label=f"{app_class}: {title}", xalign=0)
        self.append(label)

        btn = Gtk.Button(label="Restore")
        btn.connect("clicked", self.on_restore_clicked)
        self.append(btn)

    def run_cmd(self, cmd):
        """Run a shell command, return (stdout, stderr, returncode)"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    def get_focused_window(self):
        out, _, _ = self.run_cmd("hyprctl activewindow -j")
        try:
            import json
            j = json.loads(out)
            return j.get("address", "")
        except Exception:
            return ""

    def cycle_until_focused(self, target_addr, max_tries=10):
        tries = 0
        while tries < max_tries:
            focused = self.get_focused_window()
            if focused == target_addr:
                return True
            self.run_cmd("hyprctl dispatch cyclenext")
            time.sleep(0.2)
            tries += 1
        return False

    def on_restore_clicked(self, _btn):
        addr = self.address
        # Strip "0x" prefix if present
        if addr.startswith("0x"):
            addr = addr[2:]

        print(f"Restoring window {self.title} at {self.x},{self.y} on workspace {self.workspace}")

        # Step 1: switch workspace
        self.run_cmd(f"hyprctl dispatch workspace {self.workspace}")
        time.sleep(0.3)

        # Step 2: try direct focus
        self.run_cmd(f"hyprctl dispatch focuswindow address:0x{addr}")
        time.sleep(0.3)

        # Step 3: check focused window
        focused = self.get_focused_window()
        if focused != self.address:
            print("Direct focus failed, cycling to locate window...")
            success = self.cycle_until_focused(self.address)
            if not success:
                print("Failed to focus window after cycling")
                return

        # Step 4: toggle floating if needed (assume it's needed here)
        self.run_cmd("hyprctl dispatch togglefloating")
        time.sleep(0.3)

        # Step 5: move active window back on-screen
        self.run_cmd(f"hyprctl dispatch moveactive {self.x} {self.y}")

        # Step 6: remove json file to mark restored
        json_path = os.path.join(HIDE_DIR, f"{self.address}.json")
        try:
            os.remove(json_path)
        except Exception as e:
            print(f"Failed to remove {json_path}: {e}")

        print("Restore complete.")



class HyprHideApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="dev.kv.HyprHide",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = Adw.ApplicationWindow(application=self)
        win.set_title("Hidden Windows")
        win.set_default_size(400, 300)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)

        if not os.path.exists(HIDE_DIR):
            os.makedirs(HIDE_DIR)

        files = [f for f in os.listdir(HIDE_DIR) if f.endswith(".json")]

        if not files:
            content.append(Gtk.Label(label="No hidden windows", xalign=0))
        else:
            for file in files:
                with open(os.path.join(HIDE_DIR, file)) as f:
                    data = json.load(f)
                    item = HiddenWindowItem(
                        address=data['address'],
                        title=data['title'],
                        app_class=data['class'],
                        x=data['at'][0],
                        y=data['at'][1],
                        workspace = data['workspace']['id']
                    )
                    content.append(item)

        scroller = Gtk.ScrolledWindow()
        scroller.set_child(content)

        win.set_content(scroller)
        win.present()


if __name__ == "__main__":
    app = HyprHideApp()
    app.run()
