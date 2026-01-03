# -*- coding: utf-8 -*-
"""
风场编辑器 - 模块初始化

提供风场编辑功能的核心接口

创建时间: 2024-01-03
作者: Wind Field Editor Team
版本: 2.0.0

修改历史:
    2024-01-03 [v2.0.0] 重大更新
        - 集成12种数学函数模板
        - 新增functions模块
        - 更新所有子模块
    2024-01-03 [v1.0.0] 初始版本
        - 核心编辑器
        - 编辑工具
        - 工具函数

依赖:
    - numpy >= 1.19.0
"""

from .core import (
    EditMode,
    FanCell,
    WindFieldData,
    WindFieldEditor,
)

from .tools import (
    Tool,
    ToolType,
    SelectionTool,
    BrushTool,
    CircleTool,
    LineTool,
    FunctionTool,
    BrushSettings,
    SelectionSettings,
    CircleSettings,
    LineSettings,
    FunctionSettings,
)

from .functions import (
    WindFieldFunctionFactory,
    WindFieldFunction,
    FunctionParams,
    SimpleWaveFunction,
    RadialWaveFunction,
    GaussianFunction,
    GaussianWavePacketFunction,
    StandingWaveFunction,
    LinearGradientFunction,
    RadialGradientFunction,
    CircularGradientFunction,
    SpiralWaveFunction,
    InterferencePatternFunction,
    CheckerboardFunction,
    NoiseFieldFunction,
    PolynomialSurfaceFunction,
    SaddlePointFunction,
)

from .config import (
    GRID_DIM,
    MODULE_DIM,
    DEFAULT_MAX_RPM,
    DEFAULT_MAX_TIME,
    COLOR_MAP,
)

# 版本信息
__version__ = '2.0.0'
__author__ = 'Wind Field Editor Team'

# 导出接口 - 按使用频率排序
__all__ = [
    # 核心类
    'WindFieldEditor',
    'WindFieldData',
    'EditMode',
    'FanCell',

    # 函数工厂
    'WindFieldFunctionFactory',
    'FunctionParams',

    # 函数类 (按类别分组)
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

    # 编辑工具
    'Tool',
    'ToolType',
    'SelectionTool',
    'BrushTool',
    'CircleTool',
    'LineTool',
    'FunctionTool',

    # 工具设置
    'BrushSettings',
    'SelectionSettings',
    'CircleSettings',
    'LineSettings',
    'FunctionSettings',

    # 配置常量
    'GRID_DIM',
    'MODULE_DIM',
    'DEFAULT_MAX_RPM',
    'DEFAULT_MAX_TIME',
    'COLOR_MAP',
]


# 便捷函数
def create_editor(grid_dim: int = 40, max_rpm: int = 17000) -> WindFieldEditor:
    """
    创建风场编辑器实例

    Args:
        grid_dim: 网格维度 (默认40x40)
        max_rpm: 最大转速 (默认17000)

    Returns:
        WindFieldEditor实例

    示例:
        >>> editor = create_editor()
        >>> editor.apply_function('gaussian')
        >>> data = editor.to_wind_field_data()
    """
    return WindFieldEditor(grid_dim=grid_dim, max_rpm=max_rpm)


def list_functions() -> dict:
    """
    列出所有可用的函数类型

    Returns:
        函数分类字典

    示例:
        >>> funcs = list_functions()
        >>> print(funcs['categories'])
        ['基础波形', '高斯函数', '渐变图案', '复杂波场', '数学曲面']
    """
    from .functions import WindFieldFunctionFactory

    return {
        'all': WindFieldFunctionFactory.get_available_functions(),
        'categories': WindFieldFunctionFactory.get_all_categories(),
        'descriptions': {
            name: WindFieldFunctionFactory.get_description(name)
            for name in WindFieldFunctionFactory.get_available_functions()
        }
    }


# 模块信息
def get_version() -> str:
    """获取模块版本"""
    return __version__


def get_info() -> dict:
    """获取模块信息"""
    return {
        'name': 'wind_field_editor',
        'version': __version__,
        'author': __author__,
        'description': '风场编辑器 - 支持40x40风扇阵列的风场编辑和管理',
        'features': [
            '12种数学函数模板',
            '选择、笔刷、圆形编辑工具',
            '羽化效果',
            '撤销/重做',
            '数据导出',
        ],
    }
