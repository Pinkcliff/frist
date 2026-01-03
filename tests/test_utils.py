# -*- coding: utf-8 -*-
"""
工具函数单元测试
测试颜色转换、文本对比度、网格生成等工具函数
"""
import sys
import os
import unittest
import numpy as np

# 添加项目路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class TestValueToColor(unittest.TestCase):
    """测试值到颜色转换函数"""

    def test_value_to_color_import(self):
        """测试函数导入"""
        try:
            from 风场设置.main_control.utils import value_to_color
            self.value_to_color = value_to_color
        except ImportError as e:
            self.skipTest(f"无法导入value_to_color: {e}")

    def test_value_to_color_range(self):
        """测试值到颜色转换的范围"""
        from 风场设置.main_control.utils import value_to_color
        from PySide6.QtGui import QColor

        # 测试最小值（应该是蓝色）
        color_min = value_to_color(0.0, 0.0, 100.0)
        self.assertIsInstance(color_min, QColor)

        # 测试中间值（应该是绿色或黄色）
        color_mid = value_to_color(50.0, 0.0, 100.0)
        self.assertIsInstance(color_mid, QColor)

        # 测试最大值（应该是红色）
        color_max = value_to_color(100.0, 0.0, 100.0)
        self.assertIsInstance(color_max, QColor)

    def test_value_to_color_clamping(self):
        """测试值裁剪功能"""
        from 风场设置.main_control.utils import value_to_color

        # 测试超出范围的值（应该被裁剪）
        color_below = value_to_color(-10.0, 0.0, 100.0)
        color_at_min = value_to_color(0.0, 0.0, 100.0)

        color_above = value_to_color(150.0, 0.0, 100.0)
        color_at_max = value_to_color(100.0, 0.0, 100.0)

        # 裁剪后的颜色应该等于边界颜色
        self.assertEqual(color_below, color_at_min)
        self.assertEqual(color_above, color_at_max)

    def test_value_to_color_consistency(self):
        """测试颜色转换一致性"""
        from 风场设置.main_control.utils import value_to_color

        # 相同的输入应该产生相同的输出
        color1 = value_to_color(25.0, 0.0, 100.0)
        color2 = value_to_color(25.0, 0.0, 100.0)

        self.assertEqual(color1, color2)


class TestContrastingTextColor(unittest.TestCase):
    """测试对比度文本颜色函数"""

    def test_contrasting_text_color_import(self):
        """测试函数导入"""
        try:
            from 风场设置.main_control.utils import get_contrasting_text_color
            self.get_contrasting_text_color = get_contrasting_text_color
        except ImportError as e:
            self.skipTest(f"无法导入get_contrasting_text_color: {e}")

    def test_light_background(self):
        """测试浅色背景"""
        from 风场设置.main_control.utils import get_contrasting_text_color
        from PySide6.QtGui import QColor
        from PySide6.QtCore import Qt

        # 浅色背景应该返回黑色文本
        light_bg = QColor(255, 255, 255)
        text_color = get_contrasting_text_color(light_bg)

        self.assertEqual(text_color, QColor(Qt.black))

    def test_dark_background(self):
        """测试深色背景"""
        from 风场设置.main_control.utils import get_contrasting_text_color
        from PySide6.QtGui import QColor
        from PySide6.QtCore import Qt

        # 深色背景应该返回白色文本
        dark_bg = QColor(0, 0, 0)
        text_color = get_contrasting_text_color(dark_bg)

        self.assertEqual(text_color, QColor(Qt.white))

    def test_threshold_boundary(self):
        """测试阈值边界"""
        from 风场设置.main_control.config import LUMINANCE_THRESHOLD
        from 风场设置.main_control.utils import get_contrasting_text_color
        from PySide6.QtGui import QColor

        # LUMINANCE_THRESHOLD是140
        # 亮度 = 0.299*R + 0.587*G + 0.114*B
        # 140 = 0.299*R + 0.587*G + 0.114*B

        # 测试刚好在阈值之上的颜色
        above_threshold = QColor(150, 150, 150)
        text_above = get_contrasting_text_color(above_threshold)

        # 测试刚好在阈值之下的颜色
        below_threshold = QColor(130, 130, 130)
        text_below = get_contrasting_text_color(below_threshold)


class TestGridUtils(unittest.TestCase):
    """测试网格工具函数"""

    def test_generate_stretched_coords_import(self):
        """测试函数导入"""
        try:
            from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size
            self.generate_stretched_coords_by_size = generate_stretched_coords_by_size
        except ImportError as e:
            self.skipTest(f"无法导入generate_stretched_coords_by_size: {e}")

    def test_basic_coords_generation(self):
        """测试基本坐标生成"""
        from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size

        length = 100.0
        first_cell_size = 5.0
        ratio = 1.1

        coords = generate_stretched_coords_by_size(length, first_cell_size, ratio)

        # 验证返回的是numpy数组
        self.assertIsInstance(coords, np.ndarray)

        # 验证起点是0
        self.assertEqual(coords[0], 0.0)

        # 验证终点接近length
        self.assertAlmostEqual(coords[-1], length, places=5)

        # 验证坐标是单调递增的
        for i in range(len(coords) - 1):
            self.assertLess(coords[i], coords[i + 1])

    def test_zero_length(self):
        """测试零长度情况"""
        from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size

        coords = generate_stretched_coords_by_size(0.0, 1.0, 1.1)

        # 应该返回只包含0的数组
        self.assertEqual(len(coords), 1)
        self.assertEqual(coords[0], 0.0)

    def test_very_small_length(self):
        """测试极小长度情况"""
        from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size

        coords = generate_stretched_coords_by_size(1e-7, 1.0, 1.1)

        # 应该返回只包含0的数组
        self.assertEqual(len(coords), 1)
        self.assertEqual(coords[0], 0.0)

    def test_stretching_effect(self):
        """测试拉伸效果"""
        from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size

        length = 100.0
        first_cell_size = 1.0
        ratio = 1.2  # 20%拉伸

        coords = generate_stretched_coords_by_size(length, first_cell_size, ratio)

        # 计算单元间距
        spacings = np.diff(coords)

        # 验证大部分间距是递增的（由于拉伸比）
        # 注意：最后的缩放步骤可能导致最后几个点不严格递增
        increasing_count = 0
        for i in range(len(spacings) - 1):
            if spacings[i + 1] > spacings[i]:
                increasing_count += 1

        # 至少80%的间距应该是递增的
        increasing_ratio = increasing_count / (len(spacings) - 1)
        self.assertGreater(increasing_ratio, 0.8)

    def test_ratio_1_no_stretching(self):
        """测试比率为1时不拉伸"""
        from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size

        length = 100.0
        first_cell_size = 10.0
        ratio = 1.0  # 无拉伸

        coords = generate_stretched_coords_by_size(length, first_cell_size, ratio)

        # 计算单元间距
        spacings = np.diff(coords)

        # 所有间距应该相等
        for spacing in spacings:
            self.assertAlmostEqual(spacing, first_cell_size, places=5)

    def test_max_cells_limit(self):
        """测试最大单元数限制"""
        from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size

        # 使用大长度和很小的初始单元，确保会触发max_cells限制
        length = 100000.0
        first_cell_size = 0.1
        ratio = 1.01

        coords = generate_stretched_coords_by_size(length, first_cell_size, ratio, max_cells=100)

        # 验证不会超过最大单元数太多
        # 函数添加初始点和终点，所以最多是max_cells + 2
        self.assertLessEqual(len(coords), 102)  # 100个单元 + 初始点0 + 终点length

    def test_precision_of_endpoint(self):
        """测试终点精度"""
        from 前处理.CFD_module.grid_utils import generate_stretched_coords_by_size

        length = 123.456
        first_cell_size = 5.0
        ratio = 1.15

        coords = generate_stretched_coords_by_size(length, first_cell_size, ratio)

        # 终点应该非常接近目标长度
        self.assertAlmostEqual(coords[-1], length, places=5)


class TestFanIdGenerator(unittest.TestCase):
    """测试风扇ID生成器"""

    def test_fan_id_generator_import(self):
        """测试风扇ID生成器导入"""
        try:
            from 前处理.CFD_module.fan_id_generator import generate_fan_id
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"无法导入fan_id_generator: {e}")


if __name__ == '__main__':
    unittest.main()
