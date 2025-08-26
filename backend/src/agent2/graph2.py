from state2 import IntentState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
import os
from nodes2 import model,intent_analysis_node,tool_node
graph = StateGraph(IntentState)
graph.add_node("intent_analysis_node", intent_analysis_node)
graph.add_node("tools",tool_node)
graph.add_edge(START, "intent_analysis_node")
graph.add_conditional_edges("intent_analysis_node", tools_condition)
agent = graph.compile()
events = agent.stream( {"messages": [("human", "你可以告诉我现在的上海时间和上海天气吗")]})
for event in events:
    print(event)