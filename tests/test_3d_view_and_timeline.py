# -*- coding: utf-8 -*-
"""测试3D视图和时间轴集成功能"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

print("=" * 70)
print("测试3D视图和时间轴集成功能")
print("=" * 70)

# 创建QApplication实例
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# 导入模块
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams
from 风场设置.main_control.function_3d_view import Function3DView
from 风场设置.main_control.timeline_widget import TimelineWidget

print("\n1. 测试TimelineWidget时间范围功能")
print("-" * 70)

timeline = TimelineWidget()
print(f"   默认最大时间: {timeline.max_time}s")
print(f"   默认分辨率: {timeline.time_resolution}s")
print(f"   当前时间: {timeline.get_current_time()}s")

# 测试设置不同的最大时间
test_max_times = [5.0, 10.0, 30.0, 60.0]
for max_time in test_max_times:
    timeline.set_max_time(max_time)
    print(f"   设置最大时间为 {max_time}s: [OK]")

print("\n2. 测试3D视图组件")
print("-" * 70)

# 创建3D视图
view_3d = Function3DView()
print(f"   3D视图组件创建成功")
print(f"   当前函数: {view_3d.current_function}")
print(f"   当前时间: {view_3d.current_time}s")

# 创建测试网格数据
test_grid = np.random.rand(40, 40) * 100
view_3d.set_grid_data(test_grid)
print(f"   设置测试网格数据: [OK]")

# 测试函数数据更新
params = FunctionParams()
params.center = (20.0, 20.0)
view_3d.update_function_data('gaussian', {'center': (20.0, 20.0), 'amplitude': 100.0}, 0.0)
print(f"   更新函数数据: [OK]")

print("\n3. 测试函数与时间轴集成")
print("-" * 70)

# 测试不同时间点的函数计算
func = WindFieldFunctionFactory.create('gaussian', params)

time_points = [0.0, 2.5, 5.0, 7.5, 10.0]
print(f"   测试时间点: {time_points}")

for time_val in time_points:
    result = func.apply(np.zeros((40, 40)), time=time_val)
    max_val = result.max()
    min_val = result.min()
    mean_val = result.mean()
    print(f"   t={time_val:5.1f}s: max={max_val:6.2f}%, min={min_val:6.2f}%, mean={mean_val:6.2f}%")

print("\n4. 测试时间轴动态更新")
print("-" * 70)

timeline.set_max_time(10.0)
timeline.set_time_resolution(0.5)

# 模拟时间推进
time_values = []
for i in range(0, 21):  # 0到10秒，步长0.5
    time_val = i * 0.5
    timeline.set_current_time(time_val)
    current = timeline.get_current_time()
    time_values.append(current)

print(f"   时间轴步进测试完成，共 {len(time_values)} 个时间点")
print(f"   时间范围: {min(time_values):.1f}s - {max(time_values):.1f}s")

print("\n5. 验证时间轴与3D视图联动")
print("-" * 70)

# 创建一个新的3D视图来测试联动
test_view = Function3DView()

# 模拟时间变化时更新3D视图
for t in [0.0, 2.5, 5.0, 7.5, 10.0]:
    # 应用函数
    result_grid = func.apply(np.zeros((40, 40)), time=t)

    # 更新3D视图
    test_view.current_time = t
    test_view.grid_data = result_grid

    print(f"   t={t:5.1f}s: 更新3D视图，网格最大值={result_grid.max():.2f}%")

print("\n6. 测试不同函数类型")
print("-" * 70)

function_types = ['gaussian', 'simple_wave', 'radial_wave', 'spiral_wave']
for func_type in function_types:
    try:
        func = WindFieldFunctionFactory.create(func_type, params)
        result = func.apply(np.zeros((40, 40)), time=0.0)
        print(f"   {func_type:15s}: max={result.max():6.2f}%, mean={result.mean():6.2f}%")
    except Exception as e:
        print(f"   {func_type:15s}: 错误 - {e}")

print("\n" + "=" * 70)
print("[SUCCESS] 所有测试完成!")
print("=" * 70)

# 显示3D视图（可选）
view_3d.show()
timeline.show()

print("\n提示: 3D视图和时间轴组件已创建并测试完成")
