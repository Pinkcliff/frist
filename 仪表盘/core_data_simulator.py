# core_data_simulator.py
from PySide6.QtCore import QObject, Signal, QTimer, QDateTime
import random

class DataSimulator(QObject):
    data_updated = Signal(float, float, float)
    comm_speed_updated = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step_value = 450.0
        self.device_on = False  # 新增设备状态标志，默认为关闭

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_data)
        
        self.comm_timer = QTimer(self)
        self.comm_timer.timeout.connect(self.check_communication_speed)

        # 定时器在初始化时就启动，并一直运行
        self.data_timer.start(1000)
        self.comm_timer.start(5000)

    def set_device_status(self, is_on: bool):
        """由主窗口调用，用于更新设备状态"""
        self.device_on = is_on
        # 如果设备刚刚被关闭，立即发送一次0值以重置图表
        if not self.device_on:
            self.data_updated.emit(0.0, 0.0, 0.0)

    def update_data(self):
        """根据设备状态发送数据"""
        if self.device_on:
            # 设备开启，发送模拟数据
            if random.random() < 0.2:
                self.current_step_value = 450 + random.uniform(-100, 100)
            current_val = self.current_step_value + random.uniform(-5, 5)
            voltage_val = 380.0 + random.uniform(-0.1, 0.1)
            power_val = current_val * voltage_val * 1.732 / 1000
            self.data_updated.emit(current_val, voltage_val, power_val)
        else:
            # 设备关闭，持续发送0值（或者可以选择不发送）
            # 持续发送0可以确保图表在关机状态下保持为0
            self.data_updated.emit(0.0, 0.0, 0.0)

    def check_communication_speed(self):
        """通讯速度检查只在设备开启时有意义"""
        if self.device_on:
            speed_val = random.uniform(3.0, 5.0)
            speed_str = f"{speed_val:.3f}"
            self.comm_speed_updated.emit("all", speed_str)
