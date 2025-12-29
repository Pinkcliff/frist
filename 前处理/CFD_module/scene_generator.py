# scene_generator.py

import numpy as np
import pyvista as pv
from . import pre_processor_config as config
from .grid_utils import generate_stretched_coords_by_size

# --- (此函数无变化) ---
def create_fan_instance(args):
    """创建一个风扇实例(MultiBlock)，用于并行化"""
    base_fan_multiblock, position = args
    fan_instance = base_fan_multiblock.copy(deep=True)
    for block in fan_instance:
        if block is not None:
            block.translate(position, inplace=True)
    return fan_instance

# --- (此函数无变化) ---
def calculate_translated_points(args):
    """
    一个极其轻量的并行任务：只计算平移后的顶点坐标。
    args: (base_points, position)
    - base_points: 共享的基础顶点NumPy数组
    - position: 该实例的目标位置向量
    返回: 平移后的顶点NumPy数组
    """
    base_points, position = args
    return base_points + position


class SceneGenerator:
    # --- 【手动修复第二版】修改 create_single_fan 函数 ---
    # 返回正确的、包含NumPy数组的Python字典，以匹配FanGeneratorWorker的期望。
    def create_single_fan(self):
        """
        【手动修复版 V3.1 - 修正版】: 生成完整的单个3D风扇几何体。
        此版本修复了V3中的内部逻辑错误，并确保在发生异常时也能返回
        一个有效的空数据结构，防止程序崩溃。
        """
        print("    > 正在创建单个风扇基础几何体 (手动修复版 V3.1 - 修正版)...")
        try:
            # --- 1. 参数初始化 ---
            W = config.FAN_WIDTH
            H = config.FAN_THICKNESS
            center = W / 2.0
            hole_radius = config.FAN_HOLE_DIAMETER / 2
            hub_radius = config.FAN_HUB_DIAMETER / 2
            segments = config.FAN_CIRCLE_SEGMENTS
            if segments % 4 != 0:
                raise ValueError("FAN_CIRCLE_SEGMENTS 必须是4的倍数")
            # --- 2. 生成风扇框架 (Frame) ---
            segs_per_quadrant = segments // 4
            all_angles = []
            corner_angles = np.array([np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4])
            for i in range(4):
                start_angle, end_angle = corner_angles[i], corner_angles[(i + 1) % 4]
                if end_angle < start_angle: end_angle += 2 * np.pi
                all_angles.extend(np.linspace(start_angle, end_angle, segs_per_quadrant, endpoint=False))
            angles = np.array(all_angles)
            
            inner_x = hole_radius * np.cos(angles) + center
            inner_y = hole_radius * np.sin(angles) + center
            inner_points_bottom = np.array([inner_x, inner_y, np.zeros(segments)]).T
            
            outer_x, outer_y = np.zeros(segments), np.zeros(segments)
            for i, angle in enumerate(angles):
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                if abs(sin_a) > abs(cos_a):
                    r = center / abs(sin_a)
                    outer_x[i], outer_y[i] = r * cos_a + center, np.sign(sin_a) * center + center
                else:
                    r = center / abs(cos_a)
                    outer_x[i], outer_y[i] = np.sign(cos_a) * center + center, r * sin_a + center
            outer_points_bottom = np.array([outer_x, outer_y, np.zeros(segments)]).T
            
            bottom_points = np.vstack([outer_points_bottom, inner_points_bottom])
            num_points_per_face = len(bottom_points)
            top_points = bottom_points.copy(); top_points[:, 2] += H
            frame_points = np.vstack([bottom_points, top_points])
            faces_list = []
            num_outer = segments
            for i in range(segments):
                p_b1_outer, p_b2_outer = i, (i + 1) % segments
                p_t1_outer, p_t2_outer = p_b1_outer + num_points_per_face, p_b2_outer + num_points_per_face
                p_b1_inner, p_b2_inner = i + num_outer, (i + 1) % segments + num_outer
                p_t1_inner, p_t2_inner = p_b1_inner + num_points_per_face, p_b2_inner + num_points_per_face
                
                faces_list.extend([[3, p_b1_outer, p_b2_outer, p_b1_inner], [3, p_b2_outer, p_b2_inner, p_b1_inner]]) # Bottom face
                faces_list.extend([[3, p_t1_outer, p_t1_inner, p_t2_outer], [3, p_t2_outer, p_t1_inner, p_t2_inner]]) # Top face
                faces_list.extend([[4, p_b1_outer, p_b2_outer, p_t2_outer, p_t1_outer]]) # Outer wall
                faces_list.extend([[4, p_b1_inner, p_t1_inner, p_t2_inner, p_b2_inner]]) # Inner wall
            frame_faces_array = np.hstack(faces_list)
            # --- 3. 生成轮毂 (Hub) ---
            hub_angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
            hub_x = hub_radius * np.cos(hub_angles) + center
            hub_y = hub_radius * np.sin(hub_angles) + center
            
            hub_points_bottom = np.array([hub_x, hub_y, np.zeros(segments)]).T
            hub_points_top = hub_points_bottom.copy(); hub_points_top[:, 2] = H
            
            hub_points = np.vstack([
                hub_points_bottom, 
                hub_points_top,
                [center, center, 0],    # Bottom center point
                [center, center, H]     # Top center point
            ])
            
            bottom_center_idx = 2 * segments
            top_center_idx = 2 * segments + 1
            
            hub_faces_list = []
            for i in range(segments):
                p_b1, p_b2 = i, (i + 1) % segments
                p_t1, p_t2 = p_b1 + segments, p_b2 + segments
                
                hub_faces_list.extend([[4, p_b1, p_b2, p_t2, p_t1]]) # Side wall
                hub_faces_list.extend([[3, p_b1, bottom_center_idx, p_b2]]) # Bottom cap
                hub_faces_list.extend([[3, p_t1, p_t2, top_center_idx]]) # Top cap
            
            hub_faces_array = np.hstack(hub_faces_list)
            return {
                "frame": {"points": frame_points, "faces": frame_faces_array},
                "hub": {"points": hub_points, "faces": hub_faces_array}
            }
        except Exception as e:
            print(f"    [ERROR] An exception occurred during single fan geometry creation: {e}")
            import traceback
            print(traceback.format_exc())
            # --- 【关键修复】确保即使失败也返回有效（但为空）的字典 ---
            return {
                "frame": {"points": np.array([]), "faces": np.array([])},
                "hub": {"points": np.array([]), "faces": np.array([])}
            }
    # 让它只生成一个风扇，用于调试。
    def create_fan_array_generator(self, progress_callback):
        """
        【最终优化版】: 采用向量化 "Mega-Mesh" 策略生成风扇阵列。
        此方法通过NumPy广播一次性计算所有顶点和面片，避免了并行开销和
        循环中的对象创建，实现数量级的性能提升。
        """
        print("正在使用向量化 'Mega-Mesh' 策略生成风扇阵列...")
        
        # 1. 创建单个基础几何体，作为模板
        base_fan_data = self.create_single_fan()
        base_frame_points = base_fan_data["frame"]["points"]
        base_frame_faces = base_fan_data["frame"]["faces"]
        base_hub_points = base_fan_data["hub"]["points"]
        base_hub_faces = base_fan_data["hub"]["faces"]
        
        num_frame_pts = base_frame_points.shape[0]
        num_hub_pts = base_hub_points.shape[0]
        
        progress_callback(10)
        # 2. 计算所有风扇实例的平移向量
        rows, cols = config.FAN_ARRAY_SHAPE
        total_fans = rows * cols
        fan_width = config.FAN_WIDTH
        x_pos = np.arange(cols) * fan_width
        y_pos = np.arange(rows) * fan_width
        xx, yy = np.meshgrid(x_pos, y_pos)
        positions = np.vstack([xx.ravel(), yy.ravel(), np.zeros(total_fans)]).T
        
        progress_callback(20)
        # 3. 【核心】一次性计算所有顶点
        # 使用NumPy广播，避免循环和并行开销
        # all_points = base_points[None, :, :] + positions[:, None, :]
        # all_points_flat = all_points.reshape(-1, 3)
        all_frame_points = (base_frame_points[None, :, :] + positions[:, None, :]).reshape(-1, 3)
        all_hub_points = (base_hub_points[None, :, :] + positions[:, None, :]).reshape(-1, 3)
        
        progress_callback(50)
        # 4. 【核心】一次性计算所有面片
        # 为每个风扇实例的面片索引添加偏移量
        # 这是一个复杂但高效的操作
        def create_mega_faces(base_faces, num_pts_per_instance, num_instances):
            if base_faces.size == 0:
                return np.array([], dtype=int)
            
            # 创建每个实例的顶点索引偏移量
            offsets = np.arange(num_instances) * num_pts_per_instance
            
            # 复制基础面片数据
            mega_faces = np.tile(base_faces, num_instances)
            
            # 创建一个掩码，只选择顶点索引（忽略面片中的顶点计数值，如3或4）
            is_vertex_index_mask = np.ones_like(mega_faces, dtype=bool)
            
            # 遍历基础面片，将顶点计数值的位置标记为False
            ptr = 0
            base_face_len = len(base_faces)
            while ptr < base_face_len:
                num_verts_in_face = base_faces[ptr]
                # 在每个复制块中，将此位置标记为False
                is_vertex_index_mask[ptr::base_face_len] = False
                ptr += num_verts_in_face + 1
            
            # 创建偏移数组，其形状与 mega_faces 相同
            offset_array = np.repeat(offsets, base_face_len)
            
            # 仅将偏移量应用于顶点索引
            mega_faces[is_vertex_index_mask] += offset_array[is_vertex_index_mask]
            
            return mega_faces
        all_frame_faces = create_mega_faces(base_frame_faces, num_frame_pts, total_fans)
        all_hub_faces = create_mega_faces(base_hub_faces, num_hub_pts, total_fans)
        
        progress_callback(80)
        # 5. 一次性创建PyVista对象
        frame_mesh = pv.PolyData(all_frame_points, faces=all_frame_faces)
        hub_mesh = pv.PolyData(all_hub_points, faces=all_hub_faces)
        
        combined_multiblock = pv.MultiBlock({"frame": frame_mesh, "hub": hub_mesh})
        yield combined_multiblock
        progress_callback(100)
        print("风扇阵列生成完毕。")

    def _calculate_grid_coords(self):
        from .grid_utils import generate_stretched_coords_by_size

        config.update_domain_bounds()
        print("正在以【米】为单位计算网格坐标 (V5 - 调试打印版)...")

        # --- Z轴坐标生成 ---
        fan_thickness_m = config.FAN_THICKNESS / 1000.0
        core_nz = config.COMPONENT_GRID_CELLS[2]
        
        z_core = np.linspace(0.0, fan_thickness_m, core_nz + 1)
        base_dz_m = np.diff(z_core)[0]

        inlet_len_m = abs(config.DOMAIN_BOUNDS_M['zmin'])
        z_inlet_stretched = generate_stretched_coords_by_size(inlet_len_m, base_dz_m, config.STRETCH_RATIO_Z)
        z_inlet = z_inlet_stretched - inlet_len_m

        outlet_len_m = abs(config.DOMAIN_BOUNDS_M['zmax'] - fan_thickness_m)
        z_outlet_stretched = generate_stretched_coords_by_size(outlet_len_m, base_dz_m, config.STRETCH_RATIO_Z)
        z_outlet = z_outlet_stretched + fan_thickness_m
        
        z_coords = np.unique(np.concatenate((z_inlet, z_core, z_outlet)))
        
        # --- X/Y轴坐标生成 ---
        rows, cols = config.FAN_ARRAY_SHAPE
        base_dx_m = (config.FAN_WIDTH / config.COMPONENT_GRID_CELLS[0]) / 1000.0
        base_dy_m = (config.FAN_WIDTH / config.COMPONENT_GRID_CELLS[1]) / 1000.0
        core_x_end_m = (cols * config.FAN_WIDTH) / 1000.0
        core_nx = cols * config.COMPONENT_GRID_CELLS[0]
        x_core = np.linspace(0.0, core_x_end_m, core_nx + 1)
        core_y_end_m = (rows * config.FAN_WIDTH) / 1000.0
        core_ny = rows * config.COMPONENT_GRID_CELLS[1]
        y_core = np.linspace(0.0, core_y_end_m, core_ny + 1)
        margin_x_m = config.MARGIN_X / 1000.0
        x_margin_n_stretched = generate_stretched_coords_by_size(margin_x_m, base_dx_m, config.STRETCH_RATIO_XY)
        x_margin_n = -np.flip(x_margin_n_stretched)
        x_margin_p_stretched = generate_stretched_coords_by_size(margin_x_m, base_dx_m, config.STRETCH_RATIO_XY)
        x_margin_p = core_x_end_m + x_margin_p_stretched
        margin_y_m = config.MARGIN_Y / 1000.0
        y_margin_n_stretched = generate_stretched_coords_by_size(margin_y_m, base_dy_m, config.STRETCH_RATIO_XY)
        y_margin_n = -np.flip(y_margin_n_stretched)
        y_margin_p_stretched = generate_stretched_coords_by_size(margin_y_m, base_dy_m, config.STRETCH_RATIO_XY)
        y_margin_p = core_y_end_m + y_margin_p_stretched
        x_coords = np.unique(np.concatenate((x_margin_n, x_core, x_margin_p)))
        y_coords = np.unique(np.concatenate((y_margin_n, y_core, y_margin_p)))

        # --- 统计信息 ---
        num_x, num_y, num_z = len(x_coords) - 1, len(y_coords) - 1, len(z_coords) - 1
        total_cells = num_x * num_y * num_z
        dx_vals, dy_vals, dz_vals = np.diff(x_coords), np.diff(y_coords), np.diff(z_coords)
        min_size = (np.min(dx_vals), np.min(dy_vals), np.min(dz_vals))
        max_size = (np.max(dx_vals), np.max(dy_vals), np.max(dz_vals))
        stats = {"total_cells": total_cells, "min_size": min_size, "max_size": max_size}
        
        return x_coords, y_coords, z_coords, stats

    def create_grid_geometry(self):
        x_coords_m, y_coords_m, z_coords_m, stats = self._calculate_grid_coords()
        print("正在为每个面构建网格几何体 (单位: mm)...")

        x_coords = x_coords_m * 1000.0
        y_coords = y_coords_m * 1000.0
        z_coords = z_coords_m * 1000.0
        
        bds = {key: value * 1000.0 for key, value in config.DOMAIN_BOUNDS_M.items()}
        xmin, xmax = bds['xmin'], bds['xmax']
        ymin, ymax = bds['ymin'], bds['ymax']
        zmin, zmax = bds['zmin'], bds['zmax']

        def _create_face_grid(points_list, lines_list):
            if not points_list: return pv.PolyData()
            return pv.PolyData(np.array(points_list), lines=np.array(lines_list))

        grids = {}
        
        points_zmin, lines_zmin = [], []
        for x in x_coords:
            if xmin <= x <= xmax: points_zmin.extend([[x, ymin, zmin], [x, ymax, zmin]]); lines_zmin.extend([2, len(points_zmin)-2, len(points_zmin)-1])
        for y in y_coords:
            if ymin <= y <= ymax: points_zmin.extend([[xmin, y, zmin], [xmax, y, zmin]]); lines_zmin.extend([2, len(points_zmin)-2, len(points_zmin)-1])
        grids['zmin'] = _create_face_grid(points_zmin, lines_zmin)
        
        points_zmax, lines_zmax = [], []
        for x in x_coords:
            if xmin <= x <= xmax: points_zmax.extend([[x, ymin, zmax], [x, ymax, zmax]]); lines_zmax.extend([2, len(points_zmax)-2, len(points_zmax)-1])
        for y in y_coords:
            if ymin <= y <= ymax: points_zmax.extend([[xmin, y, zmax], [xmax, y, zmax]]); lines_zmax.extend([2, len(points_zmax)-2, len(points_zmax)-1])
        grids['zmax'] = _create_face_grid(points_zmax, lines_zmax)

        points_ymin, lines_ymin = [], []
        for x in x_coords:
            if xmin <= x <= xmax: points_ymin.extend([[x, ymin, zmin], [x, ymin, zmax]]); lines_ymin.extend([2, len(points_ymin)-2, len(points_ymin)-1])
        for z in z_coords:
            if zmin <= z <= zmax: points_ymin.extend([[xmin, ymin, z], [xmax, ymin, z]]); lines_ymin.extend([2, len(points_ymin)-2, len(points_ymin)-1])
        grids['ymin'] = _create_face_grid(points_ymin, lines_ymin)

        points_ymax, lines_ymax = [], []
        for x in x_coords:
            if xmin <= x <= xmax: points_ymax.extend([[x, ymax, zmin], [x, ymax, zmax]]); lines_ymax.extend([2, len(points_ymax)-2, len(points_ymax)-1])
        for z in z_coords:
            if zmin <= z <= zmax: points_ymax.extend([[xmin, ymax, z], [xmax, ymax, z]]); lines_ymax.extend([2, len(points_ymax)-2, len(points_ymax)-1])
        grids['ymax'] = _create_face_grid(points_ymax, lines_ymax)

        points_xmin, lines_xmin = [], []
        for y in y_coords:
            if ymin <= y <= ymax: points_xmin.extend([[xmin, y, zmin], [xmin, y, zmax]]); lines_xmin.extend([2, len(points_xmin)-2, len(points_xmin)-1])
        for z in z_coords:
            if zmin <= z <= zmax: points_xmin.extend([[xmin, ymin, z], [xmin, ymax, z]]); lines_xmin.extend([2, len(points_xmin)-2, len(points_xmin)-1])
        grids['xmin'] = _create_face_grid(points_xmin, lines_xmin)

        points_xmax, lines_xmax = [], []
        for y in y_coords:
            if ymin <= y <= ymax: points_xmax.extend([[xmax, y, zmin], [xmax, y, zmax]]); lines_xmax.extend([2, len(points_xmax)-2, len(points_xmax)-1])
        for z in z_coords:
            if zmin <= z <= zmax: points_xmax.extend([[xmax, ymin, z], [xmax, ymax, z]]); lines_xmax.extend([2, len(points_xmax)-2, len(points_xmax)-1])
        grids['xmax'] = _create_face_grid(points_xmax, lines_xmax)
        
        print("所有面的网格几何体构建完毕。")
        return grids, stats
