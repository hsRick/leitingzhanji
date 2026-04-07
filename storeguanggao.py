#!/usr/bin/env python3
"""
自动按键精灵 - 雷霆战机：集结

用于自动执行雷霆战机小程序中的操作，如点击广告、关闭广告等
"""

import pyautogui
import time
import sys
import os
from utils import (
    find_and_click, 
    find_text_and_click, 
    fix_coordinates,
    is_retina
)

# 初始化时检测 Retina 显示器
RETINA = is_retina()

# ====================== 【你只需要改这里】 ======================
# 循环次数（必须 > 0）
LOOP_TIMES = 2

# 是否跳过 icon 查找阶段（True = 跳过，直接开始执行动作）
SKIP_ICON_FIND = False

# 每一步等待时间（秒）
AFTER_WAIT = 0.5

# 动作列表：
# 支持：
# ["find", "图片路径.png"]   → 自动找图并点击
# ["find_text", "文本"]       → 根据文本查找并点击（使用 macOS OCR）
# ["key", "按键"]            → 按键盘
# ["wait", 秒数]             → 等待
# ["click", x, y]            → 手动点击坐标
ACTIONS = [
    ["find", "guanggao.png"],   # 自动找屏幕上的 guanggao.png 并点击
    ["wait", 31],
    ["find", "closed.png"],   # 自动找屏幕上的 closed.png 并点击
    # ["find_text", "关闭"],       # 根据文本"关闭"查找并点击（需要安装 pyobjc）
    ["find", "get.png"],   # 自动找屏幕上的 get.png 并点击
    ["wait", 0.5],
]

# 找图精度（0.8~0.99，越接近1越严格）
CONFIDENCE = 0.85


# ====================== 以下不用动 ======================

# 显示当前工作目录和文件信息
print(f"当前工作目录: {os.getcwd()}")
print(f"当前目录文件列表: {os.listdir('.')}")
print(f"icon.png 是否存在: {os.path.exists('icon.png')}")
if os.path.exists('icon.png'):
    print(f"icon.png 完整路径: {os.path.abspath('icon.png')}")

def run_action(act):
    """
    执行单个动作
    
    参数:
        act: 动作列表，如 ["find", "guanggao.png"]
    
    返回:
        bool: 动作是否执行成功
    """
    t = act[0]
    if t == "find":
        # 执行找图动作并返回结果
        return find_and_click(act[1])
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
    # time.sleep(AFTER_WAIT)
    return True

def run_loop():
    """
    主循环，执行所有动作
    """
    print("🚀 自动按键精灵已启动（Ctrl+C 停止）")
    
    # 确保循环次数有效，防止无限循环
    max_loops = max(1, LOOP_TIMES)
    print(f"将执行 {max_loops} 轮循环")
    
    # 首先全屏查找 icon 并点击（可选）
    if not SKIP_ICON_FIND:
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
                pos = pyautogui.locateOnScreen("icon.png", confidence=current_confidence)
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
                # 等待小程序启动（增加等待时间）
                print("等待小程序启动...")
                time.sleep(5)
                break
            else:
                print(f"第 {i+1} 次未找到 icon，重试...")
                time.sleep(1)
        
        if not icon_found:
            print("❌ 未找到 icon，继续执行后续操作")
    else:
        print("\n===== 已跳过 icon 查找阶段 =====")
    
    # 执行主循环（使用 for 循环替代 while，确保不会无限循环）
    for count in range(1, max_loops + 1):
        print(f"\n===== 第 {count} 轮 =====")
        
        # 执行动作，检查每个动作的返回值
        action_success = True
        for a in ACTIONS:
            # 执行当前动作
            success = run_action(a)
            
            # 如果是找图动作且失败，停止执行后续动作
            if not success:
                print("❌ 动作执行失败，停止当前轮次")
                action_success = False
                break
    
    # 主循环执行完毕后 执行返回动作
    print("\n🎉 所有轮次执行完毕")


if __name__ == "__main__":
    try:
        time.sleep(2)
        run_loop()
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()
