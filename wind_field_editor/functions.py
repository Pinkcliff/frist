# -*- coding: utf-8 -*-
"""
风场编辑 - 函数模板模块

提供12种数学函数模板用于风场生成

创建时间: 2024-01-03
作者: Wind Field Editor Team
版本: 1.0.0

修改历史:
    2024-01-03 [v1.0.0] 初始版本
        - 从fan_con项目移植12种函数模板
        - 实现高斯、径向波、渐变等函数
        - 添加函数参数验证

依赖:
    - numpy >= 1.19.0
"""

import numpy as np
from typing import Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class FunctionParams:
    """函数参数基类"""
    center: Tuple[float, float] = (20.0, 20.0)  # 函数中心 (行, 列) - 默认在第20行第20列风扇
    amplitude: float = 100.0                      # 幅度
    time: float = 0.0                              # 时间参数


class WindFieldFunction:
    """风场函数基类"""

    @staticmethod
    def validate_grid(grid_data: np.ndarray) -> None:
        """验证网格数据"""
        if grid_data.ndim != 2:
            raise ValueError("网格数据必须是2维数组")
        if grid_data.shape[0] != grid_data.shape[1]:
            raise ValueError("网格必须是正方形")

    @staticmethod
    def normalize(value: np.ndarray, min_val: float = 0.0,
                  max_val: float = 100.0) -> np.ndarray:
        """归一化到指定范围"""
        return np.clip(value, min_val, max_val)


# ==================== 基础波形函数 ====================

class SimpleWaveFunction(WindFieldFunction):
    """简单波动函数

    公式: z = sin(x) * cos(y + t)
    适用场景: 基础波浪分布
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用简单波动"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        # 归一化坐标到 [-5, 5]
        x = np.linspace(-5, 5, cols)
        y = np.linspace(-5, 5, rows)
        X, Y = np.meshgrid(x, y)  # 使用默认的indexing='xy'

        # 计算波浪
        Z = np.sin(X) * np.cos(Y + time)

        # 归一化到 [0, 100] 并应用幅度
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class RadialWaveFunction(WindFieldFunction):
    """径向波动函数

    公式: z = sin(r - t) * exp(-0.1 * r)
    适用场景: 从中心向外扩散的波浪
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()

    def apply(self, grid_data: np.ndarray, time: float = 0.0,
              decay: float = 0.1) -> np.ndarray:
        """应用径向波动

        坐标系统：
        - 函数中心在(20.5, 20.5)，对应风扇(20,20),(20,21),(21,20),(21,21)的中心
        - 每个风扇的坐标：x = col - 20 + 0.5, y = row - 20 + 0.5
        """
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        row_center, col_center = self.params.center

        # 创建坐标网格
        x = np.arange(cols) - 20 + 0.5  # 列坐标
        y = np.arange(rows) - 20 + 0.5  # 行坐标
        X, Y = np.meshgrid(x, y)

        # 如果中心不是(20,20)，需要调整偏移
        offset_col = 20 - col_center
        offset_row = 20 - row_center
        X = X + offset_col
        Y = Y + offset_row

        # 计算到中心的距离
        R = np.sqrt(X ** 2 + Y ** 2)

        # 归一化距离
        R_norm = R / np.max(R) * 5

        # 计算径向波
        Z = np.sin(R_norm - time) * np.exp(-decay * R_norm)

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


# ==================== 高斯函数 ====================

class GaussianFunction(WindFieldFunction):
    """高斯函数

    公式: z = A * exp(-(r²) / (2σ²))
    适用场景: 中心高斯分布
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.sigma = 5.0  # 标准差

    def set_sigma(self, sigma: float) -> None:
        """设置标准差"""
        self.sigma = max(0.1, sigma)

    def apply(self, grid_data: np.ndarray, sigma: Optional[float] = None,
              time: float = 0.0) -> np.ndarray:
        """应用高斯分布

        坐标系统：
        - 每个风扇使用其整数坐标(row, col)进行计算
        - 函数中心在(20, 20)时，周围4个风扇(20,20),(20,21),(21,20),(21,21)对称
        """
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        if sigma is not None:
            self.set_sigma(sigma)

        row_center, col_center = self.params.center

        # 创建坐标网格，每个风扇使用其整数坐标
        x = np.arange(cols)  # 列坐标：0, 1, 2, ..., 39
        y = np.arange(rows)  # 行坐标：0, 1, 2, ..., 39
        X, Y = np.meshgrid(x, y)

        # 计算到中心的距离平方
        dist_sq = (X - col_center) ** 2 + (Y - row_center) ** 2

        # 高斯函数
        Z = self.params.amplitude * np.exp(-dist_sq / (2 * self.sigma ** 2))

        # 添加时间动态：中心移动
        if time > 0:
            offset_x = 3 * np.cos(time * 0.5)  # 列方向偏移
            offset_y = 3 * np.sin(time * 0.5)  # 行方向偏移
            dist_sq = (X - col_center - offset_x) ** 2 + (Y - row_center - offset_y) ** 2
            Z = self.params.amplitude * np.exp(-dist_sq / (2 * self.sigma ** 2))

        return self.normalize(Z)


class GaussianWavePacketFunction(WindFieldFunction):
    """高斯波包函数

    公式: z = exp(-((x-x0)² + (y-y0)²) / (2σ²)) * sin(kx*x + ky*y + ωt)
    适用场景: 移动的高斯波包
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.sigma = 2.0
        self.k_x = 2.0  # x方向波数
        self.k_y = 2.0  # y方向波数
        self.omega = 1.0  # 角频率

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用高斯波包

        坐标系统：
        - 函数中心在(20.5, 20.5)，对应风扇(20,20),(20,21),(21,20),(21,21)的中心
        - 每个风扇的坐标：x = col - 20 + 0.5, y = row - 20 + 0.5
        """
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        row_center, col_center = self.params.center

        # 波包中心随时间移动（在新的坐标系统中）
        x0 = 5 * np.cos(time * 0.3)  # 相对于中心的x偏移
        y0 = 5 * np.sin(time * 0.3)  # 相对于中心的y偏移

        # 创建坐标网格
        x = np.arange(cols) - 20 + 0.5  # 列坐标
        y = np.arange(rows) - 20 + 0.5  # 行坐标
        X, Y = np.meshgrid(x, y)

        # 如果中心不是(20,20)，需要调整偏移
        offset_col = 20 - col_center
        offset_row = 20 - row_center
        X = X + offset_col
        Y = Y + offset_row

        # 高斯包络
        envelope = np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * self.sigma ** 2))

        # 载波
        carrier = np.sin(self.k_x * X + self.k_y * Y + self.omega * time)

        Z = self.params.amplitude * envelope * carrier

        # 归一化到 [0, 100]
        Z = (Z + self.params.amplitude) / (2 * self.params.amplitude) * 100

        return self.normalize(Z)


# ==================== 渐变函数 ====================

class LinearGradientFunction(WindFieldFunction):
    """线性渐变函数

    公式: z = 0.5 * (x + y) * sin(t)
    适用场景: 对角线方向渐变
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.direction = 'diagonal'  # 'x', 'y', 'diagonal'

    def set_direction(self, direction: str) -> None:
        """设置渐变方向"""
        if direction not in ['x', 'y', 'diagonal']:
            raise ValueError("方向必须是 'x', 'y', 或 'diagonal'")
        self.direction = direction

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用线性渐变"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        x = np.linspace(-1, 1, cols)
        y = np.linspace(-1, 1, rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        if self.direction == 'x':
            Z = X * np.sin(time) if time > 0 else X
        elif self.direction == 'y':
            Z = Y * np.sin(time) if time > 0 else Y
        else:  # diagonal
            Z = 0.5 * (X + Y) * np.sin(time) if time > 0 else 0.5 * (X + Y)

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class RadialGradientFunction(WindFieldFunction):
    """径向渐变函数

    公式: z = (r / 5) * cos(t + r)
    适用场景: 同心圆渐变
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()

    def apply(self, grid_data: np.ndarray, time: float = 0.0,
              num_bands: int = 3) -> np.ndarray:
        """应用径向渐变"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        cr, cc = self.params.center
        x = np.arange(cols)
        y = np.arange(rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 计算到中心的距离
        R = np.sqrt((X - cc) ** 2 + (Y - cr) ** 2)

        # 归一化距离
        max_r = np.sqrt(cr ** 2 + cc ** 2)
        r_norm = R / (max_r + 1) * 5

        # 径向渐变
        Z = (r_norm / 5) * np.cos(time + r_norm) if time > 0 else r_norm / 5

        # 添加同心圆条纹
        if num_bands > 0:
            Z = (np.sin(2 * np.pi * num_bands * r_norm / 5 - time) + 1) / 2

        # 归一化到 [0, 100]
        Z = Z * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class CircularGradientFunction(WindFieldFunction):
    """圆形渐变函数

    公式: z = clip((r - r_inner) / (r_outer - r_inner), 0, 1)
    适用场景: 从中心向外扩散的圆形渐变
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.inner_radius = 0.0
        self.outer_radius = 10.0

    def set_radii(self, inner: float, outer: float) -> None:
        """设置内外半径"""
        self.inner_radius = max(0, inner)
        self.outer_radius = max(inner + 0.1, outer)

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用圆形渐变"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        cr, cc = self.params.center
        x = np.arange(cols)
        y = np.arange(rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 计算到中心的距离
        R = np.sqrt((X - cc) ** 2 + (Y - cr) ** 2)

        # 扩展的外圆半径
        current_outer = self.outer_radius + time * 2 if time > 0 else self.outer_radius

        # 圆形渐变
        Z = np.clip((R - self.inner_radius) / (current_outer - self.inner_radius), 0, 1)

        # 归一化到 [0, 100]
        Z = Z * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


# ==================== 复杂波形函数 ====================

class SpiralWaveFunction(WindFieldFunction):
    """螺旋波函数

    公式: z = sin(n*θ + r - t) * exp(-0.1*r)
    适用场景: 多臂螺旋波
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.arms = 3  # 螺旋臂数量
        self.decay = 0.05

    def set_arms(self, arms: int) -> None:
        """设置螺旋臂数量"""
        self.arms = max(1, min(10, arms))

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用螺旋波"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        cr, cc = self.params.center
        x = np.arange(cols)
        y = np.arange(rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 转换到极坐标
        R = np.sqrt((X - cc) ** 2 + (Y - cr) ** 2)
        Theta = np.arctan2(Y - cr, X - cc)

        # 归一化
        max_r = np.sqrt(cr ** 2 + cc ** 2)
        r_norm = R / (max_r + 1)

        # 螺旋波
        Z = np.sin(self.arms * Theta + r_norm - 2 * np.pi * time) * np.exp(-self.decay * r_norm)

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class InterferencePatternFunction(WindFieldFunction):
    """干涉图样函数

    公式: z = sin(r1 - t) + sin(r2 - t)
    适用场景: 双波源干涉
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        # 两个波源的位置（相对于中心的偏移）
        self.source1_offset = (-5, 0)
        self.source2_offset = (5, 0)

    def set_sources(self, offset1: Tuple[float, float],
                    offset2: Tuple[float, float]) -> None:
        """设置两个波源的位置"""
        self.source1_offset = offset1
        self.source2_offset = offset2

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用干涉图样"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        cr, cc = self.params.center
        x = np.arange(cols)
        y = np.arange(rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 第一个波源
        s1x, s1y = self.source1_offset
        R1 = np.sqrt((X - cc - s1x) ** 2 + (Y - cr - s1y) ** 2)

        # 第二个波源
        s2x, s2y = self.source2_offset
        R2 = np.sqrt((X - cc - s2x) ** 2 + (Y - cr - s2y) ** 2)

        # 归一化距离
        max_r = np.sqrt(cr ** 2 + cc ** 2)
        R1_norm = R1 / max_r * 5
        R2_norm = R2 / max_r * 5

        # 干涉
        Z1 = np.sin(R1_norm - time)
        Z2 = np.sin(R2_norm - time)
        Z = (Z1 + Z2) / 2

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class StandingWaveFunction(WindFieldFunction):
    """驻波函数

    公式: z = sin(x) * sin(y) * cos(t)
    适用场景: 二维驻波
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用驻波"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        # 归一化坐标到 [-π, π]
        x = np.linspace(-np.pi, np.pi, cols)
        y = np.linspace(-np.pi, np.pi, rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 驻波
        Z = np.sin(X) * np.sin(Y) * np.cos(time)

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


# ==================== 其他函数 ====================

class CheckerboardFunction(WindFieldFunction):
    """棋盘格函数

    公式: z = sin(x*size + t) * sin(y*size + t)
    适用场景: 周期性网格图案
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.size = 2.0  # 格子大小

    def set_size(self, size: float) -> None:
        """设置格子大小"""
        self.size = max(0.5, size)

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用棋盘格"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        # 归一化坐标
        x = np.linspace(-2 * np.pi, 2 * np.pi, cols)
        y = np.linspace(-2 * np.pi, 2 * np.pi, rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 棋盘格
        Z = np.sin(X * self.size + time) * np.sin(Y * self.size + time)

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class NoiseFieldFunction(WindFieldFunction):
    """噪声场函数

    使用简化的Perlin噪声模拟
    适用场景: 添加随机扰动
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.scale = 0.5
        self.octaves = 3

    def set_scale(self, scale: float) -> None:
        """设置噪声尺度"""
        self.scale = max(0.1, min(2.0, scale))

    def apply(self, grid_data: np.ndarray, time: float = 0.0,
              seed: Optional[int] = None) -> np.ndarray:
        """应用噪声场"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        if seed is not None:
            np.random.seed(seed)
        else:
            np.random.seed(int(time * 100) if time > 0 else 42)

        x = np.linspace(-5, 5, cols)
        y = np.linspace(-5, 5, rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 简化的噪声函数（多层正弦叠加）
        Z = np.zeros_like(X)
        for i in range(self.octaves):
            freq = self.scale * (2 ** i)
            amplitude = 1.0 / (2 ** i)
            phase = time * (i + 1) * 0.5 if time > 0 else 0
            Z += amplitude * np.sin(freq * X + phase) * np.cos(freq * Y)

        # 添加随机噪声
        noise = np.random.randn(*X.shape) * 0.1
        Z += noise

        # 归一化到 [0, 100]
        Z_min, Z_max = Z.min(), Z.max()
        if Z_max > Z_min:
            Z = (Z - Z_min) / (Z_max - Z_min) * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class PolynomialSurfaceFunction(WindFieldFunction):
    """多项式曲面函数

    公式: z = (x³ - 3xy²) / 10 (猴鞍面)
    适用场景: 数学曲面
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()
        self.order = 3  # 多项式阶数

    def set_order(self, order: int) -> None:
        """设置多项式阶数"""
        self.order = max(1, min(3, order))

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用多项式曲面"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        # 归一化坐标到 [-2, 2]
        x = np.linspace(-2, 2, cols)
        y = np.linspace(-2, 2, rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        if self.order == 1:
            # 线性函数
            Z = 0.5 * (X + Y) * np.cos(time) if time > 0 else 0.5 * (X + Y)
        elif self.order == 2:
            # 二次函数（抛物面）
            R2 = X ** 2 + Y ** 2
            Z = (R2 / 8 - 1) * np.sin(time) if time > 0 else (R2 / 8 - 1)
        else:
            # 三次函数（猴鞍面）
            Z = (X ** 3 - 3 * X * Y ** 2) / 10 * np.sin(time) if time > 0 else (X ** 3 - 3 * X * Y ** 2) / 10

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


class SaddlePointFunction(WindFieldFunction):
    """鞍点函数

    公式: z = (x² - y²) / 5
    适用场景: 鞍形点分布
    """

    def __init__(self, params: Optional[FunctionParams] = None):
        self.params = params or FunctionParams()

    def apply(self, grid_data: np.ndarray, time: float = 0.0) -> np.ndarray:
        """应用鞍点分布"""
        self.validate_grid(grid_data)
        rows, cols = grid_data.shape

        # 归一化坐标到 [-3, 3]
        x = np.linspace(-3, 3, cols)
        y = np.linspace(-3, 3, rows)
        X, Y = np.meshgrid(x, y, indexing='xy')

        # 鞍点
        Z = (X ** 2 - Y ** 2) / 5 * np.cos(time) if time > 0 else (X ** 2 - Y ** 2) / 5

        # 归一化到 [0, 100]
        Z = (Z + 1) / 2 * 100 * (self.params.amplitude / 100.0)

        return self.normalize(Z)


# ==================== 函数工厂 ====================

class WindFieldFunctionFactory:
    """风场函数工厂

    提供12种预定义函数模板的统一访问接口
    """

    # 函数类型映射
    FUNCTIONS = {
        'simple_wave': SimpleWaveFunction,
        'radial_wave': RadialWaveFunction,
        'gaussian': GaussianFunction,
        'gaussian_packet': GaussianWavePacketFunction,
        'standing_wave': StandingWaveFunction,
        'linear_gradient': LinearGradientFunction,
        'radial_gradient': RadialGradientFunction,
        'circular_gradient': CircularGradientFunction,
        'spiral_wave': SpiralWaveFunction,
        'interference': InterferencePatternFunction,
        'checkerboard': CheckerboardFunction,
        'noise_field': NoiseFieldFunction,
        'polynomial_surface': PolynomialSurfaceFunction,
        'saddle_point': SaddlePointFunction,
    }

    # 函数分类
    CATEGORIES = {
        '基础波形': ['simple_wave', 'radial_wave', 'standing_wave'],
        '高斯函数': ['gaussian', 'gaussian_packet'],
        '渐变图案': ['linear_gradient', 'circular_gradient', 'radial_gradient'],
        '复杂波场': ['spiral_wave', 'interference', 'checkerboard', 'noise_field'],
        '数学曲面': ['polynomial_surface', 'saddle_point'],
    }

    # 函数描述
    DESCRIPTIONS = {
        'simple_wave': '简单波动 - sin(x) * cos(y + t)',
        'radial_wave': '径向波 - 从中心向外扩散',
        'gaussian': '高斯分布 - 中心集中衰减',
        'gaussian_packet': '高斯波包 - 移动的波包',
        'standing_wave': '驻波 - 二维驻波振动',
        'linear_gradient': '线性渐变 - 对角线方向',
        'radial_gradient': '径向渐变 - 同心圆条纹',
        'circular_gradient': '圆形渐变 - 从中心向外扩散',
        'spiral_wave': '螺旋波 - 多臂螺旋图案',
        'interference': '干涉图样 - 双波源干涉',
        'checkerboard': '棋盘格 - 周期性网格',
        'noise_field': '噪声场 - 随机扰动',
        'polynomial_surface': '多项式曲面 - 数学曲面',
        'saddle_point': '鞍点 - 鞍形分布',
    }

    @classmethod
    def create(cls, function_type: str, params: Optional[FunctionParams] = None) -> WindFieldFunction:
        """
        创建函数实例

        Args:
            function_type: 函数类型名称
            params: 函数参数

        Returns:
            函数实例

        Raises:
            ValueError: 未知函数类型
        """
        if function_type not in cls.FUNCTIONS:
            raise ValueError(
                f"未知函数类型: {function_type}. "
                f"可用类型: {list(cls.FUNCTIONS.keys())}"
            )

        return cls.FUNCTIONS[function_type](params)

    @classmethod
    def get_available_functions(cls) -> list:
        """获取所有可用函数列表"""
        return list(cls.FUNCTIONS.keys())

    @classmethod
    def get_functions_by_category(cls, category: str) -> list:
        """按分类获取函数列表"""
        return cls.CATEGORIES.get(category, [])

    @classmethod
    def get_all_categories(cls) -> list:
        """获取所有分类"""
        return list(cls.CATEGORIES.keys())

    @classmethod
    def get_description(cls, function_type: str) -> str:
        """获取函数描述"""
        return cls.DESCRIPTIONS.get(function_type, "无描述")


# ==================== 导出接口 ====================

# 导出所有函数类
__all__ = [
    # 函数类
    'SimpleWaveFunction',
    'RadialWaveFunction',
    'GaussianFunction',
    'GaussianWavePacketFunction',
    'StandingWaveFunction',
    'LinearGradientFunction',
    'RadialGradientFunction',
    'CircularGradientFunction',
    'SpiralWaveFunction',
    'InterferencePatternFunction',
    'CheckerboardFunction',
    'NoiseFieldFunction',
    'PolynomialSurfaceFunction',
    'SaddlePointFunction',
    # 工厂类
    'WindFieldFunctionFactory',
    # 参数类
    'FunctionParams',
]


if __name__ == "__main__":
    # 测试代码
    import matplotlib.pyplot as plt

    # 创建测试网格
    grid_data = np.zeros((40, 40))

    # 测试高斯函数
    gaussian = GaussianFunction()
    result = gaussian.apply(grid_data, sigma=5.0)

    # 可视化
    plt.figure(figsize=(10, 8))
    plt.imshow(result.T, cmap='jet', origin='lower', vmin=0, vmax=100)
    plt.colorbar(label='转速 %')
    plt.title('高斯分布示例')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()

    # 打印所有可用函数
    print("可用函数类型:")
    for func_type in WindFieldFunctionFactory.get_available_functions():
        desc = WindFieldFunctionFactory.get_description(func_type)
        print(f"  - {func_type}: {desc}")
