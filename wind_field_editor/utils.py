# -*- coding: utf-8 -*-
"""
风场编辑工具函数

提供颜色转换、数学计算等辅助功能
"""
import numpy as np
from typing import Tuple, List
from . import config


# ==================== 颜色相关函数 ====================

def value_to_color(value: float, min_val: float = 0.0,
                   max_val: float = 100.0) -> Tuple[int, int, int]:
    """
    将转速值转换为颜色RGB

    Args:
        value: 转速值 (0-100)
        min_val: 最小值
        max_val: 最大值

    Returns:
        RGB颜色元组 (r, g, b)
    """
    # 裁剪到有效范围
    value = max(min_val, min(max_val, value))

    # 计算颜色索引
    color_index = int(((value - min_val) / (max_val - min_val)) *
                      (len(config.COLOR_MAP) - 1))

    return config.COLOR_MAP[color_index]


def get_contrasting_text_color(bg_color: Tuple[int, int, int]) -> str:
    """
    根据背景色选择对比文本颜色

    Args:
        bg_color: 背景RGB颜色

    Returns:
        'black' 或 'white'
    """
    r, g, b = bg_color
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return 'black' if luminance > config.LUMINANCE_THRESHOLD else 'white'


# ==================== 几何计算函数 ====================

def distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """计算两点之间的欧氏距离"""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def rect_intersects_circle(rect_center: Tuple[float, float],
                           rect_size: Tuple[float, float],
                           circle_center: Tuple[float, float],
                           circle_radius: float) -> bool:
    """
    检查矩形是否与圆形相交

    Args:
        rect_center: 矩形中心 (x, y)
        rect_size: 矩形尺寸 (width, height)
        circle_center: 圆心 (x, y)
        circle_radius: 圆半径

    Returns:
        是否相交
    """
    rx, ry = rect_center
    rw, rh = rect_size[0] / 2, rect_size[1] / 2
    cx, cy = circle_center

    # 计算圆心到矩形的距离
    dx = abs(cx - rx)
    dy = abs(cy - ry)

    # 圆心在矩形内部
    if dx <= rw and dy <= rh:
        return True

    # 圆心在角落区域
    if dx > rw and dy > rh:
        corner_dist_sq = (dx - rw) ** 2 + (dy - rh) ** 2
        return corner_dist_sq <= circle_radius ** 2

    # 圆心在边缘区域
    if dx > rw:
        return (dx - rw) <= circle_radius
    else:
        return (dy - rh) <= circle_radius


def point_in_circle(point: Tuple[int, int],
                    circle_center: Tuple[int, int],
                    radius: float) -> bool:
    """检查点是否在圆内"""
    return distance(point, circle_center) <= radius


def point_in_rect(point: Tuple[int, int],
                  rect_top_left: Tuple[int, int],
                  rect_size: Tuple[int, int]) -> bool:
    """检查点是否在矩形内"""
    x, y = point
    rx, ry = rect_top_left
    rw, rh = rect_size
    return rx <= x <= rx + rw and ry <= y <= ry + rh


# ==================== 网格相关函数 ====================

def get_module_cells(row: int, col: int, module_dim: int = 4) -> List[Tuple[int, int]]:
    """
    获取指定单元格所属模块的所有单元格

    Args:
        row: 行索引
        col: 列索引
        module_dim: 模块维度

    Returns:
        模块内所有单元格坐标列表
    """
    module_row_start = (row // module_dim) * module_dim
    module_col_start = (col // module_dim) * module_dim

    cells = []
    for r in range(module_row_start, module_row_start + module_dim):
        for c in range(module_col_start, module_col_start + module_dim):
            cells.append((r, c))

    return cells


def get_circle_cells(center: Tuple[int, int], radius: float,
                     grid_dim: int) -> List[Tuple[int, int]]:
    """
    获取圆形区域内所有单元格

    Args:
        center: 圆心 (row, col)
        radius: 半径
        grid_dim: 网格维度

    Returns:
        圆形内所有单元格坐标列表
    """
    cells = []
    cr, cc = center

    # 计算边界框
    r_min = max(0, int(cr - radius - 1))
    r_max = min(grid_dim, int(cr + radius + 1))
    c_min = max(0, int(cc - radius - 1))
    c_max = min(grid_dim, int(cc + radius + 1))

    for r in range(r_min, r_max):
        for c in range(c_min, c_max):
            if point_in_circle((r, c), center, radius):
                cells.append((r, c))

    return cells


def get_line_cells(start: Tuple[int, int], end: Tuple[int, int],
                   grid_dim: int) -> List[Tuple[int, int]]:
    """
    使用Bresenham算法获取直线上的所有单元格

    Args:
        start: 起点 (row, col)
        end: 终点 (row, col)
        grid_dim: 网格维度

    Returns:
        直线上所有单元格坐标列表
    """
    r1, c1 = start
    r2, c2 = end

    # 确保在网格范围内
    r1 = max(0, min(grid_dim - 1, r1))
    c1 = max(0, min(grid_dim - 1, c1))
    r2 = max(0, min(grid_dim - 1, r2))
    c2 = max(0, min(grid_dim - 1, c2))

    cells = []

    # Bresenham直线算法
    dr = abs(r2 - r1)
    dc = abs(c2 - c1)
    sr = 1 if r1 < r2 else -1
    sc = 1 if c1 < c2 else -1
    err = dr - dc

    r, c = r1, c1
    while True:
        cells.append((r, c))
        if r == r2 and c == c2:
            break

        e2 = 2 * err
        if e2 > -dc:
            err -= dc
            r += sr
        if e2 < dr:
            err += dr
            c += sc

    return cells


# ==================== 数据转换函数 ====================

def percent_to_rpm(percent: float, max_rpm: int = 17000) -> int:
    """将百分比转换为RPM"""
    return int(percent / 100.0 * max_rpm)


def rpm_to_percent(rpm: int, max_rpm: int = 17000) -> float:
    """将RPM转换为百分比"""
    return (rpm / max_rpm) * 100.0


def clamp_value(value: float, min_val: float = 0.0,
                max_val: float = 100.0) -> float:
    """将值裁剪到指定范围"""
    return max(min_val, min(max_val, value))


# ==================== 统计函数 ====================

def calculate_stats(values: List[float]) -> dict:
    """
    计算数据统计信息

    Args:
        values: 数值列表

    Returns:
        包含统计信息的字典
    """
    if not values:
        return {
            'count': 0,
            'min': 0.0,
            'max': 0.0,
            'avg': 0.0,
            'sum': 0.0
        }

    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'avg': sum(values) / len(values),
        'sum': sum(values)
    }


def normalize_grid(grid: np.ndarray) -> np.ndarray:
    """
    归一化网格数据到0-100范围

    Args:
        grid: 输入网格

    Returns:
        归一化后的网格
    """
    min_val = grid.min()
    max_val = grid.max()

    if max_val == min_val:
        return np.zeros_like(grid)

    normalized = (grid - min_val) / (max_val - min_val) * 100
    return normalized


# ==================== 文件名生成函数 ====================

def generate_fan_id(row: int, col: int) -> str:
    """
    生成风扇ID

    Args:
        row: 行索引
        col: 列索引

    Returns:
        风扇ID字符串 (格式: XxxxYyyy)
    """
    return f"X{col:03d}Y{row:03d}"


def parse_fan_id(fan_id: str) -> Tuple[int, int]:
    """
    解析风扇ID

    Args:
        fan_id: 风扇ID字符串 (格式: XxxxYyyy)

    Returns:
        (row, col) 元组
    """
    # 假设格式为 X123Y456
    parts = fan_id.upper().replace('X', ' ').replace('Y', ' ').split()
    return int(parts[1]), int(parts[0])
