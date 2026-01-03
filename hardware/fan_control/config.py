# -*- coding: utf-8 -*-
"""
风扇控制配置文件

定义风扇控制的所有配置参数
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class FanConfig:
    """风扇配置类"""

    # 网络配置
    device_ip: str = "192.168.2.1"      # 风扇控制器IP地址
    device_port: int = 8234             # Modbus TCP端口
    slave_addr: int = 1                 # Modbus从站地址

    # 风扇配置
    fan_count: int = 16                 # 风扇总数
    start_register: int = 0             # 起始寄存器地址
    pwm_min: int = 0                    # 最小PWM值（0%）
    pwm_max: int = 1000                 # 最大PWM值（100%）

    # 通信配置
    timeout: float = 5.0                # 通信超时时间（秒）
    reconnect_attempts: int = 3         # 重连尝试次数
    reconnect_delay: float = 2.0        # 重连延迟（秒）

    # 功能码
    func_code_write_single: int = 0x06  # 写单个寄存器
    func_code_write_multiple: int = 0x10  # 写多个寄存器

    # 编码配置
    enable_encoding: bool = True        # 是否启用编码
    encoding_base: int = 1000           # 编码基数（PWM最大值）

    def get_register_address(self, fan_index: int) -> int:
        """获取指定风扇的寄存器地址"""
        return self.start_register + fan_index

    def validate_fan_index(self, fan_index: int) -> bool:
        """验证风扇索引是否有效"""
        return 0 <= fan_index < self.fan_count

    def validate_pwm(self, pwm_value: int) -> bool:
        """验证PWM值是否有效"""
        return self.pwm_min <= pwm_value <= self.pwm_max

    def get_fan_list(self) -> List[int]:
        """获取所有风扇索引列表"""
        return list(range(self.fan_count))


# 预定义配置
class PredefinedConfigs:
    """预定义的配置模板"""

    # 单板配置（16风扇）
    SINGLE_BOARD_16_FANS = FanConfig(
        device_ip="192.168.2.1",
        fan_count=16,
        start_register=0,
    )

    # 单板配置（32风扇）
    SINGLE_BOARD_32_FANS = FanConfig(
        device_ip="192.168.2.1",
        fan_count=32,
        start_register=0,
    )

    # 双板配置（板1: 16风扇）
    DUAL_BOARD_BOARD1 = FanConfig(
        device_ip="192.168.2.1",
        fan_count=16,
        start_register=0,
    )

    # 双板配置（板2: 16风扇）
    DUAL_BOARD_BOARD2 = FanConfig(
        device_ip="192.168.2.2",
        fan_count=16,
        start_register=0,
    )
