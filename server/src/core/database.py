"""
Configuração e inicialização do banco de dados.
Utiliza SQLAlchemy para ORM e SQLite para simplicidade no protótipo.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from typing import Generator

from .config import settings

# Configurar engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    # Configurações específicas para SQLite
    connect_args={
        "check_same_thread": False,
        "timeout": 20
    },
    poolclass=StaticPool,
    echo=settings.DEBUG  # Log SQL queries em modo debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency para obter sessão do banco de dados.
    Usado com FastAPI Depends() para injeção de dependência.

    Yields:
        Session: Sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas.
    Deve ser chamada no startup da aplicação.
    """
    try:
        # Importar todos os modelos para garantir que sejam registrados
        from ..models import persona, knowledge_base, user

        print(" Criando tabelas do banco de dados...")
        Base.metadata.create_all(bind=engine)
        print("Banco de dados inicializado com sucesso!")

    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        raise

def create_tables():
    """Cria todas as tabelas do banco de dados"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Remove todas as tabelas do banco de dados"""
    Base.metadata.drop_all(bind=engine)

def reset_database():
    """Reseta completamente o banco de dados"""
    print(" Resetando banco de dados...")
    drop_tables()
    create_tables()
    print(" Banco de dados resetado!")

# Metadata para introspection se necessário
metadata = MetaData()
metadata.reflect(bind=engine)