# wind_wall_simulator/utils.py

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from . import config

def value_to_color(value: float, min_val: float = 0.0, max_val: float = 100.0) -> QColor:
    """
    [核心修正] Directly looks up a color from the pre-calculated COLOR_MAP.
    This guarantees that the same value always returns the exact same color.
    """
    # Clamp the value to the valid range
    value = max(min_val, min(max_val, value))
    
    # Calculate the index in the 256-color map
    color_index = int(((value - min_val) / (max_val - min_val)) * (len(config.COLOR_MAP) - 1))
    
    # Return the pre-calculated color from the table
    return config.COLOR_MAP[color_index]

def get_contrasting_text_color(bg_color: QColor) -> QColor:
    """Calculates whether black or white text is more readable on a given background color."""
    luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
    return QColor(Qt.black) if luminance > config.LUMINANCE_THRESHOLD else QColor(Qt.white)
