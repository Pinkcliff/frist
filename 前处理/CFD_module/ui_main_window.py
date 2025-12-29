# ui_main_window.py

from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                               QProgressBar, QLabel, QGroupBox, QFormLayout,
                               QLineEdit, QComboBox, QCheckBox, QTextEdit,
                               QGridLayout, QTabWidget, QToolBar, QMenuBar)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt
import pyqtgraph as pg

class Ui_MainWindow:
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("风墙前处理 (Wind Wall Preprocessor)")
        MainWindow.resize(1250, 850)

        self.menubar = MainWindow.menuBar()
        self.menu_file = self.menubar.addMenu("文件")
        self.menu_settings = self.menubar.addMenu("设置")
        self.menu_help = self.menubar.addMenu("帮助")

        self.toolbar = QToolBar("主工具栏")
        MainWindow.addToolBar(self.toolbar)

        # 仿真控制按钮组
        self.sim_run_action = QAction(QIcon(), "运行", MainWindow)
        self.sim_run_action.setStatusTip("开始仿真")
        self.sim_run_action.setEnabled(False)

        self.sim_pause_action = QAction(QIcon(), "暂停", MainWindow)
        self.sim_pause_action.setStatusTip("暂停仿真")
        self.sim_pause_action.setEnabled(False)

        self.sim_stop_action = QAction(QIcon(), "停止", MainWindow)
        self.sim_stop_action.setStatusTip("停止仿真")
        self.sim_stop_action.setEnabled(False)

        # 在View按钮后添加分隔符和仿真控制按钮
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.sim_run_action)
        self.toolbar.addAction(self.sim_pause_action)
        self.toolbar.addAction(self.sim_stop_action)

        self.central_widget = QWidget()
        MainWindow.setCentralWidget(self.central_widget)
        
        self.main_hbox = QHBoxLayout(self.central_widget)
        self.main_hbox.setContentsMargins(5, 5, 5, 5)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        self.tab_widget = QTabWidget()
        self.left_layout.addWidget(self.tab_widget, 2)

        # --- Tab 1: 全局参数 ---
        self.tab_global_params = QWidget()
        self.global_params_layout = QVBoxLayout(self.tab_global_params)
        self.global_params_layout.setAlignment(Qt.AlignTop)
        
        params_group = QGroupBox("全局参数")
        params_grid = QGridLayout(params_group)
        
        self.le_margin_x = QLineEdit(); self.le_margin_y = QLineEdit()
        self.check_grounded = QCheckBox("贴地")
        self.le_inlet_length = QLineEdit(); self.le_outlet_length = QLineEdit()
        self.le_fan_width = QLineEdit(); self.le_fan_thickness = QLineEdit()
        self.le_fan_hole_diameter = QLineEdit(); self.le_fan_hub_diameter = QLineEdit()
        self.le_fan_circle_segments = QLineEdit()
        self.le_comp_grid_x = QLineEdit(); self.le_comp_grid_y = QLineEdit(); self.le_comp_grid_z = QLineEdit()
        comp_grid_layout = QHBoxLayout(); comp_grid_layout.addWidget(self.le_comp_grid_x); comp_grid_layout.addWidget(self.le_comp_grid_y); comp_grid_layout.addWidget(self.le_comp_grid_z)
        self.le_env_grid_x = QLineEdit(); self.le_env_grid_y = QLineEdit(); self.le_env_grid_z = QLineEdit()
        self.le_stretch_ratio_z = QLineEdit()
        self.le_stretch_ratio_xy = QLineEdit()
        env_grid_layout = QHBoxLayout(); env_grid_layout.addWidget(self.le_env_grid_x); env_grid_layout.addWidget(self.le_env_grid_y); env_grid_layout.addWidget(self.le_env_grid_z)
        
        params_grid.addWidget(QLabel("X裕量(mm):"), 0, 0); params_grid.addWidget(self.le_margin_x, 0, 1)
        params_grid.addWidget(QLabel("Y裕量(mm):"), 0, 2); params_grid.addWidget(self.le_margin_y, 0, 3)
        params_grid.addWidget(QLabel("入口长度(m):"), 1, 0); params_grid.addWidget(self.le_inlet_length, 1, 1)
        params_grid.addWidget(QLabel("出口长度(m):"), 1, 2); params_grid.addWidget(self.le_outlet_length, 1, 3)
        params_grid.addWidget(QLabel("风扇宽度(mm):"), 2, 0); params_grid.addWidget(self.le_fan_width, 2, 1)
        params_grid.addWidget(QLabel("风扇厚度(mm):"), 2, 2); params_grid.addWidget(self.le_fan_thickness, 2, 3)
        params_grid.addWidget(QLabel("开孔直径(mm):"), 3, 0); params_grid.addWidget(self.le_fan_hole_diameter, 3, 1)
        params_grid.addWidget(QLabel("轮毂直径(mm):"), 3, 2); params_grid.addWidget(self.le_fan_hub_diameter, 3, 3)
        params_grid.addWidget(QLabel("圆形分段数:"), 4, 0); params_grid.addWidget(self.le_fan_circle_segments, 4, 1)
        params_grid.addWidget(self.check_grounded, 4, 2, 1, 2)
        params_grid.addWidget(QLabel("组件网格(x,y,z):"), 5, 0); params_grid.addLayout(comp_grid_layout, 5, 1, 1, 3)
        params_grid.addWidget(QLabel("环境网格(mm):"), 6, 0); params_grid.addLayout(env_grid_layout, 6, 1, 1, 3)
        params_grid.addWidget(QLabel("Z轴拉伸比:"), 7, 0); params_grid.addWidget(self.le_stretch_ratio_z, 7, 1)
        params_grid.addWidget(QLabel("XY裕量拉伸比:"), 7, 2); params_grid.addWidget(self.le_stretch_ratio_xy, 7, 3)

        self.le_air_temp = QLineEdit("25.0")
        self.le_air_humidity = QLineEdit("50.0")
        self.le_ambient_pressure = QLineEdit("0.0")
        params_grid.addWidget(QLabel("空气温度(°C):"), 8, 0); params_grid.addWidget(self.le_air_temp, 8, 1)
        params_grid.addWidget(QLabel("空气湿度(RH%):"), 8, 2); params_grid.addWidget(self.le_air_humidity, 8, 3)
        params_grid.addWidget(QLabel("环境压力(Pa):"), 9, 0); params_grid.addWidget(self.le_ambient_pressure, 9, 1)
        
        self.global_params_layout.addWidget(params_group)
        
        boundary_group = QGroupBox("边界封闭")
        boundary_grid = QGridLayout(boundary_group)
        self.check_boundary_xp = QCheckBox("+X"); self.check_boundary_xn = QCheckBox("-X")
        self.check_boundary_yp = QCheckBox("+Y"); self.check_boundary_yn = QCheckBox("-Y")
        self.check_boundary_zp = QCheckBox("+Z"); self.check_boundary_zn = QCheckBox("-Z")
        boundary_grid.addWidget(self.check_boundary_xp, 0, 0); boundary_grid.addWidget(self.check_boundary_xn, 0, 1)
        boundary_grid.addWidget(self.check_boundary_yp, 0, 2); boundary_grid.addWidget(self.check_boundary_yn, 0, 3)
        boundary_grid.addWidget(self.check_boundary_zp, 0, 4); boundary_grid.addWidget(self.check_boundary_zn, 0, 5)
        self.global_params_layout.addWidget(boundary_group)
        
        self.tab_widget.addTab(self.tab_global_params, "全局参数")

        # --- Tab 2: 风扇参数 ---
        self.tab_fan_params = QWidget()
        self.fan_params_layout = QVBoxLayout(self.tab_fan_params)
        fan_op_group = QGroupBox("风扇运行参数")
        fan_op_layout = QFormLayout(fan_op_group)
        
        self.le_rpm1 = QLineEdit()
        self.check_dir1 = QCheckBox("顺时针")
        rpm1_layout = QHBoxLayout()
        rpm1_layout.addWidget(self.le_rpm1)
        rpm1_layout.addWidget(self.check_dir1)
        
        self.le_rpm2 = QLineEdit()
        self.check_dir2 = QCheckBox("顺时针")
        rpm2_layout = QHBoxLayout()
        rpm2_layout.addWidget(self.le_rpm2)
        rpm2_layout.addWidget(self.check_dir2)

        fan_op_layout.addRow("一级额定转速/方向:", rpm1_layout)
        fan_op_layout.addRow("二级额定转速/方向:", rpm2_layout)
        
        self.fan_params_layout.addWidget(fan_op_group)
        
        pq_group = QGroupBox("PQ曲线")
        pq_layout = QVBoxLayout(pq_group)
        self.btn_load_pq = QPushButton("读取PQ曲线文件")
        self.pq_graph_widget = pg.PlotWidget()
        pq_layout.addWidget(self.btn_load_pq)
        pq_layout.addWidget(self.pq_graph_widget)
        self.fan_params_layout.addWidget(pq_group)
        self.tab_widget.addTab(self.tab_fan_params, "风扇参数")

        # --- Tab 3: 仿真设置 ---
        self.tab_sim_settings = QWidget()
        sim_settings_layout = QVBoxLayout(self.tab_sim_settings)
        
        # 仿真控制组
        sim_control_group = QGroupBox("仿真控制")
        sim_control_form = QFormLayout(sim_control_group)
        self.le_max_iterations = QLineEdit("1000")
        self.le_residual_tolerance = QLineEdit("1e-5")
        sim_control_form.addRow("最大迭代数:", self.le_max_iterations)
        sim_control_form.addRow("收敛残差:", self.le_residual_tolerance)
        sim_settings_layout.addWidget(sim_control_group)

        # 残差图组
        residual_group = QGroupBox("残差监控")
        residual_layout = QVBoxLayout(residual_group)
        self.residual_plot_widget = pg.PlotWidget()
        residual_layout.addWidget(self.residual_plot_widget)
        sim_settings_layout.addWidget(residual_group)

        self.tab_post_processing = QWidget()
        self.tab_widget.addTab(self.tab_sim_settings, "仿真设置")
        self.tab_widget.addTab(self.tab_post_processing, "后处理")
        
        log_group = QGroupBox("信息输出")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        self.left_layout.addWidget(log_group, 1)

        self.right_panel = QWidget()
        self.right_panel.setFixedSize(900, 800)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.plotter_layout = QVBoxLayout()
        status_layout = QHBoxLayout()
        self.status_label = QLabel("状态: 就绪"); self.progress_bar = QProgressBar(); self.progress_bar.setVisible(False)
        status_layout.addWidget(self.status_label, 1); status_layout.addWidget(self.progress_bar, 2)
        self.right_layout.addLayout(self.plotter_layout, 1)
        self.right_layout.addLayout(status_layout)
        
        self.main_hbox.addWidget(self.left_panel)
        self.main_hbox.addWidget(self.right_panel)


