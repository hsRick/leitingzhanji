#!/usr/bin/env python3
"""
窗口管理工具模块

提供窗口查找、获取窗口信息等功能，特别是针对微信小程序窗口的处理
"""

def get_thunder_fighter_window():
    """
    获取雷霆战机：集结窗口的位置和大小
    
    返回:
        dict: 窗口信息字典，包含 left, top, width, height，未找到返回 None
    """
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

        print("\n=== 调试：所有微信相关窗口 ===")
        # 直接查找雷霆战机：集结窗口
        for window in window_list:
            owner_name = window.get("kCGWindowOwnerName", "")
            window_title = window.get("kCGWindowName", "")
            
            # 打印所有微信相关窗口（调试用）
            if "微信" in owner_name or "WeChat" in owner_name or "雷霆" in window_title:
                bounds = window.get("kCGWindowBounds", {})
                left = bounds.get("X", 0)
                top = bounds.get("Y", 0)
                width = bounds.get("Width", 0)
                height = bounds.get("Height", 0)
                print(f"窗口标题: '{window_title}' | 所有者: '{owner_name}' | 位置: {left},{top} | 大小: {width}x{height}")
            
            # 尝试匹配雷霆战机窗口（多种变体）
            if "雷霆战机" in window_title or "雷霆" in window_title:
                bounds = window.get("kCGWindowBounds", {})
                left = bounds.get("X", 0)
                top = bounds.get("Y", 0)
                width = bounds.get("Width", 0)
                height = bounds.get("Height", 0)
                
                # 只考虑在屏幕内的窗口
                if left >= 0 and top >= 0 and width > 200 and height > 200:
                    print(f"\n✅ 找到雷霆战机窗口 - 位置: {left},{top} 大小: {width}x{height}")
                    return {
                        "left": int(left),
                        "top": int(top),
                        "width": int(width),
                        "height": int(height)
                    }
        
        print("\n未找到雷霆战机：集结窗口")
        return None
    except Exception as e:
        print(f"获取窗口失败：{e}")
        import traceback
        print(traceback.format_exc())
        return None


def is_retina():
    """
    检测是否为 Retina 显示器
    
    返回:
        bool: 是否为 Retina 显示器
    """
    import sys
    if sys.platform == 'darwin':
        import subprocess
        output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode('utf-8')
        return 'Retina' in output
    return False
