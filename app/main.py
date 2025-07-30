from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.models.database import get_db, engine
from app.models import Base
from app.schemas import (
    ProcessDocumentationRequest,
    ProcessDocumentationResponse,
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ProcessingStatusResponse
)
from app.services.chat_service import ChatService
from app.agents.documentation_agent import DocumentationAgent
from app.tasks.processing_tasks import process_documentation_task
from app.config import settings
import logging

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title="Documentación RAG Agent",
    description="Un agente inteligente de documentación que utiliza RAG para responder preguntas sobre documentación técnica",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
chat_service = ChatService()
documentation_agent = DocumentationAgent()


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Documentación RAG Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/v1/process-documentation", response_model=ProcessDocumentationResponse)
async def process_documentation(
    request: ProcessDocumentationRequest,
    db: Session = Depends(get_db)
):
    """
    Procesar documentación desde una URL
    
    - **url**: URL de la documentación a procesar
    - **chatId**: ID único del chat
    """
    try:
        # Crear trabajo de procesamiento
        success = chat_service.create_processing_job(request.chatId, str(request.url))
        if not success:
            raise HTTPException(status_code=500, detail="Error creating processing job")
        
        # Lanzar tarea de Celery
        task = process_documentation_task.delay(str(request.url), request.chatId)
        
        logger.info(f"Processing task started for chat_id: {request.chatId}, task_id: {task.id}")
        
        return ProcessDocumentationResponse(
            message="Processing started",
            status="IN_PROGRESS",
            chatId=request.chatId
        )
        
    except Exception as e:
        logger.error(f"Error starting processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/processing-status/{chat_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(chat_id: str, db: Session = Depends(get_db)):
    """
    Obtener el estado de procesamiento de un chat
    
    - **chat_id**: ID del chat
    """
    try:
        job = chat_service.get_processing_job(chat_id)
        if not job:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return ProcessingStatusResponse(
            status=job.status,
            chatId=chat_id,
            source_url=job.source_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat/{chat_id}", response_model=ChatResponse)
async def chat(chat_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    """
    Hacer una pregunta al agente de documentación
    
    - **chat_id**: ID del chat
    - **question**: Pregunta del usuario
    """
    try:
        # Procesar pregunta con el agente
        response = await documentation_agent.process_question(request.question, chat_id)
        
        return ChatResponse(
            response=response,
            chatId=chat_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chat-history/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: str, db: Session = Depends(get_db)):
    """
    Obtener el historial de chat
    
    - **chat_id**: ID del chat
    """
    try:
        # Verificar que el chat existe
        job = chat_service.get_processing_job(chat_id)
        if not job:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Obtener historial
        messages = db.query(chat_service.db.query.__class__).filter(
            chat_service.db.query.__class__.chat_id == chat_id
        ).order_by(chat_service.db.query.__class__.created_at).all()
        
        # Convertir a formato de respuesta
        history_items = []
        for msg in messages:
            history_items.append({
                "message_id": msg.message_id,
                "sender": msg.sender,
                "message_text": msg.message_text,
                "created_at": msg.created_at
            })
        
        return ChatHistoryResponse(
            chatId=chat_id,
            history=history_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 