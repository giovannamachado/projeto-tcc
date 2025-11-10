"""
🚀 FastAPI Application - IA Generativa para Conteúdo de Mídia Social
TCC - Sistemas de Informação

Este é o ponto de entrada da aplicação backend que utiliza arquitetura RAG
para geração personalizada de conteúdo para Instagram.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Importar routers
from src.api.routes import auth, personas, knowledge_base, content_generation, health

# Importar configurações e utilitários
from src.core.config import settings
from src.core.database import init_db
from src.services.vector_store import init_vector_store

# Carregar variáveis de ambiente
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    try:
        # Inicializar banco de dados
        print("🔧 Inicializando banco de dados...")
        await init_db()

        # Inicializar vector store
        print("🧠 Inicializando banco vetorial...")
        await init_vector_store()

        print("✅ Aplicação inicializada com sucesso!")
        yield
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        raise
    finally:
        print("🔄 Finalizando aplicação...")

# Criar aplicação FastAPI
app = FastAPI(
    title="IA Generativa para Conteúdo de Mídia Social",
    description="""
    Sistema de geração automatizada de conteúdo para Instagram utilizando
    Inteligência Artificial Generativa com arquitetura RAG (Retrieval-Augmented Generation).

    ## Funcionalidades

    * **Personas**: Gerenciamento de identidade de marca
    * **Base de Conhecimento**: Upload e processamento de documentos
    * **Geração de Conteúdo**: Criação de textos e imagens personalizadas
    * **RAG**: Recuperação inteligente de contexto para gerações autênticas
    """,
    version="1.0.0",
    contact={
        "name": "Estudante - Sistemas de Informação",
        "email": "seu.email@universidade.edu.br",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Montar arquivos estáticos (para uploads, imagens geradas, etc.)
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluir routers da API
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(personas.router, prefix="/api/v1/personas", tags=["Personas"])
app.include_router(knowledge_base.router, prefix="/api/v1/knowledge", tags=["Base de Conhecimento"])
app.include_router(content_generation.router, prefix="/api/v1/content", tags=["Geração de Conteúdo"])

@app.get("/", summary="Endpoint raiz")
async def root():
    """Endpoint de boas-vindas da API"""
    return {
        "message": "🚀 IA Generativa para Conteúdo de Mídia Social - API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/v1", summary="Informações da API")
async def api_info():
    """Retorna informações gerais sobre a API"""
    return {
        "title": "IA Generativa para Conteúdo de Mídia Social",
        "version": "1.0.0",
        "description": "API para geração automatizada de conteúdo usando IA Generativa com RAG",
        "endpoints": {
            "health": "/api/v1/health",
            "auth": "/api/v1/auth",
            "personas": "/api/v1/personas",
            "knowledge": "/api/v1/knowledge",
            "content": "/api/v1/content"
        }
    }

if __name__ == "__main__":
    # Executar aplicação
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )