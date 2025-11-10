"""
Modelo de dados para usuários do sistema.
Define a estrutura básica de autenticação e autorização.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base

class User(Base):
    """
    Modelo para usuários do sistema

    Representa criadores de conteúdo, marcas ou agências que utilizam o sistema
    para gerar conteúdo personalizado para suas redes sociais.
    """

    __tablename__ = "users"

    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Informações do perfil
    full_name = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, index=True)
    bio = Column(Text)

    # Configurações da conta
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relacionamentos
    personas = relationship("Persona", back_populates="owner", cascade="all, delete-orphan")
    knowledge_bases = relationship("KnowledgeBase", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    @property
    def display_name(self) -> str:
        """Retorna o nome de exibição preferido"""
        return self.full_name or self.username or self.email.split('@')[0]