from nodes3 import llm,expression_refinement_node, model_router, model_executor
from state3 import AgentState
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
import os
builder = StateGraph(AgentState)
builder.add_node("router", model_router)
builder.add_node("execute", model_executor)
builder.add_node("expression_refinement_node", expression_refinement_node)
builder.add_edge(START, "expression_refinement_node")
builder.add_edge("expression_refinement_node","router")
builder.add_edge("router","execute")
builder.add_edge("execute", END)
agent=builder.compile()
events = agent.stream(
    {"messages": "我想要翻译hello"}
)
for event in events:
    print(event)