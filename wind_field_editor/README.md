# 风场编辑模块

## 概述

风场编辑模块是风机面板的核心功能，用于编辑和管理40×40风扇阵列的风场分布。

## 功能特性

### 1. 编辑工具

| 工具 | 描述 | 快捷键 |
|------|------|--------|
| **选择工具** | 点选、框选风扇单元 | - |
| **笔刷工具** | 自由绘制风场 | - |
| **圆形工具** | 圆形区域选择 | - |
| **直线工具** | 直线路径选择 | - |
| **函数工具** | 基于数学函数生成风场 | - |

### 2. 交互模式

#### 选择操作
- **单击**: 选择单个风扇
- **Shift+单击**: 添加到选择
- **Ctrl+单击**: 反选风扇
- **双击**: 选择整个4×4模块
- **ESC**: 取消选择

#### 修饰键
- **Shift**: 添加模式
- **Ctrl**: 反选模式
- **无修饰**: 替换模式

### 3. 羽化功能

羽化可以在编辑区域边缘创建平滑过渡。

```python
# 启用3层羽化
feather_enabled = True
feather_value = 3
```

羽化算法:
```
第1层: 100% 基础值
第2层: 66% 基础值
第3层: 33% 基础值
```

### 4. 颜色映射

| 转速 | 颜色 | RGB |
|------|------|-----|
| 0% | 淡蓝 | (173, 216, 230) |
| 33% | 绿 | (0, 255, 0) |
| 66% | 黄 | (255, 255, 0) |
| 100% | 红 | (255, 0, 0) |

### 5. 撤销/重做

- **Ctrl+Z**: 撤销
- **Ctrl+Y**: 重做
- 最大历史记录: 50步

## 模块结构

```
风场编辑/
├── __init__.py       # 模块初始化
├── core.py           # 核心编辑器类
├── tools.py          # 编辑工具实现
├── config.py         # 配置常量
├── utils.py          # 工具函数
└── README.md         # 本文档
```

## 核心类

### WindFieldEditor

风场编辑器核心类。

```python
from 风场编辑 import WindFieldEditor

# 创建编辑器
editor = WindFieldEditor(grid_dim=40, max_rpm=17000)

# 设置转速
editor.set_cell_value(10, 10, 50.0)  # (行, 列, 值)

# 选择区域
editor.selected_cells.add((10, 10))
editor.selected_cells.add((10, 11))

# 应用转速到选择
editor.apply_speed_to_selection(80.0, feather=True, feather_value=3)

# 撤销操作
editor.undo()

# 导出数据
data = editor.to_wind_field_data()
```

### 工具类

```python
from 风场编辑.tools import BrushTool, BrushSettings

# 创建笔刷工具
brush = BrushTool()
brush.activate()

# 配置笔刷
brush.set_size(10)      # 直径10格
brush.set_value(100.0)  # 100%转速
brush.set_feather(True, 3)  # 启用3层羽化
```

## 数据格式

### WindFieldData

```python
@dataclass
class WindFieldData:
    grid_data: np.ndarray      # (40, 40) 转速百分比
    max_rpm: int = 17000       # 最大转速
    max_time: float = 10.0     # 最大时间
    time_resolution: float = 0.1  # 时间分辨率
    metadata: dict = None      # 元数据
```

### 时间序列数据

```python
time_series_data = {
    'time_points': [...],      # 时间点数组
    'time_resolution': 0.1,    # 时间分辨率
    'max_time': 10.0,          # 最大时间
    'max_rpm': 17000,          # 最大转速
    'grid_shape': (40, 40),    # 网格形状
    'rpm_data': np.ndarray,    # (time, 40, 40) RPM数据
    'metadata': {...}
}
```

## 配置参数

所有配置参数在 `config.py` 中定义：

```python
from 风场编辑.config import (
    GRID_DIM,           # 网格维度: 40
    MODULE_DIM,         # 模块维度: 4
    DEFAULT_MAX_RPM,    # 默认最大转速: 17000
    DEFAULT_MAX_TIME,   # 默认最大时间: 10.0
    COLOR_MAP,          # 颜色映射表
)
```

## 使用示例

### 示例1: 创建高斯分布

```python
from 风场编辑 import WindFieldEditor
from 风场编辑.tools import FunctionTool

# 创建编辑器
editor = WindFieldEditor()

# 使用函数工具
func_tool = FunctionTool()
func_tool.settings.center = (20, 20)
func_tool.settings.sigma = 10.0
func_tool.settings.amplitude = 100.0

# 应用高斯分布
func_tool.apply_gaussian(
    editor.grid_data,
    center=(20, 20),
    sigma=10.0,
    amplitude=100.0
)

# 导出数据
data = editor.to_wind_field_data()
```

### 示例2: 使用笔刷绘制

```python
from 风场编辑 import WindFieldEditor

editor = WindFieldEditor()

# 应用笔刷
editor.apply_brush(
    center_row=20,
    center_col=20,
    brush_size=10,
    brush_value=100.0,
    feather=True,
    feather_value=3
)

# 导出时间序列
time_series = editor.get_summary()
```

## 依赖

- Python 3.7+
- NumPy
- PySide6 (用于GUI)

## 注意事项

1. 所有转速值范围为 0-100%
2. 羽化层数范围为 1-10
3. 笔刷直径范围为 1-40 格
4. 撤销历史最多保存 50 步

## 版本历史

- **v1.0.0** (2024-01-03)
  - 初始版本
  - 支持选择、笔刷、圆形、直线、函数工具
  - 羽化功能
  - 撤销/重做
