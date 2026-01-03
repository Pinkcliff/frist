# -*- coding: utf-8 -*-
"""
3D视图位置诊断和修复

这个脚本会在主程序界面上添加明显的标记，帮助定位3D视图的位置
"""
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QDockWidget, QStackedWidget, QFormLayout, QLabel,
    QTextEdit, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

import numpy as np

print("=" * 70)
print("3D视图位置诊断工具")
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
main_window.setWindowTitle("3D视图位置诊断 - 请查找底部有红色边框的3D视图")
main_window.resize(1600, 900)

# 创建中央组件
central_widget = QWidget()
central_layout = QHBoxLayout(central_widget)
main_window.setCentralWidget(central_widget)

# 左侧占位符（模拟风墙画布）
left_panel = QWidget()
left_panel.setStyleSheet("background: #e0e0e0;")
left_layout = QVBoxLayout(left_panel)
left_label = QLabel("风墙画布区域")
left_label.setAlignment(Qt.AlignCenter)
left_label.setStyleSheet("font-size: 24px; color: #666; padding: 50px;")
left_layout.addWidget(left_label)
central_layout.addWidget(left_panel, 2)  # 占2/3宽度

# 右侧Dock容器（直接放在中央布局中，不使用Dock）
right_panel = QWidget()
right_panel.setMinimumWidth(450)
right_panel.setStyleSheet("background: #f5f5f5; border-left: 2px solid #ccc;")
right_layout = QVBoxLayout(right_panel)
right_layout.setContentsMargins(10, 10, 10, 10)
right_layout.setSpacing(10)
central_layout.addWidget(right_panel, 1)  # 占1/3宽度

# 1. 工具模式面板（缩小）
tool_group = QGroupBox("1. 工具选择区域")
tool_group.setStyleSheet("QGroupBox { font-weight: bold; background: #fff; }")
tool_group.setMaximumHeight(200)
tool_layout = QVBoxLayout()
tool_stack = QStackedWidget()
function_widget = EnhancedFunctionToolWindow(main_window)
tool_stack.addWidget(function_widget)
tool_layout.addWidget(tool_stack)
tool_group.setLayout(tool_layout)
right_layout.addWidget(tool_group)

# 2. 状态面板（缩小）
status_group = QGroupBox("2. 状态信息")
status_group.setStyleSheet("QGroupBox { font-weight: bold; background: #fff; }")
status_group.setMaximumHeight(150)
status_layout = QFormLayout()
for i in range(3):
    label = QLabel("--")
    status_layout.addRow(f"项目{i}:", label)
status_group.setLayout(status_layout)
right_layout.addWidget(status_group)

# 3. 信息面板（缩小）
info_group = QGroupBox("3. 系统信息")
info_group.setStyleSheet("QGroupBox { font-weight: bold; background: #fff; }")
info_group.setMaximumHeight(120)
info_layout = QVBoxLayout()
info_output = QTextEdit()
info_output.setReadOnly(True)
info_output.setMaximumHeight(100)
info_output.append("系统就绪...")
info_layout.addWidget(info_output)
info_group.setLayout(info_layout)
right_layout.addWidget(info_group)

# 4. 3D视图面板（突出显示）
view_3d_group = QGroupBox("⭐ 4. 3D函数视图 (应该在这里看到彩色图形) ⭐")
view_3d_group.setStyleSheet("""
    QGroupBox {
        font-weight: bold;
        background: #fff8e1;
        border: 3px solid red;
        color: red;
        font-size: 14px;
    }
""")
view_3d_group.setMinimumSize(400, 400)

view_3d_layout = QVBoxLayout()
view_3d_layout.setContentsMargins(10, 10, 10, 10)

# 添加说明标签
hint_label = QLabel("👇 下图是3D函数视图，应该能看到彩色的3D表面图 👇")
hint_label.setAlignment(Qt.AlignCenter)
hint_label.setStyleSheet("color: #ff6600; font-weight: bold; padding: 5px; background: #fff3cd;")
view_3d_layout.addWidget(hint_label)

# 创建3D视图
function_3d_view = Function3DView(main_window)
function_3d_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
function_3d_view.setMinimumSize(380, 350)
view_3d_layout.addWidget(function_3d_view)

view_3d_group.setLayout(view_3d_layout)
right_layout.addWidget(view_3d_group, 1)  # 设置stretch=1，让它占据剩余空间

# 设置stretch因子
right_layout.setStretch(0, 0)
right_layout.setStretch(1, 0)
right_layout.setStretch(2, 0)
right_layout.setStretch(3, 1)  # 3D视图占据所有剩余空间

# 添加日志输出
def log(msg):
    info_output.append(f"[{msg}]")

log("程序已启动")
log("")
log("=== 请检查右侧面板 ===")
log("1. 最顶部：工具选择区域")
log("2. 中间上部：状态信息")
log("3. 中间下部：系统信息")
log("4. ⭐ 底部：3D函数视图（红色边框）⭐")
log("")
log("如果没有看到3D图形：")
log("  - 可能需要向下滚动")
log("  - 或拖动窗口边界")
log("")

# 添加测试按钮
test_layout = QHBoxLayout()

btn_test = QPushButton("测试3D视图")
btn_test.setStyleSheet("""
    QPushButton {
        background: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 10px;
        font-size: 14px;
    }
""")
btn_test.clicked.connect(lambda: test_3d_view())

btn_clear = QPushButton("清空数据")
btn_clear.setStyleSheet("padding: 10px;")
btn_clear.clicked.connect(lambda: clear_3d_view())

test_layout.addWidget(btn_test)
test_layout.addWidget(btn_clear)
right_layout.insertLayout(3, test_layout)  # 插入到3D视图之前

def test_3d_view():
    """测试3D视图"""
    log("正在测试3D视图...")
    try:
        params = FunctionParams()
        params.center = (20.0, 20.0)
        params.amplitude = 100.0

        func = WindFieldFunctionFactory.create('gaussian', params)
        result_grid = func.apply(np.zeros((40, 40)), time=0.0)

        function_3d_view.set_grid_data(result_grid)
        function_3d_view.current_function = 'gaussian'
        function_3d_view.current_time = 0.0

        log(f"[OK] 测试成功！")
        log(f"    最大值: {result_grid.max():.2f}%")
        log(f"    平均值: {result_grid.mean():.2f}%")
        log(f"    如果能看到彩色的3D图形，说明3D视图工作正常")

    except Exception as e:
        log(f"[ERROR] 测试失败: {e}")

def clear_3d_view():
    """清空3D视图"""
    function_3d_view.grid_data = np.zeros((40, 40))
    function_3d_view._update_plot()
    log("3D视图已清空")

# 连接函数工具信号
def apply_function(func_type, params, time_val):
    log(f"应用函数: {func_type}")
    test_3d_view()

function_widget.apply_function_signal.connect(apply_function)
function_widget.preview_animation_signal.connect(lambda ft, pm: apply_function(ft, pm, 0.0))

print("\n" + "=" * 70)
print("诊断程序已启动")
print("=" * 70)
print("\n请查看窗口：")
print("  - 右侧面板应该有4个区域")
print("  - 最底部有一个红色边框的区域是3D视图")
print("  - 点击'测试3D视图'按钮可以更新3D图形")
print("\n如果能看到彩色的3D图形，说明3D视图工作正常！")
print("问题只是在于主程序的布局或显示。")
print("=" * 70)

main_window.show()
sys.exit(app.exec())
