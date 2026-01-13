# core_theme_manager.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
                               QPushButton, QLabel, QComboBox, QDoubleSpinBox, QTabWidget, 
                               QTableWidget, QCheckBox, QSlider, QTextEdit, QFormLayout,
                               QLineEdit, QSpinBox, QFrame, QRadioButton)
from ui_custom_widgets import CommunicationStatusIndicator
themes = {
    "dark": {
        "main_bg": "#1a1c23", 
        "frame_bg": "#2a2c33",  # MODIFIED: Was rgba(42, 44, 51, 0.8)
        "frame_border": "#3a3c43",
        "title_bar_bg": "#3a3c43", "text_color": "#e1e1e6", "text_secondary_color": "#8a8f98",
        "text_tertiary_color": "#5e626a", "toolbar_bg": "#2a2c33", "button_bg": "#3a3c43",
        "button_border": "#4a4c53", "button_text": "#e1e1e6", "button_checked_bg": "#00d1ff",
        "button_checked_text": "#1a1c23", "tab_bg": "#2a2c33", "tab_selected_bg": "#3a3c43",
        "table_grid": "#3a3c43", "header_bg": "#2a2c33", "textbox_bg": "#2a2c33",
        "chart_title_bg": "rgba(42, 44, 51, 0.7)", "close_button_bg": "#3a3c43",
        "close_button_text": "#2a2c33", "close_button_hover": "#5a5c63",
    },
    "light": {
        "main_bg": "#f0f2f5", 
        "frame_bg": "#ffffff",  # MODIFIED: Was rgba(255, 255, 255, 0.8)
        "frame_border": "#d9d9d9",
        "title_bar_bg": "#e8e8e8", "text_color": "#2c3e50", "text_secondary_color": "#596275",
        "text_tertiary_color": "#8395a7", "toolbar_bg": "#ffffff", "button_bg": "#e8e8e8",
        "button_border": "#d9d9d9", "button_text": "#2c3e50", "button_checked_bg": "#00d1ff",
        "button_checked_text": "#ffffff", "tab_bg": "#f0f2f5", "tab_selected_bg": "#ffffff",
        "table_grid": "#d9d9d9", "header_bg": "#f0f2f5", "textbox_bg": "#ffffff",
        "chart_title_bg": "rgba(255, 255, 255, 0.7)", "close_button_bg": "#d9d9d9",
        "close_button_text": "#596275", "close_button_hover": "#c0c0c0",
    }
}

# ... (apply_theme 函数保持不变) ...
# core_theme_manager.py

def apply_theme(window, theme_name):
    """
    应用指定的主题到整个应用程序窗口及其所有子控件。
    """
    theme = themes[theme_name]
    
    # --- 1. 全局样式设置 ---
    # 设置主窗口和工具栏的背景
    window.setStyleSheet(f"""
        QMainWindow {{
            background-color: {theme['toolbar_bg']};
        }}
        QToolBar {{
            border: none;
            padding: 5px;
            spacing: 10px;
        }}
    """)
    
    # --- 2. 工具栏按钮样式 ---
    button_style = f"""
        QPushButton {{ 
            font-size: 14px;
            color: {theme['button_text']};
            background-color: {theme['button_bg']}; 
            border: 1px solid {theme['button_border']};
            border-radius: 5px;
        }}
        QPushButton:hover {{
            border-color: #00d1ff;
        }}
        QPushButton:checked {{
            background-color: {theme['button_checked_bg']};
            color: {theme['button_checked_text']};
        }}
    """
    for button in window.toolbar.findChildren(QPushButton):
        button.setStyleSheet(button_style)

    # --- 3. 遍历所有Docks并应用样式 ---
    for dock in window.docks.values():
        if not dock:  # 检查dock是否存在
            continue

        # 设置Dock框架本身
        dock.setStyleSheet(f"""
            DraggableFrame {{
                background-color: {theme['frame_bg']};
                border: 1px solid {theme['frame_border']};
                border-radius: 8px;
            }}
        """)
        
        # 设置Dock的标题栏和标题文字
        dock.title_bar.setStyleSheet(f"""
            background-color: {theme['title_bar_bg']};
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
        """)
        dock.title_label.setStyleSheet(f"""
            color: {theme['text_color']};
            font-size: 14px;
            font-weight: 600;
            padding: 8px 0;
            background-color: transparent; /* 确保背景透明 */
            border: none;
        """)
        
        # 设置Dock的关闭按钮
        dock.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['close_button_bg']};
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                color: {theme['close_button_text']};
            }}
            QPushButton:hover {{
                background-color: {theme['close_button_hover']};
            }}
        """)

        # --- 4. 遍历Dock内部的所有子控件 ---
        # 这是一个更通用的方法，可以覆盖所有类型的控件
        
        # 定义通用样式字符串
        label_style = f"color: {theme['text_color']};"
        checkbox_style = f"color: {theme['text_color']};"
        radiobutton_style = f"color: {theme['text_color']};"
        groupbox_style = f"""
            QGroupBox {{
                color: {theme['text_color']};
                font-weight: bold;
                border: 1px solid {theme['frame_border']};
                border-radius: 5px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }}
        """
        textbox_style = f"""
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {{
                color: {theme['text_color']};
                background-color: {theme['textbox_bg']};
                border: 1px solid {theme['button_border']};
                border-radius: 4px;
                padding: 2px 4px;
            }}
        """
        combobox_style = f"""
            QComboBox {{
                color: {theme['text_color']};
                background-color: {theme['textbox_bg']};
                border: 1px solid {theme['button_border']};
                border-radius: 4px;
                padding: 2px 4px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none; /* 可以添加自定义箭头图标 */
            }}
        """
        # 查找并应用样式
        for child in dock.findChildren(QWidget):
            if isinstance(child, QLabel) and child is not dock.title_label:
                # 排除一些特殊处理的QLabel
                if not isinstance(child.parent(), (type(window.env_temp), CommunicationStatusIndicator)):
                     child.setStyleSheet(label_style)
            elif isinstance(child, QCheckBox):
                child.setStyleSheet(checkbox_style)
            elif isinstance(child, QRadioButton):
                child.setStyleSheet(radiobutton_style)
            elif isinstance(child, QGroupBox):
                child.setStyleSheet(groupbox_style)
            elif isinstance(child, (QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit)):
                child.setStyleSheet(textbox_style)
            elif isinstance(child, QComboBox):
                child.setStyleSheet(combobox_style)
            # QPushButton 在Dock内部的样式 (例如 "执行", "打开仿真模块" 等)
            elif isinstance(child, QPushButton) and child is not dock.close_button:
                 child.setStyleSheet(f"""
                    QPushButton {{
                        color: {theme['button_text']};
                        background-color: {theme['button_bg']};
                        border: 1px solid {theme['button_border']};
                        border-radius: 4px;
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        border-color: #00d1ff;
                    }}
                 """)

    # --- 5. 特殊控件和主窗口UI元素 ---
    # 这些控件是主窗口的直接成员，需要单独处理
    
    if hasattr(window, 'health_indicator'):
        window.health_indicator.set_text_color(theme['text_color'])
        
    if hasattr(window, 'comm_indicators'):
        for indicator in window.comm_indicators:
            indicator.name_label.setStyleSheet(f"font-size: 12px; color: {theme['text_color']};")
            indicator.count_label.setStyleSheet(f"font-size: 11px; color: {theme['text_secondary_color']};")
            indicator.speed_label.setStyleSheet(f"font-size: 10px; color: {theme['text_tertiary_color']};")
    
    if all(hasattr(window, attr) for attr in ['env_temp', 'env_humid', 'env_press', 'env_density']):
        for env_display in [window.env_temp, window.env_humid, window.env_press, window.env_density]:
            env_display.title_label.setStyleSheet(f"font-size: 12px; color: {theme['text_secondary_color']};")
            
    if hasattr(window, 'time_label'):
        window.time_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {theme['text_color']}; padding-top: 10px;")
        
    if hasattr(window, 'user_label'):
        window.user_label.setStyleSheet(f"font-size: 12px; color: {theme['text_secondary_color']};")

    # --- 6. 图表和Tab样式 ---
    if all(hasattr(window, attr) for attr in ['chart_current_widget', 'chart_voltage_widget', 'chart_power_widget']):
        for chart in [window.chart_current_widget, window.chart_voltage_widget, window.chart_power_widget]:
            if chart:
                chart.set_theme(theme['text_color'], theme['chart_title_bg'])

    tab_style = f"""
        QTabWidget::pane {{
            border: 1px solid {theme['frame_border']};
            background-color: transparent;
        }}
        QTabBar::tab {{
            background: {theme['tab_bg']};
            border: 1px solid {theme['frame_border']};
            border-bottom: none;
            padding: 8px 15px;
            color: {theme['text_color']};
        }}
        QTabBar::tab:selected {{
            background: {theme['tab_selected_bg']};
            color: #00d1ff;
        }}
    """
    table_style = f"""
        QTableWidget {{
            background-color: transparent;
            gridline-color: {theme['table_grid']};
            color: {theme['text_color']};
        }}
        QHeaderView::section {{
            background-color: {theme['header_bg']};
            color: {theme['text_color']};
            border: 1px solid {theme['frame_border']};
            padding: 8px;
        }}
    """
    if hasattr(window, 'log_tab_widget'):
        window.log_tab_widget.setStyleSheet(tab_style + table_style)

    if hasattr(window, 'settings_tab_widget'):
        window.settings_tab_widget.setStyleSheet(tab_style)

    # 为"俯仰·造雨·示踪"组合dock中的TabWidget应用主题
    if '俯仰·造雨·示踪' in window.docks:
        dock = window.docks['俯仰·造雨·示踪']
        if dock:
            # 查找dock中的所有QTabWidget并应用主题
            for tab_widget in dock.findChildren(QTabWidget):
                tab_widget.setStyleSheet(tab_style)
                # 同时为tab内的table应用样式
                for table in tab_widget.findChildren(QTableWidget):
                    table.setStyleSheet(table_style)

    # --- 7. 确保设备状态相关的颜色更新 ---
    window.update_device_state()

