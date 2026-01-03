# -*- coding: utf-8 -*-
"""
风扇控制模块

基于Modbus RTU协议的风扇速度控制系统

作者: Wind Field Hardware Team
创建时间: 2026-01-03
版本: 1.0.0
"""

from .modbus_fan import ModbusFanController
from .fan_encoder import FanSpeedEncoder, FanMapping, PresetEncoders, AdvancedFanEncoder
from .config import FanConfig, PredefinedConfigs
from .batch_control import BatchFanController, MultiBoardConfig, create_batch_controller

__all__ = [
    'ModbusFanController',
    'FanSpeedEncoder',
    'FanConfig',
    'FanMapping',
    'PredefinedConfigs',
    'PresetEncoders',
    'AdvancedFanEncoder',
    'BatchFanController',
    'MultiBoardConfig',
    'create_batch_controller',
]
