from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(255), ForeignKey("processing_jobs.chat_id"), nullable=False)
    sender = Column(String(50), nullable=False)  # 'user' o 'agent'
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con ProcessingJobs
    processing_job = relationship("ProcessingJobs", back_populates="chat_history")
    
    def __repr__(self):
        return f"<ChatHistory(message_id={self.message_id}, sender={self.sender})>" 