#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic PyQt5 GUI")
        self.setGeometry(100, 100, 300, 100)

        self.button = QPushButton("Click me")
        self.button.clicked.connect(self.on_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_button_clicked(self):
        print("Hello from PyQt!")

def main():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
