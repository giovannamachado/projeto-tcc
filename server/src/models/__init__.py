"""
Inicialização dos modelos.
Centraliza as importações de todos os modelos para facilitar o uso.
"""

from .user import User
from .persona import Persona
from .knowledge_base import KnowledgeBase, DocumentType, ProcessingStatus

__all__ = [
    "User",
    "Persona",
    "KnowledgeBase",
    "DocumentType",
    "ProcessingStatus"
]