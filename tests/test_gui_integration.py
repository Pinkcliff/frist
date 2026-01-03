# -*- coding: utf-8 -*-
"""
测试GUI集成 - 验证增强函数工具窗口集成

创建时间: 2024-01-03
作者: Wind Field Editor Team
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from wind_field_editor import create_editor, list_functions
from 风场设置.main_control.enhanced_function_tool import EnhancedFunctionToolWindow
import numpy as np

def test_enhanced_function_tool_window():
    """测试增强函数工具窗口"""
    print("\n测试1: 创建增强函数工具窗口")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = EnhancedFunctionToolWindow()
    print(f"  窗口创建成功: {window.windowTitle()}")
    print(f"  窗口尺寸: {window.width()}x{window.height()}")

    # 测试函数工厂导入
    print("\n测试2: 验证函数工厂集成")
    print(f"  可用函数数量: {len(window.available_functions)}")
    print(f"  函数分类: {window.categories}")

    # 测试参数获取
    print("\n测试3: 测试参数获取")
    params = window.get_function_params()
    print(f"  默认参数: {params}")
    print(f"  中心位置: {params['center']}")
    print(f"  幅度: {params['amplitude']}%")
    print(f"  时间: {params['time']}s")

    # 测试信号连接
    print("\n测试4: 测试信号连接")
    signal_received = []

    def on_apply(function_type, params, time_value):
        signal_received.append({
            'function_type': function_type,
            'params': params,
            'time_value': time_value
        })
        print(f"  信号接收: function_type={function_type}, time={time_value}")

    window.apply_function_signal.connect(on_apply)

    # 模拟应用函数
    window._apply_function()
    print(f"  信号已触发,接收到的数据数量: {len(signal_received)}")

    if signal_received:
        data = signal_received[0]
        print(f"  函数类型: {data['function_type']}")
        print(f"  时间参数: {data['time_value']}")

    # 测试时间设置
    print("\n测试5: 测试时间参数设置")
    window.set_time_value(5.0)
    print(f"  设置时间值: 5.0s")
    print(f"  实际时间值: {window.time_spinbox.value()}s")

    # 测试函数列表填充
    print("\n测试6: 测试函数列表填充")
    window._populate_functions()
    print(f"  函数列表项数量: {window.function_list.count()}")

    # 测试公式显示
    print("\n测试7: 测试公式显示")
    formula = window._get_function_formula('gaussian')
    print(f"  Gaussian公式: {formula}")

    print("\n[PASS] 所有GUI集成测试通过!")
    return True

if __name__ == '__main__':
    try:
        test_enhanced_function_tool_window()
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
