# fan_id_generator.py

import numpy as np
import csv

# 假设每个模组是 2x2 的风扇。如果需要更改，请修改此处。
MODULE_SHAPE = (2, 2)

def generate_fan_id_matrix(array_shape=(40, 40)):
    """
    生成风扇ID矩阵，遵循新的编码规则。
    返回的矩阵布局与UI画布一致 ([0][0] 在左上角)。
    """
    rows, cols = array_shape
    
    # 创建一个空的列表的列表来存储ID
    id_matrix = [["" for _ in range(cols)] for _ in range(rows)]
    
    # 遍历UI画布的索引 (r=0是顶行, c=0是左列)
    for r in range(rows):
        for c in range(cols):
            # 将UI的行、列索引转换为新的坐标系
            # UI的列索引 'c' (0 to 39) 直接对应 X坐标 (1 to 40)
            x_coord = c + 1
            
            # UI的行索引 'r' (0 to 39) 需要翻转来对应 Y坐标 (1 to 40)
            # UI顶行 r=0 -> Y坐标 40
            # UI底行 r=39 -> Y坐标 1
            y_coord = rows - r
            
            # 生成ID字符串
            fan_id = f"X{x_coord:03}Y{y_coord:03}"
            
            # 存入与UI布局对应的矩阵位置
            id_matrix[r][c] = fan_id
            
    return id_matrix


def save_id_matrix_to_csv(id_matrix, filename):
    """将ID矩阵保存到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(id_matrix)
    print(f"风扇ID表已保存至: {filename}")

