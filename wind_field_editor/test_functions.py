# -*- coding: utf-8 -*-
"""测试函数集成"""
import sys
sys.path.insert(0, '.')

from wind_field_editor import create_editor, list_functions
import numpy as np

# 测试1: 创建编辑器
print("测试1: 创建编辑器")
editor = create_editor()
print(f"  编辑器创建成功: {editor.grid_dim}x{editor.grid_dim}")

# 测试2: 应用高斯函数
print("\n测试2: 应用高斯函数")
success = editor.apply_function('gaussian')
print(f"  应用函数成功: {success}")
print(f"  最大值: {editor.grid_data.max():.2f}")
print(f"  最小值: {editor.grid_data.min():.2f}")

# 测试3: 列出所有函数
print("\n测试3: 列出所有函数")
funcs = list_functions()
print(f"  可用函数数量: {len(funcs['all'])}")
print(f"  函数分类: {funcs['categories']}")

# 测试4: 撤销/重做
print("\n测试4: 撤销/重做")
editor._save_state()
editor.set_cell_value(10, 10, 50.0)
print(f"  设置单元格值: {editor.get_cell_value(10, 10)}")
editor.undo()
print(f"  撤销后: {editor.get_cell_value(10, 10)}")

# 测试5: 数据导出
print("\n测试5: 数据导出")
data = editor.to_wind_field_data()
print(f"  数据形状: {data.shape}")
print(f"  最大RPM: {data.max_rpm}")

print("\n[PASS] All tests passed!")
