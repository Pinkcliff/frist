# -*- coding: utf-8 -*-
"""
风场编辑模块单元测试
"""
import sys
import os
import unittest
import numpy as np

# 添加项目路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class TestWindFieldEditor(unittest.TestCase):
    """测试风场编辑器核心功能"""

    def setUp(self):
        """测试前准备"""
        from 风场编辑.core import WindFieldEditor
        self.editor = WindFieldEditor(grid_dim=40, max_rpm=17000)

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.editor.grid_dim, 40)
        self.assertEqual(self.editor.max_rpm, 17000)
        self.assertEqual(self.editor.grid_data.shape, (40, 40))
        self.assertEqual(len(self.editor.selected_cells), 0)

    def test_set_and_get_cell_value(self):
        """测试设置和获取单元格值"""
        self.editor.set_cell_value(10, 10, 50.0)
        value = self.editor.get_cell_value(10, 10)
        self.assertEqual(value, 50.0)

    def test_value_clamping(self):
        """测试值裁剪"""
        self.editor.set_cell_value(10, 10, -10.0)
        self.assertEqual(self.editor.get_cell_value(10, 10), 0.0)

        self.editor.set_cell_value(10, 10, 150.0)
        self.assertEqual(self.editor.get_cell_value(10, 10), 100.0)

    def test_select_all(self):
        """测试全选"""
        self.editor.select_all()
        self.assertEqual(len(self.editor.selected_cells), 1600)  # 40x40

    def test_clear_selection(self):
        """测试清除选择"""
        self.editor.selected_cells.add((10, 10))
        self.editor.clear_selection()
        self.assertEqual(len(self.editor.selected_cells), 0)

    def test_invert_selection(self):
        """测试反选"""
        self.editor.selected_cells.add((10, 10))
        self.editor.invert_selection()
        self.assertEqual(len(self.editor.selected_cells), 1599)  # 1600 - 1
        self.assertNotIn((10, 10), self.editor.selected_cells)

    def test_reset_all_to_zero(self):
        """测试全部清零"""
        self.editor.set_cell_value(10, 10, 50.0)
        self.editor.set_cell_value(20, 20, 80.0)
        self.editor.reset_all_to_zero()

        self.assertEqual(self.editor.get_cell_value(10, 10), 0.0)
        self.assertEqual(self.editor.get_cell_value(20, 20), 0.0)
        self.assertEqual(len(self.editor.selected_cells), 0)

    def test_apply_speed_to_selection(self):
        """测试应用转速到选择"""
        self.editor.selected_cells.add((10, 10))
        self.editor.selected_cells.add((10, 11))

        count = self.editor.apply_speed_to_selection(75.0)
        self.assertEqual(count, 2)
        self.assertEqual(self.editor.get_cell_value(10, 10), 75.0)
        self.assertEqual(self.editor.get_cell_value(10, 11), 75.0)

    def test_apply_speed_with_feathering(self):
        """测试带羽化的转速应用"""
        # 选择中心区域
        center = (20, 20)
        self.editor.selected_cells.add(center)

        # 应用带羽化的转速
        self.editor.apply_speed_to_selection(100.0, feather=True, feather_value=3)

        # 检查中心值
        self.assertEqual(self.editor.get_cell_value(*center), 100.0)

        # 检查周围有羽化效果
        neighbors = [(21, 20), (19, 20), (20, 21), (20, 19)]
        has_feathering = any(self.editor.get_cell_value(*n) > 0 for n in neighbors)
        self.assertTrue(has_feathering)

    def test_apply_brush(self):
        """测试笔刷应用"""
        count = self.editor.apply_brush(
            center_row=20,
            center_col=20,
            brush_size=10,
            brush_value=80.0
        )

        # 检查中心值
        self.assertEqual(self.editor.get_cell_value(20, 20), 80.0)
        self.assertGreater(count, 0)

    def test_apply_circle_selection(self):
        """测试圆形选择"""
        count = self.editor.apply_circle_selection(
            center_row=20,
            center_col=20,
            radius=5.0
        )

        self.assertGreater(count, 0)
        self.assertIn((20, 20), self.editor.selected_cells)

    def test_undo(self):
        """测试撤销"""
        # 保存初始状态
        self.editor._save_state()
        initial_value = self.editor.get_cell_value(10, 10)

        # 修改值（需要先保存状态）
        self.editor._save_state()
        self.editor.set_cell_value(10, 10, 50.0)

        # 撤销
        self.editor.undo()

        # 检查恢复
        self.assertEqual(self.editor.get_cell_value(10, 10), initial_value)

    def test_redo(self):
        """测试重做"""
        self.editor._save_state()
        self.editor.set_cell_value(10, 10, 50.0)
        modified_value = self.editor.get_cell_value(10, 10)

        self.editor.undo()
        self.editor.redo()

        self.assertEqual(self.editor.get_cell_value(10, 10), modified_value)

    def test_get_summary(self):
        """测试获取摘要"""
        self.editor.selected_cells.add((10, 10))
        self.editor.set_cell_value(10, 10, 50.0)

        summary = self.editor.get_summary()

        self.assertEqual(summary['selected_count'], 1)
        self.assertEqual(summary['avg_speed'], 50.0)
        self.assertIn('grid_dim', summary)


class TestWindFieldData(unittest.TestCase):
    """测试风场数据容器"""

    def test_wind_field_data_creation(self):
        """测试创建风场数据"""
        from 风场编辑.core import WindFieldData
        import numpy as np

        grid_data = np.zeros((40, 40))
        data = WindFieldData(grid_data=grid_data)

        self.assertEqual(data.max_rpm, 17000)
        self.assertEqual(data.max_time, 10.0)
        self.assertEqual(data.time_resolution, 0.1)

    def test_get_rpm_data(self):
        """测试获取RPM数据"""
        from 风场编辑.core import WindFieldData
        import numpy as np

        grid_data = np.full((40, 40), 50.0)  # 50%
        data = WindFieldData(grid_data=grid_data, max_rpm=17000)

        rpm_data = data.get_rpm_data()
        self.assertEqual(rpm_data[0, 0], 8500)  # 50% of 17000


class TestTools(unittest.TestCase):
    """测试编辑工具"""

    def test_selection_tool(self):
        """测试选择工具"""
        from 风场编辑.tools import SelectionTool

        tool = SelectionTool()
        tool.activate()

        self.assertTrue(tool.is_active)
        self.assertEqual(tool.tool_type.value, "选择工具")

    def test_brush_tool(self):
        """测试笔刷工具"""
        from 风场编辑.tools import BrushTool

        tool = BrushTool()
        tool.set_size(10)
        tool.set_value(80.0)
        tool.set_feather(True, 3)

        self.assertEqual(tool.settings.size, 10)
        self.assertEqual(tool.settings.value, 80.0)
        self.assertTrue(tool.settings.feather_enabled)
        self.assertEqual(tool.settings.feather_value, 3)

    def test_circle_tool(self):
        """测试圆形工具"""
        from 风场编辑.tools import CircleTool

        tool = CircleTool()
        tool.on_mouse_press(20, 20)
        tool.on_mouse_move(25, 20)

        self.assertGreater(tool.settings.radius, 0)

    def test_function_tool(self):
        """测试函数工具"""
        from 风场编辑.tools import FunctionTool
        import numpy as np

        tool = FunctionTool()

        grid_data = np.zeros((40, 40))
        tool.apply_gaussian(grid_data, center=(20, 20), sigma=5.0, amplitude=100.0)

        # 中心应该是最大值
        self.assertGreater(grid_data[20, 20], 90.0)


class TestUtils(unittest.TestCase):
    """测试工具函数"""

    def test_value_to_color(self):
        """测试值到颜色转换"""
        from 风场编辑.utils import value_to_color

        color_0 = value_to_color(0.0)
        color_50 = value_to_color(50.0)
        color_100 = value_to_color(100.0)

        # 检查返回RGB元组
        self.assertEqual(len(color_0), 3)
        self.assertEqual(len(color_50), 3)
        self.assertEqual(len(color_100), 3)

    def test_distance(self):
        """测试距离计算"""
        from 风场编辑.utils import distance

        dist = distance((0, 0), (3, 4))
        self.assertEqual(dist, 5.0)

    def test_get_module_cells(self):
        """测试获取模块单元格"""
        from 风场编辑.utils import get_module_cells

        cells = get_module_cells(5, 5, module_dim=4)
        self.assertEqual(len(cells), 16)  # 4x4模块

        # 检查起始坐标
        self.assertIn((4, 4), cells)
        self.assertIn((7, 7), cells)

    def test_get_circle_cells(self):
        """测试获取圆形内单元格"""
        from 风场编辑.utils import get_circle_cells

        cells = get_circle_cells((20, 20), 5.0, 40)
        self.assertGreater(len(cells), 0)
        self.assertIn((20, 20), cells)

    def test_generate_fan_id(self):
        """测试生成风扇ID"""
        from 风场编辑.utils import generate_fan_id

        fan_id = generate_fan_id(123, 456)
        self.assertEqual(fan_id, "X456Y123")

    def test_calculate_stats(self):
        """测试统计计算"""
        from 风场编辑.utils import calculate_stats

        stats = calculate_stats([10, 20, 30, 40, 50])

        self.assertEqual(stats['count'], 5)
        self.assertEqual(stats['min'], 10)
        self.assertEqual(stats['max'], 50)
        self.assertEqual(stats['avg'], 30.0)


if __name__ == '__main__':
    unittest.main()
