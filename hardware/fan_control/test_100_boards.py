# -*- coding: utf-8 -*-
"""
100个板子的风扇控制测试

演示如何控制100个风扇控制器板（1600个风扇）
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
    BatchFanController,
    MultiBoardConfig,
    create_batch_controller,
)


def test_100_boards_basic():
    """测试100个板子的基础控制"""
    print("\n" + "="*80)
    print("测试: 100个板子基础控制")
    print("="*80)

    # 创建100个板子的控制器
    print("\n创建100个板子的批量控制器...")
    print("IP范围: 192.168.2.1 - 192.168.2.100")
    print("每个板子: 16个风扇")
    print("总风扇数: 1600\n")

    batch_ctrl = create_batch_controller(
        board_count=100,
        base_ip="192.168.2.",
        start_ip=1,
        fans_per_board=16
    )

    print(f"✅ 批量控制器创建完成")
    print(f"   板子数量: {batch_ctrl.board_count}")
    print(f"   总风扇数: {batch_ctrl.board_count * 16}\n")

    # 显示前10个和后10个板子的IP
    print("板子IP地址示例:")
    print("  前10个:")
    for i in range(10):
        config = batch_ctrl.board_configs[i]
        print(f"    板子#{i+1:3d}: {config.device_ip}")
    print("  ...")
    print("  后10个:")
    for i in range(90, 100):
        config = batch_ctrl.board_configs[i]
        print(f"    板子#{i+1:3d}: {config.device_ip}")

    # 模拟控制（不实际连接）
    print("\n模拟控制操作（不实际连接硬件）...")

    # 操作1: 设置所有板子为50%
    print("\n操作1: 设置所有板子为50%...")
    print("  模拟发送命令到100个板子...")
    print("  每个板子控制16个风扇...")
    print("  总共控制1600个风扇...")

    # 记录到日志
    if batch_ctrl.batch_logger:
        batch_ctrl.batch_logger.info('模拟操作: 设置所有板子为50%')
        batch_ctrl.batch_logger.info('  板子#1 (192.168.2.1): 设置16个风扇为50%')
        batch_ctrl.batch_logger.info('  板子#2 (192.168.2.2): 设置16个风扇为50%')
        batch_ctrl.batch_logger.info('  ...')
        batch_ctrl.batch_logger.info('  板子#100 (192.168.2.100): 设置16个风扇为50%')
        batch_ctrl.batch_logger.info('  总计: 100个板子 × 16个风扇 = 1600个风扇控制')

    print("  [模拟] 完成")

    # 操作2: 分别设置每个板子的风扇
    print("\n操作2: 分别设置每个板子的风扇（渐变模式）...")
    print("  生成100个板子的速度矩阵...")

    # 为每个板子生成渐变速度
    speed_matrix = []
    for board_idx in range(100):
        # 每个板子有不同的渐变偏移
        offset = board_idx * 5.0
        speeds = [(i * (100.0 / 15) + offset) % 100 for i in range(16)]
        speed_matrix.append(speeds)

    print(f"  速度矩阵大小: {len(speed_matrix)} × {len(speed_matrix[0])}")
    print(f"  总速度值: {len(speed_matrix) * len(speed_matrix[0])}")

    # 记录到日志
    if batch_ctrl.batch_logger:
        batch_ctrl.batch_logger.info('模拟操作: 分别设置每个板子的风扇')
        batch_ctrl.batch_logger.info(f'  速度矩阵: {len(speed_matrix)}个板子 × {len(speed_matrix[0])}个风扇')
        for i in range(min(5, len(speed_matrix))):
            board_id = i + 1
            speeds_str = ", ".join([f"{s:.1f}%" for s in speed_matrix[i][:8]])
            batch_ctrl.batch_logger.info(f'  板子#{board_id:3d}: [{speeds_str}, ...]')
        batch_ctrl.batch_logger.info('  ...')
        batch_ctrl.batch_logger.info(f'  板子#100: [...，{speed_matrix[-1][-1]:.1f}%]')

    print("  [模拟] 完成")

    # 打印统计信息
    batch_ctrl.print_batch_statistics()

    print("\n日志文件已保存，记录了所有100个板子的控制信息")
    print(f"每个板子包含:")
    print("  - 板子编号 (1-100)")
    print("  - IP地址 (192.168.2.1-100)")
    print("  - 16个风扇的控制详情")
    print("  - 每个风扇的速度百分比")
    print("  - 每个风扇的PWM值")
    print("  - 每个风扇的寄存器地址")


def test_10_boards_demo():
    """测试10个板子的演示（更快的演示）"""
    print("\n" + "="*80)
    print("演示: 10个板子控制（简化版，便于查看）")
    print("="*80)

    # 创建10个板子的控制器
    print("\n创建10个板子的批量控制器...")
    batch_ctrl = create_batch_controller(
        board_count=10,
        base_ip="192.168.2.",
        start_ip=1,
        fans_per_board=16
    )

    print(f"✅ 批量控制器创建完成")
    print(f"   板子数量: {batch_ctrl.board_count}")
    print(f"   IP范围: 192.168.2.1 - 192.168.2.10")
    print(f"   总风扇数: {batch_ctrl.board_count * 16}\n")

    # 显示所有板子的IP
    print("板子配置:")
    for i, config in enumerate(batch_ctrl.board_configs):
        print(f"  板子#{i+1:3d}: IP={config.device_ip}, 风扇数={config.fan_count}")

    # 模拟控制操作
    print("\n模拟控制操作...")

    # 操作1: 设置所有板子为75%
    print("\n操作1: 设置所有板子为75%")
    if batch_ctrl.batch_logger:
        batch_ctrl.batch_logger.info('='*80)
        batch_ctrl.batch_logger.info('操作1: 设置所有板子为75%')
        for i, config in enumerate(batch_ctrl.board_configs):
            board_id = i + 1
            batch_ctrl.batch_logger.info(f'  板子#{board_id} ({config.device_ip}):')
            batch_ctrl.batch_logger.info(f'    设置所有16个风扇为75%')
            batch_ctrl.batch_logger.info(f'    PWM值: 750')
            batch_ctrl.batch_logger.info(f'    寄存器范围: 0x0000-0x000F')
    print("  [模拟] 已发送命令到10个板子")

    # 操作2: 分别设置每个板子（波浪模式）
    print("\n操作2: 分别设置每个板子（波浪模式）")
    speed_matrix = []
    for board_idx in range(10):
        # 波浪模式
        phase = board_idx * (2 * np.pi / 10)
        speeds = [50 + 30 * np.sin(i * 0.5 + phase) for i in range(16)]
        speed_matrix.append(speeds)

    if batch_ctrl.batch_logger:
        batch_ctrl.batch_logger.info('='*80)
        batch_ctrl.batch_logger.info('操作2: 分别设置每个板子（波浪模式）')
        for i, speeds in enumerate(speed_matrix):
            board_id = i + 1
            ip = batch_ctrl.board_configs[i].device_ip
            speeds_str = ", ".join([f"{s:.1f}%" for s in speeds[:4]])
            batch_ctrl.batch_logger.info(f'  板子#{board_id} ({ip}): [{speed_str}, ...]')
            # 记录每个风扇的详细信息
            for j, speed in enumerate(speeds):
                pwm = int((speed / 100.0) * 1000)
                batch_ctrl.batch_logger.debug(f'    风扇#{j+1:2d}: {speed:5.1f}% -> PWM:{pwm:4d} -> 寄存器:0x{j:04X}')

    print("  [模拟] 已发送个性化命令到10个板子")

    # 操作3: 停止所有板子
    print("\n操作3: 停止所有板子")
    if batch_ctrl.batch_logger:
        batch_ctrl.batch_logger.info('='*80)
        batch_ctrl.batch_logger.info('操作3: 停止所有板子')
        for i, config in enumerate(batch_ctrl.board_configs):
            board_id = i + 1
            batch_ctrl.batch_logger.info(f'  板子#{board_id} ({config.device_ip}): 停止所有16个风扇')
    print("  [模拟] 已发送停止命令到10个板子")

    # 打印统计信息
    batch_ctrl.print_batch_statistics()

    print("\n日志已记录每个板子的详细信息:")
    print("  - 10个板子的IP地址")
    print("  - 每个板子16个风扇的控制")
    print("  - 总共160个风扇的设置记录")


def show_all_board_ips():
    """显示所有100个板子的IP地址"""
    print("\n" + "="*80)
    print("100个板子的IP地址列表")
    print("="*80)

    print("\n板子编号与IP地址对应关系:")
    print("-"*80)

    # 分4组显示
    for group in range(4):
        start = group * 25
        end = start + 25
        print(f"\n第{group+1}组 (板子#{start+1}-{end}):")
        for i in range(start, end):
            ip = f"192.168.2.{i+1}"
            print(f"  板子#{i+1:3d}: {ip}")

    print("\n" + "="*80)
    print("总计: 100个板子")
    print("每个板子: 16个风扇")
    print("总风扇数: 1600个")
    print("="*80)


def generate_sample_log():
    """生成示例日志文件"""
    print("\n" + "="*80)
    print("生成100个板子的示例日志")
    print("="*80)

    # 创建10个板子的演示（更快）
    print("\n正在生成日志文件...")
    print("使用10个板子进行演示（更快，日志更易查看）")

    test_10_boards_demo()

    # 查找最新日志文件
    import glob
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    log_files = glob.glob(os.path.join(log_dir, 'batch_fan_control_*.log'))

    if log_files:
        latest_log = max(log_files, key=os.path.getmtime)
        print("\n" + "="*80)
        print("日志文件已生成!")
        print("="*80)
        print(f"文件路径: {latest_log}")
        print(f"文件大小: {os.path.getsize(latest_log):,} 字节")

        # 显示日志内容预览
        print("\n日志内容预览（前50行）:")
        print("-"*80)
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:50], 1):
                print(f"{i:3d}: {line.rstrip()}")
        if len(lines) > 50:
            print(f"\n... 还有 {len(lines)-50} 行 ...\n")

        print("\n日志说明:")
        print("-"*80)
        print("对于100个板子，日志会记录:")
        print("  1. 初始化信息")
        print("     - 板子总数: 100")
        print("     - 每板风扇: 16")
        print("     - 总风扇数: 1600")
        print("     - IP范围: 192.168.2.1-100")
        print()
        print("  2. 连接信息")
        print("     - 每个板子的连接状态")
        print("     - 成功/失败统计")
        print()
        print("  3. 控制操作")
        print("     - 每个板子的控制命令")
        print("     - 16个风扇 × 100个板子 = 1600个风扇")
        print("     - 每个风扇的速度百分比")
        print("     - 每个风扇的PWM值")
        print("     - 每个风扇的寄存器地址")
        print("     - Modbus请求帧（十六进制）")
        print()
        print("  4. 统计信息")
        print("     - 总命令数")
        print("     - 成功/失败统计")
        print("     - 成功率")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("100个板子的风扇控制演示")
    print("="*80)
    print("\n本程序演示如何控制100个风扇控制器板")
    print("每个板子有16个风扇，总共1600个风扇")
    print("IP地址范围: 192.168.2.1 - 192.168.2.100")

    print("\n请选择演示:")
    print("1. 显示100个板子的IP地址列表")
    print("2. 测试100个板子基础控制（模拟）")
    print("3. 测试10个板子详细演示（推荐）")
    print("4. 生成示例日志文件")

    choice = input("\n请输入选择 (1-4): ").strip()

    if choice == '1':
        show_all_board_ips()
    elif choice == '2':
        test_100_boards_basic()
    elif choice == '3':
        test_10_boards_demo()
    elif choice == '4':
        generate_sample_log()
    else:
        print("无效选择")
        return

    print("\n" + "="*80)
    print("演示完成!")
    print("="*80)


if __name__ == "__main__":
    main()
