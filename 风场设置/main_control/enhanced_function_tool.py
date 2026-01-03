# -*- coding: utf-8 -*-
"""
增强版函数工具窗口

集成12种数学函数模板用于风场生成

创建时间: 2024-01-03
作者: Wind Field Editor Team
版本: 2.0.0

修改历史:
    2024-01-03 [v2.0.0] 重大更新
        - 集成12种数学函数模板（从fan_con学习）
        - 添加函数参数配置界面
        - 支持时间参数预览
    2024-01-03 [v1.0.0] 初始版本
        - 基础函数工具界面
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QPushButton, QComboBox, QDoubleSpinBox,
    QSpinBox, QCheckBox, QSlider, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator

# 添加项目路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class EnhancedFunctionToolWindow(QDialog):
    """
    增强版函数工具窗口

    提供12种预定义函数模板的界面

    功能:
    - 函数分类选择
    - 参数实时配置
    - 时间参数预览
    - 一键应用函数
    """

    # 信号定义
    apply_function_signal = Signal(str, dict, float)  # 函数类型, 参数, 时间
    preview_animation_signal = Signal(str, dict)  # 预览动画信号: 函数类型, 参数
    clear_all_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("函数生成器 v2.0")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(450, 600)

        # 导入函数工厂
        try:
            from wind_field_editor.functions import WindFieldFunctionFactory
            self.function_factory = WindFieldFunctionFactory
            self.available_functions = self.function_factory.get_available_functions()
            self.categories = self.function_factory.get_all_categories()
        except ImportError as e:
            print(f"警告: 无法导入函数模块: {e}")
            self.available_functions = []
            self.categories = []

        # 当前选择的函数
        self.current_function = 'gaussian'
        self.current_time = 0.0

        # 中心位置（实际位置，0-based索引）
        self.center_row = 20
        self.center_col = 20

        # 创建UI
        self._create_ui()
        self._connect_signals()
        self._populate_functions()
        self._update_center_display()  # 更新中心位置显示

    def _create_ui(self):
        """创建UI"""
        main_layout = QVBoxLayout(self)

        # 1. 函数选择区域
        selection_group = QGroupBox("函数选择")
        selection_layout = QVBoxLayout()

        # 分类标签和函数列表
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        category_layout.addWidget(QLabel("分类:"))
        category_layout.addWidget(self.category_combo)
        selection_layout.addLayout(category_layout)

        # 函数列表
        self.function_list = QListWidget()
        self.function_list.setSelectionMode(QListWidget.SingleSelection)
        selection_layout.addWidget(self.function_list)

        # 函数描述
        self.description_label = QLabel("选择一个函数查看详情")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        selection_layout.addWidget(self.description_label)

        selection_group.setLayout(selection_layout)
        main_layout.addWidget(selection_group)

        # 2. 参数配置区域
        params_group = QGroupBox("参数配置")
        params_form = QFormLayout()

        # 中心位置（默认在第20行第20列，显示为x021y021）
        center_group = QGroupBox("中心位置")
        center_layout = QVBoxLayout()

        # 显示当前中心位置
        center_display_layout = QHBoxLayout()
        self.center_label = QLabel("x021y021")
        self.center_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3; padding: 5px;")
        self.center_label.setAlignment(Qt.AlignCenter)
        center_display_layout.addWidget(self.center_label)
        center_layout.addLayout(center_display_layout)

        # 平移按钮
        button_layout = QVBoxLayout()
        button_layout.setSpacing(2)

        # 上
        row1 = QHBoxLayout()
        self.btn_up = QPushButton("↑")
        self.btn_up.setFixedSize(40, 30)
        self.btn_up.clicked.connect(lambda: self._move_center(0, -1))
        row1.addStretch()
        row1.addWidget(self.btn_up)
        row1.addStretch()
        button_layout.addLayout(row1)

        # 左 右
        row2 = QHBoxLayout()
        self.btn_left = QPushButton("←")
        self.btn_left.setFixedSize(40, 30)
        self.btn_left.clicked.connect(lambda: self._move_center(-1, 0))
        self.btn_right = QPushButton("→")
        self.btn_right.setFixedSize(40, 30)
        self.btn_right.clicked.connect(lambda: self._move_center(1, 0))
        row2.addWidget(self.btn_left)
        row2.addStretch()
        row2.addWidget(self.btn_right)
        button_layout.addLayout(row2)

        # 下
        row3 = QHBoxLayout()
        self.btn_down = QPushButton("↓")
        self.btn_down.setFixedSize(40, 30)
        self.btn_down.clicked.connect(lambda: self._move_center(0, 1))
        row3.addStretch()
        row3.addWidget(self.btn_down)
        row3.addStretch()
        button_layout.addLayout(row3)

        center_layout.addLayout(button_layout)
        center_group.setLayout(center_layout)
        params_form.addRow(center_group)

        # 幅度
        self.amplitude_spinbox = QDoubleSpinBox()
        self.amplitude_spinbox.setRange(0.0, 200.0)
        self.amplitude_spinbox.setValue(100.0)
        self.amplitude_spinbox.setSuffix(" %")
        params_form.addRow("幅度:", self.amplitude_spinbox)

        # 时间参数
        self.time_spinbox = QDoubleSpinBox()
        self.time_spinbox.setRange(0.0, 20.0)
        self.time_spinbox.setValue(0.0)
        self.time_spinbox.setSingleStep(0.5)
        self.time_spinbox.setSuffix(" s")
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 200)  # 0-20秒，步长0.1
        self.time_slider.setValue(0)

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.time_spinbox)
        time_layout.addWidget(self.time_slider)
        params_form.addRow("时间参数:", time_layout)

        # 特定函数参数（根据选择的函数动态显示）
        self.specific_params_group = QGroupBox("特定参数")
        self.specific_params_layout = QFormLayout()
        self.specific_params_group.setLayout(self.specific_params_layout)
        params_form.addRow(self.specific_params_group)

        params_group.setLayout(params_form)
        main_layout.addWidget(params_group, 2)

        # 3. 操作按钮
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("应用函数")
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.preview_button = QPushButton("预览")
        self.clear_all_button = QPushButton("全部清零")

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.clear_all_button)
        main_layout.addLayout(button_layout)

        # 4. 公式预览
        formula_group = QGroupBox("函数公式")
        formula_layout = QVBoxLayout()
        self.formula_label = QLabel("函数公式将显示在这里")
        self.formula_label.setWordWrap(True)
        self.formula_label.setStyleSheet("font-family: Consolas, monospace; padding: 10px; background: #f5f5f5;")
        formula_layout.addWidget(self.formula_label)
        formula_group.setLayout(formula_layout)
        main_layout.addWidget(formula_group, 1)

    def _connect_signals(self):
        """连接信号"""
        # 分类变化
        self.category_combo.currentTextChanged.connect(self._on_category_changed)

        # 函数选择变化
        self.function_list.currentItemChanged.connect(self._on_function_changed)

        # 时间滑块和输入框同步
        self.time_slider.valueChanged.connect(lambda v: self.time_spinbox.setValue(v / 10.0))
        self.time_spinbox.valueChanged.connect(lambda v: self.time_slider.setValue(int(v * 10)))

        # 应用按钮
        self.apply_button.clicked.connect(self._apply_function)
        self.preview_button.clicked.connect(self._preview_function)
        self.clear_all_button.clicked.connect(self.clear_all_signal.emit)

    def _populate_functions(self):
        """填充函数列表"""
        self.function_list.clear()

        # 获取当前分类
        current_category = self.category_combo.currentText()

        if current_category in self.categories:
            # 获取该分类下的函数
            try:
                functions = self.function_factory.get_functions_by_category(current_category)
                for func_name in functions:
                    desc = self.function_factory.get_description(func_name)
                    item = QListWidgetItem(f"{func_name}: {desc}")
                    item.setData(Qt.UserRole, func_name)
                    self.function_list.addItem(item)
            except Exception as e:
                print(f"获取函数列表失败: {e}")
        else:
            # 显示所有函数
            for func_name in self.available_functions:
                desc = self.function_factory.get_description(func_name)
                item = QListWidgetItem(f"{func_name}: {desc}")
                item.setData(Qt.UserRole, func_name)
                self.function_list.addItem(item)

    def _on_category_changed(self, category):
        """分类变化时更新函数列表"""
        self._populate_functions()

    def _on_function_changed(self, item):
        """函数变化时更新界面"""
        if item is None:
            return

        func_name = item.data(Qt.UserRole)
        self.current_function = func_name

        # 更新描述和公式
        desc = self.function_factory.get_description(func_name)
        self.description_label.setText(f"说明: {desc}")

        # 更新公式
        formula = self._get_function_formula(func_name)
        self.formula_label.setText(formula)

        # 更新特定参数
        self._update_specific_params(func_name)

    def _get_function_formula(self, func_name: str) -> str:
        """获取函数公式"""
        formulas = {
            'simple_wave': 'z = sin(x) * cos(y + t)',
            'radial_wave': 'z = sin(r - t) * exp(-0.1 * r)',
            'gaussian': 'z = A * exp(-((x-x0)^2 + (y-y0)^2) / (2*sigma^2))',
            'gaussian_packet': 'z = exp(-r^2/2sigma^2) * sin(kx*x + ky*y + wt)',
            'standing_wave': 'z = sin(x) * sin(y) * cos(t)',
            'linear_gradient': 'z = 0.5 * (x + y) * sin(t)',
            'radial_gradient': 'z = (r / 5) * cos(t + r)',
            'circular_gradient': 'z = clip((r - r_inner) / (r_outer - r_inner), 0, 1)',
            'spiral_wave': 'z = sin(n*theta + r - t) * exp(-0.1*r)',
            'interference': 'z = sin(r1 - t) + sin(r2 - t)',
            'checkerboard': 'z = sin(x*size + t) * sin(y*size + t)',
            'noise_field': 'z = 噪声函数 + 随机扰动',
            'polynomial_surface': 'z = (x^3 - 3xy^2) / 10',
            'saddle_point': 'z = (x^2 - y^2) / 5',
        }
        return formulas.get(func_name, "公式未定义")

    def _update_specific_params(self, func_name: str):
        """更新特定函数的参数"""
        # 清除现有参数
        while self.specific_params_layout.count():
            child = self.specific_params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 根据函数类型添加特定参数
        if func_name == 'gaussian':
            sigma_spinbox = QDoubleSpinBox()
            sigma_spinbox.setRange(1.0, 20.0)
            sigma_spinbox.setValue(5.0)
            sigma_spinbox.setSuffix(" sigma")
            self.sigma_spinbox = sigma_spinbox
            self.specific_params_layout.addRow("标准差:", sigma_spinbox)

        elif func_name in ['spiral_wave']:
            arms_spinbox = QSpinBox()
            arms_spinbox.setRange(1, 10)
            arms_spinbox.setValue(3)
            self.arms_spinbox = arms_spinbox
            self.specific_params_layout.addRow("螺旋臂数:", arms_spinbox)

        elif func_name == 'radial_gradient':
            bands_spinbox = QSpinBox()
            bands_spinbox.setRange(1, 20)
            bands_spinbox.setValue(3)
            self.bands_spinbox = bands_spinbox
            self.specific_params_layout.addRow("条纹数量:", bands_spinbox)

        elif func_name == 'linear_gradient':
            direction_combo = QComboBox()
            direction_combo.addItems(['对角线', 'X方向', 'Y方向'])
            self.direction_combo = direction_combo
            self.specific_params_layout.addRow("渐变方向:", direction_combo)

        else:
            label = QLabel("无特定参数")
            label.setStyleSheet("color: #999; font-style: italic;")
            self.specific_params_layout.addRow("", label)

    def _get_function_params(self) -> dict:
        """获取当前函数参数"""
        # 使用当前的中心位置
        params = {
            'center': (float(self.center_row), float(self.center_col)),
            'amplitude': self.amplitude_spinbox.value(),
            'time': self.time_spinbox.value(),
        }

        # 添加特定参数
        func_name = self.current_function

        if func_name == 'gaussian' and hasattr(self, 'sigma_spinbox'):
            params['sigma'] = self.sigma_spinbox.value()
        elif func_name == 'spiral_wave' and hasattr(self, 'arms_spinbox'):
            params['arms'] = self.arms_spinbox.value()
        elif func_name == 'radial_gradient' and hasattr(self, 'bands_spinbox'):
            params['bands'] = self.bands_spinbox.value()
        elif func_name == 'linear_gradient' and hasattr(self, 'direction_combo'):
            direction_map = {'对角线': 'diagonal', 'X方向': 'x', 'Y方向': 'y'}
            params['direction'] = direction_map.get(self.direction_combo.currentText(), 'diagonal')

        return params

    def _apply_function(self):
        """应用函数"""
        params = self._get_function_params()
        time_value = self.time_spinbox.value()

        # 发送信号
        self.apply_function_signal.emit(self.current_function, params, time_value)

        # 记录到系统信息
        print(f"[FunctionTool] 应用函数: {self.current_function}")
        print(f"[FunctionTool] 参数: {params}")
        print(f"[FunctionTool] 时间: {time_value}")

    def _preview_function(self):
        """预览函数动画 - 发送动画信号到主窗口"""
        params = self._get_function_params()

        # 发送预览动画信号，主窗口将处理动画
        self.preview_animation_signal.emit(self.current_function, params)

        # 记录日志
        print(f"[FunctionTool] 开始预览动画: {self.current_function}")
        print(f"[FunctionTool] 参数: center={params['center']}, amplitude={params['amplitude']}%")

    def get_function_params(self) -> dict:
        """获取当前函数参数（供外部调用）"""
        return self._get_function_params()

    def set_time_value(self, time_value: float):
        """设置时间值（用于动画）"""
        self.time_spinbox.setValue(time_value)

    def _update_center_display(self):
        """更新中心位置显示"""
        # 显示为1-based索引：x020y020
        display_x = self.center_col + 1
        display_y = self.center_row + 1
        self.center_label.setText(f"x{display_x:03d}y{display_y:03d}")

    def _move_center(self, dx, dy):
        """平移中心位置

        Args:
            dx: 列方向偏移（-1左，0不变，1右）
            dy: 行方向偏移（-1上，0不变，1下）
        """
        new_row = self.center_row + dy
        new_col = self.center_col + dx

        # 检查边界
        if 0 <= new_row < 40 and 0 <= new_col < 40:
            self.center_row = new_row
            self.center_col = new_col
            self._update_center_display()
            print(f"[FunctionTool] 中心移动到: x{self.center_col+1:03d}y{self.center_row+1:03d}")
        else:
            print(f"[FunctionTool] 无法移动：超出边界")


# 保留原有FunctionToolWindow作为别名
FunctionToolWindow = EnhancedFunctionToolWindow


# 导出
__all__ = [
    'EnhancedFunctionToolWindow',
    'FunctionToolWindow',
]
