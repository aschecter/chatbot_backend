import os
from typing import List, Literal, Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai

load_dotenv()                               # reads .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- FastAPI setup ----------
app = FastAPI(title="Qualtrics Chatbot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                    # tighten later if you wish
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["Content-Type"],
)

# ---------- Pydantic models ----------
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    variant: Literal["A", "B"] = Field("A", description="Experimental condition")
    meta: Dict[str, Any] | None = None      # Anything extra you want to log

class ChatResponse(BaseModel):
    reply: str

# ---------- Variant-specific rules ----------
def build_system_prompt(variant: str) -> str:
    if variant == "A":
        return (
            "You are Chatbot-A.\n"
            "Follow these rules:\n"
            "1. be friendly\n"
            
        )
    if variant == "B":
        return (
            "You are Chatbot-B.\n"
            "Follow these rules:\n"
            "1. be sarcastic\n"
            
        )
    return "You are a helpful assistant."

# ---------- Routes ----------
@app.get("/")
async def health() -> str:
    """Lightweight health-check (good for uptime pings)."""
    return "ok"

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main endpoint hit by the Qualtrics widget."""
    try:
        completion = await openai.chat.completions.create(
            model="gpt-4.1-mini",           # or whichever model you plan to test
            messages=[
                {"role": "system", "content": build_system_prompt(req.variant)},
                *[m.dict() for m in req.messages],
            ],
            temperature=0.7,               # [[TUNE]]
        )
        reply_text = completion.choices[0].message.content
        # TODO: persist {req, reply_text} to DB / file if desired
        return ChatResponse(reply=reply_text)

    except Exception as err:
        # Forward a safe error to client & log the details server-side
        print("OpenAI call failed:", err)
        raise HTTPException(status_code=500, detail="Upstream API error")

# ---------- Run locally ----------
# uvicorn main:app --reload --port 3000
