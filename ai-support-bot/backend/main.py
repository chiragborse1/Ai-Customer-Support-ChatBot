from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all (safe for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load knowledge base
with open("knowledge.txt", "r", encoding="utf-8") as f:
    KNOWLEDGE = f.read()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "AI Support Bot Running"}

@app.post("/chat")
def chat(req: ChatRequest):
    prompt = f"""
You are an AI customer support chatbot.
Answer ONLY using the information below.
If the answer is not in the knowledge, say:
"I'm sorry, I don't have that information."

Knowledge Base:
{KNOWLEDGE}

User Question:
{req.message}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return {
        "reply": response.json()["response"].strip()
    }
