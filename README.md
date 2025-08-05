
## 🚀 Welcome to **HyprHide**

**HyprHide** is a Python-based plugin for [Hyprland](https://github.com/hyprwm/Hyprland) that brings *true window minimization* — fully functional in both **floating** and **tiling** modes.

---

### 🔧 How It Works

* [`min.sh`](min.sh) — A Bash script that:

  * Hides the currently focused window
  * Captures a screenshot of it
  * Saves all data to `~/.local/share/hypr-hide/`

* [`HyprHideGui.py`](HyprHideGui.py) — A minimalist Python GUI that:

  * Displays previews of hidden windows
  * Lets you click to instantly restore them

---

### ⚙️ Setup

#### 🖱️ Keybind Mode

1. Make sure `min.sh` is executable:

   ```bash
   chmod +x min.sh
   ```
2. Create a keybind in your Hyprland config to run `min.sh`
3. Add another keybind to launch `HyprHideGui.py`

#### 🧩 Hyprbars (Optional)

1. Install the [Hyprbars](https://github.com/hyprwm/hyprbars) plugin
2. Create a new button in your Hyprbars config
3. Bind the button to execute `min.sh`

#### 🖥️ Waybar Integration (Optional)

1. Open your Waybar config:

   ```bash
   nano ~/.config/waybar/config
   ```
2. Add `"custom/hyprhide"` to your desired module section, such as `modules-left`, `modules-center`, or `modules-right`. For example:

   ```json
   "modules-right": ["custom/hyprhide", ...]
   ```
3. Open your custom module definitions:

   ```bash
   nano ~/.config/waybar/modules/modules-custom.jsonc
   ```
4. Add the following snippet (replace the path on-click as needed):

   ```json
   "custom/hyprhide": {
       "exec": "echo '🗔'", 
       "interval": 0,
       "on-click": "python3 /mnt/MyCodeProjects/hyprlandhide/HyprHideGui.py",
       "tooltip-format": "Press to see all hidden windows"
   }
   ```

---

### ⚠️ Known Issues

#### 🪟 Floating vs. Tiling Conflicts

* Hyprland may ignore per-window geometry and instead follow workspace defaults:

  * Floating windows may restore as **tiled** if the workspace is in tiling mode
  * Restored windows may be auto-resized or moved

#### ↩️ Inconsistent Restore Behavior

* Windows don’t always return to their exact previous location:

  * They restore to the correct **monitor/workspace**
  * But may appear in the **wrong spot** or **wrong mode** (e.g., tiled instead of floating)

---

### 🌱 Future Improvements

* Better tracking of window state (floating/tiling)
* More accurate positioning on restore
* Persistent metadata storage for full layout memory

