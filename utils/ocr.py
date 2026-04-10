#!/usr/bin/env python3
"""
OCR 文字识别工具模块

提供基于 macOS Vision 框架的文字识别功能
"""

import io
from PIL import Image
import pyautogui

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
        # 检查必要的模块是否可用
        from Quartz import (
            CGWindowListCreateImage,
            CGRectNull,
            kCGWindowImageBoundsIgnoreFraming,
            kCGWindowImageDefault,
        )
        from Vision import VNRecognizeTextRequest, VNImageRequestHandler, VNImageOptionProperties
        import objc
    except ImportError:
        print(f"❌ OCR 功能不可用：缺少必要的模块")
        print(f"💡 提示：如需使用 OCR 文本查找功能，请运行: pip install pyobjc")
        print(f"💡 或者使用图片查找功能 (['find', 'xxx.png'])")
        return None
    
    try:
        # 优先全屏截图（更可靠）
        screenshot = pyautogui.screenshot()
        screenshot_region = None  # 标记是全屏截图
        
        # 保存截图用于调试
        screenshot.save('debug_ocr_screenshot.png')
        print(f"📸 已保存 OCR 调试截图: debug_ocr_screenshot.png")
        print(f"📸 截图尺寸: {screenshot.size}")
        
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
        request.setRecognitionLevel_(0)  # 0 = fast, 1 = accurate (快速模式可能更适合中文)
        
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
        
        # 打印所有识别到的文本（调试用）
        print(f"🔍 OCR 识别到的所有文本: {recognized_texts}")
        
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
                
                # 转换为像素坐标（总是全屏截图）
                center_x = int(center_x_normalized * img_width)
                center_y = int(center_y_normalized * img_height)
                
                return (center_x, center_y)
        
        print(f"未找到文本 '{text}'")
        return None
        
    except Exception as e:
        print(f"OCR 查找失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None
