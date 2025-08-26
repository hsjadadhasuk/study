from langchain_core.prompts import ChatPromptTemplate
intent_prompt = ChatPromptTemplate.from_template("""
You are a user intent analysis assistant. A user enters a message {latest_message}, and you need to analyze the user's intent based on this message.
Intents are categorized into three types: weather, time, and model. If the user wants to query the weather, the intent should include weather; if the user wants to query the time, the intent should include time; 
if the user has other needs, such as translation or text summary, the intent should include model.

Here are some guidelines:

1. The intent may be one, two, or even three. You need to maximize the user's intent.

2. Define the parameters for each intent. The parameter for weather is city, the parameter for time is location, and the model parameter is empty.
 You need to find the corresponding parameters in {latest_message} yourself. 

3.Output must be **valid JSON only**, strictly following this format:
for example：
{{
"intent":["weather","time"],
"task_params":{{
"weather":{{"city":Beijing}}
"time": {{"location":Beijing}}
}}
｝｝
""")