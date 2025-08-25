from nodes import intent_analysis_node,llm,time_tool_node,weather_tool_node
from state import IntentState
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
import os
graph = StateGraph(IntentState)
graph.add_node("intent_analysis_node", intent_analysis_node)
graph.add_node("time_tool_node",time_tool_node)
graph.add_node("weather_tool_node",weather_tool_node)
graph.add_edge(START, "intent_analysis_node")
graph.add_edge("intent_analysis_node", "time_tool_node")
graph.add_edge("time_tool_node","weather_tool_node")
graph.add_edge("weather_tool_node", END)
agent = graph.compile()
events = agent.stream(
    {"messages": "我想知道上海时间和上海的天气"}
)
for event in events:
    print(event)