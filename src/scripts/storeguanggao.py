#!/usr/bin/env python3
"""
自动按键精灵 - 雷霆战机：集结

用于自动执行雷霆战机小程序中的操作，如点击广告、关闭广告等
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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.common import run_main_loop
from src.utils import find_and_click

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
    ["find", "static/images/guanggao.png"],   # 自动找屏幕上的 guanggao.png 并点击
    ["wait", 32],
    ["find", "static/images/closed.png"],   # 自动找屏幕上的 closed.png 并点击
    ["wait", 1],    
    ["find", "static/images/get.png"],   # 自动找屏幕上的 get.png 并点击
    ["wait", 1],
]


# ====================== 以下不用动 ======================

# 显示当前工作目录和文件信息
print(f"当前工作目录: {os.getcwd()}")
print(f"当前目录文件列表: {os.listdir('.')}")
print(f"icon.png 是否存在: {os.path.exists('static/images/icon.png')}")
if os.path.exists('static/images/icon.png'):
    print(f"icon.png 完整路径: {os.path.abspath('static/images/icon.png')}")

# 定义点击 icon 后执行的操作
def post_icon_action():
    find_and_click("static/images/store.png")


if __name__ == "__main__":
    try:
        time.sleep(2)
        run_main_loop(LOOP_TIMES, ACTIONS, SKIP_ICON_FIND, post_icon_action)
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()
