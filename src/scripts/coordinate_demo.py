#!/usr/bin/env python3
"""
坐标转换 demo

使用 ollama 模型识别"商城"元素坐标
使用图片查找识别 store.png 坐标
比对两个坐标并计算转换关系
"""

import pyautogui
import time
import sys
import json
import base64
import io
from PIL import Image
import requests
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import find_and_click, find_text_and_click, fix_coordinates, is_retina


# 检测是否为 Retina 显示器
def is_retina():
    if sys.platform == "darwin":
        import subprocess

        output = subprocess.check_output(
            ["system_profiler", "SPDisplaysDataType"]
        ).decode("utf-8")
        return "Retina" in output
    return False


# 获取雷霆战机：集结窗口位置
def get_thunder_fighter_window():
    """只获取雷霆战机：集结窗口的位置和大小，未找到则返回 None"""
    try:
        find_and_click("static/images/icon.png")
        time.sleep(1)
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

                print(
                    f"找到窗口：{window_title} (所有者: {owner_name}) - 位置: {left},{top} 大小: {width}x{height}"
                )

                # 检查窗口是否在屏幕内且大小合适
                if left >= 0 and top >= 0 and width > 200 and height > 200:
                    print(
                        f"✅ 选择雷霆战机窗口：{window_title} (面积: {int(width * height)})"
                    )
                    return {
                        "left": int(left),
                        "top": int(top),
                        "width": int(width),
                        "height": int(height),
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
    finally:
        pyautogui.press(["command", "tab"])


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
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


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
            "prompt": f"请快速识别以下图像中的'{description}'元素，直接返回其中心点坐标，不要进行过度思考。"
            "坐标格式应为 (x, y)，其中 x 是水平坐标，y 是垂直坐标，"
            "以左上角为原点，计算元素中心点坐标。"
            "如果未找到该元素，请直接返回 'None'。"
            "请只返回坐标或 'None'，不要添加任何额外的描述或解释。",
            "images": [image_base64],
            "stream": False,
            "options": {
                "temperature": 0.1,  # 降低温度，减少随机性
                "max_tokens": 50,  # 限制输出长度
            },
        }

        # 发送请求到 ollama API
        print("正在请求 ollama API...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=data,
            headers={"Content-Type": "application/json"},
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

                match = re.search(r"\((\d+),\s*(\d+)\)", content)
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


# 使用 pyautogui 查找图片并获取坐标
def find_image_coordinates(image_path, confidence=0.85):
    """
    使用 pyautogui 查找图片并获取中心点坐标
    参数:
        image_path: 图片文件路径
        confidence: 置信度
    返回:
        元素的坐标 (x, y) 或 None
    """
    try:
        find_and_click("static/images/icon.png")
        time.sleep(1)
        print(f"正在使用 pyautogui 查找图片：{image_path}")

        # 检查图片文件是否存在
        if not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {os.path.abspath(image_path)}")
            return None

        # 尝试查找图片
        pos = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if pos:
            x, y = pyautogui.center(pos)
            print(f"找到图片位置：({x}, {y})")
            return (x, y)
        else:
            print("未找到图片")
            return None
    except Exception as e:
        print(f"查找图片失败：{e}")
        import traceback

        print(f"详细错误信息：{traceback.format_exc()}")
        return None


# 计算坐标转换函数
def calculate_coordinate_transform(ollama_coords, image_coords, window):
    """
    计算坐标转换关系
    参数:
        ollama_coords: ollama 识别的坐标（相对于窗口）
        image_coords: 图片查找的坐标（相对于屏幕）
        window: 窗口信息
    返回:
        转换函数
    """
    if not ollama_coords or not image_coords or not window:
        print("❌ 坐标信息不完整，无法计算转换关系")
        return None

    # 计算 ollama 坐标对应的屏幕坐标
    ollama_screen_x = window["left"] + ollama_coords[0]
    ollama_screen_y = window["top"] + ollama_coords[1]

    print(f"\n===== 坐标比对 =====")
    print(f"Ollama 识别的相对坐标：({ollama_coords[0]}, {ollama_coords[1]})")
    print(f"Ollama 对应的屏幕坐标：({ollama_screen_x}, {ollama_screen_y})")
    print(f"图片查找的屏幕坐标：({image_coords[0]}, {image_coords[1]})")

    # 计算差异
    delta_x = image_coords[0] - ollama_screen_x
    delta_y = image_coords[1] - ollama_screen_y

    print(f"\n===== 坐标差异 =====")
    print(f"X 轴差异：{delta_x}")
    print(f"Y 轴差异：{delta_y}")

    # 定义转换函数
    def transform_coordinates(relative_x, relative_y):
        """
        将相对窗口的坐标转换为屏幕坐标
        """
        screen_x = window["left"] + relative_x + delta_x
        screen_y = window["top"] + relative_y + delta_y
        # 修复 Retina 显示器问题
        fixed_x, fixed_y = fix_coordinates(screen_x, screen_y)
        return (fixed_x, fixed_y)

    print("\n===== 转换函数 =====")
    print(
        f"转换函数：screen_x = window.left + relative_x + {delta_x}, screen_y = window.top + relative_y + {delta_y}"
    )

    return transform_coordinates


# 主函数
def main():
    print("🚀 坐标转换 demo 启动")

    # 首先查找雷霆战机：集结窗口
    print("\n===== 查找雷霆战机窗口 =====")
    window = get_thunder_fighter_window()

    if not window:
        print("❌ 未找到雷霆战机：集结窗口，程序退出")
        sys.exit(1)

    print(f"✅ 已找到雷霆战机窗口：{window}")

    # 1. 使用 ollama 识别"商城"元素
    print("\n===== 使用 ollama 识别 '商城' 元素 =====")
    # 对窗口进行截图
    screenshot_region = (
        window["left"],
        window["top"],
        window["width"],
        window["height"],
    )
    screenshot = pyautogui.screenshot(region=screenshot_region)

    # 使用 ollama 识别"商城"元素
    mall_coords = recognize_element(screenshot, "商城")

    if not mall_coords:
        print("❌ 未识别到 '商城' 元素，程序退出")
        sys.exit(1)

    # 2. 使用图片查找获取 store.png 坐标
    print("\n===== 使用图片查找获取 store.png 坐标 =====")
    store_coords = find_image_coordinates("static/images/store.png")

    if not store_coords:
        print("❌ 未找到 store.png，程序退出")
        sys.exit(1)

    # 3. 计算坐标转换关系
    print("\n===== 计算坐标转换关系 =====")
    transform_func = calculate_coordinate_transform(mall_coords, store_coords, window)

    if transform_func:
        # 测试转换函数
        test_x, test_y = mall_coords
        transformed_x, transformed_y = transform_func(test_x, test_y)
        print(f"\n===== 转换测试 =====")
        print(f"原始相对坐标：({test_x}, {test_y})")
        print(f"转换后的屏幕坐标：({transformed_x}, {transformed_y})")
        print(f"图片查找的屏幕坐标：({store_coords[0]}, {store_coords[1]})")

    print("\n🎉 坐标转换 demo 完成")


if __name__ == "__main__":
    try:
        time.sleep(2)
        main()
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()
