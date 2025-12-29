# wind_wall_simulator/simulation_interface.py

from PySide6.QtCore import QObject, Signal, QThread
import numpy as np
import time

class SimulationWorker(QObject):
    """A worker that runs the simulation in a separate thread."""
    finished = Signal()
    progress = Signal(str)

    def __init__(self, grid_data: np.ndarray):
        super().__init__()
        self.grid_data = grid_data

    def run(self):
        """Starts the simulation process."""
        self.progress.emit("仿真任务开始... 正在准备数据。")
        print("--- Simulation Started ---")
        print(f"Data shape: {self.grid_data.shape}")
        print(f"Max value: {self.grid_data.max():.2f}%, Min value: {self.grid_data.min():.2f}%")
        
        # Simulate a long-running task
        time.sleep(2) 
        self.progress.emit("网格生成 (Gmsh)...")
        time.sleep(3)
        self.progress.emit("流场计算 (VTK/Solver)...")
        time.sleep(5)

        print("--- Simulation Finished ---")
        self.progress.emit("仿真完成！")
        self.finished.emit()

def run_simulation(grid_data: np.ndarray, main_window) -> QThread:
    """
    Sets up and starts the simulation in a new thread.
    Returns the thread object.
    """
    thread = QThread()
    worker = SimulationWorker(grid_data)
    worker.moveToThread(thread)

    # Connect signals
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    
    # Connect worker signals to main window slots for UI updates
    worker.progress.connect(main_window.update_statusbar_message)
    worker.finished.connect(main_window.on_simulation_finished)

    thread.start()
    return thread
