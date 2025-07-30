from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base


class ProcessingJobs(Base):
    __tablename__ = "processing_jobs"
    
    chat_id = Column(String(255), primary_key=True)
    source_url = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relación con ChatHistory
    chat_history = relationship("ChatHistory", back_populates="processing_job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProcessingJobs(chat_id={self.chat_id}, status={self.status})>" 