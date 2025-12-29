# wind_wall_simulator/template_library.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, 
                               QHBoxLayout, QAbstractItemView)
from PySide6.QtCore import Qt

class TemplateLibrary(QWidget):
    """The left-side panel for managing templates."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        
        self.template_list = QListWidget()
        self.template_list.setSelectionMode(QAbstractItemView.SingleSelection)
        # Add dummy items
        self.template_list.addItems(["中心高斯喷流_v1", "左右扫描风_初始", "城市峡谷风"])

        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("加载")
        self.save_button = QPushButton("保存")
        self.delete_button = QPushButton("删除")
        
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.delete_button)

        self.main_layout.addWidget(self.template_list)
        self.main_layout.addLayout(self.button_layout)
