# wind_wall_simulator/config.py

from PySide6.QtGui import QColor, QFont

# --- Grid and Canvas Dimensions ---
GRID_DIM: int = 40
MODULE_DIM: int = 4
CELL_SIZE: int = 16
CELL_SPACING: int = 2
TOTAL_CELL_SIZE = CELL_SIZE + CELL_SPACING
CANVAS_WIDTH: int = GRID_DIM * TOTAL_CELL_SIZE
CANVAS_HEIGHT: int = GRID_DIM * TOTAL_CELL_SIZE

# --- Colors and Styling ---
# [最终版] 唯一的、预先计算好的颜色对应表 (Color Lookup Table)
# 严格遵循 淡蓝 -> 绿 -> 黄 -> 红 的视觉分布
COLOR_MAP = []
c1 = QColor(173, 216, 230) # Light Blue
c2 = QColor(0, 255, 0)     # Green
c3 = QColor(255, 255, 0)   # Yellow
c4 = QColor(255, 0, 0)     # Red

def lerp_color(start_color, end_color, t):
    r = int(start_color.red() + (end_color.red() - start_color.red()) * t)
    g = int(start_color.green() + (end_color.green() - start_color.green()) * t)
    b = int(start_color.blue() + (end_color.blue() - start_color.blue()) * t)
    return QColor(r, g, b)

for i in range(256):
    p = i / 255.0
    if p < 0.33: # Blue to Green (33% of range)
        scale = p / 0.33
        COLOR_MAP.append(lerp_color(c1, c2, scale))
    elif p < 0.66: # Green to Yellow (33% of range)
        scale = (p - 0.33) / 0.33
        COLOR_MAP.append(lerp_color(c2, c3, scale))
    else: # Yellow to Red (34% of range)
        scale = (p - 0.66) / 0.34
        COLOR_MAP.append(lerp_color(c3, c4, scale))


MODULE_LINE_COLOR: QColor = QColor(0, 0, 0, 255)
MODULE_LINE_WIDTH: int = 2
SELECTION_BORDER_COLOR: QColor = QColor(0, 120, 215, 220)
SELECTION_BORDER_WIDTH: int = 2

# --- Text Rendering ---
CELL_FONT: QFont = QFont("Arial", 6)
LUMINANCE_THRESHOLD = 140

# --- Other Constants ---
APP_NAME: str = "风墙设置 (Wind Wall Settings)"
APP_VERSION: str = "0.6.0 (Color Consistency Guaranteed)"
