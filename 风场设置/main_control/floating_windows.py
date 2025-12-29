# floating_windows.py
# 各种浮动小窗口的实现

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QCheckBox, QSlider,
    QListWidget, QTextEdit, QComboBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QDoubleValidator, QIntValidator
from . import config

class SelectionInfoWindow(QDialog):
    """选择信息浮动窗口"""
    # 信号定义
    apply_speed_signal = Signal(float)
    invert_selection_signal = Signal()
    reset_selection_signal = Signal()
    
# floating_windows.py -> SelectionInfoWindow
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. 修改窗口标题
        self.setWindowTitle("点选模式") 
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setGeometry(600, 300, 250, 150)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.selection_count_label = QLabel("0")
        self.avg_speed_label = QLabel("N/A")
        self.speed_input = QLineEdit("0.00")
        validator = QDoubleValidator(0.0, 100.0, 2)
        self.speed_input.setValidator(validator)

        # 【新增】羽化控件
        self.feather_checkbox = QCheckBox()
        self.feather_spinbox = QSpinBox()
        self.feather_spinbox.setRange(1, 10)
        self.feather_spinbox.setValue(3)
        self.feather_spinbox.setEnabled(False) # 默认禁用
        
        form_layout.addRow("选中数量:", self.selection_count_label)
        form_layout.addRow("平均转速:", self.avg_speed_label)
        form_layout.addRow("设置转速 (%):", self.speed_input)
        form_layout.addRow("羽化:", self.feather_checkbox)
        form_layout.addRow("羽化值:", self.feather_spinbox)
        
        button_layout = QHBoxLayout()
        self.select_all_button = QPushButton("全选")
        self.invert_selection_button = QPushButton("反选")
        # 2. 修改按钮文本
        self.reset_button = QPushButton("全部清零") 
        
        self.select_all_button.setFocusPolicy(Qt.NoFocus)
        self.invert_selection_button.setFocusPolicy(Qt.NoFocus)
        self.reset_button.setFocusPolicy(Qt.NoFocus)
        
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.invert_selection_button)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        # 3. 连接信号
        self.speed_input.returnPressed.connect(self.apply_speed_to_selection)
        self.invert_selection_button.clicked.connect(self.invert_selection_signal.emit)
        # 注意：reset_button 的信号将在主窗口中连接到一个新的槽函数
        # 【新增】连接checkbox和spinbox
        self.feather_checkbox.toggled.connect(self.feather_spinbox.setEnabled)
    # 【新增】两个获取羽化设置的方法
    def is_feathering_enabled(self):
        return self.feather_checkbox.isChecked()
    def get_feather_value(self):
        return self.feather_spinbox.value()        
# floating_windows.py -> SelectionInfoWindow & CircleToolWindow
    def update_selection_info(self, selected_cells):
        count = len(selected_cells)
        self.selection_count_label.setText(str(count))
        if count > 0:
            total_speed = sum(cell.value for cell in selected_cells)
            avg_speed = total_speed / count
            self.avg_speed_label.setText(f"{avg_speed:.2f} %")
            # 【核心修复】使用单次定时器延迟设置焦点
            QTimer.singleShot(50, self.speed_input.setFocus)
            QTimer.singleShot(50, self.speed_input.selectAll)
        else:
            self.avg_speed_label.setText("N/A")
            self.speed_input.clearFocus()

            
    def apply_speed_to_selection(self):
        """应用转速到选中的风扇"""
        try:
            speed = float(self.speed_input.text())
            if 0 <= speed <= 100:
                self.apply_speed_signal.emit(speed)
        except ValueError:
            pass
    
    def reset_selection_with_zero_speed(self):
        """重置选择并设置转速为0%"""
        self.speed_input.setText("0.00")
        self.reset_selection_signal.emit()

# floating_windows.py -> BrushToolWindow

class BrushToolWindow(QDialog):
    """笔刷工具浮动窗口"""
    # 添加信号
    clear_all_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 【修改】不再需要独立的窗口标题，因为它将被嵌入
        # self.setWindowTitle("笔刷工具")
        # self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        # self.setGeometry(600, 300, 250, 200)
        
        # 【修改】使用 QVBoxLayout 作为主布局
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.brush_size_spinbox = QSpinBox()
        self.brush_size_spinbox.setRange(1, config.GRID_DIM)
        self.brush_size_spinbox.setValue(5)
        
        self.brush_value_input = QLineEdit("100.00")
        validator = QDoubleValidator(0.0, 100.0, 2)
        self.brush_value_input.setValidator(validator)

        # 【新增】羽化控件
        self.feather_checkbox = QCheckBox()
        self.feather_spinbox = QSpinBox()
        self.feather_spinbox.setRange(1, 10)
        self.feather_spinbox.setValue(3)
        self.feather_spinbox.setEnabled(False)
        
        form_layout.addRow("笔刷直径 (个):", self.brush_size_spinbox)
        form_layout.addRow("笔刷转速 (%):", self.brush_value_input)
        form_layout.addRow("羽化:", self.feather_checkbox)
        form_layout.addRow("羽化值:", self.feather_spinbox)
        
        # 添加全部清零按钮
        self.clear_all_button = QPushButton("全部清零")
        self.clear_all_button.setFocusPolicy(Qt.NoFocus)
        
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.clear_all_button)
        
        # 【新增】连接checkbox和spinbox
        self.feather_checkbox.toggled.connect(self.feather_spinbox.setEnabled)
        # 连接全部清零按钮
        self.clear_all_button.clicked.connect(self.clear_all_signal.emit)
    # 【新增】两个获取羽化设置的方法
    def is_feathering_enabled(self):
        return self.feather_checkbox.isChecked()
    def get_feather_value(self):
        return self.feather_spinbox.value()
        
    def closeEvent(self, event):
        """窗口关闭时恢复到选择模式"""
        # 这个方法现在不再需要，因为窗口不会被独立关闭
        pass
        
    def is_brush_active(self):
        return True
        
    def get_brush_size(self):
        return self.brush_size_spinbox.value()
        
    def get_brush_value(self):
        try:
            return round(float(self.brush_value_input.text()), 2)
        except ValueError:
            return 100.0


class FanSettingsWindow(QDialog):
    """风机设置浮动窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("风机设置")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(250, 120)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.max_rpm_input = QLineEdit("17000")
        self.max_rpm_input.setValidator(QIntValidator(0, 100000))
        form_layout.addRow("最大转速 (RPM):", self.max_rpm_input)
        
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
    def get_max_rpm(self):
        try:
            return int(self.max_rpm_input.text())
        except ValueError:
            return 17000
            
    def set_max_rpm(self, rpm):
        self.max_rpm_input.setText(str(rpm))

class TimeSettingsWindow(QDialog):
    """时间设置浮动窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("时间设置")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setGeometry(600, 300, 250, 150)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.max_time_input = QLineEdit("10.0")
        self.max_time_input.setValidator(QDoubleValidator(0.1, 1000.0, 1))
        
        self.time_resolution_input = QLineEdit("0.1")
        self.time_resolution_input.setValidator(QDoubleValidator(0.01, 1.0, 2))
        
        form_layout.addRow("最大时间 (s):", self.max_time_input)
        form_layout.addRow("时间分辨率 (s):", self.time_resolution_input)
        
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
    def get_max_time(self):
        try:
            return float(self.max_time_input.text())
        except ValueError:
            return 10.0
            
    def get_time_resolution(self):
        try:
            return float(self.time_resolution_input.text())
        except ValueError:
            return 0.1
            
    def set_max_time(self, time):
        self.max_time_input.setText(str(time))
        
    def set_time_resolution(self, resolution):
        self.time_resolution_input.setText(str(resolution))

class TemplateLibraryWindow(QDialog):
    """模版库浮动窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("项目与模版库")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(300, 400)
        
        layout = QVBoxLayout(self)
        
        self.template_list = QListWidget()
        self.template_list.setSelectionMode(QAbstractItemView.SingleSelection)
        # 添加示例模板
        self.template_list.addItems(["中心高斯喷流_v1", "左右扫描风_初始", "城市峡谷风"])
        
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("加载")
        self.save_button = QPushButton("保存")
        self.delete_button = QPushButton("删除")
        
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        
        layout.addWidget(self.template_list)
        layout.addLayout(button_layout)

# floating_windows.py -> CircleToolWindow

class CircleToolWindow(QDialog):
    """圆形工具窗口"""
    apply_speed_signal = Signal(float)
    clear_all_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("圆形工具")
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.selection_count_label = QLabel("0")
        self.avg_speed_label = QLabel("N/A")
        self.speed_input = QLineEdit("0.00")
        validator = QDoubleValidator(0.0, 100.0, 2)
        self.speed_input.setValidator(validator)
        
        self.feather_checkbox = QCheckBox()
        self.feather_spinbox = QSpinBox()
        self.feather_spinbox.setRange(1, 10)
        self.feather_spinbox.setValue(3)
        self.feather_spinbox.setEnabled(False)
        
        form_layout.addRow("选中数量:", self.selection_count_label)
        form_layout.addRow("平均转速:", self.avg_speed_label)
        form_layout.addRow("设置转速 (%):", self.speed_input)
        form_layout.addRow("羽化:", self.feather_checkbox)
        form_layout.addRow("羽化值:", self.feather_spinbox)
        
        # 添加全部清零按钮
        self.clear_all_button = QPushButton("全部清零")
        self.clear_all_button.setFocusPolicy(Qt.NoFocus)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.clear_all_button)
        
        self.speed_input.returnPressed.connect(self.on_apply_speed)
        self.feather_checkbox.toggled.connect(self.feather_spinbox.setEnabled)
        self.clear_all_button.clicked.connect(self.clear_all_signal.emit)

    def on_apply_speed(self):
        try:
            speed = float(self.speed_input.text())
            self.apply_speed_signal.emit(speed)
        except ValueError:
            pass

    def update_selection_info(self, selected_cells):
        count = len(selected_cells)
        self.selection_count_label.setText(str(count))
        if count > 0:
            total_speed = sum(cell.value for cell in selected_cells)
            avg_speed = total_speed / count
            self.avg_speed_label.setText(f"{avg_speed:.2f} %")
            self.speed_input.setFocus()
            self.speed_input.selectAll()
        else:
            self.avg_speed_label.setText("N/A")
            self.speed_input.clearFocus()

    def is_feathering_enabled(self):
        return self.feather_checkbox.isChecked()

    def get_feather_value(self):
        return self.feather_spinbox.value()


class LineToolWindow(QDialog):
    """直线工具浮动窗口"""
    clear_all_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("直线工具")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setGeometry(600, 300, 200, 100)
        
        layout = QVBoxLayout(self)
        
        # 全部清零按钮
        self.clear_all_button = QPushButton("全部清零")
        self.clear_all_button.setFocusPolicy(Qt.NoFocus)
        self.clear_all_button.clicked.connect(self.clear_all_signal.emit)
        
        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        
        layout.addWidget(self.clear_all_button)
        layout.addWidget(self.close_button)
        
    def closeEvent(self, event):
        """窗口关闭时恢复到选择模式"""
        if hasattr(self.parent(), 'current_mode'):
            self.parent().current_mode = "selection"
            print("[Debug] 直线窗口关闭，恢复到选择模式")
        super().closeEvent(event)

class InfoWindow(QDialog):
    """信息浮动窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("信息")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(300, 400)
        
        layout = QVBoxLayout(self)
        
        # 状态区域
        status_group = QGroupBox("状态信息")
        status_layout = QFormLayout()
        
        self.fan_id_label = QLabel("--")
        self.fan_position_label = QLabel("--")
        self.fan_speed1_label = QLabel("--")
        self.fan_speed2_label = QLabel("--")
        self.fan_pwm_label = QLabel("--")
        self.fan_power_label = QLabel("2.7A, 54V")
        self.fan_runtime_label = QLabel("1234h56m00s")
        
        status_layout.addRow("风扇ID:", self.fan_id_label)
        status_layout.addRow("位置(行,列):", self.fan_position_label)
        status_layout.addRow("一级转速:", self.fan_speed1_label)
        status_layout.addRow("二级转速:", self.fan_speed2_label)
        status_layout.addRow("占空比:", self.fan_pwm_label)
        status_layout.addRow("电流电压:", self.fan_power_label)
        status_layout.addRow("运行时间:", self.fan_runtime_label)
        
        status_group.setLayout(status_layout)
        
        # 信息输出区域
        info_group = QGroupBox("系统信息")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setPlainText("系统信息输出区域\n")
        
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        
        # 1:1高度分配
        layout.addWidget(status_group, 1)
        layout.addWidget(info_group, 1)
        
        # 自动滚动到底部的定时器
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self._scroll_to_bottom)
        self.scroll_timer.setSingleShot(True)
        
    def update_fan_status(self, fan_id, row, col, pwm_ratio):
        """更新风扇状态信息"""
        self.fan_id_label.setText(str(fan_id))
        self.fan_position_label.setText(f"({row},{col})")
        
        # 计算转速
        speed1 = int(17000 * pwm_ratio / 100)
        speed2 = int(14600 * pwm_ratio / 100)
        
        self.fan_speed1_label.setText(f"{speed1} RPM")
        self.fan_speed2_label.setText(f"{speed2} RPM")
        self.fan_pwm_label.setText(f"{pwm_ratio:.1f}%")
        
    def clear_fan_status(self):
        """清除风扇状态信息"""
        self.fan_id_label.setText("--")
        self.fan_position_label.setText("--")
        self.fan_speed1_label.setText("--")
        self.fan_speed2_label.setText("--")
        self.fan_pwm_label.setText("--")
        
    def add_message(self, message):
        """添加消息到信息窗口"""
        self.info_text.append(message)
        # 延迟滚动到底部
        self.scroll_timer.start(10)
        
    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.info_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
class FunctionToolWindow(QDialog):
    """函数工具浮动窗口"""
    clear_all_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("函数工具")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setGeometry(600, 300, 200, 100)
        
        layout = QVBoxLayout(self)
        
        # 全部清零按钮
        self.clear_all_button = QPushButton("全部清零")
        self.clear_all_button.setFocusPolicy(Qt.NoFocus)
        self.clear_all_button.clicked.connect(self.clear_all_signal.emit)
        layout.addWidget(self.clear_all_button)
        
        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        
        layout.addWidget(self.close_button)
        
    def closeEvent(self, event):
        """窗口关闭时恢复到选择模式"""
        if hasattr(self.parent(), 'current_mode'):
            self.parent().current_mode = "selection"
            print("[Debug] 函数窗口关闭，恢复到选择模式")
        super().closeEvent(event)