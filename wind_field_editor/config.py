# -*- coding: utf-8 -*-
"""
风场编辑模块配置

定义各种常量和配置参数
"""

# ==================== 网格配置 ====================
GRID_DIM: int = 40          # 网格维度 (40x40)
MODULE_DIM: int = 4         # 模块维度 (4x4风扇为一个模块)

# ==================== 单元格配置 ====================
CELL_SIZE: int = 16         # 单元格大小 (像素)
CELL_SPACING: int = 2       # 单元格间距 (像素)
TOTAL_CELL_SIZE = CELL_SIZE + CELL_SPACING

# ==================== 画布配置 ====================
CANVAS_WIDTH: int = GRID_DIM * TOTAL_CELL_SIZE
CANVAS_HEIGHT: int = GRID_DIM * TOTAL_CELL_SIZE

# ==================== 风扇配置 ====================
DEFAULT_MAX_RPM: int = 17000       # 默认最大转速
FAN_RPM_2: int = 14600             # 二级转速
DEFAULT_MAX_TIME: float = 10.0     # 默认最大时间 (秒)
DEFAULT_TIME_RESOLUTION: float = 0.1  # 默认时间分辨率 (秒)

# ==================== 羽化配置 ====================
MIN_FEATHER_VALUE: int = 1         # 最小羽化层数
MAX_FEATHER_VALUE: int = 10        # 最大羽化层数
DEFAULT_FEATHER_VALUE: int = 3     # 默认羽化层数

# ==================== 笔刷配置 ====================
MIN_BRUSH_SIZE: int = 1            # 最小笔刷直径
MAX_BRUSH_SIZE: int = 40           # 最大笔刷直径
DEFAULT_BRUSH_SIZE: int = 5        # 默认笔刷直径
DEFAULT_BRUSH_VALUE: float = 100.0 # 默认笔刷值

# ==================== 转速范围 ====================
MIN_SPEED_VALUE: float = 0.0       # 最小转速百分比
MAX_SPEED_VALUE: float = 100.0     # 最大转速百分比

# ==================== 颜色映射 ====================
# 颜色梯度: 淡蓝 -> 绿 -> 黄 -> 红
COLOR_MAP_SIZE: int = 256

COLOR_MAP = []
c1 = (173, 216, 230)  # Light Blue - 0%
c2 = (0, 255, 0)      # Green - 33%
c3 = (255, 255, 0)    # Yellow - 66%
c4 = (255, 0, 0)      # Red - 100%

def _lerp_color(start_color, end_color, t: float) -> tuple:
    """线性插值颜色"""
    r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
    g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
    b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
    return (r, g, b)

# 生成256色颜色映射表
for i in range(COLOR_MAP_SIZE):
    p = i / (COLOR_MAP_SIZE - 1)
    if p < 0.33:
        scale = p / 0.33
        COLOR_MAP.append(_lerp_color(c1, c2, scale))
    elif p < 0.66:
        scale = (p - 0.33) / 0.33
        COLOR_MAP.append(_lerp_color(c2, c3, scale))
    else:
        scale = (p - 0.66) / 0.34
        COLOR_MAP.append(_lerp_color(c3, c4, scale))

# ==================== UI 配置 ====================
MODULE_LINE_COLOR = (0, 0, 0)          # 模块分割线颜色
MODULE_LINE_WIDTH = 2                  # 模块分割线宽度
SELECTION_BORDER_COLOR = (0, 120, 215) # 选中边框颜色
SELECTION_BORDER_WIDTH = 2             # 选中边框宽度

LUMINANCE_THRESHOLD = 140              # 文本颜色亮度阈值

# ==================== 历史记录配置 ====================
MAX_HISTORY_SIZE: int = 50    # 最大撤销历史记录数

# ==================== 模板配置 ====================
TEMPLATE_DIR = "templates"     # 模板目录
TEMPLATE_EXT = ".json"         # 模板文件扩展名

# ==================== 导出配置 ====================
EXPORT_FORMAT_VERSION = "1.0"  # 导出格式版本
