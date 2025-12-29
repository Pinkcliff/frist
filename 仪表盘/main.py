# main.py
import sys
import os
from PySide6.QtWidgets import QApplication

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ui_main_window import GlobalDashboardWindow

def main():
    app = QApplication(sys.argv)
    window = GlobalDashboardWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
