#!/usr/bin/env python3
"""
通用功能模块

包含多个脚本共享的功能和逻辑
"""

import pyautogui
import time
import sys
import os
from src.utils import (
    find_and_click, 
    find_text_and_click, 
    fix_coordinates,
    is_retina
)

# 初始化时检测 Retina 显示器
RETINA = is_retina()

# 找图精度（0.8~0.99，越接近1越严格）
CONFIDENCE = 0.85

def run_action(act):
    """
    执行单个动作
    
    参数:
        act: 动作列表，如 ["find", "图片路径.png"]
    
    返回:
        bool: 动作是否执行成功
    """
    t = act[0]
    if t == "find":
        image_path = act[1]
        # 先尝试找图
        success = find_and_click(image_path)
        # 如果找 closed.png 失败，等待 3 秒后重试 3 次
        imagename = os.path.basename(image_path)
        if not success and imagename == "closed.png":
            for i in range(3):
                print(f"📝 closed.png 未找到，等待 3 秒后第 {i+1} 次重试...")
                time.sleep(3)
                success = find_and_click(image_path)
                if success:
                    break
        return success
    elif t == "find_text":
        # 执行找文本动作并返回结果
        return find_text_and_click(act[1])
    elif t == "key":
        pyautogui.press(act[1])
        return True
    elif t == "wait":
        time.sleep(act[1])
        return True
    elif t == "click":
        pyautogui.click(act[1], act[2])
        return True
    return True

def find_icon_and_click(skip_icon_find=False, post_icon_action=None):
    """
    查找并点击 icon
    
    参数:
        skip_icon_find: 是否跳过 icon 查找
        post_icon_action: 点击 icon 后执行的回调函数
    
    返回:
        bool: 是否找到并点击了 icon
    """
    if skip_icon_find:
        print("\n===== 已跳过 icon 查找阶段 =====")
        return False
    
    print("\n===== 启动阶段 =====")
    print("正在全屏查找 icon...")
    
    # 尝试多次查找 icon
    icon_found = False
    print(f"使用的置信度: {CONFIDENCE}")
    
    for i in range(3):
        # 尝试不同的置信度
        current_confidence = CONFIDENCE - (i * 0.1)
        if current_confidence < 0.5:
            current_confidence = 0.5
        
        print(f"第 {i+1} 次查找 icon，置信度: {current_confidence}")
        
        # 全屏查找 icon
        pos = None
        try:
            pos = pyautogui.locateOnScreen("static/images/icon.png", confidence=current_confidence)
        except pyautogui.ImageNotFoundException:
            print(f"  未找到 icon")
        except Exception as e:
            print(f"查找 icon 出错：{e}")
        
        if pos:
            x, y = pyautogui.center(pos)
            print(f"找到 icon 位置：{x}, {y}")
            
            # 修复坐标
            fixed_x, fixed_y = fix_coordinates(x, y)
            print(f"修复后的坐标：{fixed_x}, {fixed_y}")
            
            # 点击 icon
            pyautogui.moveTo(fixed_x, fixed_y, duration=0.5)
            time.sleep(0.5)
            pyautogui.click()
            print("✅ 已点击 icon")
            icon_found = True
            # 等待小程序启动
            print("等待小程序启动...")
            time.sleep(1)
            
            # 执行 post_icon_action
            if post_icon_action:
                post_icon_action()
            break
        else:
            print(f"第 {i+1} 次未找到 icon，重试...")
            time.sleep(1)
    
    if not icon_found:
        print("❌ 未找到 icon，继续执行后续操作")
    
    return icon_found

def run_main_loop(loop_times, actions, skip_icon_find=False, post_icon_action=None):
    """
    执行主循环
    
    参数:
        loop_times: 循环次数
        actions: 动作列表
        skip_icon_find: 是否跳过 icon 查找
        post_icon_action: 点击 icon 后执行的回调函数
    """
    print("🚀 自动按键精灵已启动（Ctrl+C 停止）")
    
    # 确保循环次数有效，防止无限循环
    max_loops = max(1, loop_times)
    print(f"将执行 {max_loops} 轮循环")
    
    # 首先全屏查找 icon 并点击（可选）
    find_icon_and_click(skip_icon_find, post_icon_action)

    # 检查 actions 是否为空
    if actions is None:
        print("⚠️ 未提供动作列表，将跳过执行任何操作")
        return
    
    # 执行主循环
    
    # 执行主循环
    for count in range(1, max_loops + 1):
        print(f"\n===== 第 {count} 轮 =====")
        
        # 执行动作，检查每个动作的返回值
        action_success = True
        for a in actions:
            # 执行当前动作
            success = run_action(a)
            
            # 如果是找图动作且失败，停止执行后续动作
            if not success:
                print("❌ 动作执行失败，停止当前轮次")
                action_success = False
                break
    
    # 主循环执行完毕后 执行返回动作
    print("\n🎉 所有轮次执行完毕")
