# -*- coding: utf-8 -*-
"""测试新的中心位置系统"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from wind_field_editor.functions import WindFieldFunctionFactory, FunctionParams

print("=" * 60)
print("测试新的中心位置系统")
print("=" * 60)

# 测试默认中心
print("\n1. 测试默认中心")
params = FunctionParams()
print(f"   默认中心: {params.center}")
assert params.center == (19.0, 19.0), "默认中心应该是(19.0, 19.0)"
print("   [OK] 默认中心正确: (19.0, 19.0)")

# 应用高斯函数
func = WindFieldFunctionFactory.create('gaussian', params)
result = func.apply(np.zeros((40, 40)), time=0.0)

max_val = result.max()
max_pos = np.unravel_index(result.argmax(), result.shape)
print(f"   最大值位置(0-based): {max_pos}")
print(f"   显示位置(1-based): x{max_pos[1]+1:03d}y{max_pos[0]+1:03d}")
print(f"   最大值: {max_val:.2f}%")

assert max_pos == (19, 19), f"最大值应该在(19,19)，但实际在{max_pos}"
print("   [OK] 中心位置正确")

# 检查中心风扇的值
center_value = result[19, 19]
print(f"   中心风扇(19,19)的值: {center_value:.2f}%")

# 测试平移功能
print("\n2. 测试不同中心位置")
test_centers = [
    ((19, 19), "x020y020"),
    ((18, 19), "x020y019"),
    ((19, 18), "x019y020"),
    ((20, 19), "x020y021"),
    ((19, 20), "x021y020"),
]

for center, expected_display in test_centers:
    params = FunctionParams()
    params.center = (float(center[0]), float(center[1]))
    func = WindFieldFunctionFactory.create('gaussian', params)
    result = func.apply(np.zeros((40, 40)), time=0.0)

    max_pos = np.unravel_index(result.argmax(), result.shape)
    display = f"x{max_pos[1]+1:03d}y{max_pos[0]+1:03d}"

    assert display == expected_display, f"期望显示{expected_display}，但实际是{display}"
    print(f"   中心{center} -> 显示{display} [OK]")

print("\n" + "=" * 60)
print("[SUCCESS] 所有测试通过!")
print("=" * 60)
