import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de datos
    database_url: str = "postgresql://user:password@localhost/documentacion_rag"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # LLM Configuration
    llm_provider: str = "ollama"  # ollama, openai, anthropic
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    secret_key: str = "your_secret_key_here"
    
    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 