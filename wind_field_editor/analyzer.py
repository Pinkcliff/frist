# -*- coding: utf-8 -*-
"""
风场编辑器 - 点分析器模块

提供固定点时间序列分析功能（从fan_con学习）

创建时间: 2024-01-03
作者: Wind Field Editor Team
版本: 1.0.0

修改历史:
    2024-01-03 [v1.0.0] 初始版本
        - 从fan_con项目移植PointAnalyzer
        - 适配风场编辑器
        - 添加时间序列分析

依赖:
    - numpy >= 1.19.0
    - pandas >= 1.0.0 (可选，用于数据导出)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrackedPoint:
    """
    被追踪的点数据

    属性:
        row: 行索引
        col: 列索引
        label: 点的标签
        color: 可视化颜色
    """
    row: int
    col: int
    label: str = ""
    color: str = "red"

    def __post_init__(self):
        if not self.label:
            self.label = f"({self.row}, {self.col})"

    @property
    def position(self) -> Tuple[int, int]:
        """获取位置元组"""
        return (self.row, self.col)


class WindFieldAnalyzer:
    """
    风场点分析器

    用于分析和追踪风场中特定点的时间序列数据

    示例:
        >>> editor = WindFieldEditor()
        >>> analyzer = WindFieldAnalyzer(editor)
        >>> analyzer.add_point(20, 20, "中心点")
        >>> analyzer.add_point(10, 10, "左上")
        >>> series = analyzer.get_time_series(t_range=(0, 10))
    """

    def __init__(self, editor=None):
        """
        初始化分析器

        Args:
            editor: WindFieldEditor实例 (可选)
        """
        self.editor = editor
        self.tracked_points: Dict[str, TrackedPoint] = {}
        self._creation_time = datetime.now()

    # ==================== 点管理 ====================

    def add_point(self, row: int, col: int, label: str = "",
                  color: str = "red") -> None:
        """
        添加要分析的点

        Args:
            row: 行索引
            col: 列索引
            label: 点的标签
            color: 可视化颜色

        示例:
            >>> analyzer.add_point(20, 20, "中心点", "blue")
        """
        if not label:
            label = f"({row}, {col})"

        point = TrackedPoint(row=row, col=col, label=label, color=color)
        self.tracked_points[label] = point

    def remove_point(self, label: str) -> bool:
        """
        移除追踪点

        Args:
            label: 点的标签

        Returns:
            是否成功移除
        """
        if label in self.tracked_points:
            del self.tracked_points[label]
            return True
        return False

    def clear_points(self) -> None:
        """清除所有追踪点"""
        self.tracked_points.clear()

    def get_point(self, label: str) -> Optional[TrackedPoint]:
        """获取指定点"""
        return self.tracked_points.get(label)

    def get_all_points(self) -> List[TrackedPoint]:
        """获取所有追踪点"""
        return list(self.tracked_points.values())

    def get_point_count(self) -> int:
        """获取追踪点数量"""
        return len(self.tracked_points)

    # ==================== 时间序列分析 ====================

    def get_time_series(self, t_range: Tuple[float, float] = (0, 10),
                       num_points: int = 100,
                       function_type: str = 'gaussian',
                       function_params: Optional[Dict] = None) -> Dict[str, np.ndarray]:
        """
        获取所有追踪点的时间序列

        Args:
            t_range: 时间范围 (t_min, t_max)
            num_points: 时间点数量
            function_type: 函数类型
            function_params: 函数参数

        Returns:
            字典 {label: 时间序列数组}
        """
        from .functions import WindFieldFunctionFactory, FunctionParams

        time_points = np.linspace(t_range[0], t_range[1], num_points)
        result = {'time': time_points}

        # 创建参数
        params = FunctionParams()
        if function_params:
            if 'center' in function_params:
                params.center = function_params['center']
            if 'amplitude' in function_params:
                params.amplitude = function_params['amplitude']

        # 创建函数
        func = WindFieldFunctionFactory.create(function_type, params)

        # 为每个追踪点计算时间序列
        for label, point in self.tracked_points.items():
            values = []
            for t in time_points:
                # 创建单个点的网格
                point_grid = np.zeros((1, 1))
                # 应用函数
                result_grid = func.apply(point_grid, time=t)
                values.append(result_grid[0, 0])

            result[label] = np.array(values)

        return result

    def analyze_points(self, t_range: Tuple[float, float] = (0, 10),
                      num_points: int = 100,
                      function_type: str = 'gaussian') -> Dict[str, Any]:
        """
        分析所有追踪点

        Args:
            t_range: 时间范围
            num_points: 时间点数量
            function_type: 函数类型

        Returns:
            分析结果字典
        """
        time_series = self.get_time_series(t_range, num_points, function_type)

        analysis = {
            'time_range': t_range,
            'num_points': num_points,
            'function_type': function_type,
            'time_series': time_series,
            'statistics': {}
        }

        # 计算统计信息
        for label in self.tracked_points.keys():
            if label in time_series:
                values = time_series[label]
                analysis['statistics'][label] = {
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'final': float(values[-1]),
                }

        return analysis

    # ==================== 数据导出 ====================

    def export_to_csv(self, t_range: Tuple[float, float] = (0, 10),
                      num_points: int = 100,
                      filename: str = 'wind_field_points.csv',
                      function_type: str = 'gaussian') -> bool:
        """
        导出时间序列数据到CSV

        Args:
            t_range: 时间范围
            num_points: 时间点数量
            filename: 文件名
            function_type: 函数类型

        Returns:
            是否成功导出
        """
        try:
            time_series = self.get_time_series(t_range, num_points, function_type)

            # 准备数据
            data = {'time': time_series['time']}
            for label in self.tracked_points.keys():
                if label in time_series:
                    data[label] = time_series[label]

            # 尝试导入pandas
            try:
                import pandas as pd
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                return True
            except ImportError:
                # 如果没有pandas，手动写入CSV
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    # 写入表头
                    headers = ','.join(data.keys())
                    f.write(headers + '\n')

                    # 写入数据
                    num_rows = len(data['time'])
                    for i in range(num_rows):
                        row_data = [str(data[key][i]) for key in data.keys()]
                        f.write(','.join(row_data) + '\n')
                return True

        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def export_summary(self) -> Dict[str, Any]:
        """
        导出分析摘要

        Returns:
            摘要字典
        """
        return {
            'analyzer_version': '1.0.0',
            'creation_time': self._creation_time.isoformat(),
            'tracked_points': [
                {
                    'label': p.label,
                    'row': p.row,
                    'col': p.col,
                    'color': p.color
                }
                for p in self.tracked_points.values()
            ],
            'point_count': len(self.tracked_points),
            'has_editor': self.editor is not None,
        }

    # ==================== 可视化辅助 ====================

    def get_plot_data(self, t_range: Tuple[float, float] = (0, 10),
                      num_points: int = 100,
                      function_type: str = 'gaussian') -> Dict[str, Any]:
        """
        获取用于绘图的数据

        Args:
            t_range: 时间范围
            num_points: 时间点数量
            function_type: 函数类型

        Returns:
            绘图数据字典
        """
        time_series = self.get_time_series(t_range, num_points, function_type)

        return {
            'time': time_series['time'],
            'series': [
                {
                    'label': label,
                    'values': time_series[label],
                    'color': self.tracked_points[label].color,
                }
                for label in self.tracked_points.keys()
                if label in time_series
            ],
            'title': f'风场追踪点时间序列 - {function_type}',
            'xlabel': '时间 (s)',
            'ylabel': '转速 (%)',
        }


# ==================== 导出接口 ====================

__all__ = [
    'TrackedPoint',
    'WindFieldAnalyzer',
]
