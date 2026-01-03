# 单元测试套件

本测试套件用于测试项目的各个模块功能。

## 测试文件说明

### test_dashboard.py
测试仪表盘模块功能：
- DataSimulator 数据模拟器初始化
- 设备状态切换（开/关）
- 数据更新信号发送
- 主题管理器导入
- 图表组件导入

### test_wind_config.py
测试风场设置模块配置：
- 网格尺寸参数验证
- 画布尺寸计算
- 应用信息
- 颜色映射生成（256色）
- 颜色插值函数
- 颜色分布验证（蓝→绿→黄→红）

### test_cfd_config.py
测试CFD前处理模块配置：
- 计算域参数（边界、入口/出口长度）
- 计算域边界计算
- 风扇墙尺寸计算
- 风扇几何参数（宽度、厚度、孔径、轮毂直径）
- 风扇阵列形状
- 网格参数（组件网格、环境网格、拉伸比）
- 风扇运行参数（转速、方向、PQ曲线）
- 物理约束和合理性检查

### test_utils.py
测试工具函数：
- 值到颜色转换（value_to_color）
- 值裁剪功能
- 颜色转换一致性
- 对比度文本颜色计算
- 网格坐标生成（拉伸网格）
- 拉伸效果验证
- 终点精度验证

## 运行测试

### 方法1：使用测试运行脚本
```bash
# 使用conda环境my_env运行所有测试
conda run -n my_env python tests/run_tests.py

# 运行特定测试模块
conda run -n my_env python tests/run_tests.py --module test_dashboard

# 列出所有可用的测试模块
conda run -n my_env python tests/run_tests.py --list
```

### 方法2：直接使用unittest
```bash
# 运行所有测试
conda run -n my_env python -m unittest discover -s tests -p "test_*.py"

# 运行特定测试文件
conda run -n my_env python -m unittest tests.test_dashboard

# 运行特定测试类
conda run -n my_env python -m unittest tests.test_dashboard.TestDataSimulator

# 运行特定测试方法
conda run -n my_env python -m unittest tests.test_dashboard.TestDataSimulator.test_simulator_initialization
```

### 方法3：直接运行测试文件
```bash
conda run -n my_env python tests/test_dashboard.py
```

## 依赖要求

测试需要以下依赖：
- Python 3.7+
- PySide6
- NumPy

## 注意事项

1. 某些测试需要PySide6环境，如果导入失败会自动跳过
2. GUI相关测试可能需要显示环境
3. 确保conda环境my_env已正确配置所有依赖
