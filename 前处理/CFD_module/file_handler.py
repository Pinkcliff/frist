# file_handler.py

import json
import os
import tempfile
import zipfile
import pyvista as pv
import numpy as np
from .fan_id_generator import generate_fan_id_matrix, save_id_matrix_to_csv

def save_parameters(main_window, filename):
    """从UI收集所有参数并保存为JSON文件"""
    params = {
        # 全局参数
        "MARGIN_X": main_window.ui.le_margin_x.text(),
        "MARGIN_Y": main_window.ui.le_margin_y.text(),
        "INLET_LENGTH": main_window.ui.le_inlet_length.text(),
        "OUTLET_LENGTH": main_window.ui.le_outlet_length.text(),
        "FAN_WIDTH": main_window.ui.le_fan_width.text(),
        "FAN_THICKNESS": main_window.ui.le_fan_thickness.text(),
        "FAN_HOLE_DIAMETER": main_window.ui.le_fan_hole_diameter.text(),
        "FAN_HUB_DIAMETER": main_window.ui.le_fan_hub_diameter.text(),
        "FAN_CIRCLE_SEGMENTS": main_window.ui.le_fan_circle_segments.text(),
        "GROUNDED": main_window.ui.check_grounded.isChecked(),
        "COMPONENT_GRID_CELLS_X": main_window.ui.le_comp_grid_x.text(),
        "COMPONENT_GRID_CELLS_Y": main_window.ui.le_comp_grid_y.text(),
        "COMPONENT_GRID_CELLS_Z": main_window.ui.le_comp_grid_z.text(),
        "ENVIRONMENT_GRID_SIZE_X": main_window.ui.le_env_grid_x.text(),
        "ENVIRONMENT_GRID_SIZE_Y": main_window.ui.le_env_grid_y.text(),
        "ENVIRONMENT_GRID_SIZE_Z": main_window.ui.le_env_grid_z.text(),
        # 边界封闭
        "BOUNDARY_XP": main_window.ui.check_boundary_xp.isChecked(),
        "BOUNDARY_XN": main_window.ui.check_boundary_xn.isChecked(),
        "BOUNDARY_YP": main_window.ui.check_boundary_yp.isChecked(),
        "BOUNDARY_YN": main_window.ui.check_boundary_yn.isChecked(),
        "BOUNDARY_ZP": main_window.ui.check_boundary_zp.isChecked(),
        "BOUNDARY_ZN": main_window.ui.check_boundary_zn.isChecked(),
        # 风扇参数
        "FAN_RPM_1": main_window.ui.le_rpm1.text(),
        "FAN_DIRECTION_1_IS_CW": main_window.ui.check_dir1.isChecked(),
        "FAN_RPM_2": main_window.ui.le_rpm2.text(),
        "FAN_DIRECTION_2_IS_CW": main_window.ui.check_dir2.isChecked(),
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(params, f, indent=4)
    main_window.log_message(f"参数已保存至: {filename}")

def load_parameters(main_window, filename):
    """从JSON文件读取参数并更新UI"""
    with open(filename, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    # 全局参数
    main_window.ui.le_margin_x.setText(params.get("MARGIN_X", ""))
    main_window.ui.le_margin_y.setText(params.get("MARGIN_Y", ""))
    main_window.ui.le_inlet_length.setText(params.get("INLET_LENGTH", ""))
    main_window.ui.le_outlet_length.setText(params.get("OUTLET_LENGTH", ""))
    main_window.ui.le_fan_width.setText(params.get("FAN_WIDTH", ""))
    main_window.ui.le_fan_thickness.setText(params.get("FAN_THICKNESS", ""))
    main_window.ui.le_fan_hole_diameter.setText(params.get("FAN_HOLE_DIAMETER", ""))
    main_window.ui.le_fan_hub_diameter.setText(params.get("FAN_HUB_DIAMETER", ""))
    main_window.ui.le_fan_circle_segments.setText(params.get("FAN_CIRCLE_SEGMENTS", ""))
    main_window.ui.check_grounded.setChecked(params.get("GROUNDED", False))
    main_window.ui.le_comp_grid_x.setText(params.get("COMPONENT_GRID_CELLS_X", ""))
    main_window.ui.le_comp_grid_y.setText(params.get("COMPONENT_GRID_CELLS_Y", ""))
    main_window.ui.le_comp_grid_z.setText(params.get("COMPONENT_GRID_CELLS_Z", ""))
    main_window.ui.le_env_grid_x.setText(params.get("ENVIRONMENT_GRID_SIZE_X", ""))
    main_window.ui.le_env_grid_y.setText(params.get("ENVIRONMENT_GRID_SIZE_Y", ""))
    main_window.ui.le_env_grid_z.setText(params.get("ENVIRONMENT_GRID_SIZE_Z", ""))
    # 边界封闭
    main_window.ui.check_boundary_xp.setChecked(params.get("BOUNDARY_XP", False))
    main_window.ui.check_boundary_xn.setChecked(params.get("BOUNDARY_XN", False))
    main_window.ui.check_boundary_yp.setChecked(params.get("BOUNDARY_YP", False))
    main_window.ui.check_boundary_yn.setChecked(params.get("BOUNDARY_YN", False))
    main_window.ui.check_boundary_zp.setChecked(params.get("BOUNDARY_ZP", False))
    main_window.ui.check_boundary_zn.setChecked(params.get("BOUNDARY_ZN", False))
    # 风扇参数
    main_window.ui.le_rpm1.setText(params.get("FAN_RPM_1", ""))
    main_window.ui.check_dir1.setChecked(params.get("FAN_DIRECTION_1_IS_CW", False))
    main_window.ui.le_rpm2.setText(params.get("FAN_RPM_2", ""))
    main_window.ui.check_dir2.setChecked(params.get("FAN_DIRECTION_2_IS_CW", False))
    
    main_window.log_message(f"参数已从 {filename} 加载。")
    # 触发UI更新
    main_window.on_parameter_changed()

def save_calculation_file(main_window, filename):
    # --- 【关键修复】将所有需要的导入都放在函数顶部 ---
    import os
    import json
    import numpy as np
    import pyvista as pv
    from io import StringIO
    import csv
    import datetime
    from . import pre_processor_config as config
    from .fan_id_generator import generate_fan_id_matrix

    main_window.log_message(f"进入 file_handler.save_calculation_file 函数。")
    main_window.log_message(f"接收到的文件名: {filename}")
    main_window.log_message(f"开始构建计算文件...")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_data = pv.MultiBlock()
    main_window.log_message(f"PyVista MultiBlock 对象已创建。")

    # 1. 添加几何数据
    if main_window.fan_actor:
        geom_block = pv.MultiBlock()
        fan_multiblock = main_window.fan_actor.mapper.dataset.copy()
        main_window.log_message(f"正在转换几何体单位 (除以1000)...")
        for block in fan_multiblock:
            if block is not None:
                block.points /= 1000.0
        geom_block["FanFrame"] = fan_multiblock["frame"]
        geom_block["FanHub"] = fan_multiblock["hub"]
        project_data["Geometry"] = geom_block
        main_window.log_message("风扇几何体已(转换为米)并添加到项目。")
    else:
        main_window.log_message("警告: 未找到风扇几何体。")
    
    # 2. 添加网格坐标
    main_window.log_message(f"正在计算网格坐标...")
    try:
        x_coords, y_coords, z_coords, _ = main_window.scene_generator._calculate_grid_coords()
        project_data.field_data["grid_x_coords"] = x_coords
        project_data.field_data["grid_y_coords"] = y_coords
        project_data.field_data["grid_z_coords"] = z_coords
        main_window.log_message("网格坐标已作为元数据添加。")
    except Exception as e:
        main_window.log_message(f"错误: 网格坐标计算失败 - {e}")
        # 提供默认坐标
        x_coords = np.linspace(0, 1, 11)
        y_coords = np.linspace(0, 1, 11)
        z_coords = np.linspace(0, 1, 11)
        project_data.field_data["grid_x_coords"] = x_coords
        project_data.field_data["grid_y_coords"] = y_coords
        project_data.field_data["grid_z_coords"] = z_coords
        main_window.log_message("使用默认网格坐标。")

    # 3. 添加全局参数 (parameters.json)
    params_dict = {k: v for k, v in config.__dict__.items() if not k.startswith('__') and isinstance(v, (int, float, str, bool, tuple, list, dict))}
    try:
        params_dict['AIR_TEMPERATURE_C'] = float(main_window.ui.le_air_temp.text())
        params_dict['AIR_HUMIDITY_RH'] = float(main_window.ui.le_air_humidity.text())
        params_dict['AMBIENT_PRESSURE_PA'] = float(main_window.ui.le_ambient_pressure.text())
    except ValueError:
        params_dict['AIR_TEMPERATURE_C'] = 25.0; params_dict['AIR_HUMIDITY_RH'] = 50.0; params_dict['AMBIENT_PRESSURE_PA'] = 0.0
    project_data.field_data["parameters.json"] = np.array([json.dumps(params_dict, indent=4)])
    main_window.log_message("全局参数已作为元数据添加。")

    # 4. 添加边界条件 (boundary_conditions.json)
    bc_dict = {
      "x_min": {"type": "inlet", "value": [10.0, 0, 0]}, "x_max": {"type": "outlet", "value": 0.0},
      "y_min": {"type": "wall", "value": "no_slip"}, "y_max": {"type": "wall", "value": "no_slip"},
      "z_min": {"type": "wall", "value": "no_slip"}, "z_max": {"type": "wall", "value": "no_slip"}
    }
    project_data.field_data["boundary_conditions.json"] = np.array([json.dumps(bc_dict, indent=4)])
    main_window.log_message("边界条件(示例)已作为元数据添加。")

    # 5. 添加风扇ID矩阵 (fan_id_matrix.csv)
    try:
        id_matrix = generate_fan_id_matrix()
        string_io = StringIO()
        csv_writer = csv.writer(string_io)
        csv_writer.writerows(id_matrix)
        project_data.field_data["fan_id_matrix.csv"] = np.array([string_io.getvalue()])
        main_window.log_message("风扇ID矩阵已作为元数据添加。")
    except Exception as e:
        main_window.log_message(f"错误: 风扇ID矩阵生成失败 - {e}")
        # 提供一个最小的默认ID矩阵
        default_id_matrix = [[0, 0], [0, 0]]
        string_io = StringIO()
        csv_writer = csv.writer(string_io)
        csv_writer.writerows(default_id_matrix)
        project_data.field_data["fan_id_matrix.csv"] = np.array([string_io.getvalue()])
        main_window.log_message("使用默认风扇ID矩阵。")

    # 6. 添加PQ曲线 (pq_curve.csv)
    try:
        plot_items = main_window.ui.pq_graph_widget.getPlotItem().listDataItems()
        if plot_items:
            pq_curve_data_item = plot_items[0]
            flow_rate, pressure = pq_curve_data_item.getData()
            if flow_rate is not None and pressure is not None:
                pq_string_io = StringIO()
                pq_writer = csv.writer(pq_string_io)
                pq_writer.writerow(['Pressure_Pa', 'FlowRate_m3s'])
                for p, q in zip(pressure, flow_rate): pq_writer.writerow([p, q])
                project_data.field_data["pq_curve.csv"] = np.array([pq_string_io.getvalue()])
                main_window.log_message("PQ曲线数据已作为元数据添加。")
            else:
                main_window.log_message("警告: PQ曲线数据为空。")
        else:
            main_window.log_message("警告: 未找到PQ曲线数据。")
    except Exception as e:
        main_window.log_message(f"错误: PQ曲线数据获取失败 - {e}")
        # 提供默认的PQ曲线数据
        default_pq_data = "Pressure_Pa,FlowRate_m3s\n0,0\n100,0.1\n200,0.05"
        project_data.field_data["pq_curve.csv"] = np.array([default_pq_data])
        main_window.log_message("使用默认PQ曲线数据。")

    # 7. 添加风扇转速数据
    if hasattr(main_window, 'fan_rpm_array') and main_window.fan_rpm_array is not None:
        project_data.field_data["fan_rpm_array"] = main_window.fan_rpm_array
        main_window.log_message("稳态风扇RPM数组(NumPy)已作为元数据添加。")
    elif hasattr(main_window, 'fan_bc_content') and main_window.fan_bc_content:
        project_data.field_data["fan_boundary_conditions.csv"] = np.array([main_window.fan_bc_content])
        main_window.log_message("风扇动态边界条件(CSV)已作为元数据添加。")
    else:
        main_window.log_message("警告: 未找到任何风扇转速数据。")

    project_data.field_data["generation_timestamp"] = np.array([timestamp])
    project_data.field_data["length_unit"] = np.array(["meters"])

    try:
        abs_path = os.path.abspath(filename)
        main_window.log_message(f"准备调用 project_data.save()。")
        project_data.save(filename, binary=True)
        main_window.log_message(f"project_data.save() 调用执行完毕。")
        main_window.log_message(f"计算文件已成功保存至: {filename}")
    except Exception as e:
        import traceback
        main_window.log_message(f"错误: 在 project_data.save() 过程中发生异常: {e}")
        main_window.log_message(f"【严重】详细追溯信息:\n{traceback.format_exc()}")
