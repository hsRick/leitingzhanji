#!/usr/bin/env python3
"""
坐标处理工具模块

提供坐标修复、转换等功能，特别是处理 Retina 显示器的坐标问题
"""

import pyautogui
from utils.window import is_retina

# 检测是否为 Retina 显示器
RETINA = is_retina()

def fix_coordinates(x, y):
    """
    修复坐标，处理 Retina 显示器问题
    
    参数:
        x: 原始 x 坐标
        y: 原始 y 坐标
    
    返回:
        (fixed_x, fixed_y): 修复后的坐标
    """
    screen_width, screen_height = pyautogui.size()
    
    fixed_x = x
    fixed_y = y
    
    # 如果是 Retina 显示器，直接除以 2
    if RETINA:
        fixed_x = int(x / 2)
        fixed_y = int(y / 2)
    # 否则只在坐标超出屏幕范围时除以 2（兼容非 Retina）
    elif x > screen_width or y > screen_height:
        fixed_x = int(x / 2)
        fixed_y = int(y / 2)
    
    # 确保坐标在屏幕范围内
    fixed_x = max(0, min(fixed_x, screen_width - 1))
    fixed_y = max(0, min(fixed_y, screen_height - 1))
    
    return fixed_x, fixed_y


def is_point_in_window(point, window):
    """
    检查点是否在窗口内
    
    参数:
        point: (x, y) 坐标
        window: 窗口信息字典，包含 left, top, width, height
    
    返回:
        bool: 点是否在窗口内
    """
    x, y = point
    return (
        x >= window["left"] and 
        x <= window["left"] + window["width"] and 
        y >= window["top"] and 
        y <= window["top"] + window["height"]
    )
