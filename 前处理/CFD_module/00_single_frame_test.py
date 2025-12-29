# single_face_corner_first_test.py

import pyvista as pv
import numpy as np

# --- 关键参数 ---
FAN_WIDTH = 80.0
FAN_HOLE_DIAMETER = 76.0
# 我们将要测试的分段数列表
SEGMENTS_TO_TEST = [4, 8, 16, 32]

def create_holed_face_corner_first(segments):
    """
    只创建一个外方内圆的2D平面。
    采用“角点优先”策略，先定义指向角点的射线，再在其中插值，
    从根本上解决相位问题。
    """
    print(f"--- 正在为 {segments} 个分段生成底面 (角点优先版) ---")
    W = FAN_WIDTH
    center = W / 2.0
    hole_radius = FAN_HOLE_DIAMETER / 2
    
    if segments % 4 != 0:
        raise ValueError("FAN_CIRCLE_SEGMENTS 必须是4的倍数")
    
    segs_per_quadrant = segments // 4
    
    # 1. 定义以角点为基准的角度（射线方向）
    all_angles = []
    # 定义4个角点的角度
    corner_angles = np.array([np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4])
    
    # 在角点之间均匀插入中间角度
    for i in range(4):
        start_angle = corner_angles[i]
        end_angle = corner_angles[(i + 1) % 4]
        if end_angle < start_angle:
            end_angle += 2 * np.pi # 处理跨越 2pi 的情况
            
        # 包含起始角点，不包含结束角点（因为下一个循环会包含它）
        quadrant_angles = np.linspace(start_angle, end_angle, segs_per_quadrant, endpoint=False)
        all_angles.extend(quadrant_angles)
        
    angles = np.array(all_angles)

    # 2. 计算内圈交点
    inner_x = hole_radius * np.cos(angles) + center
    inner_y = hole_radius * np.sin(angles) + center
    inner_points = np.array([inner_x, inner_y, np.zeros(segments)]).T

    # 3. 计算外框交点
    outer_x = np.zeros(segments)
    outer_y = np.zeros(segments)
    
    for i, angle in enumerate(angles):
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        if abs(sin_a) > abs(cos_a):
            r = center / abs(sin_a)
            outer_x[i] = r * cos_a + center
            outer_y[i] = np.sign(sin_a) * center + center
        else:
            r = center / abs(cos_a)
            outer_x[i] = np.sign(cos_a) * center + center
            outer_y[i] = r * sin_a + center
            
    outer_points = np.array([outer_x, outer_y, np.zeros(segments)]).T
    
    # 4. 合并所有顶点
    points = np.vstack([outer_points, inner_points])
    
    # 5. 手动构建面片
    faces = []
    num_outer = segments
    
    for i in range(segments):
        p_outer_1 = i
        p_outer_2 = (i + 1) % segments
        p_inner_1 = i + num_outer
        p_inner_2 = ((i + 1) % segments) + num_outer
        
        faces.extend([3, p_outer_1, p_outer_2, p_inner_1])
        faces.extend([3, p_outer_2, p_inner_2, p_inner_1])

    holed_face = pv.PolyData(points, faces=faces)
    
    if holed_face and holed_face.n_cells > 0:
        print(f"    - 成功: 包含 {holed_face.n_points} 个顶点和 {holed_face.n_cells} 个三角面。")
    else:
        print(f"    - 失败: 未能生成有效的底面。")
        
    return holed_face

if __name__ == '__main__':
    # 创建一个2x2的子图布局
    plotter = pv.Plotter(shape=(2, 2))
    
    print("\n正在为不同的分段数生成和显示底面，请检查其几何形状是否正确。")
    
    for i, seg_count in enumerate(SEGMENTS_TO_TEST):
        # 计算子图的位置
        row = i // 2
        col = i % 2
        
        # 激活子图
        plotter.subplot(row, col)
        
        # 生成带孔的底面
        fan_face = create_holed_face_corner_first(seg_count)
        
        # 在当前子图中显示
        plotter.add_mesh(fan_face, show_edges=True, color='lightblue')
        plotter.add_text(f"Segments = {seg_count}", position='upper_edge', font_size=10)
        plotter.add_axes()
        plotter.view_xy() 
        plotter.enable_zoom_style()

    # 链接所有子图的相机
    plotter.link_views()
    
    plotter.show()
