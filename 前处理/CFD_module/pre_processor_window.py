# main_window.py

import numpy as np
import vtk
import os
from PySide6.QtWidgets import (QMainWindow, QApplication, QLineEdit, QCheckBox,
                               QFileDialog, QDialog, QVBoxLayout, QComboBox,
                               QPushButton, QLabel, QDialogButtonBox, QFormLayout)
from PySide6.QtGui import QAction
from PySide6.QtCore import QThread, Signal
import pyvista as pv
from pyvistaqt import QtInteractor
from multiprocessing import Pool, cpu_count, freeze_support
from datetime import datetime
import time
import pyqtgraph as pg
from .ui_main_window import Ui_MainWindow
from . import pre_processor_config as config
from .scene_generator import SceneGenerator
from . import file_handler
from . import fan_id_generator

class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    # ... (此类无变化) ...
    def __init__(self, parent=None):
        super().__init__(); self.AddObserver("MiddleButtonPressEvent", self.middle_button_press_event); self.AddObserver("MiddleButtonReleaseEvent", self.middle_button_release_event); self.AddObserver("RightButtonPressEvent", self.right_button_press_event); self.AddObserver("RightButtonReleaseEvent", self.right_button_release_event)
    def middle_button_press_event(self, obj, event): pass
    def middle_button_release_event(self, obj, event): pass
    def right_button_press_event(self, obj, event): self.StartPan()
    def right_button_release_event(self, obj, event): self.EndPan()

# --- 决定性修复: 采用最终的、健壮的面片合并逻辑 ---
# pre_processor_window.py

# ... (文件顶部的其他导入) ...

class FanGeneratorWorker(QThread):
    progress = Signal(int)
    finished = Signal(object)
    def __init__(self, scene_generator, cpu_cores):
        super().__init__()
        self.scene_generator = scene_generator
        # self.cpu_cores is no longer used but kept for API consistency for now
        self.cpu_cores = cpu_cores 
    def run(self):
        start_time = time.time()
        
        self.log("开始使用向量化方法生成风扇阵列...")
        self.progress.emit(5)
        
        try:
            # 1. 调用最终优化版的生成器 (不再需要传入 cpu_cores)
            generator = self.scene_generator.create_fan_array_generator(
                self.progress.emit
            )
            
            # 2. 获取最终的 "Mega-Mesh" MultiBlock 对象
            combined_mesh = next(generator)
            
            end_time = time.time()
            self.log(f"风扇阵列几何体生成完毕。总耗时: {end_time - start_time:.2f} 秒。")
            
            # 3. 发送完成信号
            self.finished.emit(combined_mesh)
        except Exception as e:
            import traceback
            self.log(f"错误: 风扇生成过程中发生异常: {e}")
            self.log(f"详细追溯信息:\n{traceback.format_exc()}")
            self.finished.emit(None)
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Worker] {message}")



class SettingsDialog(QDialog):
    # ... (此类无变化) ...
    def __init__(self, parent=None, current_cores=None):
        super().__init__(parent); self.setWindowTitle("设置"); layout = QVBoxLayout(self)
        form_layout = QFormLayout(); self.combo_cpu_count = QComboBox(); max_cores = cpu_count()
        for i in range(1, max_cores + 1): self.combo_cpu_count.addItem(str(i))
        if current_cores and current_cores <= max_cores: self.combo_cpu_count.setCurrentText(str(current_cores))
        else: self.combo_cpu_count.setCurrentText(str(max(1, max_cores - 2)))
        form_layout.addRow("并行核心数:", self.combo_cpu_count); layout.addLayout(form_layout)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def get_selected_cores(self): return int(self.combo_cpu_count.currentText())

class MainWindow(QMainWindow):
    # ... (此类及以下所有函数均无变化) ...
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow(); self.ui.setupUi(self)
        self.fan_actor = None; self.grid_actors = {}; self.is_grid_globally_visible = False
        self.scene_generator = SceneGenerator(); self.domain_box_actor = None
        self.boundary_face_actors = {}
        self.cpu_cores = max(1, cpu_count() - 2)
        self.debug_logging_enabled = True
        self.is_fan_style_surface = False

        self.plotter = QtInteractor(self.ui.right_panel); self.ui.plotter_layout.addWidget(self.plotter.interactor)
        self.create_actions(); self.populate_toolbar_and_menu()
        self.fan_bc_content = None
        self.fan_rpm_array = None

        # 仿真控制状态管理 - 必须在update_button_states之前初始化
        self.simulation_state = 'idle'  # idle, running, paused, stopped
        self.solver_instance = None
        self.simulation_thread = None
        self.residual_history = {'UX': [], 'UY': [], 'UZ': [], 'Continuity': [], 'k': [], 'epsilon': []}
        self.max_residual_points = 1000

        # 现在可以安全地调用update_button_states了
        self.load_parameters(); self.connect_signals(); self.update_button_states(); self.initialize_plotter()

        # 设置仿真控制
        self.setup_simulation_controls()

    def create_actions(self):
        self.action_save_params = QAction("保存参数", self)
        self.action_generate_fans = QAction("生成风扇", self)
        self.action_generate_grid = QAction("生成网格", self)
        self.action_toggle_style = QAction("切换显示", self); self.action_toggle_style.setShortcut("W")
        self.action_toggle_projection = QAction("切换投影", self)
        self.action_toggle_grid = QAction("切换网格", self); self.action_toggle_grid.setShortcut("G")
        self.action_reset_view = QAction("恢复视图", self); self.action_reset_view.setShortcut("Home")
        self.action_view_xp = QAction("View +X", self); self.action_view_xn = QAction("View -X", self)
        self.action_view_yp = QAction("View +Y", self); self.action_view_yn = QAction("View -Y", self)
        self.action_view_zp = QAction("View +Z", self); self.action_view_zn = QAction("View -Z", self)
        self.action_set_cores = QAction("设置并行核心数...", self)
        self.action_load_params = QAction("读取参数", self)
        self.action_export_fan_ids = QAction("导出风扇ID表", self)
        self.action_save_calc_file = QAction("保存计算文件", self)
        self.action_load_fan_bc = QAction("加载风扇BC文件", self)
        self.action_toggle_debug_log = QAction("开启调试日志", self); self.action_toggle_debug_log.setCheckable(True); self.action_toggle_debug_log.setChecked(True)
        self.action_show_status = QAction("显示仿真状态", self)
        self.action_force_enable = QAction("强制启用仿真", self)

    def populate_toolbar_and_menu(self):
        self.ui.menu_file.addAction(self.action_save_params)
        self.ui.menu_file.addAction(self.action_load_params)
        self.ui.menu_file.addSeparator()
        self.ui.menu_file.addAction(self.action_load_fan_bc)
        self.ui.menu_file.addAction(self.action_export_fan_ids)
        self.ui.menu_file.addAction(self.action_save_calc_file)
        self.ui.menu_file.addSeparator()
        self.ui.menu_settings.addAction(self.action_set_cores)
        self.ui.menu_settings.addAction(self.action_toggle_debug_log)
        self.ui.menu_settings.addSeparator()
        self.ui.menu_settings.addAction(self.action_show_status)
        self.ui.menu_settings.addAction(self.action_force_enable)
        self.ui.toolbar.addAction(self.action_save_params)
        self.ui.toolbar.addAction(self.action_load_params)
        self.ui.toolbar.addSeparator()

        self.ui.toolbar.addAction(self.action_save_calc_file)
        self.ui.toolbar.addAction(self.action_load_fan_bc)
        self.ui.toolbar.addSeparator()

        self.ui.toolbar.addAction(self.action_generate_fans)
        self.ui.toolbar.addAction(self.action_generate_grid)
        self.ui.toolbar.addSeparator()

        self.ui.toolbar.addAction(self.action_toggle_style)
        self.ui.toolbar.addAction(self.action_toggle_projection)
        self.ui.toolbar.addAction(self.action_toggle_grid)
        self.ui.toolbar.addSeparator()

        self.ui.toolbar.addAction(self.action_reset_view)
        self.ui.toolbar.addAction(self.action_view_xp)
        self.ui.toolbar.addAction(self.action_view_xn)
        self.ui.toolbar.addAction(self.action_view_yp)
        self.ui.toolbar.addAction(self.action_view_yn)
        self.ui.toolbar.addAction(self.action_view_zp)
        self.ui.toolbar.addAction(self.action_view_zn)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.ui.log_output.append(f"[{timestamp}][INFO] {message}")

    def load_parameters(self):
        self.ui.le_margin_x.setText(str(config.MARGIN_X)); self.ui.le_margin_y.setText(str(config.MARGIN_Y))
        self.ui.le_inlet_length.setText(str(config.INLET_LENGTH)); self.ui.le_outlet_length.setText(str(config.OUTLET_LENGTH))
        self.ui.le_fan_width.setText(str(config.FAN_WIDTH)); self.ui.le_fan_thickness.setText(str(config.FAN_THICKNESS))
        self.ui.le_fan_hole_diameter.setText(str(config.FAN_HOLE_DIAMETER)); self.ui.le_fan_hub_diameter.setText(str(config.FAN_HUB_DIAMETER))
        self.ui.le_fan_circle_segments.setText(str(config.FAN_CIRCLE_SEGMENTS))
        self.ui.le_comp_grid_x.setText(str(config.COMPONENT_GRID_CELLS[0])); self.ui.le_comp_grid_y.setText(str(config.COMPONENT_GRID_CELLS[1])); self.ui.le_comp_grid_z.setText(str(config.COMPONENT_GRID_CELLS[2]))
        self.ui.le_env_grid_x.setText(str(config.ENVIRONMENT_GRID_SIZE[0])); self.ui.le_env_grid_y.setText(str(config.ENVIRONMENT_GRID_SIZE[1])); self.ui.le_env_grid_z.setText(str(config.ENVIRONMENT_GRID_SIZE[2]))
        self.ui.le_rpm1.setText(str(config.FAN_RPM_1)); self.ui.check_dir1.setChecked(config.FAN_DIRECTION_1_IS_CW)
        self.ui.le_rpm2.setText(str(config.FAN_RPM_2)); self.ui.check_dir2.setChecked(config.FAN_DIRECTION_2_IS_CW)
        self.load_pq_curve(config.DEFAULT_PQ_CURVE_FILE)
        self.ui.le_stretch_ratio_z.setText(str(config.STRETCH_RATIO_Z))
        self.ui.le_stretch_ratio_xy.setText(str(config.STRETCH_RATIO_XY))

    def connect_signals(self):
        self.action_generate_fans.triggered.connect(self.start_fan_generation); self.action_generate_grid.triggered.connect(self.generate_grid)
        self.action_toggle_style.triggered.connect(self.toggle_style); self.action_toggle_projection.triggered.connect(self.toggle_projection)
        self.action_toggle_grid.triggered.connect(self.toggle_grid_global_visibility); self.action_reset_view.triggered.connect(self.reset_view_to_default)
        self.action_view_xp.triggered.connect(lambda: self.set_view('x')); self.action_view_xn.triggered.connect(lambda: self.set_view('x', negative=True))
        self.action_view_yp.triggered.connect(lambda: self.set_view('y')); self.action_view_yn.triggered.connect(lambda: self.set_view('y', negative=True))
        self.action_view_zp.triggered.connect(lambda: self.set_view('z')); self.action_view_zn.triggered.connect(lambda: self.set_view('z', negative=True))
        self.action_set_cores.triggered.connect(self.open_settings_dialog)
        self.action_toggle_debug_log.triggered.connect(self.toggle_debug_logging)
        self.action_show_status.triggered.connect(self.show_simulation_status)
        self.action_force_enable.triggered.connect(self.force_enable_simulation)
        for line_edit in self.ui.tab_global_params.findChildren(QLineEdit):
            line_edit.editingFinished.connect(self.on_parameter_changed)
        for checkbox in self.ui.tab_global_params.findChildren(QCheckBox):
            checkbox.stateChanged.connect(self.on_parameter_changed)
        self.ui.btn_load_pq.clicked.connect(self.select_and_load_pq_curve)
        self.action_save_params.triggered.connect(self.save_parameters_dialog)
        self.action_load_params.triggered.connect(self.load_parameters_dialog)
        self.action_export_fan_ids.triggered.connect(self.export_fan_id_table)
        self.action_save_calc_file.triggered.connect(self.save_calculation_file_dialog)
        self.action_load_fan_bc.triggered.connect(self.load_fan_bc_dialog)
    def toggle_debug_logging(self, checked):
        self.debug_logging_enabled = checked
        self.log_message(f"调试日志已 {'开启' if checked else '关闭'}.")

    def open_settings_dialog(self):
        dialog = SettingsDialog(self, current_cores=self.cpu_cores)
        if dialog.exec():
            self.cpu_cores = dialog.get_selected_cores()
            self.log_message(f"并行核心数已设置为: {self.cpu_cores}")

    def on_parameter_changed(self):
        print("参数已更改，正在更新计算域...")
        if self._update_config_from_ui():
            if self.domain_box_actor: self.plotter.remove_actor(self.domain_box_actor)
            self.domain_box_mesh = pv.Box(bounds=list(config.DOMAIN_BOUNDS.values()))
            self.domain_box_actor = self.plotter.add_mesh(self.domain_box_mesh, style='wireframe', color='black', line_width=2)
            self.log_message(f"计算域已更新。")
            self.update_boundary_faces()
            self.plotter.render()

    def _update_config_from_ui(self):
        try:
            # 【核心修复】首先更新 IS_GROUNDED 状态
            config.IS_GROUNDED = self.ui.check_grounded.isChecked()
            config.MARGIN_X = float(self.ui.le_margin_x.text())
            config.MARGIN_Y = float(self.ui.le_margin_y.text())
            
            # UI交互逻辑：如果贴地，则Y裕量输入框不可用
            if self.ui.check_grounded.isChecked():
                self.ui.le_margin_y.setEnabled(False)
            else:
                self.ui.le_margin_y.setEnabled(True)
            config.INLET_LENGTH = float(self.ui.le_inlet_length.text())
            config.OUTLET_LENGTH = float(self.ui.le_outlet_length.text())
            config.FAN_WIDTH = float(self.ui.le_fan_width.text())
            config.FAN_THICKNESS = float(self.ui.le_fan_thickness.text())
            config.FAN_HOLE_DIAMETER = float(self.ui.le_fan_hole_diameter.text())
            config.FAN_HUB_DIAMETER = float(self.ui.le_fan_hub_diameter.text())
            config.FAN_CIRCLE_SEGMENTS = int(self.ui.le_fan_circle_segments.text())
            config.COMPONENT_GRID_CELLS = (int(self.ui.le_comp_grid_x.text()), int(self.ui.le_comp_grid_y.text()), int(self.ui.le_comp_grid_z.text()))
            config.ENVIRONMENT_GRID_SIZE = (float(self.ui.le_env_grid_x.text()), float(self.ui.le_env_grid_y.text()), float(self.ui.le_env_grid_z.text()))
            config.STRETCH_RATIO_Z = float(self.ui.le_stretch_ratio_z.text())
            config.STRETCH_RATIO_XY = float(self.ui.le_stretch_ratio_xy.text())
            
            # 现在调用 update_domain_bounds() 会自动处理贴地逻辑
            config.update_domain_bounds()
            
            # 【核心修复】移除旧的、手动的 ymin 修改逻辑
            # if self.ui.check_grounded.isChecked(): config.DOMAIN_BOUNDS['ymin'] = 0 # <-- 此行被删除
            return True
        except (ValueError, IndexError) as e:
            self.ui.status_label.setText(f"错误: 参数输入无效: {e}")
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 错误: 参数输入无效: {e}")
            return False

    def initialize_plotter(self):
        # 初始化3D场景
        self.plotter.add_axes()
        self.plotter.set_background('white')
        style = CustomInteractorStyle()
        self.plotter.interactor.SetInteractorStyle(style)
        self.on_parameter_changed()
        self.reset_view_to_default()
        self.plotter.enable_parallel_projection()
        self.log_message("3D场景初始化完毕，默认使用平行投影。")
        self.plotter.iren.add_observer("EndInteractionEvent", self.update_grid_visibility)

        # --- 新增: 初始化残差图 ---
        self.ui.residual_plot_widget.setBackground('w')
        self.ui.residual_plot_widget.setLabel('left', 'Residual', color='k')
        self.ui.residual_plot_widget.setLabel('bottom', 'Iteration', color='k')
        self.ui.residual_plot_widget.showGrid(x=True, y=True)
        self.ui.residual_plot_widget.setLogMode(y=True) # 设置Y轴为对数坐标
        self.ui.residual_plot_widget.addLegend()

        # 为每条曲线创建空的PlotDataItem
        self.residual_curves = {
            'Ux': self.ui.residual_plot_widget.plot(pen='r', name='Ux'),
            'Uy': self.ui.residual_plot_widget.plot(pen='g', name='Uy'),
            'Uz': self.ui.residual_plot_widget.plot(pen='b', name='Uz'),
            'Continuity': self.ui.residual_plot_widget.plot(pen='c', name='Continuity'),
            'k': self.ui.residual_plot_widget.plot(pen='m', name='k'),
            'epsilon': self.ui.residual_plot_widget.plot(pen=(255, 165, 0), name='epsilon') # Orange
        }
        self.log_message("残差监控图初始化完毕。")


    def reset_view_to_default(self):
        center = self.domain_box_mesh.center
        distance = np.linalg.norm(np.array(self.domain_box_mesh.bounds[1::2]) - np.array(self.domain_box_mesh.bounds[0::2]))
        position = (center[0] + distance, center[1], center[2] + distance)
        view_up = (0.0, 1.0, 0.0)
        self.plotter.camera.SetPosition(position); self.plotter.camera.SetFocalPoint(center); self.plotter.camera.SetViewUp(view_up)
        self.plotter.reset_camera(); self.update_grid_visibility()

    def update_button_states(self, is_generating=False):
        fans_exist = self.fan_actor is not None; grid_exist = bool(self.grid_actors)
        self.action_generate_fans.setEnabled(not is_generating); self.action_generate_grid.setEnabled(not is_generating)
        self.action_toggle_style.setEnabled(fans_exist and not is_generating)
        self.action_toggle_grid.setEnabled(grid_exist and not is_generating)
        self.action_save_calc_file.setEnabled(grid_exist and not is_generating)

        # 更新仿真控制按钮状态
        self.update_simulation_button_states()

    def start_fan_generation(self):
        if not self._update_config_from_ui(): return
        if self.fan_actor: self.plotter.remove_actor(self.fan_actor); self.fan_actor = None
        self.update_button_states(is_generating=True)
        self.ui.status_label.setText("状态: 正在生成风扇..."); self.ui.progress_bar.setValue(0); self.ui.progress_bar.setVisible(True)
        
        self.fan_worker = FanGeneratorWorker(self.scene_generator, self.cpu_cores)
        self.fan_worker.progress.connect(self.update_progress)
        self.fan_worker.finished.connect(self.on_fan_generation_finished)
        self.fan_worker.start()

    def update_progress(self, value): self.ui.progress_bar.setValue(value)

    def on_fan_generation_finished(self, combined_mesh):
        self.ui.status_label.setText("状态: 正在将模型添加到场景...")
        QApplication.processEvents()
        
        self.fan_actor = self.plotter.add_mesh(combined_mesh, style='wireframe', color='lightblue', show_edges=True)
        self.is_fan_style_surface = False
        
        self.plotter.reset_camera()
        self.ui.status_label.setText("状态: 就绪"); self.ui.progress_bar.setVisible(False)
        self.update_button_states(is_generating=False)
        self.log_message(f"成功生成 {config.FAN_ARRAY_SHAPE[0] * config.FAN_ARRAY_SHAPE[1]} 个风扇。")
        self.log_message("风扇显示模式默认为: 线框")

    def generate_grid(self):
        if not self._update_config_from_ui(): return
        if self.grid_actors:
            for actor in self.grid_actors.values(): self.plotter.remove_actor(actor)
        
        self.ui.status_label.setText("状态: 正在生成网格...")
        QApplication.processEvents()
        
        grid_meshes, stats = self.scene_generator.create_grid_geometry()
        self.grid_actors = {}
        for name, mesh in grid_meshes.items():
            if mesh.n_points > 0:
                actor = self.plotter.add_mesh(mesh, color='black'); actor.visibility = False
                self.grid_actors[name] = actor
        
        self.ui.status_label.setText("状态: 就绪")
        self.update_button_states()
        self.update_grid_visibility()
        
        self.log_message("网格生成完毕。")
        self.log_message(f"  - 总网格数: {stats['total_cells']:,}")
        self.log_message(f"  - 最小网格尺寸 (dx,dy,dz): ({stats['min_size'][0]:.2f}, {stats['min_size'][1]:.2f}, {stats['min_size'][2]:.2f}) mm")
        self.log_message(f"  - 最大网格尺寸 (dx,dy,dz): ({stats['max_size'][0]:.2f}, {stats['max_size'][1]:.2f}, {stats['max_size'][2]:.2f}) mm")

    def toggle_projection(self):
        if self.plotter.camera.parallel_projection:
            self.plotter.disable_parallel_projection()
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 切换为透视投影。")
        else:
            self.plotter.enable_parallel_projection()
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 切换为平行投影。")

    def toggle_style(self):
        if not self.fan_actor: return
        if self.is_fan_style_surface:
            self.fan_actor.prop.style = 'wireframe'; log_text = "线框"; self.is_fan_style_surface = False
        else:
            self.fan_actor.prop.style = 'surface'; log_text = "实体"; self.is_fan_style_surface = True
        self.log_message(f"风扇显示模式切换为: {log_text}"); self.plotter.render()

    def toggle_grid_global_visibility(self):
        if not self.grid_actors: return
        self.is_grid_globally_visible = not self.is_grid_globally_visible
        self.log_message(f"网格显示已 {'开启' if self.is_grid_globally_visible else '关闭'}.")
        self.update_grid_visibility()

    def update_grid_visibility(self, *args):
        if self.debug_logging_enabled:
            print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 正在更新网格可见性...")
        if not self.grid_actors: return
        camera_pos = np.array(self.plotter.camera.position); domain_center = self.domain_box_mesh.center
        view_vector = domain_center - camera_pos
        normals = {'xmax': np.array([1, 0, 0]), 'xmin': np.array([-1, 0, 0]), 'ymax': np.array([0, 1, 0]), 'ymin': np.array([0, -1, 0]), 'zmax': np.array([0, 0, 1]), 'zmin': np.array([0, 0, -1]),}
        for name, actor in self.grid_actors.items():
            if self.is_grid_globally_visible:
                dot_product = np.dot(view_vector, normals[name]); actor.visibility = int(dot_product >= 1e-6)
            else:
                actor.visibility = 0
        self.plotter.render()
    
    def set_view(self, axis, negative=False):
        if self.debug_logging_enabled:
            print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 切换到 {axis} {'负' if negative else '正'}向视图。")
        center = self.domain_box_mesh.center
        distance = np.linalg.norm(np.array(self.domain_box_mesh.bounds[1::2]) - np.array(self.domain_box_mesh.bounds[0::2])) * 1.5
        position = list(center); view_up = [0.0, 1.0, 0.0]
        if axis == 'x': position[0] += distance * (1 if negative else -1)
        elif axis == 'y': position[1] += distance * (1 if negative else -1); view_up = [0.0, 0.0, -1.0]
        elif axis == 'z': position[2] += distance * (1 if negative else -1)
        self.plotter.camera.SetPosition(position); self.plotter.camera.SetFocalPoint(center); self.plotter.camera.SetViewUp(view_up)
        self.plotter.reset_camera(); self.update_grid_visibility()

    def update_boundary_faces(self):
        if not self._update_config_from_ui(): return

        for name, actor in list(self.boundary_face_actors.items()):
            self.plotter.remove_actor(actor)
            del self.boundary_face_actors[name]
            if self.debug_logging_enabled:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 已移除旧的 {name} 边界。")

        bds = config.DOMAIN_BOUNDS
        xmin, xmax = bds['xmin'], bds['xmax']; ymin, ymax = bds['ymin'], bds['ymax']; zmin, zmax = bds['zmin'], bds['zmax']
        face_corners = {
            'xp': [[xmax, ymin, zmin], [xmax, ymax, zmin], [xmax, ymax, zmax], [xmax, ymin, zmax]], 'xn': [[xmin, ymin, zmax], [xmin, ymax, zmax], [xmin, ymax, zmin], [xmin, ymin, zmin]],
            'yp': [[xmin, ymax, zmin], [xmax, ymax, zmin], [xmax, ymax, zmax], [xmin, ymax, zmax]], 'yn': [[xmin, ymin, zmax], [xmax, ymin, zmax], [xmax, ymin, zmin], [xmin, ymin, zmin]],
            'zp': [[xmin, ymin, zmax], [xmax, ymin, zmax], [xmax, ymax, zmax], [xmin, ymax, zmax]], 'zn': [[xmin, ymin, zmin], [xmin, ymax, zmin], [xmax, ymax, zmin], [xmax, ymin, zmin]],
        }
        checkbox_map = {
            'xp': self.ui.check_boundary_xp, 'xn': self.ui.check_boundary_xn, 'yp': self.ui.check_boundary_yp, 'yn': self.ui.check_boundary_yn,
            'zp': self.ui.check_boundary_zp, 'zn': self.ui.check_boundary_zn,
        }
        
        for name, checkbox in checkbox_map.items():
            if checkbox.isChecked():
                points = face_corners[name]; faces = [4, 0, 1, 2, 3]
                plane = pv.PolyData(points, faces=faces)
                actor = self.plotter.add_mesh(plane, color='grey', opacity=0.5)
                self.boundary_face_actors[name] = actor
                if self.debug_logging_enabled:
                     print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 已重新生成 {name} 边界。")

    def select_and_load_pq_curve(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择PQ曲线文件", "", "文本文件 (*.txt);;所有文件 (*)")
        if filename:
            self.load_pq_curve(filename)

    def load_pq_curve(self, filename):
        try:
            # 1. 设置背景为白色
            self.ui.pq_graph_widget.setBackground('w')
            
            # 2. 获取坐标轴并设置颜色
            axis_pen = pg.mkPen(color='k', width=1)
            self.ui.pq_graph_widget.getAxis('left').setPen(axis_pen)
            self.ui.pq_graph_widget.getAxis('bottom').setPen(axis_pen)
            self.ui.pq_graph_widget.getAxis('left').setTextPen(axis_pen)
            self.ui.pq_graph_widget.getAxis('bottom').setTextPen(axis_pen)

            data = np.loadtxt(filename, comments='#', delimiter=',', encoding='utf-8')
            pressure = data[:, 0]; flow_rate = data[:, 1]
            self.ui.pq_graph_widget.clear()
            
            # 3. 只用蓝色的线绘制，去掉点
            self.ui.pq_graph_widget.plot(flow_rate, pressure, pen=pg.mkPen('b', width=2))
            
            # 4. 设置坐标轴标签和网格
            self.ui.pq_graph_widget.setLabel('left', '静压 (Pa)'); self.ui.pq_graph_widget.setLabel('bottom', '流量 (m³/s)')
            self.ui.pq_graph_widget.showGrid(x=True, y=True)
            
            # 5. 移除标题
            # self.ui.pq_graph_widget.setTitle('风扇PQ曲线') # 此行被注释掉

            self.log_message(f"成功加载并绘制PQ曲线: {filename}")
        except Exception as e:
            self.log_message(f"错误: 加载PQ曲线失败 - {e}")
    def save_parameters_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存参数文件", "", "JSON 文件 (*.json);;所有文件 (*)")
        if filename:
            file_handler.save_parameters(self, filename)

    def load_parameters_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, "读取参数文件", "", "JSON 文件 (*.json);;所有文件 (*)")
        if filename:
            file_handler.load_parameters(self, filename)

    def export_fan_id_table(self):
        filename, _ = QFileDialog.getSaveFileName(self, "导出风扇ID表", "fan_id_matrix.csv", "CSV 文件 (*.csv);;所有文件 (*)")
        if filename:
            id_matrix = fan_id_generator.generate_fan_id_matrix()
            fan_id_generator.save_id_matrix_to_csv(id_matrix, filename)
            self.log_message(f"风扇ID表已导出至: {filename}")

    def save_calculation_file_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "保存计算文件", 
            "project.vtm",
            "VTK MultiBlock 文件 (*.vtm);;所有文件 (*)"
        )
        
        if filename:
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 用户选择的文件路径: {filename}")
            file_handler.save_calculation_file(self, filename)
        else:
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 用户取消了保存操作，未生成任何文件。")
            self.ui.status_label.setText("状态: 保存已取消")

    def load_fan_bc_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, "加载风扇动态边界条件文件", "", "CSV 文件 (*.csv);;所有文件 (*)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.fan_bc_content = f.read()
                self.log_message(f"成功加载风扇动态边界条件文件: {filename}")
            except Exception as e:
                self.log_message(f"错误: 加载风扇BC文件失败 - {e}")
                self.fan_bc_content = None
        # --- 新增: 用于接收内存数据的方法 ---
    def receive_fan_rpm_array(self, rpm_array: np.ndarray):
        """
        从主控程序接收风扇RPM的NumPy数组并存储在内存中。
        接收后立即在控制台打印 FanID 和 RPM 矩阵以供验证。
        """
        # --- 【新增】导入 FanID 生成器 ---
        from .fan_id_generator import generate_fan_id_matrix

        if rpm_array is not None and rpm_array.shape == (40, 40):
            self.fan_rpm_array = rpm_array
            self.fan_bc_content = None 
            self.log_message("成功从主控制程序接收到内存中的风扇RPM数组。")
            self.ui.status_label.setText("状态: 已从主控加载风扇RPM数组")

            # --- 【核心修改】使用循环打印 FanID 和 RPM ---
            # 1. 生成与UI布局一致的FanID矩阵 (40x40, [0][0]是左上角)
            id_matrix = generate_fan_id_matrix()
            
            # 2. 翻转RPM数组，使其打印顺序与ID矩阵和UI一致 (40x40, [0][0]是左上角)
            rpm_array_to_print = np.flipud(rpm_array)
            
            print("\n--- Verifying Received Fan RPM Matrix with IDs (Top-Down, Left-to-Right) ---")
            
            # 3. 遍历矩阵并格式化输出
            for r in range(rpm_array_to_print.shape[0]):
                row_string = ""
                for c in range(rpm_array_to_print.shape[1]):
                    fan_id = id_matrix[r][c]
                    rpm = rpm_array_to_print[r, c]
                    # 格式化字符串，确保对齐
                    row_string += f"[{fan_id}: {rpm:>5}] "
                print(row_string) # 打印一整行

            print("--------------------------------------------------------------------------------\n")

        else:
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 警告: 从主控程序接收到的风扇RPM数组无效或为空。")

    def receive_time_series_data(self, time_series_data):
        """
        从风墙设置界面接收时间序列数据并生成CSV文件
        """
        try:
            # 验证数据结构
            if not all(key in time_series_data for key in ['time_points', 'rpm_data', 'metadata']):
                self.log_message("错误: 接收到的时间序列数据格式不正确")
                return

            # 存储数据
            self.time_series_data = time_series_data
            self.log_message("成功接收到时间序列数据")

            # 提取关键信息
            time_points = time_series_data['time_points']
            rpm_data = time_series_data['rpm_data']  # shape: (time, rows, cols)
            metadata = time_series_data['metadata']
            max_rpm = time_series_data.get('max_rpm', 15000)
            time_resolution = time_series_data.get('time_resolution', 0.1)

            # 生成CSV文件
            self.generate_time_series_csv(time_points, rpm_data, metadata, max_rpm, time_resolution)

            # 同时生成第一个时间点的RPM数组用于预览
            first_time_point_rpm = rpm_data[0] if len(rpm_data) > 0 else None
            if first_time_point_rpm is not None:
                self.receive_fan_rpm_array(first_time_point_rpm)
                self.log_message(f"已加载第一个时间点的风扇RPM数据 (时间: {time_points[0]:.1f}s)")

        except Exception as e:
            self.log_message(f"处理时间序列数据时出错: {str(e)}")
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] 时间序列数据处理错误: {e}")

    def generate_time_series_csv(self, time_points, rpm_data, metadata, max_rpm, time_resolution):
        """
        生成时间序列数据的CSV文件
        """
        import csv
        import os
        from datetime import datetime

        # 创建文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"time_series_fan_data_{timestamp}.csv"

        # 获取项目根目录
        # 从当前文件位置向上查找项目根目录（包含main_app.py的目录）
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)

        # 向上查找项目根目录
        project_root = current_dir
        while project_root != os.path.dirname(project_root):  # 直到到达文件系统根目录
            if os.path.exists(os.path.join(project_root, 'main_app.py')):
                break
            project_root = os.path.dirname(project_root)

        # 如果没找到main_app.py，使用当前目录的上两级目录
        if not os.path.exists(os.path.join(project_root, 'main_app.py')):
            project_root = os.path.dirname(os.path.dirname(current_file))

        # 确保保存目录存在
        csv_save_dir = os.path.join(project_root, 'csv_outputs')
        os.makedirs(csv_save_dir, exist_ok=True)

        csv_path = os.path.join(csv_save_dir, csv_filename)

        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # 写入元数据头部
                writer.writerow(['# 时间序列风扇转速数据'])
                writer.writerow([f'# 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'# 数据来源: {metadata.get("generated_by", "Unknown")}'])
                writer.writerow([f'# 描述: {metadata.get("description", "No description")}'])
                writer.writerow([f'# 最大转速: {max_rpm} RPM'])
                writer.writerow([f'# 时间分辨率: {time_resolution} s'])
                writer.writerow([f'# 时间点数量: {len(time_points)}'])
                writer.writerow([f'# 网格形状: {rpm_data.shape[1]}x{rpm_data.shape[2]}'])
                writer.writerow([])

                # 写入列标题
                writer.writerow(['Time(s)'] + [f'Fan_{i}' for i in range(rpm_data.shape[1] * rpm_data.shape[2])])

                # 写入数据
                for time_idx, time_point in enumerate(time_points):
                    # 展平2D风扇数据为1D数组
                    flat_rpm_data = rpm_data[time_idx].flatten()
                    row = [f"{time_point:.3f}"] + [str(int(rpm)) for rpm in flat_rpm_data]
                    writer.writerow(row)

            self.log_message(f"CSV文件已生成: {csv_path}")
            print(f"\n时间序列数据CSV文件已保存: {csv_path}")
            print(f"文件包含 {len(time_points)} 个时间点，{rpm_data.shape[1] * rpm_data.shape[2]} 个风扇的数据")

            # CSV文件已静默保存，不再弹出提示
            # self._offer_open_directory(csv_path)

        except Exception as e:
            self.log_message(f"生成CSV文件失败: {str(e)}")
            if self.debug_logging_enabled:
                print(f"[{datetime.now().strftime('%H:%M:%S')}][DEBUG] CSV生成错误: {e}")

    # ================ 仿真控制功能 ================

    def setup_simulation_controls(self):
        """设置仿真控制按钮的信号连接"""
        self.ui.sim_run_action.triggered.connect(self.start_simulation)
        self.ui.sim_pause_action.triggered.connect(self.pause_simulation)
        self.ui.sim_stop_action.triggered.connect(self.stop_simulation)

        # 初始化残差监控图表
        self.setup_residual_plot()

        # 更新按钮状态
        self.update_simulation_button_states()

    def update_simulation_button_states(self):
        """更新仿真按钮的启用/禁用状态"""
        has_grid = bool(self.grid_actors)  # 检查是否有网格
        has_fans = bool(self.fan_actor)    # 检查是否有风扇
        has_boundary = bool(self.boundary_face_actors)  # 检查是否有边界条件

        # 检查仿真设置是否有效
        try:
            max_iterations = int(self.ui.le_max_iterations.text())
            residual_tolerance = float(self.ui.le_residual_tolerance.text())
            has_valid_settings = max_iterations > 0 and residual_tolerance > 0
        except (ValueError, AttributeError):
            has_valid_settings = False

        # 所有条件都满足时才能运行仿真
        can_run = has_grid and has_fans and has_boundary and has_valid_settings

        if self.simulation_state == 'idle':
            self.ui.sim_run_action.setEnabled(can_run)
            self.ui.sim_pause_action.setEnabled(False)
            self.ui.sim_stop_action.setEnabled(False)
        elif self.simulation_state == 'running':
            self.ui.sim_run_action.setEnabled(False)
            self.ui.sim_pause_action.setEnabled(True)
            self.ui.sim_stop_action.setEnabled(True)
        elif self.simulation_state == 'paused':
            self.ui.sim_run_action.setEnabled(True)
            self.ui.sim_pause_action.setEnabled(False)
            self.ui.sim_stop_action.setEnabled(True)
        elif self.simulation_state == 'stopped':
            self.ui.sim_run_action.setEnabled(can_run)
            self.ui.sim_pause_action.setEnabled(False)
            self.ui.sim_stop_action.setEnabled(False)

        # 更新状态标签
        self.update_status_display()

    def update_status_display(self):
        """更新状态显示"""
        status_messages = {
            'idle': '状态: 就绪' if self._check_simulation_readiness() else '状态: 等待网格/风扇/边界条件',
            'running': '状态: 仿真运行中...',
            'paused': '状态: 仿真已暂停',
            'stopped': '状态: 仿真已停止'
        }
        self.ui.status_label.setText(status_messages.get(self.simulation_state, '状态: 未知'))

    def _check_simulation_readiness(self):
        """检查仿真是否准备就绪"""
        has_grid = bool(self.grid_actors)
        has_fans = bool(self.fan_actor)
        has_boundary = bool(self.boundary_face_actors)

        # 添加详细的状态检查日志
        if self.debug_logging_enabled:
            self.log_message(f"仿真状态检查:")
            self.log_message(f"  - 网格: {'存在' if has_grid else '不存在'} (数量: {len(self.grid_actors)})")
            self.log_message(f"  - 风扇: {'存在' if has_fans else '不存在'}")
            self.log_message(f"  - 边界条件: {'存在' if has_boundary else '不存在'} (数量: {len(self.boundary_face_actors)})")

        return has_grid and has_fans and has_boundary

    def show_simulation_status(self):
        """显示详细的仿真状态信息（调试用）"""
        status_info = {
            "网格数量": len(self.grid_actors),
            "风扇状态": "存在" if self.fan_actor else "不存在",
            "边界条件数量": len(self.boundary_face_actors),
            "最大迭代次数": self.ui.le_max_iterations.text(),
            "收敛判据": self.ui.le_residual_tolerance.text(),
            "仿真状态": self.simulation_state
        }

        self.log_message("=== 详细仿真状态 ===")
        for key, value in status_info.items():
            self.log_message(f"{key}: {value}")

    def force_enable_simulation(self):
        """强制启用仿真按钮（调试用）"""
        self.ui.sim_run_action.setEnabled(True)
        self.ui.sim_pause_action.setEnabled(True)
        self.ui.sim_stop_action.setEnabled(True)
        self.log_message("警告: 仿真按钮已强制启用（调试模式）")
        self.log_message("注意：这可能导致仿真失败，请确保已准备好所有条件")

    def start_simulation(self):
        """开始仿真"""
        if not self._check_simulation_readiness():
            self.log_message("错误: 仿真条件不满足，请确保已生成网格、风扇和边界条件")
            return

        try:
            self.log_message("开始启动CFD仿真...")
            self.simulation_state = 'running'
            self.update_simulation_button_states()

            # 重置残差历史
            self.residual_history = {key: [] for key in self.residual_history.keys()}

            # 创建并启动求解器
            self._create_and_run_solver()

        except Exception as e:
            self.log_message(f"启动仿真失败: {str(e)}")
            self.simulation_state = 'idle'
            self.update_simulation_button_states()

    def pause_simulation(self):
        """暂停仿真"""
        if self.simulation_state == 'running':
            self.simulation_state = 'paused'
            self.log_message("仿真已暂停")
            self.update_simulation_button_states()

    def stop_simulation(self):
        """停止仿真"""
        self.simulation_state = 'stopped'
        self.log_message("仿真已停止")

        if self.solver_instance:
            # 这里可以添加清理逻辑
            self.solver_instance = None

        self.update_simulation_button_states()

    def _create_and_run_solver(self):
        """创建并运行求解器"""
        try:
            # 导入求解器
            from 求解器.solver.solver import Solver
            from 求解器 import solver_config

            # 获取配置参数
            max_iterations = int(self.ui.le_max_iterations.text())
            residual_tolerance = float(self.ui.le_residual_tolerance.text())

            # 更新求解器配置
            config = solver_config.get_config()
            config['simulation_control']['max_iterations'] = max_iterations
            config['simulation_control']['convergence_criterion'] = residual_tolerance

            # 创建求解器实例（这里需要实际的网格文件路径）
            # 暂时使用占位符，实际使用时需要从界面获取或生成网格文件
            vtm_file = self._get_vtm_file_path()

            if not vtm_file or not os.path.exists(vtm_file):
                self.log_message("错误: 找不到网格文件，无法启动求解器")
                self.simulation_state = 'idle'
                self.update_simulation_button_states()
                return

            # 创建求解器
            device = 'gpu' if self._check_gpu_available() else 'cpu'
            self.solver_instance = Solver(vtm_file, device=device, debug_mode=self.debug_logging_enabled)

            # 在后台线程中运行求解器
            self._run_solver_in_background()

        except Exception as e:
            self.log_message(f"创建求解器失败: {str(e)}")
            self.simulation_state = 'idle'
            self.update_simulation_button_states()

    def _run_solver_in_background(self):
        """在后台线程中运行求解器"""
        from PySide6.QtCore import QThread, Signal

        class SimulationThread(QThread):
            progress = Signal(str)
            residual_update = Signal(dict)
            finished = Signal(bool, str)

            def __init__(self, solver):
                super().__init__()
                self.solver = solver
                self.should_stop = False
                self.is_paused = False

            def run(self):
                try:
                    self.progress.emit("开始稳态仿真计算...")

                    # 这里调用求解器的实际运行方法
                    # 由于求解器的实际实现可能不同，这里提供一个框架
                    for iteration in range(100):  # 占位符迭代次数
                        if self.should_stop:
                            break

                        while self.is_paused:
                            self.msleep(100)
                            if self.should_stop:
                                break

                        if self.should_stop:
                            break

                        # 模拟残差计算
                        if iteration % 5 == 0:  # 每5次迭代更新一次残差
                            residuals = {
                                'UX': 1e-3 * (1 + np.random.random()),
                                'UY': 1e-3 * (1 + np.random.random()),
                                'UZ': 1e-3 * (1 + np.random.random()),
                                'Continuity': 1e-4 * (1 + np.random.random()),
                                'k': 1e-2 * (1 + np.random.random()),
                                'epsilon': 1e-2 * (1 + np.random.random())
                            }
                            self.residual_update.emit(residuals)
                            self.progress.emit(f"迭代 {iteration+1}/100")

                        self.msleep(100)  # 模拟计算时间

                    self.finished.emit(True, "仿真完成")

                except Exception as e:
                    self.finished.emit(False, f"仿真失败: {str(e)}")

        # 创建并启动仿真线程
        self.simulation_thread = SimulationThread(self.solver_instance)
        self.simulation_thread.progress.connect(self._on_simulation_progress)
        self.simulation_thread.residual_update.connect(self._update_residual_plot)
        self.simulation_thread.finished.connect(self._on_simulation_finished)
        self.simulation_thread.start()

    def _on_simulation_progress(self, message):
        """处理仿真进度更新"""
        self.log_message(message)

    def _update_residual_plot(self, residuals):
        """更新残差监控图表"""
        try:
            # 添加新的残差数据
            for key, value in residuals.items():
                if key in self.residual_history:
                    self.residual_history[key].append(value)
                    # 限制数据点数量
                    if len(self.residual_history[key]) > self.max_residual_points:
                        self.residual_history[key] = self.residual_history[key][-self.max_residual_points:]

            # 更新图表
            self._refresh_residual_plot()

        except Exception as e:
            if self.debug_logging_enabled:
                print(f"更新残差图表失败: {e}")

    def _refresh_residual_plot(self):
        """刷新残差监控图表"""
        try:
            self.ui.residual_plot_widget.clear()

            # 为每个残差类型绘制曲线
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

            for i, (key, values) in enumerate(self.residual_history.items()):
                if values:  # 确保有数据
                    color = colors[i % len(colors)]
                    self.ui.residual_plot_widget.plot(
                        values,
                        pen=pg.mkPen(color, width=2),
                        name=key
                    )

            # 设置图表属性
            self.ui.residual_plot_widget.setLabel('left', '残差值')
            self.ui.residual_plot_widget.setLabel('bottom', '迭代次数')
            self.ui.residual_plot_widget.setLogMode(y=True)  # Y轴对数坐标
            self.ui.residual_plot_widget.showGrid(x=True, y=True)
            self.ui.residual_plot_widget.addLegend()

        except Exception as e:
            if self.debug_logging_enabled:
                print(f"刷新残差图表失败: {e}")

    def setup_residual_plot(self):
        """设置残差监控图表"""
        try:
            self.ui.residual_plot_widget.setLabel('left', '残差值')
            self.ui.residual_plot_widget.setLabel('bottom', '迭代次数')
            self.ui.residual_plot_widget.setLogMode(y=True)
            self.ui.residual_plot_widget.showGrid(x=True, y=True)
            self.ui.residual_plot_widget.setTitle("残差监控")
        except Exception as e:
            if self.debug_logging_enabled:
                print(f"设置残差图表失败: {e}")

    def _on_simulation_finished(self, success, message):
        """处理仿真完成"""
        self.simulation_state = 'stopped' if success else 'idle'
        self.log_message(message)
        self.update_simulation_button_states()

    def _get_vtm_file_path(self):
        """获取VTM网格文件路径"""
        # 这里需要根据实际情况实现
        # 可能需要从网格生成过程中获取，或让用户选择
        # 暂时返回None，需要后续完善
        return None

    def _check_gpu_available(self):
        """检查GPU是否可用"""
        try:
            import cupy as cp
            return cp.is_available()
        except ImportError:
            return False

    def closeEvent(self, event):
        """
        重写窗口关闭事件。
        在窗口正式关闭前，安全地关闭PyVista的plotter。
        """
        print("CFD_module window is closing. Safely shutting down the plotter...")
        
        # 1. 明确地关闭 plotter，释放VTK和OpenGL资源
        self.plotter.close()
        
        # 2. 调用父类的 closeEvent，让Qt继续执行正常的关闭流程
        super().closeEvent(event)





