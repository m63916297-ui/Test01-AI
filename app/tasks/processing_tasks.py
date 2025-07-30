import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from sentence_transformers import SentenceTransformer
import chromadb
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.processing_jobs import ProcessingJobs
from app.config import settings
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_documentation_task(self, url: str, chat_id: str):
    """
    Tarea de Celery para procesar documentación desde una URL
    """
    try:
        # Actualizar estado a IN_PROGRESS
        update_processing_status(chat_id, "IN_PROGRESS")
        
        # 1. Web Scraping
        logger.info(f"Starting web scraping for {url}")
        html_content = scrape_website(url)
        
        # 2. Limpieza del HTML
        logger.info("Cleaning HTML content")
        clean_text = clean_html_content(html_content)
        
        # 3. Segmentación inteligente
        logger.info("Performing intelligent chunking")
        chunks = intelligent_chunking(clean_text)
        
        # 4. Generación de embeddings y almacenamiento
        logger.info("Generating embeddings and storing in ChromaDB")
        store_embeddings(chunks, chat_id, url)
        
        # 5. Actualizar estado a COMPLETED
        update_processing_status(chat_id, "COMPLETED")
        logger.info(f"Documentation processing completed for chat_id: {chat_id}")
        
        return {"status": "success", "chat_id": chat_id}
        
    except Exception as e:
        logger.error(f"Error processing documentation: {str(e)}")
        update_processing_status(chat_id, "FAILED", str(e))
        raise


def update_processing_status(chat_id: str, status: str, error_message: str = None):
    """Actualizar el estado de procesamiento en la base de datos"""
    db = SessionLocal()
    try:
        job = db.query(ProcessingJobs).filter(ProcessingJobs.chat_id == chat_id).first()
        if job:
            job.status = status
            if error_message:
                # Aquí podrías agregar un campo error_message al modelo si lo necesitas
                pass
            db.commit()
    except Exception as e:
        logger.error(f"Error updating processing status: {str(e)}")
        db.rollback()
    finally:
        db.close()


async def scrape_website(url: str) -> str:
    """Scraping de website usando httpx y BeautifulSoup, con fallback a Playwright"""
    try:
        # Intentar con httpx primero
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.warning(f"httpx failed, trying Playwright: {str(e)}")
        # Fallback a Playwright para SPAs
        return await scrape_with_playwright(url)


async def scrape_with_playwright(url: str) -> str:
    """Scraping con Playwright para manejar JavaScript"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        content = await page.content()
        await browser.close()
        return content


def clean_html_content(html_content: str) -> str:
    """Limpieza del contenido HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Eliminar elementos no deseados
    for element in soup.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
        element.decompose()
    
    # Priorizar contenido en etiquetas específicas
    main_content = soup.find(['main', 'article', 'body'])
    if main_content:
        text = main_content.get_text(separator='\n', strip=True)
    else:
        text = soup.get_text(separator='\n', strip=True)
    
    # Limpiar espacios extra y líneas vacías
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)


def intelligent_chunking(text: str, max_chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Segmentación inteligente del texto"""
    chunks = []
    
    # Dividir por párrafos primero
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    
    for paragraph in paragraphs:
        # Si agregar este párrafo excede el tamaño máximo
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Mantener overlap
            words = current_chunk.split()
            overlap_text = ' '.join(words[-overlap//10:])  # Aproximadamente overlap caracteres
            current_chunk = overlap_text + '\n\n' + paragraph
        else:
            current_chunk += '\n\n' + paragraph if current_chunk else paragraph
    
    # Agregar el último chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def store_embeddings(chunks: list[str], chat_id: str, source_url: str):
    """Generar embeddings y almacenar en ChromaDB"""
    # Inicializar modelo de embeddings
    model = SentenceTransformer(settings.embedding_model)
    
    # Inicializar ChromaDB
    client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
    
    # Crear o obtener colección
    collection_name = f"chat_{chat_id}"
    try:
        collection = client.get_collection(collection_name)
    except:
        collection = client.create_collection(collection_name)
    
    # Generar embeddings para cada chunk
    embeddings = model.encode(chunks)
    
    # Preparar metadatos
    metadatas = [
        {
            "source_url": source_url,
            "chunk_index": i,
            "chunk_size": len(chunk)
        }
        for i, chunk in enumerate(chunks)
    ]
    
    # IDs únicos para cada chunk
    ids = [f"chunk_{chat_id}_{i}" for i in range(len(chunks))]
    
    # Almacenar en ChromaDB
    collection.add(
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    logger.info(f"Stored {len(chunks)} chunks in ChromaDB for chat_id: {chat_id}") 