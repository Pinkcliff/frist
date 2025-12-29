# wind_wall_simulator/canvas_widget.py

from PySide6.QtCore import Qt, QRectF, QRect, QSizeF, Signal, QPointF, Slot
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem
from PySide6.QtGui import QPen, QBrush, QPainter, QColor
import numpy as np
from typing import Set

from . import config
from . import utils





class FanCell(QGraphicsRectItem):
    """Represents a single fan cell in the grid."""
    def __init__(self, row: int, col: int, size: int, spacing: int):
        total_size = size + spacing
        super().__init__(col * total_size, row * total_size, size, size)
        self.row, self.col, self.value, self.is_selected = row, col, 0.0, False
        self.setAcceptHoverEvents(True)
        self.pen = QPen(Qt.NoPen)
        self.setPen(self.pen)
        self.selection_pen = QPen(config.SELECTION_BORDER_COLOR, config.SELECTION_BORDER_WIDTH)
        self.bg_color, self.text_color = QColor(), QColor()

    def paint(self, painter: QPainter, option, widget):
        super().paint(painter, option, widget)
        if config.CELL_SIZE > 12:
            painter.setPen(self.text_color)
            painter.setFont(config.CELL_FONT)
            painter.drawText(self.boundingRect(), Qt.AlignCenter, f"{int(self.value)}")

    def set_value(self, value: float):
        self.value = max(0.0, min(100.0, value))
        self.bg_color = utils.value_to_color(self.value)
        self.text_color = utils.get_contrasting_text_color(self.bg_color)
        self.setBrush(QBrush(self.bg_color))
        self.update()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.setPen(self.selection_pen if self.is_selected else self.pen)


class CanvasWidget(QGraphicsView):
    """The main interactive canvas."""
    selection_changed = Signal(set)
    fan_hover = Signal(int, int, int, float)  # fan_id_temp, row, col, pwm_ratio
    fan_hover_exit = Signal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.grid_data = np.zeros((config.GRID_DIM, config.GRID_DIM), dtype=float)
        self.cells: list[list[FanCell]] = []
        self.selected_cells: Set[FanCell] = set()
        
        # 选择工具相关
        self.selection_origin = QPointF()
        
        # 圆形工具相关
        self.circle_preview = QGraphicsEllipseItem()
        self.circle_preview.setPen(QPen(Qt.red, 1, Qt.DashLine))
        self.circle_preview.setZValue(1)
        self.circle_center = QPointF()
        
        self._init_grid()
        self._setup_view()
        self._init_brush_preview()
        
        # 添加圆形预览到场景
        self.scene.addItem(self.circle_preview)
        self.circle_preview.hide()

    def _setup_view(self):
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedSize(config.CANVAS_WIDTH, config.CANVAS_HEIGHT)
        self.scene.setSceneRect(-config.CELL_SPACING, -config.CELL_SPACING, 
                                config.CANVAS_WIDTH + config.CELL_SPACING, 
                                config.CANVAS_HEIGHT + config.CELL_SPACING)
        self.viewport().setMouseTracking(True)
        self.setMouseTracking(True)

    def _init_grid(self):
        self.cells = [[None for _ in range(config.GRID_DIM)] for _ in range(config.GRID_DIM)]
        for r in range(config.GRID_DIM):
            for c in range(config.GRID_DIM):
                cell = FanCell(r, c, config.CELL_SIZE, config.CELL_SPACING)
                cell.set_value(self.grid_data[r, c])
                self.scene.addItem(cell)
                self.cells[r][c] = cell

    def _init_brush_preview(self):
        self.brush_preview = QGraphicsEllipseItem()
        self.brush_preview.setPen(QPen(Qt.black, 1, Qt.DashLine))
        self.brush_preview.setZValue(1)
        self.scene.addItem(self.brush_preview)
        self.brush_preview.hide()

    def drawForeground(self, painter: QPainter, rect: QRectF):
        super().drawForeground(painter, rect)
        pen = QPen(config.MODULE_LINE_COLOR, config.MODULE_LINE_WIDTH, Qt.SolidLine)
        painter.setPen(pen)
        module_pixel_size = config.MODULE_DIM * config.TOTAL_CELL_SIZE
        offset = config.CELL_SPACING / 2
        for r in range(config.MODULE_DIM, config.GRID_DIM, config.MODULE_DIM):
            y = r * config.TOTAL_CELL_SIZE - offset
            painter.drawLine(QPointF(0, y), QPointF(config.CANVAS_WIDTH, y))
        for c in range(config.MODULE_DIM, config.GRID_DIM, config.MODULE_DIM):
            x = c * config.TOTAL_CELL_SIZE - offset
            painter.drawLine(QPointF(x, 0), QPointF(x, config.CANVAS_HEIGHT))

    def clear_selection(self):
        for cell in self.selected_cells:
            cell.set_selected(False)
        self.selected_cells.clear()

# canvas_widget.py -> CanvasWidget
    def mousePressEvent(self, event):
        mode_widget = self.main_window.tool_stack.currentWidget()

        if event.button() == Qt.LeftButton:
            if mode_widget == self.main_window.selection_widget:
                self.selection_origin = event.pos()
            elif mode_widget == self.main_window.circle_widget:
                self.circle_center = self.mapToScene(event.pos())
                self.circle_preview.setRect(QRectF(self.circle_center, QSizeF(0, 0)))
                self.circle_preview.show()
            elif mode_widget == self.main_window.brush_widget:
                self.main_window.data_before_edit = np.copy(self.grid_data)
                self._apply_brush(self.mapToScene(event.pos()))
        
        super().mousePressEvent(event)


    def mouseDoubleClickEvent(self, event):
        mode_widget = self.main_window.tool_stack.currentWidget()
        is_brush_mode = mode_widget == self.main_window.brush_widget
        is_circle_mode = mode_widget == self.main_window.circle_widget
        
        if event.button() == Qt.LeftButton and not is_brush_mode and not is_circle_mode:
            # 设置双击标志，防止触发单击选择
            self._double_click_handled = True
            
            item = self.itemAt(event.pos())
            if not isinstance(item, FanCell): return
            
            modifiers = event.modifiers()
            if modifiers == Qt.ShiftModifier:
                # Shift+双击：添加模块到选择
                self._handle_shift_toggle_module(item)
            elif modifiers == Qt.ControlModifier:
                # Ctrl+双击：反选模块
                module_cells = self._get_module_cells(item)
                num_selected_in_module = sum(1 for cell in module_cells if cell.is_selected)
                if num_selected_in_module > 0:
                    self._remove_module_from_selection(item)
                else:
                    self._add_module_to_selection(item)
            else:
                # 普通双击：选择模块中的16颗风扇
                self.clear_selection()
                self._add_module_to_selection(item)
            self.selection_changed.emit(self.selected_cells)
                
        super().mouseDoubleClickEvent(event)

# canvas_widget.py -> CanvasWidget
    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        mode_widget = self.main_window.tool_stack.currentWidget()

        if event.buttons() == Qt.LeftButton:
            if mode_widget == self.main_window.selection_widget:
                pass  # 移除rubber_band显示
            elif mode_widget == self.main_window.circle_widget:
                radius = np.linalg.norm(np.array([scene_pos.x(), scene_pos.y()]) - 
                                        np.array([self.circle_center.x(), self.circle_center.y()]))
                self.circle_preview.setRect(self.circle_center.x() - radius, self.circle_center.y() - radius, 
                                            2 * radius, 2 * radius)
            elif mode_widget == self.main_window.brush_widget:
                self._apply_brush(scene_pos)
        
        if mode_widget == self.main_window.brush_widget:
            self.brush_preview.setPos(scene_pos)
        
        item = self.itemAt(event.pos())
        if isinstance(item, FanCell):
            display_row = config.GRID_DIM - item.row
            display_col = item.col + 1
            fan_id_temp = item.row * config.GRID_DIM + item.col
            pwm_ratio = item.value
            self.fan_hover.emit(fan_id_temp, display_row, display_col, pwm_ratio)
        else:
            self.fan_hover_exit.emit()
        
        super().mouseMoveEvent(event)


    def enterEvent(self, event):
        self.update_brush_preview()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.brush_preview.hide()
        self.fan_hover_exit.emit()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，包括单击选择、笔刷操作的撤销支持和圆形选择"""
        mode_widget = self.main_window.tool_stack.currentWidget()
        
        if event.button() == Qt.LeftButton:
            if mode_widget == self.main_window.selection_widget:
                # 点选模式下的单击选择 - 但要避免双击后的单击
                if not hasattr(self, '_double_click_handled') or not self._double_click_handled:
                    item = self.itemAt(event.pos())
                    if isinstance(item, FanCell):
                        modifiers = event.modifiers()
                        if modifiers == Qt.ShiftModifier:
                            # Shift+单击：添加到选择
                            self._handle_ctrl_toggle(item, force_select=True)
                        elif modifiers == Qt.ControlModifier:
                            # Ctrl+单击：反选
                            self._handle_ctrl_toggle(item)
                        else:
                            # 普通单击：选择单个单元格
                            self._handle_single_selection(item)
                        self.selection_changed.emit(self.selected_cells)
                # 重置双击标志
                self._double_click_handled = False
            elif mode_widget == self.main_window.brush_widget:
                # 笔刷操作完成，推送撤销命令
                if hasattr(self.main_window, 'data_before_edit') and self.main_window.data_before_edit is not None:
                    # 检查是否有实际变化
                    if not np.array_equal(self.main_window.data_before_edit, self.grid_data):
                        brush_size = self.main_window.brush_widget.get_brush_size()
                        brush_value = self.main_window.brush_widget.get_brush_value()
                        description = f"笔刷操作 (大小: {brush_size}, 值: {brush_value}%)"
                        if self.main_window.brush_widget.is_feathering_enabled():
                            feather_value = self.main_window.brush_widget.get_feather_value()
                            description += f" (羽化: {feather_value})"
                        self.main_window._push_edit_command(description)
            elif mode_widget == self.main_window.circle_widget:
                # 圆形选择完成，支持修饰键
                modifiers = event.modifiers()
                self._apply_circle_selection(modifiers)
                self.circle_preview.hide()
        
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """处理键盘事件，特别是ESC键取消所有选择"""
        if event.key() == Qt.Key_Escape:
            # ESC键：取消所有选择
            if self.selected_cells:
                self.clear_selection()
                self.selection_changed.emit(self.selected_cells)
        else:
            super().keyPressEvent(event)

    def _apply_circle_selection(self, modifiers=None):
        """应用圆形选择，选择与圆形线条接触的风扇单元，支持修饰键"""
        if not hasattr(self, 'circle_center'):
            return
        
        # 计算圆形半径
        circle_rect = self.circle_preview.rect()
        circle_radius = circle_rect.width() / 2
        
        # 如果半径太小，不进行选择
        if circle_radius < 1:
            return
        
        # 根据修饰键决定选择行为
        if modifiers != Qt.ShiftModifier and modifiers != Qt.ControlModifier:
            # 普通圆形选择：清除当前选择
            self.clear_selection()
        
        # 收集与圆形相交的风扇单元
        intersecting_cells = set()
        for row in range(config.GRID_DIM):
            for col in range(config.GRID_DIM):
                cell = self.cells[row][col]
                cell_rect = cell.sceneBoundingRect()
                
                # 检查矩形（风扇单元）是否与圆形相交
                if self._rect_intersects_circle(cell_rect, self.circle_center, circle_radius):
                    intersecting_cells.add(cell)
        
        # 根据修饰键处理选择
        if modifiers == Qt.ShiftModifier:
            # Shift+圆形选择：添加到当前选择
            for cell in intersecting_cells:
                self.selected_cells.add(cell)
                cell.set_selected(True)
        elif modifiers == Qt.ControlModifier:
            # Ctrl+圆形选择：反选
            for cell in intersecting_cells:
                if cell in self.selected_cells:
                    self.selected_cells.remove(cell)
                    cell.set_selected(False)
                else:
                    self.selected_cells.add(cell)
                    cell.set_selected(True)
        else:
            # 普通圆形选择：选择相交的单元
            for cell in intersecting_cells:
                self.selected_cells.add(cell)
                cell.set_selected(True)
        
        # 通知主窗口选择已更改
        self.selection_changed.emit(self.selected_cells)
    
    def _rect_intersects_circle(self, rect, circle_center, circle_radius):
        """检查矩形是否与圆形相交（包括接触）"""
        # 计算矩形中心到圆心的距离
        rect_center_x = rect.center().x()
        rect_center_y = rect.center().y()
        
        # 计算矩形的半宽和半高
        half_width = rect.width() / 2
        half_height = rect.height() / 2
        
        # 计算圆心到矩形的最短距离
        dx = abs(circle_center.x() - rect_center_x)
        dy = abs(circle_center.y() - rect_center_y)
        
        # 如果圆心在矩形内部，则相交
        if dx <= half_width and dy <= half_height:
            return True
        
        # 如果圆心在矩形的角落区域，检查到最近角点的距离
        if dx > half_width and dy > half_height:
            corner_distance_sq = (dx - half_width) ** 2 + (dy - half_height) ** 2
            return corner_distance_sq <= circle_radius ** 2
        
        # 如果圆心在矩形的边缘区域，检查到最近边的距离
        if dx > half_width:
            return (dx - half_width) <= circle_radius
        else:
            return (dy - half_height) <= circle_radius

# canvas_widget.py -> CanvasWidget

    def _apply_brush(self, center_pos: QPointF, is_start_of_stroke=False):
        # 【新增】如果是笔画的开始，记录当前数据状态
        if is_start_of_stroke:
            self.brush_stroke_start_data = np.copy(self.grid_data)

        brush_size = self.main_window.brush_widget.get_brush_size()
        brush_value = self.main_window.brush_widget.get_brush_value()
        brush_radius_sq = ((brush_size / 2.0) * config.TOTAL_CELL_SIZE) ** 2
        
        brushed_cells = []
        
        for r in range(config.GRID_DIM):
            for c in range(config.GRID_DIM):
                cell = self.cells[r][c]
                cell_center = cell.sceneBoundingRect().center()
                dist_sq = (center_pos.x() - cell_center.x())**2 + (center_pos.y() - cell_center.y())**2
                if dist_sq <= brush_radius_sq:
                    if self.grid_data[r, c] != brush_value:
                        self.grid_data[r, c] = brush_value
                        cell.set_value(brush_value)
                    brushed_cells.append(cell)
        
        if self.main_window.brush_widget.is_feathering_enabled() and brushed_cells:
            feather_value = self.main_window.brush_widget.get_feather_value()
            self._apply_feathering(brushed_cells, brush_value, feather_value)


    # ... (在 _apply_brush 方法之后) ...

    def _apply_feathering(self, source_cells, base_value, feather_value):
        """
        对源单元格集合应用羽化效果。
        :param source_cells: 羽化效果的源单元格列表或集合。
        :param base_value: 源单元格的转速值。
        :param feather_value: 羽化层数。
        """
        if not source_cells or feather_value <= 0:
            return

        processed_cells = set(source_cells)
        current_layer = list(source_cells)

        for layer in range(1, feather_value + 1):
            next_layer = set()
            # 根据公式计算当前羽化层的转速值
            layer_value = base_value * (feather_value - layer) / feather_value
            layer_value = max(0.0, layer_value) # 确保不小于0

            if not current_layer:
                break # 如果没有更多单元格可以扩展，提前退出

            for cell in current_layer:
                # 检查上下左右四个邻居
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = cell.row + dr, cell.col + dc

                    # 检查边界
                    if 0 <= nr < config.GRID_DIM and 0 <= nc < config.GRID_DIM:
                        neighbor_cell = self.cells[nr][nc]
                        if neighbor_cell not in processed_cells:
                            # 为这个邻居应用羽化值
                            # 【核心修复】确保同时更新 grid_data 和 cell 的值
                            current_val = self.grid_data[nr, nc]
                            # 只有当羽化值大于当前值时才更新，避免覆盖更高转速的区域
                            if layer_value > current_val:
                                self.grid_data[nr, nc] = layer_value
                                neighbor_cell.set_value(layer_value)
                            
                            # 将其加入下一层和已处理集合
                            next_layer.add(neighbor_cell)
                            processed_cells.add(neighbor_cell)
            
            current_layer = list(next_layer)

    # ... (其他方法，如 set_values_for_selection) ...

    def _handle_single_selection(self, item):
        if not item.is_selected or len(self.selected_cells) > 1:
            self.clear_selection()
            self.selected_cells.add(item)
            item.set_selected(True)

    def _handle_ctrl_toggle(self, item, force_select=False):
        if force_select:
            if not item.is_selected:
                self.selected_cells.add(item)
                item.set_selected(True)
            return

        if item.is_selected:
            self.selected_cells.remove(item)
            item.set_selected(False)
        else:
            self.selected_cells.add(item)
            item.set_selected(True)


    def _get_module_cells(self, item: FanCell) -> list[FanCell]:
        cells_in_module = []
        module_row_start = (item.row // config.MODULE_DIM) * config.MODULE_DIM
        module_col_start = (item.col // config.MODULE_DIM) * config.MODULE_DIM
        for r in range(module_row_start, module_row_start + config.MODULE_DIM):
            for c in range(module_col_start, module_col_start + config.MODULE_DIM):
                cells_in_module.append(self.cells[r][c])
        return cells_in_module

    def _add_module_to_selection(self, item: FanCell):
        for cell in self._get_module_cells(item):
            if not cell.is_selected:
                self.selected_cells.add(cell)
                cell.set_selected(True)

    def _remove_module_from_selection(self, item: FanCell):
        for cell in self._get_module_cells(item):
            if cell.is_selected:
                self.selected_cells.remove(cell)
                cell.set_selected(False)

    def _handle_shift_toggle_module(self, item: FanCell):
        module_cells = self._get_module_cells(item)
        num_selected_in_module = sum(1 for cell in module_cells if cell.is_selected)
        total_cells_in_module = config.MODULE_DIM * config.MODULE_DIM
        is_remove_intent = (not item.is_selected and 
                            num_selected_in_module == total_cells_in_module - 1)
        if is_remove_intent:
            self._remove_module_from_selection(item)
        else:
            self._add_module_to_selection(item)

    @Slot()
    def update_brush_preview(self):
        try:
            if self.main_window.tool_stack.currentWidget() == self.main_window.brush_widget:
                size = self.main_window.brush_widget.get_brush_size() * config.TOTAL_CELL_SIZE
                value = self.main_window.brush_widget.get_brush_value()
                solid_color = utils.value_to_color(value)
                preview_color = QColor(solid_color)
                preview_color.setAlpha(50)
                self.brush_preview.setBrush(QBrush(preview_color))
                self.brush_preview.setRect(-size/2, -size/2, size, size)
                self.brush_preview.show()
            else:
                self.brush_preview.hide()
        except Exception as e:
            print(f"Error in update_brush_preview: {e}")
            self.brush_preview.hide()

    def set_values_for_selection(self, value: float):
        for cell in self.selected_cells:
            self.grid_data[cell.row, cell.col] = value
            cell.set_value(value)
        self.selection_changed.emit(self.selected_cells)

    def get_grid_data(self) -> np.ndarray:
        return self.grid_data
    
    def update_all_cells_from_data(self):
        """从grid_data更新所有单元格的显示"""
        for r in range(config.GRID_DIM):
            for c in range(config.GRID_DIM):
                cell = self.cells[r][c]
                cell.set_value(self.grid_data[r, c])
        self.update()

    @Slot()
    def select_all_cells(self):
        for r in range(config.GRID_DIM):
            for c in range(config.GRID_DIM):
                cell = self.cells[r][c]
                if not cell.is_selected:
                    self.selected_cells.add(cell)
                    cell.set_selected(True)
        self.selection_changed.emit(self.selected_cells)
        
    def get_selected_cells(self) -> list:
        return list(self.selected_cells)
        
    def invert_selection(self):
        new_selection = set()
        for r in range(config.GRID_DIM):
            for c in range(config.GRID_DIM):
                cell = self.cells[r][c]
                if cell in self.selected_cells:
                    cell.set_selected(False)
                else:
                    cell.set_selected(True)
                    new_selection.add(cell)
        self.selected_cells = new_selection
        self.selection_changed.emit(self.selected_cells)
        
    def reset_selection(self):
        for cell in self.selected_cells:
            cell.set_selected(False)
        self.selected_cells.clear()
        self.selection_changed.emit(self.selected_cells)
    # canvas_widget.py -> CanvasWidget

    def apply_speed_and_feather_to_selection(self, speed, feather_enabled, feather_value):
        """
        一个统一的方法，用于对当前选中的单元格设置速度并应用羽化。
        这是处理点选模式下设置速度的核心逻辑。
        """
        selected_cells = self.get_selected_cells()
        if not selected_cells:
            return 0 # 返回受影响的单元格数量

        # 1. 对选中的单元格设置基础速度，并更新 grid_data
        for cell in selected_cells:
            self.grid_data[cell.row, cell.col] = speed
            cell.set_value(speed)
        
        # 2. 如果羽化已启用，则应用羽化效果
        if feather_enabled:
            self._apply_feathering(selected_cells, speed, feather_value)

        self.update() # 更新整个视图
        return len(selected_cells)

