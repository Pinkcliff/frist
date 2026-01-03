# -*- coding: utf-8 -*-
"""
PWM值CSV记录器

将1600个风扇（100个板子 × 16个风扇）的PWM设置值
每隔0.1秒写入CSV文件

作者: Wind Field Hardware Team
创建时间: 2026-01-03
"""

import csv
import os
import threading
import time
from datetime import datetime
from typing import List, Optional
import numpy as np


class PWMCSVRecorder:
    """PWM值CSV记录器"""

    def __init__(
        self,
        board_count: int = 100,
        fans_per_board: int = 16,
        output_dir: str = None,
        interval: float = 0.1
    ):
        """
        初始化PWM CSV记录器

        Args:
            board_count: 板子数量，默认100
            fans_per_board: 每个板子的风扇数，默认16
            output_dir: 输出目录，默认为当前目录下的csv_files
            interval: 记录间隔（秒），默认0.1秒
        """
        self.board_count = board_count
        self.fans_per_board = fans_per_board
        self.total_fans = board_count * fans_per_board
        self.interval = interval

        # 输出目录
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(__file__),
                'csv_files'
            )
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # CSV文件路径
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_file = os.path.join(
            self.output_dir,
            f'pwm_values_{timestamp}.csv'
        )

        # 记录状态
        self.is_recording = False
        self.record_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # 当前PWM值（total_fans个元素）
        self.current_pwm_values = np.zeros(self.total_fans, dtype=int)

        # 统计信息
        self.record_count = 0
        self.start_time = None
        self.end_time = None

        # 初始化CSV文件
        self._init_csv_file()

    def _init_csv_file(self):
        """初始化CSV文件，写入表头"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # 生成列标题
            headers = ['timestamp', 'elapsed_time']

            # 为每个风扇生成列标题：Board1_Fan1, Board1_Fan2, ..., Board100_Fan16
            for board_idx in range(self.board_count):
                board_num = board_idx + 1
                for fan_idx in range(self.fans_per_board):
                    fan_num = fan_idx + 1
                    header = f'Board{board_num:03d}_Fan{fan_num:02d}'
                    headers.append(header)

            # 写入表头
            writer.writerow(headers)

        print(f"CSV文件已创建: {self.csv_file}")
        print(f"总风扇数: {self.total_fans}")
        print(f"记录间隔: {self.interval}秒")

    def set_pwm_values(self, pwm_values: List[int]):
        """
        设置所有风扇的PWM值

        Args:
            pwm_values: PWM值列表，长度应为total_fans
        """
        if len(pwm_values) != self.total_fans:
            raise ValueError(
                f"PWM值数量不匹配: 期望{self.total_fans}个，实际{len(pwm_values)}个"
            )

        self.current_pwm_values = np.array(pwm_values, dtype=int)

    def set_board_pwm(self, board_index: int, pwm_values: List[int]):
        """
        设置指定板子的风扇PWM值

        Args:
            board_index: 板子索引（0-based）
            pwm_values: 该板子的PWM值列表，长度应为fans_per_board
        """
        if board_index < 0 or board_index >= self.board_count:
            raise ValueError(f"板子索引超出范围: {board_index}")

        if len(pwm_values) != self.fans_per_board:
            raise ValueError(
                f"板子{board_index}的PWM值数量不匹配: "
                f"期望{self.fans_per_board}个，实际{len(pwm_values)}个"
            )

        start_idx = board_index * self.fans_per_board
        end_idx = start_idx + self.fans_per_board
        self.current_pwm_values[start_idx:end_idx] = pwm_values

    def _write_row(self):
        """写入一行数据到CSV文件"""
        # 时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # 经过时间
        if self.start_time:
            elapsed = time.time() - self.start_time
        else:
            elapsed = 0.0

        # 构建一行数据
        row = [timestamp, f'{elapsed:.3f}']

        # 添加所有风扇的PWM值
        for pwm_value in self.current_pwm_values:
            row.append(str(pwm_value))

        # 写入CSV文件
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        self.record_count += 1

    def _recording_loop(self):
        """记录循环"""
        self.start_time = time.time()

        while not self.stop_event.is_set():
            self._write_row()

            # 等待指定的间隔时间
            self.stop_event.wait(self.interval)

        self.end_time = time.time()

    def start_recording(self):
        """开始记录"""
        if self.is_recording:
            print("记录已经在进行中")
            return

        self.is_recording = True
        self.stop_event.clear()
        self.record_count = 0

        # 启动记录线程
        self.record_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.record_thread.start()

        print(f"\n开始记录PWM值到CSV文件...")
        print(f"文件: {self.csv_file}")
        print(f"间隔: {self.interval}秒")
        print(f"总风扇数: {self.total_fans}")

    def stop_recording(self):
        """停止记录"""
        if not self.is_recording:
            print("记录未在进行中")
            return

        print("\n正在停止记录...")
        self.stop_event.set()

        # 等待线程结束
        if self.record_thread:
            self.record_thread.join(timeout=5.0)

        self.is_recording = False

        # 计算统计信息
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
        else:
            duration = 0.0

        print("\n" + "="*80)
        print("记录已停止")
        print("="*80)
        print(f"CSV文件: {self.csv_file}")
        print(f"记录行数: {self.record_count}")
        print(f"记录时长: {duration:.2f}秒")
        print(f"实际间隔: {duration / self.record_count:.4f}秒" if self.record_count > 0 else "N/A")
        print(f"文件大小: {os.path.getsize(self.csv_file):,} 字节")
        print("="*80)

    def get_statistics(self):
        """获取统计信息"""
        return {
            'csv_file': self.csv_file,
            'is_recording': self.is_recording,
            'record_count': self.record_count,
            'total_fans': self.total_fans,
            'interval': self.interval,
            'file_size': os.path.getsize(self.csv_file) if os.path.exists(self.csv_file) else 0
        }


class PWMRecorderWithController:
    """带批量控制器的PWM记录器"""

    def __init__(
        self,
        batch_controller,
        interval: float = 0.1,
        output_dir: str = None
    ):
        """
        初始化带控制器的PWM记录器

        Args:
            batch_controller: 批量风扇控制器实例
            interval: 记录间隔（秒），默认0.1秒
            output_dir: 输出目录
        """
        self.batch_controller = batch_controller
        self.board_count = batch_controller.board_count
        self.fans_per_board = 16  # 假设每个板子16个风扇

        # 创建CSV记录器
        self.recorder = PWMCSVRecorder(
            board_count=self.board_count,
            fans_per_board=self.fans_per_board,
            output_dir=output_dir,
            interval=interval
        )

    def sync_pwm_from_controller(self):
        """从控制器同步当前PWM值"""
        all_pwm_values = []

        for controller in self.batch_controller.controllers:
            # 获取每个控制器的当前PWM值
            if hasattr(controller, 'current_pwm_values'):
                all_pwm_values.extend(controller.current_pwm_values)
            else:
                # 如果控制器没有存储PWM值，使用0填充
                all_pwm_values.extend([0] * self.fans_per_board)

        self.recorder.set_pwm_values(all_pwm_values)

    def start_recording(self):
        """开始记录"""
        self.recorder.start_recording()

    def stop_recording(self):
        """停止记录"""
        self.recorder.stop_recording()

    def set_all_fans_pwm(self, pwm_value: int):
        """
        设置所有风扇为相同的PWM值

        Args:
            pwm_value: PWM值 (0-1000)
        """
        pwm_values = [pwm_value] * self.recorder.total_fans
        self.recorder.set_pwm_values(pwm_values)

    def set_gradient_pwm(self):
        """设置渐变PWM值（用于演示）"""
        pwm_values = []
        for board_idx in range(self.board_count):
            # 每个板子有不同的渐变
            offset = board_idx * 50
            for fan_idx in range(self.fans_per_board):
                pwm = (fan_idx * (1000 / 15) + offset) % 1000
                pwm_values.append(int(pwm))

        self.recorder.set_pwm_values(pwm_values)

    def set_wave_pwm(self, time_val: float):
        """
        设置波浪式PWM值（随时间变化）

        Args:
            time_val: 时间值，用于生成波浪效果
        """
        pwm_values = []
        for board_idx in range(self.board_count):
            # 每个板子的相位偏移
            phase = board_idx * (2 * np.pi / self.board_count)
            for fan_idx in range(self.fans_per_board):
                # 生成波浪效果
                wave = np.sin(fan_idx * 0.5 + phase + time_val)
                pwm = int(500 + 400 * wave)  # 范围: 100-900
                pwm_values.append(max(0, min(1000, pwm)))

        self.recorder.set_pwm_values(pwm_values)


def create_demo_csv_recording(
    duration: float = 10.0,
    interval: float = 0.1,
    board_count: int = 100
):
    """
    创建演示CSV记录

    Args:
        duration: 记录时长（秒）
        interval: 记录间隔（秒）
        board_count: 板子数量
    """
    print("\n" + "="*80)
    print("PWM值CSV记录演示")
    print("="*80)

    # 创建记录器
    recorder = PWMCSVRecorder(
        board_count=board_count,
        fans_per_board=16,
        interval=interval
    )

    # 开始记录
    recorder.start_recording()

    # 模拟PWM值变化
    print(f"\n开始生成PWM值数据（持续{duration}秒）...")
    start_time = time.time()
    time_counter = 0.0

    try:
        while time.time() - start_time < duration:
            # 每0.5秒更新一次PWM值
            time_counter += interval

            # 生成波浪式PWM值
            pwm_values = []
            for board_idx in range(board_count):
                phase = board_idx * (2 * np.pi / board_count)
                for fan_idx in range(16):
                    wave = np.sin(fan_idx * 0.5 + phase + time_counter)
                    pwm = int(500 + 400 * wave)
                    pwm_values.append(max(0, min(1000, pwm)))

            recorder.set_pwm_values(pwm_values)

            # 每秒打印一次进度
            elapsed = time.time() - start_time
            if int(elapsed) > int(elapsed - interval):
                progress = (elapsed / duration) * 100
                print(f"  进度: {progress:.1f}% ({elapsed:.1f}/{duration:.1f}秒) "
                      f"- 已记录{recorder.record_count}行")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n用户中断记录")

    # 停止记录
    recorder.stop_recording()

    # 显示文件信息
    print(f"\nCSV文件内容预览（前20行）:")
    print("-"*80)
    with open(recorder.csv_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 20:
                break
            print(f"{i+1:3d}: {line.rstrip()}")
    if recorder.record_count > 20:
        print(f"... 还有 {recorder.record_count - 20} 行数据 ...\n")

    return recorder.csv_file


if __name__ == "__main__":
    # 运行演示
    csv_file = create_demo_csv_recording(
        duration=10.0,  # 记录10秒
        interval=0.1,   # 每0.1秒记录一次
        board_count=100 # 100个板子
    )

    print(f"\n演示完成！")
    print(f"CSV文件: {csv_file}")
    print(f"您可以用Excel或其他工具打开此文件查看1600个风扇的PWM值变化")
