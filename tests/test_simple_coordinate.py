# -*- coding: utf-8 -*-
"""测试简化后的坐标系统"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

print("=" * 70)
print("测试简化后的坐标系统")
print("=" * 70)

print("\n1. 应用高斯函数（默认中心(20,20)）")
params = FunctionParams()
print(f"   默认中心: {params.center}")

func = WindFieldFunctionFactory.create('gaussian', params)
result = func.apply(np.zeros((40, 40)), time=0.0)

# 检查中心风扇和周围的值
print(f"\n2. 中心风扇和周围的值:")
print(f"   (20,20): {result[20,20]:.2f}% - 中心")
print(f"   (20,21): {result[20,21]:.2f}% - x+1")
print(f"   (21,20): {result[21,20]:.2f}% - y+1")
print(f"   (21,21): {result[21,21]:.2f}% - x+1,y+1")

print(f"\n3. x方向（第20行，列从18到22）:")
for j in range(18, 23):
    dist = abs(j - 20)
    val = result[20, j]
    print(f"   列{j} (距离{dist}): {val:.2f}%")

print(f"\n4. y方向（第20列，行从18到22）:")
for i in range(18, 23):
    dist = abs(i - 20)
    val = result[i, 20]
    print(f"   行{i} (距离{dist}): {val:.2f}%")

# 验证对称性
print(f"\n5. 对称性验证:")
val_2021 = result[20, 21]
val_2120 = result[21, 20]
val_2019 = result[20, 19]
val_1920 = result[19, 20]

print(f"   (20,21): {val_2021:.2f}%")
print(f"   (21,20): {val_2120:.2f}%")
print(f"   (20,19): {val_2019:.2f}%")
print(f"   (19,20): {val_1920:.2f}%")

if abs(val_2021 - val_2120) < 0.01 and abs(val_2021 - val_2019) < 0.01 and abs(val_2021 - val_1920) < 0.01:
    print(f"   [OK] 4个方向对称!")
else:
    print(f"   [WARN] 4个方向不对称")

print("\n" + "=" * 70)
print("[SUCCESS] 测试完成!")
print("=" * 70)
