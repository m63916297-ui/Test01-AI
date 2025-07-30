from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Servicio RAG implementado desde cero"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
    
    def retrieve_documents(self, question: str, chat_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recuperar documentos relevantes usando similitud de embeddings
        """
        try:
            # Obtener colección
            collection_name = f"chat_{chat_id}"
            collection = self.client.get_collection(collection_name)
            
            # Generar embedding de la pregunta
            question_embedding = self.embedding_model.encode([question])
            
            # Buscar documentos similares
            results = collection.query(
                query_embeddings=question_embedding.tolist(),
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Formatear resultados
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "similarity_score": 1 - results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                    })
            
            logger.info(f"Retrieved {len(documents)} documents for chat_id: {chat_id}")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def retrieve_code_documents(self, question: str, chat_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recuperar documentos específicos de código
        """
        # Para consultas de código, podemos ajustar la búsqueda
        # Por ahora, usamos la misma lógica pero con más resultados
        return self.retrieve_documents(question, chat_id, top_k * 2)
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Formatear los documentos recuperados como contexto
        """
        if not documents:
            return "No se encontró información relevante en la documentación."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc["content"]
            metadata = doc.get("metadata", {})
            source_url = metadata.get("source_url", "Fuente desconocida")
            
            context_parts.append(f"Documento {i} (Fuente: {source_url}):\n{content}\n")
        
        return "\n".join(context_parts) 