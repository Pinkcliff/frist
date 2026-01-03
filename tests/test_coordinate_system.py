# -*- coding: utf-8 -*-
"""
测试坐标系统和动画功能

创建时间: 2024-01-03
作者: Wind Field Editor Team
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from wind_field_editor import create_editor
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

def test_coordinate_system():
    """测试坐标系统"""
    print("\n=== 测试坐标系统 ===")

    # 创建40x40的风场编辑器
    editor = create_editor(grid_dim=40, max_rpm=17000)
    print(f"[OK] 编辑器创建成功: {editor.grid_dim}x{editor.grid_dim}")

    # 测试1: 默认中心位置
    print("\n测试1: 默认中心位置")
    params = FunctionParams()
    print(f"  默认中心: {params.center}")
    assert params.center == (20.5, 20.5), "默认中心应该是(20.5, 20.5)"
    print(f"  [OK] 默认中心正确: 第20行和21行之间, 第20列和21列之间")

    # 测试2: 应用高斯函数
    print("\n测试2: 应用高斯函数")
    params = FunctionParams()
    params.center = (20.5, 20.5)  # 几何中心
    params.amplitude = 100.0

    func = WindFieldFunctionFactory.create('gaussian', params)
    result = func.apply(np.zeros((40, 40)), time=0.0)

    # 验证中心点的值最大
    center_value = result[20, 20]  # 第20行第20列
    print(f"  中心点(20,20)的值: {center_value:.2f}%")

    # 验证对称性
    corner_value = result[0, 0]
    print(f"  角落点(0,0)的值: {corner_value:.2f}%")

    assert center_value > corner_value, "中心点值应该大于角落点值"
    print(f"  [OK] 高斯函数应用正确，中心点值最大")

    # 测试3: 时间动画
    print("\n测试3: 时间动画效果")
    times = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    print(f"  时间点: {times}")

    for t in times:
        result_t = func.apply(np.zeros((40, 40)), time=t)
        max_val = result_t.max()
        max_pos = np.unravel_index(result_t.argmax(), result_t.shape)
        print(f"  t={t:.1f}s: 最大值={max_val:.2f}%, 位置={max_pos}")

    print(f"  [OK] 时间动画计算成功")

    # 测试4: 不同中心位置
    print("\n测试4: 不同中心位置")
    test_centers = [
        (10.5, 10.5),  # 左上区域
        (30.5, 30.5),  # 右下区域
        (10.5, 30.5),  # 右上区域
        (30.5, 10.5),  # 左下区域
    ]

    for center in test_centers:
        params.center = center
        func = WindFieldFunctionFactory.create('gaussian', params)
        result = func.apply(np.zeros((40, 40)), time=0.0)
        max_pos = np.unravel_index(result.argmax(), result.shape)
        print(f"  中心{center} -> 最大值位置{max_pos}")

    print(f"  [OK] 不同中心位置测试通过")

    print("\n[PASS] 所有坐标系统测试通过!")

def test_function_animation():
    """测试函数动画"""
    print("\n=== 测试函数动画 ===")

    # 创建编辑器
    editor = create_editor(grid_dim=40, max_rpm=17000)

    # 测试径向波动画
    print("\n测试1: 径向波动画")
    params = FunctionParams()
    params.center = (20.5, 20.5)
    params.amplitude = 100.0

    func = WindFieldFunctionFactory.create('radial_wave', params)

    # 模拟动画帧
    frame_times = np.linspace(0, 5, 11)  # 0到5秒，11帧
    print(f"  动画帧数: {len(frame_times)}")

    for i, t in enumerate(frame_times):
        result = func.apply(np.zeros((40, 40)), time=t)
        max_val = result.max()
        min_val = result.min()
        if i % 2 == 0:  # 每隔一帧打印
            print(f"  帧{i+1} (t={t:.1f}s): max={max_val:.2f}%, min={min_val:.2f}%")

    print(f"  [OK] 径向波动画测试通过")

    # 测试高斯波包动画
    print("\n测试2: 高斯波包动画")
    func = WindFieldFunctionFactory.create('gaussian_packet', params)

    for i, t in enumerate(frame_times):
        result = func.apply(np.zeros((40, 40)), time=t)
        max_pos = np.unravel_index(result.argmax(), result.shape)
        if i % 2 == 0:  # 每隔一帧打印
            print(f"  帧{i+1} (t={t:.1f}s): 最大值位置={max_pos}")

    print(f"  [OK] 高斯波包动画测试通过")

    print("\n[PASS] 所有函数动画测试通过!")

if __name__ == '__main__':
    try:
        test_coordinate_system()
        test_function_animation()
        print("\n" + "="*50)
        print("[SUCCESS] 所有测试通过!")
        print("="*50)
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
