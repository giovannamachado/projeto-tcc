"""
Rota para verificação de saúde da aplicação.
Endpoint para monitoramento e status da API.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import psutil
import datetime

from ...core.database import get_db
from ...core.config import settings
from ...services.vector_store import vector_store

router = APIRouter()

@router.get("/", summary="Verificação básica de saúde")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint básico para verificar se a API está funcionando
    """
    return {
        "status": "healthy",
        "message": "API está funcionando normalmente",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/detailed", summary="Verificação detalhada de saúde")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Verificação completa incluindo banco de dados, serviços e recursos do sistema
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {},
        "system": {},
        "configuration": {}
    }

    # Verificar banco de dados
    try:
        db.execute("SELECT 1")
        health_status["services"]["database"] = {
            "status": "healthy",
            "type": "SQLite",
            "message": "Conexão estabelecida com sucesso"
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Verificar banco vetorial
    try:
        if vector_store.client:
            # Tentar uma operação simples
            collections = vector_store.client.list_collections()
            health_status["services"]["vector_store"] = {
                "status": "healthy",
                "type": "ChromaDB",
                "collections_count": len(collections),
                "persist_directory": str(settings.chroma_path)
            }
        else:
            raise Exception("Cliente ChromaDB não inicializado")
    except Exception as e:
        health_status["services"]["vector_store"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Verificar IA Service
    try:
        from ...services.ai_service import ai_service
        if ai_service.model:
            health_status["services"]["ai_service"] = {
                "status": "healthy",
                "model": settings.DEFAULT_MODEL,
                "message": "Gemini Pro conectado"
            }
        else:
            raise Exception("Modelo não inicializado")
    except Exception as e:
        health_status["services"]["ai_service"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Informações do sistema
    try:
        health_status["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "python_version": f"{psutil.PYTHON_EXECUTABLE}",
            "uptime_seconds": datetime.datetime.now().timestamp()
        }
    except Exception as e:
        health_status["system"] = {"error": f"Não foi possível obter informações do sistema: {e}"}

    # Configurações (sem dados sensíveis)
    health_status["configuration"] = {
        "debug": settings.DEBUG,
        "environment": settings.ENVIRONMENT,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
        "cors_origins_count": len(settings.CORS_ORIGINS),
        "default_model": settings.DEFAULT_MODEL,
        "chunk_size": settings.CHUNK_SIZE,
        "top_k_retrieval": settings.TOP_K_RETRIEVAL
    }

    return health_status

@router.get("/api-info", summary="Informações da API")
async def api_info() -> Dict[str, Any]:
    """
    Retorna informações sobre a API e suas capacidades
    """
    return {
        "name": "IA Generativa para Conteúdo de Mídia Social",
        "version": "1.0.0",
        "description": "API para geração automatizada de conteúdo usando IA Generativa com RAG",
        "author": "Estudante - Sistemas de Informação",
        "license": "MIT",
        "capabilities": [
            "Gerenciamento de personas de marca",
            "Upload e processamento de base de conhecimento",
            "Geração de legendas para Instagram",
            "Geração de hashtags personalizadas",
            "Ideias de conteúdo baseadas em IA",
            "Arquitetura RAG para contextualização"
        ],
        "supported_file_types": settings.ALLOWED_EXTENSIONS,
        "ai_models": {
            "text_generation": settings.DEFAULT_MODEL,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "authentication": "/api/v1/auth",
            "personas": "/api/v1/personas",
            "knowledge_base": "/api/v1/knowledge",
            "content_generation": "/api/v1/content"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        }
    }