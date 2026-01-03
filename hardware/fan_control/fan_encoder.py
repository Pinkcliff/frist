# -*- coding: utf-8 -*-
"""
风扇速度编码器

将风场数据转换为风扇速度的编码模块
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FanMapping:
    """风扇映射配置"""

    # 风扇布局
    rows: int = 4           # 行数
    cols: int = 4           # 列数
    fan_count: int = 16     # 总风扇数

    # 速度映射参数
    min_threshold: float = 0.0   # 最小阈值（低于此值风扇关闭）
    max_threshold: float = 100.0 # 最大阈值
    speed_multiplier: float = 1.0  # 速度倍数

    # 高级映射选项
    enable_curve: bool = False    # 是否启用曲线映射
    curve_power: float = 2.0      # 曲线指数（>1=非线性加速）

    def __post_init__(self):
        """初始化后验证"""
        self.fan_count = self.rows * self.cols


class FanSpeedEncoder:
    """风扇速度编码器

    将2D风场数据编码为风扇速度控制信号
    """

    def __init__(self, mapping: Optional[FanMapping] = None):
        """
        初始化编码器

        Args:
            mapping: 风扇映射配置
        """
        self.mapping = mapping or FanMapping()

    def encode_grid_to_fans(self, grid_data: np.ndarray) -> List[float]:
        """
        将2D风场网格数据编码为风扇速度列表

        Args:
            grid_data: 2D numpy数组，形状为(40, 40)，值范围0-100

        Returns:
            List[float]: 风扇速度列表，长度为fan_count
        """
        # 下采样网格数据到风扇数量
        sampled_data = self._downsample_grid(grid_data)

        # 转换为风扇速度
        fan_speeds = self._normalize_to_fan_speed(sampled_data)

        return fan_speeds.tolist()

    def _downsample_grid(self, grid_data: np.ndarray) -> np.ndarray:
        """
        下采样网格数据到风扇布局

        Args:
            grid_data: 原始网格数据 (40x40)

        Returns:
            np.ndarray: 下采样后的数据 (rows x cols)
        """
        h, w = grid_data.shape
        target_h, target_w = self.mapping.rows, self.mapping.cols

        # 计算采样步长
        step_h = h / target_h
        step_w = w / target_w

        # 分块平均采样
        sampled = np.zeros((target_h, target_w))

        for i in range(target_h):
            for j in range(target_w):
                # 计算源区域
                h_start = int(i * step_h)
                h_end = int((i + 1) * step_h)
                w_start = int(j * step_w)
                w_end = int((j + 1) * step_w)

                # 提取区域并计算平均值
                region = grid_data[h_start:h_end, w_start:w_end]
                sampled[i, j] = np.mean(region) if region.size > 0 else 0.0

        return sampled

    def _normalize_to_fan_speed(self, sampled_data: np.ndarray) -> np.ndarray:
        """
        将采样数据规范化为风扇速度

        Args:
            sampled_data: 采样后的数据

        Returns:
            np.ndarray: 风扇速度数组
        """
        # 应用阈值
        normalized = np.clip(sampled_data,
                           self.mapping.min_threshold,
                           self.mapping.max_threshold)

        # 应用倍数
        normalized = normalized * self.mapping.speed_multiplier

        # 裁剪到0-100范围
        normalized = np.clip(normalized, 0.0, 100.0)

        # 应用曲线映射
        if self.mapping.enable_curve:
            normalized = self._apply_curve(normalized)

        return normalized.flatten()

    def _apply_curve(self, values: np.ndarray) -> np.ndarray:
        """
        应用非线性曲线映射

        Args:
            values: 输入值（0-100）

        Returns:
            np.ndarray: 曲线映射后的值
        """
        # 归一化到0-1
        normalized = values / 100.0

        # 应用幂函数
        if self.mapping.curve_power > 1:
            # 加速曲线（低值响应更灵敏）
            curved = np.power(normalized, 1.0 / self.mapping.curve_power)
        elif self.mapping.curve_power < 1:
            # 减速曲线（高值响应更灵敏）
            curved = np.power(normalized, self.mapping.curve_power)
        else:
            curved = normalized

        # 恢复到0-100范围
        return curved * 100.0

    def encode_region_to_fans(self,
                             grid_data: np.ndarray,
                             center: Tuple[int, int],
                             radius: int) -> List[float]:
        """
        编码特定区域的风扇速度

        Args:
            grid_data: 完整的网格数据
            center: 中心位置 (row, col)
            radius: 半径

        Returns:
            List[float]: 风扇速度列表
        """
        # 创建区域掩码
        h, w = grid_data.shape
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        mask = dist_from_center <= radius

        # 提取区域数据
        region_data = grid_data.copy()
        region_data[~mask] = 0.0

        # 编码
        return self.encode_grid_to_fans(region_data)

    def create_gradient_pattern(self,
                                direction: str = 'diagonal',
                                start_speed: float = 0.0,
                                end_speed: float = 100.0) -> List[float]:
        """
        创建渐变风扇速度模式

        Args:
            direction: 渐变方向 ('diagonal', 'horizontal', 'vertical')
            start_speed: 起始速度
            end_speed: 结束速度

        Returns:
            List[float]: 风扇速度列表
        """
        rows, cols = self.mapping.rows, self.mapping.cols
        speeds = np.zeros((rows, cols))

        if direction == 'horizontal':
            for i in range(rows):
                speeds[i, :] = np.linspace(start_speed, end_speed, cols)

        elif direction == 'vertical':
            for j in range(cols):
                speeds[:, j] = np.linspace(start_speed, end_speed, rows)

        else:  # diagonal
            for i in range(rows):
                for j in range(cols):
                    factor = (i + j) / (rows + cols - 2)
                    speeds[i, j] = start_speed + (end_speed - start_speed) * factor

        return speeds.flatten().tolist()

    def create_radial_pattern(self,
                             center: Optional[Tuple[int, int]] = None,
                             center_speed: float = 100.0,
                             edge_speed: float = 0.0) -> List[float]:
        """
        创建径向风扇速度模式

        Args:
            center: 中心位置 (row, col)，默认为网格中心
            center_speed: 中心速度
            edge_speed: 边缘速度

        Returns:
            List[float]: 风扇速度列表
        """
        rows, cols = self.mapping.rows, self.mapping.cols

        if center is None:
            center = (rows // 2, cols // 2)

        speeds = np.zeros((rows, cols))
        max_dist = np.sqrt((rows - 1)**2 + (cols - 1)**2) / 2

        for i in range(rows):
            for j in range(cols):
                dist = np.sqrt((i - center[0])**2 + (j - center[1])**2)
                factor = dist / max_dist
                speeds[i, j] = center_speed - (center_speed - edge_speed) * factor

        return speeds.flatten().tolist()

    def create_wave_pattern(self,
                           time: float = 0.0,
                           frequency: float = 1.0,
                           amplitude: float = 50.0) -> List[float]:
        """
        创建波浪风扇速度模式

        Args:
            time: 时间参数
            frequency: 频率
            amplitude: 振幅

        Returns:
            List[float]: 风扇速度列表
        """
        rows, cols = self.mapping.rows, self.mapping.cols
        speeds = np.zeros((rows, cols))

        for i in range(rows):
            for j in range(cols):
                # 对角线波浪
                phase = (i + j) * frequency * 0.5 + time
                value = 50.0 + amplitude * np.sin(phase)
                speeds[i, j] = np.clip(value, 0.0, 100.0)

        return speeds.flatten().tolist()


class AdvancedFanEncoder(FanSpeedEncoder):
    """高级风扇编码器

    提供更复杂的编码算法
    """

    def __init__(self, mapping: Optional[FanMapping] = None):
        super().__init__(mapping)

    def encode_with_weight_mask(self,
                                grid_data: np.ndarray,
                                weight_mask: Optional[np.ndarray] = None) -> List[float]:
        """
        使用权重掩码进行编码

        Args:
            grid_data: 网格数据
            weight_mask: 权重掩码（与风扇布局相同大小）

        Returns:
            List[float]: 风扇速度列表
        """
        sampled = self._downsample_grid(grid_data)

        if weight_mask is not None:
            weight_mask = weight_mask.reshape(self.mapping.rows, self.mapping.cols)
            sampled = sampled * weight_mask

        return self._normalize_to_fan_speed(sampled).tolist()

    def encode_with_zones(self,
                         grid_data: np.ndarray,
                         zones: Dict[str, Tuple[Tuple[int, int, int, int], float]]) -> List[float]:
        """
        分区编码

        Args:
            grid_data: 网格数据
            zones: 区域字典，格式为 {'zone_name': ((r1, r2, c1, c2), multiplier)}

        Returns:
            List[float]: 风扇速度列表
        """
        sampled = self._downsample_grid(grid_data)

        for zone_name, ((r1, r2, c1, c2), multiplier) in zones.items():
            sampled[r1:r2, c1:c2] = sampled[r1:r2, c1:c2] * multiplier

        return self._normalize_to_fan_speed(sampled).tolist()


# 预定义编码器
class PresetEncoders:
    """预定义的编码器配置"""

    # 4x4标准布局
    STANDARD_4X4 = FanSpeedEncoder(FanMapping(rows=4, cols=4))

    # 4x4高响应布局
    HIGH_RESPONSE_4X4 = FanSpeedEncoder(FanMapping(
        rows=4, cols=4,
        speed_multiplier=1.2,
        enable_curve=True,
        curve_power=1.5
    ))

    # 8x4布局（32风扇）
    STANDARD_8X4 = FanSpeedEncoder(FanMapping(rows=8, cols=4))

    # 4x8布局（32风扇）
    STANDARD_4X8 = FanSpeedEncoder(FanMapping(rows=4, cols=8))
