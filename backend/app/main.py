from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables before importing app modules that rely on them
load_dotenv()

from app.chat import process_conversation

app = FastAPI(title="Askaweather API")

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    message: Message

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Convert Pydantic models to dicts for the chat logic
    conversation_history = [m.model_dump() for m in request.messages]
    
    # Process the conversation
    response_message = await process_conversation(conversation_history)
    
    return ChatResponse(message=Message(**response_message))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
