# grid_utils.py
import numpy as np

def generate_stretched_coords_by_size(length, first_cell_size, ratio, max_cells=2000):
    """
    根据初始单元尺寸和拉伸比，生成一个从0到length的一维坐标点数组。
    这是我们最终使用的、经过验证的函数。
    """
    if length <= 1e-6:
        return np.array([0.0])

    coords = [0.0]
    current_pos = 0.0
    current_size = first_cell_size
    
    for _ in range(max_cells):
        current_pos += current_size
        if current_pos >= length:
            break
        coords.append(current_pos)
        current_size *= ratio
    
    coords.append(length)
    
    coords_np = np.array(coords)
    # 缩放以确保终点精确
    return coords_np * (length / coords_np[-1])
