# -*- coding: utf-8 -*-
"""
风场设置模块单元测试
测试配置参数和颜色映射
"""
import sys
import os
import unittest

# 添加项目路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class TestWindConfigParameters(unittest.TestCase):
    """测试风场配置参数"""

    def test_grid_dimensions(self):
        """测试网格尺寸参数"""
        from 风场设置.main_control.config import (
            GRID_DIM, MODULE_DIM, CELL_SIZE, CELL_SPACING,
            TOTAL_CELL_SIZE, CANVAS_WIDTH, CANVAS_HEIGHT
        )

        # 验证网格维度
        self.assertEqual(GRID_DIM, 40)
        self.assertEqual(MODULE_DIM, 4)
        self.assertEqual(CELL_SIZE, 16)
        self.assertEqual(CELL_SPACING, 2)
        self.assertEqual(TOTAL_CELL_SIZE, 18)

        # 验证画布尺寸计算
        expected_canvas_size = GRID_DIM * TOTAL_CELL_SIZE  # 40 * 18 = 720
        self.assertEqual(CANVAS_WIDTH, expected_canvas_size)
        self.assertEqual(CANVAS_HEIGHT, expected_canvas_size)

    def test_app_info(self):
        """测试应用信息"""
        from 风场设置.main_control.config import APP_NAME, APP_VERSION

        self.assertEqual(APP_NAME, "风墙设置 (Wind Wall Settings)")
        self.assertIn("0.6", APP_VERSION)
        self.assertIn("Color Consistency", APP_VERSION)


class TestColorMap(unittest.TestCase):
    """测试颜色映射"""

    def test_color_map_import(self):
        """测试颜色映射导入"""
        from 风场设置.main_control.config import COLOR_MAP

        # 验证颜色映射长度为256
        self.assertEqual(len(COLOR_MAP), 256)

    def test_color_map_gradient(self):
        """测试颜色梯度"""
        from 风场设置.main_control.config import COLOR_MAP, lerp_color
        from PySide6.QtGui import QColor

        # 验证颜色映射包含有效的QColor对象
        for color in COLOR_MAP:
            self.assertIsInstance(color, QColor)
            # 验证颜色值在有效范围内
            self.assertGreaterEqual(color.red(), 0)
            self.assertLessEqual(color.red(), 255)
            self.assertGreaterEqual(color.green(), 0)
            self.assertLessEqual(color.green(), 255)
            self.assertGreaterEqual(color.blue(), 0)
            self.assertLessEqual(color.blue(), 255)

    def test_lerp_color_function(self):
        """测试颜色插值函数"""
        from 风场设置.main_control.config import lerp_color
        from PySide6.QtGui import QColor

        c1 = QColor(0, 0, 0)
        c2 = QColor(255, 255, 255)

        # 测试t=0（起始颜色）
        result_start = lerp_color(c1, c2, 0)
        self.assertEqual(result_start.red(), 0)
        self.assertEqual(result_start.green(), 0)
        self.assertEqual(result_start.blue(), 0)

        # 测试t=1（结束颜色）
        result_end = lerp_color(c1, c2, 1)
        self.assertEqual(result_end.red(), 255)
        self.assertEqual(result_end.green(), 255)
        self.assertEqual(result_end.blue(), 255)

        # 测试t=0.5（中间颜色）
        result_mid = lerp_color(c1, c2, 0.5)
        self.assertEqual(result_mid.red(), 127)
        self.assertEqual(result_mid.green(), 127)
        self.assertEqual(result_mid.blue(), 127)


class TestColorDistribution(unittest.TestCase):
    """测试颜色分布"""

    def test_blue_to_green_transition(self):
        """测试蓝色到绿色过渡"""
        from 风场设置.main_control.config import COLOR_MAP

        # 索引0-84（33%）应该是蓝到绿过渡
        first_color = COLOR_MAP[0]
        transition_color = COLOR_MAP[80]

        # 验证起始颜色偏蓝
        self.assertGreater(first_color.blue(), first_color.green())

    def test_green_to_yellow_transition(self):
        """测试绿色到黄色过渡"""
        from 风场设置.main_control.config import COLOR_MAP

        # 索引85-169（33%）应该是绿到黄过渡
        mid_color = COLOR_MAP[128]

        # 验证中间颜色包含绿色和黄色成分
        self.assertGreater(mid_color.green(), 100)

    def test_yellow_to_red_transition(self):
        """测试黄色到红色过渡"""
        from 风场设置.main_control.config import COLOR_MAP

        # 索引170-255（34%）应该是黄到红过渡
        end_color = COLOR_MAP[255]

        # 验证结束颜色偏红
        self.assertEqual(end_color.red(), 255)


if __name__ == '__main__':
    unittest.main()
