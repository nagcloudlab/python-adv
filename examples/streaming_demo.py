from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load API key
load_dotenv()

# Initialize model with streaming enabled
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    streaming=True
)

# Simple prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You explain concepts clearly for freshers."),
    ("human", "Explain Artificial Intelligence in simple terms.")
])

# Chain
chain = prompt | llm

print("🤖 AI (streaming response):\n")

# Stream response token by token
for chunk in chain.stream({}):
    if chunk.content:
        print(chunk.content, end="", flush=True)

print("\n\n--- Stream End ---")
