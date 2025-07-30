# Documentación RAG Agent

Un agente inteligente de documentación que utiliza RAG (Retrieval-Augmented Generation) para responder preguntas sobre documentación técnica.

## 🏗️ Arquitectura

- **Backend**: FastAPI (Python)
- **Base de Datos**: PostgreSQL
- **Base de Datos Vectorial**: ChromaDB
- **Orquestación**: Celery + Redis
- **LLM**: Ollama (desarrollo) / OpenAI/Anthropic (producción)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

## 🚀 Instalación

### Prerrequisitos

- Python 3.9+
- PostgreSQL
- Redis
- Ollama (para desarrollo local)

### Configuración

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd documentacion-rag-agent
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Configurar base de datos**
```bash
# Crear base de datos PostgreSQL
createdb documentacion_rag

# Ejecutar migraciones
alembic upgrade head
```

6. **Instalar Playwright**
```bash
playwright install
```

## 🏃‍♂️ Ejecución

### Desarrollo

1. **Iniciar Redis**
```bash
redis-server
```

2. **Iniciar Celery worker**
```bash
celery -A app.celery_app worker --loglevel=info
```

3. **Iniciar FastAPI**
```bash
uvicorn app.main:app --reload
```

4. **Iniciar Ollama (opcional)**
```bash
ollama run llama2
```

### Producción

```bash
# Usar gunicorn para producción
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📚 Uso de la API

### 1. Procesar Documentación

```bash
curl -X POST "http://localhost:8000/api/v1/process-documentation" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.example.com",
    "chatId": "chat_123"
  }'
```

### 2. Verificar Estado de Procesamiento

```bash
curl "http://localhost:8000/api/v1/processing-status/chat_123"
```

### 3. Hacer Pregunta

```bash
curl -X POST "http://localhost:8000/api/v1/chat/chat_123" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cómo configurar la base de datos?"
  }'
```

### 4. Obtener Historial

```bash
curl "http://localhost:8000/api/v1/chat-history/chat_123"
```

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost/documentacion_rag

# Redis
REDIS_URL=redis://localhost:6379

# LLM
LLM_PROVIDER=ollama  # ollama, openai, anthropic
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Configuración de la aplicación
DEBUG=True
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov=app
```

## 📁 Estructura del Proyecto

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── celery_app.py          # Celery configuration
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── agents/                # LangGraph agents
│   ├── tasks/                 # Celery tasks
│   └── utils/                 # Utilities
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── requirements.txt
├── .env.example
└── README.md
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles. 