from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

prompt = ChatPromptTemplate.from_messages([
    ("human", "{question}")
])

chain = prompt | llm

questions = [
    "Explain AI",
    "Explain AI for a fresher",
    "Explain AI for a fresher using a real-life analogy"
]

for q in questions:
    response = chain.invoke({"question": q})
    print(f"\nQ: {q}")
    print(f"A: {response.content}")
