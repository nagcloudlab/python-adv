from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# Load API key
load_dotenv()

# 1️⃣ Define a Python function (tool)
@tool
def get_python_usage() -> str:
    """
    Returns common use cases of Python.
    """
    return (
        "Python is used in web development, data analysis, "
        "artificial intelligence, automation, and scripting."
    )

@tool
def get_current_time() -> str:
    """
    Returns the current system time.
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 2️⃣ Initialize model with tools
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

llm_with_tools = llm.bind_tools([get_python_usage, get_current_time])

# 3️⃣ Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}")
])

chain = prompt | llm_with_tools

# 4️⃣ User input
user_question = "date?"

# 5️⃣ Invoke AI
response = chain.invoke({"input": user_question})

# 6️⃣ If AI decides to call a function
if response.tool_calls:
    for tool_call in response.tool_calls:
        if tool_call["name"] == "get_python_usage":
            tool_result = get_python_usage.invoke({})
            print("🔧 Function Executed")
            print("Result:", tool_result)
        if tool_call["name"] == "get_current_time":
            tool_result = get_current_time.invoke({})
            print("🔧 Function Executed")
            print("Result:", tool_result)    
else:
    print("AI:", response.content)
