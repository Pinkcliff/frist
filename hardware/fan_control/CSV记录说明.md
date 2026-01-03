# PWM值CSV记录功能说明

## 功能概述

已成功实现将1600个风扇（100个板子 × 16个风扇）的PWM设置值每隔0.1秒写入CSV文件的功能。

## 创建的文件

### 1. pwm_csv_recorder.py - CSV记录器核心模块
```python
from hardware.fan_control.pwm_csv_recorder import (
    PWMCSVRecorder,
    PWMRecorderWithController,
    create_demo_csv_recording
)
```

**主要类和功能**：
- `PWMCSVRecorder` - 核心记录器类
- `PWMRecorderWithController` - 带批量控制器集成的记录器
- `create_demo_csv_recording()` - 快速演示函数

### 2. test_pwm_csv_recorder.py - 测试脚本
提供5种测试场景：
1. 基础PWM值记录（10个板子，5秒）
2. 100个板子PWM值记录（1600个风扇，10秒）
3. 与批量控制器集成（10个板子，3秒）
4. 不同的PWM模式（5个板子）
5. 快速演示（100个板子，3秒）

## 生成的CSV文件

### 文件示例
```
F:\A-User\cliff\frist\frist\hardware\fan_control\csv_files\pwm_values_20260103_205013.csv
```

### 文件规格
- **文件大小**: 651,062 字节 (约636 KB)
- **记录时长**: 10秒
- **记录行数**: 98行数据 + 1行表头
- **记录间隔**: 0.1秒
- **实际间隔**: 0.1024秒
- **总数据点**: 98 × 1600 = 156,800个PWM值

### CSV文件格式

#### 列结构
```
timestamp,elapsed_time,Board001_Fan01,Board001_Fan02,...,Board001_Fan16,Board002_Fan01,...,Board100_Fan16
```

- **第1列**: 时间戳 (格式: YYYY-MM-DD HH:MM:SS.mmm)
- **第2列**: 经过时间（秒，精确到毫秒）
- **第3-1602列**: 1600个风扇的PWM值
  - Board001_Fan01 到 Board001_Fan16 (板子1的16个风扇)
  - Board002_Fan01 到 Board002_Fan16 (板子2的16个风扇)
  - ...
  - Board100_Fan01 到 Board100_Fan16 (板子100的16个风扇)

#### 数据示例
```csv
timestamp,elapsed_time,Board001_Fan01,Board001_Fan02,Board001_Fan03,...
2026-01-03 20:50:13.174,0.000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,...
2026-01-03 20:50:13.279,0.105,579,757,872,896,823,670,476,288,151,...
2026-01-03 20:50:13.385,0.211,744,888,886,789,622,424,245,128,102,...
```

## 使用方法

### 方法1: 快速演示
```python
from hardware.fan_control.pwm_csv_recording import create_demo_csv_recording

# 生成10秒的演示数据
csv_file = create_demo_csv_recording(
    duration=10.0,   # 记录时长（秒）
    interval=0.1,    # 记录间隔（秒）
    board_count=100  # 板子数量
)
```

### 方法2: 使用记录器类
```python
from hardware.fan_control.pwm_csv_recorder import PWMCSVRecorder

# 创建记录器
recorder = PWMCSVRecorder(
    board_count=100,      # 100个板子
    fans_per_board=16,    # 每个板子16个风扇
    interval=0.1          # 每0.1秒记录一次
)

# 开始记录
recorder.start_recording()

# 设置PWM值
pwm_values = [500] * 1600  # 所有风扇设置为500
recorder.set_pwm_values(pwm_values)

# 或者设置单个板子的PWM值
board_pwm = [100, 200, 300, ..., 1000]  # 16个风扇的PWM值
recorder.set_board_pwm(board_index=0, pwm_values=board_pwm)

# 停止记录
recorder.stop_recording()
```

### 方法3: 与批量控制器集成
```python
from hardware.fan_control import create_batch_controller
from hardware.fan_control.pwm_csv_recorder import PWMRecorderWithController

# 创建批量控制器
batch_ctrl = create_batch_controller(
    board_count=100,
    base_ip="192.168.2.",
    start_ip=1,
    fans_per_board=16
)

# 创建带控制器的记录器
recorder = PWMRecorderWithController(
    batch_controller=batch_ctrl,
    interval=0.1
)

# 开始记录
recorder.start_recording()

# 设置所有风扇为相同PWM值
recorder.set_all_fans_pwm(500)

# 或者设置渐变PWM值
recorder.set_gradient_pwm()

# 或者设置波浪式PWM值（随时间变化）
import time
t = 0
while True:
    recorder.set_wave_pwm(t)
    time.sleep(0.1)
    t += 0.1

# 停止记录
recorder.stop_recording()
```

## 运行测试

```bash
# 运行测试脚本
cd F:\A-User\cliff\frist\frist\hardware\fan_control
python test_pwm_csv_recorder.py
```

选择测试选项：
- 选项1: 基础测试（快速）
- 选项2: 100板子完整测试（推荐）
- 选项3: 控制器集成测试
- 选项4: 不同PWM模式测试
- 选项5: 快速演示

## 特性

### 1. 高精度时间记录
- 时间戳精确到毫秒
- 经过时间记录，便于分析数据变化

### 2. 灵活的PWM设置
- `set_pwm_values()` - 一次设置所有1600个风扇
- `set_board_pwm()` - 设置单个板子的16个风扇
- `set_all_fans_pwm()` - 设置所有风扇为相同值
- `set_gradient_pwm()` - 渐变模式
- `set_wave_pwm()` - 波浪模式（随时间变化）

### 3. 后台线程记录
- 使用独立线程进行记录，不影响主程序
- 支持启动/停止控制
- 线程安全的数据更新

### 4. 完整的统计信息
记录结束时显示：
- CSV文件路径
- 记录行数
- 记录时长
- 实际记录间隔
- 文件大小

## 实际应用场景

### 场景1: 风扇控制日志记录
```python
recorder = PWMCSVRecorder(board_count=100, fans_per_board=16, interval=0.1)
recorder.start_recording()

# 在控制风扇的同时记录PWM值
while True:
    # 从控制器读取当前PWM值
    current_pwm = read_pwm_from_controller()
    recorder.set_pwm_values(current_pwm)
    time.sleep(0.1)
```

### 场景2: PWM模式测试
```python
recorder = PWMCSVRecorder(board_count=100, fans_per_board=16, interval=0.1)
recorder.start_recording()

# 测试不同的PWM模式
for mode in ['constant', 'gradient', 'wave', 'random']:
    if mode == 'constant':
        recorder.set_all_fans_pwm(500)
    elif mode == 'gradient':
        recorder.set_gradient_pwm()
    elif mode == 'wave':
        for t in range(100):
            recorder.set_wave_pwm(t * 0.1)
            time.sleep(0.1)
    time.sleep(5)

recorder.stop_recording()
```

### 场景3: 性能监控
```python
# 记录10分钟的数据
recorder = PWMCSVRecorder(board_count=100, fans_per_board=16, interval=0.1)
recorder.start_recording()

start_time = time.time()
while time.time() - start_time < 600:  # 10分钟
    # 记录当前PWM值
    pwm_values = get_current_pwm_values()
    recorder.set_pwm_values(pwm_values)
    time.sleep(0.1)

recorder.stop_recording()
```

## 数据分析

### 用Excel打开
1. 打开Excel
2. 文件 → 打开 → 选择CSV文件
3. 可以看到1600个风扇的PWM值随时间变化

### 用Python分析
```python
import pandas as pd
import matplotlib.pyplot as plt

# 读取CSV文件
df = pd.read_csv('pwm_values_20260103_205013.csv')

# 查看数据
print(df.head())

# 绘制某个风扇的PWM变化
plt.figure(figsize=(12, 6))
plt.plot(df['elapsed_time'], df['Board001_Fan01'])
plt.xlabel('Time (s)')
plt.ylabel('PWM Value')
plt.title('Fan PWM Over Time')
plt.grid(True)
plt.show()

# 统计分析
print(df.describe())
```

## 文件位置

- **核心模块**: `hardware/fan_control/pwm_csv_recorder.py`
- **测试脚本**: `hardware/fan_control/test_pwm_csv_recorder.py`
- **CSV文件目录**: `hardware/fan_control/csv_files/`
- **示例CSV文件**: `hardware/fan_control/csv_files/pwm_values_20260103_205013.csv`

## 总结

✅ 成功实现1600个风扇的PWM值记录功能
✅ 每0.1秒自动写入CSV文件
✅ 支持多种PWM设置模式
✅ 完整的时间戳和经过时间记录
✅ 可与批量控制器集成使用
✅ 提供完整的测试和演示脚本
✅ 生成的CSV文件可用Excel或其他工具打开分析

现在您可以轻松记录所有1600个风扇的PWM值变化情况，便于后续分析和监控！
