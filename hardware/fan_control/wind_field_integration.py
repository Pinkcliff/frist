# -*- coding: utf-8 -*-
"""
风场编辑器与风扇控制集成示例

演示如何将风场编辑器的数据实时转换为风扇速度控制
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
    PresetEncoders,
)


class WindFieldFanController:
    """风场风扇控制器

    将风场编辑器的数据转换为风扇控制信号
    """

    def __init__(self,
                 encoder: FanSpeedEncoder = None,
                 config: FanConfig = None):
        """
        初始化控制器

        Args:
            encoder: 风扇速度编码器
            config: 风扇配置
        """
        self.encoder = encoder or PresetEncoders.STANDARD_4X4
        self.config = config or FanConfig(device_ip="192.168.2.1", fan_count=16)
        self.controller = ModbusFanController(self.config)

        # 当前状态
        self.current_speeds = [0.0] * self.config.fan_count
        self.is_connected = False

    def connect(self) -> bool:
        """连接到风扇控制器"""
        self.is_connected = self.controller.connect()
        return self.is_connected

    def disconnect(self):
        """断开连接"""
        self.controller.disconnect()
        self.is_connected = False

    def apply_wind_field(self, grid_data: np.ndarray, time_value: float = 0.0) -> bool:
        """
        应用风场数据到风扇

        Args:
            grid_data: 40x40的风场网格数据
            time_value: 时间参数（用于动画）

        Returns:
            bool: 成功返回True
        """
        if not self.is_connected:
            print("❌ 未连接到风扇控制器")
            return False

        # 编码为风扇速度
        self.current_speeds = self.encoder.encode_grid_to_fans(grid_data)

        # 发送到控制器
        success = self.controller.set_fans_speed_individual(self.current_speeds)

        return success

    def apply_function(self, function_name: str, params: dict = None, time: float = 0.0) -> bool:
        """
        应用预设函数模式

        Args:
            function_name: 函数名称
            params: 函数参数
            time: 时间参数

        Returns:
            bool: 成功返回True
        """
        if not self.is_connected:
            print("❌ 未连接到风扇控制器")
            return False

        # 根据函数名称生成风扇速度
        if function_name == 'gradient':
            direction = params.get('direction', 'diagonal') if params else 'diagonal'
            speeds = self.encoder.create_gradient_pattern(direction, 0, 100)

        elif function_name == 'radial':
            center_speed = params.get('center_speed', 100.0) if params else 100.0
            edge_speed = params.get('edge_speed', 0.0) if params else 0.0
            speeds = self.encoder.create_radial_pattern(
                center_speed=center_speed,
                edge_speed=edge_speed
            )

        elif function_name == 'wave':
            frequency = params.get('frequency', 1.0) if params else 1.0
            amplitude = params.get('amplitude', 50.0) if params else 50.0
            speeds = self.encoder.create_wave_pattern(
                time=time,
                frequency=frequency,
                amplitude=amplitude
            )

        elif function_name == 'all':
            speed = params.get('speed', 50.0) if params else 50.0
            return self.controller.set_all_fans_speed(speed)

        elif function_name == 'stop':
            return self.controller.stop_all_fans()

        else:
            print(f"❌ 未知的函数: {function_name}")
            return False

        # 发送到控制器
        self.current_speeds = speeds
        return self.controller.set_fans_speed_individual(speeds)

    def animate_function(self, function_name: str, duration: float = 10.0, params: dict = None):
        """
        动画播放函数模式

        Args:
            function_name: 函数名称
            duration: 动画持续时间（秒）
            params: 函数参数
        """
        if not self.is_connected:
            print("❌ 未连接到风扇控制器")
            return

        print(f"▶️  开始播放动画: {function_name} (持续{duration}秒)")

        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            frame_count += 1

            # 应用当前时间的函数
            self.apply_function(function_name, params, current_time)

            # 控制帧率（10fps）
            time.sleep(0.1)

        print(f"⏹️  动画结束，共播放{frame_count}帧")

    def get_current_speeds(self) -> list:
        """获取当前风扇速度"""
        return self.current_speeds.copy()

    def print_current_speeds(self):
        """打印当前风扇速度"""
        print("\n当前风扇速度:")
        print("="*40)

        rows, cols = self.encoder.mapping.rows, self.encoder.mapping.cols

        for i in range(rows):
            row_str = ""
            for j in range(cols):
                idx = i * cols + j
                speed = self.current_speeds[idx]
                row_str += f"{speed:5.1f}% "
            print(f"| {row_str}|")

        print("="*40)

    def stop_all(self):
        """停止所有风扇"""
        if self.is_connected:
            self.controller.stop_all_fans()
            self.current_speeds = [0.0] * self.config.fan_count
            print("🛑 所有风扇已停止")


def demo_1_basic_usage():
    """演示1: 基础使用"""
    print("\n" + "="*60)
    print("演示1: 基础使用 - 风场数据应用到风扇")
    print("="*60)

    # 创建控制器
    fan_ctrl = WindFieldFanController()

    # 连接
    if not fan_ctrl.connect():
        print("连接失败，演示结束")
        return

    try:
        # 创建测试风场数据
        grid_data = np.zeros((40, 40))
        for i in range(40):
            for j in range(40):
                grid_data[i, j] = 50 + 30 * np.sin(i / 5.0) * np.cos(j / 5.0)

        # 应用到风扇
        print("应用风场数据...")
        fan_ctrl.apply_wind_field(grid_data)

        # 显示当前速度
        fan_ctrl.print_current_speeds()

        time.sleep(3)

    finally:
        fan_ctrl.stop_all()
        fan_ctrl.disconnect()


def demo_2_function_patterns():
    """演示2: 函数模式"""
    print("\n" + "="*60)
    print("演示2: 函数模式")
    print("="*60)

    fan_ctrl = WindFieldFanController()

    if not fan_ctrl.connect():
        print("连接失败，演示结束")
        return

    try:
        # 1. 渐变模式
        print("\n1. 对角线渐变")
        fan_ctrl.apply_function('gradient', {'direction': 'diagonal'})
        fan_ctrl.print_current_speeds()
        time.sleep(2)

        # 2. 径向模式
        print("\n2. 径向模式")
        fan_ctrl.apply_function('radial', {'center_speed': 100, 'edge_speed': 0})
        fan_ctrl.print_current_speeds()
        time.sleep(2)

        # 3. 所有风扇50%
        print("\n3. 所有风扇50%")
        fan_ctrl.apply_function('all', {'speed': 50})
        fan_ctrl.print_current_speeds()
        time.sleep(2)

    finally:
        fan_ctrl.stop_all()
        fan_ctrl.disconnect()


def demo_3_animation():
    """演示3: 动画效果"""
    print("\n" + "="*60)
    print("演示3: 动画效果")
    print("="*60)

    fan_ctrl = WindFieldFanController()

    if not fan_ctrl.connect():
        print("连接失败，演示结束")
        return

    try:
        # 播放波浪动画
        print("播放波浪动画...")
        fan_ctrl.animate_function('wave', duration=5.0, params={
            'frequency': 2.0,
            'amplitude': 50.0
        })

        # 显示最终速度
        fan_ctrl.print_current_speeds()

    finally:
        fan_ctrl.stop_all()
        fan_ctrl.disconnect()


def demo_4_continuous_control():
    """演示4: 持续控制"""
    print("\n" + "="*60)
    print("演示4: 持续控制（每秒更新风场）")
    print("="*60)

    fan_ctrl = WindFieldFanController()

    if not fan_ctrl.connect():
        print("连接失败，演示结束")
        return

    try:
        print("持续更新10秒...")
        for t in range(10):
            # 创建随时间变化的风场
            grid_data = np.zeros((40, 40))
            for i in range(40):
                for j in range(40):
                    grid_data[i, j] = 50 + 40 * np.sin(i / 5.0 + t * 0.5) * np.cos(j / 5.0)

            # 应用到风扇
            fan_ctrl.apply_wind_field(grid_data, time_value=t * 0.1)

            print(f"时间 {t+1}秒")
            fan_ctrl.print_current_speeds()

            time.sleep(1)

    finally:
        fan_ctrl.stop_all()
        fan_ctrl.disconnect()


def demo_5_custom_layout():
    """演示5: 自定义布局"""
    print("\n" + "="*60)
    print("演示5: 自定义布局（8x4，32风扇）")
    print("="*60)

    # 创建32风扇配置
    from hardware.fan_control import FanMapping

    custom_mapping = FanMapping(rows=8, cols=4)
    custom_encoder = FanSpeedEncoder(custom_mapping)
    custom_config = FanConfig(device_ip="192.168.2.1", fan_count=32)

    fan_ctrl = WindFieldFanController(
        encoder=custom_encoder,
        config=custom_config
    )

    if not fan_ctrl.connect():
        print("连接失败，演示结束")
        return

    try:
        # 应用渐变模式
        fan_ctrl.apply_function('gradient', {'direction': 'horizontal'})
        fan_ctrl.print_current_speeds()

        time.sleep(3)

    finally:
        fan_ctrl.stop_all()
        fan_ctrl.disconnect()


def main():
    """主函数"""
    demos = [
        ("基础使用", demo_1_basic_usage),
        ("函数模式", demo_2_function_patterns),
        ("动画效果", demo_3_animation),
        ("持续控制", demo_4_continuous_control),
        ("自定义布局", demo_5_custom_layout),
    ]

    print("\n" + "="*60)
    print("风场编辑器 - 风扇控制集成演示")
    print("="*60)
    print("\n可用演示:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")

    print("\n请选择要运行的演示（1-5），或输入0运行所有演示:")
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
        elif 1 <= choice_num <= len(demos):
            # 运行选定的演示
            name, func = demos[choice_num - 1]
            func()
        else:
            print("❌ 无效的选择")
    except ValueError:
        print("❌ 请输入数字")


if __name__ == "__main__":
    main()
