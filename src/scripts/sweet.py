#!/usr/bin/env python3
"""
自动按键精灵 - 扫荡脚本

用于自动执行扫荡操作：
1. 点击闯关模式
2. 点击英雄难度
3. 点击快速扫荡
4. 点击扫荡
5. 查找双倍奖励，存在则点击并等待30秒，不存在则继续
6. 重复扫荡流程
"""

import pyautogui
import time
import sys
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from scripts.powerplus import ACTIONS
from src.utils.common import run_main_loop

from src.utils.common import run_action
from src.utils import find_and_click

# ====================== 【你只需要改这里】 ======================
# 循环次数（必须 > 0）
LOOP_TIMES = 4

# 是否跳过 icon 查找阶段（True = 跳过，直接开始执行动作）
SKIP_ICON_FIND = False

# 扫荡流程中的等待时间（秒）
SWEEP_WAIT_TIME = 30

# 闯关模式图片路径
CHALLENGE_MODE_IMAGE = "static/images/闯关模式.png"
# 英雄难度图片路径
HERO_DIFFICULTY_IMAGE = "static/images/英雄难度.png"
# 快速扫荡图片路径
QUICK_SWEEP_IMAGE = "static/images/快速扫荡.png"
# 扫荡图片路径
SWEEP_IMAGE = "static/images/扫荡.png"
# 双倍奖励图片路径
DOUBLE_REWARD_IMAGE = "static/images/双倍奖励.png"


# ====================== 以下不用动 ======================

# 显示当前工作目录和文件信息
print(f"当前工作目录: {os.getcwd()}")
print(f"当前目录文件列表: {os.listdir('.')}")


def check_and_click_double_reward():
    """
    检查双倍奖励是否存在，如果存在则点击

    返回:
        bool: 双倍奖励是否被点击
    """
    print("查找双倍奖励...")
    if os.path.exists(DOUBLE_REWARD_IMAGE):
        success = find_and_click(DOUBLE_REWARD_IMAGE)
        if success:
            print("✅ 找到并点击了双倍奖励")
            return True
        else:
            print("❌ 未找到双倍奖励")
            return False
    else:
        print(f"❌ 双倍奖励图片不存在: {DOUBLE_REWARD_IMAGE}")
        return False


def run_sweep_cycle(cycle_num):
    """
    执行一次扫荡循环

    参数:
        cycle_num: 当前循环编号
    """
    print(f"\n===== 第 {cycle_num} 轮扫荡 =====")

    # 4. 点击扫荡
    print("4. 点击扫荡")
    find_and_click(SWEEP_IMAGE)
    time.sleep(1)

    # 5. 查找并点击双倍奖励
    print("5. 查找双倍奖励")
    if check_and_click_double_reward():
        print(f"⏳ 等待 {SWEEP_WAIT_TIME} 秒...")
        time.sleep(SWEEP_WAIT_TIME)
        # 点击关闭
        success = find_and_click("static/images/closed.png")
        if not success:
            for i in range(3):
                print(f"📝 closed.png 未找到，等待 3 秒后第 {i+1} 次重试...")
                time.sleep(3)
                success = find_and_click("static/images/closed.png")
                if success:
                    break
        return success
    else:
        print("⚠️ 双倍奖励不存在，继续执行")

    time.sleep(1)
    # 4. 点击扫荡
    print("4. 点击扫荡")
    find_and_click(SWEEP_IMAGE)
    time.sleep(1)


def run_sweep_loop():
    """
    执行扫荡主循环
    """
    print("🚀 自动扫荡脚本已启动（Ctrl+C 停止）")
    find_and_click(CHALLENGE_MODE_IMAGE)
    print(f"将执行 {LOOP_TIMES} 轮扫荡")

    # 执行扫荡循环
    for i in range(1, LOOP_TIMES + 1):
        run_sweep_cycle(i)

    print("\n🎉 所有扫荡轮次执行完毕")


# 定义点击 icon 后执行的操作
def post_icon_action():
    # 1. 点击闯关模式
    print("1. 点击闯关模式")
    find_and_click(CHALLENGE_MODE_IMAGE)
    time.sleep(1)

    # 2. 点击英雄难度
    print("2. 点击英雄难度")
    find_and_click(HERO_DIFFICULTY_IMAGE)
    time.sleep(1)

    # 3. 点击快速扫荡
    print("3. 点击快速扫荡")
    find_and_click(QUICK_SWEEP_IMAGE)
    time.sleep(1)
    print("执行 icon 点击后的操作")


ACTIONS = None
if __name__ == "__main__":
    try:
        time.sleep(2)
        run_main_loop(LOOP_TIMES, ACTIONS, SKIP_ICON_FIND, post_icon_action)

        run_sweep_loop()
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()
