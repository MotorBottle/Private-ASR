import os
import logging
import requests
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# OpenAI API 基本URL（如果未在 .env 中指定）
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def openai_call(api_key=None, 
                model="gpt-3.5-turbo", 
                system_content=None, 
                user_content="如何做西红柿炖牛腩？", 
                api_base=None):
    """直接使用 requests 与 OpenAI API 交互"""
    
    # 如果没有提供 API Key，则尝试从 .env 文件加载
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API Key is required but not provided.")
    
    # 如果没有提供 API Base，则尝试从 .env 文件加载
    api_base = api_base or os.getenv('OPENAI_API_BASE')
    
    # 设置请求头
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 设置消息内容
    if system_content:
        messages = [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ]
    else:
        messages = [
            {'role': 'user', 'content': user_content}
        ]
    
    # 构造请求的 payload
    payload = {
        'model': model,
        'messages': messages
    }
    
    # 使用自定义 API Base，或使用默认的 OpenAI API URL
    api_url = api_base or OPENAI_API_URL

    # 发起请求
    response = requests.post(api_url, json=payload, headers=headers)

    # 处理响应
    if response.status_code == 200:
        chat_completion = response.json()
        logging.info("OpenAI model inference done.")
        return chat_completion['choices'][0]['message']['content']
    else:
        logging.error(f"Error: {response.status_code} - {response.text}")
        return "API 请求失败"