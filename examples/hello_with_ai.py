from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


# Load API key from .env
load_dotenv()

# Initialize OpenAI model via LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])

# Combine prompt + model
chain = prompt | llm

# Invoke the chain
response = chain.invoke({
    "question": "Explain Artificial Intelligence in simple terms for a fresher."
})

print(response.content)
