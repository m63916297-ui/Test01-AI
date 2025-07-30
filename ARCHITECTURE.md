# Arquitectura del Documentación RAG Agent

## Visión General

El Documentación RAG Agent es una aplicación de inteligencia artificial que permite a los usuarios hacer preguntas sobre documentación técnica y recibir respuestas precisas basadas en el contenido de esa documentación. La aplicación utiliza técnicas de RAG (Retrieval-Augmented Generation) para combinar la recuperación de información relevante con la generación de respuestas contextualizadas.

## Arquitectura del Sistema

### 1. Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Celery Tasks  │    │   LangGraph     │
│   (API Layer)   │    │   (Background)  │    │   (Agent)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     ChromaDB    │    │   LLM Service   │
│   (Metadata)    │    │   (Vector DB)   │    │   (Ollama/API)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Stack Tecnológico

#### Backend Framework: FastAPI
- **Justificación**: Alto rendimiento, soporte nativo para async/await, documentación automática
- **Responsabilidades**: API REST, manejo de requests/responses, validación de datos

#### Base de Datos: PostgreSQL
- **Justificación**: Robusto, soporte para JSONB, extensibilidad con pgvector
- **Responsabilidades**: Almacenamiento de metadatos, historial de chat, estado de procesamiento

#### Base de Datos Vectorial: ChromaDB
- **Justificación**: Simplicidad, API-first, integración nativa con Python
- **Responsabilidades**: Almacenamiento y búsqueda de embeddings

#### Orquestación: Celery + Redis
- **Justificación**: Manejo de tareas asíncronas, escalabilidad
- **Responsabilidades**: Procesamiento de documentación en background

#### Agente: LangGraph
- **Justificación**: Orquestación de flujos complejos, nodos especializados
- **Responsabilidades**: Coordinación del flujo de conversación

## Flujo de Datos

### 1. Procesamiento de Documentación

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Celery
    participant Scraper
    participant ChromaDB
    participant PostgreSQL

    Client->>FastAPI: POST /process-documentation
    FastAPI->>PostgreSQL: Create processing job
    FastAPI->>Celery: Start processing task
    FastAPI->>Client: 202 Accepted
    
    Celery->>Scraper: Scrape website
    Scraper->>Celery: HTML content
    Celery->>Celery: Clean and chunk text
    Celery->>Celery: Generate embeddings
    Celery->>ChromaDB: Store embeddings
    Celery->>PostgreSQL: Update status to COMPLETED
```

### 2. Conversación con el Agente

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant LangGraph
    participant RAG Service
    participant LLM Service
    participant ChromaDB
    participant PostgreSQL

    Client->>FastAPI: POST /chat/{chatId}
    FastAPI->>LangGraph: Process question
    LangGraph->>LangGraph: Analyze intent
    LangGraph->>RAG Service: Retrieve documents
    RAG Service->>ChromaDB: Query embeddings
    ChromaDB->>RAG Service: Relevant documents
    LangGraph->>LLM Service: Generate response
    LLM Service->>LangGraph: Response
    LangGraph->>PostgreSQL: Save conversation
    LangGraph->>FastAPI: Final response
    FastAPI->>Client: Response
```

## Diseño del Agente LangGraph

### Estado del Agente

```python
class AgentState(TypedDict):
    question: str                    # Pregunta del usuario
    chat_history: List[tuple]        # Historial de conversación
    intent: str                      # Intención clasificada
    documents: List[Dict]            # Documentos recuperados
    response: str                    # Respuesta generada
    chat_id: str                     # ID del chat
```

### Nodos del Grafo

1. **Input Node**: Carga el historial y prepara el estado inicial
2. **Intent Analysis Node**: Clasifica la intención de la pregunta
3. **Conditional Router**: Enruta según la intención
4. **RAG Node**: Recupera documentos relevantes
5. **Code Analysis Node**: Recupera documentos específicos de código
6. **Response Generation Node**: Genera la respuesta final
7. **Code Formatting Node**: Formatea bloques de código
8. **Memory Node**: Guarda en base de datos
9. **Clarification Node**: Solicita más información

### Flujo del Grafo

```
Input Node → Intent Analysis Node → Conditional Router
                                              ↓
                    ┌─────────────────────────────────────────┐
                    ↓                                         ↓
              RAG Node ←───────────────────────────── Code Analysis Node
                    ↓                                         ↓
                    └─────────→ Response Generation Node ←────┘
                                        ↓
                              Code Formatting Node
                                        ↓
                                    Memory Node
                                        ↓
                                       END
```

## Pipeline de Procesamiento de Documentación

### 1. Web Scraping
- **Herramientas**: httpx + BeautifulSoup4, Playwright (fallback)
- **Estrategia**: Priorizar contenido en `<main>`, `<article>`, `<body>`
- **Manejo de SPAs**: Fallback automático a Playwright

### 2. Limpieza de Contenido
- Eliminación de elementos no deseados (nav, header, footer, etc.)
- Normalización de espacios y caracteres
- Extracción de texto limpio

### 3. Segmentación Inteligente
- **Método**: RecursiveCharacterTextSplitter
- **Separadores**: `\n\n` (párrafos) → `\n` (líneas) → espacios
- **Overlap**: 200 caracteres para mantener contexto
- **Tamaño máximo**: 1000 caracteres por chunk

### 4. Generación de Embeddings
- **Modelo**: sentence-transformers/all-MiniLM-L6-v2
- **Ventajas**: Equilibrio entre calidad y velocidad
- **Ejecución**: Local, sin costos de API

### 5. Almacenamiento Vectorial
- **Base de datos**: ChromaDB
- **Estructura**: Una colección por chat_id
- **Metadatos**: URL de origen, índice del chunk, tamaño

## Servicios y Capas

### 1. Capa de API (FastAPI)
- **Endpoints principales**:
  - `POST /api/v1/process-documentation`
  - `GET /api/v1/processing-status/{chatId}`
  - `POST /api/v1/chat/{chatId}`
  - `GET /api/v1/chat-history/{chatId}`

### 2. Capa de Servicios
- **LLMService**: Manejo de diferentes proveedores LLM
- **RAGService**: Recuperación de documentos desde cero
- **ChatService**: Operaciones de base de datos

### 3. Capa de Tareas (Celery)
- **process_documentation_task**: Pipeline completo de procesamiento
- **Manejo de errores**: Reintentos automáticos, logging detallado

### 4. Capa de Agente (LangGraph)
- **Orquestación**: Coordinación de flujo de conversación
- **Especialización**: Nodos específicos para diferentes tipos de consultas

## Configuración y Despliegue

### Variables de Entorno
```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost/documentacion_rag

# Redis
REDIS_URL=redis://localhost:6379

# LLM
LLM_PROVIDER=ollama  # ollama, openai, anthropic
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Aplicación
DEBUG=True
LOG_LEVEL=INFO
```

### Escalabilidad
- **Horizontal**: Múltiples instancias de FastAPI
- **Vertical**: Configuración de Celery workers
- **Base de datos**: Replicación PostgreSQL, sharding ChromaDB

### Monitoreo
- **Logging**: Estructurado con diferentes niveles
- **Métricas**: Tiempo de respuesta, tasa de éxito
- **Health checks**: Endpoints para verificar estado

## Consideraciones de Seguridad

### Autenticación y Autorización
- Implementar JWT tokens para autenticación
- Control de acceso basado en roles
- Rate limiting para prevenir abuso

### Validación de Entrada
- Validación de URLs antes del scraping
- Sanitización de contenido HTML
- Límites en tamaño de archivos y requests

### Protección de Datos
- Encriptación de datos sensibles
- Logs sin información personal
- Cumplimiento GDPR/CCPA

## Optimizaciones y Mejoras Futuras

### Rendimiento
- **Caching**: Redis para respuestas frecuentes
- **CDN**: Para archivos estáticos
- **Compresión**: Gzip para responses

### Funcionalidades
- **Búsqueda semántica**: Mejoras en embeddings
- **Análisis de sentimiento**: Clasificación de intención
- **Multilingüe**: Soporte para múltiples idiomas

### Integración
- **Webhooks**: Notificaciones de eventos
- **APIs externas**: Integración con sistemas existentes
- **Plugins**: Arquitectura extensible 