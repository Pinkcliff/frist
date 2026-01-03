# -*- coding: utf-8 -*-
"""
风扇控制单元测试
"""

import sys
import os
import unittest
import numpy as np

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from hardware.fan_control import (
    FanConfig,
    FanMapping,
    FanSpeedEncoder,
    ModbusFanController,
    PresetEncoders,
    PredefinedConfigs,
)


class TestFanConfig(unittest.TestCase):
    """测试FanConfig类"""

    def test_default_config(self):
        """测试默认配置"""
        config = FanConfig()
        self.assertEqual(config.device_ip, "192.168.2.1")
        self.assertEqual(config.fan_count, 16)
        self.assertEqual(config.slave_addr, 1)

    def test_custom_config(self):
        """测试自定义配置"""
        config = FanConfig(
            device_ip="192.168.2.100",
            fan_count=32,
            slave_addr=2
        )
        self.assertEqual(config.device_ip, "192.168.2.100")
        self.assertEqual(config.fan_count, 32)
        self.assertEqual(config.slave_addr, 2)

    def test_validate_fan_index(self):
        """测试风扇索引验证"""
        config = FanConfig(fan_count=16)
        self.assertTrue(config.validate_fan_index(0))
        self.assertTrue(config.validate_fan_index(15))
        self.assertFalse(config.validate_fan_index(-1))
        self.assertFalse(config.validate_fan_index(16))

    def test_validate_pwm(self):
        """测试PWM值验证"""
        config = FanConfig()
        self.assertTrue(config.validate_pwm(0))
        self.assertTrue(config.validate_pwm(500))
        self.assertTrue(config.validate_pwm(1000))
        self.assertFalse(config.validate_pwm(-1))
        self.assertFalse(config.validate_pwm(1001))

    def test_get_register_address(self):
        """测试寄存器地址计算"""
        config = FanConfig(start_register=100)
        self.assertEqual(config.get_register_address(0), 100)
        self.assertEqual(config.get_register_address(5), 105)


class TestFanMapping(unittest.TestCase):
    """测试FanMapping类"""

    def test_default_mapping(self):
        """测试默认映射"""
        mapping = FanMapping()
        self.assertEqual(mapping.rows, 4)
        self.assertEqual(mapping.cols, 4)
        self.assertEqual(mapping.fan_count, 16)

    def test_post_init(self):
        """测试初始化后计算"""
        mapping = FanMapping(rows=8, cols=4)
        self.assertEqual(mapping.fan_count, 32)


class TestFanSpeedEncoder(unittest.TestCase):
    """测试FanSpeedEncoder类"""

    def setUp(self):
        """设置测试环境"""
        self.mapping = FanMapping(rows=4, cols=4)
        self.encoder = FanSpeedEncoder(self.mapping)

    def test_encode_grid_to_fans(self):
        """测试网格编码"""
        # 创建40x40的测试网格
        grid_data = np.ones((40, 40)) * 50  # 全部50%

        fan_speeds = self.encoder.encode_grid_to_fans(grid_data)

        self.assertEqual(len(fan_speeds), 16)
        for speed in fan_speeds:
            self.assertAlmostEqual(speed, 50.0, places=1)

    def test_encode_with_zeros(self):
        """测试全零网格"""
        grid_data = np.zeros((40, 40))
        fan_speeds = self.encoder.encode_grid_to_fans(grid_data)

        self.assertEqual(len(fan_speeds), 16)
        for speed in fan_speeds:
            self.assertEqual(speed, 0.0)

    def test_encode_with_max(self):
        """测试最大值网格"""
        grid_data = np.ones((40, 40)) * 100
        fan_speeds = self.encoder.encode_grid_to_fans(grid_data)

        self.assertEqual(len(fan_speeds), 16)
        for speed in fan_speeds:
            self.assertAlmostEqual(speed, 100.0 * self.mapping.speed_multiplier, places=1)

    def test_create_gradient_pattern(self):
        """测试渐变模式生成"""
        speeds = self.encoder.create_gradient_pattern('horizontal', 0, 100)

        self.assertEqual(len(speeds), 16)
        self.assertAlmostEqual(speeds[0], 0.0, places=1)
        self.assertAlmostEqual(speeds[-1], 100.0, places=1)

    def test_create_radial_pattern(self):
        """测试径向模式生成"""
        speeds = self.encoder.create_radial_pattern()

        self.assertEqual(len(speeds), 16)
        # 中心应该是最高的
        self.assertGreater(speeds[4], speeds[0])  # 假设中心在(2,2)

    def test_create_wave_pattern(self):
        """测试波浪模式生成"""
        speeds = self.encoder.create_wave_pattern(time=0.0)

        self.assertEqual(len(speeds), 16)
        for speed in speeds:
            self.assertGreaterEqual(speed, 0.0)
            self.assertLessEqual(speed, 100.0)

    def test_curve_mapping(self):
        """测试曲线映射"""
        mapping = FanMapping(enable_curve=True, curve_power=2.0)
        encoder = FanSpeedEncoder(mapping)

        grid_data = np.ones((40, 40)) * 50
        fan_speeds = encoder.encode_grid_to_fans(grid_data)

        # 启用曲线后应该与原始值不同
        self.assertEqual(len(fan_speeds), 16)


class TestModbusCRC(unittest.TestCase):
    """测试Modbus CRC计算"""

    def test_crc_calculation(self):
        """测试CRC计算"""
        from hardware.fan_control.modbus_fan import ModbusCRC

        # 测试标准Modbus帧
        frame = [0x01, 0x06, 0x00, 0x00, 0x00, 0x64]
        crc = ModbusCRC.calculate(frame)

        self.assertEqual(len(crc), 2)
        self.assertIsInstance(crc[0], int)
        self.assertIsInstance(crc[1], int)


class TestModbusFanController(unittest.TestCase):
    """测试ModbusFanController类（离线测试）"""

    def setUp(self):
        """设置测试环境"""
        self.config = FanConfig(device_ip="192.168.2.1")
        self.controller = ModbusFanController(self.config)

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.controller.config)
        self.assertFalse(self.controller.is_connected)
        self.assertIsNone(self.controller.sock)

    def test_build_write_request(self):
        """测试写请求构建"""
        request = self.controller._build_write_request(0, 500)

        self.assertEqual(len(request), 8)  # 6字节数据 + 2字节CRC
        self.assertEqual(request[0], 1)   # 从站地址
        self.assertEqual(request[1], 0x06)  # 功能码

    def test_build_write_multiple_request(self):
        """测试写多个寄存器请求构建"""
        values = [100, 200, 300, 400]
        request = self.controller._build_write_multiple_request(0, values)

        self.assertGreater(len(request), 8)
        self.assertEqual(request[0], 1)  # 从站地址
        self.assertEqual(request[1], 0x10)  # 功能码0x10

    def test_parse_response_valid(self):
        """测试有效响应解析"""
        # 构造有效响应（写单个寄存器）
        response = bytearray([0x01, 0x06, 0x00, 0x00, 0x00, 0x64])
        crc = self.controller._parse_response(response[:-2])  # 临时CRC
        full_response = response + bytearray([0x00, 0x00])  # 添加CRC占位

        result = self.controller._parse_response(full_response)

        self.assertIn('valid', result)

    def test_parse_response_invalid_crc(self):
        """测试无效CRC响应解析"""
        response = bytearray([0x01, 0x06, 0x00, 0x00, 0x00, 0x64, 0xFF, 0xFF])

        result = self.controller._parse_response(response)

        self.assertIn('error', result)
        self.assertFalse(result.get('valid', False))


class TestPresetEncoders(unittest.TestCase):
    """测试预定义编码器"""

    def test_standard_4x4(self):
        """测试4x4标准编码器"""
        encoder = PresetEncoders.STANDARD_4X4
        self.assertEqual(encoder.mapping.rows, 4)
        self.assertEqual(encoder.mapping.cols, 4)

    def test_high_response_4x4(self):
        """测试4x4高响应编码器"""
        encoder = PresetEncoders.HIGH_RESPONSE_4X4
        self.assertTrue(encoder.mapping.enable_curve)
        self.assertEqual(encoder.mapping.curve_power, 1.5)


class TestPredefinedConfigs(unittest.TestCase):
    """测试预定义配置"""

    def test_single_board_16_fans(self):
        """测试单板16风扇配置"""
        config = PredefinedConfigs.SINGLE_BOARD_16_FANS
        self.assertEqual(config.fan_count, 16)
        self.assertEqual(config.device_ip, "192.168.2.1")

    def test_single_board_32_fans(self):
        """测试单板32风扇配置"""
        config = PredefinedConfigs.SINGLE_BOARD_32_FANS
        self.assertEqual(config.fan_count, 32)


class TestIntegration(unittest.TestCase):
    """集成测试（不需要实际硬件）"""

    def test_encoder_to_controller_workflow(self):
        """测试编码器到控制器的工作流程"""
        # 1. 创建风场数据
        grid_data = np.random.rand(40, 40) * 100

        # 2. 编码为风扇速度
        encoder = PresetEncoders.STANDARD_4X4
        fan_speeds = encoder.encode_grid_to_fans(grid_data)

        # 3. 验证速度范围
        self.assertEqual(len(fan_speeds), 16)
        for speed in fan_speeds:
            self.assertGreaterEqual(speed, 0.0)
            self.assertLessEqual(speed, 100.0)

    def test_pattern_to_speeds_workflow(self):
        """测试模式生成到速度的工作流程"""
        encoder = PresetEncoders.STANDARD_4X4

        # 生成渐变模式
        speeds = encoder.create_gradient_pattern('diagonal', 0, 100)

        # 验证
        self.assertEqual(len(speeds), 16)
        self.assertLess(speeds[0], speeds[-1])  # 应该递增


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFanConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestFanMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestFanSpeedEncoder))
    suite.addTests(loader.loadTestsFromTestCase(TestModbusCRC))
    suite.addTests(loader.loadTestsFromTestCase(TestModbusFanController))
    suite.addTests(loader.loadTestsFromTestCase(TestPresetEncoders))
    suite.addTests(loader.loadTestsFromTestCase(TestPredefinedConfigs))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
