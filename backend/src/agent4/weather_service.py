from mcp.server import Server
from mcp.server.fastmcp import FastMCP
import asyncio
import os
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from state import IntentState
from langgraph.graph import add_messages
from langchain_openai import ChatOpenAI
from prompts import intent_prompt,refinement_prompt
import json
import os
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Weather Service")
@mcp.tool()
async def get_weather(city:str):
    """
    查询实时天气
    依赖 OpenWeatherMap API
    """
    try:
        city_map = {
            "北京": "Beijing",
            "上海": "Shanghai",
            "广州": "Guangzhou",
            "深圳": "Shenzhen",
            "南京": "Nanjing",
            "杭州": "Hangzhou",
            # 需要的话可以继续补充
        }
        location = city_map.get(city, city)
        api_key = "d093aac5e2272e9861a53c1c30f8fad3"
        if not api_key:
            raise ValueError("缺少 OPENWEATHER_API_KEY，请在环境变量或 .env 中设置")

        # 调用 OWM API
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "lang": "zh_cn",  # 中文返回
            "units": "metric" # 摄氏度
        }

        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            raise ValueError(data.get("message", "查询失败"))

        # 解析结果
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]

        result = f"{location} 当前天气：{weather}，气温 {temp}℃，体感 {feels_like}℃"

        return {"messages": result}

    except Exception as e:
        return {"messages": f"查询天气失败，错误: {str(e)}"}
if __name__ == "__main__":
    # MCP 服务运行在 stdio，供客户端连接
    mcp.run(transport="stdio")