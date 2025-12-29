# config.py

# 1. 计算域参数 (Computational Domain Parameters)
MARGIN_X = 200.0 # mm
MARGIN_Y = 200.0 # mm
INLET_LENGTH = 1.0   # m
OUTLET_LENGTH = 10.0 # m
IS_GROUNDED = False
# 2. 风扇阵列 (Fan Array)
FAN_ARRAY_SHAPE = (40, 40)
# FAN_PITCH is deprecated. Fan spacing is determined by FAN_WIDTH.

# 3. 风扇几何模型 (Fan Geometry) in mm
FAN_WIDTH = 80.0
FAN_THICKNESS = 80.0
FAN_HOLE_DIAMETER = 76.0   # 风扇开孔直径
FAN_HUB_DIAMETER = 36.0    # 轮毂直径
FAN_CIRCLE_SEGMENTS = 8

# 4. 网格定义 (Grid Definition)
COMPONENT_GRID_CELLS = (4, 4, 4)
ENVIRONMENT_GRID_SIZE = (50.0, 50.0, 50.0) # mm
# 6. 网格拉伸比 (Grid Stretching Ratios)
STRETCH_RATIO_Z = 1.05
STRETCH_RATIO_XY = 1.1
# 5. 风扇运行参数
FAN_RPM_1 = 17000
FAN_DIRECTION_1_IS_CW = False
FAN_RPM_2 = 14600
FAN_DIRECTION_2_IS_CW = False
DEFAULT_PQ_CURVE_FILE = "fan_curve_14600.txt"

# --- 在 pre_processor_config.py 的文件末尾 ---

DOMAIN_BOUNDS = {}
DOMAIN_BOUNDS_M = {} # 新增：用于存储米单位的边界

def update_domain_bounds():
    """根据当前参数计算并更新全局的DOMAIN_BOUNDS字典 (单位: mm 和 m)"""
    global DOMAIN_BOUNDS, DOMAIN_BOUNDS_M
    
    fan_wall_x_size = FAN_ARRAY_SHAPE[1] * FAN_WIDTH
    fan_wall_y_size = FAN_ARRAY_SHAPE[0] * FAN_WIDTH
    
    # 【核心修复】根据 IS_GROUNDED 标志来决定 ymin 的值
    ymin_val = 0.0 if IS_GROUNDED else -MARGIN_Y
    
    # 毫米单位的边界
    DOMAIN_BOUNDS = {
        'xmin': -MARGIN_X,
        'xmax': fan_wall_x_size + MARGIN_X,
        'ymin': ymin_val, # 使用计算出的 ymin_val
        'ymax': fan_wall_y_size + MARGIN_Y,
        'zmin': -INLET_LENGTH * 1000,
        'zmax': FAN_THICKNESS + OUTLET_LENGTH * 1000
    }
    
    # 米单位的边界
    DOMAIN_BOUNDS_M = {key: value / 1000.0 for key, value in DOMAIN_BOUNDS.items()}

