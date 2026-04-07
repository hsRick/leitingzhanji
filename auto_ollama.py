#!/usr/bin/env python3
"""
使用 ollama 本地模型 qwen3vl:8b 对微信小程序图片进行识别
识别到图标后返回对应的坐标
只查找并选择雷霆战机：集结窗口，未找到则退出程序
"""

import pyautogui
import time
import sys
import json
import base64
import io
from PIL import Image
import requests

# 检测是否为 Retina 显示器
def is_retina():
    if sys.platform == 'darwin':
        import subprocess
        output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode('utf-8')
        return 'Retina' in output
    return False

# 获取雷霆战机：集结窗口位置
def get_thunder_fighter_window():
    """只获取雷霆战机：集结窗口的位置和大小，未找到则返回 None"""
    try:
        # macOS 上使用 Quartz 获取窗口信息
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID,
        )

        # 获取所有窗口
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )

        # 查找雷霆战机：集结窗口
        for window in window_list:
            window_title = window.get("kCGWindowName", "")
            owner_name = window.get("kCGWindowOwnerName", "")
            
            # 只查找雷霆战机：集结窗口
            if "雷霆战机：集结" in window_title:
                bounds = window.get("kCGWindowBounds", {})
                left = bounds.get("X", 0)
                top = bounds.get("Y", 0)
                width = bounds.get("Width", 0)
                height = bounds.get("Height", 0)
                
                print(f"找到窗口：{window_title} (所有者: {owner_name}) - 位置: {left},{top} 大小: {width}x{height}")
                
                # 检查窗口是否在屏幕内且大小合适
                if left >= 0 and top >= 0 and width > 200 and height > 200:
                    print(f"✅ 选择雷霆战机窗口：{window_title} (面积: {int(width * height)})")
                    return {
                        "left": int(left),
                        "top": int(top),
                        "width": int(width),
                        "height": int(height)
                    }
                else:
                    print(f"⚠️ 雷霆战机窗口不在屏幕内或大小不合适")
                    return None
        
        # 未找到雷霆战机窗口
        print("❌ 未找到雷霆战机：集结窗口")
        return None
    except Exception as e:
        print(f"获取窗口失败：{e}")
        return None

# 修复坐标，处理 Retina 显示器问题
def fix_coordinates(x, y):
    """修复坐标，处理 Retina 显示器问题"""
    screen_width, screen_height = pyautogui.size()
    
    fixed_x = x
    fixed_y = y
    
    # 如果坐标超出屏幕范围，可能是 Retina 显示器的缩放问题
    if x > screen_width or y > screen_height:
        # 将坐标除以 2
        fixed_x = int(x / 2)
        fixed_y = int(y / 2)
    
    # 确保坐标在屏幕范围内
    fixed_x = max(0, min(fixed_x, screen_width - 1))
    fixed_y = max(0, min(fixed_y, screen_height - 1))
    
    return fixed_x, fixed_y

# 将 PIL 图像转换为 base64
def image_to_base64(image):
    """将 PIL 图像转换为 base64 编码"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# 使用 ollama 模型识别图像中的元素
def recognize_element(image, description):
    """
    使用 ollama 本地模型 qwen3vl:8b 识别图像中的元素
    参数:
        image: PIL 图像对象
        description: 要识别的元素描述
    返回:
        元素的坐标 (x, y) 或 None
    """
    try:
        # 将图像转换为 base64
        image_base64 = image_to_base64(image)
        
        # 构建请求数据
        data = {
            "model": "qwen3-vl:8b",
            "prompt": f"请在以下图像中识别'{description}'元素，返回其中心点坐标。"\
                      "坐标格式应为 (x, y)，其中 x 是水平坐标，y 是垂直坐标，"\
                      "坐标原点在图像的左上角。"\
                      "如果未找到该元素，请返回 'None'。"\
                      "请详细描述你看到的内容，包括元素的位置、形状、颜色等信息。",
            "images": [image_base64],
            "stream": False
        }
        
        # 发送请求到 ollama API
        print("正在请求 ollama API...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        # 打印完整响应
        print(f"HTTP 状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 解析响应
        response_json = response.json()
        if "response" in response_json:
            content = response_json["response"]
            print(f"模型响应: {content}")
            
            # 提取坐标
            if "(" in content and ")" in content:
                # 尝试从响应中提取坐标
                import re
                match = re.search(r'\((\d+),\s*(\d+)\)', content)
                if match:
                    x = int(match.group(1))
                    y = int(match.group(2))
                    print(f"识别到元素坐标：({x}, {y})")
                    return (x, y)
        
        print("未识别到元素坐标")
        return None
    except Exception as e:
        print(f"识别元素失败：{e}")
        import traceback
        print(f"详细错误信息：{traceback.format_exc()}")
        return None

# 查找并点击元素
def find_and_click_element(description, window):
    """
    在指定窗口内查找并点击指定描述的元素
    参数:
        description: 元素描述
        window: 窗口位置和大小
    返回:
        是否成功找到并点击
    """
    try:
        print(f"正在寻找：{description}")

        # 对窗口进行截图（不落盘）
        screenshot_region = (
            window["left"],
            window["top"],
            window["width"],
            window["height"]
        )
        screenshot = pyautogui.screenshot(region=screenshot_region)

        # 使用 ollama 识别元素
        print("使用 ollama 模型识别元素...")
        element_pos = recognize_element(screenshot, description)
        
        if element_pos:
            # 计算实际屏幕坐标
            actual_x = window["left"] + element_pos[0]
            actual_y = window["top"] + element_pos[1]
            
            # 修复坐标
            fixed_x, fixed_y = fix_coordinates(actual_x, actual_y)
            print(f"修复后的坐标：{fixed_x}, {fixed_y}")

            # 移动到位置并点击
            pyautogui.moveTo(fixed_x, fixed_y, duration=0.5)
            time.sleep(0.5)
            pyautogui.click()
            print(f"✅ 找到并点击：{fixed_x}, {fixed_y}")
            return True
        else:
            print("❌ 未找到目标元素")
            return False
    except Exception as e:
        print(f"错误：{e}")
        return False

# 运行动作
def run_action(act, window):
    t = act[0]
    if t == "find":
        # 执行找图动作并返回结果
        return find_and_click_element(act[1], window)
    elif t == "key":
        pyautogui.press(act[1])
        return True
    elif t == "wait":
        time.sleep(act[1])
        return True
    elif t == "click":
        pyautogui.click(act[1], act[2])
        return True
    time.sleep(1)  # 默认等待时间
    return True

# 主循环
def run_loop():
    count = 1
    print("🚀 自动按键精灵已启动（Ctrl+C 停止）")
    
    # 首先查找雷霆战机：集结窗口
    print("\n===== 查找雷霆战机窗口 =====")
    window = get_thunder_fighter_window()
    
    if not window:
        print("❌ 未找到雷霆战机：集结窗口，程序退出")
        sys.exit(1)
    
    print(f"✅ 已找到雷霆战机窗口：{window}")
    
    # 执行主循环
    while True:
        if LOOP_TIMES > 0 and count > LOOP_TIMES:
            break
        print(f"\n===== 第 {count} 轮 =====")
        
        # 执行动作，检查每个动作的返回值
        action_success = True
        for a in ACTIONS:
            # 执行当前动作
            success = run_action(a, window)
            
            # 如果是找图动作且失败，停止执行后续动作
            if not success:
                print("❌ 动作执行失败，停止当前轮次")
                action_success = False
                break
        
        # 无论动作是否成功，都增加轮次计数
        count += 1

# 初始化时检测 Retina 显示器
RETINA = is_retina()

# ====================== 【你只需要改这里】 ======================
# 循环次数：0 = 无限循环
LOOP_TIMES = 2

# 动作列表：
# 支持：
# ["find", "元素描述"]   → 使用 ollama 识别元素并点击
# ["key", "按键"]            → 按键盘
# ["wait", 秒数]             → 等待
# ["click", x, y]            → 手动点击坐标
ACTIONS = [
    ["find", "免费广告入口"],   # 使用 ollama 识别免费广告入口并点击 icon_pos = recognize_element(screenshot, "免费广告入口")
    ["wait", 2],
    ["find", "广告关闭按钮"],   # 使用 ollama 识别广告关闭按钮并点击
    ["wait", 0.5],
    ["key", "enter"],
    ["wait", 0.5]
]

# ====================== 以下不用动 ======================

if __name__ == "__main__":
    try:
        time.sleep(2)
        run_loop()
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()