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