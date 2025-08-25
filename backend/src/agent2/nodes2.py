from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from state2 import IntentState
from langgraph.graph import add_messages
from langchain_openai import ChatOpenAI
import json
from langgraph.prebuilt import ToolNode, tools_condition
import os
from tools import time_tool,weather_tool
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv
llm = ChatOpenAI(
model="Qwen/Qwen2.5-72B-Instruct",
# model='Pro/deepseek-ai/DeepSeek-R1',
openai_api_key="sk-firpeftdsrvktaueszxtomtsizlqhkzifuqzizxdaxobmmql",
openai_api_base="https://api.siliconflow.cn/v1",
)
tools=[time_tool,weather_tool]
model=llm.bind_tools(tools)
tool_node = ToolNode(tools, handle_tool_errors=True)
# Intent Analysis Node
def intent_analysis_node(state: IntentState) -> Dict:
    latest_message = state["messages"][-1]
    message = [latest_message]
    # 调用 LLM
    result = model.invoke(message)
    return {
        "messages": [result]
    }