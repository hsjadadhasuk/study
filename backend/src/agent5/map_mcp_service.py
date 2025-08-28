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

mcp = FastMCP("IP Service")
@mcp.tool()
async def ip_loc():
    url = "https://restapi.amap.com/v3/ip"
    params = {
        "key":"05787d3ee5e222b389a6c0fa6a4e4318"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("status") != "1":
        raise ValueError(data.get("info", "查询失败"))
    result = f"ip在{data.get('city')}"
    return {
        "messages":result
    }
if __name__ == "__main__":
    # MCP 服务运行在 stdio，供客户端连接
    mcp.run(transport="stdio")