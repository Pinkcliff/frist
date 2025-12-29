# check_vtm.py
import pyvista as pv
import json
import numpy as np
import time
import vtk

# --- 请将这里的文件名替换为您实际保存的文件名 ---
filename = "project.vtm" 
# -------------------------------------------------

def check_isolated_fluid_cells(is_solid):
    """
    检查并统计被固体完全包围的孤立流体单元。
    """
    print("\n3. 检查孤立流体单元:")
    if is_solid is None:
        print("  无法执行检查，因为固体标记数组未生成。")
        return

    nx, ny, nz = is_solid.shape
    isolated_count = 0
    
    # 遍历所有内部单元 (不包括边界)
    # 我们只关心那些可能被包围的单元
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            for k in range(1, nz - 1):
                # 如果当前单元是流体
                if not is_solid[i, j, k]:
                    # 检查它的所有六个邻居是否都是固体
                    if (is_solid[i+1, j, k] and is_solid[i-1, j, k] and
                        is_solid[i, j+1, k] and is_solid[i, j-1, k] and
                        is_solid[i, j, k+1] and is_solid[i, j, k-1]):
                        
                        isolated_count += 1
                        if isolated_count < 10: # 只打印前几个例子
                            print(f"  - 发现孤立流体单元于索引: ({i}, {j}, {k})")
    
    print(f"\n  检查完毕。总共发现 {isolated_count} 个孤立流体单元。")
    if isolated_count > 0:
        print("  警告: 存在孤立流体单元，这会导致压力泊松矩阵出现奇异行，严重影响求解器性能和稳定性。")
    else:
        print("  优秀: 未发现孤立流体单元。")


print(f"--- 开始检查文件: {filename} ---\n")

try:
    data = pv.read(filename)
    
    print("1. 文件内部几何结构:")
    print(data)
    print("-" * 20)
    
    print("\n2. 元数据 (FieldData):")
    if not data.field_data:
        print("  未找到FieldData。")
    else:
        for key in data.field_data:
            print(f"  - 找到了元数据: '{key}'")
            content_array = data.field_data[key]
            if content_array is None: print("    内容为空。"); continue
            if key.startswith("grid_") and key.endswith("_coords"):
                print(f"    类型: NumPy Array, 形状: {content_array.shape}, 前5个值: {content_array[:5]}")
            elif isinstance(content_array[0], str):
                content_str = content_array[0]
                try: parsed_json = json.loads(content_str); print(json.dumps(parsed_json, indent=2))
                except (json.JSONDecodeError, TypeError): print(content_str[:500] + "...")
            else: print(f"    未知类型的元数据: {type(content_array)}")
            print("-" * 20)

    # --- 开始执行固体单元标记和孤立单元检查 ---
    is_solid_mask = None
    if "Geometry" in data and "grid_x_coords" in data.field_data:
        print("\n--- 开始执行固体单元标记 (与求解器逻辑相同) ---")
        start_time = time.time()
        
        # 提取网格和几何
        geom_block = data["Geometry"]
        x_coords = data.field_data["grid_x_coords"]
        y_coords = data.field_data["grid_y_coords"]
        z_coords = data.field_data["grid_z_coords"]
        
        nx, ny, nz = len(x_coords)-1, len(y_coords)-1, len(z_coords)-1
        
        dx, dy, dz = np.diff(x_coords), np.diff(y_coords), np.diff(z_coords)
        xc, yc, zc = x_coords[:-1] + 0.5*dx, y_coords[:-1] + 0.5*dy, z_coords[:-1] + 0.5*dz
        
        # 注意：这里的meshgrid索引顺序必须是'ij'来匹配NumPy数组(nx, ny, nz)的顺序
        Xc, Yc, Zc = np.meshgrid(xc, yc, zc, indexing='ij')
        cell_centers = np.vstack((Xc.ravel(), Yc.ravel(), Zc.ravel())).T
        
        # 使用与求解器相同的底层方法
        def get_enclosed_mask(surface_block, points_np):
            surface_polydata = pv.PolyData(surface_block.points, faces=surface_block.faces)
            points_pv_polydata = pv.PolyData(points_np)
            selector = vtk.vtkSelectEnclosedPoints()
            selector.SetInputData(points_pv_polydata)
            selector.SetSurfaceData(surface_polydata)
            selector.Update()
            result_polydata = pv.wrap(selector.GetOutput())
            return result_polydata.point_data['SelectedPoints'].astype(bool)

        frame_mask = get_enclosed_mask(geom_block["FanFrame"], cell_centers)
        hub_mask = get_enclosed_mask(geom_block["FanHub"], cell_centers)
        
        is_solid_mask_1d = np.logical_or(frame_mask, hub_mask)
        is_solid_mask = is_solid_mask_1d.reshape((nx, ny, nz))
        
        num_solid = np.sum(is_solid_mask)
        print(f"标记完成，耗时 {time.time() - start_time:.2f}s。共找到 {num_solid} 个固体单元。")
        
        # 调用检查函数
        check_isolated_fluid_cells(is_solid_mask)

except Exception as e:
    import traceback
    print(f"\n--- 检查过程中发生错误 ---")
    print(e)
    print(traceback.format_exc())

print("\n--- 检查完毕 ---")
