# main.py

import sys
from PySide6.QtWidgets import QApplication
from .pre_processor_window import MainWindow
from multiprocessing import freeze_support

if __name__ == '__main__':
    # --- 决定性修复: 添加 freeze_support() 以支持打包 ---
    freeze_support()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
