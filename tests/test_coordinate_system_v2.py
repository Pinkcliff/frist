# -*- coding: utf-8 -*-
"""测试新的坐标系统 v2"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

print("=" * 70)
print("测试新的坐标系统")
print("=" * 70)

print("\n1. 验证坐标系统定义")
print("   中心点在(20.5, 20.5)")
print("   风扇(20,20)的坐标: x=20-20+0.5=0.5, y=20-20+0.5=0.5")
print("   风扇(20,21)的坐标: x=21-20+0.5=1.5, y=20-20+0.5=0.5")
print("   风扇(21,20)的坐标: x=20-20+0.5=0.5, y=21-20+0.5=1.5")
print("   风扇(21,21)的坐标: x=21-20+0.5=1.5, y=21-20+0.5=1.5")

print("\n2. 应用高斯函数（默认中心(20,20)）")
params = FunctionParams()
print(f"   默认中心: {params.center}")

func = WindFieldFunctionFactory.create('gaussian', params)
result = func.apply(np.zeros((40, 40)), time=0.0)

# 检查4个中心风扇的值
print("\n3. 检查4个中心风扇的值:")
for i in [20, 21]:
    for j in [20, 21]:
        val = result[i, j]
        # 计算坐标
        x = j - 20 + 0.5
        y = i - 20 + 0.5
        dist_sq = x**2 + y**2
        expected = 100.0 * np.exp(-dist_sq / (2 * 5.0**2))
        print(f"   风扇({i},{j}): x={x:.1f}, y={y:.1f}, r2={dist_sq:.2f}, 值={val:.2f}%, 期望={expected:.2f}%")

# 检查对称性
val_2020 = result[20, 20]
val_2021 = result[20, 21]
val_2120 = result[21, 20]
val_2121 = result[21, 21]

print(f"\n4. 对称性验证:")
print(f"   2020: {val_2020:.2f}%")
print(f"   2021: {val_2021:.2f}%")
print(f"   2120: {val_2120:.2f}%")
print(f"   2121: {val_2121:.2f}%")

if abs(val_2020 - val_2021) < 0.01 and abs(val_2020 - val_2120) < 0.01 and abs(val_2020 - val_2121) < 0.01:
    print("   [OK] 4个中心风扇的值相同!")
else:
    print("   [FAIL] 4个中心风扇的值不相同!")

# 检查周围的值
print(f"\n5. 检查周围的值（验证x+0.5, y+0.5规则）:")
# x正方向+0.5: 从(0.5)到(1.5)
print("   x正方向（行20，列从20到22）:")
for j in [20, 21, 22]:
    val = result[20, j]
    x = j - 20 + 0.5
    print(f"   列{j}: x={x:.1f}, 值={val:.2f}%")

# y正方向+0.5: 从(0.5)到(1.5)
print("   y正方向（列20，行从20到22）:")
for i in [20, 21, 22]:
    val = result[i, 20]
    y = i - 20 + 0.5
    print(f"   行{i}: y={y:.1f}, 值={val:.2f}%")

# 测试平移后的中心
print(f"\n6. 测试平移后的中心:")
test_centers = [(19, 19), (21, 21), (20, 19)]
for center in test_centers:
    params = FunctionParams()
    params.center = (float(center[0]), float(center[1]))
    func = WindFieldFunctionFactory.create('gaussian', params)
    result = func.apply(np.zeros((40, 40)), time=0.0)

    # 检查以该点为中心的4个风扇
    base_i, base_j = center
    vals = []
    print(f"   中心({base_i},{base_j})周围:")
    for di in [0, 1]:
        for dj in [0, 1]:
            i, j = base_i + di, base_j + dj
            if i < 40 and j < 40:
                val = result[i, j]
                vals.append(val)
                x = j - 20 + 0.5
                y = i - 20 + 0.5
                print(f"     风扇({i},{j}): x={x:.1f}, y={y:.1f}, 值={val:.2f}%")

    # 检查对称性
    if len(vals) == 4:
        if max(vals) - min(vals) < 0.01:
            print(f"     [OK] 对称!")
        else:
            print(f"     [WARN] 不对称: max={max(vals):.2f}%, min={min(vals):.2f}%")

print("\n" + "=" * 70)
print("[SUCCESS] 测试完成!")
print("=" * 70)
