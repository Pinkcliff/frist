# -*- coding: utf-8 -*-
"""
3D视图和动画功能完整测试

验证所有功能是否正常工作
"""
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox
from PySide6.QtCore import Qt, QTimer
import numpy as np

print("=" * 70)
print("3D视图和动画功能完整测试")
print("=" * 70)

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# 导入模块
from 风场设置.main_control.function_3d_view import Function3DView
from 风场设置.main_control.timeline_widget import TimelineWidget
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

# 创建窗口
window = QWidget()
window.setWindowTitle("3D视图和动画功能测试")
window.resize(1000, 700)

layout = QVBoxLayout(window)

# 创建3D视图和时间轴
view_3d = Function3DView()
timeline = TimelineWidget()

# 添加到布局
view_3d_group = QGroupBox("3D函数视图（应该看到彩色的3D表面图）")
view_3d_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #4CAF50; }")
view_3d_layout = QVBoxLayout()
view_3d_layout.addWidget(view_3d)
view_3d_group.setLayout(view_3d_layout)

timeline_group = QGroupBox("时间轴（拖动滑块或点击播放）")
timeline_group.setStyleSheet("QGroupBox { font-weight: bold; }")
timeline_layout = QVBoxLayout()
timeline_layout.addWidget(timeline)
timeline_group.setLayout(timeline_layout)

layout.addWidget(view_3d_group, 3)
layout.addWidget(timeline_group, 1)

# 创建控制按钮
button_layout = QHBoxLayout()
btn_gaussian = QPushButton("高斯函数")
btn_wave = QPushButton("波函数")
btn_spiral = QPushButton("螺旋函数")
btn_play = QPushButton("播放动画")

button_layout.addWidget(btn_gaussian)
button_layout.addWidget(btn_wave)
button_layout.addWidget(btn_spiral)
button_layout.addWidget(btn_play)

layout.addLayout(button_layout)

# 状态标签
status_label = QLabel("准备就绪 - 点击上方按钮测试不同函数")
status_label.setStyleSheet("padding: 10px; background: #e3f2fd; border-radius: 5px;")
layout.addWidget(status_label)

# 当前函数
current_function = None
current_params = FunctionParams()
current_params.center = (20.0, 20.0)
current_params.amplitude = 100.0

def show_message(msg):
    status_label.setText(msg)
    print(f"[INFO] {msg}")

def apply_gaussian():
    global current_function
    current_function = 'gaussian'
    func = WindFieldFunctionFactory.create(current_function, current_params)
    result_grid = func.apply(np.zeros((40, 40)), time=0.0)
    view_3d.set_grid_data(result_grid)
    view_3d.current_function = 'gaussian'
    view_3d.current_time = 0.0
    show_message("✅ 高斯函数已应用 - 应该看到中心对称的彩色山峰")

def apply_wave():
    global current_function
    current_function = 'simple_wave'
    func = WindFieldFunctionFactory.create(current_function, current_params)
    result_grid = func.apply(np.zeros((40, 40)), time=0.0)
    view_3d.set_grid_data(result_grid)
    view_3d.current_function = 'simple_wave'
    view_3d.current_time = 0.0
    show_message("✅ 波函数已应用 - 应该看到波浪状的表面")

def apply_spiral():
    global current_function
    current_function = 'spiral_wave'
    func = WindFieldFunctionFactory.create(current_function, current_params)
    result_grid = func.apply(np.zeros((40, 40)), time=0.0)
    view_3d.set_grid_data(result_grid)
    view_3d.current_function = 'spiral_wave'
    view_3d.current_time = 0.0
    show_message("✅ 螺旋函数已应用 - 应该看到螺旋图案")

def play_animation():
    if current_function is None:
        show_message("⚠️ 请先选择一个函数")
        return

    show_message(f"▶️ 播放 {current_function} 动画...")

    # 模拟动画
    def update_frame():
        for t in np.linspace(0, 10, 21):
            func = WindFieldFunctionFactory.create(current_function, current_params)
            result_grid = func.apply(np.zeros((40, 40)), time=t)
            view_3d.set_grid_data(result_grid)
            view_3d.current_time = t
            timeline.set_current_time(t)
            QApplication.processEvents()

    QTimer.singleShot(100, update_frame)

# 连接信号
btn_gaussian.clicked.connect(apply_gaussian)
btn_wave.clicked.connect(apply_wave)
btn_spiral.clicked.connect(apply_spiral)
btn_play.clicked.connect(play_animation)

# 连接时间轴信号
def on_time_changed(t):
    if current_function:
        func = WindFieldFunctionFactory.create(current_function, current_params)
        result_grid = func.apply(np.zeros((40, 40)), time=t)
        view_3d.set_grid_data(result_grid)
        view_3d.current_time = t
        show_message(f"时间: {t:.1f}s - {current_function}")

timeline.time_changed.connect(on_time_changed)

print("\n" + "=" * 70)
print("测试程序已启动")
print("=" * 70)
print("\n请测试以下功能：")
print("1. 点击'高斯函数' - 应该看到中心对称的彩色山峰")
print("2. 点击'波函数' - 应该看到波浪状的表面")
print("3. 点击'螺旋函数' - 应该看到螺旋图案")
print("4. 拖动时间轴滑块 - 3D图形会随时间变化")
print("5. 点击'播放动画' - 自动播放动画效果")
print("\n如果能看到彩色的3D表面图，说明一切正常！")
print("=" * 70)

window.show()
sys.exit(app.exec())
