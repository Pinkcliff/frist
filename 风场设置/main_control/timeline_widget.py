# timeline_widget.py
# 时间条控件的实现

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon

class TimelineWidget(QWidget):
    """时间条控件，包含播放控制和时间轴"""

    # 信号
    time_changed = Signal(float)  # 时间改变信号
    play_state_changed = Signal(bool)  # 播放状态改变信号
    playback_finished = Signal()  # 播放完成信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_time = 10.0  # 最大时间（秒）
        self.time_resolution = 0.1  # 时间分辨率（秒）
        self.current_time = 0.0  # 当前时间
        self.is_playing = False  # 是否正在播放
        self.auto_reset = True  # 播放完成后自动重置

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)

        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """设置UI布局 (修正版)"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        
        # 创建控件
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(30, 30)
        self.play_button.setToolTip("播放/暂停")
        
        self.stop_button = QPushButton("⏹")
        self.stop_button.setFixedSize(30, 30)
        self.stop_button.setToolTip("停止")
        
        self.time_label = QLabel("0.0 / 10.0 s")
        self.time_label.setMinimumWidth(100)
        
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(int(self.max_time / self.time_resolution))
        self.time_slider.setValue(0)
        self.time_slider.setToolTip("拖动设置时间")

        # 【核心】将创建的控件添加到布局中
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.time_slider)
        layout.addWidget(self.time_label)



        
    def _connect_signals(self):
        """连接信号"""
        self.play_button.clicked.connect(self._toggle_play)
        self.stop_button.clicked.connect(self._stop)
        self.time_slider.valueChanged.connect(self._slider_changed)
        
    def _toggle_play(self):
        """切换播放/暂停状态"""
        if self.is_playing:
            self._pause()
        else:
            self._play()
            
    def _play(self):
        """开始播放"""
        self.is_playing = True
        self.play_button.setText("⏸")
        self.play_button.setToolTip("暂停")
        
        # 设置定时器间隔（毫秒）
        interval = int(self.time_resolution * 1000)
        self.timer.start(interval)
        
        self.play_state_changed.emit(True)
        
    def _pause(self):
        """暂停播放"""
        self.is_playing = False
        self.play_button.setText("▶")
        self.play_button.setToolTip("播放")
        self.timer.stop()
        
        self.play_state_changed.emit(False)
        
    def _stop(self):
        """停止播放并重置到开始"""
        self._pause()
        self.current_time = 0.0
        self.time_slider.setValue(0)
        self._update_time_display()
        self.time_changed.emit(self.current_time)
        
    def _update_time(self):
        """更新时间（定时器回调）"""
        self.current_time += self.time_resolution

        if self.current_time >= self.max_time:
            # 到达最大时间，停止播放
            self.current_time = self.max_time
            self._pause()

            # 发送播放完成信号
            self.playback_finished.emit()

            # 自动重置到开始位置
            if self.auto_reset:
                self._reset_to_start()
                return

        # 更新滑块位置
        slider_value = int(self.current_time / self.time_resolution)
        self.time_slider.setValue(slider_value)

        self._update_time_display()
        self.time_changed.emit(self.current_time)

    def _reset_to_start(self):
        """重置到开始位置"""
        self.current_time = 0.0
        self.time_slider.setValue(0)
        self._update_time_display()
        self.time_changed.emit(self.current_time)
        
    def _slider_changed(self, value):
        """滑块值改变"""
        self.current_time = value * self.time_resolution
        self._update_time_display()
        self.time_changed.emit(self.current_time)
        
    def _update_time_display(self):
        """更新时间显示"""
        self.time_label.setText(f"{self.current_time:.1f} / {self.max_time:.1f} s")
        
    def set_max_time(self, max_time):
        """设置最大时间"""
        self.max_time = max_time
        self.time_slider.setMaximum(int(self.max_time / self.time_resolution))
        # self.max_time_label.setText(f"{self.max_time}s")
        
        # 如果当前时间超过新的最大时间，重置
        if self.current_time > self.max_time:
            self.current_time = 0.0
            self.time_slider.setValue(0)
            
        self._update_time_display()
        
    def set_time_resolution(self, resolution):
        """设置时间分辨率"""
        self.time_resolution = resolution
        self.time_slider.setMaximum(int(self.max_time / self.time_resolution))
        
        # 重新设置定时器间隔
        if self.is_playing:
            interval = int(self.time_resolution * 1000)
            self.timer.start(interval)
            
    def get_current_time(self):
        """获取当前时间"""
        return self.current_time
        
    def set_current_time(self, time):
        """设置当前时间"""
        self.current_time = max(0.0, min(time, self.max_time))
        slider_value = int(self.current_time / self.time_resolution)
        self.time_slider.setValue(slider_value)
        self._update_time_display()
        self.time_changed.emit(self.current_time)