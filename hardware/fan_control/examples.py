# -*- coding: utf-8 -*-
"""
风扇控制示例程序

演示如何使用风扇控制模块的各种功能
"""

import sys
import os
import time
import numpy as np

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from hardware.fan_control import (
    ModbusFanController,
    FanSpeedEncoder,
    FanConfig,
    PredefinedConfigs,
    PresetEncoders,
    quick_control_fan,
    quick_control_all_fans
)


def example_1_basic_control():
    """示例1: 基础风扇控制"""
    print("\n" + "="*60)
    print("示例1: 基础风扇控制")
    print("="*60)

    # 使用默认配置
    config = FanConfig(device_ip="192.168.2.1")

    with ModbusFanController(config) as controller:
        # 设置单个风扇
        controller.set_fan_speed(0, 50.0)  # 风扇1设置为50%
        time.sleep(1)

        # 设置所有风扇为75%
        controller.set_all_fans_speed(75.0)
        time.sleep(1)

        # 停止所有风扇
        controller.stop_all_fans()

    controller.print_statistics()


def example_2_individual_control():
    """示例2: 分别控制每个风扇"""
    print("\n" + "="*60)
    print("示例2: 分别控制每个风扇")
    print("="*60)

    config = FanConfig(device_ip="192.168.2.1", fan_count=16)

    with ModbusFanController(config) as controller:
        # 创建渐变速度模式
        speeds = [i * (100.0 / 15) for i in range(16)]  # 0%, 6.67%, ..., 100%

        # 分别设置每个风扇
        controller.set_fans_speed_individual(speeds)
        time.sleep(3)

        # 停止所有风扇
        controller.stop_all_fans()


def example_3_dict_control():
    """示例3: 使用字典控制特定风扇"""
    print("\n" + "="*60)
    print("示例3: 使用字典控制特定风扇")
    print("="*60)

    config = FanConfig(device_ip="192.168.2.1")

    with ModbusFanController(config) as controller:
        # 只控制部分风扇
        fan_dict = {
            0: 100.0,   # 风扇1: 100%
            5: 75.0,    # 风扇6: 75%
            10: 50.0,   # 风扇11: 50%
            15: 25.0,   # 风扇16: 25%
        }

        controller.set_fans_speed_dict(fan_dict)
        time.sleep(2)
        controller.stop_all_fans()


def example_4_quick_control():
    """示例4: 快速控制函数"""
    print("\n" + "="*60)
    print("示例4: 快速控制函数")
    print("="*60)

    # 快速设置所有风扇为50%
    quick_control_all_fans(50.0, device_ip="192.168.2.1")
    print("已设置所有风扇为50%")
    time.sleep(2)

    # 快速停止所有风扇
    quick_control_all_fans(0.0, device_ip="192.168.2.1")
    print("已停止所有风扇")


def example_5_wind_field_integration():
    """示例5: 风场数据集成"""
    print("\n" + "="*60)
    print("示例5: 风场数据集成")
    print("="*60)

    # 创建风场数据（40x40网格）
    grid_data = np.zeros((40, 40))

    # 生成简单的波纹图案
    for i in range(40):
        for j in range(40):
            grid_data[i, j] = 50 + 30 * np.sin(i / 5.0) * np.cos(j / 5.0)

    # 创建编码器（4x4风扇布局）
    encoder = PresetEncoders.STANDARD_4X4

    # 编码为风扇速度
    fan_speeds = encoder.encode_grid_to_fans(grid_data)

    print(f"编码后的风扇速度: {[f'{s:.1f}%' for s in fan_speeds]}")

    # 发送到控制器
    config = FanConfig(device_ip="192.168.2.1", fan_count=16)

    with ModbusFanController(config) as controller:
        controller.set_fans_speed_individual(fan_speeds)
        time.sleep(3)
        controller.stop_all_fans()


def example_6_pattern_generation():
    """示例6: 生成各种风扇模式"""
    print("\n" + "="*60)
    print("示例6: 生成各种风扇模式")
    print("="*60)

    encoder = PresetEncoders.STANDARD_4X4
    config = FanConfig(device_ip="192.168.2.1", fan_count=16)

    with ModbusFanController(config) as controller:
        # 1. 渐变模式
        print("\n1. 对角线渐变模式")
        speeds = encoder.create_gradient_pattern('diagonal', 0, 100)
        controller.set_fans_speed_individual(speeds)
        time.sleep(2)

        # 2. 径向模式
        print("\n2. 径向模式")
        speeds = encoder.create_radial_pattern(center_speed=100, edge_speed=0)
        controller.set_fans_speed_individual(speeds)
        time.sleep(2)

        # 3. 波浪模式
        print("\n3. 波浪模式（时间=0）")
        speeds = encoder.create_wave_pattern(time=0.0)
        controller.set_fans_speed_individual(speeds)
        time.sleep(2)

        print("\n4. 波浪模式（时间=1）")
        speeds = encoder.create_wave_pattern(time=1.0)
        controller.set_fans_speed_individual(speeds)
        time.sleep(2)

        controller.stop_all_fans()


def example_7_animation():
    """示例7: 风扇动画效果"""
    print("\n" + "="*60)
    print("示例7: 风扇动画效果")
    print("="*60)

    encoder = PresetEncoders.STANDARD_4X4
    config = FanConfig(device_ip="192.168.2.1", fan_count=16)

    with ModbusFanController(config) as controller:
        print("播放波浪动画（5秒）...")
        start_time = time.time()

        while time.time() - start_time < 5.0:
            current_time = time.time() - start_time
            speeds = encoder.create_wave_pattern(time=current_time * 2.0)
            controller.set_fans_speed_individual(speeds)
            time.sleep(0.2)  # 5fps

        controller.stop_all_fans()
        print("动画结束")


def example_8_error_handling():
    """示例8: 错误处理"""
    print("\n" + "="*60)
    print("示例8: 错误处理和重连")
    print("="*60)

    config = FanConfig(
        device_ip="192.168.2.1",
        timeout=2.0,
        reconnect_attempts=3
    )

    controller = ModbusFanController(config)

    # 尝试连接
    if controller.connect():
        try:
            # 尝试控制
            controller.set_all_fans_speed(50.0)
            time.sleep(1)

            # 尝试无效的风扇索引
            print("\n尝试设置无效的风扇索引...")
            controller.set_fan_speed(999, 50.0)  # 无效索引

        finally:
            controller.disconnect()
    else:
        print("连接失败，请检查设备")

    controller.print_statistics()


def example_9_custom_config():
    """示例9: 自定义配置"""
    print("\n" + "="*60)
    print("示例9: 自定义配置")
    print("="*60)

    # 创建自定义配置
    custom_config = FanConfig(
        device_ip="192.168.2.1",
        device_port=8234,
        slave_addr=1,
        fan_count=16,
        start_register=0,
        pwm_min=0,
        pwm_max=1000,
        timeout=5.0,
    )

    # 创建高响应编码器
    encoder = PresetEncoders.HIGH_RESPONSE_4X4

    # 生成测试数据
    test_grid = np.random.rand(40, 40) * 100

    # 编码
    fan_speeds = encoder.encode_grid_to_fans(test_grid)

    print(f"风扇数量: {custom_config.fan_count}")
    print(f"PWM范围: {custom_config.pwm_min}-{custom_config.pwm_max}")
    print(f"编码后的速度范围: {min(fan_speeds):.1f}% - {max(fan_speeds):.1f}%")


def example_10_batch_control():
    """示例10: 批量控制多个板子"""
    print("\n" + "="*60)
    print("示例10: 批量控制多个板子")
    print("="*60)

    # 定义多个板子
    boards = [
        FanConfig(device_ip="192.168.2.1", fan_count=16),
        FanConfig(device_ip="192.168.2.2", fan_count=16),
    ]

    target_speed = 75.0

    for i, config in enumerate(boards):
        print(f"\n控制板子 {i+1}: {config.device_ip}")
        with ModbusFanController(config) as controller:
            controller.set_all_fans_speed(target_speed)
            time.sleep(1)


def main():
    """主函数 - 运行所有示例"""
    examples = [
        ("基础风扇控制", example_1_basic_control),
        ("分别控制每个风扇", example_2_individual_control),
        ("使用字典控制特定风扇", example_3_dict_control),
        ("快速控制函数", example_4_quick_control),
        ("风场数据集成", example_5_wind_field_integration),
        ("生成各种风扇模式", example_6_pattern_generation),
        ("风扇动画效果", example_7_animation),
        ("错误处理和重连", example_8_error_handling),
        ("自定义配置", example_9_custom_config),
        ("批量控制多个板子", example_10_batch_control),
    ]

    print("\n" + "="*60)
    print("风扇控制示例程序")
    print("="*60)
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\n请选择要运行的示例（1-10），或输入0运行所有示例:")
    choice = input("> ")

    try:
        choice_num = int(choice)
        if choice_num == 0:
            # 运行所有示例
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ 示例 '{name}' 执行失败: {e}")
        elif 1 <= choice_num <= len(examples):
            # 运行选定的示例
            name, func = examples[choice_num - 1]
            func()
        else:
            print("❌ 无效的选择")
    except ValueError:
        print("❌ 请输入数字")


if __name__ == "__main__":
    main()
