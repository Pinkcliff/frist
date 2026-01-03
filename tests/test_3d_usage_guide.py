# -*- coding: utf-8 -*-
"""
3D视图和动画功能使用说明

## 功能说明

1. 3D函数视图：显示风场函数的3D表面图
2. 时间轴动画：通过时间轴控制函数随时间变化

## 使用步骤

### 方法一：预览动画模式（推荐）

1. 打开风墙设置程序
2. 点击工具栏的"函数"按钮，或菜单"工具" -> "函数生成器"
3. 在右侧面板会出现"函数模式"工具窗口
4. 在函数工具窗口中：
   - 选择一个函数类型（如"gaussian"高斯函数）
   - 调整参数（中心位置、幅度等）
   - 点击"预览"按钮
5. 函数会立即应用到风墙网格
6. 在底部的时间轴上：
   - 点击"播放"按钮（▶）开始动画
   - 或拖动滑块查看不同时间点的效果
7. 右侧的"3D函数视图"会实时显示函数的3D表面图

### 方法二：直接应用模式

1. 在函数工具窗口中选择函数和参数
2. 点击"应用函数"按钮
3. 函数会立即应用到风墙网格（可以撤销）
4. 3D视图会显示该时间点的函数状态

## 注意事项

1. 必须先点击"预览"或"应用函数"，3D视图才会显示
2. 时间轴范围默认是0-10秒，可以在"设置" -> "时间设置"中修改
3. 不是所有函数都有明显的时间变化效果
4. 3D视图位于右侧Dock面板的底部

## 测试步骤

运行此脚本验证功能：
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

print("=" * 70)
print("3D视图和动画功能 - 使用说明和测试")
print("=" * 70)

# 创建QApplication实例
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# 导入模块
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams
from 风场设置.main_control.function_3d_view import Function3DView
from 风场设置.main_control.timeline_widget import TimelineWidget

print("\n[功能测试]")
print("-" * 70)

# 创建组件
timeline = TimelineWidget()
view_3d = Function3DView()

print("\n1. 组件初始化状态:")
print(f"   时间轴最大时间: {timeline.max_time}s")
print(f"   时间轴分辨率: {timeline.time_resolution}s")
print(f"   3D视图当前函数: {view_3d.current_function}")
print(f"   3D视图当前时间: {view_3d.current_time}s")

# 应用高斯函数并测试
print("\n2. 应用高斯函数:")
params = FunctionParams()
params.center = (20.0, 20.0)
params.amplitude = 100.0

func = WindFieldFunctionFactory.create('gaussian', params)
result_grid = func.apply(np.zeros((40, 40)), time=0.0)

print(f"   网格形状: {result_grid.shape}")
print(f"   最大值: {result_grid.max():.2f}%")
print(f"   最小值: {result_grid.min():.2f}%")
print(f"   平均值: {result_grid.mean():.2f}%")

# 更新3D视图
view_3d.set_grid_data(result_grid)
view_3d.current_function = 'gaussian'
view_3d.current_time = 0.0

print("\n3. 3D视图已更新")
print("   提示: 在主程序中，3D视图会显示在右侧面板底部")

# 测试时间变化
print("\n4. 测试时间变化效果:")
time_points = [0.0, 2.5, 5.0, 7.5, 10.0]

for t in time_points:
    result_grid = func.apply(np.zeros((40, 40)), time=t)
    view_3d.set_grid_data(result_grid)
    view_3d.current_time = t
    max_val = result_grid.max()
    print(f"   t={t:5.1f}s: 最大值={max_val:6.2f}%")

print("\n[推荐函数]")
print("-" * 70)
print("1. gaussian - 高斯函数（中心对称，效果最明显）")
print("2. simple_wave - 简单波函数（随时间波动）")
print("3. radial_wave - 径向波函数（向外扩散的波）")
print("4. spiral_wave - 螺旋波函数（旋转效果）")
print("5. gaussian_packet - 高斯波包（波传播效果）")

print("\n[故障排除]")
print("-" * 70)
print("问题: 3D视图不显示")
print("解决: ")
print("  1. 确保已点击'预览'或'应用函数'按钮")
print("  2. 检查右侧面板是否有'3D函数视图'分组")
print("  3. 尝试拖动右侧Dock面板的边界调整大小")
print("  4. 查看控制台是否有'3D视图初始化成功'的消息")

print("\n问题: 动画不播放")
print("解决: ")
print("  1. 确保已点击'预览'按钮激活函数")
print("  2. 点击时间轴的播放按钮（▶）")
print("  3. 或手动拖动时间轴滑块")
print("  4. 检查函数是否支持时间参数")

print("\n" + "=" * 70)
print("[完成] 测试结束")
print("=" * 70)

# 显示组件（可选）
view_3d.show()
view_3d.resize(600, 500)

print("\n3D视图窗口已显示（测试窗口）")
print("在实际程序中，3D视图会嵌入在右侧面板中")
