# -*- coding: utf-8 -*-
"""
调试3D视图显示问题
"""
import sys
import os

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import QTimer

import numpy as np

# 创建应用
app = QApplication(sys.argv)

# 创建窗口
window = QWidget()
window.setWindowTitle("3D视图调试")
window.resize(800, 600)

layout = QVBoxLayout(window)

# 添加标签
label = QLabel("3D视图调试窗口 - 应该显示彩色的3D表面图")
label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
layout.addWidget(label)

# 导入3D视图
from 风场设置.main_control.function_3d_view import Function3DView
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

# 创建3D视图
view_3d = Function3DView()
layout.addWidget(view_3d)

# 添加按钮用于测试
btn_update = QPushButton("更新3D视图")
def update_view():
    params = FunctionParams()
    params.center = (20.0, 20.0)
    func = WindFieldFunctionFactory.create('gaussian', params)
    result_grid = func.apply(np.zeros((40, 40)), time=0.0)
    view_3d.set_grid_data(result_grid)
    print("3D视图已更新")

btn_update.clicked.connect(update_view)
layout.addWidget(btn_update)

# 添加说明
info = QLabel("说明：\n1. 上方应该看到彩色的3D表面图\n2. 如果看不到，说明matplotlib有问题\n3. 点击'更新3D视图'可以重新绘制")
info.setStyleSheet("color: #666; padding: 10px;")
layout.addWidget(info)

# 显示窗口
window.show()

# 自动更新一次
QTimer.singleShot(1000, update_view)

print("3D调试窗口已启动")
print("如果看到窗口但没有3D图形，请检查matplotlib安装")

sys.exit(app.exec())
