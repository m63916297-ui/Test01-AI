from typing import Optional
from langchain.llms.base import LLM
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Servicio para manejar diferentes proveedores de LLM"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> LLM:
        """Inicializar el LLM según la configuración"""
        provider = settings.llm_provider.lower()
        
        if provider == "ollama":
            return Ollama(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                temperature=0.7
            )
        elif provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model="gpt-4o-mini",  # o gpt-4o para mejor calidad
                temperature=0.7
            )
        elif provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model="claude-3-haiku-20240307",  # o claude-3-opus-20240229 para mejor calidad
                temperature=0.7
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    async def generate_response(self, prompt: str) -> str:
        """Generar respuesta usando el LLM configurado"""
        try:
            response = await self.llm.ainvoke(prompt)
            return response
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    async def analyze_intent(self, question: str, chat_history: list) -> str:
        """Analizar la intención de la pregunta del usuario"""
        intent_prompt = f"""
        Analiza la siguiente pregunta de usuario en el contexto de una conversación sobre documentación técnica.
        Clasifica la intención como:
        - 'general_query': Pregunta general sobre la documentación
        - 'code_query': Pregunta específica sobre código o implementación
        - 'follow_up_question': Pregunta de seguimiento o clarificación
        
        Pregunta: {question}
        Historial de conversación: {chat_history}
        
        Responde solo con una de las tres opciones: general_query, code_query, o follow_up_question
        """
        
        try:
            intent = await self.generate_response(intent_prompt)
            return intent.strip().lower()
        except Exception as e:
            logger.error(f"Error analyzing intent: {str(e)}")
            return "general_query"  # Fallback por defecto 