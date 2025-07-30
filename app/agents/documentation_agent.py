from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.chat_service import ChatService
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Estado del agente que se pasa entre nodos"""
    question: str
    chat_history: List[tuple[str, str]]
    intent: str
    documents: List[Dict[str, Any]]
    response: str
    chat_id: str


class DocumentationAgent:
    """Agente de documentación usando LangGraph"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.chat_service = ChatService()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construir el grafo de LangGraph"""
        workflow = StateGraph(AgentState)
        
        # Agregar nodos
        workflow.add_node("input_node", self._input_node)
        workflow.add_node("intent_analysis_node", self._intent_analysis_node)
        workflow.add_node("rag_node", self._rag_node)
        workflow.add_node("code_analysis_node", self._code_analysis_node)
        workflow.add_node("response_generation_node", self._response_generation_node)
        workflow.add_node("code_formatting_node", self._code_formatting_node)
        workflow.add_node("memory_node", self._memory_node)
        workflow.add_node("clarification_node", self._clarification_node)
        
        # Agregar enrutamiento condicional
        workflow.add_conditional_edges(
            "intent_analysis_node",
            self._conditional_router,
            {
                "general_query": "rag_node",
                "code_query": "code_analysis_node",
                "clarification": "clarification_node"
            }
        )
        
        # Agregar edges
        workflow.add_edge("input_node", "intent_analysis_node")
        workflow.add_edge("rag_node", "response_generation_node")
        workflow.add_edge("code_analysis_node", "response_generation_node")
        workflow.add_edge("response_generation_node", "code_formatting_node")
        workflow.add_edge("code_formatting_node", "memory_node")
        workflow.add_edge("memory_node", END)
        workflow.add_edge("clarification_node", END)
        
        return workflow.compile()
    
    async def _input_node(self, state: AgentState) -> AgentState:
        """Nodo de entrada: cargar historial y preparar estado"""
        chat_id = state["chat_id"]
        question = state["question"]
        
        # Cargar historial de chat
        chat_history = self.chat_service.get_chat_history(chat_id)
        
        return {
            **state,
            "chat_history": chat_history
        }
    
    async def _intent_analysis_node(self, state: AgentState) -> AgentState:
        """Nodo de análisis de intención"""
        question = state["question"]
        chat_history = state["chat_history"]
        
        # Analizar intención usando LLM
        intent = await self.llm_service.analyze_intent(question, chat_history)
        
        return {
            **state,
            "intent": intent
        }
    
    def _conditional_router(self, state: AgentState) -> str:
        """Enrutamiento condicional basado en la intención"""
        intent = state["intent"]
        
        if intent == "general_query" or intent == "follow_up_question":
            return "general_query"
        elif intent == "code_query":
            return "code_query"
        else:
            return "clarification"
    
    async def _rag_node(self, state: AgentState) -> AgentState:
        """Nodo RAG: recuperar documentos relevantes"""
        question = state["question"]
        chat_id = state["chat_id"]
        
        # Recuperar documentos usando RAG
        documents = self.rag_service.retrieve_documents(question, chat_id)
        
        return {
            **state,
            "documents": documents
        }
    
    async def _code_analysis_node(self, state: AgentState) -> AgentState:
        """Nodo de análisis de código: recuperar documentos específicos de código"""
        question = state["question"]
        chat_id = state["chat_id"]
        
        # Recuperar documentos específicos de código
        documents = self.rag_service.retrieve_code_documents(question, chat_id)
        
        return {
            **state,
            "documents": documents
        }
    
    async def _response_generation_node(self, state: AgentState) -> AgentState:
        """Nodo de generación de respuesta"""
        question = state["question"]
        chat_history = state["chat_history"]
        documents = state["documents"]
        
        # Formatear contexto
        context = self.rag_service.format_context(documents)
        
        # Formatear historial
        history_text = ""
        if chat_history:
            history_parts = []
            for user_msg, agent_msg in chat_history[-3:]:  # Últimos 3 intercambios
                history_parts.append(f"Usuario: {user_msg}")
                history_parts.append(f"Asistente: {agent_msg}")
            history_text = "\n".join(history_parts)
        
        # Generar prompt
        prompt = f"""
        Eres un asistente experto en la documentación técnica proporcionada.
        
        Usando el siguiente CONTEXTO y el HISTORIAL de la conversación, responde a la PREGUNTA del usuario de manera clara y precisa.
        
        Si no sabes la respuesta basándote en la documentación proporcionada, di claramente que no tienes esa información.
        
        CONTEXTO:
        {context}
        
        HISTORIAL DE CONVERSACIÓN:
        {history_text}
        
        PREGUNTA: {question}
        
        Responde de manera útil y concisa:
        """
        
        # Generar respuesta
        response = await self.llm_service.generate_response(prompt)
        
        return {
            **state,
            "response": response
        }
    
    async def _code_formatting_node(self, state: AgentState) -> AgentState:
        """Nodo de formateo de código: asegurar que el código esté bien formateado"""
        response = state["response"]
        
        # Verificar si hay bloques de código sin formato
        if "```" not in response and any(keyword in response.lower() for keyword in ["function", "class", "def ", "import ", "from "]):
            # Agregar formato de código si es necesario
            lines = response.split('\n')
            formatted_lines = []
            in_code_block = False
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ["def ", "class ", "import ", "from ", "if __name__"]):
                    if not in_code_block:
                        formatted_lines.append("```python")
                        in_code_block = True
                elif in_code_block and line.strip() == "":
                    formatted_lines.append("```")
                    in_code_block = False
                
                formatted_lines.append(line)
            
            if in_code_block:
                formatted_lines.append("```")
            
            response = '\n'.join(formatted_lines)
        
        return {
            **state,
            "response": response
        }
    
    async def _memory_node(self, state: AgentState) -> AgentState:
        """Nodo de memoria: guardar en base de datos"""
        question = state["question"]
        response = state["response"]
        chat_id = state["chat_id"]
        
        # Guardar mensaje del usuario
        self.chat_service.save_message(chat_id, "user", question)
        
        # Guardar respuesta del agente
        self.chat_service.save_message(chat_id, "agent", response)
        
        return state
    
    async def _clarification_node(self, state: AgentState) -> AgentState:
        """Nodo de clarificación: pedir más información al usuario"""
        response = "Necesito más información para responder tu pregunta. ¿Podrías ser más específico o proporcionar más contexto?"
        
        return {
            **state,
            "response": response
        }
    
    async def process_question(self, question: str, chat_id: str) -> str:
        """Procesar una pregunta del usuario"""
        try:
            # Verificar estado de procesamiento
            status = self.chat_service.check_processing_status(chat_id)
            if status != "COMPLETED":
                if status == "PENDING" or status == "IN_PROGRESS":
                    return "La documentación aún se está procesando. Por favor, espera un momento y vuelve a intentar."
                elif status == "FAILED":
                    return "Hubo un error procesando la documentación. Por favor, intenta procesar la documentación nuevamente."
                else:
                    return "No se encontró documentación procesada para este chat. Por favor, procesa una documentación primero."
            
            # Estado inicial
            initial_state = AgentState(
                question=question,
                chat_history=[],
                intent="",
                documents=[],
                response="",
                chat_id=chat_id
            )
            
            # Ejecutar grafo
            final_state = await self.graph.ainvoke(initial_state)
            
            return final_state["response"]
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return f"Lo siento, hubo un error procesando tu pregunta: {str(e)}" 