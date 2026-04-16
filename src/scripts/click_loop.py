#!/usr/bin/env python3
"""
自动按键精灵 - 循环点击脚本

用于循环执行点击 65.png 和 出击.png 的操作
"""

import pyautogui
import time
import sys
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 也添加父目录，确保能够找到 src 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 再添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.common import run_main_loop

# ====================== 【你只需要改这里】 ======================
# 循环次数（必须 > 0）
LOOP_TIMES = 10

# 是否跳过 icon 查找阶段（True = 跳过，直接开始执行动作）
SKIP_ICON_FIND = False

# 动作列表：
# 支持：
# ["find", "图片路径.png"]   → 自动找图并点击
# ["find_text", "文本"]       → 根据文本查找并点击（使用 macOS OCR）
# ["key", "按键"]            → 按键盘
# ["wait", 秒数]             → 等待
# ["click", x, y]            → 手动点击坐标
ACTIONS = [
    ["find", "static/images/65.png"],   # 自动找屏幕上的 65.png 并点击
    ["wait", 1],          # 隔 1s
    ["find", "static/images/出击.png"],   # 自动找屏幕上的 出击.png 并点击
    ["wait", 15],         # 等待 15s
    ["find", "static/images/继续.png"],   # 自动找屏幕上的 65.png 并点击
    ["wait", 1],          # 隔 1s
]


# ====================== 以下不用动 ======================

# 显示当前工作目录和文件信息
print(f"当前工作目录: {os.getcwd()}")
print(f"当前目录文件列表: {os.listdir('.')}")
print(f"65.png 是否存在: {os.path.exists('static/images/65.png')}")
print(f"出击.png 是否存在: {os.path.exists('static/images/出击.png')}")
if os.path.exists('static/images/65.png'):
    print(f"65.png 完整路径: {os.path.abspath('static/images/65.png')}")
if os.path.exists('static/images/出击.png'):
    print(f"出击.png 完整路径: {os.path.abspath('static/images/出击.png')}")


if __name__ == "__main__":
    try:
        time.sleep(2)
        run_main_loop(LOOP_TIMES, ACTIONS, SKIP_ICON_FIND)
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()
