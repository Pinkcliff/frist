# -*- coding: utf-8 -*-
"""
风扇控制日志演示

演示如何使用日志功能记录风扇控制过程
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
    FanConfig,
    FanSpeedEncoder,
    PresetEncoders,
    setup_fan_logger,
)


def demo_basic_logging():
    """演示基础日志功能"""
    print("\n" + "="*80)
    print("演示1: 基础日志 - 单风扇控制")
    print("="*80)

    # 创建配置
    config = FanConfig(device_ip="192.168.2.1", fan_count=16)

    # 创建控制器（启用日志）
    controller = ModbusFanController(config, enable_logging=True)

    # 连接
    if controller.connect():
        try:
            # 设置单个风扇
            print("\n设置风扇1为50%...")
            controller.set_fan_speed(0, 50.0)
            time.sleep(1)

            # 设置风扇2为75%
            print("\n设置风扇2为75%...")
            controller.set_fan_speed(1, 75.0)
            time.sleep(1)

            # 停止风扇1
            print("\n停止风扇1...")
            controller.set_fan_speed(0, 0.0)

        finally:
            controller.disconnect()
            controller.print_statistics()

    print("\n日志文件已保存到: hardware/fan_control/logs/")
    print("请查看最新的.log文件")


def demo_all_fans_logging():
    """演示所有风扇控制日志"""
    print("\n" + "="*80)
    print("演示2: 所有风扇控制日志")
    print("="*80)

    config = FanConfig(device_ip="192.168.2.1", fan_count=16)
    controller = ModbusFanController(config, enable_logging=True)

    if controller.connect():
        try:
            # 设置所有风扇为50%
            print("\n设置所有风扇为50%...")
            controller.set_all_fans_speed(50.0)
            time.sleep(2)

            # 设置所有风扇为75%
            print("\n设置所有风扇为75%...")
            controller.set_all_fans_speed(75.0)
            time.sleep(2)

            # 停止所有风扇
            print("\n停止所有风扇...")
            controller.stop_all_fans()

        finally:
            controller.disconnect()

    print("\n日志文件中记录了每个风扇的详细信息")


def demo_individual_logging():
    """演示分别设置风扇的日志"""
    print("\n" + "="*80)
    print("演示3: 分别设置风扇日志")
    print("="*80)

    config = FanConfig(device_ip="192.168.2.1", fan_count=16)
    controller = ModbusFanController(config, enable_logging=True)

    if controller.connect():
        try:
            # 创建渐变速度列表
            speeds = [i * (100.0 / 15) for i in range(16)]

            print("\n应用渐变速度模式...")
            controller.set_fans_speed_individual(speeds)
            time.sleep(3)

            # 创建波浪模式
            print("\n应用波浪模式...")
            speeds = [50 + 30 * np.sin(i * 0.5) for i in range(16)]
            controller.set_fans_speed_individual(speeds)
            time.sleep(3)

            # 停止所有风扇
            controller.stop_all_fans()

        finally:
            controller.disconnect()

    print("\n日志文件中记录了每个风扇的独立速度设置")


def demo_wind_field_logging():
    """演示风场数据集成日志"""
    print("\n" + "="*80)
    print("演示4: 风场数据集成日志")
    print("="*80)

    config = FanConfig(device_ip="192.168.2.1", fan_count=16)
    controller = ModbusFanController(config, enable_logging=True)

    # 创建编码器
    encoder = PresetEncoders.STANDARD_4X4

    if controller.connect():
        try:
            # 创建风场数据
            grid_data = np.zeros((40, 40))
            for i in range(40):
                for j in range(40):
                    grid_data[i, j] = 50 + 30 * np.sin(i / 5.0) * np.cos(j / 5.0)

            # 编码为风扇速度
            fan_speeds = encoder.encode_grid_to_fans(grid_data)

            print("\n应用风场数据到风扇...")
            print("编码后的速度:", [f"{s:.1f}%" for s in fan_speeds])
            controller.set_fans_speed_individual(fan_speeds)
            time.sleep(3)

            # 停止所有风扇
            controller.stop_all_fans()

        finally:
            controller.disconnect()

    print("\n日志文件中记录了风场数据的详细编码过程")


def demo_pattern_logging():
    """演示模式生成日志"""
    print("\n" + "="*80)
    print("演示5: 模式生成日志")
    print("="*80)

    config = FanConfig(device_ip="192.168.2.1", fan_count=16)
    controller = ModbusFanController(config, enable_logging=True)
    encoder = PresetEncoders.STANDARD_4X4

    if controller.connect():
        try:
            # 渐变模式
            print("\n1. 对角线渐变模式")
            speeds = encoder.create_gradient_pattern('diagonal', 0, 100)
            controller.set_fans_speed_individual(speeds)
            time.sleep(2)

            # 径向模式
            print("\n2. 径向模式")
            speeds = encoder.create_radial_pattern(center_speed=100, edge_speed=0)
            controller.set_fans_speed_individual(speeds)
            time.sleep(2)

            # 停止所有风扇
            controller.stop_all_fans()

        finally:
            controller.disconnect()

    print("\n日志文件中记录了各种模式的生成和应用过程")


def demo_animation_logging():
    """演示动画日志"""
    print("\n" + "="*80)
    print("演示6: 动画日志")
    print("="*80)

    config = FanConfig(device_ip="192.168.2.1", fan_count=16)
    controller = ModbusFanController(config, enable_logging=True)
    encoder = PresetEncoders.STANDARD_4X4

    if controller.connect():
        try:
            print("\n播放波浪动画（5秒）...")
            start_time = time.time()

            while time.time() - start_time < 5.0:
                current_time = time.time() - start_time
                speeds = encoder.create_wave_pattern(time=current_time * 2.0)
                controller.set_fans_speed_individual(speeds)
                time.sleep(0.5)  # 2fps，减少日志量

            # 停止所有风扇
            controller.stop_all_fans()

        finally:
            controller.disconnect()

    print("\n日志文件中记录了动画的每一帧")


def demo_custom_log_file():
    """演示自定义日志文件"""
    print("\n" + "="*80)
    print("演示7: 自定义日志文件")
    print("="*80)

    # 创建自定义日志文件
    log_file = os.path.join(
        os.path.dirname(__file__),
        'logs',
        'custom_fan_control.log'
    )

    # 设置自定义日志记录器
    logger = setup_fan_logger(log_file)
    print(f"\n自定义日志文件: {log_file}")

    # 记录一些信息
    logger.info("这是一个自定义日志文件")
    logger.info("记录风扇控制过程")

    # 使用自定义日志的控制器
    config = FanConfig(device_ip="192.168.2.1", fan_count=16)
    controller = ModbusFanController(config, enable_logging=True)

    if controller.connect():
        try:
            controller.set_all_fans_speed(50.0)
            time.sleep(1)
            controller.stop_all_fans()
        finally:
            controller.disconnect()

    print(f"\n请查看自定义日志文件: {log_file}")


def show_log_files():
    """显示日志文件列表"""
    import glob

    log_dir = os.path.join(os.path.dirname(__file__), 'logs')

    if os.path.exists(log_dir):
        log_files = glob.glob(os.path.join(log_dir, '*.log'))

        if log_files:
            print("\n" + "="*80)
            print("可用的日志文件:")
            print("="*80)

            # 按时间排序
            log_files.sort(key=os.path.getmtime, reverse=True)

            for i, log_file in enumerate(log_files[:10], 1):  # 只显示最近10个
                file_name = os.path.basename(log_file)
                file_size = os.path.getsize(log_file)
                mtime = os.path.getmtime(log_file)
                mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                print(f"{i}. {file_name}")
                print(f"   大小: {file_size:,} 字节")
                print(f"   时间: {mtime_str}")
                print()
        else:
            print("\n没有找到日志文件")
    else:
        print("\n日志文件夹不存在")


def view_latest_log():
    """查看最新的日志文件"""
    import glob

    log_dir = os.path.join(os.path.dirname(__file__), 'logs')

    if os.path.exists(log_dir):
        log_files = glob.glob(os.path.join(log_dir, '*.log'))

        if log_files:
            # 找到最新的日志文件
            latest_log = max(log_files, key=os.path.getmtime)

            print("\n" + "="*80)
            print(f"最新日志文件内容: {os.path.basename(latest_log)}")
            print("="*80)

            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 显示最后50行
            if len(lines) > 50:
                print(f"\n... (共{len(lines)}行，显示最后50行) ...\n")
                display_lines = lines[-50:]
            else:
                display_lines = lines

            for line in display_lines:
                print(line.rstrip())

        else:
            print("\n没有找到日志文件")
    else:
        print("\n日志文件夹不存在")


def main():
    """主函数"""
    demos = [
        ("基础日志 - 单风扇控制", demo_basic_logging),
        ("所有风扇控制日志", demo_all_fans_logging),
        ("分别设置风扇日志", demo_individual_logging),
        ("风场数据集成日志", demo_wind_field_logging),
        ("模式生成日志", demo_pattern_logging),
        ("动画日志", demo_animation_logging),
        ("自定义日志文件", demo_custom_log_file),
    ]

    print("\n" + "="*80)
    print("风扇控制日志演示程序")
    print("="*80)
    print("\n所有控制操作都会被记录到日志文件中")
    print("日志文件位置: hardware/fan_control/logs/")
    print("\n可用演示:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print(f"{len(demos)+1}. 查看所有日志文件")
    print(f"{len(demos)+2}. 查看最新日志内容")
    print(f"0. 运行所有演示")

    print("\n请选择要运行的演示:")
    choice = input("> ")

    try:
        choice_num = int(choice)
        if choice_num == 0:
            # 运行所有演示
            for name, func in demos:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ 演示 '{name}' 执行失败: {e}")
            # 显示日志文件
            show_log_files()
        elif 1 <= choice_num <= len(demos):
            # 运行选定的演示
            name, func = demos[choice_num - 1]
            func()
        elif choice_num == len(demos) + 1:
            # 显示日志文件
            show_log_files()
        elif choice_num == len(demos) + 2:
            # 查看最新日志
            view_latest_log()
        else:
            print("❌ 无效的选择")
    except ValueError:
        print("❌ 请输入数字")

    # 显示日志文件列表
    if choice_num in [0, len(demos) + 1]:
        show_log_files()


if __name__ == "__main__":
    main()
