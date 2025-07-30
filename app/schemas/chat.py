from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    response: str
    chatId: str


class ChatHistoryItem(BaseModel):
    message_id: int
    sender: str
    message_text: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    chatId: str
    history: List[ChatHistoryItem] 