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
llm = ChatOpenAI(
model="Qwen/Qwen2.5-72B-Instruct",
# model='Pro/deepseek-ai/DeepSeek-R1',
openai_api_key=os.getenv("OPENAI_API_KEY"),
openai_api_base="https://api.siliconflow.cn/v1",
)
def expression_refinement_node(state: IntentState) -> Dict:
    latest_message = state["messages"][-1].content
    chain = refinement_prompt | llm
    refined_message = chain.invoke({"message": latest_message}).content

    print("Refined message:", refined_message)

    return {"refined_message": refined_message}
# Intent Analysis Node
def intent_analysis_node(state: IntentState) -> Dict:
    latest_message = state.get("refined_message")
    current_intent = state.get("intent",[])
    #context = state["messages"][-5:]
    # 调用 LLM
    chain = intent_prompt | llm
    result = chain.invoke({
        "refined_message": latest_message
       # "context":context,
    }).content
    # JSON 解析
    try:
        parsed = json.loads(result)
        intent = parsed.get("intent", [])
        task_params = parsed.get("task_params", {})
    except Exception:
        intent = []
        task_params = {}

    if intent and intent != current_intent:
        # 记录 intent
        new_intent = intent
    else:
        new_intent = current_intent
    return {
        "intent": new_intent,
        "task_params": task_params
    }
#Time Node
def time_tool_node(state: IntentState) -> Dict:
    """
    时间查询工具节点
    输入: state["task_params"]["time"]["location"] -> 需要查询的时区 (字符串)
    输出: {"messages": [{"role": "tool", "content": "当前时间是 ..."}]}
    """
    try:
        task_params = state.get("task_params", {})
        time_params = task_params.get("time", {})

        # 如果没有 timezone，但有 location，就兜底映射
        timezone = time_params.get("timezone")
        if not timezone and "location" in time_params:
            loc = time_params["location"]
            # 简单映射（你可以扩展）
            mapping = {
                "北京": "Asia/Shanghai",
                "上海": "Asia/Shanghai",
                "纽约": "America/New_York",
                "伦敦": "Europe/London"
            }
            timezone = mapping.get(loc, "Asia/Shanghai")

        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        return {"messages": f"{time_params.get('location', timezone)} 当前时间是 {current_time}"}

    except Exception as e:
        return {"messages": f"查询时间失败，错误: {str(e)}"}
def weather_tool_node(state):
    """
    查询实时天气
    依赖 OpenWeatherMap API
    """
    try:
        task_params = state.get("task_params", {}).get("weather", {})
        city_map = {
            "北京": "Beijing",
            "上海": "Shanghai",
            "广州": "Guangzhou",
            "深圳": "Shenzhen",
            "南京": "Nanjing",
            "杭州": "Hangzhou",
            # 需要的话可以继续补充
        }
        location = task_params.get("city", "Beijing")
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
def model_tool_node(state):
    message = "调用模型"
    print(message)
    return {"message": message}
def merge_node(state):
    num = len(state["intent"])
    message = state["messages"][-num:]
    return {"messages": message}