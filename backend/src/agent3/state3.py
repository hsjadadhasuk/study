from typing import TypedDict
from typing import Literal, Annotated
from langgraph.graph import add_messages
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # 消息累积
    model_selection: str  # 当前选定模型
    refined_message: str