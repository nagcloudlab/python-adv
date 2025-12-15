from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


# Load API key from .env
load_dotenv()

# Initialize OpenAI model via LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
)

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])

# Combine prompt + model
chain = prompt | llm


# FastAPI application
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    response = chain.invoke({
        "question": request.question
    })
    return {"answer": response}

