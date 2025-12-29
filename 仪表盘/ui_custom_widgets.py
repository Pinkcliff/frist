# ui_custom_widgets.py
import math
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QEasingCurve, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QMouseEvent, QPixmap, QPainterPath

class ThemeSwitch(QWidget):
    toggled = Signal(bool)
    # ... (代码与之前版本完全相同)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 30)
        self.setCursor(Qt.PointingHandCursor)
        self._is_on = False

        self._knob_x_pos = 3
        self.knob_pos_anim = QPropertyAnimation(self, b"knob_position", self)
        self.knob_pos_anim.setDuration(200)
        self.knob_pos_anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.bg_color_on = QColor("#00d1ff")
        self.bg_color_off = QColor("#5e626a")
        self.knob_color = QColor("#e1e1e6")
        self.icon_color = QColor("#f0f2f5")

    def set_on(self, is_on):
        if self._is_on == is_on:
            return
        self._is_on = is_on
        self.knob_pos_anim.setStartValue(self._knob_x_pos)
        self.knob_pos_anim.setEndValue(23 if self._is_on else 3)
        self.knob_pos_anim.start()
        self.toggled.emit(self._is_on)

    def is_on(self):
        return self._is_on

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_color = self.bg_color_on if self._is_on else self.bg_color_off
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

        painter.setBrush(QBrush(self.icon_color))
        moon_path = QPainterPath()
        moon_path.addEllipse(7, 7, 16, 16)
        moon_path.addEllipse(4, 7, 16, 16)
        painter.drawPath(moon_path)
        painter.drawEllipse(30, 10, 10, 10)
        for i in range(8):
            angle = i * 45
            x1 = 35 + 7 * math.cos(math.radians(angle))
            y1 = 15 + 7 * math.sin(math.radians(angle))
            x2 = 35 + 9 * math.cos(math.radians(angle))
            y2 = 15 + 9 * math.sin(math.radians(angle))
            painter.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))

        painter.setBrush(QBrush(self.knob_color))
        painter.drawEllipse(QPoint(self._knob_x_pos + 12, 15), 11, 11)

    def mousePressEvent(self, event):
        self.set_on(not self._is_on)
        super().mousePressEvent(event)

    def _get_knob_position(self):
        return self._knob_x_pos

    def _set_knob_position(self, pos):
        self._knob_x_pos = pos
        self.update()

    knob_position = Property(int, _get_knob_position, _set_knob_position)

class BackgroundWidget(QWidget):
    def __init__(self, image_path, opacity, parent=None):
        super().__init__(parent)
        self.bg_pixmap = QPixmap(image_path)
        self.opacity = opacity

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            painter.setOpacity(self.opacity)
            painter.drawPixmap(self.rect(), self.bg_pixmap)
        super().paintEvent(event)

class DraggableFrame(QFrame):
    visibilityChanged = Signal(bool)
    
    # --- MODIFIED: Added is_independent_window parameter ---
    def __init__(self, title, parent=None, is_independent_window=False):
        super().__init__(parent)
        
        # --- MODIFIED: Set window flag if it's an independent window ---
        if is_independent_window:
            # 使用 Qt.Dialog 标志，它是一个顶级窗口，但仍能保持与父窗口的关联。
            # Qt.FramelessWindowHint 移除原生边框。
            self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
            # 这一行非常重要，它确保了窗口在任务栏上没有自己的独立图标，
            # 感觉更像是主程序的“一部分”，而不是一个全新的程序。
            self.setWindowModality(Qt.NonModal)
        else:
            # 对于嵌入式窗口，确保它没有窗口标志，只是一个普通的Frame
            self.setWindowFlags(Qt.Widget)
        self.setFrameShape(QFrame.StyledPanel)

        self.setFrameShape(QFrame.StyledPanel)
        
        self.m_drag = False
        self.m_resize = False
        self.m_drag_position = QPoint()
        self.m_start_geometry = QRect()
        self.m_start_mouse_pos = QPoint()
        
        self.m_resizing_left = False
        self.m_resizing_right = False
        self.m_resizing_top = False
        self.m_resizing_bottom = False

        self.resize_margin = 8

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        title_bar_widget = QWidget()
        self.title_bar_layout = QHBoxLayout(title_bar_widget)
        self.title_bar_layout.setContentsMargins(8, 0, 4, 0)
        
        self.title_label = QLabel(title)
        
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(22, 22)
        
        self.title_bar_layout.addWidget(self.title_label)
        self.title_bar_layout.addStretch()
        self.title_bar_layout.addWidget(self.close_button)

        self.title_bar = QWidget()
        self.title_bar.setLayout(self.title_bar_layout)
        
        self.close_button.clicked.connect(self.hide)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)

        main_layout.addWidget(self.title_bar, 0)
        main_layout.addWidget(self.content_widget, 1)

        self.setMouseTracking(True)
        self.content_widget.setMouseTracking(True)
        self.title_bar.setMouseTracking(True)
    
    def setContentWidget(self, widget):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        self.content_layout.addWidget(widget)

    def setMinimumSizeFromContent(self):
        self.content_widget.adjustSize()
        content_hint = self.content_widget.sizeHint()
        title_bar_height = self.title_bar.sizeHint().height()
        frame_margins = self.layout().contentsMargins()
        min_w = (content_hint.width() + frame_margins.left() + frame_margins.right())*0.8
        min_h = (content_hint.height() + title_bar_height + frame_margins.top() + frame_margins.bottom())*0.8
        self.setMinimumSize(min_w, min_h)

    def showEvent(self, event):
        super().showEvent(event)
        self.visibilityChanged.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibilityChanged.emit(False)

    def mousePressEvent(self, event: QMouseEvent):
        self.raise_()
        
        if event.button() == Qt.LeftButton:
            self.m_start_geometry = self.geometry()
            self.m_start_mouse_pos = event.globalPosition().toPoint()
            
            if self.m_resizing_left or self.m_resizing_right or self.m_resizing_top or self.m_resizing_bottom:
                self.m_resize = True
                event.accept()
            elif self.title_bar.geometry().contains(event.position().toPoint()):
                if not self.close_button.geometry().contains(self.title_bar.mapFrom(self, event.position().toPoint())):
                    self.m_drag = True
                    self.m_drag_position = event.globalPosition().toPoint() - self.pos()
                    self.setCursor(Qt.ClosedHandCursor)
                    event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        
        if not self.m_resize and not self.m_drag:
            on_left = pos.x() >= 0 and pos.x() <= self.resize_margin
            on_right = pos.x() >= self.width() - self.resize_margin and pos.x() <= self.width()
            on_top = pos.y() >= 0 and pos.y() <= self.resize_margin
            on_bottom = pos.y() >= self.height() - self.resize_margin and pos.y() <= self.height()

            self.m_resizing_left = on_left
            self.m_resizing_right = on_right
            self.m_resizing_top = on_top
            self.m_resizing_bottom = on_bottom

            if (on_top and on_left) or (on_bottom and on_right):
                self.setCursor(Qt.SizeFDiagCursor)
            elif (on_top and on_right) or (on_bottom and on_left):
                self.setCursor(Qt.SizeBDiagCursor)
            elif on_left or on_right:
                self.setCursor(Qt.SizeHorCursor)
            elif on_top or on_bottom:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
                if self.title_bar.geometry().contains(pos):
                    self.setCursor(Qt.OpenHandCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)

        elif self.m_drag:
            self.move(event.globalPosition().toPoint() - self.m_drag_position)
            event.accept()
            
        elif self.m_resize:
            delta = event.globalPosition().toPoint() - self.m_start_mouse_pos
            new_geometry = QRect(self.m_start_geometry)

            if self.m_resizing_left:
                new_geometry.setLeft(self.m_start_geometry.left() + delta.x())
            if self.m_resizing_right:
                new_geometry.setRight(self.m_start_geometry.right() + delta.x())
            if self.m_resizing_top:
                new_geometry.setTop(self.m_start_geometry.top() + delta.y())
            if self.m_resizing_bottom:
                new_geometry.setBottom(self.m_start_geometry.bottom() + delta.y())

            min_width = self.minimumWidth()
            min_height = self.minimumHeight()
            
            if new_geometry.width() < min_width:
                if self.m_resizing_left:
                    new_geometry.setLeft(new_geometry.right() - min_width)
                else:
                    new_geometry.setWidth(min_width)
            if new_geometry.height() < min_height:
                if self.m_resizing_top:
                    new_geometry.setTop(new_geometry.bottom() - min_height)
                else:
                    new_geometry.setHeight(min_height)
            
            self.setGeometry(new_geometry)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.m_drag = False
        self.m_resize = False
        self.m_resizing_left = False
        self.m_resizing_right = False
        self.m_resizing_top = False
        self.m_resizing_bottom = False
        self.setCursor(Qt.ArrowCursor)
        event.accept()

# ... (The rest of the file remains unchanged) ...
class OverallHealthIndicator(QWidget):
    # ... (代码与之前版本完全相同)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(30)
        self._device_on = True
        self.text_color = QColor("#e1e1e6")

    def set_device_status(self, is_on):
        self._device_on = is_on
        self.update()

    def set_text_color(self, color):
        self.text_color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self._device_on:
            color = "#00ff7f"
            text = "系统正常"
        else:
            color = "#FFFFFF" if self.text_color.lightness() < 128 else "#5e626a"
            text = "系统关机"
            
        pen = QPen(QColor(color), 3)
        painter.setPen(pen)
        painter.drawEllipse(2, 6, 18, 18)
        
        brush = QBrush(QColor(color))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(5, 9, 12, 12)
        
        painter.setPen(QPen(self.text_color))
        font = QFont("Inter", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(30, 22, text)

class CommunicationStatusIndicator(QWidget):
    # ... (代码与之前版本完全相同)
    def __init__(self, name, online, total, speed, parent=None):
        super().__init__(parent)
        self.name = name
        self.total = total
        self.setMinimumWidth(80)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(name, self)
        self.count_label = QLabel(f"{online}/{total}", self)
        self.speed_label = QLabel(f"({speed}ms)", self)
        self.status_light = QLabel(self)
        self.status_light.setFixedSize(10, 10)
        
        self.name_label.setAlignment(Qt.AlignCenter)
        self.count_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.status_light, 0, Qt.AlignCenter)
        layout.addWidget(self.count_label)
        layout.addWidget(self.speed_label)

    def update_status(self, is_on):
        if is_on:
            self.status_light.setStyleSheet("background-color: #00ff7f; border-radius: 5px;")
            self.count_label.setText(f"{self.total}/{self.total}")
            self.speed_label.setText("(---ms)")
        else:
            self.status_light.setStyleSheet("background-color: #ff3b30; border-radius: 5px;")
            self.count_label.setText(f"0/{self.total}")
            self.speed_label.setText("(N/A)")

    def set_speed(self, speed_ms_str):
        self.speed_label.setText(f"({speed_ms_str}ms)")

class EnvironmentDisplay(QWidget):
    # ... (代码与之前版本完全相同)
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)
        self.title_label = QLabel(title, self)
        self.value_label = QLabel(value, self)
        
        self.title_label.setAlignment(Qt.AlignCenter)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d1ff;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
