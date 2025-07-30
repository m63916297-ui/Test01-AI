# Ejemplos de Uso - Documentación RAG Agent

## Configuración Inicial

### 1. Instalación y Configuración

```bash
# Clonar el repositorio
git clone <repository-url>
cd documentacion-rag-agent

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# Configurar base de datos
createdb documentacion_rag
alembic upgrade head

# Instalar Playwright
playwright install
```

### 2. Iniciar Servicios

```bash
# Terminal 1: Iniciar Redis
redis-server

# Terminal 2: Iniciar Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Iniciar FastAPI
uvicorn app.main:app --reload

# Terminal 4: Iniciar Ollama (opcional)
ollama run llama2
```

## Ejemplos de Uso de la API

### 1. Procesar Documentación

#### Ejemplo 1: Documentación de FastAPI

```bash
curl -X POST "http://localhost:8000/api/v1/process-documentation" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://fastapi.tiangolo.com/",
    "chatId": "fastapi_docs_001"
  }'
```

**Respuesta:**
```json
{
  "message": "Processing started",
  "status": "IN_PROGRESS",
  "chatId": "fastapi_docs_001"
}
```

#### Ejemplo 2: Documentación de Python

```bash
curl -X POST "http://localhost:8000/api/v1/process-documentation" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.python.org/3/",
    "chatId": "python_docs_001"
  }'
```

### 2. Verificar Estado de Procesamiento

```bash
curl "http://localhost:8000/api/v1/processing-status/fastapi_docs_001"
```

**Respuesta:**
```json
{
  "status": "COMPLETED",
  "chatId": "fastapi_docs_001",
  "source_url": "https://fastapi.tiangolo.com/"
}
```

### 3. Hacer Preguntas

#### Ejemplo 1: Pregunta General sobre FastAPI

```bash
curl -X POST "http://localhost:8000/api/v1/chat/fastapi_docs_001" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué es FastAPI y cuáles son sus principales características?"
  }'
```

**Respuesta esperada:**
```json
{
  "response": "FastAPI es un framework web moderno y rápido para construir APIs con Python 3.7+ basado en type hints estándar de Python. Sus principales características incluyen:\n\n- **Velocidad**: Rendimiento muy alto, comparable a NodeJS y Go\n- **Fácil de usar**: Diseñado para ser fácil de usar y aprender\n- **Menos errores**: Reducción del 40% de errores humanos\n- **Intellisense**: Soporte completo para autocompletado\n- **Validación automática**: Validación automática de datos\n- **Documentación automática**: Genera automáticamente documentación interactiva\n- **Basado en estándares**: Basado en OpenAPI (anteriormente Swagger) y JSON Schema",
  "chatId": "fastapi_docs_001"
}
```

#### Ejemplo 2: Pregunta sobre Código

```bash
curl -X POST "http://localhost:8000/api/v1/chat/fastapi_docs_001" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cómo creo un endpoint básico en FastAPI?"
  }'
```

**Respuesta esperada:**
```json
{
  "response": "Para crear un endpoint básico en FastAPI, puedes usar el siguiente código:\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/\")\ndef read_root():\n    return {\"Hello\": \"World\"}\n\n@app.get(\"/items/{item_id}\")\ndef read_item(item_id: int, q: str = None):\n    return {\"item_id\": item_id, \"q\": q}\n```\n\nLos elementos clave son:\n- Usar el decorador `@app.get()` para endpoints GET\n- Definir la función que maneja la request\n- FastAPI automáticamente convierte el return a JSON\n- Los parámetros de path se definen en la URL\n- Los query parameters se definen como parámetros de la función",
  "chatId": "fastapi_docs_001"
}
```

#### Ejemplo 3: Pregunta de Seguimiento

```bash
curl -X POST "http://localhost:8000/api/v1/chat/fastapi_docs_001" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Y cómo puedo agregar validación de datos a ese endpoint?"
  }'
```

**Respuesta esperada:**
```json
{
  "response": "Para agregar validación de datos en FastAPI, puedes usar Pydantic models. Aquí tienes un ejemplo:\n\n```python\nfrom fastapi import FastAPI\nfrom pydantic import BaseModel\nfrom typing import Optional\n\napp = FastAPI()\n\nclass Item(BaseModel):\n    name: str\n    description: Optional[str] = None\n    price: float\n    tax: Optional[float] = None\n\n@app.post(\"/items/\")\ndef create_item(item: Item):\n    return item\n```\n\nLa validación automática incluye:\n- Verificación de tipos de datos\n- Validación de campos requeridos\n- Conversión automática de tipos\n- Generación automática de documentación\n- Mensajes de error detallados",
  "chatId": "fastapi_docs_001"
}
```

### 4. Obtener Historial de Chat

```bash
curl "http://localhost:8000/api/v1/chat-history/fastapi_docs_001"
```

**Respuesta:**
```json
{
  "chatId": "fastapi_docs_001",
  "history": [
    {
      "message_id": 1,
      "sender": "user",
      "message_text": "¿Qué es FastAPI y cuáles son sus principales características?",
      "created_at": "2024-01-01T10:00:00Z"
    },
    {
      "message_id": 2,
      "sender": "agent",
      "message_text": "FastAPI es un framework web moderno...",
      "created_at": "2024-01-01T10:00:05Z"
    },
    {
      "message_id": 3,
      "sender": "user",
      "message_text": "¿Cómo creo un endpoint básico en FastAPI?",
      "created_at": "2024-01-01T10:05:00Z"
    },
    {
      "message_id": 4,
      "sender": "agent",
      "message_text": "Para crear un endpoint básico...",
      "created_at": "2024-01-01T10:05:03Z"
    }
  ]
}
```

## Ejemplos con Python

### Usando requests

```python
import requests
import time

# Configuración
BASE_URL = "http://localhost:8000"
CHAT_ID = "python_example_001"

# 1. Procesar documentación
response = requests.post(f"{BASE_URL}/api/v1/process-documentation", json={
    "url": "https://docs.python.org/3/",
    "chatId": CHAT_ID
})
print("Procesamiento iniciado:", response.json())

# 2. Esperar a que termine el procesamiento
while True:
    status_response = requests.get(f"{BASE_URL}/api/v1/processing-status/{CHAT_ID}")
    status = status_response.json()["status"]
    
    if status == "COMPLETED":
        print("Procesamiento completado")
        break
    elif status == "FAILED":
        print("Error en el procesamiento")
        break
    else:
        print(f"Estado: {status}")
        time.sleep(5)

# 3. Hacer preguntas
questions = [
    "¿Qué es Python?",
    "¿Cómo creo una función en Python?",
    "¿Qué son las list comprehensions?"
]

for question in questions:
    response = requests.post(f"{BASE_URL}/api/v1/chat/{CHAT_ID}", json={
        "question": question
    })
    print(f"\nPregunta: {question}")
    print(f"Respuesta: {response.json()['response']}")
```

### Usando aiohttp (Async)

```python
import aiohttp
import asyncio

async def chat_with_docs():
    async with aiohttp.ClientSession() as session:
        # Procesar documentación
        async with session.post("http://localhost:8000/api/v1/process-documentation", json={
            "url": "https://fastapi.tiangolo.com/",
            "chatId": "async_example_001"
        }) as response:
            result = await response.json()
            print("Procesamiento iniciado:", result)
        
        # Esperar procesamiento
        chat_id = "async_example_001"
        while True:
            async with session.get(f"http://localhost:8000/api/v1/processing-status/{chat_id}") as response:
                status = await response.json()
                if status["status"] == "COMPLETED":
                    break
                await asyncio.sleep(5)
        
        # Hacer preguntas
        questions = [
            "¿Qué es FastAPI?",
            "¿Cómo manejo errores en FastAPI?",
            "¿Cómo implemento autenticación?"
        ]
        
        for question in questions:
            async with session.post(f"http://localhost:8000/api/v1/chat/{chat_id}", json={
                "question": question
            }) as response:
                result = await response.json()
                print(f"\nPregunta: {question}")
                print(f"Respuesta: {result['response']}")

# Ejecutar
asyncio.run(chat_with_docs())
```

## Ejemplos de Casos de Uso

### 1. Documentación de API

```bash
# Procesar documentación de una API
curl -X POST "http://localhost:8000/api/v1/process-documentation" \
  -d '{"url": "https://api.example.com/docs", "chatId": "api_docs"}'

# Preguntas específicas sobre la API
curl -X POST "http://localhost:8000/api/v1/chat/api_docs" \
  -d '{"question": "¿Cómo autentico mis requests a la API?"}'
```

### 2. Documentación de Librería

```bash
# Procesar documentación de una librería
curl -X POST "http://localhost:8000/api/v1/process-documentation" \
  -d '{"url": "https://pandas.pydata.org/docs/", "chatId": "pandas_docs"}'

# Preguntas sobre funcionalidades
curl -X POST "http://localhost:8000/api/v1/chat/pandas_docs" \
  -d '{"question": "¿Cómo puedo leer un archivo CSV con pandas?"}'
```

### 3. Documentación de Framework

```bash
# Procesar documentación de un framework
curl -X POST "http://localhost:8000/api/v1/process-documentation" \
  -d '{"url": "https://docs.djangoproject.com/", "chatId": "django_docs"}'

# Preguntas sobre configuración
curl -X POST "http://localhost:8000/api/v1/chat/django_docs" \
  -d '{"question": "¿Cómo configuro la base de datos en Django?"}'
```

## Troubleshooting

### Error: "Chat not found"
```bash
# Verificar que el chat existe
curl "http://localhost:8000/api/v1/processing-status/chat_id"

# Si no existe, procesar documentación primero
curl -X POST "http://localhost:8000/api/v1/process-documentation" \
  -d '{"url": "https://example.com", "chatId": "chat_id"}'
```

### Error: "Processing failed"
```bash
# Verificar logs de Celery
celery -A app.celery_app worker --loglevel=debug

# Verificar que Redis esté ejecutándose
redis-cli ping
```

### Error: "Database connection failed"
```bash
# Verificar configuración de PostgreSQL
psql -h localhost -U user -d documentacion_rag

# Verificar variables de entorno
cat .env | grep DATABASE_URL
``` 