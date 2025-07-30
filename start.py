#!/usr/bin/env python3
"""
Script de inicio para el Documentación RAG Agent
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary",
        "celery", "redis", "sentence-transformers", "chromadb"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Faltan dependencias: {', '.join(missing_packages)}")
        print("Instala las dependencias con: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True


def check_services():
    """Verificar que los servicios estén ejecutándose"""
    print("🔍 Verificando servicios...")
    
    # Verificar Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis está ejecutándose")
    except Exception:
        print("❌ Redis no está ejecutándose")
        print("Inicia Redis con: redis-server")
        return False
    
    # Verificar PostgreSQL (opcional, se puede configurar después)
    print("ℹ️  Asegúrate de que PostgreSQL esté configurado y ejecutándose")
    
    return True


def setup_environment():
    """Configurar el entorno"""
    print("🔧 Configurando entorno...")
    
    # Crear directorio para ChromaDB si no existe
    chroma_dir = Path("./chroma_db")
    chroma_dir.mkdir(exist_ok=True)
    print("✅ Directorio ChromaDB creado")
    
    # Verificar archivo .env
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado")
        print("Copia env.example a .env y configura las variables")
        return False
    
    print("✅ Archivo .env encontrado")
    return True


def run_migrations():
    """Ejecutar migraciones de base de datos"""
    print("🗄️  Ejecutando migraciones...")
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print("✅ Migraciones ejecutadas correctamente")
            return True
        else:
            print(f"❌ Error ejecutando migraciones: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Alembic no encontrado. Instala las dependencias con: pip install -r requirements.txt")
        return False


def start_services():
    """Iniciar los servicios"""
    print("🚀 Iniciando servicios...")
    
    # Iniciar Celery worker en background
    print("📋 Iniciando Celery worker...")
    celery_process = subprocess.Popen(
        ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Esperar un momento para que Celery se inicie
    time.sleep(3)
    
    # Verificar que Celery esté ejecutándose
    if celery_process.poll() is None:
        print("✅ Celery worker iniciado")
    else:
        print("❌ Error iniciando Celery worker")
        return False
    
    # Iniciar FastAPI
    print("🌐 Iniciando FastAPI...")
    try:
        subprocess.run([
            "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        celery_process.terminate()
        celery_process.wait()
        print("✅ Servicios detenidos")


def main():
    """Función principal"""
    print("🤖 Documentación RAG Agent - Iniciando...")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar servicios
    if not check_services():
        sys.exit(1)
    
    # Configurar entorno
    if not setup_environment():
        sys.exit(1)
    
    # Ejecutar migraciones
    if not run_migrations():
        sys.exit(1)
    
    # Iniciar servicios
    start_services()


if __name__ == "__main__":
    main() 