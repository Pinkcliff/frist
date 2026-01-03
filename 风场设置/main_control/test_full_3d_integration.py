# -*- coding: utf-8 -*-
"""
完整的3D视图集成测试

模拟主程序中的完整流程，验证3D视图是否正确显示
"""
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDockWidget, QStackedWidget, QFormLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

import numpy as np

print("=" * 70)
print("完整3D视图集成测试")
print("=" * 70)

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# 导入所有需要的模块
from 风场设置.main_control.function_3d_view import Function3DView
from 风场设置.main_control.enhanced_function_tool import EnhancedFunctionToolWindow
from 风场设置.main_control.timeline_widget import TimelineWidget
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

# 创建主窗口
main_window = QMainWindow()
main_window.setWindowTitle("3D视图完整测试")
main_window.resize(1400, 900)

# 创建中央组件
central_widget = QWidget()
central_layout = QVBoxLayout(central_widget)
central_widget.setLayout(central_layout)
main_window.setCentralWidget(central_widget)

# 添加中央占位符
central_label = QLabel("中央区域 - 风墙画布")
central_label.setStyleSheet("background: #ddd; padding: 50px; font-size: 20px;")
central_layout.addWidget(central_label)

# 创建时间轴
timeline = TimelineWidget()
central_layout.addWidget(timeline)

print("\n1. 创建右侧Dock面板")

# 创建Dock面板
right_dock = QDockWidget("工具与信息", main_window)
right_dock.setAllowedAreas(Qt.RightDockWidgetArea)
right_dock.setMinimumWidth(400)

dock_container = QWidget()
dock_container.setMinimumWidth(400)
dock_layout = QVBoxLayout(dock_container)
dock_layout.setContentsMargins(5, 5, 5, 5)
dock_layout.setSpacing(5)

# 创建工具面板
tool_mode_group = QGroupBox("点选模式")
tool_stack = QStackedWidget()
function_widget = EnhancedFunctionToolWindow(main_window)
tool_stack.addWidget(function_widget)

tool_mode_layout = QVBoxLayout()
tool_mode_layout.addWidget(tool_stack)
tool_mode_group.setLayout(tool_mode_layout)

# 创建状态面板
status_group = QGroupBox("状态信息")
status_layout = QFormLayout()
for i in range(6):
    label = QLabel("--")
    status_layout.addRow(f"项目{i}:", label)
status_group.setLayout(status_layout)

# 创建信息面板
info_group = QGroupBox("系统信息")
info_layout = QVBoxLayout()
info_output = QTextEdit()
info_output.setReadOnly(True)
info_output.append("系统就绪...")
info_layout.addWidget(info_output)
info_group.setLayout(info_layout)

# 创建3D视图
print("   - 创建3D视图组件...")
view_3d_group = QGroupBox("3D函数视图")
view_3d_group.setStyleSheet("QGroupBox { font-weight: bold; }")
view_3d_layout = QVBoxLayout()
view_3d_layout.setContentsMargins(5, 5, 5, 5)

function_3d_view = Function3DView(main_window)
view_3d_layout.addWidget(function_3d_view)
view_3d_group.setLayout(view_3d_layout)

from PySide6.QtWidgets import QSizePolicy
function_3d_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
view_3d_group.setMinimumSize(350, 350)

print("   - 添加组件到Dock布局...")

# 设置布局比例
dock_layout.addWidget(tool_mode_group, 8)
dock_layout.addWidget(status_group, 4)
dock_layout.addWidget(info_group, 4)
dock_layout.addWidget(view_3d_group, 50)

dock_layout.setStretch(0, 8)
dock_layout.setStretch(1, 4)
dock_layout.setStretch(2, 4)
dock_layout.setStretch(3, 50)

right_dock.setWidget(dock_container)
main_window.addDockWidget(Qt.RightDockWidgetArea, right_dock)

print("\n2. 连接信号和槽")

def log_message(msg):
    info_output.append(f"[{msg}]")
    print(f"[LOG] {msg}")

# 连接时间轴信号
timeline.time_changed.connect(lambda t: log_message(f"时间变化: {t:.1f}s"))

# 连接函数工具信号
def apply_function(func_type, params, time_val):
    log_message(f"应用函数: {func_type}")
    try:
        func_params = FunctionParams()
        if 'center' in params:
            func_params.center = params['center']
        if 'amplitude' in params:
            func_params.amplitude = params['amplitude']

        func = WindFieldFunctionFactory.create(func_type, func_params)
        result_grid = func.apply(np.zeros((40, 40)), time=time_val)

        # 更新3D视图
        function_3d_view.set_grid_data(result_grid)
        function_3d_view.current_function = func_type
        function_3d_view.current_time = time_val

        log_message(f"  最大值: {result_grid.max():.2f}%")
        log_message(f"  平均值: {result_grid.mean():.2f}%")
        log_message(f"  3D视图已更新")

    except Exception as e:
        log_message(f"  错误: {e}")

function_widget.apply_function_signal.connect(apply_function)
function_widget.preview_animation_signal.connect(lambda ft, pm: apply_function(ft, pm, 0.0))

print("\n3. 显示窗口")
main_window.show()
log_message("主窗口已显示")
log_message("请检查右侧面板底部是否有'3D函数视图'")
log_message("应该能看到彩色的3D表面图（高斯函数）")

print("\n" + "=" * 70)
print("测试程序已启动")
print("请查看窗口，验证3D视图是否显示在右侧面板底部")
print("=" * 70)

sys.exit(app.exec())
