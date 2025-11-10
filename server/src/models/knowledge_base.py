"""
Modelo de dados para base de conhecimento.
Gerencia documentos e conteúdos que servem como fonte de verdade para a IA.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from ..core.database import Base

class DocumentType(PyEnum):
    """Tipos de documentos suportados"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "md"
    WEBPAGE = "webpage"
    SOCIAL_POST = "social_post"

class ProcessingStatus(PyEnum):
    """Status do processamento do documento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class KnowledgeBase(Base):
    """
    Modelo para base de conhecimento

    Armazena documentos, posts anteriores e outros conteúdos que servem
    como contexto para a IA gerar conteúdo autêntico e alinhado com a marca.
    """

    __tablename__ = "knowledge_bases"

    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Relacionamentos
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Informações do arquivo
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)  # Em bytes
    file_type = Column(String(10))  # pdf, docx, txt, etc.

    # Processamento e vetorização
    processing_status = Column(String(20), default=ProcessingStatus.PENDING.value)
    processing_error = Column(Text)

    # Metadados de conteúdo
    word_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)  # Número de chunks criados

    # Configurações de embedding
    embedding_model = Column(String(100), default="sentence-transformers/all-MiniLM-L6-v2")
    vector_store_id = Column(String(255))  # ID no ChromaDB

    # Relevância e uso
    usage_count = Column(Integer, default=0)  # Quantas vezes foi usado para geração
    relevance_score = Column(Float, default=0.0)  # Score de relevância (calculado)

    # Status e configurações
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Para compartilhamento futuro

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relacionamentos
    persona = relationship("Persona", back_populates="knowledge_bases")
    owner = relationship("User", back_populates="knowledge_bases")

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, title='{self.title}', status='{self.processing_status}')>"

    @property
    def file_size_mb(self) -> float:
        """Retorna o tamanho do arquivo em MB"""
        if not self.file_size:
            return 0.0
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def is_processed(self) -> bool:
        """Verifica se o documento foi processado com sucesso"""
        return self.processing_status == ProcessingStatus.COMPLETED.value

    @property
    def is_processing(self) -> bool:
        """Verifica se o documento está sendo processado"""
        return self.processing_status == ProcessingStatus.PROCESSING.value

    @property
    def has_error(self) -> bool:
        """Verifica se houve erro no processamento"""
        return self.processing_status == ProcessingStatus.FAILED.value

    def increment_usage(self):
        """Incrementa o contador de uso"""
        self.usage_count += 1

    def update_relevance_score(self, score: float):
        """Atualiza o score de relevância"""
        self.relevance_score = max(0.0, min(1.0, score))  # Entre 0 e 1