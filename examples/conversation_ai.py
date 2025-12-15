from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

# Load API key
load_dotenv()

# Initialize model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("placeholder", "{history}"),
    ("human", "{input}")
])

# Chain = Prompt + Model
chain = prompt | llm

# Create in-memory chat history
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Add memory to the chain
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

print("🤖 Conversational AI (type 'exit' to quit)\n")

session_id = "demo-session"

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    response = conversation.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )

    print("AI:", response.content)
