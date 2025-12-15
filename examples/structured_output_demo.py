from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load API key
load_dotenv()

# Initialize model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)

# Prompt enforcing structured JSON output
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI that always responds in valid JSON."),
    ("human", """
Explain Python for a fresher.
Respond ONLY in the following JSON format:
\'{{\n
  "language": "",
  "difficulty": "",
  "used_for": [],
  "summary": ""
}}\'
""")
])

# Create chain
chain = prompt | llm

# Invoke
response = chain.invoke({})

print(response.content)
