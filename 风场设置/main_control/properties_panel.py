# wind_wall_simulator/properties_panel.py

from . import config
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel, QLineEdit, 
                               QPushButton, QFormLayout, QSpinBox, QComboBox,
                               QFrame, QCheckBox, QHBoxLayout)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator

class PropertiesPanel(QWidget):
    """The right-side panel with a new 'Select All' button."""
    export_requested = Signal()
    select_all_requested = Signal() # New signal for select all

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self._create_selection_group()
        self._create_tools_group()
        self._create_export_group()
        self.main_layout.addStretch()

    def _create_selection_group(self):
        group_box = QGroupBox("选择信息 (Selection Info)")
        # Use a QVBoxLayout to hold the form and the button
        main_v_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.selection_count_label = QLabel("0")
        self.avg_speed_label = QLabel("N/A")
        self.speed_input = QLineEdit("0.00")
        validator = QDoubleValidator(0.0, 100.0, 2)
        self.speed_input.setValidator(validator)
        form_layout.addRow("选中数量:", self.selection_count_label)
        form_layout.addRow("平均转速:", self.avg_speed_label)
        form_layout.addRow("设置转速 (%):", self.speed_input)
        
        # [新增] Select All button
        self.select_all_button = QPushButton("全选 (Select All)")
        self.select_all_button.clicked.connect(self.select_all_requested.emit)
        
        main_v_layout.addLayout(form_layout)
        main_v_layout.addWidget(self.select_all_button)
        
        group_box.setLayout(main_v_layout)
        self.main_layout.addWidget(group_box)

    def _create_tools_group(self):
        group_box = QGroupBox("工具箱 (Toolbox)")
        layout = QVBoxLayout()
        brush_group = QGroupBox("笔刷工具 (Brush Tool)")
        brush_layout = QFormLayout()
        self.brush_size_spinbox = QSpinBox()
        self.brush_size_spinbox.setRange(1, config.GRID_DIM)
        self.brush_size_spinbox.setValue(5)
        self.brush_value_input = QLineEdit("100.00")
        validator = QDoubleValidator(0.0, 100.0, 2)
        self.brush_value_input.setValidator(validator)
        brush_layout.addRow("笔刷直径 (个):", self.brush_size_spinbox)
        brush_layout.addRow("笔刷转速 (%):", self.brush_value_input)
        brush_group.setLayout(brush_layout)
        layout.addWidget(brush_group)
        func_group = QGroupBox("函数生成器 (Function Generator)")
        layout.addWidget(func_group)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_export_group(self):
        group_box = QGroupBox("仿真与导出 (Simulation & Export)")
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.max_rpm_input = QLineEdit("15000")
        self.max_rpm_input.setValidator(QIntValidator(0, 100000))
        form_layout.addRow("最大转速 (RPM):", self.max_rpm_input)
        self.export_button = QPushButton("导出场文件")
        self.export_button.clicked.connect(self.export_requested.emit)
        layout.addLayout(form_layout)
        layout.addWidget(self.export_button)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    @Slot(set)
    def update_on_selection(self, selected_cells: set):
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

    def is_brush_active(self) -> bool:
        # 笔刷激活状态现在由笔刷窗口的显示状态决定
        # 这个方法保留是为了兼容性，但总是返回False
        return False

    def get_brush_size(self) -> int:
        return self.brush_size_spinbox.value()

    def get_brush_value(self) -> float:
        try:
            return round(float(self.brush_value_input.text()), 2)
        except ValueError:
            return 100.0

    def get_max_rpm(self) -> int:
        try:
            return int(self.max_rpm_input.text())
        except ValueError:
            return 0
