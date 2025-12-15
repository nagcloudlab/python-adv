from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

# BAD PROMPT
# bad_prompt = ChatPromptTemplate.from_messages([
#     ("human", "Explain Python")
# ])

# bad_chain = bad_prompt | llm
# bad_response = bad_chain.invoke({})

# print("\n❌ Bad Prompt Output:\n")
# print(bad_response.content)


# # GOOD PROMPT ( Role + Specifics )
good_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a trainer teaching freshers."),
    ("human", "Explain Python")
])

good_chain = good_prompt | llm
good_response = good_chain.invoke({})

print("\n✅ Good Prompt Output:\n")
print(good_response.content)
