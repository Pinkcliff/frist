# commands.py
from PySide6.QtGui import QUndoCommand
import numpy as np

class EditCommand(QUndoCommand):
    """一个封装了对grid_data修改的通用命令"""
    def __init__(self, canvas, old_data, new_data, description):
        super().__init__(description)
        self.canvas = canvas
        self.old_data = np.copy(old_data)
        self.new_data = np.copy(new_data)

    def undo(self):
        """撤销操作"""
        self.canvas.grid_data = np.copy(self.old_data)
        self.canvas.update_all_cells_from_data()

    def redo(self):
        """重做操作"""
        self.canvas.grid_data = np.copy(self.new_data)
        self.canvas.update_all_cells_from_data()
