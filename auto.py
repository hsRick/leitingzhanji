import pyautogui
import time
import sys

# 检测是否为 Retina 显示器
def is_retina():
    if sys.platform == 'darwin':
        import subprocess
        output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode('utf-8')
        return 'Retina' in output
    return False

# 获取微信小程序窗口位置
def get_wechat_miniprogram_window():
    """获取微信小程序窗口的位置和大小"""
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

        # 收集所有微信窗口
        wechat_windows = []
        for window in window_list:
            owner_name = window.get("kCGWindowOwnerName", "")
            window_title = window.get("kCGWindowName", "")
            
            # 调试：打印所有窗口信息
            if "微信" in owner_name or "WeChat" in owner_name or "雷霆战机" in window_title:
                bounds = window.get("kCGWindowBounds", {})
                left = bounds.get("X", 0)
                top = bounds.get("Y", 0)
                width = bounds.get("Width", 0)
                height = bounds.get("Height", 0)
                print(f"  窗口：{window_title} (所有者: {owner_name}) - 位置: {left},{top} 大小: {width}x{height}")
                
                # 只考虑在屏幕内的窗口
                if left >= 0 and top >= 0 and width > 200 and height > 200:
                    wechat_windows.append({
                        "title": window_title,
                        "left": int(left),
                        "top": int(top),
                        "width": int(width),
                        "height": int(height),
                        "area": int(width * height)
                    })
        
        # 优先选择雷霆战机：集结窗口
        thunder_fighter_window = None
        for window in wechat_windows:
            if "雷霆战机：集结" in window["title"]:
                thunder_fighter_window = window
                break
        
        # 如果找到雷霆战机窗口，使用它
        if thunder_fighter_window:
            print(f"选择微信窗口：{thunder_fighter_window['title']} (面积: {thunder_fighter_window['area']})")
            
            return {
                "left": thunder_fighter_window["left"],
                "top": thunder_fighter_window["top"],
                "width": thunder_fighter_window["width"],
                "height": thunder_fighter_window["height"]
            }
        
        # 否则按面积排序选择最大的窗口
        elif wechat_windows:
            # 按面积降序排序
            wechat_windows.sort(key=lambda w: w["area"], reverse=True)
            largest_window = wechat_windows[0]
            print(f"选择微信窗口：{largest_window['title']} (面积: {largest_window['area']})")
            
            return {
                "left": largest_window["left"],
                "top": largest_window["top"],
                "width": largest_window["width"],
                "height": largest_window["height"]
            }
        
        return None
    except Exception as e:
        print(f"获取窗口失败：{e}")
        return None

# 初始化时检测 Retina 显示器
RETINA = is_retina()

# ====================== 【你只需要改这里】 ======================
# 循环次数：0 = 无限循环
LOOP_TIMES = 2

# 每一步等待时间（秒）
AFTER_WAIT = 1

# 动作列表：
# 支持：
# ["find", "图片路径.png"]   → 自动找图并点击
# ["key", "按键"]            → 按键盘
# ["wait", 秒数]             → 等待
# ["click", x, y]            → 手动点击坐标
ACTIONS = [
    ["find", "guanggao.png"],   # 自动找屏幕上的 guanggao.png 并点击
    ["wait", 0.5],
    ["find", "closed.png"],   # 自动找屏幕上的 closed.png 并点击
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
    count = 1
    print("🚀 自动按键精灵已启动（Ctrl+C 停止）")
    
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
    
    # 执行主循环
    while True:
        if LOOP_TIMES > 0 and count > LOOP_TIMES:
            break
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
        
        # 只有所有动作都成功执行，才增加轮次计数
        if action_success:
            count += 1


if __name__ == "__main__":
    try:
        time.sleep(2)
        run_loop()
    except KeyboardInterrupt:
        print("\n🛑 已停止")
        sys.exit()
