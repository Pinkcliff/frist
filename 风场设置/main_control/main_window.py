# wind_wall_simulator/main_window.py

import sys
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStatusBar, 
    QToolBar, QLabel, QFileDialog, QTextEdit, QMenu, QSplitter, QDialog,
    QGroupBox, QFormLayout, QDockWidget, QStackedWidget
)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtGui import QUndoStack
from .commands import EditCommand
import numpy as np

from . import config
from .canvas_widget import CanvasWidget
from .timeline_widget import TimelineWidget
from .floating_windows import (
    SelectionInfoWindow, BrushToolWindow, FanSettingsWindow,
    TimeSettingsWindow, TemplateLibraryWindow, InfoWindow,
    CircleToolWindow, LineToolWindow, FunctionToolWindow
) 

class MainWindow(QMainWindow):
    """重新设计的主窗口，包含右侧Dock面板和工具模式切换"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.setGeometry(100, 100, 1200, 900)
        # 【新增】初始化撤销栈和状态暂存
        self.undo_stack = QUndoStack(self)
        self.data_before_edit = None
        
        # 调试模式标志
        self.debug_mode = True
        
        # 时间设置
        self.max_time = 10.0
        self.time_resolution = 0.1
        self.max_rpm = 15000
        
        # 运行时间计时器
        self.start_time = datetime.now()
        self.base_runtime = timedelta(hours=1234, minutes=56)
        self.runtime_timer = QTimer(self)
        self.runtime_timer.setInterval(1000) # 每秒更新一次
        self.runtime_timer.timeout.connect(self._update_runtime_display)
        # self.runtime_timer.start()
        
        # 初始化工具面板
        self._init_tool_widgets()
        
        # 创建UI元素
        self._create_docks_and_central_widget()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        
        self._connect_signals()

    def _init_tool_widgets(self):
        """初始化所有工具面板的QWidget"""
        # 这些现在是普通的QWidget，将被放入QStackedWidget
        self.selection_widget = SelectionInfoWindow(self)
        self.brush_widget = BrushToolWindow(self)
        self.circle_widget = CircleToolWindow(self)
        self.line_widget = LineToolWindow(self)
        self.function_widget = FunctionToolWindow(self)
        # 这些仍然是独立的对话框
        self.fan_settings_window = FanSettingsWindow(self)
        self.time_settings_window = TimeSettingsWindow(self)
        self.template_window = TemplateLibraryWindow(self)
        
        # 设置初始值
        self.fan_settings_window.set_max_rpm(self.max_rpm)
        self.time_settings_window.set_max_time(self.max_time)
        self.time_settings_window.set_time_resolution(self.time_resolution)

# main_window.py -> MainWindow

# main_window.py -> MainWindow

# main_window.py -> MainWindow

    def _create_docks_and_central_widget(self):
        """创建Dock面板和中央组件 (布局修复版)"""
        # --- 中央组件：使用QVBoxLayout并为时间轴设置固定高度 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(5, 5, 5, 5)
        central_layout.setSpacing(5)

        self.canvas_widget = CanvasWidget(self, self)
        self.timeline_widget = TimelineWidget()
        self.timeline_widget.set_max_time(self.max_time)
        self.timeline_widget.set_time_resolution(self.time_resolution)

        # 【核心修复】将画布和时间条添加到布局中
        central_layout.addWidget(self.canvas_widget)
        central_layout.addWidget(self.timeline_widget)

        # 【核心修复】强制时间轴占据固定高度，让画布填充剩余空间
        central_layout.setStretch(0, 1) # 画布是可伸缩的
        central_layout.setStretch(1, 0) # 时间轴不可伸缩
        self.timeline_widget.setMaximumHeight(80) # 设置一个最大高度

        # --- 右侧Dock面板 (代码与之前相同) ---
        right_dock = QDockWidget("工具与信息", self)
        right_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        
        dock_container = QWidget()
        dock_layout = QVBoxLayout(dock_container)
        
        # 1. 工具模式面板
        self.tool_mode_group = QGroupBox("点选模式")
        self.tool_stack = QStackedWidget()
        self.tool_stack.addWidget(self.selection_widget)
        self.tool_stack.addWidget(self.brush_widget)
        self.tool_stack.addWidget(self.circle_widget)
        self.tool_stack.addWidget(self.line_widget)
        self.tool_stack.addWidget(self.function_widget)
        
        tool_mode_layout = QVBoxLayout()
        tool_mode_layout.addWidget(self.tool_stack)
        self.tool_mode_group.setLayout(tool_mode_layout)

        # 2. 状态信息面板
        status_group = QGroupBox("状态信息")
        status_layout = QFormLayout()
        self.fan_id_label = QLabel("--")
        self.fan_position_label = QLabel("--")
        self.fan_speed1_label = QLabel("--")
        self.fan_speed2_label = QLabel("--")
        self.fan_pwm_label = QLabel("--")
        self.fan_power_label = QLabel("--")
        self.fan_runtime_label = QLabel("--")
        status_layout.addRow("风扇ID:", self.fan_id_label)
        status_layout.addRow("位置(行,列):", self.fan_position_label)
        status_layout.addRow("一级转速:", self.fan_speed1_label)
        status_layout.addRow("二级转速:", self.fan_speed2_label)
        status_layout.addRow("占空比:", self.fan_pwm_label)
        status_layout.addRow("电流电压功率:", self.fan_power_label)
        status_layout.addRow("运行时间:", self.fan_runtime_label)
        status_group.setLayout(status_layout)

        # 3. 系统信息面板
        info_group = QGroupBox("系统信息")
        info_layout = QVBoxLayout()
        self.info_output = QTextEdit()
        self.info_output.setReadOnly(True)
        self.info_output.append("系统就绪...")
        info_layout.addWidget(self.info_output)
        info_group.setLayout(info_layout)
        
        # 将三个部分添加到Dock容器中，并设置比例
        dock_layout.addWidget(self.tool_mode_group, 15)
        dock_layout.addWidget(status_group, 10)
        dock_layout.addWidget(info_group, 10)

        right_dock.setWidget(dock_container)
        self.addDockWidget(Qt.RightDockWidgetArea, right_dock)




# main_window.py -> MainWindow
    def _create_actions(self):
        """创建所有菜单栏的动作"""
        # 文件菜单动作
        self.menu_open_action = QAction("打开", self)
        self.menu_save_action = QAction("保存", self)
        self.menu_save_as_action = QAction("另存为", self)
        self.menu_exit_action = QAction("退出", self)
        
        # 工具菜单动作
        self.menu_selection_action = QAction("选择", self)
        self.menu_brush_tool_action = QAction("笔刷工具", self)
        self.menu_circle_tool_action = QAction("圆形工具", self)
        self.menu_line_tool_action = QAction("直线工具", self)
        self.menu_function_generator_action = QAction("函数生成器", self)
        self.menu_run_sim_action = QAction("进入仿真", self)
        
        # 设置菜单动作
        self.menu_fan_settings_action = QAction("风机设置", self)
        self.menu_time_settings_action = QAction("时间设置", self)
        self.menu_template_library_action = QAction("模版库", self)
        self.menu_debug_mode_action = QAction("调试模式", self)
        self.menu_debug_mode_action.setCheckable(True)
        self.menu_debug_mode_action.setChecked(self.debug_mode)

# main_window.py -> MainWindow

    def _create_menus(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        file_menu.addAction(self.menu_open_action)
        file_menu.addAction(self.menu_save_action)
        file_menu.addAction(self.menu_save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.menu_exit_action)
        
        # 工具菜单
        tools_menu = menu_bar.addMenu("工具")
        tools_menu.addAction(self.menu_selection_action)
        tools_menu.addSeparator()
        tools_menu.addAction(self.menu_brush_tool_action)
        tools_menu.addAction(self.menu_circle_tool_action)
        tools_menu.addAction(self.menu_line_tool_action)
        tools_menu.addSeparator()
        tools_menu.addAction(self.menu_function_generator_action)
        tools_menu.addSeparator()
        tools_menu.addAction(self.menu_run_sim_action)
        
        # 设置菜单
        settings_menu = menu_bar.addMenu("设置")
        settings_menu.addAction(self.menu_fan_settings_action)
        settings_menu.addAction(self.menu_time_settings_action)
        settings_menu.addAction(self.menu_template_library_action)
        settings_menu.addSeparator()
        settings_menu.addAction(self.menu_debug_mode_action)


# main_window.py -> MainWindow

# main_window.py -> MainWindow

# main_window.py -> MainWindow

# main_window.py -> MainWindow

# main_window.py -> MainWindow._create_toolbar
    def _create_toolbar(self):
        """创建带图标和文字的工具栏 (带撤销/重做)"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        current_dir = os.path.dirname(__file__)
        # 图标文件位于风场设置/icon目录下
        icon_path = os.path.join(current_dir, '..', 'icon')

        # 【新增】创建回退和前进按钮
        self.undo_action = self.undo_stack.createUndoAction(self, "回退")
        self.redo_action = self.undo_stack.createRedoAction(self, "前进")
        self.undo_action.setShortcut("Ctrl+Z")
        self.redo_action.setShortcut("Ctrl+Y")
        
        # 设置固定文本，不显示具体命令
        self.undo_action.setText("回退")
        self.redo_action.setText("前进")
        
        # 连接信号以保持固定文本
        self.undo_stack.indexChanged.connect(self._update_undo_redo_text)
        
        # 假设 icon 文件夹中有 undo.png 和 redo.png
        # self.undo_action.setIcon(QIcon(os.path.join(icon_path, "undo.png")))
        # self.redo_action.setIcon(QIcon(os.path.join(icon_path, "redo.png")))

        self.tool_open_action = QAction(QIcon(os.path.join(icon_path, "打开.png")), "打开", self)
        self.tool_save_action = QAction(QIcon(os.path.join(icon_path, "保存.png")), "保存", self)
        self.tool_save_as_action = QAction(QIcon(os.path.join(icon_path, "另存为1.png")), "另存为", self)
        self.undo_action = QAction(QIcon(os.path.join(icon_path, "undo.png")), "undo", self)
        self.redo_action = QAction(QIcon(os.path.join(icon_path, "redo.png")), "redo", self)
        self.tool_select_action = QAction(QIcon(os.path.join(icon_path, "选择.png")), "点选", self)
        self.tool_brush_action = QAction(QIcon(os.path.join(icon_path, "笔刷工具.png")), "笔刷", self)
        self.tool_circle_action = QAction(QIcon(os.path.join(icon_path, "圆形工具.png")), "圆形", self)
        self.tool_line_action = QAction(QIcon(os.path.join(icon_path, "直线工具.png")), "直线", self)
        self.tool_func_action = QAction(QIcon(os.path.join(icon_path, "fx.png")), "函数", self)
        self.tool_fan_action = QAction(QIcon(os.path.join(icon_path, "风扇设置.png")), "风机", self)
        self.tool_time_action = QAction(QIcon(os.path.join(icon_path, "时间设置.png")), "时间", self)
        self.tool_template_action = QAction(QIcon(os.path.join(icon_path, "模板库.png")), "模板", self)
        self.tool_sim_action = QAction(QIcon(os.path.join(icon_path, "仿真分析1.png")), "仿真", self)

        toolbar.addAction(self.tool_open_action)
        toolbar.addAction(self.tool_save_action)
        toolbar.addAction(self.tool_save_as_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.tool_select_action)
        toolbar.addAction(self.tool_brush_action)
        toolbar.addAction(self.tool_circle_action)
        toolbar.addAction(self.tool_line_action)
        toolbar.addAction(self.tool_func_action)
        toolbar.addSeparator()
        toolbar.addAction(self.tool_fan_action)
        toolbar.addAction(self.tool_time_action)
        toolbar.addAction(self.tool_template_action)
        toolbar.addSeparator()
        toolbar.addAction(self.tool_sim_action)

    @Slot(float)
    def _apply_speed_to_selected_fans(self, speed):
        """将速度应用到选中的风扇，并根据设置应用羽化 (最终修复版)"""
        self.data_before_edit = np.copy(self.canvas_widget.grid_data)
        
        # 决定从哪个工具窗口获取羽化设置
        current_tool_widget = self.tool_stack.currentWidget()
        feather_enabled = False
        feather_value = 0
        if hasattr(current_tool_widget, 'is_feathering_enabled'):
            feather_enabled = current_tool_widget.is_feathering_enabled()
            feather_value = current_tool_widget.get_feather_value()
        affected_count = self.canvas_widget.apply_speed_and_feather_to_selection(
            speed, feather_enabled, feather_value
        )
        if affected_count > 0:
            description = f"设置 {affected_count} 个风扇速度为 {speed}%"
            if feather_enabled:
                description += f" (羽化: {feather_value})"
            self._push_edit_command(description)
            
            self._add_info_message(f"已将 {affected_count} 个风扇单元的速度设置为 {speed}%")
            if feather_enabled:
                self._add_info_message(f"并应用了 {feather_value} 层的羽化")
        else:
            self._add_info_message("没有选中的风扇单元")
    
    def _push_edit_command(self, description):
        """推送编辑命令到撤销栈"""
        if self.data_before_edit is not None:
            command = EditCommand(
                self.canvas_widget,
                self.data_before_edit,
                self.canvas_widget.grid_data,
                description
            )
            self.undo_stack.push(command)
            self.data_before_edit = None

    def _create_statusbar(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪。")

# main_window.py -> MainWindow

# main_window.py -> MainWindow

    def _connect_signals(self):
        """连接所有信号和槽"""
        # 画布相关信号
        self.canvas_widget.selection_changed.connect(self.selection_widget.update_selection_info)
        self.canvas_widget.selection_changed.connect(self.circle_widget.update_selection_info) # 新增
        self.canvas_widget.selection_changed.connect(self._update_info_output)
        self.canvas_widget.fan_hover.connect(self._update_fan_hover_info)
        self.canvas_widget.fan_hover_exit.connect(self._clear_fan_hover_info)
        
        # 选择工具widget信号
        self.selection_widget.apply_speed_signal.connect(self._apply_speed_to_selected_fans)
        self.selection_widget.invert_selection_signal.connect(self.canvas_widget.invert_selection)
        self.selection_widget.reset_button.clicked.connect(self._reset_all_fans_to_zero)
        self.selection_widget.select_all_button.clicked.connect(self.canvas_widget.select_all_cells)

        # 【新增】圆形工具信号
        self.circle_widget.apply_speed_signal.connect(self._apply_speed_to_selected_fans)
        
        # 【新增】所有工具窗口的全部清零信号
        self.brush_widget.clear_all_signal.connect(self._reset_all_fans_to_zero)
        self.circle_widget.clear_all_signal.connect(self._reset_all_fans_to_zero)
        self.line_widget.clear_all_signal.connect(self._reset_all_fans_to_zero)
        self.function_widget.clear_all_signal.connect(self._reset_all_fans_to_zero)
        
        # 时间条信号
        self.timeline_widget.time_changed.connect(self._on_time_changed)
        self.timeline_widget.play_state_changed.connect(self._on_play_state_changed)
        
        # 文件操作连接
        self.menu_open_action.triggered.connect(self._open_file)
        self.tool_open_action.triggered.connect(self._open_file)
        self.menu_save_action.triggered.connect(self._save_file)
        self.tool_save_action.triggered.connect(self._save_file)
        self.menu_save_as_action.triggered.connect(self._save_as_file)
        self.tool_save_as_action.triggered.connect(self._save_as_file)
        self.menu_exit_action.triggered.connect(self.close)
        
        # 工具模式连接
        self.menu_selection_action.triggered.connect(self._show_selection_tool)
        self.tool_select_action.triggered.connect(self._show_selection_tool)
        self.menu_brush_tool_action.triggered.connect(self._show_brush_tool)
        self.tool_brush_action.triggered.connect(self._show_brush_tool)
        self.menu_circle_tool_action.triggered.connect(self._show_circle_tool)
        self.tool_circle_action.triggered.connect(self._show_circle_tool)
        self.menu_line_tool_action.triggered.connect(self._show_line_tool)
        self.tool_line_action.triggered.connect(self._show_line_tool)
        self.menu_function_generator_action.triggered.connect(self._show_function_tool)
        self.tool_func_action.triggered.connect(self._show_function_tool)
        self.menu_run_sim_action.triggered.connect(self.launch_cfd_interface)
        self.tool_sim_action.triggered.connect(self.launch_cfd_interface)
        
        # 设置连接
        self.menu_fan_settings_action.triggered.connect(self._show_fan_settings)
        self.tool_fan_action.triggered.connect(self._show_fan_settings)
        self.menu_time_settings_action.triggered.connect(self._show_time_settings)
        self.tool_time_action.triggered.connect(self._show_time_settings)
        self.menu_template_library_action.triggered.connect(self._show_template_library)
        self.tool_template_action.triggered.connect(self._show_template_library)
        self.menu_debug_mode_action.toggled.connect(self._toggle_debug_mode)
        
        # 笔刷widget参数变化信号
        self.brush_widget.brush_size_spinbox.valueChanged.connect(self.canvas_widget.update_brush_preview)
        self.brush_widget.brush_value_input.textChanged.connect(self.canvas_widget.update_brush_preview)




    def set_cfd_launch_function(self, func):
        self.launch_cfd_function = func
        print("[MainControl] CFD launch function has been injected.")

    @Slot()
    def _open_file(self):
        self._add_info_message("打开文件功能暂未实现")
            
    @Slot()
    def _save_file(self):
        self._add_info_message("保存文件功能暂未实现")
        
    @Slot()
    def _save_as_file(self):
        self._add_info_message("另存为功能暂未实现")
            
    @Slot()
    def _show_selection_tool(self):
        self.tool_stack.setCurrentWidget(self.selection_widget)
        self.tool_mode_group.setTitle("点选模式")
        self.canvas_widget.update_brush_preview()
        self._add_info_message("切换到 [选择模式]")

    @Slot()
    def _show_brush_tool(self):
        self.tool_stack.setCurrentWidget(self.brush_widget)
        self.tool_mode_group.setTitle("笔刷模式")
        self.canvas_widget.update_brush_preview()
        self._add_info_message("切换到 [笔刷模式]")
        
    @Slot()
    def _show_circle_tool(self):
        self.tool_stack.setCurrentWidget(self.circle_widget)
        self.tool_mode_group.setTitle("圆形工具模式")
        self.canvas_widget.update_brush_preview()
        self._add_info_message("切换到 [圆形工具模式]")
        
    @Slot()
    def _show_line_tool(self):
        self.tool_stack.setCurrentWidget(self.line_widget)
        self.tool_mode_group.setTitle("直线工具模式")
        self.canvas_widget.update_brush_preview()
        self._add_info_message("切换到 [直线工具模式]")
    @Slot()
    def _show_function_tool(self):
        """切换到函数工具"""
        self.tool_stack.setCurrentWidget(self.function_widget)
        self.tool_mode_group.setTitle("函数模式")
        self.canvas_widget.update_brush_preview()
        self._add_info_message("切换到 [函数模式]")

    @Slot()
    def _show_fan_settings(self):
        if self.fan_settings_window.exec() == QDialog.Accepted:
            self._apply_fan_settings()
            
    @Slot()
    def _show_time_settings(self):
        if self.time_settings_window.exec() == QDialog.Accepted:
            self._apply_time_settings()
            
    @Slot()
    def _show_template_library(self):
        self.template_window.show()
        self.template_window.raise_()
        
    @Slot()
    def _function_generator_placeholder(self):
        self._add_info_message("函数生成器功能暂未实现")
        
    @Slot()
    def _apply_fan_settings(self):
        max_rpm = self.fan_settings_window.get_max_rpm()
        self.max_rpm = max_rpm
        self._add_info_message(f"风机最大转速设置为: {max_rpm} RPM")
        
    @Slot()
    def _apply_time_settings(self):
        max_time = self.time_settings_window.get_max_time()
        resolution = self.time_settings_window.get_time_resolution()
        self.max_time = max_time
        self.time_resolution = resolution
        self.timeline_widget.set_max_time(max_time)
        self.timeline_widget.set_time_resolution(resolution)
        self._add_info_message(f"时间设置更新: 最大时间={max_time}s, 分辨率={resolution}s")
        
    @Slot(bool)
    def _toggle_debug_mode(self, enabled):
        self.debug_mode = enabled
        status = "开启" if enabled else "关闭"
        self._add_info_message(f"调试模式已{status}")
        
    @Slot(float)
    def _on_time_changed(self, time_value):
        if self.debug_mode:
            self._add_info_message(f"时间设置为: {time_value:.2f}s")
        
    @Slot(bool)
    def _on_play_state_changed(self, is_playing):
        status = "播放" if is_playing else "暂停"
        self._add_info_message(f"时间条{status}")
        
    def _add_info_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.info_output.append(formatted_message)
        if self.debug_mode:
            print(f"[Info] {formatted_message}")
        
    @Slot()
    def _update_info_output(self):
        selected_count = len(self.canvas_widget.get_selected_cells())
        if selected_count > 0:
            self._add_info_message(f"选中了 {selected_count} 个风扇单元")
            
    @Slot()
    def launch_cfd_interface(self):
        """启动前处理程序"""
        import subprocess
        import sys

        self._add_info_message("正在启动前处理程序...")

        # 获取前处理 main.py 的路径
        pre_processor_main = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '前处理', 'main.py'
        )

        try:
            # 使用当前 Python 解释器启动前处理程序
            subprocess.Popen([sys.executable, pre_processor_main])
            self._add_info_message("前处理程序已启动")
        except Exception as e:
            self._add_info_message(f"启动前处理程序失败: {e}")

    def generate_time_series_data(self):
        """生成时间序列数据"""
        import numpy as np

        # 计算时间点数量
        num_time_points = int(self.max_time / self.time_resolution) + 1

        # 生成时间点数组
        time_points = np.linspace(0, self.max_time, num_time_points)

        # 获取当前网格数据（风扇转速百分比）
        grid_data_percent = self.canvas_widget.get_grid_data()

        # 转换为实际转速 (RPM)
        grid_data_rpm = (grid_data_percent / 100.0 * self.max_rpm).astype(int)

        # 生成每个时间点的风扇转速数据
        # 假设所有时间点使用相同的转速设置（可根据需要修改）
        time_series_rpm = np.tile(grid_data_rpm, (num_time_points, 1, 1))

        # 构建数据字典
        time_series_data = {
            'time_points': time_points,
            'time_resolution': self.time_resolution,
            'max_time': self.max_time,
            'max_rpm': self.max_rpm,
            'grid_shape': grid_data_rpm.shape,
            'rpm_data': time_series_rpm,  # shape: (time, rows, cols)
            'metadata': {
                'generated_by': 'Wind Wall Settings',
                'description': 'Time series fan RPM data for CFD simulation'
            }
        }

        return time_series_data

# main_window.py -> MainWindow



    @Slot(int, int, int, float)
    def _update_fan_hover_info(self, fan_id_temp, row, col, pwm_ratio):
        x_coord = col
        y_coord = row
        fan_id_str = f"X{x_coord:03}Y{y_coord:03}"
        
        self.fan_id_label.setText(fan_id_str)
        self.fan_position_label.setText(f"({row}, {col})")
        self.fan_pwm_label.setText(f"{pwm_ratio:.1f}%")

        speed1 = int(self.max_rpm * pwm_ratio / 100)
        speed2 = int(14600 * pwm_ratio / 100)
        self.fan_speed1_label.setText(f"{speed1} RPM")
        self.fan_speed2_label.setText(f"{speed2} RPM")

        current = 2.7 * (pwm_ratio / 100.0)
        power = 145.8 * (pwm_ratio / 100.0)
        self.fan_power_label.setText(f"{current:.2f}A, 54V, {power:.1f}W")
        
        # 【修改】只有在悬停时才启动/显示运行时间
        self.runtime_timer.start()
        self._update_runtime_display() # 立即更新一次


# main_window.py -> MainWindow

    @Slot()
    def _clear_fan_hover_info(self):
        self.fan_id_label.setText("--")
        self.fan_position_label.setText("--")
        self.fan_pwm_label.setText("--")
        self.fan_speed1_label.setText("--")
        self.fan_speed2_label.setText("--")
        self.fan_power_label.setText("--")
        # 【修改】鼠标移出时，停止计时器并清空显示
        self.runtime_timer.stop()
        self.fan_runtime_label.setText("--")


    @Slot()
    def _update_runtime_display(self):
        """槽函数：由QTimer调用，每秒更新运行时间"""
        elapsed = datetime.now() - self.start_time
        total_runtime = self.base_runtime + elapsed
        
        # 格式化为 HHHHh MMm SSs
        hours = total_runtime.days * 24 + total_runtime.seconds // 3600
        minutes = (total_runtime.seconds % 3600) // 60
        seconds = total_runtime.seconds % 60
        
        self.fan_runtime_label.setText(f"{hours:04d}h{minutes:02d}m{seconds:02d}s")

    @Slot()
    def _reset_all_fans_to_zero(self):
        """槽函数：将所有风扇的转速设置为0%并取消所有选择 (支持撤销)"""
        self.data_before_edit = np.copy(self.canvas_widget.grid_data)
        self.canvas_widget.grid_data.fill(0)
        self.canvas_widget.update_all_cells_from_data()
        # 取消所有选择
        self.canvas_widget.selected_cells.clear()
        self.canvas_widget.update()
        self._push_edit_command("全部清零")
        self._add_info_message("所有风扇转速已清零，选择已取消")
    
    @Slot()
    def _update_undo_redo_text(self):
        """更新撤销/重做按钮文本，保持固定显示"""
        self.undo_action.setText("回退")
        self.redo_action.setText("前进")


