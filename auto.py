import pyautogui
import time
import sys
import io
from PIL import Image

# 检测是否为 Retina 显示器
def is_retina():
    if sys.platform == 'darwin':
        import subprocess
        output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode('utf-8')
        return 'Retina' in output
    return False

# 获取微信小程序窗口位置
def get_wechat_miniprogram_window():
    """获取雷霆战机：集结窗口的位置和大小"""
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

        # 直接查找雷霆战机：集结窗口
        for window in window_list:
            window_title = window.get("kCGWindowName", "")
            
            if "雷霆战机：集结" in window_title:
                bounds = window.get("kCGWindowBounds", {})
                left = bounds.get("X", 0)
                top = bounds.get("Y", 0)
                width = bounds.get("Width", 0)
                height = bounds.get("Height", 0)
                
                # 只考虑在屏幕内的窗口
                if left >= 0 and top >= 0 and width > 200 and height > 200:
                    print(f"找到雷霆战机：集结窗口 - 位置: {left},{top} 大小: {width}x{height}")
                    return {
                        "left": int(left),
                        "top": int(top),
                        "width": int(width),
                        "height": int(height)
                    }
        
        print("未找到雷霆战机：集结窗口")
        return None
    except Exception as e:
        print(f"获取窗口失败：{e}")
        return None

# 初始化时检测 Retina 显示器
RETINA = is_retina()

# ====================== 【你只需要改这里】 ======================
# 循环次数（必须 > 0）
LOOP_TIMES = 2

# 每一步等待时间（秒）
AFTER_WAIT = 1

# 动作列表：
# 支持：
# ["find", "图片路径.png"]   → 自动找图并点击
# ["find_text", "文本"]       → 根据文本查找并点击（使用 macOS OCR）
# ["key", "按键"]            → 按键盘
# ["wait", 秒数]             → 等待
# ["click", x, y]            → 手动点击坐标
ACTIONS = [
    ["find", "guanggao.png"],   # 自动找屏幕上的 guanggao.png 并点击
    ["wait", 0.5],
    ["find_text", "关闭"],       # 根据文本"关闭"查找并点击
    # ["find", "closed.png"],   # 自动找屏幕上的 closed.png 并点击
    # ["key", "enter"],
    # ["wait", 0.5],
]

# 找图精度（0.8~0.99，越接近1越严格）
CONFIDENCE = 0.85


# ====================== 以下不用动 ======================

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


def find_text_ocr(text, window=None):
    """
    使用 macOS Vision 框架在屏幕或窗口中查找文本并返回中心点坐标
    
    参数:
        text: 要查找的文本
        window: 窗口信息字典 (可选)，包含 left, top, width, height
    
    返回:
        (x, y) 坐标或 None
    """
    try:
        from Quartz import (
            CGWindowListCreateImage,
            CGRectNull,
            kCGWindowImageBoundsIgnoreFraming,
            kCGWindowImageDefault,
        )
        from Vision import VNRecognizeTextRequest, VNImageRequestHandler, VNImageOptionProperties
        import objc
        
        # 截取屏幕或窗口
        if window:
            # 截取指定窗口区域
            screenshot = pyautogui.screenshot(region=(
                window["left"],
                window["top"],
                window["width"],
                window["height"]
            ))
        else:
            # 截取全屏
            screenshot = pyautogui.screenshot()
        
        # 转换为 PNG 数据
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # 创建 Vision 请求
        recognized_texts = []
        bounding_boxes = []
        
        def handle_request(request, error):
            if error:
                print(f"OCR 错误: {error}")
                return
            results = request.results()
            if results:
                for result in results:
                    recognized_texts.append(result.topCandidates_(1)[0].string())
                    bounding_boxes.append(result.boundingBox())
        
        request = VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handle_request)
        request.setRecognitionLevel_(1)  # 1 = accurate, 0 = fast
        
        # 创建图像请求处理器
        handler = VNImageRequestHandler.alloc().initWithData_options_(
            img_buffer.read(),
            None
        )
        
        # 执行请求
        success, error = handler.performRequests_error_([request], None)
        
        if not success:
            print(f"OCR 执行失败: {error}")
            return None
        
        # 查找匹配的文本
        for i, recognized_text in enumerate(recognized_texts):
            if text in recognized_text:
                print(f"找到文本 '{text}' 在: '{recognized_text}'")
                # 获取边界框并转换为屏幕坐标
                box = bounding_boxes[i]
                # Vision 框架返回的是归一化坐标 (0-1)，原点在左下角
                img_width, img_height = screenshot.size
                
                # 转换坐标：左下角 → 左上角
                center_x_normalized = box.origin.x + box.size.width / 2
                center_y_normalized = 1 - (box.origin.y + box.size.height / 2)
                
                # 转换为像素坐标
                if window:
                    center_x = window["left"] + int(center_x_normalized * window["width"])
                    center_y = window["top"] + int(center_y_normalized * window["height"])
                else:
                    center_x = int(center_x_normalized * img_width)
                    center_y = int(center_y_normalized * img_height)
                
                return (center_x, center_y)
        
        print(f"未找到文本 '{text}'")
        return None
        
    except ImportError as e:
        print(f"需要 macOS Vision 框架: {e}")
        return None
    except Exception as e:
        print(f"OCR 查找失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def find_text_and_click(text):
    """
    根据文本查找并点击
    
    参数:
        text: 要查找的文本
        
    返回:
        是否成功
    """
    try:
        print(f"正在查找文本：{text}")
        
        # 获取微信小程序窗口位置
        print("查找微信小程序窗口...")
        window = get_wechat_miniprogram_window()
        if window:
            print(f"限制在微信小程序窗口内查找：{window}")
        else:
            print("未找到微信小程序窗口，将在全屏查找")
        
        # 尝试多次查找
        for i in range(3):
            pos = find_text_ocr(text, window)
            if pos:
                x, y = pos
                print(f"找到文本位置：{x}, {y}")
                
                # 修复坐标
                fixed_x, fixed_y = fix_coordinates(x, y)
                print(f"修复后的坐标：{fixed_x}, {fixed_y}")
                
                # 移动到位置并点击
                pyautogui.moveTo(fixed_x, fixed_y, duration=0.5)
                time.sleep(0.5)
                pyautogui.click()
                print(f"✅ 找到并点击：{fixed_x}, {fixed_y}")
                return True
            else:
                print(f"第 {i+1} 次未找到，重试...")
                time.sleep(0.5)
        
        print("❌ 未找到目标文本")
        return False
        
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        print(traceback.format_exc())
        return False


def find_and_click(image_path):
    try:
        print(f"正在寻找：{image_path}")

        # 获取微信小程序窗口位置
        print("查找微信小程序窗口...")
        window = get_wechat_miniprogram_window()
        if window:
            print(f"限制在微信小程序窗口内查找：{window}")
        else:
            print("未找到微信小程序窗口，将在全屏查找")

        # 尝试多次找图，提高成功率
        for i in range(3):
            try:
                # 如果在窗口内查找，使用 region 参数
                if window:
                    pos = pyautogui.locateOnScreen(
                        image_path,
                        confidence=CONFIDENCE,
                        region=(
                            window["left"],
                            window["top"],
                            window["width"],
                            window["height"],
                        ),
                    )
                else:
                    pos = pyautogui.locateOnScreen(image_path, confidence=CONFIDENCE)

                if pos:
                    x, y = pyautogui.center(pos)
                    print(f"找到图片位置：{x}, {y}")
                    
                    # 修复坐标
                    fixed_x, fixed_y = fix_coordinates(x, y)
                    print(f"修复后的坐标：{fixed_x}, {fixed_y}")

                    # 移动到位置并点击
                    pyautogui.moveTo(fixed_x, fixed_y, duration=0.5)
                    time.sleep(0.5)
                    pyautogui.click()
                    print(f"✅ 找到并点击：{fixed_x}, {fixed_y}")
                    return True
            except pyautogui.ImageNotFoundException:
                # 尝试降低置信度重试
                if i < 2:
                    try:
                        # 如果在窗口内查找，使用 region 参数
                        if window:
                            pos = pyautogui.locateOnScreen(
                                image_path,
                                confidence=CONFIDENCE - 0.05,
                                region=(
                                    window["left"],
                                    window["top"],
                                    window["width"],
                                    window["height"],
                                ),
                            )
                        else:
                            pos = pyautogui.locateOnScreen(image_path, confidence=CONFIDENCE - 0.05)

                        if pos:
                            x, y = pyautogui.center(pos)
                            # 修复坐标
                            fixed_x, fixed_y = fix_coordinates(x, y)
                            # 移动到位置并点击
                            pyautogui.moveTo(fixed_x, fixed_y, duration=0.5)
                            time.sleep(0.5)
                            pyautogui.click()
                            print(f"✅ 找到并点击：{fixed_x}, {fixed_y}")
                            return True
                    except:
                        pass
            except Exception as e:
                print(f"找图失败：{e}")
            finally:
                time.sleep(0.5)
        print("❌ 未找到目标元素")
        return False
    except Exception as e:
        print(f"错误：{e}")
        return False


def run_action(act):
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
    time.sleep(AFTER_WAIT)
    return True


def run_loop():
    print("🚀 自动按键精灵已启动（Ctrl+C 停止）")
    
    # 确保循环次数有效，防止无限循环
    max_loops = max(1, LOOP_TIMES)
    print(f"将执行 {max_loops} 轮循环")
    
    # 首先全屏查找 icon 并点击
    print("\n===== 启动阶段 =====")
    print("正在全屏查找 icon...")
    
    # 尝试多次查找 icon
    icon_found = False
    for i in range(3):
        try:
            # 全屏查找 icon
            pos = pyautogui.locateOnScreen("icon.png", confidence=CONFIDENCE)
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
        except Exception as e:
            print(f"查找 icon 失败：{e}")
            time.sleep(1)
    
    if not icon_found:
        print("❌ 未找到 icon，继续执行后续操作")
    
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
        



if __name__ == "__main__":
    try:
        time.sleep(2)
        run_loop()
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()
