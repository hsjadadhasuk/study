from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from state3 import AgentState
from langgraph.graph import add_messages
from langchain_openai import ChatOpenAI
import json
from prompts3 import refinement_prompt
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
def expression_refinement_node(state:AgentState) -> Dict:
    latest_message = state["messages"][-1].content
    chain = refinement_prompt | llm
    refined_message = chain.invoke({"message": latest_message}).content
    print("Refined message:", refined_message)
    return {"refined_message": refined_message}

def model_router(state: AgentState):
    query = state["refined_message"]
    if "翻译" in query:
        return {"model_selection": "model1"}
    elif "总结" in query:
        return {"model_selection": "model2"}
    else:
        return {"model_selection": "default_model"}  # 默认模型

def model_executor(state: AgentState):
    model_id = state["model_selection"]
    response = f"调用{model_id}"
    return {"messages": [AIMessage(content=response)]}