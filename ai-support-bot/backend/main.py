from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and parse knowledge
def load_knowledge():
    sections = {}
    current_key = None

    with open("knowledge.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current_key = line[1:-1]
                sections[current_key] = ""
            elif current_key:
                sections[current_key] += line + " "

    return sections

KNOWLEDGE = load_knowledge()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    question = req.message.lower()

    # Simple keyword matching
    relevant_info = ""

    if "refund" in question:
        relevant_info = KNOWLEDGE.get("REFUND_POLICY", "")
    elif "hour" in question or "time" in question:
        relevant_info = KNOWLEDGE.get("WORKING_HOURS", "")
    elif "contact" in question or "support" in question:
        relevant_info = KNOWLEDGE.get("CONTACT", "")
    elif "payment" in question or "upi" in question:
        relevant_info = KNOWLEDGE.get("PAYMENTS", "")
    else:
        relevant_info = KNOWLEDGE.get("ABOUT", "")

    prompt = f"""
You are a professional AI customer support agent.
Answer clearly and briefly using ONLY the information below.
If information is missing, say you don't have it.

Information:
{relevant_info}

Customer Question:
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

    return {"reply": response.json()["response"].strip()}
