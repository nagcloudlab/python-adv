from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Python trainer for fresh graduates."),
    ("human", "What is Artificial Intelligence?")
])

chain = prompt | llm
response = chain.invoke({})

print(response.content)
