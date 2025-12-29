# ui_chart_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

class RealTimeChartWidget(QWidget):
    # ... (代码与之前版本完全相同)
    def __init__(self, title, y_label, y_range, parent=None):
        super().__init__(parent)
        self.time_counter = 0
        self.time_window = 300
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        container = QWidget(self)
        main_layout.addWidget(container)
        
        self.chart_view = QChartView(container)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background-color: transparent; border: none;")
        
        self.title_label = QLabel(title, container)
        
        chart_layout = QVBoxLayout(container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.addWidget(self.chart_view)
        
        self.chart = QChart()
        self.chart.setBackgroundBrush(QBrush(QColor("transparent")))
        self.chart.legend().hide()
        self.chart.setMargins(QMargins(0,0,0,0))
        self.chart.layout().setContentsMargins(0,0,0,0)

        self.series = QLineSeries()
        pen = QPen(QColor("#00d1ff"))
        pen.setWidth(2)
        self.series.setPen(pen)
        self.chart.addSeries(self.series)
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.axis_x.setLabelFormat("%d s")
        self.axis_y.setTitleText(y_label)
        self.axis_x.setRange(0, self.time_window)
        self.axis_y.setRange(y_range[0], y_range[1])
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        self.chart_view.setChart(self.chart)

    def set_theme(self, text_color, title_bg_color):
        self.title_label.setStyleSheet(f"color: {text_color}; font-size: 16px; font-weight: 600; background-color: {title_bg_color}; padding: 5px 10px; border-radius: 5px;")
        self.title_label.adjustSize()
        
        axis_color = QColor(text_color)
        axis_color.setAlpha(180)
        self.axis_x.setLabelsColor(axis_color)
        self.axis_y.setLabelsColor(axis_color)
        self.axis_y.setTitleBrush(QBrush(axis_color))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.title_label.move(15, 15)

    def update_data(self, value):
        self.time_counter += 1
        self.series.append(self.time_counter, value)
        if self.time_counter > self.time_window:
            self.axis_x.setRange(self.time_counter - self.time_window, self.time_counter)
        if self.series.count() > self.time_window * 2:
            self.series.removePoints(0, self.series.count() - (self.time_window * 2))
