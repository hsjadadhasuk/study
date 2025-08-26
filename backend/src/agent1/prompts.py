from langchain_core.prompts import ChatPromptTemplate
refinement_prompt = ChatPromptTemplate.from_messages([
        ("system", """
你是一个表达优化助手。你的任务是将用户的自然语言请求转化为更清晰、简洁、规范的表达。
要求：
1. 不改变原本的意图。
2. 删除模糊的口语化表达，保留关键信息。
3. 输出一条优化后的指令性语句。
        """),
        ("human", "用户输入: {message}")
    ])
intent_prompt = ChatPromptTemplate.from_template("""
You are a user intent analysis assistant. A user enters a message {refined_message}, and you need to analyze the user's intent based on this message.
Intents are categorized into three types: weather, time, and model.  
- If the user explicitly asks about the weather, the intent should include "weather".  
- If the user explicitly asks about the time, the intent should include "time".  
- For any other requests (e.g., translation, summarization, or other tasks), the intent should include "model".  
Instructions:
1. The intent may be one, two, or even three. You need to maximize the user's intent.

2. Define the parameters for each intent. The parameter for weather is city, the parameter for time is location, and the model parameter is empty.
 You need to find the corresponding parameters in {refined_message} yourself. 

Output：
Output must be **valid JSON only**, strictly following this format:
for example：
{{
"intent":["weather","time"],
"task_params":{{
"weather":{{"city":Beijing}}
"time": {{"location":Beijing}}
}}
｝｝
""")