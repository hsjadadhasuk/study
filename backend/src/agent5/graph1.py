from nodes import intent_analysis_node,llm,time_tool_node,weather_tool_node,model_tool_node,merge_node,expression_refinement_node
from state import IntentState
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
import os
from nodes import ip_node
def route(state: IntentState):
    intent = state.get("intent", [])
    return intent
graph = StateGraph(IntentState)
graph.add_node("expression_refinement_node",expression_refinement_node)
graph.add_node("intent_analysis_node", intent_analysis_node)
graph.add_node("time_tool_node",time_tool_node)
graph.add_node("weather_tool_node",weather_tool_node)
graph.add_node("model_tool_node",model_tool_node)
graph.add_node("merge_node",merge_node)
graph.add_node("ip",ip_node)
graph.add_edge(START, "expression_refinement_node")
graph.add_edge("expression_refinement_node","intent_analysis_node")
graph.add_conditional_edges(
    "intent_analysis_node",
    route,
    {
        "time": "time_tool_node",
        "weather": "weather_tool_node",
        "model": "model_tool_node",
    },
)
graph.add_edge("time_tool_node", "merge_node")
graph.add_edge("weather_tool_node", "merge_node")
graph.add_edge("model_tool_node", "merge_node")
graph.add_edge("merge_node", "ip")
graph.add_edge("ip",END)
agent = graph.compile()
events = agent.stream(
    {"messages": "现在是上海什么时间和天气，还有我想要翻译文本"}
)
for event in events:
    print(event)