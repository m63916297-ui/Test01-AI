from pydantic import BaseModel
from typing import Optional


class ProcessingStatusResponse(BaseModel):
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    chatId: str
    source_url: Optional[str] = None
    error_message: Optional[str] = None 