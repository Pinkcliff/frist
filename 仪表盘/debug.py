# debug.py
import datetime

# 调试模式开关，默认为打开
DEBUG_ENABLED = True

def log_debug(message: str):
    """
    如果调试模式开启，则向终端打印带有时间戳的调试信息。
    """
    if DEBUG_ENABLED:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp} DEBUG] {message}")
