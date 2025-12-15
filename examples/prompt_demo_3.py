from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You explain concepts to freshers."),
    ("human", "Explain Machine Learning in 5 bullet points, simple language.")
])

chain = prompt | llm
response = chain.invoke({})

print(response.content)
