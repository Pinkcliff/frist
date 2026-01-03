# -*- coding: utf-8 -*-
"""
生成完整的风扇控制演示日志

模拟完整的控制过程，展示每个风扇的控制详情
"""

import sys
import os

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from hardware.fan_control import ModbusFanController, FanConfig


def main():
    """生成完整的演示日志"""

    print("\n" + "="*80)
    print("生成完整的风扇控制演示日志")
    print("="*80)

    # 创建配置
    config = FanConfig(device_ip="192.168.2.1", fan_count=16)

    # 创建控制器（启用日志）
    controller = ModbusFanController(config, enable_logging=True)

    print("\n正在模拟风扇控制操作...")
    print("日志文件将记录每个风扇的控制详情\n")

    # 模拟控制操作
    print("操作1: 设置单个风扇速度...")
    for i in range(4):
        speed = 25.0 + i * 25.0  # 25%, 50%, 75%, 100%
        controller.set_fan_speed(i, speed)
        print(f"  风扇#{i+1} -> {speed:.0f}%")

    print("\n操作2: 设置所有风扇为50%...")
    controller.set_all_fans_speed(50.0)

    print("\n操作3: 分别设置每个风扇（渐变模式）...")
    speeds = [i * (100.0 / 15) for i in range(16)]  # 0% to 100%
    controller.set_fans_speed_individual(speeds)
    print("  速度列表:", [f"{s:.1f}%" for s in speeds])

    print("\n操作4: 分别设置每个风扇（波浪模式）...")
    import math
    speeds = [50 + 30 * math.sin(i * 0.5) for i in range(16)]
    controller.set_fans_speed_individual(speeds)
    print("  速度列表:", [f"{s:.1f}%" for s in speeds])

    print("\n操作5: 停止所有风扇...")
    controller.stop_all_fans()

    # 打印统计信息
    controller.print_statistics()

    # 显示日志文件路径
    import glob
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    log_files = glob.glob(os.path.join(log_dir, '*.log'))

    if log_files:
        latest_log = max(log_files, key=os.path.getmtime)

        print("\n" + "="*80)
        print("日志文件已生成!")
        print("="*80)
        print(f"文件路径: {latest_log}")
        print(f"文件大小: {os.path.getsize(latest_log):,} 字节")
        print(f"总行数: {sum(1 for _ in open(latest_log, 'r', encoding='utf-8'))} 行")

        # 显示日志内容
        print("\n" + "="*80)
        print("日志文件完整内容:")
        print("="*80 + "\n")

        with open(latest_log, 'r', encoding='utf-8') as f:
            for line in f:
                print(line.rstrip())

        print("\n" + "="*80)
        print("日志说明:")
        print("="*80)
        print("每条日志记录包含:")
        print("  - 时间戳（精确到毫秒）")
        print("  - 日志级别（INFO/DEBUG/ERROR）")
        print("  - 风扇编号和索引")
        print("  - 速度百分比（0-100%）")
        print("  - PWM值（0-1000）")
        print("  - 寄存器地址（0x0000-0x000F）")
        print("  - 请求帧（Modbus RTU十六进制格式）")
        print("  - 操作结果（成功/失败）")
        print("\n示例日志解读:")
        print("  '风扇 #1 速度' - 控制第1个风扇")
        print("  '风扇索引: 0' - 内部0-based索引")
        print("  '速度百分比: 50.00%' - 用户可见的速度")
        print("  'PWM值: 500' - 实际发送到硬件的值")
        print("  '寄存器地址: 0x0000' - Modbus寄存器地址")
        print("  '请求帧: 01 06 00 00 01 F4 89 DD' - 完整的Modbus RTU帧")
        print("    - 01: 从站地址")
        print("    - 06: 功能码（写单个寄存器）")
        print("    - 00 00: 寄存器地址")
        print("    - 01 F4: 数据值（500 = 0x01F4）")
        print("    - 89 DD: CRC校验码")


if __name__ == "__main__":
    main()
