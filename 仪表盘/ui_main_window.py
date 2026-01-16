# ui_main_window.py
from PySide6.QtWidgets import QMainWindow, QToolBar, QPushButton, QTableWidgetItem, QApplication
from PySide6.QtCore import QDateTime, QTimer, QPoint, Qt
import random

from ui_custom_widgets import BackgroundWidget, ThemeSwitch
from core_theme_manager import apply_theme, themes
from core_data_simulator import DataSimulator
import ui_docks as Docks
import debug
from ui_motion_capture import CameraSettingsDock

class GlobalDashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setObjectName("GlobalDashboardWindow")
        
        self.setWindowTitle("微小型无人机智能风场测试评估系统 - 全局监控仪表盘")
        
        self.resize(1200, 850)
        
        self.device_on = False
        
        self.comm_indicators = []
        
        self.DEFAULT_COMM_PROTOCOLS = {
            "主控制器": "TCP/IP", "电驱": "EtherCAT", "风速传感": "EtherCAT",
            "温度传感": "EtherCAT", "湿度传感": "EtherCAT", "动捕": "API",
            "俯仰伺服": "Modbus", "造雨": "Modbus", "喷雾": "Modbus",
            "训练": "API", "仿真": "API", "电力": "Modbus"
        }
        
        self.comm_protocols = self.DEFAULT_COMM_PROTOCOLS.copy()
        
        self.protocol_combos = {}
        
        self.comm_info_box = None
        
        self.themes = themes
        
        self.current_theme = "dark"
        
        self.docks = {}
        
        self.toolbar_buttons = {}
        
        self._create_mock_camera_data()
        
        self.setup_ui()
        
        self.data_simulator = DataSimulator(self)
        
        self.data_simulator.data_updated.connect(self.on_data_updated)
        
        self.data_simulator.comm_speed_updated.connect(self.on_comm_speed_updated)
        
        self.time_updater = QTimer(self)
        
        self.time_updater.timeout.connect(self.update_time_label)
        
        self.time_updater.start(1000)
        
        self.update_device_state()

        debug.log_debug("主窗口初始化完成。")

    def changeEvent(self, event):
        """处理窗口状态变化事件"""
        if event.type() == event.Type.WindowStateChange:
            old_state = event.oldState()
            new_state = self.windowState()

            # 即将最小化时，保存所有dock的完整状态
            if (new_state & Qt.WindowMinimized) and not (old_state & Qt.WindowMinimized):
                debug.log_debug("[changeEvent] 主窗口即将最小化，保存所有dock状态")
                self._save_docks_visibility()

            # 从最小化恢复时，延迟恢复所有dock的状态
            elif (old_state & Qt.WindowMinimized) and not (new_state & Qt.WindowMinimized):
                debug.log_debug("[changeEvent] 主窗口从最小化恢复，准备恢复所有dock状态")
                # 使用定时器延迟执行，确保窗口完全恢复后再操作dock
                QTimer.singleShot(50, self._restore_docks_visibility)

        super().changeEvent(event)

    def _save_docks_visibility(self):
        """主窗口最小化时，保存所有dock的完整状态（位置、大小、可见性）"""
        self._docks_state_before_minimize = {}
        for name, dock in self.docks.items():
            if dock:
                # 使用_visible_before_hide属性来判断dock原本是否可见
                # 因为最小化时Qt已经自动隐藏了所有子窗口，isVisible()会返回False
                was_visible = getattr(dock, '_visible_before_hide', False)
                self._docks_state_before_minimize[name] = {
                    'visible': was_visible,
                    'x': dock.x(),
                    'y': dock.y(),
                    'width': dock.width(),
                    'height': dock.height()
                }
                debug.log_debug(f"  保存dock状态: {name} -> visible={was_visible}, pos=({dock.x()}, {dock.y()}), size=({dock.width()}, {dock.height()})")

    def _restore_docks_visibility(self):
        """主窗口恢复时，恢复所有dock到最小化前的完整状态（位置、大小、可见性）"""
        debug.log_debug("[_restore_docks_visibility] 开始恢复dock状态")

        if not hasattr(self, '_docks_state_before_minimize'):
            debug.log_debug("  没有保存的状态，使用默认行为")
            self._restore_all_docks_visibility()
            return

        debug.log_debug(f"  已保存的dock数量: {len(self._docks_state_before_minimize)}")
        for name, state in self._docks_state_before_minimize.items():
            debug.log_debug(f"    {name}: visible={state['visible']}, pos=({state['x']}, {state['y']}), size=({state['width']}, {state['height']})")

        for name, dock in self.docks.items():
            if dock and name in self._docks_state_before_minimize:
                state = self._docks_state_before_minimize[name]
                # 先设置位置和大小
                dock.move(state['x'], state['y'])
                dock.resize(state['width'], state['height'])
                # 然后根据可见性显示或隐藏
                if state['visible']:
                    dock.show()
                    dock.raise_()
                    debug.log_debug(f"  ✓ 恢复dock: {name} -> pos=({state['x']}, {state['y']}), size=({state['width']}, {state['height']})")
                else:
                    dock.hide()
                    debug.log_debug(f"  ✗ 保持隐藏dock: {name}")
            else:
                if dock:
                    debug.log_debug(f"  ! dock '{name}' 没有保存的状态")

        # 强制刷新界面
        self.update()

    def _update_dock_geometry(self, dock):
        """当dock被拖动或调整大小时，更新保存的状态"""
        # 找到对应的dock名称
        dock_name = None
        for name, d in self.docks.items():
            if d is dock:
                dock_name = name
                break

        if dock_name:
            # 确保_docks_state_before_minimize存在
            if not hasattr(self, '_docks_state_before_minimize'):
                self._docks_state_before_minimize = {}

            # 使用_visible_before_hide来判断dock是否可见
            was_visible = getattr(dock, '_visible_before_hide', False)

            # 更新保存的状态中的位置和大小
            self._docks_state_before_minimize[dock_name] = {
                'visible': was_visible,
                'x': dock.x(),
                'y': dock.y(),
                'width': dock.width(),
                'height': dock.height()
            }
            debug.log_debug(f"  更新dock位置和大小: {dock_name} -> pos=({dock.x()}, {dock.y()}), size=({dock.width()}, {dock.height()})")

    def _restore_all_docks_visibility(self):
        """备用方法：重新显示所有之前标记为可见的dock"""
        for name, dock in self.docks.items():
            if dock and hasattr(dock, '_visible_before_hide') and dock._visible_before_hide:
                dock.show()
                dock.raise_()
                debug.log_debug(f"  重新显示dock: {name}")

    def _create_mock_camera_data(self):
        """为20个相机创建模拟数据"""
        self.camera_data = {}
        statuses = ["green"] * 15 + ["yellow"] * 3 + ["red"] * 2
        random.shuffle(statuses)
        
        for i in range(1, 21):
            self.camera_data[i] = {
                "id": i,
                "status": statuses[i-1],
                "ip": f"192.168.1.{100+i}",
                "subnet": "255.255.255.0",
                "gateway": "192.168.1.1",
                "dhcp": False,
                "firmware": "v1.2.3",
                "framerate": 210,
                "resolution": "2048x1536",
                "exposure": random.randint(40, 80),
                "threshold": random.randint(30, 70),
                "led_brightness": random.randint(70, 100),
                "marker_min_size": 5,
                "marker_max_size": 120,
                "sync_mode": "外部同步"
            }

    def setup_ui(self):
        self.canvas = BackgroundWidget("背景.png", 0.5)
        self.setCentralWidget(self.canvas)

        self.toolbar = QToolBar("主工具栏")
        self.addToolBar(self.toolbar)

        # --- 创建 Docks ---
        self.docks['系统'] = Docks.create_system_dock(self)
        self.docks['通讯'] = Docks.create_comm_dock(self)  # 现在包含电力模块
        # 电力模块（电流、电压、功率）已整合到通讯dock中，不再创建独立dock
        self.docks['环境'] = Docks.create_env_dock(self)
        self.docks['日志'] = Docks.create_log_dock(self)
        # 俯仰、造雨、示踪整合为一个组合dock
        self.docks['俯仰·造雨·示踪'] = Docks.create_combined_pitch_rain_trace_dock(self)
        self.docks['风机'] = Docks.create_fan_dock(self)

        self.camera_status_lights = []
        self.docks['动捕'] = Docks.create_motion_capture_dock(self)

        self.docks['标定'] = Docks.create_calibration_dock(self)
        self.docks['仿真'] = Docks.create_simulation_dock(self)
        self.docks['训练'] = Docks.create_training_dock(self)
        self.docks['设置'] = Docks.create_settings_dock(self)

        self.docks['TCP/IP设置'] = Docks.create_tcp_settings_dock(self)
        self.docks['Modbus RTU设置'] = Docks.create_modbus_settings_dock(self)
        self.docks['EtherCAT设置'] = Docks.create_ethercat_settings_dock(self)
        self.docks['API设置'] = Docks.create_api_settings_dock(self)

        # --- 创建单例和隐藏的 Docks ---
        # Parent is None to be a true top-level window, not constrained by the main window
        self.camera_settings_dock = CameraSettingsDock(self.canvas)
        self.docks['相机详细设置'] = self.camera_settings_dock
        self.camera_settings_dock.hide()
        self.docks['相机详细设置'] = self.camera_settings_dock
        self.camera_settings_dock.hide()

        # --- 创建动捕视场Dock ---
        self.docks['动捕视场'] = Docks.create_motion_capture_view_dock(self)
        self.docks['动捕视场'].hide()

        # Position default Docks - 设置默认dock的位置
        self.docks['系统'].move(20, 10); self.docks['系统'].resize(250, 135)
        self.docks['通讯'].move(280, 10); self.docks['通讯'].resize(910, 310)
        self.docks['环境'].move(20, 330); self.docks['环境'].resize(350, 300)
        self.docks['日志'].move(390, 330); self.docks['日志'].resize(800, 300)

        # Hide all non-default docks initially
        default_docks = ['系统', '通讯', '环境', '日志']
        for name, dock in self.docks.items():
            if name not in default_docks:
                dock.hide()
            else:
                # 确保默认dock的可见性标记被设置
                dock._visible_before_hide = True

        # Setup Toolbar
        button_order = ["系统", "通讯", "环境", "日志",
                        "俯仰·造雨·示踪", "风机", "动捕", "标定", "仿真", "训练"]

        dynamic_docks = ['俯仰·造雨·示踪', '风机', '动捕', '标定', '仿真', '训练', '设置']

        for name in button_order:
            button = QPushButton(name)
            button.setCheckable(True)
            # 对于默认dock，初始应该是checked状态
            initial_checked = name in default_docks
            button.setChecked(initial_checked)

            if name in dynamic_docks:
                button.toggled.connect(lambda checked, n=name: self.toggle_dynamic_dock(n, checked))
            else:
                button.toggled.connect(self.docks[name].setVisible)

            self.docks[name].visibilityChanged.connect(button.setChecked)

            # 根据按钮文字长度设置按钮大小
            if name == "俯仰·造雨·示踪":
                button.setFixedSize(115, 30)  # 为长文字按钮设置更大的宽度
            else:
                button.setFixedSize(45, 30)

            self.toolbar_buttons[name] = button
            self.toolbar.addWidget(button)
        
        self.toolbar.addSeparator()

        settings_button = QPushButton("设置")
        settings_button.setCheckable(True)
        settings_button.setChecked(self.docks['设置'].isVisible())
        settings_button.toggled.connect(lambda checked: self.toggle_dynamic_dock('设置', checked))
        self.docks['设置'].visibilityChanged.connect(settings_button.setChecked)
        settings_button.setFixedSize(45, 30)
        self.toolbar.addWidget(settings_button)
        
        self.theme_switch = ThemeSwitch()
        self.theme_switch.set_on(self.current_theme == "dark")
        self.theme_switch.toggled.connect(self._on_theme_switched)
        self.toolbar.addWidget(self.theme_switch)
        
        self.estop_button = QPushButton("急停")
        self.switch_button = QPushButton()
        
        self.estop_button.setFixedSize(70, 30)
        self.switch_button.setFixedSize(70, 30)
        
        self.estop_button.clicked.connect(self.handle_estop)
        self.switch_button.clicked.connect(self.handle_switch_toggle)

        self.toolbar.addWidget(self.estop_button)
        self.toolbar.addWidget(self.switch_button)
        
        self.apply_theme(self.current_theme)
        
        self.update_camera_status_lights()

    # --- FIX: 添加缺失的方法 ---
    def show_motion_capture_view(self):
        """显示动捕实时视场Dock"""
        self.docks['动捕视场'].show()
        self.docks['动捕视场'].raise_()
        self.docks['动捕视场'].activateWindow()

    def update_camera_status_lights(self):
        """
        根据设备状态更新所有相机状态灯的颜色
        """
        if self.device_on:
            # 需求2: 当设备状态处于开机时,默认全部为绿色
            for light_widget in self.camera_status_lights:
                light_widget.setStatus("green")
        else:
            for light_widget in self.camera_status_lights:
                light_widget.setStatus("red")

    def show_camera_settings(self, camera_id: int):
        """
        当相机状态灯被点击时调用，显示对应相机的设置面板
        """
        debug.log_debug(f"请求显示相机ID {camera_id} 的设置面板。")
        
        if camera_id in self.camera_data:
            data = self.camera_data[camera_id]
            
            self.camera_settings_dock.load_camera_data(data)
            
            self.camera_settings_dock.show()
            
            # 需求5: 单个动捕相机dock启动时要位于最前端
            self.camera_settings_dock.raise_()
            
            self.camera_settings_dock.activateWindow()

    def toggle_dynamic_dock(self, dock_name, show):
        """
        Toggles the visibility of a dock with dynamic positioning.
        """
        debug.log_debug(f"切换Dock '{dock_name}' 可见性为: {show}")
        
        if show:
            self.show_dynamic_dock(dock_name)
        else:
            if dock_name in self.docks:
                self.docks[dock_name].hide()

    def show_dynamic_dock(self, dock_name):
        """Shows a dock at the next available cascaded position."""
        if dock_name not in self.docks:
            return

        target_dock = self.docks[dock_name]

        # 首先检查是否有保存的位置（用户之前拖动过的位置）
        if hasattr(self, '_docks_state_before_minimize') and dock_name in self._docks_state_before_minimize:
            state = self._docks_state_before_minimize[dock_name]
            # 使用保存的位置和大小
            target_dock.move(state['x'], state['y'])
            target_dock.resize(state['width'], state['height'])
            target_dock.show()
            target_dock.raise_()
            debug.log_debug(f"  恢复dock到保存的位置: {dock_name} -> pos=({state['x']}, {state['y']})")
            return

        # 如果没有保存的位置，使用默认的级联定位
        base_pos = QPoint(400, 300)
        offset = QPoint(20, 20)

        i = 0
        while True:
            target_pos = base_pos + offset * i
            is_occupied = False
            for name, dock in self.docks.items():
                if dock.isVisible() and dock is not target_dock and dock.pos() == target_pos:
                    is_occupied = True
                    break

            if not is_occupied:
                target_dock.move(target_pos)
                target_dock.show()
                target_dock.raise_()
                break

            i += 1
            if i > 50:
                target_dock.move(base_pos)
                target_dock.show()
                target_dock.raise_()
                break

    def _on_theme_switched(self, is_dark):
        """
        处理主题切换事件
        """
        self.current_theme = "dark" if is_dark else "light"
        
        debug.log_debug(f"主题切换为: {self.current_theme}")
        
        self.apply_theme(self.current_theme)

    def apply_theme(self, theme_name):
        apply_theme(self, theme_name)

    def on_data_updated(self, current, voltage, power):
        if hasattr(self, 'chart_current_widget') and self.chart_current_widget:
            self.chart_current_widget.update_data(current)
        if hasattr(self, 'chart_voltage_widget') and self.chart_voltage_widget:
            self.chart_voltage_widget.update_data(voltage)
        if hasattr(self, 'chart_power_widget') and self.chart_power_widget:
            self.chart_power_widget.update_data(power)

    def on_comm_speed_updated(self, module_name, speed_str):
        for indicator in self.comm_indicators:
            indicator.set_speed(speed_str)
            log_message = f"{indicator.name} 通讯响应时间: {speed_str}ms"
            self.add_system_log("信息", "通讯", log_message)
            
    def update_time_label(self):
        if hasattr(self, 'time_label'):
            current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd \ndddd HH:mm:ss")
            self.time_label.setText(current_time)

    def handle_estop(self):
        """
        处理急停按钮点击事件
        """
        if self.device_on:
            self.device_on = False
            
            debug.log_debug("急停按钮被触发，设备关闭。")
            
            self.add_active_alarm("警告", "系统", "紧急停机")
            
            self.add_system_log("警告", "系统", "触发紧急停机按钮, 设备已关闭")
            
            for indicator in self.comm_indicators:
                log_msg = f"{indicator.name}已断开 0/{indicator.total}"
                
                self.add_system_log("信息", "通讯", log_msg)
                
            self.update_device_state()
    def handle_switch_toggle(self):
        """
        处理开/关机按钮点击事件
        """
        self.device_on = not self.device_on
        
        debug.log_debug(f"设备开关切换为: {'开机' if self.device_on else '关机'}")
        
        if self.device_on:
            self.add_active_alarm("信息", "系统", "设备开机")
            
            self.add_system_log("信息", "系统", "执行开机操作")
            
            for indicator in self.comm_indicators:
                log_msg = f"{indicator.name}已连接 {indicator.total}/{indicator.total}"
                
                self.add_system_log("信息", "通讯", log_msg)
        else:
            self.add_active_alarm("信息", "系统", "设备关机")
            
            self.add_system_log("信息", "系统", "执行关机操作")
            
            for indicator in self.comm_indicators:
                log_msg = f"{indicator.name}已断开 0/{indicator.total}"
                
                self.add_system_log("信息", "通讯", log_msg)
        
        self.update_device_state()

    def update_device_state(self):
        self.health_indicator.set_device_status(self.device_on)
        for indicator in self.comm_indicators:
            indicator.update_status(self.device_on)
        
        self.update_camera_status_lights()
        
        theme = self.themes[self.current_theme]
        if not self.device_on:
            self.estop_button.setStyleSheet("background-color: #ffc800; color: black; font-weight: bold; border-radius: 5px;")
            self.switch_button.setText("开机")
            self.switch_button.setStyleSheet(f"background-color: {theme['button_bg']}; color: {theme['button_text']}; border-radius: 5px;")
        else:
            self.estop_button.setStyleSheet("background-color: #ff3b30; color: white; font-weight: bold; border-radius: 5px;")
            self.switch_button.setText("关机")
            self.switch_button.setStyleSheet("background-color: #00ff7f; color: black; font-weight: bold; border-radius: 5px;")

        if hasattr(self, 'data_simulator'):
            self.data_simulator.set_device_status(self.device_on)

    def add_system_log(self, level, source, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        row_position = self.table_system_logs.rowCount()
        self.table_system_logs.insertRow(row_position)
        self.table_system_logs.setItem(row_position, 0, QTableWidgetItem(timestamp))
        self.table_system_logs.setItem(row_position, 1, QTableWidgetItem(level))
        self.table_system_logs.setItem(row_position, 2, QTableWidgetItem(source))
        self.table_system_logs.setItem(row_position, 3, QTableWidgetItem(message))
        self.table_system_logs.scrollToBottom()

    def add_active_alarm(self, level, source, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        row_position = self.table_active_alarms.rowCount()
        self.table_active_alarms.insertRow(row_position)
        self.table_active_alarms.setItem(row_position, 0, QTableWidgetItem(timestamp))
        self.table_active_alarms.setItem(row_position, 1, QTableWidgetItem(level))
        self.table_active_alarms.setItem(row_position, 2, QTableWidgetItem(source))
        self.table_active_alarms.setItem(row_position, 3, QTableWidgetItem(message))
        self.table_active_alarms.setItem(row_position, 4, QTableWidgetItem(""))
        self.table_active_alarms.scrollToBottom()

    def show_settings_dock(self):
        for module_name, combo in self.protocol_combos.items():
            combo.setCurrentText(self.comm_protocols.get(module_name, ""))
        self.docks['设置'].show()
        self.docks['设置'].raise_()

    def save_settings(self):
        """
        保存设置
        """
        if not self.comm_info_box:
            return
            
        self.comm_info_box.clear()
        
        for module_name, combo in self.protocol_combos.items():
            self.comm_protocols[module_name] = combo.currentText()
            
        log_msg = "通讯协议设置已保存。"
        
        debug.log_debug("设置已保存。")
        
        self.add_system_log("信息", "设置", log_msg)
        
        self.comm_info_box.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] {log_msg}")
        
        print("Settings saved:", self.comm_protocols)
    def reset_settings(self):
        """
        重置设置
        """
        if not self.comm_info_box:
            return
            
        self.comm_info_box.clear()
        
        for module_name, combo in self.protocol_combos.items():
            default_protocol = self.DEFAULT_COMM_PROTOCOLS.get(module_name, "")
            
            combo.setCurrentText(default_protocol)
            
        log_msg = "通讯协议设置已重置为默认值。"
        
        debug.log_debug("设置已重置为默认值。")
        
        self.add_system_log("信息", "设置", log_msg)
        
        self.comm_info_box.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] {log_msg}")
    def cancel_settings(self):
        """
        取消设置并关闭窗口
        """
        debug.log_debug("设置窗口: 点击 '取消'。")
        
        self.docks['设置'].hide()
    def apply_settings(self):
        """
        应用并保存设置
        """
        debug.log_debug("设置窗口: 点击 '确定' (应用设置)。")
        
        self.save_settings()
        
        self.docks['设置'].hide()
    def test_settings(self):
        """
        测试设置
        """
        if not self.comm_info_box:
            return
            
        debug.log_debug("设置窗口: 开始测试通讯。")
        
        self.comm_info_box.clear()
        
        self.comm_info_box.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] 开始测试当前通讯协议配置...")
        
        for module_name, combo in self.protocol_combos.items():
            protocol = combo.currentText()
            
            self.comm_info_box.append(f"  - 正在测试 {module_name} (协议: {protocol})...")
            
            QApplication.processEvents()
            
            timer = QTimer()
            
            timer.singleShot(100, lambda: None)
            
            success = random.choice([True, True, True, False])
            
            if success:
                self.comm_info_box.append(f"    -> {module_name} 连接成功!")
            else:
                self.comm_info_box.append(f"    -> <font color='red'>错误: {module_name} 连接失败!</font>")
                
        self.comm_info_box.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] 通讯测试完成。")

    def handle_specific_module_setting(self, module_name):
        if not self.comm_info_box: return
        
        protocol = self.protocol_combos[module_name].currentText()
        
        dock_map = {
            "TCP/IP": "TCP/IP设置",
            "Modbus": "Modbus RTU设置",
            "EtherCAT": "EtherCAT设置",
            "API": "API设置"
        }

        dock_to_show_name = dock_map.get(protocol)
        
        if dock_to_show_name and dock_to_show_name in self.docks:
            self.show_dynamic_dock(dock_to_show_name)
            self.comm_info_box.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] 已打开 '{module_name}' 的 '{protocol}' 设置面板。")
        else:
            self.comm_info_box.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] 错误: 未找到协议 '{protocol}' 的设置面板。")
    def toggle_debug_mode(self, checked: bool):
        """
        用于切换全局调试模式的槽函数
        """
        debug.DEBUG_ENABLED = checked
        
        # 立即打印一条日志来确认状态变更
        debug.log_debug(f"调试模式已 {'启用' if checked else '禁用'}")
