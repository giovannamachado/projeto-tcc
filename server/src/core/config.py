"""
Configurações globais da aplicação.
Centraliza todas as configurações usando Pydantic Settings para validação e type safety.
"""

from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configurações da aplicação com validação Pydantic"""

    # =============================================================================
    # CONFIGURAÇÕES BÁSICAS
    # =============================================================================
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # =============================================================================
    # API KEYS - CRÍTICO PARA SEGURANÇA!
    # =============================================================================
    GOOGLE_API_KEY: str = ""  # Gemini via Google AI Studio (grátis)
    OPENROUTER_API_KEY: str = ""  # Alternativa com modelos grátis
    STABILITY_API_KEY: str = ""  # Para geração de imagens

    # Provider de IA para texto (google, openrouter, ou ollama)
    AI_TEXT_PROVIDER: str = "google"  # google | openrouter | ollama
    OPENROUTER_MODEL: str = "google/gemma-2-9b-it:free"  # modelo gratuito do OpenRouter
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    @validator('GOOGLE_API_KEY')
    def validate_google_api_key(cls, v, values):
        provider = values.get('AI_TEXT_PROVIDER', 'google')
        if provider == 'google' and (not v or v == "your_gemini_pro_api_key_here"):
            raise ValueError(
                "GOOGLE_API_KEY não configurada!\n"
                "Opção 1: Obtenha GRÁTIS em https://aistudio.google.com/app/apikey\n"
                "Opção 2: Use AI_TEXT_PROVIDER=openrouter e configure OPENROUTER_API_KEY\n"
                "Opção 3: Use AI_TEXT_PROVIDER=ollama para rodar localmente"
            )
        return v

    # =============================================================================
    # CORS E SEGURANÇA
    # =============================================================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]

    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v

    # =============================================================================
    # BANCO DE DADOS
    # =============================================================================
    DATABASE_URL: str = "sqlite:///./app.db"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    # =============================================================================
    # CONFIGURAÇÕES DE UPLOAD
    # =============================================================================
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt", "md"]
    UPLOAD_DIRECTORY: str = "./uploads"

    @validator('ALLOWED_EXTENSIONS', pre=True)
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v

    # =============================================================================
    # CONFIGURAÇÕES DE IA
    # =============================================================================
    DEFAULT_MODEL: str = "gemini-pro"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7

    # Configurações específicas do RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5

    # =============================================================================
    # CONFIGURAÇÕES DE AMBIENTE
    # =============================================================================
    ENVIRONMENT: str = "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def upload_path(self) -> Path:
        """Retorna o caminho completo para a pasta de uploads"""
        path = Path(self.UPLOAD_DIRECTORY)
        path.mkdir(exist_ok=True)
        return path

    @property
    def chroma_path(self) -> Path:
        """Retorna o caminho completo para o banco vetorial"""
        path = Path(self.CHROMA_PERSIST_DIRECTORY)
        path.mkdir(exist_ok=True)
        return path

    # =============================================================================
    # CONFIGURAÇÃO DE CARREGAMENTO
    # =============================================================================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Instância global das configurações
settings = Settings()

# Função para validar configurações críticas
def validate_critical_settings():
    """Valida se todas as configurações críticas estão presentes"""
    critical_checks = []

    # Verificar chave da API
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_gemini_pro_api_key_here":
        critical_checks.append("❌ GOOGLE_API_KEY não configurada!")

    # Verificar se diretórios podem ser criados
    try:
        settings.upload_path
        settings.chroma_path
    except Exception as e:
        critical_checks.append(f"❌ Erro ao criar diretórios: {e}")

    if critical_checks:
        error_msg = "\n".join([
            " CONFIGURAÇÕES CRÍTICAS FALTANDO:",
            *critical_checks,
            "",
            " Para corrigir:",
            "1. Copie o arquivo .env.example para .env",
            "2. Configure sua chave da API do Gemini Pro",
            "3. Reinicie a aplicação"
        ])
        raise ValueError(error_msg)

    return True