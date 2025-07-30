from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.processing_jobs import ProcessingJobs
from app.models.chat_history import ChatHistory
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Servicio para manejar operaciones de chat y base de datos"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_chat_history(self, chat_id: str) -> List[tuple[str, str]]:
        """
        Obtener historial de chat como lista de tuplas (user_message, agent_response)
        """
        try:
            messages = self.db.query(ChatHistory).filter(
                ChatHistory.chat_id == chat_id
            ).order_by(ChatHistory.created_at).all()
            
            # Convertir a formato de tuplas
            history = []
            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    user_msg = messages[i].message_text
                    agent_msg = messages[i + 1].message_text
                    history.append((user_msg, agent_msg))
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def save_message(self, chat_id: str, sender: str, message_text: str) -> bool:
        """
        Guardar un mensaje en el historial
        """
        try:
            message = ChatHistory(
                chat_id=chat_id,
                sender=sender,
                message_text=message_text
            )
            self.db.add(message)
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            self.db.rollback()
            return False
    
    def check_processing_status(self, chat_id: str) -> Optional[str]:
        """
        Verificar el estado de procesamiento de un chat
        """
        try:
            job = self.db.query(ProcessingJobs).filter(
                ProcessingJobs.chat_id == chat_id
            ).first()
            
            return job.status if job else None
            
        except Exception as e:
            logger.error(f"Error checking processing status: {str(e)}")
            return None
    
    def create_processing_job(self, chat_id: str, source_url: str) -> bool:
        """
        Crear un nuevo trabajo de procesamiento
        """
        try:
            job = ProcessingJobs(
                chat_id=chat_id,
                source_url=source_url,
                status="PENDING"
            )
            self.db.add(job)
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error creating processing job: {str(e)}")
            self.db.rollback()
            return False
    
    def get_processing_job(self, chat_id: str) -> Optional[ProcessingJobs]:
        """
        Obtener un trabajo de procesamiento
        """
        try:
            return self.db.query(ProcessingJobs).filter(
                ProcessingJobs.chat_id == chat_id
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting processing job: {str(e)}")
            return None 