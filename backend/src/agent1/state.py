from typing import TypedDict
from typing import Literal, Annotated
from langgraph.graph import add_messages
class IntentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: list[Literal["models", "weather_tool","time_tool"]]
    task_params:dict
    intent_summary:str
    latest_message:str

