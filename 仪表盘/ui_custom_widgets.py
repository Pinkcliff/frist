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

    def __init__(self, title, parent=None, is_independent_window=False):
        super().__init__(parent)

        self._is_independent_window = is_independent_window
        self._original_geometry = None
        self._visible_before_hide = False

        # 设置为普通Widget，嵌入在父窗口中
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
        """当dock显示时，发射可见性改变信号并标记为可见"""
        super().showEvent(event)
        self.visibilityChanged.emit(True)
        self._visible_before_hide = True

    def hideEvent(self, event):
        """当dock被隐藏时，发射可见性改变信号"""
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

class OverallHealthIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self._device_on = True
        self.text_color = QColor("#e1e1e6")

        # 初始化子系统状态：风机、造雨、示踪、动捕
        # 状态：0=待机(黄色), 1=运行(绿色), 2=故障(红色)
        self.subsystem_status = {
            "风机": 0,
            "造雨": 0,
            "示踪": 0,
            "动捕": 0
        }

    def set_device_status(self, is_on):
        self._device_on = is_on
        self.update()

    def set_subsystem_status(self, subsystem, status):
        """设置子系统状态
        Args:
            subsystem: 子系统名称 (风机/造雨/示踪/动捕)
            status: 0=待机(黄色), 1=运行(绿色), 2=故障(红色)
        """
        if subsystem in self.subsystem_status:
            self.subsystem_status[subsystem] = status
            self.update()

    def set_text_color(self, color):
        self.text_color = QColor(color)
        self.update()

    def _get_status_color(self, status):
        """获取状态对应的颜色"""
        if status == 0:
            return "#FFFF00"  # 黄色 - 待机
        elif status == 1:
            return "#00FF00"  # 绿色 - 运行
        else:
            return "#FF0000"  # 红色 - 故障

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 主系统状态显示
        if self._device_on:
            color = "#00ff7f"
            text = "系统开机"
        else:
            color = "#FFFFFF" if self.text_color.lightness() < 128 else "#5e626a"
            text = "系统待机"

        # 绘制主状态指示灯
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

        # 绘制底部分隔线
        painter.setPen(QPen(QColor("#404448"), 1))
        painter.drawLine(10, 35, self.width() - 10, 35)

        # 绘制底部子系统状态
        subsystem_start_y = 45
        subsystem_spacing = 50
        start_x = 10

        for i, (name, status) in enumerate(self.subsystem_status.items()):
            x = start_x + i * subsystem_spacing

            # 绘制子系统状态灯（绿红黄）
            status_color = self._get_status_color(status)

            # 外圈
            painter.setPen(QPen(QColor(status_color), 2))
            painter.drawEllipse(x, subsystem_start_y, 14, 14)

            # 内圈实心
            painter.setBrush(QBrush(QColor(status_color)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x + 3, subsystem_start_y + 3, 8, 8)

            # 绘制名称
            painter.setPen(QPen(self.text_color))
            font = QFont("Inter", 9)
            painter.setFont(font)
            painter.drawText(x - 5, subsystem_start_y + 28, name)

class CommunicationStatusIndicator(QWidget):
    def __init__(self, name, online, total, speed, parent=None):
        super().__init__(parent)
        self.name = name
        self.total = total
        self.setMinimumWidth(80)
        self.setMinimumHeight(90)
        self.setMouseTracking(True)  # 启用鼠标追踪以支持悬停事件
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(name, self)
        self.count_label = QLabel(f"{online}/{total}", self)
        self.speed_label = QLabel(f"({speed}ms)", self)
        self.status_light = QLabel(self)
        self.status_light.setFixedSize(10, 10)

        # 问题部件编号标签
        self.issue_label = QLabel("", self)
        self.issue_label.setStyleSheet("color: #ff6b6b; font-size: 9px;")
        self.issue_label.setAlignment(Qt.AlignCenter)

        self.name_label.setAlignment(Qt.AlignCenter)
        self.count_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.name_label)
        layout.addWidget(self.status_light, 0, Qt.AlignCenter)
        layout.addWidget(self.count_label)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.issue_label)

        # 存储有问题的部件编号
        self.problematic_units = []

    def update_status(self, is_on):
        if is_on:
            self.status_light.setStyleSheet("background-color: #00ff7f; border-radius: 5px;")
            self.count_label.setText(f"{self.total}/{self.total}")
            self.speed_label.setText("(---ms)")
            self.issue_label.setText("")
            self.problematic_units = []
        else:
            self.status_light.setStyleSheet("background-color: #ff3b30; border-radius: 5px;")
            self.count_label.setText(f"0/{self.total}")
            self.speed_label.setText("(N/A)")
            # 模拟随机问题部件（仅用于演示）
            import random
            if self.name == "电驱":
                num_issues = random.randint(1, 5)
                self.problematic_units = random.sample(range(100), num_issues)
                self.issue_label.setText(f"问题: {len(self.problematic_units)}个")

    def set_problematic_units(self, unit_list):
        """设置有问题的部件编号列表"""
        self.problematic_units = unit_list
        if unit_list:
            self.issue_label.setText(f"问题: {len(unit_list)}个")
        else:
            self.issue_label.setText("")

    def set_speed(self, speed_ms_str):
        self.speed_label.setText(f"({speed_ms_str}ms)")

    def mouseMoveEvent(self, event):
        """鼠标悬停时显示弹窗"""
        if self.problematic_units:
            from PySide6.QtWidgets import QToolTip
            tooltip_text = f"{self.name} - 问题部件编号:\n" + ", ".join(map(str, self.problematic_units))
            QToolTip.showText(event.globalPosition().toPoint(), tooltip_text, self)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """鼠标离开时隐藏弹窗"""
        from PySide6.QtWidgets import QToolTip
        QToolTip.hideText()
        super().leaveEvent(event)

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
