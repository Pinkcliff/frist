# -*- coding: utf-8 -*-
"""
前处理应用入口文件
用于正确启动 CFD_module 中的 MainWindow (CFD前处理器)
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置 Qt 插件路径（修复 Qt 平台插件加载问题）
import PySide6
qt_plugins_path = os.path.join(os.path.dirname(PySide6.__file__), 'plugins')
os.environ['QT_PLUGIN_PATH'] = qt_plugins_path

from PySide6.QtWidgets import QApplication
from CFD_module.pre_processor_window import MainWindow
from multiprocessing import freeze_support

def main():
    """主函数"""
    # 支持打包为可执行文件
    freeze_support()

    app = QApplication(sys.argv)
    app.setApplicationName("CFD前处理器")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
