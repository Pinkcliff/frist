# fan_con 项目学习总结

## 项目概述

`fan_con` 是一个**动态表面分析系统**，用于分析和可视化 `z = f(x, y, t)` 形式的动态曲面函数。

## 核心架构

### 1. 文件结构

```
fan_con/
├── src/
│   ├── config.py              # 预定义波形函数
│   ├── dynamic_surface.py     # 动态表面类
│   ├── dynamic_surface_grid.py # 网格化动态表面
│   ├── point_analyzer.py      # 点分析器
│   ├── main.py                # 主程序
│   ├── interactive_demo.py    # 交互演示
│   └── gui_*.py               # 多个GUI版本
├── tests/
├── docs/
└── *.py                       # 演示文件
```

### 2. 核心类

| 类名 | 功能 | 文件 |
|------|------|------|
| `DynamicSurface` | 动态曲面分析工具 | `dynamic_surface.py` |
| `DynamicSurfaceGrid` | 网格化动态表面 | `dynamic_surface_grid.py` |
| `PointAnalyzer` | 固定点分析器 | `point_analyzer.py` |
| `OptimizedGUI` | 优化版GUI | `gui_optimized.py` |

## 数学函数库

### 基础波形 (config.py)

| 函数名 | 描述 | 公式 |
|--------|------|------|
| `simple_wave` | 简单波动 | `sin(x + t) * cos(y - t)` |
| `radial_wave` | 径向扩散波 | `sin(√(x² + y²) - 2t) * exp(-0.1t)` |
| `gaussian_wave_packet` | 高斯波包 | 沿轨道移动的高斯分布 |
| `standing_wave` | 二维驻波 | `sin(x) * sin(y) * cos(2t)` |
| `spiral_wave` | 螺旋波 | 带角度和径向衰减 |
| `interference_pattern` | 干涉图样 | 双波源叠加 |
| `soliton` | 孤立子 | 孤立波解 |

### 扩展函数 (gui_optimized.py)

| 函数名 | 描述 | 应用场景 |
|--------|------|----------|
| `linear_gradient` | 线性渐变 | `0.5 * (x + y) * sin(t)` |
| `radial_gradient` | 径向渐变 | `(r / 5) * cos(t + r)` |
| `checkerboard` | 棋盘格模式 | 周期性网格 |
| `noise_field` | 噪声场 | 随机扰动 |
| `polynomial_surface` | 多项式曲面 | `(x³ - 3xy²) / 10` |
| `saddle_point` | 鞍形点 | `(x² - y²) / 5` |

## 核心功能

### 1. DynamicSurface 类

```python
class DynamicSurface:
    """动态曲面分析工具"""

    def evaluate_surface(x_range, y_range, t, resolution=50)
    # 在给定时间t计算曲面值

    def get_time_series_at_point(x0, y0, t_range, num_points=100)
    # 获取固定点的时间序列

    def plot_surface_at_time(x_range, y_range, t, save_path=None)
    # 绘制特定时刻的曲面

    def interactive_surface_with_slider(x_range, y_range, t_range)
    # 带时间滑块的交互式曲面

    def create_animation(x_range, y_range, t_range, frames=50)
    # 创建曲面动画
```

### 2. DynamicSurfaceGrid 类

```python
class DynamicSurfaceGrid:
    """网格化动态表面 - 更适合风场编辑"""

    def __init__(x_range, y_range, divisions=20)
    # 初始化网格

    def calculate_z_values(t, function_type, **kwargs)
    # 计算网格点的z值

    def get_point_time_series(x_idx, y_idx, time_points)
    # 获取点的时间序列

    def plot_surface(Z, title)
    # 绘制3D表面

    def animate_surface(function_type, duration, fps, **kwargs)
    # 创建动画
```

**关键方法：**

```python
# 12种预定义函数类型
'wave'              # 基础波浪
'ripple'            # 涟漪（多源）
'interference'      # 干涉图案
'gaussian'          # 高斯脉冲
'linear_gradient'   # 线性渐变
'circular_gradient' # 圆形渐变
'radial_gradient'   # 径向渐变
'spiral_wave'       # 螺旋波
'checkerboard'      # 棋盘格
'noise_field'       # 噪声场
'polynomial_surface'# 多项式曲面
'wedge_pattern'     # 楔形图案
```

### 3. PointAnalyzer 类

```python
class PointAnalyzer:
    """固定点分析器"""

    def add_point(x, y, label=None)
    # 添加要分析的点

    def analyze_points(t_range, num_points=100)
    # 分析所有点，返回DataFrame

    def plot_multiple_points(t_range, num_points, save_path)
    # 绘制多点时间序列

    def plot_heatmap(t_range, grid_size=(20, 20))
    # 创建时空热力图

    def create_composite_plot(t_range, num_points)
    # 创建复合图（3D曲面 + 时间序列）

    def export_data(t_range, num_points, filename)
    # 导出数据到CSV
```

## GUI实现要点

### OptimizedGUI 核心特性

#### 1. 时间同步算法

```python
# 精确控制每帧时间
target_time = real_start_time + (i * frame_time)

# 两种同步模式
if sync_mode == "frame_skip":
    # 跳过慢帧，保证总时间准确
    if current_time > target_time + frame_time:
        skip_frame()
else:
    # 补偿模式：等待到目标时间
    if current_time < target_time:
        time.sleep(target_time - current_time)
```

#### 2. 异步渲染系统

```python
# 防阻塞更新
update_queue.put_nowait(update_task)
root.after(10, update_worker)  # 延迟执行
```

#### 3. 智能缓存机制

```python
# 复用网格数据，避免重复计算
if cache_key in render_cache:
    X, Y = render_cache[cache_key]
else:
    X, Y = create_grid()
    render_cache[cache_key] = (X, Y)
```

#### 4. 多档质量设置

```python
render_quality = {
    'low': {'rcount': 20, 'ccount': 20, 'alpha': 0.9},
    'medium': {'rcount': 30, 'ccount': 30, 'alpha': 0.85},
    'high': {'rcount': 40, 'ccount': 40, 'alpha': 0.8}
}
```

## 可应用到风场编辑的功能

### 1. 函数生成器

将 `DynamicSurfaceGrid` 的函数集成到风场编辑的 `FunctionTool`：

```python
# 在 wind_field_editor/tools.py 中添加
class FunctionTool(Tool):
    def apply_gaussian_to_grid(self, grid_data, center, sigma, amplitude):
        """应用高斯分布"""
        import numpy as np

        rows, cols = grid_data.shape
        cr, cc = center

        r_indices = np.arange(rows)
        c_indices = np.arange(cols)
        r_grid, c_grid = np.meshgrid(r_indices, c_indices, indexing='ij')

        distance_sq = (r_grid - cr) ** 2 + (c_grid - cc) ** 2
        gaussian = amplitude * np.exp(-distance_sq / (2 * sigma ** 2))

        np.maximum(grid_data, gaussian, out=grid_data)
```

### 2. 12种函数模板

```python
# 在 wind_field_editor/config.py 中添加
FUNCTION_TEMPLATES = {
    'gaussian': GaussianFunction(),
    'radial_wave': RadialWaveFunction(),
    'linear_gradient': LinearGradientFunction(),
    'radial_gradient': RadialGradientFunction(),
    'spiral_wave': SpiralWaveFunction(),
    'checkerboard': CheckerboardFunction(),
    'interference': InterferenceFunction(),
    'noise': NoiseFunction(),
    'polynomial': PolynomialFunction(),
    'saddle': SaddleFunction(),
    'standing_wave': StandingWaveFunction(),
    'ripple': RippleFunction()
}
```

### 3. 动画预览功能

```python
# 在 wind_field_editor/ 添加 animation.py
class WindFieldAnimation:
    """风场动画预览"""

    def __init__(self, editor):
        self.editor = editor
        self.is_playing = False
        self.current_frame = 0

    def play(self, duration=5.0, fps=30):
        """播放风场动画"""
        total_frames = int(fps * duration)

        for i in range(total_frames):
            if not self.is_playing:
                break

            # 计算时间参数
            t = (i / total_frames) * 10

            # 应用时间相关的函数
            self.apply_time_function(t)

            # 更新显示
            yield i

    def apply_time_function(self, t):
        """应用时间函数到风场"""
        # 根据选择的函数模板应用
        pass
```

### 4. 点分析功能

```python
# 在 wind_field_editor/ 添加 analyzer.py
class WindFieldAnalyzer:
    """风场数据分析器"""

    def __init__(self, editor):
        self.editor = editor
        self.tracked_points = {}

    def add_point(self, row, col, label=None):
        """添加追踪点"""
        if label is None:
            label = f"({row}, {col})"
        self.tracked_points[label] = (row, col)

    def get_point_time_series(self, t_range):
        """获取点的时间序列"""
        series = {}
        for label, (r, c) in self.tracked_points.items():
            values = []
            for t in t_range:
                # 计算该点在时间t的值
                value = self.editor.compute_function_at_point(r, c, t)
                values.append(value)
            series[label] = values
        return series
```

### 5. 性能优化技术

```python
# 缓存网格坐标
class GridCache:
    """网格坐标缓存"""

    def __init__(self):
        self._cache = {}

    def get_grid(self, grid_dim):
        if grid_dim not in self._cache:
            import numpy as np
            r = np.arange(grid_dim)
            c = np.arange(grid_dim)
            self._cache[grid_dim] = np.meshgrid(r, c, indexing='ij')
        return self._cache[grid_dim]

# 使用
grid_cache = GridCache()
R, C = grid_cache.get_grid(40)
```

## 关键技术总结

### 1. NumPy 向量化计算

```python
# 禁止：使用循环
for r in range(rows):
    for c in range(cols):
        z[r, c] = function(r, c, t)

# 推荐：向量化操作
R, C = np.meshgrid(np.arange(rows), np.arange(cols), indexing='ij')
Z = function(R, C, t)
```

### 2. matplotlib 嵌入 Tkinter

```python
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

self.fig = plt.Figure(figsize=(8, 6))
self.ax = self.fig.add_subplot(111, projection='3d')
self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
self.canvas.get_tk_widget().pack()
```

### 3. 线程安全的GUI更新

```python
def update_plot_async(self):
    """异步更新图形"""
    try:
        self.update_queue.put_nowait('update')
        self.root.after(10, self.update_worker)
    except queue.Full:
        pass  # 队列满，跳过此次更新

def update_worker(self):
    """更新工作线程"""
    try:
        task = self.update_queue.get_nowait()
        if task == 'update':
            self._do_update_plot()
    except queue.Empty:
        pass
```

### 4. 资源清理

```python
def on_close(self):
    # 1. 停止动画
    self.animation_running = False

    # 2. 等待线程结束
    if self.animation_thread:
        self.animation_thread.join(timeout=1.0)

    # 3. 清空队列
    while not self.update_queue.empty():
        self.update_queue.get_nowait()

    # 4. 关闭图形
    plt.close('all')

    # 5. 清理缓存
    self.render_cache.clear()

    # 6. 销毁窗口
    self.root.destroy()
```

## 最佳实践

### 1. 函数设计

- 使用 `x, y, t` 三个参数作为标准输入
- 支持 NumPy 数组和标量
- 返回归一化的值 (0-100 或 -1 到 1)

### 2. 网格生成

```python
# 使用 indexing='ij' 获得矩阵风格索引
X, Y = np.meshgrid(x_array, y_array, indexing='ij')
# X[i, j] = x_array[i]
# Y[i, j] = y_array[j]
```

### 3. 动画优化

- 使用渲染缓存
- 限制更新队列大小
- 提供多档质量设置
- 实现帧跳跃补偿

### 4. 时间同步

```python
# 精确时间控制
target_time = start_time + (frame_index / fps)
current_time = time.time()

if sync_mode == "frame_skip":
    if current_time > target_time + frame_time:
        continue  # 跳过慢帧
```

## 总结

`fan_con` 项目提供了：

1. **12种数学函数模板** - 可直接用于风场编辑
2. **时间同步算法** - 精确的动画控制
3. **性能优化技术** - 缓存、异步渲染、多档质量
4. **点分析功能** - 追踪特定点的时间序列
5. **GUI最佳实践** - Tkinter + matplotlib 集成

这些都可以直接应用到 `wind_field_editor` 模块中！
