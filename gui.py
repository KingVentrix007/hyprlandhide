#!/usr/bin/env python3

import os
import json
import subprocess
import time
import sys
import signal

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QScrollArea, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QCursor


HIDE_DIR = os.path.expanduser("~/.local/share/hypr-hide")


class HiddenWindowItem(QWidget):
    def __init__(self, address, title, app_class, x, y, workspace):
        super().__init__()
        self.address = address
        self.x = x
        self.y = y
        self.workspace = workspace
        self.title = title

        layout = QHBoxLayout()
        layout.setSpacing(10)

        label = QLabel(f"{app_class}: {title}")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label)

        btn = QPushButton("Restore")
        btn.clicked.connect(self.on_restore_clicked)
        layout.addWidget(btn)

        self.setLayout(layout)

    def run_cmd(self, cmd):
        """Run a shell command, return (stdout, stderr, returncode)"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    def get_focused_window(self):
        out, _, _ = self.run_cmd("hyprctl activewindow -j")
        try:
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

    def on_restore_clicked(self):
        addr = self.address
        if addr.startswith("0x"):
            addr = addr[2:]

        print(f"Restoring window {self.title} at {self.x},{self.y} on workspace {self.workspace}")

        self.run_cmd(f"hyprctl dispatch workspace {self.workspace}")
        time.sleep(0.3)

        self.run_cmd(f"hyprctl dispatch focuswindow address:0x{addr}")
        time.sleep(0.3)

        focused = self.get_focused_window()
        if focused != self.address:
            print("Direct focus failed, cycling to locate window...")
            success = self.cycle_until_focused(self.address)
            if not success:
                print("Failed to focus window after cycling")
                return

        self.run_cmd("hyprctl dispatch togglefloating")
        # time.sleep(0.3)

        self.run_cmd(f"hyprctl dispatch moveactive {self.x} {self.y}")

        json_path = os.path.join(HIDE_DIR, f"{self.address}.json")
        try:
            os.remove(json_path)
        except Exception as e:
            print(f"Failed to remove {json_path}: {e}")
        self.run_cmd("hyprctl dispatch togglefloating")

        print("Restore complete.")


class HyprHideApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hidden Windows")
        self.setFixedSize(400, 300)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.Tool)  # Small popup style window, no taskbar entry

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_widget.setLayout(self.content_layout)

        self.scroll_area.setWidget(self.content_widget)

        self.load_hidden_windows()

        # Position window near mouse pointer on show
        QTimer.singleShot(10, self.position_near_mouse)


    def load_hidden_windows(self):
        if not os.path.exists(HIDE_DIR):
            os.makedirs(HIDE_DIR)

        files = [f for f in os.listdir(HIDE_DIR) if f.endswith(".json")]

        if not files:
            label = QLabel("No hidden windows")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.content_layout.addWidget(label)
        else:
            for file in files:
                try:
                    with open(os.path.join(HIDE_DIR, file)) as f:
                        data = json.load(f)
                        item = HiddenWindowItem(
                            address=data['address'],
                            title=data['title'],
                            app_class=data['class'],
                            x=data['at'][0],
                            y=data['at'][1],
                            workspace=data['workspace']['id']
                        )
                        self.content_layout.addWidget(item)
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    def closeEvent(self, event):
        QApplication.quit()

    def position_near_mouse(self):
        if not self.isVisible():
            QTimer.singleShot(10, self.position_near_mouse)
            return

        pos = QCursor.pos()
        screen = QApplication.primaryScreen().availableGeometry()
        win_width = self.frameGeometry().width()
        win_height = self.frameGeometry().height()

        x = min(pos.x(), screen.width() - win_width)
        y = min(pos.y() + 20, screen.height() - win_height)

        self.move(x, y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Add this line
    window = HyprHideApp()
    window.show()
    sys.exit(app.exec())