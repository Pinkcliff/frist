# debug_check.py
import pyvista as pv
import json
import numpy as np
import os

filename = "project.vtm" 
print(f"--- 开始检查文件: {filename} ---\n")

if not os.path.exists(filename):
    print(f"错误: 文件 '{filename}' 不存在。")
    exit()

try:
    data = pv.read(filename)
    
    # ... (前面的检查部分保持不变) ...
    print("--- 1. 基本元数据检查 --- ...")
    print("--- 2. 单位和时间戳检查 --- ...")

    # --- 3. 风扇厚度网格检查 (最终修正版) ---
    print("--- 3. 风扇厚度网格检查 ---")
    
    params = json.loads(data.field_data["parameters.json"][0])
    grid_z_coords = data.field_data["grid_z_coords"]
    
    if 'FAN_THICKNESS' in params:
        fan_thickness_m = params['FAN_THICKNESS'] / 1000.0
        print(f"  [INFO] 从VTM参数中读取到风扇厚度: {fan_thickness_m * 1000:.1f} mm ({fan_thickness_m:.4f} m)")
    else:
        print("  [!! FAILED !!] VTM文件中未找到 'FAN_THICKNESS' 参数。")
        fan_thickness_m = None

    if fan_thickness_m is not None:
        # --- 【核心修复】直接统计节点数，而不是累加尺寸 ---
        # 增加一个微小的容差来处理浮点数精度问题
        tolerance = 1e-9
        nodes_in_core_region = grid_z_coords[(grid_z_coords >= -tolerance) & (grid_z_coords <= fan_thickness_m + tolerance)]
        
        # 单元数 = 节点数 - 1
        actual_cells_in_thickness = len(nodes_in_core_region) - 1
        
        print(f"  [RESULT] 独立计算出的厚度方向网格数: {actual_cells_in_thickness}")
        
        expected_cells = params.get('COMPONENT_GRID_CELLS', [0,0,0])[2]
        print(f"  [INFO] 预处理器设定的预期网格数: {expected_cells}")

        if actual_cells_in_thickness == expected_cells:
            print("  [OK] 检查通过：VTM文件中的网格数据与参数设置一致。")
        else:
            print("  [!! FAILED !!] 检查失败：VTM文件中的网格数据与参数设置不一致！")

    print("---------------------------\n")

except Exception as e:
    import traceback
    print(f"\n--- 检查过程中发生严重错误 ---")
    print(e)
    print(traceback.format_exc())

print("\n--- 检查完毕 ---")
