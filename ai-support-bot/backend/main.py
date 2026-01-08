from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Knowledge Loading --------
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

# -------- Chat Memory --------
SESSIONS = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/chat")
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in SESSIONS:
        SESSIONS[session_id] = []

    history = SESSIONS[session_id]
    history.append(f"User: {req.message}")

    question = req.message.lower()

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

    context = "\n".join(history[-6:])

    prompt = f"""
You are GenX, a professional AI customer support agent.
Use the information below and the conversation context.
Be short and clear.

Information:
{relevant_info}

Conversation:
{context}

Reply:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    reply = response.json()["response"].strip()
    history.append(f"GenX: {reply}")

    return {
        "reply": reply,
        "session_id": session_id
    }
