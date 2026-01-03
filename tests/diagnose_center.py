# -*- coding: utf-8 -*-
"""诊断坐标系统"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

# 创建40x40网格
rows, cols = 40, 40

print("=" * 60)
print("坐标系统诊断")
print("=" * 60)
print(f"网格大小: {rows}行 x {cols}列")
print(f"行索引范围: 0-{rows-1}")
print(f"列索引范围: 0-{cols-1}")

# 计算几何中心
print("\n几何中心计算:")
print(f"  行中心: ({rows-1}) / 2 = {(rows-1)/2}")
print(f"  列中心: ({cols-1}) / 2 = {(cols-1)/2}")
print(f"  理论几何中心: ({(rows-1)/2}, {(cols-1)/2})")

# 测试当前默认中心
print("\n当前默认中心:")
params = FunctionParams()
print(f"  center = {params.center}")

# 应用高斯函数
func = WindFieldFunctionFactory.create('gaussian', params)
result = func.apply(np.zeros((rows, cols)), time=0.0)

# 找最大值位置
max_val = result.max()
max_pos = np.unravel_index(result.argmax(), result.shape)
print(f"\n高斯函数结果:")
print(f"  最大值: {max_val:.2f}%")
print(f"  最大值位置(行,列): {max_pos}")

# 检查周围的值
print(f"\n最大值周围的风扇转速:")
for dr in [-1, 0, 1]:
    for dc in [-1, 0, 1]:
        r, c = max_pos[0] + dr, max_pos[1] + dc
        if 0 <= r < rows and 0 <= c < cols:
            print(f"  ({r},{c}): {result[r,c]:.2f}%")

# 测试不同中心
print("\n" + "=" * 60)
print("测试不同中心位置")
print("=" * 60)

test_centers = [
    (19.5, 19.5),
    (20.0, 20.0),
    (20.5, 20.5),
    (21.0, 21.0),
]

for center in test_centers:
    params = FunctionParams()
    params.center = center
    params.amplitude = 100.0

    func = WindFieldFunctionFactory.create('gaussian', params)
    result = func.apply(np.zeros((rows, cols)), time=0.0)

    max_pos = np.unravel_index(result.argmax(), result.shape)
    max_val = result[max_pos]

    print(f"中心={center} -> 最大值位置={max_pos}, 值={max_val:.2f}%")
