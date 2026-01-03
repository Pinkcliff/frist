# -*- coding: utf-8 -*-
"""
快速生成风扇控制日志文件

此脚本模拟风扇控制过程并生成详细的.log文件
"""

import sys
import os
import time

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from hardware.fan_control import (
    ModbusFanController,
    FanConfig,
    FanSpeedEncoder,
    PresetEncoders,
)


def main():
    """主函数 - 模拟风扇控制并生成日志"""

    print("\n" + "="*80)
    print("风扇控制日志生成器")
    print("="*80)
    print("\n此脚本将模拟风扇控制过程并生成详细的.log文件")
    print("日志文件将记录每个风扇的控制详情\n")

    # 创建配置
    config = FanConfig(device_ip="192.168.2.1", fan_count=16)

    # 创建控制器（启用日志）
    print("正在创建风扇控制器...")
    controller = ModbusFanController(config, enable_logging=True)

    print("\n开始模拟风扇控制过程...")
    print("注意: 实际不会连接硬件，但会生成完整的日志\n")

    # 模拟各种控制操作
    try:
        # 操作1: 设置单个风扇
        print("1. 设置单个风扇速度...")
        for i in range(4):
            controller.set_fan_speed(i, 50.0 + i * 10)
            time.sleep(0.1)

        # 操作2: 设置所有风扇
        print("2. 设置所有风扇为75%...")
        controller.set_all_fans_speed(75.0)
        time.sleep(0.5)

        # 操作3: 分别设置每个风扇（渐变）
        print("3. 应用渐变速度模式...")
        speeds = [i * (100.0 / 15) for i in range(16)]
        controller.set_fans_speed_individual(speeds)
        time.sleep(0.5)

        # 操作4: 应用波浪模式
        print("4. 应用波浪模式...")
        import numpy as np
        speeds = [50 + 30 * np.sin(i * 0.5) for i in range(16)]
        controller.set_fans_speed_individual(speeds)
        time.sleep(0.5)

        # 操作5: 停止所有风扇
        print("5. 停止所有风扇...")
        controller.stop_all_fans()

    except Exception as e:
        print(f"\n控制过程出错: {e}")

    # 打印统计信息
    controller.print_statistics()

    # 查找并显示日志文件
    import glob
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')

    if os.path.exists(log_dir):
        log_files = glob.glob(os.path.join(log_dir, '*.log'))
        if log_files:
            latest_log = max(log_files, key=os.path.getmtime)
            print("\n" + "="*80)
            print("日志文件已生成!")
            print("="*80)
            print(f"文件路径: {latest_log}")
            print(f"文件大小: {os.path.getsize(latest_log):,} 字节")

            # 显示日志文件的前几行
            print("\n日志文件内容预览（前30行）:")
            print("-"*80)
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:30], 1):
                    print(f"{i:3d}: {line.rstrip()}")
            if len(lines) > 30:
                print(f"\n... 还有 {len(lines)-30} 行 ...\n")

            print("\n提示: 使用任何文本编辑器打开.log文件查看完整日志")
            print("日志中包含每个风扇的:")
            print("  - 风扇编号和索引")
            print("  - 速度百分比")
            print("  - PWM值")
            print("  - 寄存器地址")
            print("  - 请求帧（十六进制）")
            print("  - 操作结果（成功/失败）")

    print("\n" + "="*80)
    print("完成!")
    print("="*80)


if __name__ == "__main__":
    main()
