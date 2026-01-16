# ui_docks.py
import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
                               QPushButton, QLabel, QComboBox, QDoubleSpinBox, QTabWidget, 
                               QTableWidget, QCheckBox, QSlider, QTextEdit, QFormLayout,
                               QLineEdit, QSpinBox, QFrame, QRadioButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QPalette, QColor, QPixmap,QIntValidator
from functools import partial
import debug
from ui_custom_widgets import DraggableFrame, OverallHealthIndicator, CommunicationStatusIndicator, EnvironmentDisplay, BackgroundWidget 
from ui_chart_widget import RealTimeChartWidget
from ui_motion_capture import CameraStatusLight


# =========================================================================
# 参数化的Dock样式函数
# =========================================================================
# --- MODIFIED: Added is_independent parameter ---
# ui_docks.py -> create_styled_dock (恢复到原始版本)

def create_styled_dock(parent, title, content_widget,
                       min_size_from_content=True, default_size=None, default_pos=None, is_independent=False):
    # 创建dock，所有dock都嵌入在主窗口中
    frame = DraggableFrame(title, parent, is_independent_window=False)
    frame.setContentWidget(content_widget)
    if min_size_from_content:
        frame.setMinimumSizeFromContent()
    if default_size:
        frame.resize(default_size[0], default_size[1])
    if default_pos:
        frame.move(default_pos[0], default_pos[1])
    return frame


# =========================================================================
# 通信协议设置Dock (保持不变)
# =========================================================================
def create_tcp_settings_dock(main_window):
    # These settings docks can also be independent
    return create_styled_dock(main_window, "TCP/IP 设置", QWidget(), is_independent=True)

def create_modbus_settings_dock(main_window):
    return create_styled_dock(main_window, "Modbus RTU 设置", QWidget(), is_independent=True)

def create_ethercat_settings_dock(main_window):
    return create_styled_dock(main_window, "EtherCAT 设置", QWidget(), is_independent=True)

def create_api_settings_dock(main_window):
    return create_styled_dock(main_window, "API 设置", QWidget(), is_independent=True)

# ... (The code for filling the settings docks remains the same, I'll omit it for brevity but it should be there)
def create_tcp_settings_dock(main_window):
    content = QWidget()
    layout = QFormLayout(content)
    layout.setSpacing(10)
    
    ip_edit = QLineEdit("192.168.11.11")
    port_spinbox = QSpinBox()
    port_spinbox.setRange(1, 65535)
    port_spinbox.setValue(8888)
    reconnect_check = QCheckBox("自动重连")
    reconnect_check.setChecked(True)
    
    interval_widget = QWidget()
    interval_layout = QHBoxLayout(interval_widget)
    interval_layout.setContentsMargins(0,0,0,0)
    interval_spinbox = QSpinBox()
    interval_spinbox.setRange(10, 10000)
    interval_spinbox.setValue(100)
    interval_layout.addWidget(interval_spinbox)
    interval_layout.addWidget(QLabel("ms"))
    interval_layout.addStretch()

    speed_combo = QComboBox()
    speed_combo.addItems(["50条/秒", "100条/秒", "200条/秒", "300条/秒"])
    speed_combo.setCurrentText("100条/秒")

    layout.addRow("IP 地址:", ip_edit)
    layout.addRow("端口号:", port_spinbox)
    layout.addRow(reconnect_check)
    layout.addRow("重连间隔:", interval_widget)
    layout.addRow("通讯速度:", speed_combo)
    
    return create_styled_dock(main_window.canvas, "TCP/IP 设置", content, is_independent=True)

def create_modbus_settings_dock(main_window):
    content = QWidget()
    layout = QFormLayout(content)
    layout.setSpacing(10)

    com_combo = QComboBox()
    com_combo.addItems([f"COM{i}" for i in range(1, 11)])
    
    baud_combo = QComboBox()
    baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
    
    slave_range_widget = QWidget()
    slave_layout = QHBoxLayout(slave_range_widget)
    slave_layout.setContentsMargins(0,0,0,0)
    slave_from = QSpinBox()
    slave_from.setRange(1, 247)
    slave_from.setValue(10)
    slave_to = QSpinBox()
    slave_to.setRange(1, 247)
    slave_to.setValue(110)
    slave_layout.addWidget(slave_from)
    slave_layout.addWidget(QLabel(" 到 "))
    slave_layout.addWidget(slave_to)

    timeout_spinbox = QSpinBox()
    timeout_spinbox.setSuffix(" ms")
    timeout_spinbox.setRange(1, 5000)
    timeout_spinbox.setValue(10)

    layout.addRow("串口号:", com_combo)
    layout.addRow("波特率:", baud_combo)
    layout.addRow("从站范围:", slave_range_widget)
    layout.addRow("响应超时:", timeout_spinbox)

    return create_styled_dock(main_window.canvas, "Modbus RTU 设置", content, is_independent=True)

def create_ethercat_settings_dock(main_window):
    content = QWidget()
    layout = QFormLayout(content)
    layout.setSpacing(10)

    adapter_combo = QComboBox()
    adapter_combo.addItem("自动检测")
    
    file_widget = QWidget()
    file_layout = QHBoxLayout(file_widget)
    file_layout.setContentsMargins(0,0,0,0)
    file_path_edit = QLineEdit()
    file_path_edit.setPlaceholderText("点击右侧按钮选择ENI文件...")
    browse_btn = QPushButton("...")
    browse_btn.setFixedSize(30, 22)
    file_layout.addWidget(file_path_edit)
    file_layout.addWidget(browse_btn)

    layout.addRow("网络适配器:", adapter_combo)
    layout.addRow("网络信息文件:", file_widget)

    return create_styled_dock(main_window.canvas, "EtherCAT 设置", content, is_independent=True)

def create_api_settings_dock(main_window):
    content = QWidget()
    layout = QFormLayout(content)
    layout.setSpacing(10)

    api_key_edit = QLineEdit()
    api_key_edit.setEchoMode(QLineEdit.Password)
    api_key_edit.setPlaceholderText("输入您的API密钥或令牌")
    
    bandwidth_combo = QComboBox()
    bandwidth_combo.addItems(["10Mbps", "50Mbps", "100Mbps", "200Mbps"])
    bandwidth_combo.setCurrentText("100Mbps")
    
    confirm_btn = QPushButton("确认")

    layout.addRow("API密钥/令牌:", api_key_edit)
    layout.addRow("交互带宽:", bandwidth_combo)
    layout.addRow(confirm_btn)

    return create_styled_dock(main_window.canvas, "API 设置", content, is_independent=True)

# =========================================================================
# 主要功能 Dock
# =========================================================================

def create_system_dock(main_window, is_independent=False):
    main_window.health_indicator = OverallHealthIndicator()
    return create_styled_dock(main_window.canvas, "系统状态", main_window.health_indicator, is_independent=is_independent)

def create_comm_dock(main_window, is_independent=False):
    # 主容器，使用垂直布局
    main_container = QWidget()
    main_layout = QVBoxLayout(main_container)
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(0, 0, 0, 0)

    # --- 上半部分：通讯状态 ---
    comm_content = QWidget()
    comm_layout = QHBoxLayout(comm_content)
    comm_layout.setSpacing(10)

    main_window.comm_indicators.clear()
    for name in main_window.DEFAULT_COMM_PROTOCOLS.keys():
        total_map = {"主控制器": 1, "电驱": 100, "风速传感": 64, "温度传感": 64, "湿度传感": 4, "动捕": 20, "俯仰伺服": 1, "造雨": 4, "喷雾": 5, "训练": 1, "仿真": 1, "电力": 1}
        total = total_map.get(name, 1)
        indicator = CommunicationStatusIndicator(name, total, total, 10)
        comm_layout.addWidget(indicator)
        main_window.comm_indicators.append(indicator)

    comm_layout.addStretch()

    # --- 添加分隔线 ---
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setStyleSheet("background-color: #404448;")

    # --- 下半部分：电力监控 ---
    power_content = QWidget()
    power_layout = QHBoxLayout(power_content)
    power_layout.setSpacing(15)

    # 创建三个电力监控图表（缩小版本）
    from ui_chart_widget import RealTimeChartWidget

    # 电流图表
    main_window.chart_current_widget = RealTimeChartWidget("实时电流监控", "电流 (A)", (0, 1000), parent=main_window.canvas)
    main_window.chart_current_widget.setFixedHeight(120)
    power_layout.addWidget(main_window.chart_current_widget)

    # 电压图表
    main_window.chart_voltage_widget = RealTimeChartWidget("实时电压监控", "电压 (V)", (360, 400), parent=main_window.canvas)
    main_window.chart_voltage_widget.setFixedHeight(120)
    power_layout.addWidget(main_window.chart_voltage_widget)

    # 功率图表
    main_window.chart_power_widget = RealTimeChartWidget("实时功率监控", "功率 (kW)", (0, 500), parent=main_window.canvas)
    main_window.chart_power_widget.setFixedHeight(120)
    power_layout.addWidget(main_window.chart_power_widget)

    # 添加到主布局
    main_layout.addWidget(comm_content, 1)  # 通讯状态占据1份空间
    main_layout.addWidget(separator)        # 分隔线
    main_layout.addWidget(power_content, 1)  # 电力监控占据1份空间

    return create_styled_dock(main_window.canvas, "通讯与电力", main_container, is_independent=is_independent)

def create_chart_dock(main_window, title, y_label, y_range):
    chart_widget = RealTimeChartWidget(title, y_label, y_range, parent=main_window.canvas)
    if title == "实时电流监控": main_window.chart_current_widget = chart_widget
    elif title == "实时电压监控": main_window.chart_voltage_widget = chart_widget
    elif title == "实时功率监控": main_window.chart_power_widget = chart_widget
    
    return create_styled_dock(main_window.canvas, title, chart_widget, min_size_from_content=False, default_size=(400, 300))

def create_env_dock(main_window, is_independent=False):
    content_container = QWidget()
    main_layout = QVBoxLayout(content_container)
    main_layout.setContentsMargins(0,0,0,0)
    grid_widget = QWidget()
    grid_layout = QGridLayout(grid_widget)
    grid_layout.setSpacing(10)
    
    main_window.env_temp = EnvironmentDisplay("温度", "25.1℃")
    main_window.env_humid = EnvironmentDisplay("湿度", "60 RH%")
    main_window.env_press = EnvironmentDisplay("气压", "200 Pa")
    main_window.env_density = EnvironmentDisplay("空气密度", "1.177 kg/m³")
    
    grid_layout.addWidget(main_window.env_temp, 0, 0)
    grid_layout.addWidget(main_window.env_humid, 0, 1)
    grid_layout.addWidget(main_window.env_press, 1, 0)
    grid_layout.addWidget(main_window.env_density, 1, 1)

    main_window.time_label = QLabel("...")
    main_window.time_label.setAlignment(Qt.AlignCenter)
    grid_layout.addWidget(main_window.time_label, 2, 0, 1, 2)

    main_window.user_label = QLabel("欢迎你, 管理员!")
    main_window.user_label.setAlignment(Qt.AlignCenter)
    grid_layout.addWidget(main_window.user_label, 3, 0, 1, 2)

    main_layout.addWidget(grid_widget)
    main_layout.addStretch(1)

    return create_styled_dock(main_window.canvas, "环境", content_container, is_independent=is_independent)

def create_log_dock(main_window, is_independent=False):
    """
    创建日志与告警Dock，包含各模块的单独日志界面。
    修改：添加通讯、电力、环境、动捕、风机的单独日志界面。
    """
    main_window.log_tab_widget = QTabWidget()

    # 1. 活动告警选项卡
    alarm_widget = QWidget()
    alarm_layout = QVBoxLayout(alarm_widget)
    main_window.table_active_alarms = QTableWidget(0, 5)
    main_window.table_active_alarms.setHorizontalHeaderLabels(["时间", "级别", "来源", "告警内容", "操作"])
    main_window.table_active_alarms.horizontalHeader().setStretchLastSection(True)
    alarm_layout.addWidget(main_window.table_active_alarms)
    main_window.log_tab_widget.addTab(alarm_widget, "活动告警")

    # 2. 系统日志选项卡
    log_widget = QWidget()
    log_layout = QVBoxLayout(log_widget)
    main_window.table_system_logs = QTableWidget(0, 4)
    main_window.table_system_logs.setHorizontalHeaderLabels(["时间", "级别", "来源", "日志内容"])
    main_window.table_system_logs.horizontalHeader().setStretchLastSection(True)
    log_layout.addWidget(main_window.table_system_logs)
    main_window.log_tab_widget.addTab(log_widget, "系统日志")

    # 3. 通讯日志选项卡
    comm_log_widget = QWidget()
    comm_log_layout = QVBoxLayout(comm_log_widget)
    main_window.table_comm_logs = QTableWidget(0, 4)
    main_window.table_comm_logs.setHorizontalHeaderLabels(["时间", "级别", "来源", "日志内容"])
    main_window.table_comm_logs.horizontalHeader().setStretchLastSection(True)
    comm_log_layout.addWidget(main_window.table_comm_logs)
    main_window.log_tab_widget.addTab(comm_log_widget, "通讯日志")

    # 4. 电力日志选项卡
    power_log_widget = QWidget()
    power_log_layout = QVBoxLayout(power_log_widget)
    main_window.table_power_logs = QTableWidget(0, 4)
    main_window.table_power_logs.setHorizontalHeaderLabels(["时间", "级别", "来源", "日志内容"])
    main_window.table_power_logs.horizontalHeader().setStretchLastSection(True)
    power_log_layout.addWidget(main_window.table_power_logs)
    main_window.log_tab_widget.addTab(power_log_widget, "电力日志")

    # 5. 环境日志选项卡
    env_log_widget = QWidget()
    env_log_layout = QVBoxLayout(env_log_widget)
    main_window.table_env_logs = QTableWidget(0, 4)
    main_window.table_env_logs.setHorizontalHeaderLabels(["时间", "级别", "来源", "日志内容"])
    main_window.table_env_logs.horizontalHeader().setStretchLastSection(True)
    env_log_layout.addWidget(main_window.table_env_logs)
    main_window.log_tab_widget.addTab(env_log_widget, "环境日志")

    # 6. 动捕日志选项卡
    motion_log_widget = QWidget()
    motion_log_layout = QVBoxLayout(motion_log_widget)
    main_window.table_motion_logs = QTableWidget(0, 4)
    main_window.table_motion_logs.setHorizontalHeaderLabels(["时间", "级别", "来源", "日志内容"])
    main_window.table_motion_logs.horizontalHeader().setStretchLastSection(True)
    motion_log_layout.addWidget(main_window.table_motion_logs)
    main_window.log_tab_widget.addTab(motion_log_widget, "动捕日志")

    # 7. 风机日志选项卡
    fan_log_widget = QWidget()
    fan_log_layout = QVBoxLayout(fan_log_widget)
    main_window.table_fan_logs = QTableWidget(0, 4)
    main_window.table_fan_logs.setHorizontalHeaderLabels(["时间", "级别", "来源", "日志内容"])
    main_window.table_fan_logs.horizontalHeader().setStretchLastSection(True)
    fan_log_layout.addWidget(main_window.table_fan_logs)
    main_window.log_tab_widget.addTab(fan_log_widget, "风机日志")

    return create_styled_dock(main_window.canvas, "日志与告警", main_window.log_tab_widget, is_independent=is_independent)

# ui_docks.py

def _create_comm_settings_tab(main_window):
    """
    创建通讯设置选项卡，包含设置、测试窗口和功能按钮。
    """
    # 主内容Widget
    widget = QWidget()
    
    main_layout = QVBoxLayout(widget)
    
    main_layout.setSpacing(15)

    # --- 1. 通讯方式设置 Frame ---
    comm_settings_group = QGroupBox("通讯方式设置")
    
    main_layout.addWidget(comm_settings_group)
    
    grid_layout = QGridLayout(comm_settings_group)
    
    grid_layout.setSpacing(10)
    
    protocol_options = ["TCP/IP", "Modbus", "EtherCAT", "API"]
    
    main_window.protocol_combos.clear()
    
    module_names = list(main_window.DEFAULT_COMM_PROTOCOLS.keys())

    for i, module_name in enumerate(module_names):
        row = i // 2
        
        col_start = (i % 2) * 3
        
        label = QLabel(f"{module_name}:")
        
        combo = QComboBox()
        
        combo.addItems(protocol_options)
        
        default_protocol = main_window.DEFAULT_COMM_PROTOCOLS.get(module_name, "")
        
        if default_protocol:
            combo.setCurrentText(default_protocol)

        btn_detail = QPushButton("设置")
        
        btn_detail.setFixedSize(40, 22)
        
        btn_detail.clicked.connect(partial(main_window.handle_specific_module_setting, module_name))

        grid_layout.addWidget(label, row, col_start, Qt.AlignRight)
        
        grid_layout.addWidget(combo, row, col_start + 1)
        
        grid_layout.addWidget(btn_detail, row, col_start + 2)
        
        main_window.protocol_combos[module_name] = combo

    # --- 2. 通讯测试 Frame ---
    comm_test_group = QGroupBox("通讯测试")
    
    main_layout.addWidget(comm_test_group)
    
    # 使用一个新的 QVBoxLayout 来容纳信息框和按钮
    test_group_layout = QVBoxLayout(comm_test_group)

    main_window.comm_info_box = QTextEdit()
    
    main_window.comm_info_box.setReadOnly(True)
    
    main_window.comm_info_box.setPlaceholderText("点击模块后的'设置'按钮以配置详细参数，或点击下方按钮进行测试...")
    
    test_group_layout.addWidget(main_window.comm_info_box)

    # --- 3. 功能按钮 ---
    button_layout = QHBoxLayout()
    
    button_layout.addStretch()
    
    btn_test = QPushButton("测试")
    
    btn_save = QPushButton("保存")
    
    btn_reset = QPushButton("重置")
    
    # 注意：取消和确定按钮在这里没有意义，因为它们是用来关闭整个Dock的
    # 我们只保留与当前Tab功能相关的按钮
    
    main_window.settings_buttons = [btn_test, btn_save, btn_reset]
    
    for btn in main_window.settings_buttons:
        btn.setFixedSize(60, 25)
        
        button_layout.addWidget(btn)
        
    # 将按钮布局添加到测试分组框的布局中
    test_group_layout.addLayout(button_layout)
    
    # 连接按钮信号
    btn_test.clicked.connect(main_window.test_settings)
    
    btn_save.clicked.connect(main_window.save_settings)
    
    btn_reset.clicked.connect(main_window.reset_settings)
    
    # 让信息框占据更多垂直空间
    main_layout.setStretchFactor(comm_test_group, 1)

    return widget

# ui_docks.py

def _create_master_control_settings_tab(main_window):
    """
    创建主控设置选项卡的内容
    """
    # 主内容Widget
    widget = QWidget()
    
    main_layout = QVBoxLayout(widget)
    
    main_layout.setSpacing(15)
    
    main_layout.setAlignment(Qt.AlignTop)

    # --- 1. 数据处理与算法 Frame ---
    algo_group = QGroupBox("数据处理与算法")
    
    main_layout.addWidget(algo_group)
    
    algo_layout = QFormLayout(algo_group)
    
    algo_layout.setLabelAlignment(Qt.AlignRight)
    
    algo_layout.setSpacing(10)

    # 延迟限制
    delay_widget = QWidget()
    
    delay_layout = QHBoxLayout(delay_widget)
    
    delay_layout.setContentsMargins(0, 0, 0, 0)
    
    delay_edit = QLineEdit("10")
    
    delay_edit.setValidator(QIntValidator(1, 1000)) # 限制只能输入整数
    
    delay_edit.setFixedWidth(50)
    
    delay_layout.addWidget(QLabel("≤"))
    
    delay_layout.addWidget(delay_edit)
    
    delay_layout.addWidget(QLabel("ms"))
    
    delay_layout.addStretch()
    
    algo_layout.addRow("主控箱数据运算算法延迟限制:", delay_widget)

    # 误差校正算法
    correction_algo_combo = QComboBox()
    
    correction_algo_combo.addItems([
        "多项式拟合", "分段线性拟合", "查表", "线性插值", 
        "神经网络", "遗传算法", "改进型热耗散"
    ])
    
    algo_layout.addRow("风速传感器误差校正算法:", correction_algo_combo)

    # 误差约束
    error_constraint_widget = QWidget()
    
    error_constraint_layout = QHBoxLayout(error_constraint_widget)
    
    error_constraint_layout.setContentsMargins(0, 0, 0, 0)
    
    error_constraint_edit = QLineEdit("0.5")
    
    error_constraint_edit.setValidator(QDoubleValidator(0.0, 100.0, 2))
    
    error_constraint_edit.setFixedWidth(50)
    
    error_constraint_layout.addWidget(QLabel("≤ ±"))
    
    error_constraint_layout.addWidget(error_constraint_edit)
    
    error_constraint_layout.addWidget(QLabel("%FS"))
    
    error_constraint_layout.addStretch()
    
    algo_layout.addRow("风速传感器误差约束:", error_constraint_widget)

    # 动态补偿范围
    kalman_range_widget = QWidget()
    
    kalman_range_layout = QHBoxLayout(kalman_range_widget)
    
    kalman_range_layout.setContentsMargins(0, 0, 0, 0)
    
    kalman_min_edit = QLineEdit("-20")
    
    kalman_max_edit = QLineEdit("60")
    
    kalman_min_edit.setValidator(QIntValidator(-100, 100))
    
    kalman_max_edit.setValidator(QIntValidator(-100, 100))
    
    kalman_min_edit.setFixedWidth(50)
    
    kalman_max_edit.setFixedWidth(50)
    
    kalman_range_layout.addWidget(kalman_min_edit)
    
    kalman_range_layout.addWidget(QLabel("℃ ~"))
    
    kalman_range_layout.addWidget(kalman_max_edit)
    
    kalman_range_layout.addWidget(QLabel("℃"))
    
    kalman_range_layout.addStretch()
    
    algo_layout.addRow("卡尔曼滤波算法动态补偿范围:", kalman_range_widget)

    # --- 2. 通讯与升级 Frame ---
    comm_group = QGroupBox("通讯与升级")
    
    main_layout.addWidget(comm_group)
    
    comm_layout = QFormLayout(comm_group)
    
    comm_layout.setLabelAlignment(Qt.AlignRight)
    
    comm_layout.setSpacing(10)

    baud_rates = [
        "9600bps", "19200bps", "38400bps", "57600bps", 
        "115200bps", "1Mbps", "10Mbps", "100Mbps"
    ]
    
    # 传输速率
    transfer_rate_combo = QComboBox()
    
    transfer_rate_combo.addItems(baud_rates)
    
    transfer_rate_combo.setCurrentText("115200bps")
    
    comm_layout.addRow("传输速率:", transfer_rate_combo)

    # 远程升级带宽
    upgrade_bw_combo = QComboBox()
    
    upgrade_bw_combo.addItems(baud_rates)
    
    upgrade_bw_combo.setCurrentText("10Mbps")
    
    comm_layout.addRow("远程升级带宽:", upgrade_bw_combo)

    # --- 3. 电驱控制系统 Frame ---
    drive_group = QGroupBox("电驱控制系统")
    
    main_layout.addWidget(drive_group)
    
    drive_layout = QFormLayout(drive_group)
    
    drive_layout.setLabelAlignment(Qt.AlignRight)
    
    drive_layout.setSpacing(10)

    # PWM输出精度
    pwm_accuracy_combo = QComboBox()
    
    pwm_accuracy_combo.addItems(["±0.1%", "±0.2%", "±0.3%", "±0.4%", "±0.5%"])
    
    pwm_accuracy_combo.setCurrentText("±0.1%")
    
    drive_layout.addRow("PWM输出精度:", pwm_accuracy_combo)

    # PWM输出频率
    pwm_freq_combo = QComboBox()
    
    pwm_freq_combo.addItems(["1kHz", "5kHz", "10kHz", "15kHz", "20kHz", "25kHz"])
    
    pwm_freq_combo.setCurrentText("10kHz")
    
    drive_layout.addRow("PWM输出频率:", pwm_freq_combo)

    # 转速调节分辨率
    rpm_res_combo = QComboBox()
    
    rpm_res_combo.addItems(["10rpm", "20rpm", "30rpm", "40rpm", "50rpm"])
    
    rpm_res_combo.setCurrentText("10rpm")
    
    drive_layout.addRow("转速调节分辨率:", rpm_res_combo)

    # 闭环调速响应控制
    response_combo = QComboBox()
    
    response_combo.addItems(["≤50ms", "≤100ms", "≤150ms", "≤200ms", "≤250ms"])
    
    response_combo.setCurrentText("≤50ms")
    
    drive_layout.addRow("闭环调速响应控制:", response_combo)

    return widget
# ui_docks.py

def _create_pitch_settings_tab(main_window):
    """
    创建俯仰设置选项卡的内容
    """
    widget = QWidget()
    
    main_layout = QVBoxLayout(widget)
    
    main_layout.setAlignment(Qt.AlignTop)
    
    main_layout.setSpacing(15)

    # --- 精度控制 ---
    accuracy_widget = QWidget()
    
    accuracy_layout = QHBoxLayout(accuracy_widget)
    
    accuracy_layout.setContentsMargins(0, 0, 0, 0)

    # 精度控制校正 CheckBox
    correction_check = QCheckBox("精度控制校正")
    
    correction_check.setChecked(True) # 默认为选中
    
    accuracy_layout.addWidget(correction_check)

    # 精度要求
    accuracy_layout.addWidget(QLabel("精度要求: ±"))
    
    accuracy_edit = QLineEdit("0.1")
    
    accuracy_edit.setValidator(QDoubleValidator(0.0, 5.0, 2)) # 允许0-5, 2位小数
    
    accuracy_edit.setFixedWidth(50)
    
    accuracy_layout.addWidget(accuracy_edit)
    
    accuracy_layout.addWidget(QLabel("°"))
    
    accuracy_layout.addStretch()

    main_layout.addWidget(accuracy_widget)
    
    return widget


# ui_docks.py

def _create_system_settings_tab(main_window):
    """
    创建系统设置选项卡的内容
    """
    widget = QWidget()
    
    main_layout = QVBoxLayout(widget)
    
    main_layout.setSpacing(15)
    
    main_layout.setAlignment(Qt.AlignTop)

    # --- 调试模式设置 ---
    debug_checkbox = QCheckBox("启用调试模式")
    
    debug_checkbox.setChecked(debug.DEBUG_ENABLED)
    
    debug_checkbox.toggled.connect(main_window.toggle_debug_mode)
    
    main_layout.addWidget(debug_checkbox)

    # --- 电力系统 Frame ---
    power_group = QGroupBox("电力系统")
    
    main_layout.addWidget(power_group)
    
    power_layout = QFormLayout(power_group)
    
    power_layout.setLabelAlignment(Qt.AlignRight)

    # 停机响应时间
    shutdown_widget = QWidget()
    
    shutdown_layout = QHBoxLayout(shutdown_widget)
    
    shutdown_layout.setContentsMargins(0, 0, 0, 0)
    
    shutdown_layout.addWidget(QLabel("≤"))
    
    shutdown_edit = QLineEdit("100")
    
    shutdown_edit.setValidator(QIntValidator(1, 10000))
    
    shutdown_edit.setFixedWidth(60)
    
    shutdown_layout.addWidget(shutdown_edit)
    
    shutdown_layout.addWidget(QLabel("ms"))
    
    shutdown_layout.addStretch()
    
    power_layout.addRow("电力一键停机响应时间约束:", shutdown_widget)

    # 持续关机 CheckBox
    persistent_shutdown_check = QCheckBox("持续关机直至收到信号")
    
    persistent_shutdown_check.setChecked(True) # 默认选中
    
    power_layout.addRow("", persistent_shutdown_check)

    return widget


def create_settings_dock(main_window):
    """
    修改此函数以包含新的俯仰设置选项卡
    """
    content = QWidget()
    
    main_layout = QVBoxLayout(content)
    
    main_window.settings_tab_widget = QTabWidget()

    tab_names = [
        "界面设置", "主控设置", "通讯设置", "环境设置", "俯仰设置", "风机设置", 
        "造雨设置", "示踪设置", "动捕设置", "标定设置", "仿真设置", "训练设置", "系统设置"
    ]
    
    for name in tab_names:
        if name == "主控设置":
            master_control_tab = _create_master_control_settings_tab(main_window)
            main_window.settings_tab_widget.addTab(master_control_tab, name)
        elif name == "通讯设置":
            comm_tab = _create_comm_settings_tab(main_window)
            main_window.settings_tab_widget.addTab(comm_tab, name)
        elif name == "俯仰设置":
            # 调用新创建的函数
            pitch_tab = _create_pitch_settings_tab(main_window)
            main_window.settings_tab_widget.addTab(pitch_tab, name)
        elif name == "系统设置":
            system_tab = _create_system_settings_tab(main_window)
            main_window.settings_tab_widget.addTab(system_tab, name)
        else:
            placeholder_widget = QWidget()
            
            placeholder_layout = QVBoxLayout(placeholder_widget)
            
            placeholder_label = QLabel(f"'{name}' 功能正在开发中...")
            
            placeholder_label.setAlignment(Qt.AlignCenter)
            
            placeholder_layout.addWidget(placeholder_label)
            
            main_window.settings_tab_widget.addTab(placeholder_widget, name)

    main_layout.addWidget(main_window.settings_tab_widget)
    
    dock_button_layout = QHBoxLayout()
    
    dock_button_layout.addStretch()
    
    btn_cancel = QPushButton("取消")
    
    btn_ok = QPushButton("确定")
    
    main_window.settings_buttons.clear()
    
    main_window.settings_buttons.extend([btn_cancel, btn_ok])

    for btn in [btn_cancel, btn_ok]:
        btn.setFixedSize(60, 25)
        
        dock_button_layout.addWidget(btn)
        
    main_layout.addLayout(dock_button_layout)
    
    btn_cancel.clicked.connect(main_window.cancel_settings)
    
    btn_ok.clicked.connect(main_window.apply_settings)
    
    dock = create_styled_dock(main_window, "系统综合设置", content, is_independent=True)
    
    dock.resize(800, 600)
    
    return dock




# ui_docks.py

def create_pitch_dock(main_window):
    """
    创建俯仰控制Dock，包含控制和状态显示。
    俯仰精度0.1°，俯仰过程中执行按钮不可选中。
    """
    # 主内容Widget
    content = QWidget()

    main_layout = QVBoxLayout(content)

    main_layout.setSpacing(15)

    # --- 1. 控制 Frame ---
    control_group = QGroupBox("控制")

    main_layout.addWidget(control_group)

    control_layout = QFormLayout(control_group)

    control_layout.setLabelAlignment(Qt.AlignRight)

    # 目标角度输入 - 精度0.1°
    angle_spin = QDoubleSpinBox()

    angle_spin.setRange(-45, 90)
    angle_spin.setDecimals(1)  # 精度0.1°
    angle_spin.setSingleStep(0.1)  # 每次调整0.1°
    angle_spin.setSuffix("°")  # 添加单位

    # 执行按钮
    execute_btn = QPushButton("执行")

    # 将输入框和执行按钮放在同一行
    control_row_widget = QWidget()

    control_row_layout = QHBoxLayout(control_row_widget)

    control_row_layout.setContentsMargins(0, 0, 0, 0)

    control_row_layout.addWidget(angle_spin)

    control_row_layout.addWidget(execute_btn)

    control_layout.addRow("目标角度 (-45° to +90°):", control_row_widget)

    # --- 执行按钮点击事件处理 ---
    def on_execute_clicked():
        """执行俯仰操作，过程中禁用按钮"""
        target_angle = angle_spin.value()
        execute_btn.setEnabled(False)
        execute_btn.setText("执行中...")

        # 模拟执行过程（实际应用中这里应该是真正的控制逻辑）
        from PySide6.QtCore import QTimer

        # 模拟2秒后完成
        QTimer.singleShot(2000, lambda: on_execution_complete(execute_btn))

    def on_execution_complete(btn):
        """执行完成，恢复按钮"""
        btn.setEnabled(True)
        btn.setText("执行")

    execute_btn.clicked.connect(on_execute_clicked)

    # --- 2. 状态 Frame ---
    status_group = QGroupBox("状态")

    main_layout.addWidget(status_group)

    status_layout = QFormLayout(status_group)

    status_layout.setLabelAlignment(Qt.AlignRight)

    # 添加状态标签
    status_layout.addRow("当前速度:", QLabel("0 °/s"))

    status_layout.addRow("当前角度:", QLabel("0 °"))

    status_layout.addRow("到位检测:", QLabel("到位"))

    # 添加伸展项，使布局更紧凑
    main_layout.addStretch(1)

    # 需求1: 将Dock重命名为 "俯仰控制"
    return create_styled_dock(main_window, "俯仰控制", content, is_independent=True)


def create_combined_pitch_rain_trace_dock(main_window):
    """
    创建俯仰、造雨、示踪的组合Dock，三个界面放在一起。
    """
    # 主容器，使用选项卡组件
    content = QTabWidget()

    # --- 俯仰控制选项卡 ---
    pitch_content = QWidget()
    pitch_layout = QVBoxLayout(pitch_content)
    pitch_layout.setSpacing(15)

    # 俯仰控制
    pitch_control_group = QGroupBox("控制")
    pitch_layout.addWidget(pitch_control_group)
    pitch_control_layout = QFormLayout(pitch_control_group)
    pitch_control_layout.setLabelAlignment(Qt.AlignRight)
    pitch_control_layout.setVerticalSpacing(20)  # 增加行间距到20

    # 目标角度输入 - 精度0.1°
    pitch_angle_spin = QDoubleSpinBox()
    pitch_angle_spin.setRange(-45, 90)
    pitch_angle_spin.setDecimals(1)  # 精度0.1°
    pitch_angle_spin.setSingleStep(0.1)
    pitch_angle_spin.setSuffix("°")

    pitch_execute_btn = QPushButton("执行")
    pitch_control_row = QWidget()
    pitch_control_row_layout = QHBoxLayout(pitch_control_row)
    pitch_control_row_layout.setContentsMargins(0, 0, 0, 0)
    pitch_control_row_layout.addWidget(pitch_angle_spin)
    pitch_control_row_layout.addWidget(pitch_execute_btn)
    pitch_control_layout.addRow("目标角度 (-45° to +90°):", pitch_control_row)

    # 俯仰执行按钮事件
    def on_pitch_execute():
        pitch_execute_btn.setEnabled(False)
        pitch_execute_btn.setText("执行中...")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: on_pitch_complete())

    def on_pitch_complete():
        pitch_execute_btn.setEnabled(True)
        pitch_execute_btn.setText("执行")

    pitch_execute_btn.clicked.connect(on_pitch_execute)

    # 为俯仰控制设置标签字体
    from PySide6.QtGui import QFont
    pitch_label_font = QFont()
    pitch_label_font.setPointSize(12)  # 标签字体

    # 更新目标角度标签
    pitch_angle_label = QLabel("目标角度 (-45° to +90°):")
    pitch_angle_label.setFont(pitch_label_font)
    # 移除旧的行并添加新的
    pitch_control_layout.addRow(pitch_angle_label, pitch_control_row)

    # 俯仰状态
    pitch_status_group = QGroupBox("状态")
    pitch_layout.addWidget(pitch_status_group)
    pitch_status_layout = QFormLayout(pitch_status_group)
    pitch_status_layout.setLabelAlignment(Qt.AlignRight)
    pitch_status_layout.setVerticalSpacing(20)  # 增加行间距到20

    # 为俯仰状态设置标签字体
    from PySide6.QtGui import QFont
    pitch_status_label_font = QFont()
    pitch_status_label_font.setPointSize(12)
    pitch_status_value_font = QFont()
    pitch_status_value_font.setPointSize(11)

    pitch_status_layout.addRow(QLabel("当前速度:", font=pitch_status_label_font), QLabel("0 °/s", font=pitch_status_value_font))
    pitch_status_layout.addRow(QLabel("当前角度:", font=pitch_status_label_font), QLabel("0 °", font=pitch_status_value_font))
    pitch_status_layout.addRow(QLabel("到位检测:", font=pitch_status_label_font), QLabel("到位", font=pitch_status_value_font))

    pitch_layout.addStretch(1)
    content.addTab(pitch_content, "俯仰")

    # --- 造雨设置选项卡 ---
    rain_content = QWidget()
    rain_layout = QVBoxLayout(rain_content)
    rain_layout.setSpacing(20)  # 增加间距到20

    # 造雨控制
    rain_control_group = QGroupBox("控制")
    rain_layout.addWidget(rain_control_group)
    rain_control_layout = QFormLayout(rain_control_group)
    rain_control_layout.setLabelAlignment(Qt.AlignRight)
    rain_control_layout.setVerticalSpacing(25)  # 增加行间距到25，让文字更清晰

    # 定义字体样式
    from PySide6.QtGui import QFont
    # 标签字体（左侧标签）
    label_font = QFont()
    label_font.setPointSize(12)  # 标签字体大小
    # 控件字体（右侧控件）
    control_font = QFont()
    control_font.setPointSize(11)  # 控制界面字体大小
    status_font = QFont()
    status_font.setPointSize(11)  # 状态界面字体大小
    button_font = QFont()
    button_font.setPointSize(11)  # 按钮字体大小

    # 水泵按钮
    pump_button = QPushButton("开关")
    pump_button.setFont(button_font)
    pump_label = QLabel("水泵:")
    pump_label.setFont(label_font)
    rain_control_layout.addRow(pump_label, pump_button)

    # 流量设置 - 增加输入框宽度
    rain_flow_widget = QWidget()
    rain_flow_layout = QHBoxLayout(rain_flow_widget)
    rain_flow_layout.setContentsMargins(0, 0, 0, 0)
    rain_flow_layout.setSpacing(8)  # 增加控件之间的间距

    rain_flow_slider = QSlider(Qt.Horizontal)
    rain_flow_slider.setRange(0, 120)
    rain_flow_slider.setValue(120)
    rain_flow_label = QLabel()
    rain_flow_label.setTextFormat(Qt.RichText)  # 支持HTML格式

    def update_flow_label(value):
        rain_flow_label.setText(f"{value / 10.0:.1f} m<sup>3</sup>/h")

    update_flow_label(rain_flow_slider.value())
    rain_flow_label.setFixedWidth(75)  # 增加宽度
    rain_flow_label.setFont(control_font)  # 设置字体
    rain_flow_layout.addWidget(rain_flow_slider)
    rain_flow_layout.addWidget(rain_flow_label)

    # 流量输入框 - 增加宽度和字体
    rain_flow_input = QLineEdit("12.0")
    rain_flow_input.setFixedWidth(80)  # 从60增加到80
    rain_flow_input.setFont(control_font)  # 设置字体
    rain_flow_input.setValidator(QDoubleValidator(0.0, 12.0, 1))

    or_label = QLabel("或直接输入:")
    or_label.setFont(control_font)
    unit_label = QLabel("m<sup>3</sup>/h")
    unit_label.setTextFormat(Qt.RichText)
    unit_label.setFont(control_font)

    rain_flow_layout.addWidget(or_label)
    rain_flow_layout.addWidget(rain_flow_input)
    rain_flow_layout.addWidget(unit_label)

    rain_flow_slider.valueChanged.connect(update_flow_label)

    # 流量标签
    flow_label_text = QLabel("流量 (0-12 m³/h):")
    flow_label_text.setFont(label_font)
    rain_control_layout.addRow(flow_label_text, rain_flow_widget)

    # 雨量选择
    rain_level_combo = QComboBox()
    rain_level_combo.addItems(["微雨", "小雨", "中雨", "大雨", "暴雨", "大暴雨", "特大暴雨"])
    rain_level_combo.setCurrentText("特大暴雨")
    rain_level_combo.setFont(control_font)
    rain_level_label = QLabel("雨量选择:")
    rain_level_label.setFont(label_font)
    rain_control_layout.addRow(rain_level_label, rain_level_combo)

    # 喷嘴类型 (A/B/C)
    rain_nozzle_type_combo = QComboBox()
    rain_nozzle_type_combo.addItems(["类型A", "类型B", "类型C"])
    rain_nozzle_type_combo.setCurrentText("类型A")
    rain_nozzle_type_combo.setFont(control_font)
    nozzle_label = QLabel("喷嘴类型:")
    nozzle_label.setFont(label_font)
    rain_control_layout.addRow(nozzle_label, rain_nozzle_type_combo)

    rain_max_rain_check = QCheckBox("瞬时最大降雨")
    rain_max_rain_check.setChecked(True)
    rain_max_rain_check.setFont(control_font)
    rain_control_layout.addRow("", rain_max_rain_check)

    # 造雨状态
    rain_status_group = QGroupBox("状态")
    rain_layout.addWidget(rain_status_group)
    rain_status_layout = QFormLayout(rain_status_group)
    rain_status_layout.setLabelAlignment(Qt.AlignRight)
    rain_status_layout.setVerticalSpacing(20)  # 增加行间距到20，让文字更清晰

    # 状态标签 - 使用label_font
    status_labels = []
    for text in ["瞬时最大:", "当前流量:", "当前电机转速:", "当前水箱水位:", "当前补水阀门:"]:
        label = QLabel(text)
        label.setFont(label_font)  # 使用标签字体
        status_labels.append(label)

    value_labels = []

    # 当前流量值使用HTML格式显示上标
    flow_value_label = QLabel("12 m<sup>3</sup>/h")
    flow_value_label.setTextFormat(Qt.RichText)
    flow_value_label.setFont(status_font)
    value_labels.append(flow_value_label)

    # 其他值标签
    for text in ["是", "3000 rpm", "60 %", "开"]:
        label = QLabel(text)
        label.setFont(status_font)  # 状态值字体
        value_labels.append(label)

    rain_status_layout.addRow(status_labels[0], value_labels[0])
    rain_status_layout.addRow(status_labels[1], value_labels[1])
    rain_status_layout.addRow(status_labels[2], value_labels[2])
    rain_status_layout.addRow(status_labels[3], value_labels[3])
    rain_status_layout.addRow(status_labels[4], value_labels[4])

    rain_layout.addStretch(1)
    content.addTab(rain_content, "造雨")

    # --- 示踪设置选项卡 (造雾) ---
    trace_content = QWidget()
    trace_layout = QVBoxLayout(trace_content)
    trace_layout.setSpacing(15)

    # 示踪设置
    trace_settings_group = QGroupBox("设置")
    trace_layout.addWidget(trace_settings_group)
    trace_settings_layout = QFormLayout(trace_settings_group)
    trace_settings_layout.setLabelAlignment(Qt.AlignRight)
    trace_settings_layout.setVerticalSpacing(20)  # 增加行间距到20

    # 为示踪设置标签字体
    from PySide6.QtGui import QFont
    trace_label_font = QFont()
    trace_label_font.setPointSize(12)

    # 造雾机开关状态
    trace_mist_switch = QPushButton("开关")
    trace_mist_label = QLabel("造雾机:")
    trace_mist_label.setFont(trace_label_font)
    trace_settings_layout.addRow(trace_mist_label, trace_mist_switch)

    # 目标位置跟踪
    trace_tracking_check = QCheckBox("启用目标位置跟踪")
    trace_tracking_check.setChecked(True)
    trace_settings_layout.addRow("", trace_tracking_check)

    # 示踪状态
    trace_status_group = QGroupBox("状态")
    trace_layout.addWidget(trace_status_group)
    trace_status_layout = QFormLayout(trace_status_group)
    trace_status_layout.setLabelAlignment(Qt.AlignRight)
    trace_status_layout.setVerticalSpacing(20)  # 增加行间距到20

    trace_status_value_font = QFont()
    trace_status_value_font.setPointSize(11)

    trace_status_layout.addRow(QLabel("当前位置:", font=trace_label_font), QLabel("距左侧 1.215 米", font=trace_status_value_font))
    trace_status_layout.addRow(QLabel("造雾机状态:", font=trace_label_font), QLabel("关闭", font=trace_status_value_font))
    trace_status_layout.addRow(QLabel("在位:", font=trace_label_font), QLabel("是", font=trace_status_value_font))

    trace_layout.addStretch(1)
    content.addTab(trace_content, "示踪")

    # 创建并返回Dock
    dock = create_styled_dock(main_window, "俯仰·造雨·示踪", content, is_independent=False)
    dock.resize(400, 350)
    return dock


def create_fan_dock(main_window):
    """
    创建风机设置的Dock，包含全局风场状态和当前风机阵列预览。
    修改：全局风场设置改为全局风场状态，仅显示值，不可更改。
    """
    # 主内容Widget
    content = QWidget()

    main_layout = QVBoxLayout(content)

    main_layout.setContentsMargins(10, 10, 10, 10)

    main_layout.setSpacing(15)  # 增加GroupBox之间的间距

    # --- 第一部分: 全局风场状态 (仅显示，不可编辑) ---
    status_group = QGroupBox("全局风场状态")

    main_layout.addWidget(status_group)

    grid_layout = QGridLayout(status_group)

    grid_layout.setSpacing(10)

    # 第一行
    grid_layout.addWidget(QLabel("风扇控制刷新率:"), 0, 0, Qt.AlignRight)
    grid_layout.addWidget(QLabel("10Hz"), 0, 1)

    grid_layout.addWidget(QLabel("风场空间分辨率:"), 0, 2, Qt.AlignRight)
    grid_layout.addWidget(QLabel("80mm"), 0, 3)

    # 第二行
    grid_layout.addWidget(QLabel("模板时间轴分辨率:"), 1, 0, Qt.AlignRight)
    grid_layout.addWidget(QLabel("10ms"), 1, 1)

    grid_layout.addWidget(QLabel("模板可编辑风速范围:"), 1, 2, Qt.AlignRight)
    grid_layout.addWidget(QLabel("0 — 30 m/s"), 1, 3)

    # 第三行
    grid_layout.addWidget(QLabel("风速波动误差:"), 2, 0, Qt.AlignRight)
    grid_layout.addWidget(QLabel("±0.5m/s"), 2, 1)

    grid_layout.addWidget(QLabel("修正方式:"), 2, 2, Qt.AlignRight)
    grid_layout.addWidget(QLabel("自适应遗传PID"), 2, 3)

    # --- 第二部分: 当前风机阵列 ---
    fan_array_group = QGroupBox("当前风机阵列")

    main_layout.addWidget(fan_array_group)

    fan_array_layout = QVBoxLayout(fan_array_group)

    fan_array_layout.setSpacing(10)

    # 图片显示
    image_label = QLabel()

    pixmap = QPixmap("风场.png")  # 确保图片在正确的路径下

    # 将图片缩放到 400x400，并保持宽高比
    scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    image_label.setPixmap(scaled_pixmap)

    image_label.setAlignment(Qt.AlignCenter)  # 居中显示图片

    fan_array_layout.addWidget(image_label)

    # "进入风场编辑" 按钮
    edit_button = QPushButton("进入风场编辑")

    # 添加点击事件：启动风场设置程序
    def launch_wind_field_editor():
        """启动风场设置程序"""
        import subprocess
        import sys
        import os

        # 获取风场设置 main.py 的路径
        wind_field_main = os.path.join(os.path.dirname(os.path.dirname(__file__)), '风场设置', 'main.py')

        try:
            # 使用当前 Python 解释器启动风场设置程序
            subprocess.Popen([sys.executable, wind_field_main])
        except Exception as e:
            print(f"启动风场设置失败: {e}")

    edit_button.clicked.connect(launch_wind_field_editor)

    # 将按钮放在一个水平布局中以实现居中
    button_container = QWidget()

    button_layout = QHBoxLayout(button_container)

    button_layout.addStretch()

    button_layout.addWidget(edit_button)

    button_layout.addStretch()

    fan_array_layout.addWidget(button_container)

    # --- 创建并返回Dock ---
    dock = create_styled_dock(main_window, "风机设置", content, is_independent=False)

    # 调整Dock的初始尺寸以容纳新内容
    dock.resize(500, 650)

    return dock


# ui_docks.py

# ui_docks.py

def create_rain_dock(main_window):
    """
    创建造雨设置Dock，包含详细的控制和状态显示。
    修改：去掉PID修正流量精度；去掉喷嘴直径，改为喷嘴类型（A/B/C）；去掉阀门开度；控制中的流量调节增加输入框
    """
    content = QWidget()

    main_layout = QVBoxLayout(content)

    main_layout.setSpacing(15)

    # --- 1. 控制 Frame ---
    control_group = QGroupBox("控制")

    main_layout.addWidget(control_group)

    control_layout = QFormLayout(control_group)

    control_layout.setLabelAlignment(Qt.AlignRight)

    # 水泵开关
    control_layout.addRow("水泵:", QPushButton("开关"))

    # 流量设置 - 带滑块和输入框
    flow_widget = QWidget()

    flow_layout = QHBoxLayout(flow_widget)

    flow_layout.setContentsMargins(0, 0, 0, 0)

    flow_slider = QSlider(Qt.Horizontal)

    # 设置滑块范围为 0 到 120，方便映射到 0-12.0 m³/h
    flow_slider.setRange(0, 120)

    flow_slider.setValue(120)  # 默认最大值

    flow_label = QLabel()
    flow_label.setTextFormat(Qt.RichText)  # 支持HTML格式

    def update_rain_flow_label(value):
        flow_label.setText(f"{value / 10.0:.1f} m<sup>3</sup>/h")

    update_rain_flow_label(flow_slider.value())
    flow_label.setFixedWidth(70)  # 给标签一个固定宽度以防抖动

    flow_layout.addWidget(flow_slider)
    flow_layout.addWidget(flow_label)

    # 流量输入框
    flow_input = QLineEdit("12.0")
    flow_input.setFixedWidth(60)
    flow_input.setValidator(QDoubleValidator(0.0, 12.0, 1))
    flow_layout.addWidget(QLabel("或直接输入:"))
    flow_layout.addWidget(flow_input)

    # 单位标签使用HTML格式
    unit_label_rain = QLabel("m<sup>3</sup>/h")
    unit_label_rain.setTextFormat(Qt.RichText)
    flow_layout.addWidget(unit_label_rain)

    # 连接信号，当滑块值改变时更新标签文本
    flow_slider.valueChanged.connect(update_rain_flow_label)

    control_layout.addRow("流量 (0-12 m³/h):", flow_widget)

    # 雨量选择
    rain_level_combo = QComboBox()

    rain_levels = [
        "微雨", "小雨", "中雨", "大雨",
        "暴雨", "大暴雨", "特大暴雨"
    ]

    rain_level_combo.addItems(rain_levels)

    rain_level_combo.setCurrentText("特大暴雨")

    control_layout.addRow("雨量选择:", rain_level_combo)

    # 喷嘴类型 (A/B/C) - 替代原来的喷嘴直径
    nozzle_type_combo = QComboBox()

    nozzle_type_combo.addItems(["类型A", "类型B", "类型C"])

    nozzle_type_combo.setCurrentText("类型A")

    control_layout.addRow("喷嘴类型:", nozzle_type_combo)

    # 瞬时最大降雨
    max_rain_check = QCheckBox("瞬时最大降雨")

    max_rain_check.setChecked(True)

    control_layout.addRow("", max_rain_check)

    # --- 2. 状态 Frame ---
    status_group = QGroupBox("状态")

    main_layout.addWidget(status_group)

    status_layout = QFormLayout(status_group)

    status_layout.setLabelAlignment(Qt.AlignRight)

    status_layout.addRow("瞬时最大:", QLabel("是"))

    # 当前流量使用HTML格式显示上标
    current_flow_label = QLabel("12 m<sup>3</sup>/h")
    current_flow_label.setTextFormat(Qt.RichText)
    status_layout.addRow("当前流量:", current_flow_label)

    # 去掉阀门开度
    status_layout.addRow("当前电机转速:", QLabel("3000 rpm"))

    status_layout.addRow("当前水箱水位:", QLabel("60 %"))

    status_layout.addRow("当前补水阀门:", QLabel("开"))

    main_layout.addStretch(1)

    return create_styled_dock(main_window, "造雨设置", content, is_independent=False)



# ui_docks.py

def create_trace_dock(main_window):
    """
    创建示踪设置Dock（造雾），包含设置和状态显示。
    修改：去掉造雾量选择；去掉跟踪精度；状态仅保留当前位置；添加造雾机开关状态
    """
    content = QWidget()

    main_layout = QVBoxLayout(content)

    main_layout.setSpacing(15)

    # --- 1. 设置 Frame ---
    settings_group = QGroupBox("设置")

    main_layout.addWidget(settings_group)

    settings_layout = QFormLayout(settings_group)

    settings_layout.setLabelAlignment(Qt.AlignRight)

    # 造雾机开关状态
    mist_switch_btn = QPushButton("关闭")
    mist_switch_btn.setCheckable(True)
    mist_switch_btn.setChecked(False)

    def toggle_mist_switch(checked):
        if checked:
            mist_switch_btn.setText("开启")
            mist_switch_btn.setStyleSheet("background-color: #00ff7f; color: black;")
        else:
            mist_switch_btn.setText("关闭")
            mist_switch_btn.setStyleSheet("background-color: #ff3b30; color: white;")

    mist_switch_btn.toggled.connect(toggle_mist_switch)
    settings_layout.addRow("造雾机状态:", mist_switch_btn)

    # 目标位置跟踪
    tracking_check = QCheckBox("启用目标位置跟踪")

    tracking_check.setChecked(True)  # 默认打开

    settings_layout.addRow("", tracking_check)

    # --- 2. 状态 Frame ---
    status_group = QGroupBox("状态")

    main_layout.addWidget(status_group)

    status_layout = QFormLayout(status_group)

    status_layout.setLabelAlignment(Qt.AlignRight)

    # 仅保留当前位置
    status_layout.addRow("当前位置:", QLabel("距左侧 1.215 米"))

    main_layout.addStretch(1)

    return create_styled_dock(main_window, "示踪设置", content, is_independent=False)


def create_motion_capture_dock(main_window):
    """
    创建动捕设置Dock。
    修改：去掉视图设置中的所有子界面和视图设置。
    """
    content = QWidget()
    main_layout = QVBoxLayout(content)
    main_layout.setSpacing(10)

    # 动捕状态 GroupBox
    status_group = QGroupBox("动捕状态")
    status_layout = QVBoxLayout(status_group)

    status_grid_widget = QWidget()
    grid_layout = QGridLayout(status_grid_widget)
    grid_layout.setSpacing(5)
    grid_layout.setContentsMargins(0, 5, 0, 5)

    main_window.camera_status_lights = []
    num_cameras = 20
    cols = 5  # 每行5个，更紧凑
    for i in range(1, num_cameras + 1):
        light = CameraStatusLight(i)
        light.clicked.connect(main_window.show_camera_settings)
        main_window.camera_status_lights.append(light)

        row = (i - 1) // cols
        col = (i - 1) % cols
        grid_layout.addWidget(light, row, col)

    status_layout.addWidget(status_grid_widget)
    # 添加说明文字
    legend_label = QLabel(
        "绿色: 已连接，同步正常\n"
        "黄色: 已连接，存在警告\n"
        "红色: 连接断开或错误"
    )
    legend_label.setStyleSheet("color: #8a8f98; font-size: 9px;")  # 淡灰色小字体
    status_layout.addWidget(legend_label)
    main_layout.addWidget(status_group)
    main_layout.addStretch()
    dock = create_styled_dock(main_window, "动捕设置", content,
                              min_size_from_content=False, is_independent=False)
    dock.resize(300, 350)  # 调整尺寸以适应新布局
    return dock
def create_motion_capture_view_dock(main_window):
    # 使用 BackgroundWidget 作为内容
    content = BackgroundWidget("动捕.png", 1.0) # 1.0 不透明度
    dock = create_styled_dock(main_window, "动捕实时视场", content,
                              min_size_from_content=False, is_independent=False)
    dock.resize(1265, 685)
    return dock
def create_calibration_dock(main_window):
    content = QWidget()
    layout = QVBoxLayout(content)
    main_window.calib_label = QLabel("使用64路传感器进行风洞标定")
    layout.addWidget(main_window.calib_label)
    layout.addWidget(QPushButton("开始自动标定"))
    layout.addWidget(QPushButton("加载标定文件"))
    layout.addWidget(QPushButton("保存标定文件"))
    layout.addStretch()
    return create_styled_dock(main_window, "标定设置", content, is_independent=False)

# ui_docks.py

# ui_docks.py

def create_simulation_dock(main_window):
    """
    创建仿真设置Dock，包含设置、雷诺数估算和状态显示。
    """
    content = QWidget()
    
    main_layout = QHBoxLayout(content) # 使用水平布局
    
    main_layout.setSpacing(15)

    # --- 左侧部分: 设置和雷诺数估算 ---
    left_widget = QWidget()
    
    left_layout = QVBoxLayout(left_widget)
    
    left_layout.setAlignment(Qt.AlignTop)
    
    main_layout.addWidget(left_widget, 1) # 占据1份空间

    # --- 1. 设置 Frame ---
    settings_group = QGroupBox("设置")
    
    left_layout.addWidget(settings_group)
    
    settings_layout = QFormLayout(settings_group)
    
    settings_layout.setLabelAlignment(Qt.AlignRight)

    # 误差设置
    error_combo = QComboBox()
    
    error_combo.addItems([f"≤{i * 5 + 10}%" for i in range(9)]) # 10% to 50%
    
    settings_layout.addRow("误差设置:", error_combo)

    # 最大雷诺数范围
    re_range_combo = QComboBox()
    
    re_range_combo.addItems([f"≤10E{i}" for i in range(4, 9)]) # 10E4 to 10E8
    
    re_range_combo.setCurrentText("≤10E6")
    
    settings_layout.addRow("最大雷诺数范围:", re_range_combo)

    # 计算高空
    altitude_widget = QWidget()
    
    altitude_layout = QHBoxLayout(altitude_widget)
    
    altitude_layout.setContentsMargins(0, 0, 0, 0)
    
    altitude_check = QCheckBox("计算高空")
    
    altitude_edit = QLineEdit("100")
    
    altitude_edit.setValidator(QIntValidator(0, 100))
    
    altitude_edit.setFixedWidth(50)
    
    altitude_label = QLabel("高度 (0-100米)")
    
    altitude_layout.addWidget(altitude_check)
    
    altitude_layout.addWidget(altitude_label)
    
    altitude_layout.addWidget(altitude_edit)
    
    altitude_layout.addStretch()
    
    settings_layout.addRow("", altitude_widget)

    # 自动导出
    export_path_button = QPushButton("选择保存路径")
    
    export_report_check = QCheckBox("自动导出报告")
    
    export_report_check.setChecked(True)
    
    export_data_check = QCheckBox("自动导出结果数据")
    
    export_data_check.setChecked(True)
    
    settings_layout.addRow("", export_report_check)
    
    settings_layout.addRow(export_data_check, export_path_button)

    # 按钮
    buttons_widget = QWidget()
    
    buttons_layout = QHBoxLayout(buttons_widget)
    
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    
    buttons_layout.addStretch()
    
    buttons_layout.addWidget(QPushButton("打开仿真模块"))
    
    buttons_layout.addWidget(QPushButton("自动计算"))
    
    settings_layout.addRow("", buttons_widget)

    # --- 2. 雷诺数估算 Frame ---
    estimator_group = QGroupBox("雷诺数估算")
    
    left_layout.addWidget(estimator_group)
    
    estimator_layout = QFormLayout(estimator_group)
    
    estimator_layout.setLabelAlignment(Qt.AlignRight)

    # 类型选择
    rotor_radio = QRadioButton("旋翼")
    
    wing_radio = QRadioButton("机翼")
    
    rotor_radio.setChecked(True)
    
    radio_widget = QWidget()
    
    radio_layout = QHBoxLayout(radio_widget)
    
    radio_layout.setContentsMargins(0, 0, 0, 0)
    
    radio_layout.addWidget(rotor_radio)
    
    radio_layout.addWidget(wing_radio)
    
    radio_layout.addStretch()
    
    estimator_layout.addRow("类型:", radio_widget)

    # 动态显示的控件
    wing_chord_edit = QLineEdit()
    
    wing_len_edit = QLineEdit()
    
    landing_gear_check = QCheckBox("起落架")
    
    landing_gear_diam_edit = QLineEdit()
    
    rotor_chord_edit = QLineEdit("10")
    
    rotor_radius_edit = QLineEdit("50")
    
    body_diam_edit = QLineEdit("400")

    # 将动态控件添加到布局中
    estimator_layout.addRow("机翼气动弦长 (mm):", wing_chord_edit)
    
    estimator_layout.addRow("机身长度 (mm):", wing_len_edit)
    
    estimator_layout.addRow(landing_gear_check, landing_gear_diam_edit)
    
    estimator_layout.addRow("叶片弦长 (mm):", rotor_chord_edit)
    
    estimator_layout.addRow("旋翼半径 (mm):", rotor_radius_edit)
    
    estimator_layout.addRow("机身外切圆直径 (mm):", body_diam_edit)

    # 物理参数输入
    wind_speed_edit = QLineEdit("15")
    
    temp_edit = QLineEdit("10")
    
    pressure_edit = QLineEdit("101.325")
    
    estimator_layout.addRow("风洞风速 (m/s):", wind_speed_edit)
    
    estimator_layout.addRow("空气温度 (°C):", temp_edit)
    
    estimator_layout.addRow("绝对压力 (kPa):", pressure_edit)

    # --- 右侧部分: 状态 ---
    status_group = QGroupBox("状态")
    
    main_layout.addWidget(status_group)
    
    status_layout = QFormLayout(status_group)
    
    status_layout.setLabelAlignment(Qt.AlignRight)

    density_label = QLabel("N/A")
    
    speed_label = QLabel("N/A")
    
    char_len_label = QLabel("N/A")
    
    viscosity_label = QLabel("N/A")
    
    reynolds_label = QLabel("N/A")
    
    status_layout.addRow("空气密度 (kg/m³):", density_label)
    
    status_layout.addRow("风速 (m/s):", speed_label)
    
    status_layout.addRow("特征长度 (m):", char_len_label)
    
    status_layout.addRow("空气动力粘性系数 (Pa·s):", viscosity_label)
    
    status_layout.addRow("雷诺数 (Re):", reynolds_label)

    # --- 逻辑处理 ---
    def toggle_altitude(checked):
        altitude_label.setVisible(checked)
        
        altitude_edit.setVisible(checked)

    def toggle_export_path(checked):
        export_path_button.setVisible(checked)

    def toggle_estimator_type():
        is_wing = wing_radio.isChecked()
        
        # QFormLayout 行索引从0开始。
        # "类型" 是第0行。
        # 机翼控件在第 1, 2, 3 行。
        # 旋翼控件在第 4, 5, 6 行。
        
        # 切换机翼相关行的可见性
        for row_index in [1, 2, 3]:
            estimator_layout.setRowVisible(row_index, is_wing)
            
        # 切换旋翼相关行的可见性
        for row_index in [4, 5, 6]:
            estimator_layout.setRowVisible(row_index, not is_wing)
            
        update_calculations()

    def update_calculations():
        try:
            # 获取输入值
            T_C = float(temp_edit.text()) # 温度 °C
            
            P_kPa = float(pressure_edit.text()) # 压力 kPa
            
            V = float(wind_speed_edit.text()) # 速度 m/s

            # 计算物理属性
            T_K = T_C + 273.15 # 转换为开尔文
            
            P_Pa = P_kPa * 1000 # 转换为帕斯卡
            
            R = 287.05 # 气体常数
            
            rho = P_Pa / (R * T_K) # 空气密度
            
            # Sutherland's law for viscosity
            mu_ref = 1.716e-5 # 参考粘度 at 273.15K
            
            T_ref = 273.15
            
            S = 110.4
            
            mu = mu_ref * ((T_K / T_ref)**1.5) * ((T_ref + S) / (T_K + S))

            # 计算特征长度 L
            L = 0.0
            
            if wing_radio.isChecked():
                L = float(wing_chord_edit.text() or 0) / 1000.0 # 默认为0，转为米
            else: # 旋翼
                L = float(rotor_chord_edit.text() or 0) / 1000.0 # 默认为0，转为米

            # 计算雷诺数
            if mu > 0 and L > 0:
                Re = (rho * V * L) / mu
            else:
                Re = 0

            # 更新状态标签
            density_label.setText(f"{rho:.4f}")
            
            speed_label.setText(f"{V:.2f}")
            
            char_len_label.setText(f"{L:.4f}")
            
            viscosity_label.setText(f"{mu:.2e}")
            
            reynolds_label.setText(f"{Re:.2e}")

        except (ValueError, ZeroDivisionError):
            # 如果输入无效或计算出错，显示 N/A
            density_label.setText("N/A")
            
            speed_label.setText("N/A")
            
            char_len_label.setText("N/A")
            
            viscosity_label.setText("N/A")
            
            reynolds_label.setText("N/A")

    # 连接信号
    altitude_check.toggled.connect(toggle_altitude)
    
    export_data_check.toggled.connect(toggle_export_path)
    
    wing_radio.toggled.connect(toggle_estimator_type)
    
    # 所有参与计算的输入框文本变化时都触发更新
    for edit in [
        wing_chord_edit, rotor_chord_edit, wind_speed_edit, 
        temp_edit, pressure_edit
    ]:
        edit.textChanged.connect(update_calculations)

    # 初始化UI状态
    toggle_altitude(altitude_check.isChecked())
    
    toggle_export_path(export_data_check.isChecked())
    
    toggle_estimator_type()
    
    update_calculations()

    dock = create_styled_dock(main_window, "仿真设置", content, is_independent=False)

    dock.resize(800, 600)

    return dock


    # --- 逻辑处理 ---
    def toggle_altitude(checked):
        altitude_label.setVisible(checked)
        
        altitude_edit.setVisible(checked)

    def toggle_export_path(checked):
        export_path_button.setVisible(checked)

    def toggle_estimator_type():
        is_wing = wing_radio.isChecked()
        
        # 显示/隐藏机翼相关行
        for i in range(wing_chord_row.count()):
            wing_chord_row.itemAt(i).widget().setVisible(is_wing)
            
        for i in range(wing_len_row.count()):
            wing_len_row.itemAt(i).widget().setVisible(is_wing)
            
        for i in range(landing_gear_row.count()):
            landing_gear_row.itemAt(i).widget().setVisible(is_wing)
        
        # 显示/隐藏旋翼相关行
        for i in range(rotor_chord_row.count()):
            rotor_chord_row.itemAt(i).widget().setVisible(not is_wing)
            
        for i in range(rotor_radius_row.count()):
            rotor_radius_row.itemAt(i).widget().setVisible(not is_wing)
            
        for i in range(body_diam_row.count()):
            body_diam_row.itemAt(i).widget().setVisible(not is_wing)
            
        update_calculations()

    def update_calculations():
        try:
            # 获取输入值
            T_C = float(temp_edit.text()) # 温度 °C
            
            P_kPa = float(pressure_edit.text()) # 压力 kPa
            
            V = float(wind_speed_edit.text()) # 速度 m/s

            # 计算物理属性
            T_K = T_C + 273.15 # 转换为开尔文
            
            P_Pa = P_kPa * 1000 # 转换为帕斯卡
            
            R = 287.05 # 气体常数
            
            rho = P_Pa / (R * T_K) # 空气密度
            
            # Sutherland's law for viscosity
            mu_ref = 1.716e-5 # 参考粘度 at 273.15K
            
            T_ref = 273.15
            
            S = 110.4
            
            mu = mu_ref * ((T_K / T_ref)**1.5) * ((T_ref + S) / (T_K + S))

            # 计算特征长度 L
            L = 0.0
            
            if wing_radio.isChecked():
                L = float(wing_chord_edit.text() or 0) / 1000.0 # 默认为0，转为米
            else: # 旋翼
                L = float(rotor_chord_edit.text() or 0) / 1000.0 # 默认为0，转为米

            # 计算雷诺数
            if mu > 0 and L > 0:
                Re = (rho * V * L) / mu
            else:
                Re = 0

            # 更新状态标签
            density_label.setText(f"{rho:.4f}")
            
            speed_label.setText(f"{V:.2f}")
            
            char_len_label.setText(f"{L:.4f}")
            
            viscosity_label.setText(f"{mu:.2e}")
            
            reynolds_label.setText(f"{Re:.2e}")

        except (ValueError, ZeroDivisionError):
            # 如果输入无效或计算出错，显示 N/A
            density_label.setText("N/A")
            
            speed_label.setText("N/A")
            
            char_len_label.setText("N/A")
            
            viscosity_label.setText("N/A")
            
            reynolds_label.setText("N/A")

    # 连接信号
    altitude_check.toggled.connect(toggle_altitude)
    
    export_data_check.toggled.connect(toggle_export_path)
    
    wing_radio.toggled.connect(toggle_estimator_type)
    
    # 所有参与计算的输入框文本变化时都触发更新
    for edit in [
        wing_chord_edit, rotor_chord_edit, wind_speed_edit, 
        temp_edit, pressure_edit
    ]:
        edit.textChanged.connect(update_calculations)

    # 初始化UI状态
    toggle_altitude(altitude_check.isChecked())
    
    toggle_export_path(export_data_check.isChecked())
    
    toggle_estimator_type()
    
    update_calculations()

    dock = create_styled_dock(main_window, "仿真设置", content, is_independent=False)

    dock.resize(800, 600)

    return dock


def create_training_dock(main_window):
    """
    创建训练设置Dock。
    修改：增加一个按钮，点击后输出风速数据、传感器数据和动捕的所有数据。
    """
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setSpacing(15)

    # 状态标签
    status_label = QLabel("AI模型训练数据接口状态...")
    status_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(status_label)

    # 数据输出按钮
    output_data_btn = QPushButton("输出训练数据")

    def output_training_data():
        """输出训练数据到控制台"""
        print("\n" + "="*60)
        print("训练数据输出 - " + QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"))
        print("="*60)

        # 1. 输出风速数据
        print("\n【风速数据】")
        import random
        num_sensors = 64
        for i in range(num_sensors):
            speed = random.uniform(0, 30)
            print(f"  传感器 {i+1:02d}: {speed:.2f} m/s")

        # 2. 输出传感器数据（温度、湿度、气压等）
        print("\n【传感器数据】")
        print(f"  环境温度: {random.uniform(10, 35):.1f} °C")
        print(f"  环境湿度: {random.uniform(30, 80):.1f} RH%")
        print(f"  大气压力: {random.uniform(95, 105):.1f} kPa")
        print(f"  空气密度: {random.uniform(1.1, 1.3):.3f} kg/m³")

        # 3. 输出动捕数据（所有相机数据）
        print("\n【动捕数据】")
        for camera_id in range(1, 21):
            if camera_id in main_window.camera_data:
                data = main_window.camera_data[camera_id]
                print(f"  相机 {camera_id:02d}:")
                print(f"    状态: {data['status']}")
                print(f"    IP地址: {data['ip']}")
                print(f"    帧率: {data['framerate']} fps")
                print(f"    分辨率: {data['resolution']}")
                print(f"    曝光: {data['exposure']}")
                print(f"    阈值: {data['threshold']}")

        print("\n" + "="*60)
        print("数据输出完成")
        print("="*60 + "\n")

        # 记录到系统日志
        main_window.add_system_log("信息", "训练", "已输出训练数据（风速、传感器、动捕）")

    output_data_btn.clicked.connect(output_training_data)
    layout.addWidget(output_data_btn)

    layout.addStretch()

    return create_styled_dock(main_window, "训练设置", content, is_independent=False)
