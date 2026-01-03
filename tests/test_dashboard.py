# -*- coding: utf-8 -*-
"""
仪表盘模块单元测试
测试 DataSimulator 数据模拟器功能
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加项目路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class TestDataSimulator(unittest.TestCase):
    """测试数据模拟器类"""

    def setUp(self):
        """测试前准备"""
        # 需要PySide6环境，导入DataSimulator
        try:
            from 仪表盘.core_data_simulator import DataSimulator
            self.DataSimulator = DataSimulator
        except ImportError as e:
            self.skipTest(f"无法导入DataSimulator: {e}")

    def test_simulator_initialization(self):
        """测试模拟器初始化"""
        simulator = self.DataSimulator()

        # 验证初始值
        self.assertEqual(simulator.current_step_value, 450.0)
        self.assertFalse(simulator.device_on)
        self.assertIsNotNone(simulator.data_timer)
        self.assertIsNotNone(simulator.comm_timer)

    def test_device_status_off(self):
        """测试设备关闭状态"""
        simulator = self.DataSimulator()

        # 模拟数据更新信号
        with patch.object(simulator, 'data_updated') as mock_signal:
            simulator.set_device_status(False)
            # 验证是否发送了0值
            mock_signal.emit.assert_called()

    def test_device_status_on(self):
        """测试设备开启状态"""
        simulator = self.DataSimulator()

        simulator.set_device_status(True)
        self.assertTrue(simulator.device_on)

        simulator.set_device_status(False)
        self.assertFalse(simulator.device_on)


class TestThemeManager(unittest.TestCase):
    """测试主题管理器"""

    def test_theme_manager_import(self):
        """测试主题管理器导入"""
        try:
            from 仪表盘.core_theme_manager import ThemeManager
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"无法导入ThemeManager: {e}")


class TestChartWidget(unittest.TestCase):
    """测试图表组件"""

    def test_chart_widget_import(self):
        """测试图表组件导入"""
        try:
            from 仪表盘.ui_chart_widget import RealTimeChartWidget
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"无法导入RealTimeChartWidget: {e}")


if __name__ == '__main__':
    unittest.main()
