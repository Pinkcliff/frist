# -*- coding: utf-8 -*-
"""
风场编辑工具模块

提供各种编辑工具的实现
"""
from abc import ABC, abstractmethod
from typing import Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum


class ToolType(Enum):
    """工具类型枚举"""
    SELECTION = "选择工具"
    BRUSH = "笔刷工具"
    CIRCLE = "圆形工具"
    LINE = "直线工具"
    FUNCTION = "函数工具"


@dataclass
class ToolSettings:
    """工具设置基类"""
    enabled: bool = True


@dataclass
class BrushSettings(ToolSettings):
    """笔刷工具设置"""
    size: int = 5  # 笔刷直径
    value: float = 100.0  # 笔刷值
    feather_enabled: bool = False  # 是否羽化
    feather_value: int = 3  # 羽化层数


@dataclass
class SelectionSettings(ToolSettings):
    """选择工具设置"""
    value: float = 0.0  # 要设置的值
    feather_enabled: bool = False
    feather_value: int = 3


@dataclass
class CircleSettings(ToolSettings):
    """圆形工具设置"""
    center: Tuple[int, int] = (0, 0)  # 圆心
    radius: float = 0.0  # 半径
    value: float = 0.0  # 要设置的值
    feather_enabled: bool = False
    feather_value: int = 3


@dataclass
class LineSettings(ToolSettings):
    """直线工具设置"""
    start: Tuple[int, int] = (0, 0)  # 起点
    end: Tuple[int, int] = (0, 0)  # 终点
    value: float = 0.0  # 要设置的值


@dataclass
class FunctionSettings(ToolSettings):
    """函数工具设置"""
    function_type: str = "gaussian"  # 函数类型
    center: Tuple[int, int] = (20, 20)  # 中心
    sigma: float = 5.0  # 标准差
    amplitude: float = 100.0  # 幅度


class Tool(ABC):
    """工具基类"""

    def __init__(self, tool_type: ToolType):
        self.tool_type = tool_type
        self.is_active = False

    @abstractmethod
    def activate(self) -> None:
        """激活工具"""
        self.is_active = True

    @abstractmethod
    def deactivate(self) -> None:
        """停用工具"""
        self.is_active = False

    @abstractmethod
    def on_mouse_press(self, row: int, col: int, modifier: str = None) -> None:
        """鼠标按下事件"""
        pass

    @abstractmethod
    def on_mouse_move(self, row: int, col: int, modifier: str = None) -> None:
        """鼠标移动事件"""
        pass

    @abstractmethod
    def on_mouse_release(self, modifier: str = None) -> None:
        """鼠标释放事件"""
        pass


class SelectionTool(Tool):
    """选择工具"""

    def __init__(self):
        super().__init__(ToolType.SELECTION)
        self.settings = SelectionSettings()

    def activate(self) -> None:
        super().activate()

    def deactivate(self) -> None:
        super().deactivate()

    def on_mouse_press(self, row: int, col: int, modifier: str = None) -> None:
        """处理单击选择"""
        # 单击选择逻辑由编辑器处理
        pass

    def on_mouse_move(self, row: int, col: int, modifier: str = None) -> None:
        pass

    def on_mouse_release(self, modifier: str = None) -> None:
        pass

    def set_value(self, value: float) -> None:
        """设置要应用的值"""
        self.settings.value = value

    def set_feather(self, enabled: bool, value: int = 3) -> None:
        """设置羽化"""
        self.settings.feather_enabled = enabled
        self.settings.feather_value = value


class BrushTool(Tool):
    """笔刷工具"""

    def __init__(self):
        super().__init__(ToolType.BRUSH)
        self.settings = BrushSettings()
        self._is_drawing = False

    def activate(self) -> None:
        super().activate()

    def deactivate(self) -> None:
        super().deactivate()
        self._is_drawing = False

    def on_mouse_press(self, row: int, col: int, modifier: str = None) -> None:
        """开始绘制"""
        self._is_drawing = True

    def on_mouse_move(self, row: int, col: int, modifier: str = None) -> None:
        """绘制中"""
        if self._is_drawing:
            # 笔刷应用逻辑由编辑器处理
            pass

    def on_mouse_release(self, modifier: str = None) -> None:
        """结束绘制"""
        self._is_drawing = False

    def set_size(self, size: int) -> None:
        """设置笔刷大小"""
        self.settings.size = max(1, min(40, size))

    def set_value(self, value: float) -> None:
        """设置笔刷值"""
        self.settings.value = max(0.0, min(100.0, value))

    def set_feather(self, enabled: bool, value: int = 3) -> None:
        """设置羽化"""
        self.settings.feather_enabled = enabled
        self.settings.feather_value = max(1, min(10, value))


class CircleTool(Tool):
    """圆形工具"""

    def __init__(self):
        super().__init__(ToolType.CIRCLE)
        self.settings = CircleSettings()
        self._start_pos = None

    def activate(self) -> None:
        super().activate()

    def deactivate(self) -> None:
        super().deactivate()
        self._start_pos = None

    def on_mouse_press(self, row: int, col: int, modifier: str = None) -> None:
        """开始绘制圆"""
        self._start_pos = (row, col)
        self.settings.center = (row, col)

    def on_mouse_move(self, row: int, col: int, modifier: str = None) -> None:
        """更新圆半径"""
        if self._start_pos:
            dr = row - self._start_pos[0]
            dc = col - self._start_pos[1]
            self.settings.radius = (dr ** 2 + dc ** 2) ** 0.5

    def on_mouse_release(self, modifier: str = None) -> None:
        """完成圆形选择"""
        pass

    def set_value(self, value: float) -> None:
        """设置要应用的值"""
        self.settings.value = value

    def set_feather(self, enabled: bool, value: int = 3) -> None:
        """设置羽化"""
        self.settings.feather_enabled = enabled
        self.settings.feather_value = value


class LineTool(Tool):
    """直线工具"""

    def __init__(self):
        super().__init__(ToolType.LINE)
        self.settings = LineSettings()
        self._start_pos = None

    def activate(self) -> None:
        super().activate()

    def deactivate(self) -> None:
        super().deactivate()
        self._start_pos = None

    def on_mouse_press(self, row: int, col: int, modifier: str = None) -> None:
        """开始绘制直线"""
        self._start_pos = (row, col)
        self.settings.start = (row, col)

    def on_mouse_move(self, row: int, col: int, modifier: str = None) -> None:
        """更新直线终点"""
        if self._start_pos:
            self.settings.end = (row, col)

    def on_mouse_release(self, modifier: str = None) -> None:
        """完成直线选择"""
        pass

    def set_value(self, value: float) -> None:
        """设置要应用的值"""
        self.settings.value = value


class FunctionTool(Tool):
    """函数工具"""

    def __init__(self):
        super().__init__(ToolType.FUNCTION)
        self.settings = FunctionSettings()

    def activate(self) -> None:
        super().activate()

    def deactivate(self) -> None:
        super().deactivate()

    def on_mouse_press(self, row: int, col: int, modifier: str = None) -> None:
        """设置函数中心"""
        self.settings.center = (row, col)

    def on_mouse_move(self, row: int, col: int, modifier: str = None) -> None:
        pass

    def on_mouse_release(self, modifier: str = None) -> None:
        pass

    def set_function_type(self, func_type: str) -> None:
        """设置函数类型"""
        self.settings.function_type = func_type

    def set_sigma(self, sigma: float) -> None:
        """设置高斯函数标准差"""
        self.settings.sigma = sigma

    def set_amplitude(self, amplitude: float) -> None:
        """设置幅度"""
        self.settings.amplitude = amplitude

    def apply_gaussian(self, grid_data, center: Tuple[int, int],
                       sigma: float, amplitude: float) -> None:
        """应用高斯函数到网格"""
        import numpy as np

        rows, cols = grid_data.shape
        cr, cc = center

        # 创建网格坐标
        r_indices = np.arange(rows)
        c_indices = np.arange(cols)
        r_grid, c_grid = np.meshgrid(r_indices, c_indices, indexing='ij')

        # 计算高斯分布
        distance_sq = (r_grid - cr) ** 2 + (c_grid - cc) ** 2
        gaussian = amplitude * np.exp(-distance_sq / (2 * sigma ** 2))

        # 应用到网格
        np.maximum(grid_data, gaussian, out=grid_data)

    def get_available_functions(self) -> list:
        """获取可用的函数类型"""
        return [
            "gaussian",  # 高斯分布
            "linear",    # 线性分布
            "radial",    # 径向分布
            "wave",      # 波浪分布
        ]
