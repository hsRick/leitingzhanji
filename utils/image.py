#!/usr/bin/env python3
"""
图像处理工具模块

提供图片查找、点击等功能，处理 Retina 显示器的坐标问题
"""

import os
import time
import pyautogui
from utils.coordinates import fix_coordinates, is_point_in_window
from utils.window import get_thunder_fighter_window, is_retina

# 检测是否为 Retina 显示器
RETINA = is_retina()

def find_and_click(image_path):
    """
    在屏幕或指定窗口中查找图片并点击
    
    参数:
        image_path: 图片文件路径
    
    返回:
        bool: 是否成功找到并点击
    """
    try:
        print(f"正在寻找：{image_path}")
        
        # 检查图片文件是否存在
        if not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {os.path.abspath(image_path)}")
            return False

        # 获取微信小程序窗口位置
        print("查找微信小程序窗口...")
        window = get_thunder_fighter_window()
        if window:
            print(f"窗口信息：{window}")
        else:
            print("未找到微信小程序窗口")
        
        # 尝试多次找图，每次降低置信度
        confidence_levels = [0.85, 0.75, 0.65, 0.55]
        
        for attempt, conf in enumerate(confidence_levels):
            print(f"第 {attempt+1} 次尝试，置信度: {conf}")
            
            # 先尝试全屏查找
            print("  尝试全屏查找...")
            pos = None
            try:
                pos = pyautogui.locateOnScreen(image_path, confidence=conf)
            except pyautogui.ImageNotFoundException:
                print("  全屏未找到")
            except Exception as e:
                print(f"  全屏查找出错: {e}")
            
            if pos:
                x, y = pyautogui.center(pos)
                print(f"  找到图片位置：{x}, {y}")
                
                # 修复坐标（处理 Retina 显示器）
                fixed_x, fixed_y = fix_coordinates(x, y)
                print(f"  修复后的坐标：{fixed_x}, {fixed_y}")
                
                # 如果找到了窗口，检查坐标是否在窗口内
                if window:
                    print(f"  窗口范围: ({window['left']},{window['top']}) - ({window['left'] + window['width']},{window['top'] + window['height']})")
                    in_window = (
                        fixed_x >= window["left"] and 
                        fixed_x <= window["left"] + window["width"] and 
                        fixed_y >= window["top"] and 
                        fixed_y <= window["top"] + window["height"]
                    )
                    print(f"  坐标是否在窗口内: {in_window}")
                    
                    # 如果坐标不在窗口内，继续查找
                    if not in_window:
                        print("  ⚠️  坐标不在窗口内，继续查找...")
                        continue
                
                # 点击
                print(f"  用修复后的坐标点击 {image_path}: {fixed_x}, {fixed_y}")
                pyautogui.moveTo(fixed_x, fixed_y, duration=0.5)
                time.sleep(0.5)
                pyautogui.click()
                print(f"✅ 点击完成 {image_path}：{fixed_x}, {fixed_y}")
                return True
            
        print("❌ 未找到目标元素")
        return False
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        print(traceback.format_exc())
        return False


def find_text_and_click(text):
    """
    根据文本查找并点击
    
    参数:
        text: 要查找的文本
        
    返回:
        bool: 是否成功找到并点击
    """
    try:
        print(f"正在查找文本：{text}")
        
        # 获取微信小程序窗口位置
        print("查找微信小程序窗口...")
        window = get_thunder_fighter_window()
        if window:
            print(f"限制在微信小程序窗口内查找：{window}")
        else:
            print("未找到微信小程序窗口，将在全屏查找")
        
        # 尝试多次查找
        for i in range(3):
            from utils.ocr import find_text_ocr
            pos = find_text_ocr(text, window)
            if pos:
                x, y = pos
                print(f"找到文本位置：{x}, {y}")
                
                # 修复坐标
                fixed_x, fixed_y = fix_coordinates(x, y)
                print(f"修复后的坐标：{fixed_x}, {fixed_y}")
                
                # 移动到位置并点击
                pyautogui.moveTo(fixed_x, fixed_y, duration=0.5)
                pyautogui.click()
                print(f"✅ 找到并点击：{fixed_x}, {fixed_y}")
                return True
            else:
                print(f"第 {i+1} 次未找到，重试...")
        
        print("❌ 未找到目标文本")
        return False
        
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        print(traceback.format_exc())
        return False
