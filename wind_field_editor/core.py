# -*- coding: utf-8 -*-
"""
风场编辑器 - 核心模块

提供风场数据管理和编辑的核心功能

创建时间: 2024-01-03
作者: Wind Field Editor Team
版本: 2.0.0

修改历史:
    2024-01-03 [v2.0.0] 重大更新
        - 集成12种数学函数模板（从fan_con项目学习）
        - 添加函数应用接口
        - 优化羽化算法
        - 改进撤销/重做机制
    2024-01-03 [v1.0.0] 初始版本
        - 基础编辑功能
        - 选择、笔刷、圆形工具
        - 撤销/重做支持

依赖:
    - numpy >= 1.19.0
    - typing (Python 3.7+)

主要类:
    - EditMode: 编辑模式枚举
    - FanCell: 风扇单元格数据
    - WindFieldData: 风场数据容器
    - WindFieldEditor: 核心编辑器类
"""

import numpy as np
from typing import Set, Tuple, Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ==================== 枚举类型 ====================

class EditMode(Enum):
    """编辑模式枚举"""
    SELECTION = "点选模式"
    BRUSH = "笔刷模式"
    CIRCLE = "圆形工具模式"
    LINE = "直线工具模式"
    FUNCTION = "函数模式"


# ==================== 数据类 ====================

@dataclass
class FanCell:
    """
    风扇单元格数据

    属性:
        row: 行索引
        col: 列索引
        value: 转速百分比 (0.0-100.0)
        is_selected: 是否选中
    """
    row: int
    col: int
    value: float = 0.0  # 0.0 - 100.0 (转速百分比)
    is_selected: bool = False

    @property
    def fan_id(self) -> str:
        """获取风扇ID (格式: XxxxYyyy)"""
        return f"X{self.col:03d}Y{self.row:03d}"

    @property
    def rpm(self, max_rpm: int = 17000) -> int:
        """获取实际转速"""
        return int(self.value / 100.0 * max_rpm)


@dataclass
class WindFieldData:
    """
    风场数据容器

    属性:
        grid_data: 网格数据 (转速百分比)
        max_rpm: 最大转速
        max_time: 最大时间
        time_resolution: 时间分辨率
        metadata: 元数据字典
    """
    grid_data: np.ndarray
    max_rpm: int = 17000
    max_time: float = 10.0
    time_resolution: float = 0.1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        # 确保metadata不为None
        if self.metadata is None:
            self.metadata = {}

    @property
    def shape(self) -> Tuple[int, int]:
        """获取网格形状"""
        return self.grid_data.shape

    @property
    def grid_dim(self) -> int:
        """获取网格维度"""
        return self.grid_data.shape[0]

    def get_rpm_data(self) -> np.ndarray:
        """
        获取RPM数据

        Returns:
            RPM数据数组 (整数)
        """
        return (self.grid_data / 100.0 * self.max_rpm).astype(int)

    def get_time_series_data(self) -> Dict[str, Any]:
        """
        生成时间序列数据

        Returns:
            包含时间点、RPM数据等的字典
        """
        num_time_points = int(self.max_time / self.time_resolution) + 1
        time_points = np.linspace(0, self.max_time, num_time_points)
        rpm_data = np.tile(self.get_rpm_data(), (num_time_points, 1, 1))

        return {
            'time_points': time_points,
            'time_resolution': self.time_resolution,
            'max_time': self.max_time,
            'max_rpm': self.max_rpm,
            'grid_shape': self.grid_data.shape,
            'rpm_data': rpm_data,
            'metadata': self.metadata
        }


# ==================== 核心编辑器类 ====================

class WindFieldEditor:
    """
    风场编辑器核心类

    这是风场编辑系统的主要类，提供以下功能：
    - 管理风扇阵列数据 (40x40网格)
    - 提供选择和编辑操作
    - 支持撤销/重做 (最多50步)
    - 羽化效果处理
    - 函数模板集成

    示例:
        >>> editor = WindFieldEditor(grid_dim=40, max_rpm=17000)
        >>> editor.set_cell_value(10, 10, 50.0)
        >>> editor.select_all()
        >>> editor.apply_speed_to_selection(80.0, feather=True, feather_value=3)
        >>> data = editor.to_wind_field_data()
    """

    def __init__(self, grid_dim: int = 40, max_rpm: int = 17000):
        """
        初始化风场编辑器

        Args:
            grid_dim: 网格维度 (默认40x40)
            max_rpm: 最大转速 (默认17000 RPM)
        """
        self.grid_dim = grid_dim
        self.max_rpm = max_rpm
        self._creation_time = datetime.now()

        # 初始化网格数据
        self.grid_data = np.zeros((grid_dim, grid_dim), dtype=float)

        # 选择集
        self.selected_cells: Set[Tuple[int, int]] = set()

        # 编辑历史 (用于撤销/重做)
        self.history: List[np.ndarray] = []
        self.history_index = -1
        self.max_history = 50

        # 当前编辑模式
        self.current_mode = EditMode.SELECTION

        # 统计信息
        self._stats = {
            'edit_count': 0,
            'undo_count': 0,
            'redo_count': 0
        }

    # ==================== 数据管理 ====================

    def get_cell_value(self, row: int, col: int) -> float:
        """
        获取单元格值

        Args:
            row: 行索引
            col: 列索引

        Returns:
            单元格转速百分比 (0-100)
        """
        return self.grid_data[row, col]

    def set_cell_value(self, row: int, col: int, value: float) -> None:
        """
        设置单元格值

        Args:
            row: 行索引
            col: 列索引
            value: 转速值 (会自动裁剪到0-100范围)
        """
        value = max(0.0, min(100.0, value))
        self.grid_data[row, col] = value

    def get_selected_cells(self) -> Set[Tuple[int, int]]:
        """获取选中的单元格坐标集合（副本）"""
        return self.selected_cells.copy()

    def clear_selection(self) -> None:
        """清除所有选择"""
        self.selected_cells.clear()

    def select_all(self) -> None:
        """全选"""
        for r in range(self.grid_dim):
            for c in range(self.grid_dim):
                self.selected_cells.add((r, c))

    def invert_selection(self) -> None:
        """反选"""
        new_selection = set()
        for r in range(self.grid_dim):
            for c in range(self.grid_dim):
                if (r, c) not in self.selected_cells:
                    new_selection.add((r, c))
        self.selected_cells = new_selection

    def reset_all_to_zero(self) -> None:
        """
        将所有风扇转速重置为0并清除选择
        此操作支持撤销
        """
        self._save_state()
        self.grid_data.fill(0)
        self.selected_cells.clear()
        self._stats['edit_count'] += 1

    # ==================== 编辑操作 ====================

    def apply_speed_to_selection(self, speed: float, feather: bool = False,
                                 feather_value: int = 0) -> int:
        """
        应用转速到选中区域

        Args:
            speed: 转速百分比 (0-100)
            feather: 是否启用羽化
            feather_value: 羽化层数 (1-10)

        Returns:
            受影响的单元格数量

        示例:
            >>> editor = WindFieldEditor()
            >>> editor.selected_cells = {(10, 10), (10, 11)}
            >>> count = editor.apply_speed_to_selection(75.0, feather=True, feather_value=3)
            >>> print(f"影响了 {count} 个风扇")
        """
        if not self.selected_cells:
            return 0

        self._save_state()

        # 应用基础转速
        for row, col in self.selected_cells:
            self.set_cell_value(row, col, speed)

        # 应用羽化
        if feather and feather_value > 0:
            self._apply_feathering(self.selected_cells, speed, feather_value)

        self._stats['edit_count'] += 1
        return len(self.selected_cells)

    def apply_brush(self, center_row: int, center_col: int,
                    brush_size: int, brush_value: float,
                    feather: bool = False, feather_value: int = 0) -> int:
        """
        应用笔刷

        Args:
            center_row: 中心行
            center_col: 中心列
            brush_size: 笔刷直径 (格数)
            brush_value: 笔刷值
            feather: 是否羽化
            feather_value: 羽化层数

        Returns:
            受影响的单元格数量
        """
        self._save_state()

        radius = brush_size / 2.0
        affected = []

        for r in range(self.grid_dim):
            for c in range(self.grid_dim):
                dist = ((r - center_row) ** 2 + (c - center_col) ** 2) ** 0.5
                if dist <= radius:
                    self.set_cell_value(r, c, brush_value)
                    affected.append((r, c))

        if feather and feather_value > 0:
            self._apply_feathering(set(affected), brush_value, feather_value)

        self._stats['edit_count'] += 1
        return len(affected)

    def apply_circle_selection(self, center_row: int, center_col: int,
                               radius: float, modifier: str = None) -> int:
        """
        应用圆形选择

        Args:
            center_row: 圆心行
            center_col: 圆心列
            radius: 半径 (格数)
            modifier: 修饰键 ('shift', 'ctrl', None)
                     - None: 替换当前选择
                     - 'shift': 添加到当前选择
                     - 'ctrl': 反选模式

        Returns:
            选中的单元格数量
        """
        if modifier != 'shift' and modifier != 'ctrl':
            self.clear_selection()

        new_selection = set()
        for r in range(self.grid_dim):
            for c in range(self.grid_dim):
                dist = ((r - center_row) ** 2 + (c - center_col) ** 2) ** 0.5
                if dist <= radius:
                    if modifier == 'ctrl' and (r, c) in self.selected_cells:
                        continue  # Ctrl模式: 跳过已选中的
                    new_selection.add((r, c))

        if modifier == 'ctrl':
            # 反选模式
            for cell in new_selection:
                if cell in self.selected_cells:
                    self.selected_cells.remove(cell)
                else:
                    self.selected_cells.add(cell)
        else:
            # 普通或Shift模式
            self.selected_cells.update(new_selection)

        return len(self.selected_cells)

    # ==================== 函数集成 (从fan_con学习) ====================

    def apply_function(self, function_type: str, params: Optional[Dict] = None,
                      time: float = 0.0) -> bool:
        """
        应用数学函数到风场

        Args:
            function_type: 函数类型 ('gaussian', 'radial_wave', 'linear_gradient' 等)
            params: 函数参数字典
            time: 时间参数 (用于动态函数)

        Returns:
            是否成功应用

        支持的函数类型:
            - gaussian: 高斯分布
            - radial_wave: 径向波
            - linear_gradient: 线性渐变
            - radial_gradient: 径向渐变
            - spiral_wave: 螺旋波
            - interference: 干涉图样
            - standing_wave: 驻波
            - checkerboard: 棋盘格
            - noise: 噪声场
            - polynomial: 多项式曲面
            - saddle: 鞍点
            - gaussian_packet: 高斯波包
        """
        try:
            from .functions import WindFieldFunctionFactory, FunctionParams

            # 创建参数
            function_params = FunctionParams()
            if params:
                if 'center' in params:
                    function_params.center = params['center']
                if 'amplitude' in params:
                    function_params.amplitude = params['amplitude']

            # 创建并应用函数
            func = WindFieldFunctionFactory.create(function_type, function_params)
            self._save_state()
            self.grid_data = func.apply(self.grid_data, time=time)

            self._stats['edit_count'] += 1
            return True

        except Exception as e:
            print(f"应用函数失败: {e}")
            return False

    def get_available_functions(self) -> Dict[str, List[str]]:
        """
        获取所有可用的函数类型

        Returns:
            按分类组织的函数字典
        """
        from .functions import WindFieldFunctionFactory

        return {
            'all': WindFieldFunctionFactory.get_available_functions(),
            'categories': WindFieldFunctionFactory.get_all_categories(),
        }

    # ==================== 羽化效果 ====================

    def _apply_feathering(self, source_cells: Set[Tuple[int, int]],
                          base_value: float, feather_value: int) -> None:
        """
        应用羽化效果

        羽化算法:
            第1层: 100% 基础值
            第2层: (n-1)/n 基础值
            第3层: (n-2)/n 基础值
            ...
            第n层: 1/n 基础值

        Args:
            source_cells: 源单元格集合
            base_value: 基础值
            feather_value: 羽化层数 (1-10)
        """
        if not source_cells or feather_value <= 0:
            return

        processed = set(source_cells)
        current_layer = list(source_cells)

        for layer in range(1, feather_value + 1):
            next_layer = set()
            # 计算当前层的值
            layer_value = base_value * (feather_value - layer) / feather_value
            layer_value = max(0.0, layer_value)

            if not current_layer:
                break

            for row, col in current_layer:
                # 检查四个方向 (上下左右)
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = row + dr, col + dc

                    # 边界检查
                    if 0 <= nr < self.grid_dim and 0 <= nc < self.grid_dim:
                        if (nr, nc) not in processed:
                            current_val = self.get_cell_value(nr, nc)
                            # 只有当羽化值大于当前值时才更新
                            if layer_value > current_val:
                                self.set_cell_value(nr, nc, layer_value)
                            next_layer.add((nr, nc))
                            processed.add((nr, nc))

            current_layer = list(next_layer)

    # ==================== 撤销/重做 ====================

    def _save_state(self) -> None:
        """保存当前状态到历史"""
        # 如果在历史中间位置，删除后面的历史
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        # 保存当前状态
        self.history.append(np.copy(self.grid_data))
        self.history_index += 1

        # 限制历史长度
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1

    def undo(self) -> bool:
        """
        撤销上一次操作

        Returns:
            是否成功撤销
        """
        if self.history_index > 0:
            self.history_index -= 1
            self.grid_data = np.copy(self.history[self.history_index])
            self._stats['undo_count'] += 1
            return True
        return False

    def redo(self) -> bool:
        """
        重做上一次撤销的操作

        Returns:
            是否成功重做
        """
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.grid_data = np.copy(self.history[self.history_index])
            self._stats['redo_count'] += 1
            return True
        return False

    def can_undo(self) -> bool:
        """是否可以撤销"""
        return self.history_index > 0

    def can_redo(self) -> bool:
        """是否可以重做"""
        return self.history_index < len(self.history) - 1

    def clear_history(self) -> None:
        """清除历史记录"""
        self.history = []
        self.history_index = -1

    # ==================== 数据导出 ====================

    def to_wind_field_data(self) -> WindFieldData:
        """
        导出为WindFieldData对象

        Returns:
            WindFieldData对象
        """
        return WindFieldData(
            grid_data=np.copy(self.grid_data),
            max_rpm=self.max_rpm,
            max_time=10.0,
            time_resolution=0.1,
            metadata={
                'grid_dim': self.grid_dim,
                'selected_count': len(self.selected_cells),
                'creation_time': self._creation_time.isoformat(),
                'edit_count': self._stats['edit_count'],
            }
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        获取数据摘要

        Returns:
            包含统计信息的字典
        """
        selected_values = [self.grid_data[r, c]
                          for r, c in self.selected_cells]
        avg_speed = sum(selected_values) / len(selected_values) if selected_values else 0

        return {
            'grid_dim': self.grid_dim,
            'total_cells': self.grid_dim * self.grid_dim,
            'selected_count': len(self.selected_cells),
            'avg_speed': avg_speed,
            'max_rpm': self.max_rpm,
            'current_mode': self.current_mode.value,
            'edit_count': self._stats['edit_count'],
            'undo_count': self._stats['undo_count'],
            'redo_count': self._stats['redo_count'],
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取详细统计信息

        Returns:
            统计信息字典
        """
        flat_data = self.grid_data.flatten()

        return {
            'min': float(flat_data.min()),
            'max': float(flat_data.max()),
            'mean': float(flat_data.mean()),
            'std': float(flat_data.std()),
            'sum': float(flat_data.sum()),
            'non_zero_count': int(np.count_nonzero(flat_data)),
        }


# ==================== 导出接口 ====================

__all__ = [
    'EditMode',
    'FanCell',
    'WindFieldData',
    'WindFieldEditor',
]
