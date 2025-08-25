from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
#from state2 import IntentState
from langgraph.graph import add_messages
from langchain_openai import ChatOpenAI
#from prompts import intent_prompt
import json
import os
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
#Time Tool
@tool
def time_tool(location: str) -> str:
    """
    查询指定城市的当前时间。
    参数:
        location: 城市名，例如 "上海"、"纽约"。
    返回:
        一个字符串，形如 "上海 当前时间是 2025-08-23 12:34:56"
    """
    try:
        mapping = {
            "北京": "Asia/Shanghai",
            "上海": "Asia/Shanghai",
            "纽约": "America/New_York",
            "伦敦": "Europe/London",
        }
        timezone = mapping.get(location, "Asia/Shanghai")

        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        return f"{location} 当前时间是 {current_time}"

    except Exception as e:
        return f"查询时间失败，错误: {str(e)}"
#Weather Tool
@tool
def weather_tool(city: str):
    """
    查询指定城市的实时天气
    依赖 OpenWeatherMap API
    参数：
        city: 城市名，例如 "上海"、"纽约"。
    返回：
        当前城市天气
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
        location = city
        location = city_map.get(location, location)
        api_key = os.getenv("OPENWEATHER_API_KEY")
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