#!/usr/bin/env python3
"""
测试 get.png 查找和点击的脚本

专门用于测试 get.png（领取按钮）的查找逻辑
"""

import time
import os
from utils import find_and_click, get_thunder_fighter_window

print("🚀 测试 get.png 查找和点击")
print(f"当前工作目录: {os.getcwd()}")
print(f"get.png 是否存在: {os.path.exists('get.png')}")
if os.path.exists('get.png'):
    print(f"get.png 完整路径: {os.path.abspath('get.png')}")

# 等待 2 秒，让用户准备
time.sleep(2)

# 测试 1: 查找窗口
print("\n=== 测试 1: 查找雷霆战机窗口 ===")
window = get_thunder_fighter_window()
if window:
    print(f"✅ 找到窗口: {window}")
    print(f"  窗口位置: ({window['left']}, {window['top']})")
    print(f"  窗口大小: {window['width']}x{window['height']}")
else:
    print("❌ 未找到窗口")

# 测试 2: 查找并点击 get.png
print("\n=== 测试 2: 查找并点击 get.png ===")
success = find_and_click("get.png")
if success:
    print("✅ get.png 查找和点击成功")
else:
    print("❌ get.png 查找失败")

print("\n🎉 测试完成")
