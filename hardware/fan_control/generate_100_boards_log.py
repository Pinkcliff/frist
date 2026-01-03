# -*- coding: utf-8 -*-
"""
生成100个板子的完整控制日志
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hardware.fan_control import create_batch_controller


def generate_100_boards_log():
    """生成100个板子的完整控制日志"""

    print("\n" + "="*80)
    print("生成100个板子的完整控制日志")
    print("="*80)

    # 创建批量控制器
    print("\n创建100个板子的批量控制器...")
    batch_ctrl = create_batch_controller(
        board_count=100,
        base_ip="192.168.2.",
        start_ip=1,
        fans_per_board=16
    )

    print(f"板子数量: {batch_ctrl.board_count}")
    print(f"总风扇数: {batch_ctrl.board_count * 16}")
    print(f"IP范围: 192.168.2.1 - 192.168.2.100\n")

    # 记录板子信息到日志
    logger = batch_ctrl.batch_logger

    print("开始生成日志...")

    # 1. 记录所有板子的配置信息
    logger.info("")
    logger.info("="*80)
    logger.info("所有板子的配置信息")
    logger.info("="*80)

    for i in range(100):
        config = batch_ctrl.board_configs[i]
        board_id = i + 1
        logger.info(f"板子#{board_id:3d}: IP={config.device_ip}, "
                   f"风扇数={config.fan_count}, "
                   f"寄存器范围=0x{config.start_register:04X}-0x{config.start_register + config.fan_count - 1:04X}")

    # 2. 模拟设置所有板子为50%
    logger.info("")
    logger.info("="*80)
    logger.info("操作1: 设置所有板子为50%")
    logger.info("="*80)

    for i in range(100):
        config = batch_ctrl.board_configs[i]
        board_id = i + 1
        logger.info(f"板子#{board_id:3d} ({config.device_ip}):")
        logger.info(f"  设置所有16个风扇为50%")
        logger.info(f"  PWM值: 500")
        logger.info(f"  寄存器范围: 0x{config.start_register:04X}-0x{config.start_register + config.fan_count - 1:04X}")

        # 记录每个风扇的详细信息
        for fan_idx in range(16):
            reg_addr = config.start_register + fan_idx
            logger.debug(f"    风扇#{fan_idx+1:2d}: 50.0% -> PWM:500 -> 寄存器:0x{reg_addr:04X}")

    # 3. 模拟分别设置每个板子（渐变模式）
    logger.info("")
    logger.info("="*80)
    logger.info("操作2: 分别设置每个板子（渐变模式）")
    logger.info("="*80)

    for i in range(100):
        config = batch_ctrl.board_configs[i]
        board_id = i + 1

        # 为每个板子生成渐变速度
        offset = i * 5.0
        speeds = [(j * (100.0 / 15) + offset) % 100 for j in range(16)]

        logger.info(f"板子#{board_id:3d} ({config.device_ip}):")
        logger.info(f"  分别设置16个风扇（渐变模式）")

        # 记录每个风扇
        for fan_idx, speed in enumerate(speeds):
            pwm = int((speed / 100.0) * 1000)
            reg_addr = config.start_register + fan_idx
            logger.info(f"    风扇#{fan_idx+1:2d}: {speed:5.1f}% -> PWM:{pwm:4d} -> 寄存器:0x{reg_addr:04X}")

    # 4. 统计信息
    logger.info("")
    logger.info("="*80)
    logger.info("控制统计信息")
    logger.info("="*80)
    logger.info(f"总板子数: 100")
    logger.info(f"总风扇数: 1600 (100个板子 × 16个风扇)")
    logger.info(f"总控制操作: 3200 (1600个风扇 × 2次操作)")
    logger.info(f"IP地址范围: 192.168.2.1 - 192.168.2.100")
    logger.info("="*80)

    # 打印总结
    print("\n日志生成完成!")
    print(f"日志内容:")
    print(f"  - 100个板子的配置信息")
    print(f"  - 每个板子的IP地址和风扇数量")
    print(f"  - 操作1: 所有1600个风扇设置为50%")
    print(f"  - 操作2: 分别设置1600个风扇（渐变模式）")
    print(f"  - 每个风扇的详细控制记录")
    print(f"    * 风扇编号")
    print(f"    * 速度百分比")
    print(f"    * PWM值")
    print(f"    * 寄存器地址")

    # 查找日志文件
    import glob
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    log_files = glob.glob(os.path.join(log_dir, 'batch_fan_control_*.log'))

    if log_files:
        latest_log = max(log_files, key=os.path.getmtime)
        print(f"\n日志文件:")
        print(f"  路径: {latest_log}")
        print(f"  大小: {os.path.getsize(latest_log):,} 字节")

        # 统计行数
        with open(latest_log, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        print(f"  行数: {line_count:,} 行")

        print(f"\n日志文件包含了所有100个板子（1600个风扇）的完整控制记录!")

    print("\n" + "="*80)
    print("完成!")
    print("="*80)


if __name__ == "__main__":
    generate_100_boards_log()
