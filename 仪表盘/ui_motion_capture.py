# ui_motion_capture.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
                               QPushButton, QLabel, QComboBox, QSlider, QLineEdit, 
                               QSpinBox, QFormLayout, QListWidget, QListWidgetItem,
                               QFrame, QCheckBox)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QFont

from ui_custom_widgets import DraggableFrame
import debug
class _LightCircleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22) # 稍微增大尺寸以容纳立体效果
        self._color = QColor("#5e626a")

    def setColor(self, color: QColor):
        if self._color != color:
            self._color = color
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 使用径向渐变创建立体感
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = self.width() // 2
        
        gradient = QRadialGradient(center, radius)
        
        # 基础色
        base_color = self._color
        # 高光色 (更亮)
        highlight_color = base_color.lighter(150)
        # 阴影色 (更暗)
        shadow_color = base_color.darker(150)

        # 渐变分布
        gradient.setColorAt(0.0, highlight_color) # 中心高光
        gradient.setColorAt(0.8, base_color)
        gradient.setColorAt(1.0, shadow_color)   # 边缘阴影

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect())

class CameraStatusLight(QWidget):
    """单个相机状态指示灯，可点击"""
    clicked = Signal(int)

    def __init__(self, camera_id, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2) # 减小间距

        self.light_widget = _LightCircleWidget()
        
        self.id_label = QLabel(f"Cam {self.camera_id:02d}") # 缩短文字
        self.id_label.setAlignment(Qt.AlignCenter)
        # --- MODIFIED: 减小字体 ---
        font = self.id_label.font()
        font.setPointSize(8)
        self.id_label.setFont(font)

        layout.addWidget(self.light_widget, 0, Qt.AlignCenter)
        layout.addWidget(self.id_label)
        
        self.setCursor(Qt.PointingHandCursor)

    def setStatus(self, status: str):
        """设置状态: 'green', 'yellow', 'red'"""
        colors = {
            "green": QColor("#00ff7f"),
            "yellow": QColor("#ffc800"),
            "red": QColor("#ff3b30")
        }
        color = colors.get(status, QColor("#5e626a"))
        self.light_widget.setColor(color)

    def mousePressEvent(self, event):
        self.clicked.emit(self.camera_id)
        super().mousePressEvent(event)

# ui_motion_capture.py

class CameraSettingsDock(DraggableFrame):
    """
    可重复使用的单个相机详细设置面板
    """
    def __init__(self, parent=None):
        # --- MODIFIED: 重命名Dock，并将父窗口设为 canvas ---
        # 需求3: 重新命名为 "单个动捕相机设置"
        super().__init__("单个动捕相机设置", parent, is_independent_window=True)
        
        content = QWidget()
        
        main_layout = QVBoxLayout(content)
        
        main_layout.setSpacing(10)

        # ... (所有Group Box的创建代码保持不变) ...
        # 1. 概览 Frame
        overview_group = QGroupBox("概览")
        overview_layout = QFormLayout(overview_group)
        self.overview_labels = {
            "id": QLabel(), "ip": QLabel(), "firmware": QLabel(),
            "fps_res": QLabel(), "coord_acc": QLabel(), "quat_acc": QLabel(),
            "ang_vel_acc": QLabel()
        }
        overview_layout.addRow("相机 ID:", self.overview_labels["id"])
        overview_layout.addRow("IP 地址:", self.overview_labels["ip"])
        overview_layout.addRow("固件版本:", self.overview_labels["firmware"])
        overview_layout.addRow("帧率/分辨率:", self.overview_labels["fps_res"])
        overview_layout.addRow("坐标精度:", self.overview_labels["coord_acc"])
        overview_layout.addRow("四元数精度:", self.overview_labels["quat_acc"])
        overview_layout.addRow("角速度精度:", self.overview_labels["ang_vel_acc"])
        
        # 2. 基本参数设置 Frame
        params_group = QGroupBox("基本参数设置")
        params_layout = QFormLayout(params_group)
        
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_spinbox = QSpinBox()
        exposure_widget = self._create_slider_spinbox_widget(self.exposure_slider, self.exposure_spinbox)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_spinbox = QSpinBox()
        threshold_widget = self._create_slider_spinbox_widget(self.threshold_slider, self.threshold_spinbox)
        
        self.framerate_combo = QComboBox()
        self.framerate_combo.addItems(["60Hz", "120Hz", "210Hz"])
        
        self.led_slider = QSlider(Qt.Horizontal)
        self.led_spinbox = QSpinBox()
        self.led_spinbox.setSuffix(" %")
        led_widget = self._create_slider_spinbox_widget(self.led_slider, self.led_spinbox)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["2048x1536", "1280x1024", "640x480"])

        params_layout.addRow("曝光度:", exposure_widget)
        params_layout.addRow("阈值:", threshold_widget)
        params_layout.addRow("帧率:", self.framerate_combo)
        params_layout.addRow("LED 亮度:", led_widget)
        params_layout.addRow("分辨率:", self.resolution_combo)

        # 3. 图像处理与识别设置 Frame
        img_proc_group = QGroupBox("图像处理与识别设置")
        img_proc_layout = QVBoxLayout(img_proc_group)
        
        marker_size_layout = QFormLayout()
        self.marker_min_spinbox = QSpinBox()
        self.marker_max_spinbox = QSpinBox()
        marker_size_layout.addRow("最小尺寸 (Min):", self.marker_min_spinbox)
        marker_size_layout.addRow("最大尺寸 (Max):", self.marker_max_spinbox)
        
        mask_group = QGroupBox("遮罩工具")
        mask_layout = QVBoxLayout(mask_group)
        mask_btn_layout = QHBoxLayout()
        mask_btn_layout.addWidget(QPushButton("添加遮罩"))
        mask_btn_layout.addStretch()
        self.mask_list = QListWidget()
        self.mask_list.setAlternatingRowColors(True)
        self.mask_list.addItems(["遮罩区域 1", "地面反光区域"])
        mask_layout.addLayout(mask_btn_layout)
        mask_layout.addWidget(self.mask_list)

        img_proc_layout.addLayout(marker_size_layout)
        img_proc_layout.addWidget(mask_group)

        # 4. 系统与网络配置 Frame
        sys_net_group = QGroupBox("系统与网络配置")
        sys_net_layout = QFormLayout(sys_net_group)
        
        self.cam_id_edit = QLineEdit()
        self.sync_combo = QComboBox()
        self.sync_combo.addItems(["主相机", "从相机", "外部同步"])
        
        self.dhcp_check = QCheckBox("使用 DHCP")
        self.ip_edit = QLineEdit()
        self.subnet_edit = QLineEdit()
        self.gateway_edit = QLineEdit()
        
        sys_net_layout.addRow("相机ID/命名:", self.cam_id_edit)
        sys_net_layout.addRow("同步设置:", self.sync_combo)
        sys_net_layout.addRow(self.dhcp_check)
        sys_net_layout.addRow("IP 地址:", self.ip_edit)
        sys_net_layout.addRow("子网掩码:", self.subnet_edit)
        sys_net_layout.addRow("网关:", self.gateway_edit)

        main_layout.addWidget(overview_group)
        
        main_layout.addWidget(params_group)
        
        main_layout.addWidget(img_proc_group)
        
        main_layout.addWidget(sys_net_group)
        
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        self.reset_button = QPushButton("重置")
        
        self.ok_button = QPushButton("确定")
        
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.reset_button)
        
        button_layout.addWidget(self.ok_button)
        
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)

        # 需求4: "确定"和"取消"按钮都关闭此dock
        self.ok_button.clicked.connect(self.hide)
        
        self.cancel_button.clicked.connect(self.hide)
        
        # 为按钮点击添加调试日志
        self.ok_button.clicked.connect(
            lambda: debug.log_debug("单个动捕相机设置: 点击 '确定' 按钮。")
        )
        
        self.cancel_button.clicked.connect(
            lambda: debug.log_debug("单个动捕相机设置: 点击 '取消' 按钮。")
        )
        
        self.reset_button.clicked.connect(
            lambda: debug.log_debug("单个动捕相机设置: 点击 '重置' 按钮。")
        )
        
        self.setContentWidget(content)
        
        self.resize(400, 750)

    def _create_slider_spinbox_widget(self, slider, spinbox):
        widget = QWidget()
        
        layout = QHBoxLayout(widget)
        
        layout.setContentsMargins(0,0,0,0)
        
        layout.addWidget(slider)
        
        layout.addWidget(spinbox)
        
        slider.valueChanged.connect(spinbox.setValue)
        
        spinbox.valueChanged.connect(slider.setValue)
        
        return widget

    def load_camera_data(self, data: dict):
        cam_id = data.get('id', 0)
        
        debug.log_debug(f"加载相机ID {cam_id} 的数据到设置面板。")
        
        # 需求3: 将相机ID改为Camera+数字
        self.title_label.setText(f"Camera {cam_id:02d} 设置")
        
        self.overview_labels["id"].setText(f"{cam_id:02d}")
        
        self.overview_labels["ip"].setText(data.get("ip", "N/A"))
        
        self.overview_labels["firmware"].setText(data.get("firmware", "N/A"))
        
        self.overview_labels["fps_res"].setText(f"{data.get('framerate')}Hz, {data.get('resolution')}")
        
        self.overview_labels["coord_acc"].setText("±0.1mm")
        
        self.overview_labels["quat_acc"].setText("±0.01°")
        
        self.overview_labels["ang_vel_acc"].setText("±0.1°/s")
        
        self.exposure_slider.setValue(data.get("exposure", 50))
        
        self.threshold_slider.setValue(data.get("threshold", 50))
        
        self.framerate_combo.setCurrentText(f"{data.get('framerate')}Hz")
        
        self.led_slider.setValue(data.get("led_brightness", 80))
        
        self.resolution_combo.setCurrentText(data.get("resolution"))
        
        self.marker_min_spinbox.setValue(data.get("marker_min_size", 5))
        
        self.marker_max_spinbox.setValue(data.get("marker_max_size", 100))
        
        self.cam_id_edit.setText(f"Camera {cam_id:02d}")
        
        self.sync_combo.setCurrentText(data.get("sync_mode", "外部同步"))
        
        is_dhcp = data.get("dhcp", False)
        
        self.dhcp_check.setChecked(is_dhcp)
        
        self.ip_edit.setText(data.get("ip", ""))
        
        self.subnet_edit.setText(data.get("subnet", ""))
        
        self.gateway_edit.setText(data.get("gateway", ""))
        
        self.ip_edit.setEnabled(not is_dhcp)
        
        self.subnet_edit.setEnabled(not is_dhcp)
        
        self.gateway_edit.setEnabled(not is_dhcp)

    def showEvent(self, event):
        """
        重写 showEvent 以添加调试日志
        """
        super().showEvent(event)
        
        debug.log_debug("单个动捕相机设置面板: 显示。")

    def hideEvent(self, event):
        """
        重写 hideEvent 以添加调试日志
        """
        super().hideEvent(event)
        
        debug.log_debug("单个动捕相机设置面板: 关闭。")
