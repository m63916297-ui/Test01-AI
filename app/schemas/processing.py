from pydantic import BaseModel, HttpUrl
from typing import Optional


class ProcessDocumentationRequest(BaseModel):
    url: HttpUrl
    chatId: str


class ProcessDocumentationResponse(BaseModel):
    message: str
    status: str
    chatId: str 