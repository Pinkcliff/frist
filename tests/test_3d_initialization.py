# -*- coding: utf-8 -*-
"""测试3D视图的初始化和显示"""
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QApplication
import numpy as np

print("=" * 70)
print("测试3D视图初始化")
print("=" * 70)

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from 风场设置.main_control.function_3d_view import Function3DView

print("\n1. 创建3D视图组件")
view_3d = Function3DView()
print(f"   最小高度: {view_3d.minimumHeight()}")
print(f"   最小宽度: {view_3d.minimumWidth()}")

print("\n2. 检查3D图形是否初始化")
if hasattr(view_3d, 'ax') and view_3d.ax is not None:
    print("   [OK] 3D轴已创建")
else:
    print("   [FAIL] 3D轴未创建")

if hasattr(view_3d, 'canvas') and view_3d.canvas is not None:
    print("   [OK] 画布已创建")
else:
    print("   [FAIL] 画布未创建")

if hasattr(view_3d, 'figure') and view_3d.figure is not None:
    print("   [OK] 图形已创建")
else:
    print("   [FAIL] 图形未创建")

print("\n3. 测试更新函数")
test_data = np.random.rand(40, 40) * 100
view_3d.set_grid_data(test_data)
print("   [OK] 数据更新完成")

print("\n4. 显示3D视图窗口")
view_3d.setWindowTitle("3D视图测试 - 应该显示彩色3D表面图")
view_3d.resize(600, 500)
view_3d.show()

print("\n提示: 应该能看到一个窗口，里面有彩色的3D表面图")
print("如果看不到图形，说明matplotlib配置有问题")

print("\n" + "=" * 70)
print("测试完成！窗口将保持打开...")
print("=" * 70)

sys.exit(app.exec())
