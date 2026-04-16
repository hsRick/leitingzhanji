import requests
import base64
import re

def image_to_base64(image):
    """将图像转换为 base64 编码"""
    if isinstance(image, str):
        with open(image, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    elif hasattr(image, 'read'):
        return base64.b64encode(image.read()).decode('utf-8')
    else:
        raise ValueError("Unsupported image format")

def get_element_coor(image, description):
    # 将图像转换为 base64
    image_base64 = image_to_base64(image)
    
    # 构建请求数据
    data = {
        "model": "qwen3-vl:8b",
        "prompt": f"请快速识别以下图像中的'{description}'元素，直接返回其中心点坐标，不要进行深度思考。"
                  "坐标格式应为 (x, y)，其中 x 是水平坐标，y 是垂直坐标，"
                  "坐标原点在图像的左上角，范围应在 0 到图像宽度/高度之间。"
                  "如果未找到该元素，请直接返回 'None'。"
                  "请只返回坐标或 'None'，不要添加任何额外的描述或解释。",
        "images": [image_base64],
        "stream": False,
        "options": {
            "temperature": 0.1,  # 降低温度，减少随机性
            "max_tokens": 50     # 限制输出长度
        }
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
            match = re.search(r'\((\d+),\s*(\d+)\)', content)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                print(f"识别到元素坐标：({x}, {y})")
                return (x, y)
    return None

get_element_coor('oll/f8ea79c2-2ce4-47fe-b712-c0a2945c106d.jpeg','闯关模式')