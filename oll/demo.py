import os
import requests
import json

# ---------------------- 1. 定义自定义工具 ----------------------
def calculator(expression: str) -> str:
    """
    数学计算器，支持加减乘除、平方、开方等运算
    参数: expression (str): 数学表达式，例如 "2+3*5"
    """
    try:
        expression = expression.replace("^", "**")
        return f"计算结果: {eval(expression)}"
    except Exception as e:
        return f"计算失败: {str(e)}"

def search_weather(city: str) -> str:
    """
    查询指定城市的天气
    参数: city (str): 城市名称，例如 "北京"
    """
    # 模拟天气接口（真实场景可替换为天气API）
    weather_data = {
        "北京": "晴天，25℃",
        "上海": "多云，28℃",
        "广州": "小雨，26℃"
    }
    return weather_data.get(city, f"未找到{city}的天气信息")

# 工具列表
tools = {
    "calculator": calculator,
    "search_weather": search_weather
}

# ---------------------- 2. 调用本地 ollama 模型 ----------------------
def call_ollama(prompt: str) -> str:
    """
    调用本地 ollama 模型
    """
    data = {
        "model": "qwen3-vl:8b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "max_tokens": 500
        }
    }
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        response_json = response.json()
        return response_json.get("response", "")
    else:
        return f"Error: {response.status_code}"

# ---------------------- 3. 简单的 Agent 逻辑 ----------------------
def run_agent(input_text: str) -> str:
    """
    简单的 Agent 逻辑
    """
    # 构建包含工具信息的提示词
    tool_info = """
可用工具:
1. calculator(expression: str): 数学计算器，支持加减乘除、平方、开方等运算
2. search_weather(city: str): 查询指定城市的天气

请严格按照以下格式返回:
- 如果需要使用工具，返回: 工具名称(参数)
- 如果不需要使用工具，直接返回答案
    """
    
    prompt = f"你是一个智能助手，必须严格使用提供的工具回答问题，不要编造信息。\n{tool_info}\n\n问题: {input_text}"
    
    # 调用模型
    response = call_ollama(prompt)
    print(f"模型响应: {response}")

    # 收集所有工具调用
    import re
    tool_calls = []
    for tool_name, tool_func in tools.items():
        matches = re.findall(f"{tool_name}\\(([^)]+)\\)", response)
        for match in matches:
            args = match.strip().strip('"').strip("'")
            tool_calls.append((tool_name, args, tool_func))

    # 执行所有工具调用
    if tool_calls:
        tool_results = []
        for tool_name, args, tool_func in tool_calls:
            result = tool_func(args)
            tool_results.append(f"{tool_name}({args}): {result}")
            print(f"工具调用结果: {result}")

        # 再次调用模型获取最终答案
        tool_result_str = "\n".join(tool_results)
        follow_up_prompt = f"工具调用结果:\n{tool_result_str}\n请基于此结果回答原始问题: {input_text}"
        final_response = call_ollama(follow_up_prompt)
        return final_response

    return response

# ---------------------- 4. 运行 Agent ----------------------
if __name__ == "__main__":
    # 测试问题 1：需要调用工具
    question1 = "北京今天天气多少度？3的平方加上10等于多少？"
    
    # 测试问题 2：无需调用工具
    question2 = "你好，你是谁？"
    
    # 执行
    result = run_agent(question1)
    print("\n=== 最终回答 ===")
    print(result)