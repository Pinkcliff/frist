# -*- coding: utf-8 -*-
"""
CFD前处理模块单元测试
测试计算域参数、风扇几何配置等
"""
import sys
import os
import unittest

# 添加项目路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class TestComputationalDomain(unittest.TestCase):
    """测试计算域参数"""

    @classmethod
    def setUpClass(cls):
        """在所有测试前调用update_domain_bounds"""
        from 前处理.CFD_module.pre_processor_config import update_domain_bounds
        update_domain_bounds()

    def test_margin_parameters(self):
        """测试边界参数"""
        from 前处理.CFD_module.pre_processor_config import (
            MARGIN_X, MARGIN_Y, INLET_LENGTH, OUTLET_LENGTH, IS_GROUNDED
        )

        # 验证边界参数值
        self.assertEqual(MARGIN_X, 200.0)  # mm
        self.assertEqual(MARGIN_Y, 200.0)  # mm
        self.assertEqual(INLET_LENGTH, 1.0)  # m
        self.assertEqual(OUTLET_LENGTH, 10.0)  # m
        self.assertFalse(IS_GROUNDED)

    def test_domain_bounds_calculation(self):
        """测试计算域边界计算"""
        from 前处理.CFD_module.pre_processor_config import (
            DOMAIN_BOUNDS, DOMAIN_BOUNDS_M,
            FAN_ARRAY_SHAPE, FAN_WIDTH, FAN_THICKNESS
        )

        # 验证DOMAIN_BOUNDS已填充（setUpClass已调用update_domain_bounds）
        self.assertIn('xmin', DOMAIN_BOUNDS)
        self.assertIn('xmax', DOMAIN_BOUNDS)
        self.assertIn('ymin', DOMAIN_BOUNDS)
        self.assertIn('ymax', DOMAIN_BOUNDS)
        self.assertIn('zmin', DOMAIN_BOUNDS)
        self.assertIn('zmax', DOMAIN_BOUNDS)

        # 验证DOMAIN_BOUNDS_M是毫米版本的1/1000
        for key in DOMAIN_BOUNDS:
            self.assertAlmostEqual(
                DOMAIN_BOUNDS_M[key],
                DOMAIN_BOUNDS[key] / 1000.0,
                places=5
            )

    def test_fan_wall_size_calculation(self):
        """测试风扇墙尺寸计算"""
        from 前处理.CFD_module.pre_processor_config import (
            DOMAIN_BOUNDS, FAN_ARRAY_SHAPE, FAN_WIDTH
        )

        # 计算预期值（setUpClass已调用update_domain_bounds）
        expected_x_size = FAN_ARRAY_SHAPE[1] * FAN_WIDTH  # 40 * 80 = 3200
        expected_y_size = FAN_ARRAY_SHAPE[0] * FAN_WIDTH  # 40 * 80 = 3200

        # 验证xmax和ymax
        expected_xmax = expected_x_size + 200  # MARGIN_X
        expected_ymax = expected_y_size + 200  # MARGIN_Y

        self.assertEqual(DOMAIN_BOUNDS['xmax'], expected_xmax)
        self.assertEqual(DOMAIN_BOUNDS['ymax'], expected_ymax)


class TestFanGeometry(unittest.TestCase):
    """测试风扇几何参数"""

    def test_fan_dimensions(self):
        """测试风扇尺寸参数"""
        from 前处理.CFD_module.pre_processor_config import (
            FAN_WIDTH, FAN_THICKNESS, FAN_HOLE_DIAMETER, FAN_HUB_DIAMETER
        )

        # 验证风扇几何参数（单位：mm）
        self.assertEqual(FAN_WIDTH, 80.0)
        self.assertEqual(FAN_THICKNESS, 80.0)
        self.assertEqual(FAN_HOLE_DIAMETER, 76.0)
        self.assertEqual(FAN_HUB_DIAMETER, 36.0)

        # 验证物理合理性：孔径应该小于风扇宽度
        self.assertLess(FAN_HOLE_DIAMETER, FAN_WIDTH)
        # 验证物理合理性：轮毂直径应该小于孔径
        self.assertLess(FAN_HUB_DIAMETER, FAN_HOLE_DIAMETER)

    def test_fan_array_shape(self):
        """测试风扇阵列形状"""
        from 前处理.CFD_module.pre_processor_config import FAN_ARRAY_SHAPE

        # 验证风扇阵列尺寸
        self.assertEqual(FAN_ARRAY_SHAPE, (40, 40))

    def test_fan_circle_segments(self):
        """测试风扇圆周分段数"""
        from 前处理.CFD_module.pre_processor_config import FAN_CIRCLE_SEGMENTS

        self.assertEqual(FAN_CIRCLE_SEGMENTS, 8)


class TestGridParameters(unittest.TestCase):
    """测试网格参数"""

    def test_component_grid_cells(self):
        """测试组件网格单元"""
        from 前处理.CFD_module.pre_processor_config import COMPONENT_GRID_CELLS

        self.assertEqual(COMPONENT_GRID_CELLS, (4, 4, 4))

    def test_environment_grid_size(self):
        """测试环境网格尺寸"""
        from 前处理.CFD_module.pre_processor_config import ENVIRONMENT_GRID_SIZE

        self.assertEqual(ENVIRONMENT_GRID_SIZE, (50.0, 50.0, 50.0))  # mm

    def test_stretch_ratios(self):
        """测试网格拉伸比"""
        from 前处理.CFD_module.pre_processor_config import (
            STRETCH_RATIO_Z, STRETCH_RATIO_XY
        )

        self.assertEqual(STRETCH_RATIO_Z, 1.05)
        self.assertEqual(STRETCH_RATIO_XY, 1.1)

        # 验证拉伸比大于1（表示拉伸）
        self.assertGreater(STRETCH_RATIO_Z, 1.0)
        self.assertGreater(STRETCH_RATIO_XY, 1.0)


class TestFanOperatingParameters(unittest.TestCase):
    """测试风扇运行参数"""

    def test_fan_rpm(self):
        """测试风扇转速"""
        from 前处理.CFD_module.pre_processor_config import (
            FAN_RPM_1, FAN_RPM_2
        )

        self.assertEqual(FAN_RPM_1, 17000)
        self.assertEqual(FAN_RPM_2, 14600)

    def test_fan_direction(self):
        """测试风扇方向"""
        from 前处理.CFD_module.pre_processor_config import (
            FAN_DIRECTION_1_IS_CW, FAN_DIRECTION_2_IS_CW
        )

        # 验证都是逆时针（False = CCW）
        self.assertFalse(FAN_DIRECTION_1_IS_CW)
        self.assertFalse(FAN_DIRECTION_2_IS_CW)

    def test_pq_curve_file(self):
        """测试PQ曲线文件"""
        from 前处理.CFD_module.pre_processor_config import DEFAULT_PQ_CURVE_FILE

        self.assertEqual(DEFAULT_PQ_CURVE_FILE, "fan_curve_14600.txt")


class TestPhysicalConstraints(unittest.TestCase):
    """测试物理约束和合理性检查"""

    def test_unit_consistency(self):
        """测试单位一致性"""
        from 前处理.CFD_module.pre_processor_config import (
            MARGIN_X, MARGIN_Y, INLET_LENGTH, OUTLET_LENGTH,
            FAN_WIDTH, FAN_THICKNESS
        )

        # MARGIN_X和MARGIN_Y应该是mm
        # INLET_LENGTH和OUTLET_LENGTH应该是m
        # FAN_WIDTH和FAN_THICKNESS应该是mm

        # 验证数量级合理性
        self.assertLess(MARGIN_X, 1000)  # 应该小于1000mm
        self.assertGreater(INLET_LENGTH, 0)  # 应该大于0
        self.assertGreater(OUTLET_LENGTH, INLET_LENGTH)  # 出口应该比入口长

    def test_domain_bounds_when_grounded(self):
        """测试接地状态下的边界"""
        from 前处理.CFD_module.pre_processor_config import (
            update_domain_bounds, DOMAIN_BOUNDS, IS_GROUNDED
        )

        # 测试非接地状态
        original_grounded = IS_GROUNDED
        update_domain_bounds()
        ymin_ungrounded = DOMAIN_BOUNDS['ymin']
        self.assertLess(ymin_ungrounded, 0)  # 应该为负值


if __name__ == '__main__':
    unittest.main()
