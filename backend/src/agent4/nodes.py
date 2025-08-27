from typing import Dict, Any
from mcp import ClientSession

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
import asyncio
from mcp.server import Server
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.server.fastmcp import FastMCP
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
       LangGraph 节点，接收 state 中的 task_params，调用 MCP 服务返回天气
       """
    task_params = state.get("task_params", {})
    city = task_params.get("weather", {}).get("city", "北京")

    # 异步调用 MCP
    weather_info = asyncio.run(call_weather(city))

    return {
        "messages": [weather_info]
    }
def model_tool_node(state):
    message = "调用模型"
    print(message)
    return {"message": message}
def merge_node(state):
    num = len(state["intent"])
    message = state["messages"][-num:]
    return {"messages": message}
async def call_weather(city: str) -> str:
    """
    使用 MCP 调用 weather_service 的 get_weather 工具
    """
    # 显式传递环境变量，保证 MCP 子进程能读取到 API_KEY
    env = os.environ.copy()
    api_key = "d093aac5e2272e9861a53c1c30f8fad3"
    if not api_key:
        raise ValueError("缺少 OPENWEATHER_API_KEY")

    params = StdioServerParameters(
        command="python",
        args=["weather_service.py"],
        env=env
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_weather", {"city": city})
            # MCP 返回的内容在 result.content[0].text
            if result.content and hasattr(result.content[0], "text"):
                return result.content[0].text
            else:
                return "MCP 返回为空"