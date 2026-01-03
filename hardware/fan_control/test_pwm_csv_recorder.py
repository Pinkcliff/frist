# -*- coding: utf-8 -*-
"""
PWM CSV记录器测试脚本

演示如何使用PWMCSVRecorder记录1600个风扇的PWM值到CSV文件
"""

import sys
import os
import time
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from hardware.fan_control.pwm_csv_recorder import (
    PWMCSVRecorder,
    PWMRecorderWithController,
    create_demo_csv_recording
)


def test_basic_recording():
    """测试基础记录功能"""
    print("\n" + "="*80)
    print("测试1: 基础PWM值记录")
    print("="*80)

    # 创建记录器（为了快速演示，使用10个板子）
    print("\n创建PWM记录器...")
    recorder = PWMCSVRecorder(
        board_count=10,  # 10个板子（演示用）
        fans_per_board=16,
        interval=0.1  # 每0.1秒记录一次
    )

    print(f"CSV文件: {recorder.csv_file}")
    print(f"总风扇数: {recorder.total_fans}")

    # 开始记录
    recorder.start_recording()

    # 模拟5秒的数据
    print("\n生成模拟数据（5秒）...")
    for i in range(50):  # 5秒 / 0.1秒 = 50次
        # 生成渐变PWM值
        pwm_values = []
        for board_idx in range(10):
            offset = (i + board_idx * 5) % 1000
            for fan_idx in range(16):
                pwm = (fan_idx * (1000 / 15) + offset) % 1000
                pwm_values.append(int(pwm))

        recorder.set_pwm_values(pwm_values)

        if i % 10 == 0:
            print(f"  进度: {(i/50)*100:.0f}% - 已记录{recorder.record_count}行")

        time.sleep(0.1)

    # 停止记录
    recorder.stop_recording()

    # 显示CSV文件内容
    print(f"\nCSV文件内容预览（前15行）:")
    print("-"*80)
    with open(recorder.csv_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 15:
                break
            print(f"{i+1:3d}: {line.rstrip()}")

    print(f"\n测试完成！CSV文件: {recorder.csv_file}")


def test_100_boards_recording():
    """测试100个板子的记录"""
    print("\n" + "="*80)
    print("测试2: 100个板子PWM值记录（1600个风扇）")
    print("="*80)

    # 创建100个板子的记录器
    print("\n创建100个板子的PWM记录器...")
    recorder = PWMCSVRecorder(
        board_count=100,  # 100个板子
        fans_per_board=16,
        interval=0.1  # 每0.1秒记录一次
    )

    print(f"CSV文件: {recorder.csv_file}")
    print(f"总风扇数: {recorder.total_fans}")
    print(f"列数: {recorder.total_fans + 2} (时间戳 + 经过时间 + {recorder.total_fans}个风扇)")

    # 开始记录
    recorder.start_recording()

    # 模拟10秒的数据
    print("\n生成模拟数据（10秒）...")
    start_time = time.time()
    time_counter = 0.0

    while time.time() - start_time < 10:
        time_counter += 0.1

        # 生成波浪式PWM值
        pwm_values = []
        for board_idx in range(100):
            phase = board_idx * (2 * np.pi / 100)
            for fan_idx in range(16):
                wave = np.sin(fan_idx * 0.5 + phase + time_counter)
                pwm = int(500 + 400 * wave)
                pwm_values.append(max(0, min(1000, pwm)))

        recorder.set_pwm_values(pwm_values)

        # 每秒打印一次进度
        elapsed = time.time() - start_time
        if int(elapsed * 10) % 10 == 0:
            progress = (elapsed / 10) * 100
            print(f"  进度: {progress:.0f}% ({elapsed:.1f}/10.0秒) - 已记录{recorder.record_count}行")

        time.sleep(0.1)

    # 停止记录
    recorder.stop_recording()

    # 显示统计信息
    print(f"\n文件统计:")
    print(f"  文件路径: {recorder.csv_file}")
    print(f"  文件大小: {os.path.getsize(recorder.csv_file):,} 字节 ({os.path.getsize(recorder.csv_file)/1024:.2f} KB)")
    print(f"  记录行数: {recorder.record_count}")
    print(f"  总数据点: {recorder.record_count * recorder.total_fans:,}")

    # 显示前几行
    print(f"\nCSV文件内容预览（前5行）:")
    print("-"*80)
    with open(recorder.csv_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(f"{i+1}: {line.rstrip()}")


def test_with_batch_controller():
    """测试与批量控制器集成"""
    print("\n" + "="*80)
    print("测试3: 与批量控制器集成")
    print("="*80)

    try:
        from hardware.fan_control import create_batch_controller

        # 创建批量控制器
        print("\n创建批量控制器...")
        batch_ctrl = create_batch_controller(
            board_count=10,  # 10个板子（演示用）
            base_ip="192.168.2.",
            start_ip=1,
            fans_per_board=16
        )

        print(f"板子数量: {batch_ctrl.board_count}")
        print(f"总风扇数: {batch_ctrl.board_count * 16}")

        # 创建带控制器的记录器
        print("\n创建PWM记录器...")
        recorder_with_ctrl = PWMRecorderWithController(
            batch_controller=batch_ctrl,
            interval=0.1
        )

        print(f"CSV文件: {recorder_with_ctrl.recorder.csv_file}")

        # 开始记录
        recorder_with_ctrl.start_recording()

        # 模拟3秒的数据
        print("\n生成模拟数据（3秒）...")
        for i in range(30):
            # 设置渐变PWM值
            recorder_with_ctrl.set_gradient_pwm()

            time.sleep(0.1)

            if i % 10 == 0:
                print(f"  进度: {(i/30)*100:.0f}%")

        # 停止记录
        recorder_with_ctrl.stop_recording()

        print(f"\n测试完成！CSV文件: {recorder_with_ctrl.recorder.csv_file}")

    except ImportError as e:
        print(f"\n无法导入批量控制器: {e}")
        print("跳过此测试")


def test_different_patterns():
    """测试不同的PWM模式"""
    print("\n" + "="*80)
    print("测试4: 不同的PWM模式")
    print("="*80)

    # 创建记录器
    print("\n创建PWM记录器...")
    recorder = PWMCSVRecorder(
        board_count=5,
        fans_per_board=16,
        interval=0.1
    )

    # 开始记录
    recorder.start_recording()

    # 模式1: 全部相同
    print("\n模式1: 所有风扇设置为500")
    for i in range(10):
        pwm_values = [500] * 80
        recorder.set_pwm_values(pwm_values)
        time.sleep(0.1)
    print(f"  已记录10行")

    # 模式2: 线性渐变
    print("\n模式2: 线性渐变 (0-1000)")
    for i in range(10):
        pwm_values = [int(i * (1000/80)) for i in range(80)]
        recorder.set_pwm_values(pwm_values)
        time.sleep(0.1)
    print(f"  已记录10行")

    # 模式3: 随机值
    print("\n模式3: 随机PWM值")
    for i in range(10):
        pwm_values = list(np.random.randint(0, 1001, 80))
        recorder.set_pwm_values(pwm_values)
        time.sleep(0.1)
    print(f"  已记录10行")

    # 停止记录
    recorder.stop_recording()

    print(f"\n测试完成！CSV文件: {recorder.csv_file}")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("PWM CSV记录器测试")
    print("="*80)
    print("\n本程序演示如何使用PWMCSVRecorder记录风扇PWM值到CSV文件")
    print("记录间隔: 0.1秒")
    print("支持: 100个板子 × 16个风扇 = 1600个风扇\n")

    print("请选择测试:")
    print("1. 基础PWM值记录（10个板子，5秒）")
    print("2. 100个板子PWM值记录（1600个风扇，10秒）")
    print("3. 与批量控制器集成（10个板子，3秒）")
    print("4. 不同的PWM模式（5个板子）")
    print("5. 快速演示（100个板子，3秒）")

    choice = input("\n请输入选择 (1-5): ").strip()

    if choice == '1':
        test_basic_recording()
    elif choice == '2':
        test_100_boards_recording()
    elif choice == '3':
        test_with_batch_controller()
    elif choice == '4':
        test_different_patterns()
    elif choice == '5':
        print("\n运行快速演示...")
        csv_file = create_demo_csv_recording(
            duration=3.0,
            interval=0.1,
            board_count=100
        )
        print(f"\n演示完成！CSV文件: {csv_file}")
    else:
        print("无效选择")
        return

    print("\n" + "="*80)
    print("测试完成!")
    print("="*80)
    print("\n提示:")
    print("- CSV文件可以用Excel、LibreOffice Calc或其他CSV查看器打开")
    print("- 第一列是时间戳")
    print("- 第二列是经过时间（秒）")
    print("- 后续1600列是每个风扇的PWM值")
    print("- 格式: Board001_Fan01, Board001_Fan02, ..., Board100_Fan16")


if __name__ == "__main__":
    main()
