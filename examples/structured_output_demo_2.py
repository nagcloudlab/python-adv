from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You respond only in valid JSON."),
    ("human", """
Explain {topic} for a fresher.
Use this JSON format:

\'{{\n
  "topic": "",
  "simple_explanation": "",
  "real_world_usage": [],
  "confidence_level": ""
}}\'
""")
])

chain = prompt | llm

topic = "Machine Learning"

response = chain.invoke({"topic": topic})
print(response.content)
