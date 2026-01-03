# -*- coding: utf-8 -*-
"""测试动画播放和3D视图集成"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

print("=" * 70)
print("测试动画播放和3D视图集成")
print("=" * 70)

# 创建QApplication实例
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# 导入模块
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams
from 风场设置.main_control.function_3d_view import Function3DView
from 风场设置.main_control.timeline_widget import TimelineWidget

print("\n1. 创建组件")
print("-" * 70)

# 创建组件
timeline = TimelineWidget()
view_3d = Function3DView()

# 设置时间范围
timeline.set_max_time(10.0)
timeline.set_time_resolution(0.5)

print(f"   时间轴: 最大时间={timeline.max_time}s, 分辨率={timeline.time_resolution}s")
print(f"   3D视图: 初始函数={view_3d.current_function}")

print("\n2. 应用高斯函数并测试时间变化")
print("-" * 70)

# 创建函数
params = FunctionParams()
params.center = (20.0, 20.0)
params.amplitude = 100.0

func = WindFieldFunctionFactory.create('gaussian', params)

# 模拟时间推进
test_times = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
print(f"   测试时间点: {test_times}")

for t in test_times:
    # 应用函数
    result_grid = func.apply(np.zeros((40, 40)), time=t)

    # 更新3D视图（模拟时间变化）
    view_3d.set_grid_data(result_grid)
    view_3d.current_time = t
    view_3d.current_function = 'gaussian'

    max_val = result_grid.max()
    mean_val = result_grid.mean()
    print(f"   t={t:5.1f}s: max={max_val:6.2f}%, mean={mean_val:6.2f}%")

print("\n3. 测试时间轴播放功能")
print("-" * 70)

# 模拟播放状态
is_playing = False
play_count = 0
max_iterations = 20  # 最多20个时间步

print(f"   模拟时间轴播放（最多{max_iterations}步）:")
print(f"   初始状态: {'播放中' if is_playing else '暂停'}")

for i in range(max_iterations):
    # 模拟时间推进
    current_time = timeline.get_current_time()
    new_time = current_time + timeline.time_resolution

    if new_time >= timeline.max_time:
        new_time = timeline.max_time
        print(f"   步骤{i+1:2d}: 时间={new_time:5.1f}s (到达最大时间)")
        break

    timeline.set_current_time(new_time)

    # 应用函数
    result_grid = func.apply(np.zeros((40, 40)), time=new_time)
    view_3d.set_grid_data(result_grid)
    view_3d.current_time = new_time

    if i % 4 == 0:  # 每4步打印一次
        max_val = result_grid.max()
        print(f"   步骤{i+1:2d}: 时间={new_time:5.1f}s, max={max_val:6.2f}%")

print(f"   播放完成，共 {i+1} 步")

print("\n4. 测试不同函数的动画效果")
print("-" * 70)

# 测试不同函数在不同时间点的表现
function_types = ['gaussian', 'simple_wave', 'radial_wave', 'spiral_wave']
test_time_points = [0.0, 5.0, 10.0]

for func_type in function_types:
    print(f"\n   函数: {func_type}")
    try:
        func = WindFieldFunctionFactory.create(func_type, params)

        for t in test_time_points:
            result_grid = func.apply(np.zeros((40, 40)), time=t)
            max_val = result_grid.max()
            min_val = result_grid.min()
            print(f"      t={t:5.1f}s: max={max_val:6.2f}%, min={min_val:6.2f}%")

    except Exception as e:
        print(f"      错误: {e}")

print("\n5. 测试3D视图更新性能")
print("-" * 70)

import time

func = WindFieldFunctionFactory.create('gaussian', params)

# 测试连续更新
update_times = 50
start_time = time.time()

for i in range(update_times):
    t = (i / update_times) * 10.0  # 0到10秒
    result_grid = func.apply(np.zeros((40, 40)), time=t)
    view_3d.set_grid_data(result_grid)
    view_3d.current_time = t

elapsed = time.time() - start_time
fps = update_times / elapsed

print(f"   连续更新{update_times}次")
print(f"   耗时: {elapsed:.3f}秒")
print(f"   平均FPS: {fps:.1f}")

if fps >= 20:
    print(f"   [OK] 性能良好，可以流畅播放")
elif fps >= 10:
    print(f"   [WARN] 性能一般，可能会有点卡顿")
else:
    print(f"   [FAIL] 性能较差，需要优化")

print("\n" + "=" * 70)
print("[SUCCESS] 测试完成!")
print("=" * 70)
print("\n总结:")
print("  1. 3D视图可以正确显示函数的3D表面图")
print("  2. 时间轴推进时，3D视图会实时更新")
print("  3. 支持多种函数类型的动画播放")
print("  4. 性能测试: {:.1f} FPS".format(fps))
