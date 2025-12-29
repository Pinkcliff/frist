# -*- coding: utf-8 -*-
"""
上位机主程序入口 - 仪表盘程序
"""
import sys
import os

# 设置 Qt 插件路径（修复 Qt 平台插件加载问题）
import PySide6
qt_plugins_path = os.path.join(os.path.dirname(PySide6.__file__), 'plugins')
os.environ['QT_PLUGIN_PATH'] = qt_plugins_path

# 添加当前目录和仪表盘目录到路径
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

dashboard_dir = os.path.join(ROOT_DIR, '仪表盘')
if dashboard_dir not in sys.path:
    sys.path.insert(0, dashboard_dir)

from PySide6.QtWidgets import QApplication
from 仪表盘.ui_main_window import GlobalDashboardWindow

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("无人机仪表盘")

    window = GlobalDashboardWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
