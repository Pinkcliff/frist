# 风扇控制模块

基于Modbus RTU协议的风扇速度控制系统。

## 功能特点

- ✅ 支持Modbus RTU/TCP协议通信
- ✅ 单风扇/多风扇速度控制
- ✅ 风场数据到风扇速度的智能编码
- ✅ 预定义的编码器和配置模板
- ✅ 错误处理和自动重连机制
- ✅ 统计信息收集
- ✅ 上下文管理器支持

## 安装

```bash
pip install numpy PySide6
```

## 快速开始

### 1. 基础控制

```python
from hardware.fan_control import ModbusFanController, FanConfig

# 创建配置
config = FanConfig(device_ip="192.168.2.1")

# 创建控制器
with ModbusFanController(config) as controller:
    # 设置所有风扇为50%
    controller.set_all_fans_speed(50.0)

    # 设置单个风扇
    controller.set_fan_speed(0, 75.0)  # 风扇1设置为75%

    # 停止所有风扇
    controller.stop_all_fans()
```

### 2. 快速控制

```python
from hardware.fan_control import quick_control_all_fans

# 快速设置所有风扇
quick_control_all_fans(50.0, device_ip="192.168.2.1")
```

### 3. 风场数据集成

```python
import numpy as np
from hardware.fan_control import FanSpeedEncoder, ModbusFanController, FanConfig

# 创建40x40的风场数据
grid_data = np.random.rand(40, 40) * 100

# 编码为风扇速度（4x4布局）
encoder = FanSpeedEncoder()
fan_speeds = encoder.encode_grid_to_fans(grid_data)

# 发送到控制器
config = FanConfig(device_ip="192.168.2.1", fan_count=16)
with ModbusFanController(config) as controller:
    controller.set_fans_speed_individual(fan_speeds)
```

## 模块说明

### config.py - 配置管理

定义风扇控制的所有配置参数：

```python
from hardware.fan_control import FanConfig

# 自定义配置
config = FanConfig(
    device_ip="192.168.2.1",    # 设备IP
    device_port=8234,           # Modbus端口
    slave_addr=1,               # 从站地址
    fan_count=16,               # 风扇数量
    start_register=0,           # 起始寄存器
    pwm_min=0,                  # 最小PWM
    pwm_max=1000,               # 最大PWM
    timeout=5.0,                # 超时时间
)
```

### modbus_fan.py - Modbus控制器

核心风扇控制类：

```python
from hardware.fan_control import ModbusFanController, FanConfig

config = FanConfig()
controller = ModbusFanController(config)

# 连接
controller.connect()

# 控制方法
controller.set_fan_speed(0, 50.0)              # 设置单个风扇
controller.set_all_fans_speed(75.0)             # 设置所有风扇
controller.set_fans_speed_individual([0, 25, 50, ...])  # 分别设置
controller.set_fans_speed_dict({0: 50, 5: 75})  # 字典设置
controller.stop_all_fans()                      # 停止所有
controller.set_all_fans_max()                   # 最大速度

# 获取统计
controller.print_statistics()
stats = controller.get_statistics()

# 断开连接
controller.disconnect()
```

### fan_encoder.py - 风扇编码器

将风场数据编码为风扇速度：

```python
from hardware.fan_control import FanSpeedEncoder, FanMapping
import numpy as np

# 创建编码器
mapping = FanMapping(rows=4, cols=4)
encoder = FanSpeedEncoder(mapping)

# 编码风场数据
grid_data = np.ones((40, 40)) * 50
fan_speeds = encoder.encode_grid_to_fans(grid_data)

# 生成预设模式
speeds = encoder.create_gradient_pattern('diagonal', 0, 100)
speeds = encoder.create_radial_pattern(center_speed=100, edge_speed=0)
speeds = encoder.create_wave_pattern(time=0.0)
```

## 预定义配置

```python
from hardware.fan_control import PredefinedConfigs, PresetEncoders

# 使用预定义配置
config = PredefinedConfigs.SINGLE_BOARD_16_FANS
config = PredefinedConfigs.SINGLE_BOARD_32_FANS

# 使用预定义编码器
encoder = PresetEncoders.STANDARD_4X4
encoder = PresetEncoders.HIGH_RESPONSE_4X4
encoder = PresetEncoders.STANDARD_8X4
encoder = PresetEncoders.STANDARD_4X8
```

## 高级用法

### 1. 分区编码

```python
from hardware.fan_control import AdvancedFanEncoder, FanMapping

encoder = AdvancedFanEncoder(FanMapping(rows=4, cols=4))

# 定义区域
zones = {
    'center': ((1, 3, 1, 3), 1.5),    # 中心区域1.5倍速度
    'edge': ((0, 4, 0, 1), 0.5),      # 边缘区域0.5倍速度
}

grid_data = np.ones((40, 40)) * 50
speeds = encoder.encode_with_zones(grid_data, zones)
```

### 2. 动画效果

```python
import time

encoder = PresetEncoders.STANDARD_4X4
config = FanConfig(device_ip="192.168.2.1")

with ModbusFanController(config) as controller:
    # 播放波浪动画
    for t in range(50):
        speeds = encoder.create_wave_pattern(time=t * 0.1)
        controller.set_fans_speed_individual(speeds)
        time.sleep(0.1)
```

### 3. 多板控制

```python
boards = [
    FanConfig(device_ip="192.168.2.1", fan_count=16),
    FanConfig(device_ip="192.168.2.2", fan_count=16),
]

for config in boards:
    with ModbusFanController(config) as controller:
        controller.set_all_fans_speed(75.0)
```

## API参考

### ModbusFanController

| 方法 | 说明 |
|------|------|
| `connect()` | 连接到设备 |
| `disconnect()` | 断开连接 |
| `set_fan_speed(index, speed)` | 设置单个风扇速度 |
| `set_all_fans_speed(speed)` | 设置所有风扇速度 |
| `set_fans_speed_individual(speeds)` | 分别设置每个风扇 |
| `set_fans_speed_dict(speed_dict)` | 通过字典设置风扇 |
| `stop_all_fans()` | 停止所有风扇 |
| `set_all_fans_max()` | 设置所有风扇最大速度 |
| `get_statistics()` | 获取统计信息 |
| `print_statistics()` | 打印统计信息 |

### FanSpeedEncoder

| 方法 | 说明 |
|------|------|
| `encode_grid_to_fans(grid_data)` | 编码网格数据为风扇速度 |
| `create_gradient_pattern(direction, start, end)` | 创建渐变模式 |
| `create_radial_pattern(center, ...)` | 创建径向模式 |
| `create_wave_pattern(time, ...)` | 创建波浪模式 |

### 快捷函数

| 函数 | 说明 |
|------|------|
| `quick_control_fan(index, speed, ip)` | 快速控制单个风扇 |
| `quick_control_all_fans(speed, ip)` | 快速控制所有风扇 |

## 错误处理

```python
from hardware.fan_control import ModbusFanController, FanConfig

config = FanConfig(
    device_ip="192.168.2.1",
    timeout=5.0,
    reconnect_attempts=3,
    reconnect_delay=2.0,
)

controller = ModbusFanController(config)

if controller.connect():
    try:
        controller.set_all_fans_speed(50.0)
    except Exception as e:
        print(f"控制失败: {e}")
    finally:
        controller.disconnect()
else:
    print("连接失败")
```

## 测试

运行单元测试：

```bash
cd hardware/fan_control
python test_fan_control.py
```

运行示例程序：

```bash
python examples.py
```

## 硬件连接

### Modbus寄存器映射

| 风扇编号 | 寄存器地址 | 数据范围 |
|----------|------------|----------|
| 风扇1    | 0x0000     | 0-1000   |
| 风扇2    | 0x0001     | 0-1000   |
| ...      | ...        | ...      |
| 风扇16   | 0x000F     | 0-1000   |

### PWM值映射

- 0 = 0% (停止)
- 500 = 50% (中速)
- 1000 = 100% (全速)

## 注意事项

1. **IP地址**: 确保风扇控制器IP配置正确
2. **端口**: 默认Modbus TCP端口为8234
3. **从站地址**: 默认为1，根据设备调整
4. **超时设置**: 网络不稳定时增加超时时间
5. **重连机制**: 连接断开会自动尝试重连

## 性能建议

- 使用批量操作（`set_fans_speed_individual`）而非单个设置
- 合理设置超时时间（推荐2-5秒）
- 使用上下文管理器确保连接正确关闭
- 定期检查统计信息监控系统健康状态

## 许可证

MIT License

## 作者

Wind Field Hardware Team

## 更新日志

### v1.0.0 (2026-01-03)
- 初始版本发布
- 支持Modbus RTU协议
- 实现风扇速度控制
- 添加风场数据编码功能
- 提供预定义配置和编码器
